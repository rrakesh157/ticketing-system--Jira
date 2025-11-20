

import ticketing_enum
import ticketing_model
import urdhva_base
from urdhva_base  import QueryParams
from ticketing_model import WorkflowStatus,WorkflowStatusCreate,Workflow

from fastapi import APIRouter

router = APIRouter(prefix='/workflow-status')




@router.get('/workflow-status/', tags=['WorkflowStatus'])
def get_statuses():
    return ["todo","inprogress","cancelled","Resolved","onhold"]



# Action add_workflow_status
@router.post('/add-workflow-status', tags=['WorkflowStatus'])
async def workflow_status_add_workflow_status(data: ticketing_model.WorkflowstatusAddWorkflowStatusParams):
    try:
        wdata = data.__dict__

        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.workflow_id}'"
        params.limit = 1

        res_status = await Workflow.get_all(params, resp_type='plain')

        status = res_status.get('data',[])

        if not status:
            return {'status':False,
                    'message':"Give valid workflow id"
                    }

        params.q = f"workflow_id='{data.workflow_id}' AND name='{data.name.lower()}'"
        

        res = await WorkflowStatus.get_all(params, resp_type='plain')
        existing = res.get("data", [])

        if existing:  
            return {
                'status': False,
                'message': f"Status '{data.name.lower()}' already exists in this workflow"
            }

        wdata.update({
            "name": data.name.lower(),
            "order_no": data.order_no
        })

        await WorkflowStatusCreate(**wdata).create()

        return {
            'status': True,
            'message': f"Workflow status '{data.name.lower()}' created successfully"
        }

    except Exception as e:
        return {"error":str(e)}




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
        params.limit = 10

        res = await WorkflowStatus.get_all(params,resp_type='plain')

        exisiting = res.get('data',[])

        for i in exisiting:
            print(i)

        print("exisiting>>>>",exisiting)

        if exisiting:
            for i in exisiting:
                resp = await WorkflowStatus.delete(i['id'])
                print(resp)
                
        new_data = []
        for index,state in enumerate(data.name,start=1):
            new_data.append({
                "workflow_id":data.workflow_id,
                "name":state,
                "order_no":index
            })
        for record in new_data:
            await WorkflowStatusCreate(**record).create()

        return {
            "status":True,
            "message":"records inserted"
                }

            

    except Exception as e:
        return {
            'error':str(e)
        }
