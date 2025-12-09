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
from datetime import datetime,timedelta
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

        # creating  the startdate  and duedate
        startdate = datetime.now()
        duedate = startdate + timedelta(days=1)

        tdata.update({
            'ticket_id':t_id,
            'ticket_name':f'ticket_name {t_id}', # creating the ticket name
            'ticket_status':data.ticket_status,
            'start_date':startdate,
            'due_date':duedate,
            'ticket_status':Status.OPEN.value,
            'parent_ticket_id':'0'
        })

        ticket_state_str = tdata.get('ticket_state')
        print("ticket_state_str-->",ticket_state_str)

         #inserting data into the table
        result = await ticketing_model.TicketingCreate(**tdata).create()

        history = {
                    "ticket_id": result['id'],
                    # "changed_by": "",
                    "field_name": "ticket",
                    # "old_value": "",
                    "new_value": "Created the card"
                    }
        tkt_hist = await TicketHistoryCreate(**history).create()
        print("History created",tkt_hist)

        return {
            'Message':'Tickets Created Successfully',
            'Ticket':tdata,
            'id':result['id']
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
        if not os.path.exists(target_dir):#creating the path if not existed
            os.makedirs(target_dir)

        temp_file_path = os.path.join(target_dir,uploadfile.filename)
        
        # writing the file
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

            #checking the ticket is present or not
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

            
            await Ticketing(**{"id":id,**attachment_file}).modify()# updaiting the file attachments


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


async def tikt_history(u_id,feild_name,old_val,new_val):
    tkt_hist = {
                'ticket_id':u_id,
                'field_name':feild_name,
                'old_value':str(old_val),
                'new_value':str(new_val)
            }
    
    await TicketHistoryCreate(**tkt_hist).create()


# Action update_ticket
@router.post('/update-ticket', tags=['Ticketing'])
async def ticketing_update_ticket(data: ticketing_model.TicketingUpdateTicketParams):
    try:
        tdata = data.__dict__
        print(tdata)

        #To fetch the ticket
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id = {data.update_id}"
        params.limit = 1

        res = await Ticketing.get_all(params,resp_type='plain')

        print('res>>>>',res)

        if not res or len(res.get("data",[])) == 0:
            raise HTTPException(status_code=404, detail="Ticket not Found")
                
        result = res["data"][0]

        if not result: 
            return {
                "status":False,
                "message":"Ticket not found"
            }
        
        # validating user is present or not
        params.q = f"id={data.assignee_id}"

        assigne = await Users.get_all(params,resp_type='plain')
        reporter = await Users.get_all(params,resp_type='plain')

        assigne_existing = assigne.get('data',[])[0]

        reporter_existing = reporter.get('data',[])[0]
        # reporter_name = reporter_existing['first_name'] +' '+ reporter_existing['last_name']
        # print('reporter_name>>>>',reporter_name)


        if not assigne_existing or not reporter_existing:
            return {
                'status':False,
                'message':"employee doesnot exist"
            }
        
        #below is the logic for, if any changes are made storing it in ticket history table

        #closing the ticket satet if it is in ['Resolved','Cancelled']
        if data.ticket_state in ['Resolved','Cancelled']:
            data.ticket_status = 'Close'

        #creating summary history
        if result['summary'] != data.summary:
            await tikt_history(data.update_id,'Summary',result['summary'],data.summary)
            
        #creating description history
        if result['description'] != data.description:
            await tikt_history(data.update_id,'Description',result['description'],data.description)

        #creating description history
        if result['assignee_id'] != data.assignee_id:

            new_assigne_name = assigne_existing['first_name'] +' '+ assigne_existing['last_name']
            # params = urdhva_base.queryparams.QueryParams()
            params.q = f"id={result['assignee_id']}"
            new_assigne = await Users.get_all(params,resp_type='plain')
            res = new_assigne.get('data',[])[0]
            old_assigne_name = res['first_name']+' '+ res['last_name']
            print('old_assigne_name>>',old_assigne_name)
            print('new_assigne_name>>',new_assigne_name)

            await tikt_history(data.update_id,'Assignee',result['assignee_id'],data.assignee_id)

        #creating reporter history
        if result['reporter_id'] != data.reporter_id:
            await tikt_history(data.update_id,'Reporter',result['reporter_id'],data.reporter_id)
        
        #creating due_date history
        if result['due_date'] != data.due_date:
            await tikt_history(data.update_id,'Due_Date',result['due_date'],data.due_date)

        #creating file_attachment history
        if result['file_attachment'] != data.file_attachment:
            await tikt_history(data.update_id,'file_attachment',result['file_attachment'],data.file_attachment)

        # updating the ticket with new values
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




# # Action create_ticket
# @router.post('/create-ticket', tags=['Ticketing'])
# async def ticketing_create_ticket(data: ticketing_model.TicketingCreateTicketParams):

#     try:
#         tdata = data.__dict__
#         print("tdata--->",tdata)

#         # params = urdhva_base.queryparams.QueryParams()
#         # params.q = f"id='{data.assignee_id}'"
#         # params.limit = 1

#         # assigne = await Users.get_all(params,resp_type='plain')
#         # reporter = await Users.get_all(params,resp_type='plain')

#         # assigne_existing = assigne.get('data',[])
#         # reporter_existing = reporter.get('data',[])


#         # if not assigne_existing or reporter_existing:
#         #     return {
#         #         'status':False,
#         #         'message':"User doesnot exist"
#         #     }
        
#         t_id = generate_ticket_id()

#         tdata['ticket_id'] = t_id
#         tdata['ticket_name'] = f'ticket_name {t_id}' # creating the ticket name


#         startdate_str = tdata.get('startdate')

#         # updating the startdate to particular format
#         # if startdate_str:
#         #     try:
#         #         startdate = parser.isoparse(startdate_str)
#         #         print("startdate1-->",startdate)
#         #     except Exception:
#         #         try:
#         #             startdate = datetime.strptime(startdate,"%Y-%m-%d %H:%M:%S")
#         #             print("startdate2-->",startdate)
#         #         except ValueError:
#         #             try:
#         #                 startdate = datetime.strptime(startdate,"%Y-%m-%d")
#         #                 print("startdate3-->",startdate)
#         #             except ValueError:
#         #                 startdate = None


#         # creating  the startdate  and duedate
#         startdate = datetime.now()
#         duedate = startdate + timedelta(days=1)

#         tdata.update({
#             'ticket_status':data.ticket_status,
#             'start_date':startdate,
#             'due_date':duedate,
#             'ticket_status':Status.OPEN.value,
#             'parent_ticket_id':'0'
#             # 'ticket_history': []
#         })

#         ticket_state_str = tdata.get('ticket_state')
#         print("ticket_state_str-->",ticket_state_str)

#         # based on ticket state getting action type
#         # action_type_str = TicketType[ticket_state_str.name].value 
#         # print("action_type_str-->",action_type_str)

#         # processed_time = datetime.now()


#          #inserting data into the table
#         result = await ticketing_model.TicketingCreate(**tdata).create()

#         history = {
#                     "ticket_id": result['id'],
#                     # "changed_by": "",
#                     "field_name": "ticket",
#                     # "old_value": "",
#                     "new_value": "Created the card"
#                     }
#         tkt_hist = await TicketHistoryCreate(**history).create()
#         print("History created")

#         return {
#             'Message':'Tickets Created Successfully',
#             'Ticket':tdata,
#             'id':result['id']
#         }
#     except Exception as e:
#         return {
#             'error':str(e)
#         }    

