

import ticketing_enum
import ticketing_model
import urdhva_base
from urdhva_base  import QueryParams
from ticketing_model import WorkflowStatus,WorkflowStatusCreate,Workflow

from fastapi import APIRouter

router = APIRouter(prefix='/workflow-status')




@router.get('/workflow-status/', tags=['WorkflowStatus']) # Get api To get default workflow status
def get_statuses():
    return {"workflow":["todo","inprogress","cancelled","resolved","onhold"],
            "status":["open","close","pending","done"]}



# Action update_order
@router.post('/update-order', tags=['WorkflowStatus'])
async def workflow_status_update_order(data: ticketing_model.WorkflowstatusUpdateOrderParams):
    try:
        wdata = data.__dict__

        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.workflow_id}'"
        params.limit = 1

        chck = await Workflow.get_all(params,resp_type='plain') #to check wether the workflow is there or not
        if not chck.get('data',[]):
            return {
                "status":False,
                "message":"Give a valid workflow id"
            }
        

        params.q = f"workflow_id='{data.workflow_id}'"
        params.limit = 0

        res = await WorkflowStatus.get_all(params,resp_type='plain')

        exisiting = res.get('data',[])

        for i in exisiting:
            print(i)

        print("exisiting>>>>",exisiting)

        # print("wdata>>>>>>",wdata)        
        if exisiting:
            for i in exisiting:
                resp = await WorkflowStatus.delete(i['id'])
                print(resp)
                
        order = []
        for index,state in enumerate(data.workflow_order,start=1):
            order.append({
                "workflow_id":data.workflow_id,
                "ticket_state":state.ticket_state,
                "ticket_status":state.ticket_status,
                "order_no":index
            })
            
        print(order)
        for record in order:
            await WorkflowStatusCreate(**record).create()


        return {
            'status':True,
            'message':"workflow status updated"
        }
    except Exception as e:
        return {'error':str(e)}


# # Action update_order
# @router.post('/update-order', tags=['WorkflowStatus'])
# async def workflow_status_update_order(data: ticketing_model.WorkflowstatusUpdateOrderParams):
    # try:
    #     wdata = data.__dict__

    #     params = urdhva_base.queryparams.QueryParams()
    #     params.q = f"id='{data.workflow_id}'"
    #     params.limit = 1

    #     chck = await Workflow.get_all(params,resp_type='plain') #to check wether the workflow is there or not
    #     if not chck.get('data',[]):
    #         return {
    #             "status":False,
    #             "message":"Give a valid workflow id"
    #         }
        

    #     params.q = f"workflow_id='{data.workflow_id}'"
    #     params.limit = 10

    #     res = await WorkflowStatus.get_all(params,resp_type='plain')

    #     exisiting = res.get('data',[])

    #     for i in exisiting:
    #         print(i)

    #     print("exisiting>>>>",exisiting)

        # if exisiting:
        #     for i in exisiting:
        #         resp = await WorkflowStatus.delete(i['id'])
        #         print(resp)
                
        # new_data = []
        # for index,state in enumerate(data.name,start=1):
        #     new_data.append({
        #         "workflow_id":data.workflow_id,
        #         "name":state,
        #         "order_no":index
        #     })
        # for record in new_data:
        #     await WorkflowStatusCreate(**record).create()

    #     return {
    #         "status":True,
    #         "message":"records inserted"
    #             }

            

    # except Exception as e:
    #     return {
    #         'error':str(e)
    #     }

