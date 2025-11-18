

import ticketing_enum
import ticketing_model
import urdhva_base
from ticketing_model import Boards, BoardsCreate,Workflow
from fastapi import APIRouter

router = APIRouter(prefix='/boards')


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
                'message': f"Board name '{data.board_name.lower()}' already exists"
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
