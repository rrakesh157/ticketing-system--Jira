import urdhva_base.postgresmodel
import urdhva_base.queryparams
import urdhva_base.types
import hpcl_ceg_ticketing_enum
import hpcl_ceg_ticketing_model
from fastapi import APIRouter, Response, Depends, UploadFile, File
router = APIRouter()


@router.get('/ticketing/{id}', response_model=hpcl_ceg_ticketing_model.Ticketing, tags=['Ticketing'])
async def get(id: str):
    return await hpcl_ceg_ticketing_model.Ticketing.get(id, skip_secrets=True)


@router.get('/ticketing', response_model=hpcl_ceg_ticketing_model.TicketingGetResp, tags=['Ticketing'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await hpcl_ceg_ticketing_model.Ticketing.get_all(params, skip_secrets=True)
