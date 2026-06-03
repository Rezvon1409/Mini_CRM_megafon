from fastapi import Depends , HTTPException , status
from models import User , UserRole
from dependencies import get_current_user

class PermissionChecker:

    def __init__(self , allowed_roles : list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user : User = Depends(get_current_user)):
        if current_user.role not in  self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail=f"Access denied! This action is only allowed for the following roles: {[r.value for r in self.allowed_roles]}")
        return current_user
    
    
allow_user_management = PermissionChecker([UserRole.superadmin])
allow_ticket_creation = PermissionChecker([UserRole.front_office, UserRole.back_office, UserRole.superadmin])
allow_ticket_modification = PermissionChecker([UserRole.back_office, UserRole.superadmin])
allow_view_dashboard = PermissionChecker([UserRole.front_office, UserRole.back_office, UserRole.superadmin])