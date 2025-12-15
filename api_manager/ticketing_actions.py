import urdhva_base
import traceback
import os, uuid
import api_manager
import uuid
from ticketing_enum import TicketType, Status, State
from dateutil import parser
from datetime import datetime
import ticketing_model
from ticketing_model import *
from fastapi import FastAPI,APIRouter, Form, UploadFile, File,HTTPException
from datetime import datetime,timedelta
from typing import Optional
from urdhva_base import QueryParams
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
   
        # checking and creating  the  parent_ticket_id   
        if tdata['parent_ticket_id']:
            params = QueryParams()
            params.q = f"id={data.parent_ticket_id}"
            params.limit = 1
            res = await Ticketing.get_all(params,resp_type='plain')
            if res.get('data',[]):
                ptid = tdata['parent_ticket_id']
            else:
                return {
                    'status':False,
                    'message':"Parent ticket not found"
                }
        else:
            ptid = '0'

        #setting the start_date if not given
        if not data.start_date:
            startdate = datetime.now()
        else:
            startdate = data.start_date
            
        #setting the due_date if not given
        if not data.due_date:
            duedate = datetime.now() + timedelta(days=1)
        else:
            duedate = data.due_date          
        

        tdata.update({
            'ticket_id':t_id,
            'ticket_name':f'ticket_name {t_id}', # creating the ticket name
            'ticket_status':data.ticket_status,
            'start_date':startdate,
            'due_date':duedate,
            'summary':data.summary,
            'description':data.description,
            'ticket_status':Status.OPEN.value,
            'parent_ticket_id':ptid,
            'progress':data.progress
        })

         #inserting data into the table
        result = await ticketing_model.TicketingCreate(**tdata).create()


        #creating history when new ticket is inserted
        history = {
                    "ticket_id": result['id'],
                    # "changed_by": "",
                    "field_name": "Ticket",
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
        # print('res>>>>',res)

        if not res or len(res.get("data",[])) == 0:
            raise HTTPException(status_code=404, detail="Ticket not Found")
                
        result = res["data"][0]

        print("result>>>>>>>>",result)

        if not result: 
            return {
                "status":False,
                "message":"Ticket not found"
            }
        
        #below is the logic for, if any changes are made storing it in ticket history table


        # validating assignee is present or not
        if data.assignee_id:
            params.q = f"id={data.assignee_id}"
            assigne = await Users.get_all(params,resp_type='plain')

            print('assigne',assigne)

            # assigne_existing = assigne.get('data',[])
            if not assigne or len(assigne.get("data",[])) == 0:
                raise HTTPException(status_code=404, detail="Assignee not Found")
            
            #creating description history
            if result['assignee_id'] != data.assignee_id:
                await tikt_history(data.update_id,'Assignee',result['assignee_id'],data.assignee_id)
            

        # validating reporter is present or not
        if data.reporter_id:
            params.q = f"id={data.reporter_id}"
            reporter = await Users.get_all(params,resp_type='plain')
            # reporter_existing = reporter.get('data',[])

            if not reporter or len(reporter.get("data",[])) == 0:
                raise HTTPException(status_code=404, detail="Reporter not Found")
            
            #creating reporter history
            if result['reporter_id'] != data.reporter_id:
                await tikt_history(data.update_id,'Reporter',result['reporter_id'],data.reporter_id)
            

        #creating summary history
        if result['summary'] != data.summary:
            await tikt_history(data.update_id,'Summary',result['summary'],data.summary)
            
        #creating description history
        if result['description'] != data.description:
            await tikt_history(data.update_id,'Description',result['description'],data.description)

        #creating ticket_status history
        if result['ticket_status'] != data.ticket_status:
            await tikt_history(data.update_id,'Status',result['ticket_status'],data.ticket_status)

        #creating ticket_severity history
        if result['ticket_severity'] != data.ticket_severity:
            await tikt_history(data.update_id,'Severity',result['ticket_severity'],data.ticket_severity.value)

        #creating ticket_state history
        if result['ticket_state'] != data.ticket_state:
            await tikt_history(data.update_id,'State',result['ticket_state'],data.ticket_state.value)

        #creating parent_ticket_id history
        if result['parent_ticket_id'] != data.parent_ticket_id:
            await tikt_history(data.update_id,'Parent_Ticket',result['parent_ticket_id'],data.parent_ticket_id)
           

        dt_str = data.due_date
        dt2_str = result['due_date']

        dt1 = datetime.fromisoformat(str(dt_str))   # convert string to datetime
        dt2 = datetime.fromisoformat(str(dt2_str))

        new_duedate = dt1.date() #extract date
        old_duedate = dt2.date()

        print('dates>>>>',new_duedate,old_duedate)

        #creating due_date history
        if old_duedate != new_duedate:
            await tikt_history(data.update_id,'Due_Date',result['due_date'],data.due_date)

        # #creating file_attachment history
        # if result['file_attachment'] != data.file_attachment:
        #     await tikt_history(data.update_id,'file_attachment',result['file_attachment'],data.file_attachment)


        #changing the ticket_status based on the ticket_state
        if data.ticket_state in ['Resolved','Cancelled']:
            data.ticket_status = 'Close'

        elif data.ticket_state in ['ToDo','Re Open']:
            data.ticket_status = 'Open'
        
        else:
            data.ticket_status = 'Pending'



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

                # new_assigne_name = assigne_existing['first_name'] +' '+ assigne_existing['last_name']
                # # params = urdhva_base.queryparams.QueryParams()
                # params.q = f"id={result['assignee_id']}"
                # new_assigne = await Users.get_all(params,resp_type='plain')
                # res = new_assigne.get('data',[])[0]
                # old_assigne_name = res['first_name']+' '+ res['last_name']
                # print('old_assigne_name>>',old_assigne_name)
                # print('new_assigne_name>>',new_assigne_name)


# ticket_history 
	# Ticket creation
	# Summary
	# Description
	# Ticket State
	# Ticket Status
	# Ticket Severity
	# Assignee
	# Reporter
	# Parent_ticket
	# Due date


# # Action update_ticket
# @router.post('/update-ticket', tags=['Ticketing'])
# async def ticketing_update_ticket(data: ticketing_model.TicketingUpdateTicketParams):
#     try:   
#         tdata = data.__dict__
#         print(tdata)

#         #To fetch the ticket
#         params = urdhva_base.queryparams.QueryParams()
#         params.q = f"id = {data.update_id}"
#         params.limit = 1

#         res = await Ticketing.get_all(params,resp_type='plain')
#         # print('res>>>>',res)

#         if not res or len(res.get("data",[])) == 0:
#             raise HTTPException(status_code=404, detail="Ticket not Found")
                
#         result = res["data"][0]

#         if not result: 
#             return {
#                 "status":False,
#                 "message":"Ticket not found"
#             }
        
#         update_data = data.dict(exclude_unset=True)

#         # 3. Update only those fields
#         for field, value in update_data.items():
#             setattr(result, field, value)

#         print('update_data>>>>>>>',update_data)
            
        #below is the logic for, if any changes are made storing it in ticket history table


        # # validating assignee is present or not
        # if data.assignee_id:
            
        #     params.q = f"id={data.assignee_id}"
        #     assigne = await Users.get_all(params,resp_type='plain')

        #     print('assigne',assigne)

        #     # assigne_existing = assigne.get('data',[])
        #     if not assigne or len(assigne.get("data",[])) == 0:
        #         raise HTTPException(status_code=404, detail="Assignee not Found")
            
        #     #creating description history
        #     if result['assignee_id'] != data.assignee_id:
        #         await tikt_history(data.update_id,'Assignee',result['assignee_id'],data.assignee_id)
        #     u_assigne = data.assignee_id

        # else:
        #     u_assigne = result['assignee_id']
            

        # # validating reporter is present or not
        # if data.reporter_id:
        #     params.q = f"id={data.reporter_id}"
        #     reporter = await Users.get_all(params,resp_type='plain')
        #     # reporter_existing = reporter.get('data',[])

        #     if not reporter or len(reporter.get("data",[])) == 0:
        #         raise HTTPException(status_code=404, detail="Reporter not Found")
            
        #     #creating reporter history
        #     if result['reporter_id'] != data.reporter_id:
        #         await tikt_history(data.update_id,'Reporter',result['reporter_id'],data.reporter_id)
        #     u_reporter = data.reporter_id
        
        # else:
        #     u_reporter = result['reporter_id']
            

        # #creating summary history
        # if data.summary:
        #     if result['summary'] != data.summary:
        #         await tikt_history(data.update_id,'Summary',result['summary'],data.summary)
        #         u_summary = data.summary
        # else:
        #     u_summary = result['summary']
            
        # #creating description history
        # if data.description:
        #     if result['description'] != data.description:
        #         await tikt_history(data.update_id,'Description',result['description'],data.description)
        #         u_description = data.description
        # else:
        #     u_description = result['description']

        # #creating ticket_status history
        # if data.ticket_status:
        #     if data.ticket_status:
        #         if result['ticket_status'] != data.ticket_status:
        #             await tikt_history(data.update_id,'Status',result['ticket_status'],data.ticket_status)
        #         u_status = data.ticket_status
        # else:
        #     u_status = result['ticket_status']
        # #creating ticket_severity history
        # if result['ticket_severity'] != data.ticket_severity:
        #     await tikt_history(data.update_id,'Severity',result['ticket_severity'],data.ticket_severity.value)

        # #creating ticket_state history
        # if result['ticket_state'] != data.ticket_state:
        #     await tikt_history(data.update_id,'State',result['ticket_state'],data.ticket_state.value)

        # #creating parent_ticket_id history
        # if result['parent_ticket_id'] != data.parent_ticket_id:
        #     await tikt_history(data.update_id,'Parent_Ticket',result['parent_ticket_id'],data.parent_ticket_id)
           

        # dt_str = data.due_date
        # dt2_str = result['due_date']

        # dt1 = datetime.fromisoformat(str(dt_str))   # convert string to datetime
        # dt2 = datetime.fromisoformat(str(dt2_str))

        # new_duedate = dt1.date() #extract date
        # old_duedate = dt2.date()

        # print('dates>>>>',new_duedate,old_duedate)

        # #creating due_date history
        # if old_duedate != new_duedate:
        #     await tikt_history(data.update_id,'Due_Date',result['due_date'],data.due_date)

        # #creating file_attachment history
        # if result['file_attachment'] != data.file_attachment:
        #     await tikt_history(data.update_id,'file_attachment',result['file_attachment'],data.file_attachment)


        # #changing the ticket_status based on the ticket_state
        # if data.ticket_state in ['Resolved','Cancelled']:
        #     data.ticket_status = 'Close'

        # elif data.ticket_state in ['ToDo','Re Open']:
        #     data.ticket_status = 'Open'
        
        # else:
        #     data.ticket_status = 'Pending'



        # updating the ticket with new values
        # res = await Ticketing(**{"id":data.update_id,**tdata}).modify() 
    #     tdata.pop('update_id')
    #     return {
    #         "status": True,
    #         "message": "Ticket updated successfully",
    #     }
    
    # except Exception as e:
    #     return {
    #         "status":False,
    #         "message":str(e)
    #     }




