

import ticketing_enum
import ticketing_model
import uuid
import urdhva_base
# from sqlalchemy import 
from ticketing_model import ZoneCreate,Zone
from fastapi import APIRouter,HTTPException

router = APIRouter(prefix='/zone')



def generate_zone_id():
    return str(uuid.uuid4())[:6]


# Action add_new_zone
@router.post('/add-new-zone', tags=['Zone'])
async def zone_add_new_zone(data: ticketing_model.ZoneAddNewZoneParams):
    
    data_dict = data.__dict__

    params = urdhva_base.queryparams.QueryParams()
    params.q = f"zone_name = '{data.zone_name.capitalize()}'"
    params.limit = 1

    res1 = await Zone.get_all(params,resp_type='plain')
    resp_data1 = res1.get('data') if res1 else None

    if resp_data1:
        raise HTTPException(status_code=409, detail="Zone name already exists.")

    params = urdhva_base.queryparams.QueryParams()
    params.q = f"zone_short_name = '{data.zone_short_name.upper()}'"
    params.limit = 1

    res2 = await Zone.get_all(params,resp_type='plain')
    print(res2)

    resp_data2 = res2.get('data') if res2 else None

    
    if resp_data2:
        raise HTTPException(status_code=409, detail="Zone short name already exists.")

    id = generate_zone_id()
    print('>>>>>>>',id)
    

    zone_id = f"{data.zone_short_name.upper()}-{id}"
    

    data_dict.update({
        'zone_name' : data.zone_name.capitalize(),
        'zone_id' : zone_id,
        'zone_short_name' : data.zone_short_name.upper()
    })
    try:
    
        res = await ticketing_model.ZoneCreate(**data_dict).create()

        return {
            "status":True,
            'Message':f'Zone {data.zone_name} added successfully'
        }
    except Exception as e:
       return {
           "status":False,
           "message":"Failed to insert"
       }
