

import ticketing_enum
import ticketing_model
import urdhva_base
from ticketing_model import Workflow,WorkflowCreate,Boards,WorkflowStatus
from fastapi import APIRouter,HTTPException

router = APIRouter(prefix='/workflow')


# Action add_workflow
@router.post('/add-workflow', tags=['Workflow'])
async def workflow_add_workflow(data: ticketing_model.WorkflowAddWorkflowParams):
    try:
        wdata = data.model_dump()
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"workflow_name='{data.workflow_name.lower()}'"
        params.limit = 1
        exisiting = await Workflow.get_all(params,resp_type='plain')

        exisiting = exisiting.get("data",[])
        print(exisiting)

        if exisiting:
            return {
                "status":False,
                "message":f"Workflow {data.workflow_name} already exists"
            }

        wdata.update({
            "workflow_name":data.workflow_name.lower(),
            "created_by":data.created_by
        })
        resp = await WorkflowCreate(**wdata).create()

        print(resp)
        return {
            'status':True,
            'messege':f"{data.workflow_name.lower()} is created successfully",
            'workflow_id':resp.get("id"),
            'workflow_name':resp.get("workflow_name")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="something went wrong while creating workflow"
        )

#if work flow is deleted then its related status and board get effected

# Action delete_workflow
@router.post('/delete-workflow', tags=['Workflow']) # to delete this first make susre that,the other db records based on this id should be deleted first
async def workflow_delete_workflow(data: ticketing_model.WorkflowDeleteWorkflowParams):
    try:
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.workflow_id}'"
        params.limit = 1

        res = await Workflow.get_all(params,resp_type='plain')
        existing = res.get('data',[])
        if not existing:
            return {
                "status":False,
                "message":f"{data.workflow_id} not found"
            } 
        board_data = await Boards.get_all(params,resp_type='plain')
        # WorkflowStatus_data = await WorkflowStatus.get_all(params,resp_type='plain')
        print(board_data)
        if not board_data.get('data',[]): #check whether any board is using if not then delete the workflow
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
            await Workflow.delete(data.workflow_id)
            return {
                "status":True,
                "message":f"workflow {data.workflow_id} is deleted"
            }
        else:
            return {
                "status":False,
                'message':f"workflow {data.workflow_id} cannot delete since it used in boards"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="something went wrong while creating workflow"
        )


# Action update_workflow
@router.post('/update-workflow', tags=['Workflow'])
async def workflow_update_workflow(data: ticketing_model.WorkflowUpdateWorkflowParams):
    try:
        bdata = data.__dict__
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.workflow_id}'"
        res = await Workflow.get_all(params,resp_type='plain')
        exisiting = res.get('data',[])
        if not exisiting:
            return {
                "status":False,
                "message":f"Workflow {data.workflow_id} doesnot exist"
            }
    
        bdata.update({
            "workflow_name":data.workflow_name,
            "created_by":data.created_by
        })
        await Workflow(**{"id":data.workflow_id,**bdata}).modify()

        return {
            "status":True,
            "message":"Workflow data updated successfully"
        }
    except Exception as e:
        return {
            'error':str(e)
        }

