
import ticketing_enum
import ticketing_model
import urdhva_base
import uuid
from pwdlib import PasswordHash
from ticketing_model import Users,UsersCreate,UsersSignInParams,UsersSignUpParams
from fastapi import APIRouter,HTTPException
from fastapi import FastAPI, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from email_validator import validate_email, EmailNotValidError


router = APIRouter(prefix='/users')




async def send_plain_email(email_list, fm,password):
    message = MessageSchema(
        subject="Your Login Credentials",
        recipients=email_list,  
        body=f"""This is your link to signup page.
                email = {email_list[0]},
                password = {password}""",
        subtype="plain"
    )
    await fm.send_message(message)
    return True



# Action add_user
@router.post('/add-user', tags=['Users'])
async def users_add_user(data: ticketing_model.UsersAddUserParams):
    """
    creating users,
    sending mail,
    password hasing
    """


    try:
        valid = validate_email(data.email[0]) #it checks only .com value
        email = valid.email
        print("Valid email:", email)

    except EmailNotValidError as e:
        return {
            'status':False,
            'error':"Invalid Email"
        }


    try:
        udata = data.model_dump()
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"email='{data.email[0]}'"
        params.limit = 1
        existing = await Users.get_all(params,resp_type='plain')

        existing = existing.get('data',[])

        if existing:
            return {
                "status":False,
                "message":"User already exist"
            }

        conf = ConnectionConfig(
            MAIL_USERNAME="rakeshnani0415@gmail.com",
            MAIL_PASSWORD="plrk imfp lbwr hshn", 
            MAIL_FROM="rakeshnani0415@gmail.com",
            MAIL_PORT=587,
            MAIL_SERVER="smtp.gmail.com",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False
         )

        fm = FastMail(conf)

        
        password = f"{str(uuid.uuid4())[:6]}"

        print("password>>>>>>",password)

        udata.update({
            "email": data.email[0],
            "role": data.role,
            "password_hash":get_password_hash(password),
            "is_active":True
        })

        created = await UsersCreate(**udata).create()
        if not created:
            return {
            "status": False,
            "message": "Failed to create user"
        }

        email_sent = await send_plain_email(data.email, fm,password)

        return {
            "status": True,
            "message": "User created successfully" if email_sent else "User created but email sending failed",
        }

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }




password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)





# Action sign_in
@router.post('/sign-in', tags=['Users'])
async def users_sign_in(data: ticketing_model.UsersSignInParams):
    try:
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"email='{data.email.lower()}'"
        params.limit = 1
        existing = await Users.get_all(params,resp_type='plain')

        existing = existing.get('data',[])

        
        print("email>>>",data.email)
        print(existing)

        if not existing:
            
            return {
                "status":False,
                "message":"User does not exist"
            }
        verify_pass = verify_password(data.password,existing[0]['password_hash'])
        if not verify_pass:
            return {
                "status":False,
                "message":"Incorrect password"
            }
        
        return {
            'statu':True,
            'message':"Login successfully"
        }

        
    except Exception as e:
        return {
            'status':False,
            "error":str(e)
        }


# Action sign_up
@router.post('/sign-up', tags=['Users'])
async def users_sign_up(data: ticketing_model.UsersSignUpParams):
    """
    validating user in db,
    validating phone number (10 digit),
    updating the user details (password hashing)
    """
    try:
        udata = data.model_dump()
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"email='{data.email.lower()}'"
        params.limit = 1
        existing = await Users.get_all(params,resp_type='plain')

        existing = existing.get('data',[])
        if not existing:
            return {
                "status":False,
                "message":"User does not exist"
            }
    
        hashed_password = existing[0]["password_hash"]

        print("plain_password>>>",data.password)
        print("hashed_password>>>",hashed_password)

        
        if not verify_password(data.password,hashed_password):
            return {
                "status":False,
                "message":"Password incorrect"
            }

        
        if len(data.phone_number) == 10:
            udata.update({
                "first_name":data.first_name,
                "last_name":data.last_name,
                'user_id':f'UI-{str(uuid.uuid4())[:5]}',
                "Password_hash":get_password_hash(data.password),
                "phone_number":data.phone_number
                })
            
            resp = await Users(id=existing[0]['id'],**udata).modify()

            print("resp",resp)


            return {
                    "status":True,
                    "message":f"User {data.first_name} created successfully"
                }
        return {
            "status":False,
            "message":"phone number must be 10 digit"
        }
    
    except Exception as e:
        return {
            'status':False,
            'error':str(e)
        }

