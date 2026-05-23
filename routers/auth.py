from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import LoginRequest, Token, UserCreate, UserResponse
import crud
import auth
from permission import allow_user_management  

router = APIRouter(prefix='/auth', tags=['Authentication'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


@router.post('/login', response_model=Token)  
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=payload.username)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or account is inactive')
        
    if not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect password')
    
    token_data = {'user_id': user.id, 'role': user.role.value}

    access_token = auth.create_access_token(data=token_data)
    refresh_token = auth.create_refresh_token(data=token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



@router.post('/refresh', response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate refresh token', headers={'WWW-Authenticate': 'Bearer'} )

    payload = auth.verify_token(refresh_token, expected_type='refresh', credentials_exception=credentials_exception)

    user = db.query(User).filter(User.id == payload['user_id']).first()
    if not user or not user.is_active:
        raise credentials_exception
    
    new_token_data = {'user_id': user.id, 'role': user.role.value}
    new_access = auth.create_access_token(data=new_token_data)
    new_refresh = auth.create_refresh_token(data=new_token_data)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_new_user(user: UserCreate, db: Session = Depends(get_db),current_user: User = Depends(allow_user_management)):
  
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    

    db_email = crud.get_user_by_email(db, email=user.email)
    if db_email:
        raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
    return crud.create_user(db=db, user=user)