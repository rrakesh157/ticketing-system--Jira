import os
import re
import json
import glob
import uuid
import httpx
import typing
import base64
import random
import fastapi
import datetime
import traceback
import importlib
import contextvars
import fastapi.security
import urdhva_base.entity
import urdhva_base.context
import urdhva_base.settings
import urdhva_base.redispool
import ticketing_enum
from jose import jwt, JWTError
from pydantic.fields import Field
from urllib.parse import urlparse
from slowapi.extension import Limiter
from cryptography.fernet import Fernet
import urdhva_base.ttl_cache as ttl_cache
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from mangum import Mangum
from starlette.responses import RedirectResponse

logger = urdhva_base.Logger.get_instance("urdhva_api")

# Changing docs based on settings variable, Defaults to /

openapi_url=os.path.join(urdhva_base.settings.docs_path, "openapi.json")
docs_url=os.path.join(urdhva_base.settings.docs_path, "docs")
redoc_url=os.path.join(urdhva_base.settings.docs_path, "redoc")
api_prefix = urdhva_base.settings.api_prefix

app = fastapi.FastAPI(openapi_url=openapi_url, docs_url=docs_url, redoc_url=redoc_url)
cookie_name = urdhva_base.settings.cookie_name

@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: fastapi.Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."}
    )

# Set a default limit (e.g., 1000 requests per minute)
limiter = Limiter(key_func=get_remote_address, application_limits=["1000/second"])

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add SlowAPI middleware (built-in middleware)
app.add_middleware(SlowAPIMiddleware)



# This function will give keycloak auth redirection url based on realm name given
async def get_customer_authentication_extension(realm):
    return "auth"


def is_valid_python_file(filename: str) -> bool:
    """Check if the file should be considered for router discovery."""
    return filename.endswith(".py") and not os.path.basename(filename).startswith("_")


def get_module_name_from_path(path: str) -> str:
    """Convert a file path to a Python module name."""
    return os.path.splitext(path)[0].replace(os.sep, '.')


def register_router_from_module(mod, modname: str):
    """Register a router from the given module if it contains one."""
    symbol = getattr(mod, 'router', None)
    if isinstance(symbol, fastapi.APIRouter):
        app.include_router(symbol, prefix="/api")
        # print(f"Registered router from {modname}.router")
        return

    for attr in dir(mod):
        if attr.startswith("_"):
            continue
        symbol = getattr(mod, attr)
        if isinstance(symbol, fastapi.APIRouter):
            app.include_router(symbol, prefix="/api")
            # print(f"Registered router from {modname}.{attr}")


@app.on_event("startup")
def on_start():
    for filepath in glob.glob("**/*.py", recursive=True):
        if not is_valid_python_file(filepath):
            continue

        modname = get_module_name_from_path(filepath)
        try:
            mod = importlib.import_module(modname)
            # If a variable by name "router" is defined load that directly
            # Else go through the module and if any of the variable is a router load that...
            symbol = getattr(mod, 'router', None)
            if isinstance(symbol, fastapi.APIRouter):
                app.include_router(symbol, prefix=api_prefix)
            else:
                for attr in dir(mod):
                    if not attr.startswith("_"):
                        symbol = getattr(mod, attr)
                        if isinstance(symbol, fastapi.APIRouter):
                            app.include_router(symbol, prefix=api_prefix)
        except Exception as e:
            print(f"Failed to load router from {modname}: {e}")


# Api to push data to redis server
async def create_internal_error_message(err_format):
    logger.error(f"internalerror_{urdhva_base.ctx['entity_id']} {err_format}")
    try:
        uuid_id = str(uuid.uuid4()).replace("-", "")
        conn = await urdhva_base.redispool.get_redis_connection()
        await conn.setex("internalerror_" + uuid_id, 60, err_format)
        return True, uuid_id
    except Exception as e:
        return False, e

