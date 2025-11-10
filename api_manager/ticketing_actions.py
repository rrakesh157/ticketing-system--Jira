import urdhva_base
import traceback
import os, uuid
import api_manager
import random
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
    global t_id 
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


    action_type_str = ticket_state_str.value # based on ticket state getting action type
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
    

# Action update_ticket
@router.post('/update-ticket', tags=['Ticketing'])
async def ticketing_update_ticket(data: ticketing_model.TicketingUpdateTicketParams):
    data_dict = data.__dict__
    # print("data_dict-->",data_dict)
    ticket_id = data_dict["update_id"]

    #checking wether ticket is there or not
    params = urdhva_base.queryparams.QueryParams()
    params.q = f"ticket_id='{ticket_id}'"
    params.limit = 1
    params.fields = ["id","ticket_id","ticket_state"]
    ticket_records = await Ticketing.get_all(params,resp_type='plain')

    id = ticket_records.get("data")[0].get("id") if ticket_records.get("data") else None
    print("id-->",id)

    print("ticket_records-->",ticket_records)

    if not ticket_records or not ticket_records.get("data"):
        return {"status":False,"message":f"Ticket '{ticket_id}'not found"}
    
    existing_ticket = ticket_records["data"][0]

    procesed_time  = datetime.now()
    existing_history = existing_ticket.get("ticket_history",[]) or []
    last_allocated_time = procesed_time.isoformat()

    print("existing_history-->",existing_history)
    print("last_allocated_time-->",last_allocated_time)

    if existing_history:
        last_allocated_time = existing_history[-1].get("processed_time",procesed_time.isoformat())

    # -------------updateticket history-------------

    ticket_state = data_dict.get("ticket_state") # "In Progress"
    action_type_enum = TicketType[ticket_state.name].value # ticketinprogress
    print("action_type_enum-->",action_type_enum)

     
    ticket_update_entry = {
        "action_msg":f"Ticket updated, state changed to {ticket_state}",
        "action_type":action_type_enum,
        "allocated-time":last_allocated_time,
        "proccessed_time":procesed_time.isoformat()
    }
    updated_history = existing_history + [ticket_update_entry]

    print("updated_history-->",updated_history)

    if ticket_state in ["Resolved", "Cancelled"]:
        data_dict["ticket_status"] = "Close"
    else:
        data_dict["ticket_status"] = "Open"

    data_dict["ticket_history"] = updated_history

    await Ticketing(id = id, **data_dict).modify()

    return {
        "status":True,
        "message":f"Ticket {ticket_id} updated successfully",
        "updated_fields":data_dict
    }




# Action Attach_File
@router.post('/attach-file', tags=['Ticketing'])
async def ticketing_attach_file(
    ticket_id: Optional[str] = Form(None),
    tid:Optional[str] = Form(None),
    uploadfile: UploadFile = File(None)
):
    
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
        print("tid-->",tid)

        if ticket_id and tid:
            query = f"ticket_id='{ticket_id}' and id = {tid}"
            params = urdhva_base.queryparams.QueryParams(q=query)
            result = await Ticketing.get_all(params,resp_type='plain')
            res = result.get("data",[])
            if not res:
                return {
                    "status":False,
                    "message":"Ticket not found"
                }
            await Ticketing(**{"id":res[0].get("id"),"file_attachment":[temp_file_path]}).modify()

        file_uuid = str(uuid.uuid4())
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



# Action delete_ticket
@router.post('/delete-ticket', tags=['Ticketing'])
async def ticketing_delete_ticket(data: ticketing_model.TicketingDeleteTicketParams):
    await Ticketing.delete(data.delete_id)
    return {
        "status":True,
        "message":"Ticket Deleted successfully",
        "data":data.delete_id
    }




# Action delete_file_attachment
@router.post('/delete-file-attachment', tags=['Ticketing'])
async def ticketing_delete_file_attachment(data: ticketing_model.TicketingDeleteFileAttachmentParams):
    ticket_id = data.ticket_id

    #To fetch the ticket
    params = urdhva_base.queryparams.QueryParams()
    params.q = f"ticket_id = '{ticket_id}'"
    params.limit = 1

    res = await Ticketing.get_all(params,resp_type='plain')

    if not res or len(res.get("data",[])) == 0:
        raise HTTPException(status_code=404, detail="Ticket not Found")
    
    print(">>>>>>>>>>>>>>>>",res)
    
    db_record = res["data"][0]

    file_list = db_record.get('file_attachment') or []

    for file_path in file_list:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


    update_payload = {
        "file_attchment" : [],
        "file_attachment_name":"",
        "file_attachment_id":""
    }

    await Ticketing(**{"ticket_id":ticket_id,**update_payload}).modify()
    return {
        "status":True,
        'message':'file attachment deleted',
        'data':ticket_id
    }



# Action Attach_File
@router.post('/attach-file', tags=['Ticketing'])
async def ticketing_attach_file(data: ticketing_model.TicketingAttachFileParams):
    ...


# Action Attach_File
@router.post('/attach-file', tags=['Ticketing'])
async def ticketing_attach_file(data: ticketing_model.TicketingAttachFileParams):
    ...


# Action Attach_File
@router.post('/attach-file', tags=['Ticketing'])
async def ticketing_attach_file(data: ticketing_model.TicketingAttachFileParams):
    ...
