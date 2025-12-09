

import ticketing_enum
import ticketing_model
import urdhva_base
from urdhva_base import QueryParams
from ticketing_model import Projects,ProjectsCreate,Users
from fastapi import APIRouter

router = APIRouter(prefix='/projects')



# Action create_project
@router.post('/create-project', tags=['Projects'])
async def projects_create_project(data: ticketing_model.ProjectsCreateProjectParams):
    try:
        pdata = data.model_dump()
        params = QueryParams()
        params.q =f"project_name='{data.project_name}'"
        params.limit = 1

        res = await Projects.get_all(params=params,resp_type='plain')
        
        print("project_name>>",data.project_name)

        if res.get('data',[]):
            return{
            'status':False,
            'message':"Project already exist"
        }

        params.q = f"id={data.created_by_id}"
        user = await Users.get_all(params,resp_type='plain')

        if not user.get('data',[]):
            return{
            'status':False,
            'message':"user does not exist"
        }            
        

        result = await ProjectsCreate(**pdata).create()
        print(result)
        return {
            'status':True,
            'message':'Project added successfully'
            
        }


    except Exception as e:
        return{
            'status':False,
            'message':str(e)
        }

