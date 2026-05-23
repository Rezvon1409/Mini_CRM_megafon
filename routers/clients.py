from fastapi import APIRouter , Depends , HTTPException , status
from sqlalchemy.orm import Session
from database import *
from crud import *
from schemas import *
from dependencies import get_current_user , RoleChecker


router = APIRouter(prefix='/clients' , tags=['Clients'])

@router.post('/' , response_model=ClientResponse , status_code=status.HTTP_201_CREATED)
def create_new_client(client : ClientCreate , db : Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_client = get_client_by_account(db , account_number=client.account_number)
    if db_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail= 'Client with this account number already exists')
    return create_client(db=db , client=client)


@router.get('/{account_number}' , response_model=ClientResponse)
def get_client_by_account_number(account_number : str , db : Session = Depends(get_db) , current_user : UserResponse = Depends(get_current_user)):
    db_client = get_client_by_account(db , account_number=account_number)
    if not db_client:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail= 'Client not found')
    return db_client