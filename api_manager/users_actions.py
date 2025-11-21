

import ticketing_enum
import ticketing_model
import urdhva_base
import uuid
from ticketing_model import Users,UsersCreate
from fastapi import APIRouter,HTTPException
from fastapi import FastAPI, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr


router = APIRouter(prefix='/users')






async def send_plain_email(email_list, fm,password):
    message = MessageSchema(
        subject="Your Login Credentials",
        recipients=email_list,  
        body=f"""This is your link to signup page.
                email = {email_list},
                password = {password}""",
        subtype="plain"
    )
    await fm.send_message(message)
    return True



# Action add_user
@router.post('/add-user', tags=['Users'])
async def users_add_user(data: ticketing_model.UsersAddUserParams):
    try:
        udata = data.model_dump()
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"email='{data.email[0]}'"
        params.limit = 1
        existing = await Users.get_all(params,resp_type='plain')

        existing = existing.get('data',[])

        # if existing:
        #     return {
        #         "status":False,
        #         "message":"User already exist"
        #     }

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

        udata.update({
            "email": data.email[0],
            "role": data.role,
            "password":password,
            "is_active":True
        })

        await send_plain_email(data.email, fm,password)

        # Save user
        await UsersCreate(**udata).create()

        return {
            "status": True,
            "message": "Mail sent and user created successfully"
        }

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }






