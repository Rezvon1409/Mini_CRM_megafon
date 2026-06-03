from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session 
from typing import List 
import auth
from database import get_db  
from models import User


oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate credentials', 
        headers={'WWW-Authenticate': "Bearer"}
    )

    if not token:
        raise credential_exception

    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")

    payload = auth.verify_token(token, expected_type='access', credentials_exception=credential_exception)
    user = db.query(User).filter(User.id == payload['user_id']).first()

    if user is None or not user.is_active:
        raise credential_exception
    
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You don't have permission to perform this action. Access denied"
            )
        
        return current_user