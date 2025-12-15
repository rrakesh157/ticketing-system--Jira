

import ticketing_enum
import ticketing_model
import urdhva_base
import pandas as pd
from ticketing_model import Boards, BoardsCreate,Workflow,WorkflowStatus
from fastapi import APIRouter, Response, Depends, UploadFile, File, HTTPException


router = APIRouter(prefix='/boards')


@router.get('/boards', tags=['Boards'])
async def get_all_boards(params=Depends(urdhva_base.queryparams.QueryParams)):
    try:

        # params = urdhva_base.queryparams.QueryParams()
        # params.q = f'name'
        # params.limit = 1000
        # query = "select workflow_id from workflow_status group by workflow_id, name"
        # resp = await WorkflowStatus.get_aggr_data(query,limit=0)
        # resp = resp['data']
        # df = pd.DataFrame(resp)
        # print(df)
        
        res = await WorkflowStatus.get_all(params,resp_type='plain')
        df = pd.DataFrame(res['data'])
        df = df[['ticket_state','workflow_id','order_no']]
        workflow_df = (
                df.sort_values("order_no")         
                .groupby("workflow_id")["ticket_state"]
                .agg(list)
                .to_dict()
            )

        print(workflow_df)

        # print(df)

        res = await ticketing_model.Boards.get_all(params,resp_type='plain')
        boards_df = pd.DataFrame(res['data'])
        print(boards_df)
        workflow_grouped = (
            df.sort_values("order_no")
                    .groupby("workflow_id")["ticket_state"]
                    .apply(list)
                    .reset_index()
                    .rename(columns={"ticket_state": "workflow_status_list"})
        )

        result = boards_df.merge(workflow_grouped, on="workflow_id", how="left")

        print(result)

        result = result.to_dict(orient='records')

        return {
            "status":True,
            "data":result
        }
    except Exception as e:
        return {
            "error":str(e)
        }



# Action add_board
@router.post('/add-board', tags=['Boards'])
async def boards_add_board(data: ticketing_model.BoardsAddBoardParams):
    try:
        bdata = data.__dict__
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.workflow_id}'"
        params.limit = 1


        res_workflow = await Workflow.get_all(params, resp_type='plain')

        Workflow_id = res_workflow.get('data',[])

        print(Workflow_id)
    

        if not Workflow_id:
            return {'status':False,
                    'message':"Give valid workflow id"
                    }


        params.q = f"board_name='{data.board_name.lower()}'"
        res = await Boards.get_all(params,resp_type='plain')

        exisiting = res.get('data',[])
        
        if exisiting:
            return {
                'status': False,
                'message': f"{data.board_name.lower()} already exists"
            }
        
        bdata.update({
            "board_name":data.board_name.lower(),
            "board_owner":data.board_owner.lower()
        })
        
        await BoardsCreate(**bdata).create()
        return {
            'status':True,
            'message':f"Board {data.board_name.lower()} is created"
        }
    

    except Exception as e:
        return {
            'error':str(e)
        }


# Action delete_board
@router.post('/delete-board', tags=['Boards'])
async def boards_delete_board(data: ticketing_model.BoardsDeleteBoardParams):
    
    try:
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.board_id}'"
        params.limit = 1

        res = await Boards.get_all(params,resp_type='plain')
        existing = res.get('data',[])
        if not existing:
            return {
                "status":False,
                "message":"Board not found"
            } 
        resp = await Boards.delete(data.board_id)
        return {
            "status":True,
            "message":f"Board {data.board_id} is deleted"
        }
    except Exception as e:
        return {
            'error':str(e)
        }


# Action update_board
@router.post('/update-board', tags=['Boards'])
async def boards_update_board(data: ticketing_model.BoardsUpdateBoardParams):
    try:
        bdata = data.__dict__
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.board_id}'"
        params.limit = 1

        res = await Boards.get_all(params,resp_type='plain')
        exisiting = res.get('data',[])
        if not exisiting:
            return {
                "status":False,
                "message":f"Board {data.board_id} doesnot exist"
            }

        params.q = f"id='{data.workflow_id}'"
        chk_workflow = await Workflow.get_all(params,resp_type='plain')
        
        if not chk_workflow.get('data',[]):
            raise HTTPException(status_code=404,detail="Workflow not found")
        
        bdata.update({
            "board_name":data.board_name,
            "board_owner":data.board_owner,
            "workflow_id":data.workflow_id
        })
        await Boards(**{"id":data.board_id,**bdata}).modify()

        return {
            "status":True,
            "message":"Board data updated successfully"
        }
    except Exception as e:
        return {
            'error':str(e)
        }



