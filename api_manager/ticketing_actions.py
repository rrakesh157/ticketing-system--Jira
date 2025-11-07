import urdhva_base
import traceback
import os, uuid
import api_manager
from ticketing_enum import TicketType
from dateutil import parser
import ticketing_model
from fastapi import APIRouter
from datetime import datetime
from urdhva_base import BasePostgresModel

router = APIRouter(prefix='/ticketing')


t_id = 1001

# Action create_ticket
@router.post('/create-ticket', tags=['Ticketing'])
async def ticketing_create_ticket(data: ticketing_model.TicketingCreateTicketParams):
    global t_id 
    tdata = data.__dict__
    print("tdata--->",tdata)

    tdata['ticket_id'] = f'TK - {str(t_id)}'
    tdata['ticket_name'] = f'ticket_name {t_id}'

    t_id += 1

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
        'startdate':startdate,
        'ticket_history': []
    })

    ticket_state_str = tdata.get('ticket_state')
    print("ticket_state_str-->",ticket_state_str)


    action_type_str = ticket_state_str.value
    print("action_type_str-->",action_type_str)

    # ticket_data =tdata.copy()

    processed_time = datetime.now()
    tdata['ticket_history'].append({
        "processed_time":processed_time.isoformat(),
        "allocated_time":startdate.isoformat() if startdate else processed_time.isoformat(),
        "action_msg":f"Ticket is created and is in {tdata['ticket_state']} state",
        "action_type":action_type_str})
   

   
    

    # tdata.update()

    

    

    await ticketing_model.TicketingCreate(**tdata).create()
    
    # await ticketing_model.TicketingCreate(**tdata).create()
    return True

    # params = urdhva_base.queryparams.QueryParams(q=query,limit=1000)

    # print(params)

    # # q="alert_section='hello and sap_id='432' and location_name='hyd'" search_text=None skip=0 limit=1000 sort=None fields=None view=None
    
    # return 
    # params.fields = ['sop_id','alert_section','sap_id','location_name','interlock_name','unique_id']

    # resp  = await BasePostgresModel.get_all()
    




# Action get_ticket_id
@router.post('/get-ticket-id', tags=['Ticketing'])
async def ticketing_get_ticket_id(data: ticketing_model.TicketingGetTicketIdParams):
    ...
