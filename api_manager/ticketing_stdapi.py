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


@router.get('/business-unit/{id}', response_model=ticketing_model.BusinessUnit, tags=['BusinessUnit'])
async def get(id: str):
    return await ticketing_model.BusinessUnit.get(id, skip_secrets=True)


@router.get('/business-unit', response_model=ticketing_model.BusinessUnitGetResp, tags=['BusinessUnit'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.BusinessUnit.get_all(params, skip_secrets=True)


@router.get('/zone/{id}', response_model=ticketing_model.Zone, tags=['Zone'])
async def get(id: str):
    return await ticketing_model.Zone.get(id, skip_secrets=True)


@router.get('/zone', response_model=ticketing_model.ZoneGetResp, tags=['Zone'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.Zone.get_all(params, skip_secrets=True)


@router.get('/region/{id}', response_model=ticketing_model.Region, tags=['Region'])
async def get(id: str):
    return await ticketing_model.Region.get(id, skip_secrets=True)


@router.get('/region', response_model=ticketing_model.RegionGetResp, tags=['Region'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.Region.get_all(params, skip_secrets=True)


@router.get('/master-data/{id}', response_model=ticketing_model.MasterData, tags=['MasterData'])
async def get(id: str):
    return await ticketing_model.MasterData.get(id, skip_secrets=True)


@router.get('/master-data', response_model=ticketing_model.MasterDataGetResp, tags=['MasterData'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.MasterData.get_all(params, skip_secrets=True)