# API for getting internal error message
@app.get(f"{api_prefix}"+"/get_internal_error/{unique_id}", include_in_schema=False)
async def get_internal_error(unique_id: str):
    # process the data
    conn = await urdhva_base.redispool.get_redis_connection()
    resp = await conn.get(f"internalerror_{unique_id}")
    if resp:
        return {"status": True, "message": "found", "data": resp.decode("utf-8")}
    return {"status": False, "message": "not found", "data": None}


async def get_baseurl(request: fastapi.Request, redirect_type="RedirectionUrl", entity_id=""):
    # print(f"{entity_id}")
    return os.environ.get(redirect_type, request.base_url.hostname)


async def get_permission():
    rpt = urdhva_base.context.context.get('rpt', {})
    data = {"is_authenticated": False, "allowed_roles": []}
    if rpt.get("username") and rpt.get("algo_role"):
        data['is_authenticated'] = True
        data["allowed_roles"] = rpt.get("allowed_roles", [])
    return data


async def get_resource_operation(method, path):
    path_params = path.split('/')
    resource = path_params[2].lower()
    operation = {'post': 'create', 'put': 'update', 'get': 'read', 'delete': 'delete'}.get(method.lower())
    if path_params[-1] == "":
        path_params = path_params[:-1]
    if method.lower() == 'post' and len(path_params) == 4 and path_params[3]:
        operation = path_params[3].lower()
    elif method.lower() == 'post' and len(path_params) == 5:
        operation = path_params[4].lower()
    elif method.lower() == 'get' and len(path_params) == 5:
        operation = path_params[4].lower()
    elif method.lower() == 'get' and len(path_params) == 6:
        operation = path_params[5].lower()
    return resource, operation

async def get_vendor_authorization_details():
    """Cache data loader"""
    redis_ins = await urdhva_base.redispool.get_redis_connection()
    vendor_details = {}
    resp = await redis_ins.hgetall("vendor_auth")
    for key, info in resp.items():
        if isinstance(key, bytes):
            key = key.decode()
        if isinstance(info, bytes):
            info = info.decode()
        if key.endswith('_access_key'):
            vendor = key.split("_access_key")[0]
            if vendor not in vendor_details:
                vendor_details[vendor] = {}
            vendor_details[vendor]['access_key'] = info
        elif key.endswith('_allowed_apis'):
            vendor = key.split("_allowed_apis")[0]
            if vendor not in vendor_details:
                vendor_details[vendor] = {}
            vendor_details[vendor]['allowed_apis'] = json.loads(info)
    return vendor_details


async def validate_header_based_authentication(request: fastapi.Request):
    """
        Validates the authentication of an incoming HTTP request based on headers.

        Args:
            request (fastapi.Request): The incoming HTTP request object.

        Steps:
        1. Extract the Authorization header from the request.
        2. Check if the Authorization header is missing or malformed.
        3. Validate the token (e.g., a JWT) from the Authorization header.
        4. Return an appropriate response if the authentication fails.
        5. If authentication is successful, allow the request to proceed.

        Returns:
            True, None: If the authentication is valid, the function does not return anything, and the request proceeds.
            False, 403: If the authentication fails, an HTTP exception is raised with the appropriate status code and message.
            False, None: If header based authentication not enabled or auth token not available in headers
        """
    if not urdhva_base.settings.enable_header_auth:
        return False, None
    headers = request.headers
    access_key = headers.get("pipeline-auth-token")
    if access_key:
        vendor = headers.get("vendor")
        if vendor:
            ins = ttl_cache.CacheDataInstance.get_instance("vendor_auth", get_vendor_authorization_details)
            cache_data = await ins.get(vendor)
            vendor_data = cache_data.get(vendor) if cache_data else {}
            if not vendor_data or access_key != vendor_data.get('access_key'):
                return False, fastapi.responses.JSONResponse("Invalid Authentication Credentials", 401)
            if vendor_data.get('allowed_apis') and request.url.path not in vendor_data.get('allowed_apis'):
                return False, fastapi.responses.JSONResponse("Permission Denied", 403)
            return True, None
    return False, None


