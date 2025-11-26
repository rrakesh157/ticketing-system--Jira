import urdhva_base.postgresmodel
import urdhva_base.queryparams
import urdhva_base.types
import ticketing_enum
import ticketing_model
from fastapi import APIRouter, Response, Depends, UploadFile, File
router = APIRouter()


@router.get('/ticketing/{id}', response_model=ticketing_model.Ticketing, tags=['Ticketing'])
async def get(id: str):
    return await ticketing_model.Ticketing.get(id, skip_secrets=True)


@router.get('/ticketing', response_model=ticketing_model.TicketingGetResp, tags=['Ticketing'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.Ticketing.get_all(params, skip_secrets=True)


@router.get('/ticket-history/{id}', response_model=ticketing_model.TicketHistory, tags=['TicketHistory'])
async def get(id: str):
    return await ticketing_model.TicketHistory.get(id, skip_secrets=True)


@router.get('/ticket-history', response_model=ticketing_model.TicketHistoryGetResp, tags=['TicketHistory'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.TicketHistory.get_all(params, skip_secrets=True)
