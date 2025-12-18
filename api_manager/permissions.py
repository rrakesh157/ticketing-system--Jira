from fastapi import APIRouter, Response, Depends, UploadFile, File
from fastapi import HTTPException, status
import ticketing_model




def can_view_ticket(user,ticket):
    if user['role'] == "ADMIN":
        return True
    
    if ticket['reporter_id'] == user['sub']:
        return True
    
    if ticket['assignee_id'] == user['sub']:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You cannot view this ticket"
    )
    
def can_update_ticket(user,ticket):
    if user['role'] == "ADMIN":
        return True
    
    if ticket['assignee_id'] == user['sub']:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You cannot update this ticket"
    )

# tenent
def can_delete_ticket(user,ticket):
    if user['role'] == "ADMIN":
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You cannot delete this ticket"
    )




# def check_permission(permission_fun):
#     def dependency(
#             user = Depends(get_current_user),
#             ticket = Depends(get_ticket)
#     ):
#         if not permission_fun(user,ticket):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You donot have permission to perform this action"
#             )
#     return dependency
