

import ticketing_enum
import ticketing_model
import urdhva_base
from ticketing_model import Workflow,WorkflowCreate
from fastapi import APIRouter

router = APIRouter(prefix='/workflow')


# Action add_workflow
@router.post('/add-workflow', tags=['Workflow'])
async def workflow_add_workflow(data: ticketing_model.WorkflowAddWorkflowParams):
    try:
        wdata = data.__dict__
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"workflow_name='{data.workflow_name.lower()}'"
        params.limit = 1
        res = await Workflow.get_all(params,resp_type='plain')

        print(res)
        print('.>>>>',len(res.get('data',[])))

        if not res or len(res.get('data',[])) == 0:
            wdata.update({
                "workflow_name":data.workflow_name.lower(),
                "created_by":data.created_by
            })
            await WorkflowCreate(**wdata).create()
            return {
                'status':True,
                'messege':f"Workflow name {data.workflow_name.lower()} is created"
            }
        else:
           return {
                'status':False,
                'messege':f"Workflow name {data.workflow_name.lower()} already exist"
            } 
        
        

    except Exception as e:
        return {
            'error':str(e)
        }

