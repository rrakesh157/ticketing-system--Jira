

import ticketing_enum
import ticketing_model
from fastapi import APIRouter
import urdhva_base
from ticketing_model import TicketCollaboratorsCreate,TicketCollaborators,Ticketing,Users


router = APIRouter(prefix='/ticket-collaborators')


# Action create_collabs
@router.post('/create-collabs', tags=['TicketCollaborators'])
async def ticket_collaborators_create_collabs(data: ticketing_model.TicketcollaboratorsCreateCollabsParams):
    try:
        tdata = data.__dict__
        print(tdata)
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.ticket_id}'"
        params.limit = 1
        result = await Ticketing.get_all(params,resp_type='plain') #checking the ticket is existed or not
        res = result.get("data",[])
        if not res:
            return {
                "status":False,
                "message":"Ticket not found"
            }

        params.q = f"id='{data.user_id}'"
        result = await Users.get_all(params,resp_type='plain')#checking the user is existed or not
        res = result.get("data",[])
        if not res:
            return {
                "status":False,
                "message":"User not found"
            }
        
        res = await TicketCollaborators(**tdata).create() #
        return {
            'status':True,
            'messsage':"Collabs added successfully"
        }
        
    except Exception as e:
        return {
            'status':False,
            'message':str(e)
        }