def add_security_headers(response):
    return response


@app.middleware("http")
async def auth_middleware(request: fastapi.Request, call_next):
    return await call_next(request)
    status, resp = await validate_header_based_authentication(request)

    if status:
        return add_security_headers(await call_next(request))

    if not status and resp:
        return add_security_headers(resp)

    if is_public_url(request.url.path):
        return add_security_headers(await call_next(request))

    return await handle_auth_fallback(request, call_next)


def is_public_url(path: str) -> bool:
    public_paths = [
                       f"/{docs_url}", f"/{openapi_url}", f"{api_prefix}/login",
                       f"{api_prefix}/session/me", f"{api_prefix}/users/login"
                   ] + urdhva_base.settings.noauth_urls

    if path in public_paths:
        return True
    if re.match(r"/api/.*login\b(?![a-zA-Z])", path):
        return True
    if re.match(r"/api/.*authorize", path):
        return True
    return False


async def handle_auth_fallback(request: fastapi.Request, call_next) -> fastapi.Response:
    rpt = urdhva_base.context.context.get("rpt", {})
    cookie = request.cookies.get(cookie_name, None)

    if not cookie and not rpt:
        base_url = urdhva_base.ctx.get("base_url")
        if not base_url:
            return add_security_headers(JSONResponse("Provided entity is Invalid", 403))
        return add_security_headers(fastapi.responses.HTMLResponse("", 401))

    response: fastapi.Response = await call_next(request)
    if response.status_code == 307:
        response = rewrite_redirect_to_https(response)

    return add_security_headers(response)


def rewrite_redirect_to_https(response: fastapi.Response) -> fastapi.Response:
    updated_headers = []
    for key, value in response.raw_headers:
        if key.decode() == "location" and value.decode().startswith("http:"):
            new_value = value.decode().replace("http:", "https:")
            updated_headers.append((key, new_value.encode()))
        else:
            updated_headers.append((key, value))
    response.raw_headers = updated_headers
    return response

def verify_security_policy(host_name, header_value):
    if not urdhva_base.settings.origin_check_enabled or  not header_value:
        return True
    parsed_origin = urlparse(header_value)
    return host_name == parsed_origin.netloc

@app.middleware('http')
async def context_middleware(request: fastapi.Request, call_next):
    if not verify_security_policy(request.base_url.hostname, request.headers.get('origin')):
        return fastapi.responses.Response("Origin mismatch", 403)
    if not verify_security_policy(request.base_url.hostname, request.headers.get('referer')):
        return fastapi.responses.Response("Refer mismatch", 403)

    redis_client = await urdhva_base.redispool.get_redis_connection()
    cookie_id = request.cookies.get(cookie_name, None)
    entity_id = urdhva_base.settings.entity_id
    data = {}

    if cookie_id:
        entity_id, cookie_id, data = await extract_session_data(entity_id, cookie_id, data)

    else:
        # JWT-based login flow
        token = ''
        keys = ['Authorization', 'Authentication']
        for key in keys:
            if not token:
                token = request.headers.get(key)
                if not token:
                    token = request.headers.get(key.lower())
        token = token.split("Bearer")[-1].strip() if token else ""
        if token:
            try:
                jwt_secret = os.getenv("JWT_SECRET")
                jwt_algorithm = os.getenv("JWT_ALGORITHM")
                if urdhva_base.settings.jwt_secret_key:
                    jwt_secret = urdhva_base.settings.jwt_secret_key
                if urdhva_base.settings.jwt_algorithm:
                    jwt_algorithm = urdhva_base.settings.jwt_algorithm
                payload = jwt.decode(token, jwt_secret, algorithms=jwt_algorithm)
                entity_id = payload.get("entity_id", entity_id)
                data['base_url'] = payload.get("base_url", '')
                data['rpt'] = payload
            except JWTError as e:
                print(f"JWT decode error: {e}")
    if not entity_id:
        entity_id = extract_entity_from_header_or_host(request)

    context_data = await build_context_data(request, redis_client, entity_id, cookie_id, data)

    _starlette_context_token = urdhva_base.context._request_scope_context_storage.set(context_data)
    try:
        resp = await call_next(request)
    except Exception as error:
        print(traceback.format_exc())
        print(error)
        status, internal_id = await create_internal_error_message(traceback.format_exc())
        message = f"Internal Error:- {internal_id}" if status else "Internal Error"
        return fastapi.responses.JSONResponse(message, 500)
    finally:
        urdhva_base.context._request_scope_context_storage.reset(_starlette_context_token)

    return resp


