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
        "action_msg":f"Ticket is created and is in {action_type_str} state",
        "action_type":action_type_str})

    await ticketing_model.TicketingCreate(**tdata).create()
    return {
        'Message':'Tickets Created Successfully',
        'Ticket':tdata
    }
    


# Action get_ticket_id
@router.post('/get-ticket-id', tags=['Ticketing'])
async def ticketing_get_ticket_id(data: ticketing_model.TicketingGetTicketIdParams):
    
    ...


# Action attach_file
@router.post('/attach-file', tags=['Ticketing'])
async def ticketing_attach_file(data: ticketing_model.TicketingAttachFileParams):
    ...


# Action attach_file
@router.post('/attach-file', tags=['Ticketing'])
async def ticketing_attach_file(data: ticketing_model.TicketingAttachFileParams):
    ...


# Action update_ticket
@router.post('/update-ticket', tags=['Ticketing'])
async def ticketing_update_ticket(data: ticketing_model.TicketingUpdateTicketParams):
    ...
