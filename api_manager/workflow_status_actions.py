

import ticketing_enum
import ticketing_model
import urdhva_base
from ticketing_model import WorkflowStatus,WorkflowStatusCreate,Workflow

from fastapi import APIRouter

router = APIRouter(prefix='/workflow-status')


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
