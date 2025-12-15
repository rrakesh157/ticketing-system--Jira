

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



# Action update_project
@router.post('/update-project', tags=['Projects'])
async def projects_update_project(data: ticketing_model.ProjectsUpdateProjectParams):
    try:
        pdata = data.__dict__
        params = QueryParams()
        params.q = f"id={data.project_id}"
        params.limit = 1

        res = await Projects.get_all(params,resp_type='plain')

        existing = res.get('data',[])

        print('existing>>>>',existing)

        if not existing or len(existing) == 0:
            return {
                'status':False,
                'message':'Project id not found'
            }
        
        #since the project_name must be unique cheking whether the project name exist or not
        params.q = f"project_name='{data.project_name}'"
        chk_res = await Projects.get_all(params,resp_type='plain')

        chk_project_name = chk_res.get('data',[])
        if chk_project_name:
            return {
                'status':False,
                'message':f"Project {chk_project_name[0]['project_name']} already exist"
            }
        
        params.q = f"id={data.created_by_id}"
        user = await Users.get_all(params,resp_type='plain')

        if not user.get('data',[]):
            return{
            'status':False,
            'message':"user does not exist"
        } 
        
        result = await Projects(**{"id":data.project_id,**pdata}).modify()

        print('result>>>>>',result)

        return {
            'status':True,
            'message':'Project updated successfully'
        }
    
    except Exception as e:
        return {
            'status':False,
            'message':str(e)

        }


# Action delete_project
@router.post('/delete-project', tags=['Projects'])
async def projects_delete_project(data: ticketing_model.ProjectsDeleteProjectParams):
    try:
        params = QueryParams()
        params.q = f"id={data.project_id}"
        params.limit = 1

        res = await Projects.get_all(params,resp_type='plain')
        
        existing = res.get('data',[])
        if not existing:
            return {
                'status':False,
                'message':'Project id not found'
            }
        
        await Projects.delete(data.project_id)

        return {
            'status':True,
            'message':f"Project {existing[0]['project_name']} deleted"
        }
    
    except Exception as e:
        return {
            'status':False,
            'message':str(e)

        }
