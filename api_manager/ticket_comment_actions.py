

import ticketing_enum
import ticketing_model
from fastapi import APIRouter
import urdhva_base
from ticketing_model import TicketComment,TicketCommentCreate,Ticketing

router = APIRouter(prefix='/ticket-comment')


# Action create_comment
@router.post('/create-comment', tags=['TicketComment'])
async def ticket_comment_create_comment(data: ticketing_model.TicketcommentCreateCommentParams):
    try:
        tdata = data.__dict__
        print(tdata)
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.ticket_id}'"
        params.limit = 1
        result = await Ticketing.get_all(params,resp_type='plain')
        res = result.get("data",[])
        if not res:
            return {
                "status":False,
                "message":"Ticket not found"
            }
        res = await TicketCommentCreate(**tdata).create()
        return {
                    "status": True,
                    "message": "Ticket History updated"
                }
    except Exception as e:
        return {
            "status":False,
            "message":str(e)
        }
