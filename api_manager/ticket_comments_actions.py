

import ticketing_enum
import ticketing_model
from fastapi import APIRouter,HTTPException
import urdhva_base
from urdhva_base import QueryParams
from ticketing_model import TicketCommentsCreate,Ticketing,TicketComments
router = APIRouter(prefix='/ticket-comments')


# Action create_comment
@router.post('/create-comment', tags=['TicketComments'])
async def ticket_comments_create_comment(data: ticketing_model.TicketcommentsCreateCommentParams):
    try:
        tdata = data.__dict__
        print(tdata)
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.ticket_id}'"
        params.limit = 1

        #checking wether ticket is present or not
        result = await Ticketing.get_all(params,resp_type='plain')
        res = result.get("data",[])
        if not res:
            return {
                "status":False,
                "message":"Ticket not found"
            }
        

        if data.parent_id:
            params.q = f"id={data.parent_id}"
            result = await TicketComments.get_all(params,resp_type='plain')

            if not result.get('data',[]):
                raise HTTPException(status_code=404,detail='comment not found')

        res = await TicketCommentsCreate(**tdata).create()
        return {
                    "status": True,
                    "message": "Comments are added"
                }
    except Exception as e:
        return {
            "status":False,
            "message":str(e)
        }


# Action delete_comment
@router.post('/delete-comment', tags=['TicketComments'])
async def ticket_comments_delete_comment(data: ticketing_model.TicketcommentsDeleteCommentParams):
    try:
        tdata = data.__dict__
        print(tdata)
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.comment_id}'"   
        params.limit = 1
        result = await TicketComments.get_all(params,resp_type='plain')
        res = result.get("data",[])

        if not res:
            return {
                "status":False,
                "message":"Comment not found"
            }
        
        #inplace of comment it is replaced by Comment deleted
        tdata.update({
                'comment_text':"Comment deleted"
        })

        res = await TicketComments(**{'id':data.comment_id,**tdata}).modify()

        # res = await TicketComments.delete(data.comment_id)
        return {
                    "status": True,
                    "message": "Comment deleted"
                }
    except Exception as e:
        return {
            "status":False,
            "message":str(e)
        }


# Action update_comment
@router.post('/update-comment', tags=['TicketComments'])
async def ticket_comments_update_comment(data: ticketing_model.TicketcommentsUpdateCommentParams):
    try:
        tdata = data.__dict__
        print(tdata)
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.comment_id}'"
        params.limit = 1
        result = await TicketComments.get_all(params,resp_type='plain')
        res = result.get("data",[])
        
        if not res:
            return {
                "status":False,
                "message":"Comment not found"
            }
        
        tdata['edited'] = True
        res = await TicketComments(**{'id':data.comment_id,**tdata}).modify()
        return {
                    "status": True,
                    "message": "Comments are Updated"
                }
    
    except Exception as e:
        return {
            "status":False,
            "message":str(e)
        }

