

import ticketing_enum
import ticketing_model
import urdhva_base
from fastapi import APIRouter
from urdhva_base import QueryParams
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
        
        user_list = tdata['user_id']

        for tid in user_list:
            print('tid>>',tid)
            uid = int(tid)
            params.q = f"id='{uid}'"
            result = await Users.get_all(params,resp_type='plain')#checking the user is existed or not
            res = result.get("data",[])
            if not res:
                return {
                    "status":False,
                    "message":"User not found"
                }
            tdata.update({
                'ticket_id':data.ticket_id,
                "user_id":uid
            })
            res = await TicketCollaboratorsCreate(**tdata).create() #
            print("added",res['user_id']) 
        return {
            'status':True,
            'messsage':"Collabs added successfully"
        }
        
    except Exception as e:
        return {
            'status':False,
            'message':str(e)
        }



# Action get_collabs
@router.post('/get-collabs', tags=['TicketCollaborators'])
async def ticket_collaborators_get_collabs(data: ticketing_model.TicketcollaboratorsGetCollabsParams):
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

        ticket_result = await TicketCollaborators.get_all(params,resp_type='plain')

        if not ticket_result.get('data',[]):
            return {
                'status':False,
                "message":"Ticket Id not found"
            }
        qurey = f"select * from ticket_collaborators where ticket_id={data.ticket_id}"
        res = await TicketCollaborators.get_aggr_data(qurey,limit=0)
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


# Action update_collabs
@router.post('/update-collabs', tags=['TicketCollaborators'])
async def ticket_collaborators_update_collabs(data: ticketing_model.TicketcollaboratorsUpdateCollabsParams):
    ...
