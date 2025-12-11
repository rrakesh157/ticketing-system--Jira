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


@router.get('/ticket-comment/{id}', response_model=ticketing_model.TicketComment, tags=['TicketComment'])
async def get(id: str):
    return await ticketing_model.TicketComment.get(id, skip_secrets=True)


@router.get('/ticket-comment', response_model=ticketing_model.TicketCommentGetResp, tags=['TicketComment'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.TicketComment.get_all(params, skip_secrets=True)


@router.get('/ticket-collaborators/{id}', response_model=ticketing_model.TicketCollaborators, tags=['TicketCollaborators'])
async def get(id: str):
    return await ticketing_model.TicketCollaborators.get(id, skip_secrets=True)


@router.get('/ticket-collaborators', response_model=ticketing_model.TicketCollaboratorsGetResp, tags=['TicketCollaborators'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.TicketCollaborators.get_all(params, skip_secrets=True)


@router.get('/workflow/{id}', response_model=ticketing_model.Workflow, tags=['Workflow'])
async def get(id: str):
    return await ticketing_model.Workflow.get(id, skip_secrets=True)


@router.get('/workflow', response_model=ticketing_model.WorkflowGetResp, tags=['Workflow'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.Workflow.get_all(params, skip_secrets=True)


@router.get('/workflow-status/{id}', response_model=ticketing_model.WorkflowStatus, tags=['WorkflowStatus'])
async def get(id: str):
    return await ticketing_model.WorkflowStatus.get(id, skip_secrets=True)


@router.get('/workflow-status', response_model=ticketing_model.WorkflowStatusGetResp, tags=['WorkflowStatus'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.WorkflowStatus.get_all(params, skip_secrets=True)


@router.get('/boards/{id}', response_model=ticketing_model.Boards, tags=['Boards'])
async def get(id: str):
    return await ticketing_model.Boards.get(id, skip_secrets=True)


@router.get('/boards', response_model=ticketing_model.BoardsGetResp, tags=['Boards'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.Boards.get_all(params, skip_secrets=True)


@router.get('/users/{id}', response_model=ticketing_model.Users, tags=['Users'])
async def get(id: str):
    return await ticketing_model.Users.get(id, skip_secrets=True)


@router.get('/users', response_model=ticketing_model.UsersGetResp, tags=['Users'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.Users.get_all(params, skip_secrets=True)


@router.get('/projects/{id}', response_model=ticketing_model.Projects, tags=['Projects'])
async def get(id: str):
    return await ticketing_model.Projects.get(id, skip_secrets=True)


@router.get('/projects', response_model=ticketing_model.ProjectsGetResp, tags=['Projects'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.Projects.get_all(params, skip_secrets=True)


@router.get('/milestone/{id}', response_model=ticketing_model.Milestone, tags=['Milestone'])
async def get(id: str):
    return await ticketing_model.Milestone.get(id, skip_secrets=True)


@router.get('/milestone', response_model=ticketing_model.MilestoneGetResp, tags=['Milestone'])
async def get_all(response: Response, params=Depends(urdhva_base.queryparams.QueryParams)):
    return await ticketing_model.Milestone.get_all(params, skip_secrets=True)
