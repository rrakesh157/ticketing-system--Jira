

import ticketing_enum
import ticketing_model
from fastapi import APIRouter

router = APIRouter(prefix='/milestone')


# Action create_milestone
@router.post('/create-milestone', tags=['Milestone'])
async def milestone_create_milestone(data: ticketing_model.MilestoneCreateMilestoneParams):
    ...
