

import ticketing_enum
import ticketing_model
import urdhva_base
from ticketing_model import MasterData,MasterDataCreate
from fastapi import APIRouter,HTTPException


router = APIRouter(prefix='/master-data')


# Action add_new_data
@router.post('/add-new-data', tags=['MasterData'])
async def master_data_add_new_data(data: ticketing_model.MasterdataAddNewDataParams):

    
    mdata = data.__dict__

    params = urdhva_base.queryparams.QueryParams()
    params.q = f"value='{data.value}'"
    params.limit = 1
    res = await MasterData.get_all(params,resp_type='plain')

   
    if res.get('data'):
        print(">>>>>>>>>>",res)
        proj = res.get('data')[0]['name']
        val = res.get('data')[0]['value'] 

        print("proj--->",proj)
        print("val--->",val)


        if res.get('data'):
            raise HTTPException(status_code=409,detail=f"{data.value} already give another name")
        


        params.q = f"name='{data.name}' and value='{data.value}"
        res1 = await MasterData.get_all(params,resp_type='plain')
        val1 = res1.get('data')[0]['value'] 

        print("val--->",val1)

        if res1.get('data'):
            raise HTTPException(status_code=409,detail=f"Data already exist  ")

    else:            
        try:
            await ticketing_model.MasterDataCreate(**mdata).create()
            return {
                "status":True,
                'Message':f'Master Data {data.name} added successfully'
            }
        except Exception as e:
            return {
            "status":False,
            "message":f"Failed to insert {str(e)}"
        }


# Action update_data
@router.post('/update-data', tags=['MasterData'])
async def master_data_update_data(data: ticketing_model.MasterdataUpdateDataParams):
    
    # mdata = data.__dict__

    # return mdata
    try:
        params = urdhva_base.queryparams.QueryParams()
        params.q = f"id='{data.md_id}'"
        params.limit = 1
        res = await MasterData.get_all(params,resp_type='plain')

        if not res.get('data'):
            return {
                'status':False,
                'messege':"Record Does not exist"
            }
        
        # if res.get('data')[0]['value'] == data.value :
        #     raise HTTPException(status_code=409,detail="No changes detected — the provided value matches the existing record.")
        
        record = res.get('data',[])[0]
        print('>>>>>>>',record)
        updated_data = {}

        updated_data.update({
            "id":data.md_id,
            "name":data.name or record['name'],
            "description":data.description or record['description'],
            "value":data.value or record['value']
        })

        
        await MasterData(**updated_data).modify()
        return {
                    "status":True,
                    'Message':f'Master Data {data.name} Updated successfully'
                }
    except Exception as e:
        return {'error':str(e)}
    





# Action delete_data
@router.post('/delete-data', tags=['MasterData'])
async def master_data_delete_data(data: ticketing_model.MasterdataDeleteDataParams):
    await MasterData.delete(data.md_id)
    return {
        "status":True,
        "message":"Master Data Deleted successfully",
        "data":data.md_id
    }