async def extract_session_data(entity_id, cookie_id, data):
    try:
        f = Fernet(urdhva_base.settings.fernet_key)
        d = json.loads(f.decrypt(cookie_id.encode()).decode())
        new_entity_id = d["entity_id"]
        data['base_url'] = d.get("base_url", '')
        new_cookie_id = d["cookie_id"]
        return new_entity_id, new_cookie_id, data
    except Exception as e:
        print(e)
        return entity_id, cookie_id, data


def extract_entity_from_header_or_host(request):
    if request.headers.get("entity_id"):
        return request.headers["entity_id"]
    if not urdhva_base.settings.multi_tenant_support:
        return request.base_url.hostname.split('.')[0]
    return urdhva_base.settings.default_realm or "algo_fusion"


async def build_context_data(request, redis_client, entity_id, cookie_id, session_data):
    data = {
        'domain': request.base_url,
        'entity_obj': urdhva_base.entity.Entity(),
        'entity_id': entity_id,
        'base_url': session_data.get("base_url", "")
    }

    if cookie_id:
        cookie = await redis_client.get(f"algo_fusion_SessionData_{cookie_id}")
        if cookie:
            data.update(parse_cookie_data(cookie))
        else:
            data["base_url"] = await get_baseurl(request, "OAUTH_RedirectUrl", entity_id)
            data['oauth_redirect'] = f'https://{data["base_url"]}{api_prefix}/{entity_id}/login'
    else:
        data["base_url"] = await get_baseurl(request, "OAUTH_RedirectUrl", entity_id)
        data['oauth_redirect'] = f'https://{data["base_url"]}{api_prefix}/{entity_id}/login'

    if 'rpt' in data:
        includes = ",".join([v for k, v in data['rpt'].items() if k.startswith("includes")])
        excludes = ",".join([v for k, v in data['rpt'].items() if k.startswith("excludes")])
        data['rpt']['includes'] = includes
        data['rpt']['excludes'] = excludes

    return data


def parse_cookie_data(cookie):
    if isinstance(cookie, bytes):
        cookie = cookie.decode()
    parts = cookie.split("$$_##_##_$$")
    rpt_data = decode_rpt(parts[0])
    id_auth_token = parts[1] if len(parts) > 1 else ""
    return {'rpt': rpt_data, 'id_auth_token': id_auth_token}


def decode_rpt(token):
    if "=====" in token:
        payload = token.split('.')[1] + '====='
    else:
        payload = token
    return json.loads(base64.urlsafe_b64decode(payload).decode())


# @app.get("/api/login")
async def login_old(request: fastapi.Request, code: typing.Optional[str] = None):
    return await login(request, code, urdhva_base.ctx["entity_id"])


