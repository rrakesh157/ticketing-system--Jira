

import ticketing_enum
import ticketing_model
from fastapi import APIRouter
import urdhva_base
from urdhva_base import QueryParams
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
                    "message": "Comments are added"
                }
    except Exception as e:
        return {
            "status":False,
            "message":str(e)
        }


# Action get_comments
@router.post('/get-comments', tags=['TicketComment'])
async def ticket_comment_get_comments(data: ticketing_model.TicketcommentGetCommentsParams):
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

        ticket_result = await Ticketing.get_all(params,resp_type='plain')

        if not ticket_result.get('data',[]):
            return {
                'status':False,
                "message":"Ticket Id not found"
            }
        qurey = f"select * from ticket_comment where ticket_id={data.ticket_id}"
        res = await TicketComment.get_aggr_data(qurey,limit=0)
        print(res)
        return {
            "status":True,
            "data":res
        }
    except Exception as e:
        return{
            'status':False,
            'message':str(e)
        }


# Action update_comment
@router.post('/update-comment', tags=['TicketComment'])
async def ticket_comment_update_comment(data: ticketing_model.TicketcommentUpdateCommentParams):
    try:
        tdata = data.__dict__
        print(tdata)
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.comment_id}'"
        params.limit = 1
        result = await TicketComment.get_all(params,resp_type='plain')
        res = result.get("data",[])
        if not res:
            return {
                "status":False,
                "message":"Comment not found"
            }
        res = await TicketComment(**{'id':data.comment_id,**tdata}).modify()
        return {
                    "status": True,
                    "message": "Comments are Updated"
                }
    except Exception as e:
        return {
            "status":False,
            "message":str(e)
        }


# Action delete_comment
@router.post('/delete-comment', tags=['TicketComment'])
async def ticket_comment_delete_comment(data: ticketing_model.TicketcommentDeleteCommentParams):
    try:
        tdata = data.__dict__
        print(tdata)
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.comment_id}'"
        params.limit = 1
        result = await TicketComment.get_all(params,resp_type='plain')
        res = result.get("data",[])
        if not res:
            return {
                "status":False,
                "message":"Comment not found"
            }
        res = await TicketComment.delete(data.comment_id)
        return {
                    "status": True,
                    "message": "Comment deleted"
                }
    except Exception as e:
        return {
            "status":False,
            "message":str(e)
        }
