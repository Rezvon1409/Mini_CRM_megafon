from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from crud import *
from schemas import *
from dependencies import get_current_user, RoleChecker
from typing import Optional

router = APIRouter(prefix='/clients', tags=['Clients'])

@router.post('/', response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_new_client(client: ClientCreate, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_client = get_client_by_account(db, account_number=client.account_number)
    if db_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client with this account number already exists')
    return create_client(db=db, client=client)

from typing import Optional

@router.get('/search', response_model=list[ClientResponse])
def search_for_clients(
    full_name: Optional[str] = None,      
    account_number: Optional[str] = None,  
    passport_series: Optional[str] = None, 
    db: Session = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
    

    if not full_name and not account_number and not passport_series:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Please fill in at least one field for search!'
        )
    

    results = search_clients_advanced(
        db=db, 
        full_name=full_name, 
        account_number=account_number, 
        passport_series=passport_series
    )
    return results


@router.put('/{account_number}', response_model=ClientResponse)
def update_client_by_account(
    account_number: str, 
    payload: ClientCreate, 
    db: Session = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
    if getattr(current_user, "role", None) == "front_office":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and back-office users can update client details."
        )

    db_client = get_client_by_account(db, account_number=account_number)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client not found')
    
    return update_client(db=db, client_obj=db_client, payload=payload)


@router.delete('/{account_number}', status_code=status.HTTP_200_OK)
def delete_client_by_account(
    account_number: str, 
    db: Session = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
  
    if getattr(current_user, "role", None) == "front_office":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and back-office users can delete clients."
        )

    db_client = get_client_by_account(db, account_number=account_number)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client not found')
    
    delete_client(db=db, client_obj=db_client)
    return {"detail": "Client deleted successfully"}

@router.get('/{account_number}', response_model=ClientResponse)
def get_client_by_account_number(account_number: str, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_client = get_client_by_account(db, account_number=account_number)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client not found')
    return db_client