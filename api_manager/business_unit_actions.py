

import ticketing_enum
import ticketing_model
from fastapi import APIRouter,HTTPException
import uuid
import urdhva_base
from ticketing_model import BusinessUnit,BusinessUnitCreate

router = APIRouter(prefix='/business-unit')


def generate_bu_id():
    return str(uuid.uuid4())[:6]



# Action add_new_bu
@router.post('/add-new-bu', tags=['BusinessUnit'])
async def business_unit_add_new_bu(data: ticketing_model.BusinessunitAddNewBuParams):
    
    data_dict = data.__dict__

    params = urdhva_base.queryparams.QueryParams()
    params.q = f"bu_name = '{data.bu_name.capitalize()}'"
    params.limit = 1

    res1 = await BusinessUnit.get_all(params,resp_type='plain')
    resp_data1 = res1.get('data') if res1 else None

    if resp_data1:
        raise HTTPException(status_code=409, detail=f"Bussiness {data.bu_name} name already exists.")

    params = urdhva_base.queryparams.QueryParams()
    params.q = f"bu_short_name = '{data.bu_short_name.upper()}'"
    params.limit = 1

    res2 = await BusinessUnit.get_all(params,resp_type='plain')
    print(res2)

    resp_data2 = res2.get('data') if res2 else None

    
    if resp_data2:
        raise HTTPException(status_code=409, detail=f"Bussiness {data.bu_short_name} short name already exists.")

    id = generate_bu_id()
    print('>>>>>>>',id)
    

    bu_id = f"{data.bu_short_name.upper()}-{id}"
    

    data_dict.update({
        'bu_name' : data.bu_name.capitalize(),
        'bu_id' : bu_id,
        'bu_short_name' : data.bu_short_name.upper()
    })
    try:
    
        res = await ticketing_model.BusinessUnitCreate(**data_dict).create()

        return {
            "status":True,
            'Message':f'Bussiness {data.bu_name} added successfully'
        }
    except Exception as e:
        return {
           "status":False,
           "message":"Failed to insert"
       }