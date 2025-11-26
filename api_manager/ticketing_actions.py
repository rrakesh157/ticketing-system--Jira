import urdhva_base
import traceback
import os, uuid
import api_manager
import uuid
from ticketing_enum import TicketType, Status, State
from dateutil import parser
import ticketing_model
from ticketing_model import *
from fastapi import FastAPI,APIRouter, Form, UploadFile, File,HTTPException
from datetime import datetime
from typing import Optional
from urdhva_base import BasePostgresModel
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()

router = APIRouter(prefix='/ticketing')

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

def generate_ticket_id():
    return f"TK-{str(uuid.uuid4())[:6]}"  # TK-a13f92

# Action create_ticket
@router.post('/create-ticket', tags=['Ticketing'])
async def ticketing_create_ticket(data: ticketing_model.TicketingCreateTicketParams):

    try:
        tdata = data.__dict__
        print("tdata--->",tdata)

        t_id = generate_ticket_id()

        tdata['ticket_id'] = t_id
        tdata['ticket_name'] = f'ticket_name {t_id}'


        startdate_str = tdata.get('startdate')
        if startdate_str:
            try:
                startdate = parser.isoparse(startdate_str)
                print("startdate1-->",startdate)
            except Exception:
                try:
                    startdate = datetime.strptime(startdate,"%Y-%m-%d %H:%M:%S")
                    print("startdate2-->",startdate)
                except ValueError:
                    try:
                        startdate = datetime.strptime(startdate,"%Y-%m-%d")
                        print("startdate3-->",startdate)
                    except ValueError:
                        startdate = None
        else:
            startdate = None

        tdata.update({
            'ticket_status':Status.OPEN.value,
            'startdate':startdate,
            'ticket_history': []
        })

        ticket_state_str = tdata.get('ticket_state')
        print("ticket_state_str-->",ticket_state_str)


        action_type_str = TicketType[ticket_state_str.name].value # based on ticket state getting action type
        print("action_type_str-->",action_type_str)

        processed_time = datetime.now()
        tdata['ticket_history'].append({ # adding ticket history
            "processed_time":processed_time.isoformat(),
            "allocated_time":startdate.isoformat() if startdate else processed_time.isoformat(),
            "action_msg":f"Ticket is created and is in {action_type_str} state",
            "action_type":action_type_str})
        

        await ticketing_model.TicketingCreate(**tdata).create() #inserting data into the table

        return {
            'Message':'Tickets Created Successfully',
            'Ticket':tdata
        }
    except Exception as e:
        return {
            'error':str(e)
        }    



# Action attach_file
@router.post('/attach-file', tags=['Ticketing'])
async def ticketing_attach_file(
    ticket_id: Optional[str] = Form(None),
    uploadfile: UploadFile = File(None)):
    
    # creating the directory if doesn't exist
    try:
        print("comming...",urdhva_base.settings.ticketing_attachments)
        target_dir = urdhva_base.settings.ticketing_attachments
        print("target_dir",target_dir)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        temp_file_path = os.path.join(target_dir,uploadfile.filename)
        
        with open(temp_file_path,"wb") as f:
            f.write(await uploadfile.read())
        
        print("File uploaded successfully at:",temp_file_path)
        print("ticket_id-->",ticket_id)


        file_uuid = str(uuid.uuid4())

        attachment_file = {
            "file_attachment":[temp_file_path],
            "file_attachment_name":uploadfile.filename,
            "file_attachment_id":file_uuid
        }
        print("attachment_file>>>",attachment_file)

        if ticket_id:
            params = urdhva_base.queryparams.QueryParams()
            params.q = f"id='{ticket_id}'"
            params.limit = 1
            result = await Ticketing.get_all(params,resp_type='plain')
            res = result.get("data",[])

            print("res>>>",res)
            if not res:
                return {
                    "status":False,
                    "message":"Ticket not found"
                }
            
            id = result.get('data',[])[0]['id']
            print("iddddddddd",id)

            
            await Ticketing(**{"id":id,**attachment_file}).modify()
        print("not entering")


        return {
            "status":True,
            "message":f"File {uploadfile.filename} saved successfully",
            "file_attachment":temp_file_path,
            "file_attachment_name":uploadfile.filename,
            "file_attachment_id":file_uuid,
            "content_type":uploadfile.content_type
        }

    except Exception as e:
        return {
            "status":False,
            "message":f"Error saving file {str(e)}"
        }




# Action update_ticket
@router.post('/update-ticket', tags=['Ticketing'])
async def ticketing_update_ticket(data: ticketing_model.TicketingUpdateTicketParams):
    try:
        tdata = data.__dict__
        print(tdata)
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.update_id}'"
        params.limit = 1
        result = await Ticketing.get_all(params,resp_type='plain')
        res = result.get("data",[])
        if not res:
            return {
                "status":False,
                "message":"Ticket not found"
            }
        res = await Ticketing(**{"id":data.update_id,**tdata}).modify()
        tdata.pop('update_id')
        return {
            "status": True,
            "message": "Ticket updated successfully",
        }
        
    except Exception as e:
        return {
            "status":False,
            "message":str(e)
        }