# @app.get("/api/{entity_id}/login")
async def login(request: fastapi.Request, code: typing.Optional[str] = None,
                entity_id: typing.Optional[str] = ""):
    if not entity_id:
        entity_id = urdhva_base.ctx["entity_id"]

    if not code:
        return fastapi.responses.JSONResponse({"status": "Invalid parameters"}, 403)

    auth = await get_customer_authentication_extension(entity_id)
    client = await _get_http_client()

    try:
        master_token = await _get_master_token(client, auth)
        client_id = await _get_client_id(client, auth, entity_id, master_token)
        client_secret = await _get_client_secret(client, auth, entity_id, client_id, master_token)

        token_response, id_auth_token = await _get_access_token(
            request, client, auth, entity_id, client_secret, code
        )

        rpt_response = await _get_rpt_token(client, auth, entity_id, token_response["access_token"])

    except Exception as e:
        print(f"Login flow error: {e}")
        return fastapi.responses.JSONResponse({"status": "Keycloak Login Failed"}, 500)

    if rpt_response.status_code // 100 != 2:
        print("RPT Token:", rpt_response.status_code, rpt_response.text)

    response = fastapi.responses.RedirectResponse("/") if code else \
        fastapi.responses.JSONResponse({"status": "Logged in Successfully"}, 200)

    await _persist_cookie_and_session(response, token_response, id_auth_token, entity_id, code)
    return response


# -----------------------
# Helper Functions
# -----------------------

async def _get_http_client():
    return httpx.AsyncClient(verify=urdhva_base.settings.keycloak_verify_ssl, timeout=90)

async def _get_master_token(client, auth):
    login_url = f'{urdhva_base.settings.keycloak_internal_url}/{auth}/realms/master/protocol/openid-connect/token'
    login_data = {
        "client_id": "admin-cli",
        "username": urdhva_base.settings.keycloak_admin,
        "password": urdhva_base.settings.keycloak_password,
        "grant_type": "password"
    }
    resp = await client.post(login_url, data=login_data)
    return resp.json()["access_token"]

async def _get_client_id(client, auth, entity_id, token):
    url = f'{urdhva_base.settings.keycloak_internal_url}/{auth}/admin/realms/{entity_id}/clients?clientId={entity_id}_client'
    headers = {"Authorization": f'Bearer {token}'}
    resp = await client.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()[0]["id"]

async def _get_client_secret(client, auth, entity_id, client_id, token):
    url = f'{urdhva_base.settings.keycloak_internal_url}/{auth}/admin/realms/{entity_id}/clients/{client_id}/client-secret'
    headers = {"Authorization": f'Bearer {token}'}
    resp = await client.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["value"]

async def _get_access_token(request, client, auth, entity_id, client_secret, code):
    base_url = await get_baseurl(request, "OAUTH_RedirectUrl", entity_id)
    redirect_url = f'https://{base_url}/api/{entity_id}/login'
    data = {
        'grant_type': 'authorization_code',
        'client_id': f'{entity_id}_client',
        'client_secret': client_secret,
        'redirect_uri': redirect_url,
        'code': code
    }
    url = f'{urdhva_base.settings.keycloak_internal_url}/{auth}/realms/{entity_id}/protocol/openid-connect/token'
    resp = await client.post(url, data=data)
    resp.raise_for_status()
    token_json = resp.json()
    return token_json, token_json.get("id_token", "")

async def _get_rpt_token(client, auth, entity_id, access_token):
    url = f'{urdhva_base.settings.keycloak_internal_url}/{auth}/realms/{entity_id}/protocol/openid-connect/token'
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
        "audience": f'{entity_id}_client',
    }
    headers = {"Authorization": f'Bearer {access_token}'}
    return await client.post(url, data=data, headers=headers)

async def _persist_cookie_and_session(response, token_response, id_auth_token, entity_id, code):
    cookie_id = str(uuid.uuid4())
    redis_client = await urdhva_base.redispool.get_redis_connection()
    rkey = f"{entity_id}_SessionData_{cookie_id}"

    f = Fernet(urdhva_base.settings.fernet_key)
    d = {"entity_id": entity_id, "cookie_id": cookie_id, "base_url": await get_baseurl_from_token(token_response)}
    cookie_key = f.encrypt(json.dumps(d).encode()).decode()

    ttl = 3 * 60 * 60 if not code else 24 * 60 * 60
    token_data = token_response["access_token"]
    if id_auth_token:
        token_data += "$$_##_##_$$" + id_auth_token

    await redis_client.setex(rkey, ttl, token_data)

    response.set_cookie(cookie_name, cookie_key,
                        httponly=urdhva_base.settings.session_httponly,
                        secure=urdhva_base.settings.session_secure,
                        samesite=urdhva_base.settings.session_same_site)

