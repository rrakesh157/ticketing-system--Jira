

import ticketing_enum
import ticketing_model
from fastapi import APIRouter
from urdhva_base import QueryParams
from ticketing_model import Ticketing,TicketingCreate,TicketHistory,TicketHistoryCreate

router = APIRouter(prefix='/ticket-history')


# Action create_history
@router.post('/create-history', tags=['TicketHistory'])
async def ticket_history_create_history(data: ticketing_model.TickethistoryCreateHistoryParams):
    try:
        tdata = data.__dict__
        print("tdata",tdata)
        params = QueryParams()
        params.q = f"id='{data.ticket_id}'"
        params.limit = 1

        ticket_result = await Ticketing.get_all(params,resp_type='plain')

        if not ticket_result.get('data',[]):
            return {
                'status':False,
                "message":"Ticket not found"
            }
        
        if data.old_value in ['Open','Close','Pending']:
            tdata["field_name"] = "Status"
        if data.old_value in ['Critical','High','Medium','Low']:
            tdata["field_name"] = "Severity"
        if data.old_value == None:
            tdata["field_name"] = "State"
        else:
            tdata["field_name"] = "State"

        
        
        res =  await ticketing_model.TicketHistoryCreate(**tdata).create()
        print(res)
        return {
        "status":True,
        "message": "History updated",
        
        
    }

        
    except Exception as e:
        return{
            'status':False,
            'message':str(e)
        }
