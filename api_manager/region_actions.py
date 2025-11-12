

import ticketing_enum
import ticketing_model
import urdhva_base
import uuid
from ticketing_model import Region, RegionCreate

from fastapi import APIRouter,HTTPException

router = APIRouter(prefix='/region')


def generate_region_id():
    return str(uuid.uuid4())[:6]


# Action add_new_region
@router.post('/add-new-region', tags=['Region'])
async def region_add_new_region(data: ticketing_model.RegionAddNewRegionParams):
     
    data_dict = data.__dict__

    params = urdhva_base.queryparams.QueryParams()
    params.q = f"region_name = '{data.region_name.capitalize()}'"
    params.limit = 1

    res1 = await Region.get_all(params,resp_type='plain')
    resp_data1 = res1.get('data') if res1 else None

    if resp_data1:
        raise HTTPException(status_code=409, detail=f"Region {data.region_name} name already exists.")

    params = urdhva_base.queryparams.QueryParams()
    params.q = f"region_short_name = '{data.region_short_name.upper()}'"
    params.limit = 1

    res2 = await Region.get_all(params,resp_type='plain')
    print(res2)

    resp_data2 = res2.get('data') if res2 else None

    
    if resp_data2:
        raise HTTPException(status_code=409, detail=f"Region {data.region_short_name} short name already exists.")

    id = generate_region_id()
    print('>>>>>>>',id)
    

    region_id = f"{data.region_short_name.upper()}-{id}"
    

    data_dict.update({
        'region_name' : data.region_name.capitalize(),
        'region_id' : region_id,
        'region_short_name' : data.region_short_name.upper()
    })
    try:
    
        res = await ticketing_model.RegionCreate(**data_dict).create()

        return {
            "status":True,
            'Message':f'Region {data.region_name} added successfully'
        }
    except Exception as e:
        return {
           "status":False,
           "message":"Failed to insert"
       }