async def get_baseurl_from_token(token_response):
    # fallback for base_url if needed
    return token_response.get("base_url", "")

@app.get(f"{api_prefix}/logout")
async def logout(request: fastapi.Request):
    response = fastapi.responses.HTMLResponse("", 401)
    cookie_id = request.cookies.get(cookie_name, None)
    if cookie_id:
        try:
            f = Fernet(urdhva_base.settings.fernet_key)
            d = json.loads(f.decrypt(cookie_id.encode()).decode())
            cookie_id = d["cookie_id"]
        except Exception as e:
            print(e)
        redis_client = await urdhva_base.redispool.get_redis_connection()
        rkey = f"algo_fusion_SessionData_{cookie_id}"
        await redis_client.delete(rkey)
    response.delete_cookie(cookie_name, httponly = urdhva_base.settings.session_httponly,
                           secure=urdhva_base.settings.session_secure, samesite=urdhva_base.settings.session_same_site)
    # Need to clear dashboard sessions
    return response


@app.get(f"{api_prefix}"+"/{entity_id}/authorize")
async def authorize(request: fastapi.Request, entity_id: str):
    base_url = await get_baseurl(request, "OAUTH_RedirectUrl", entity_id)
    redis_client = await urdhva_base.redispool.get_redis_connection()
    oauth_redirect_url = f'https://{base_url}/api/{entity_id}/login'
    if await redis_client.hget(f"{entity_id}_domainMapping", request.base_url.hostname):
        await redis_client.hget(f"{entity_id}_domainMapping", request.base_url.hostname)
        oauth_redirect_url = f'https://{request.base_url.hostname}/api/{entity_id}/login'
    redis_client = await urdhva_base.redispool.get_redis_connection()
    data = await redis_client.hget(f"{entity_id}_domainMapping", request.base_url.hostname)
    if data:
        base_url = json.loads(data)["base_url"]
    redirect_url = f'https://{base_url}/{await get_customer_authentication_extension(entity_id)}' \
                   f'/realms/{entity_id}/protocol/openid-connect/auth?client_id={entity_id}' \
                   f'_client&response_type=code&redirect_uri={oauth_redirect_url}&scope=email openid&state=123'
    return RedirectResponse(url=redirect_url)


@app.get(f"{api_prefix}/session/me")
async def me(request: fastapi.Request):
    rpt = urdhva_base.context.context.get('rpt', {})
    resp = {"is_authenticated": False}
    algo_role = rpt.get("algo_role", [])
    permission_data = await get_permission()
    if permission_data["is_authenticated"]:
        roles = await urdhva_base.postgresmodel.BasePostgresModel.get_aggr_data(
            f"""select * from roles where name='{algo_role[0]}'""")
        roles = roles.get('data',[])
        resp["menu_items"] = roles[0]["menu_items"] if roles and "menu_items" in roles[0] else []
        resp = {"permissions": permission_data["allowed_roles"], "is_authenticated": True, "menu_items": resp["menu_items"] }
        base_keys = ["first_name", "last_name", "allowed_roles", "email", "employee_id", "algo_role"]
        permission_keys = ["org_id", "perspective_ids"]
        resp.update({key: rpt.get(key, '') for key in base_keys})
        resp.update({key: rpt.get(key, []) for key in permission_keys})
    return resp


@app.get(f"{api_prefix}/ping")
async def ping():
    return "pong"


def convert_role_dict(role_data):
    role_dict = {}
    if "authorization" in role_data and "permissions" in role_data['authorization']:
        for role_scop in role_data['authorization']['permissions']:
            if role_scop['rsname'].lower() not in role_dict:
                role_dict[role_scop['rsname'].lower()] = role_scop['scopes']
    return role_dict


handler = Mangum(app)
