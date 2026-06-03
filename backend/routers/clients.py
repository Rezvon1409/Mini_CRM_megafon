from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Client  
from crud import search_clients_advanced, get_client_by_account, create_client, update_client, delete_client
from schemas import ClientCreate, ClientResponse, UserResponse
from dependencies import get_current_user
from typing import Optional

router = APIRouter(tags=['Clients'])

@router.get('/search', response_model=list[ClientResponse])
def search_for_clients(
    q: Optional[str] = Query(None, description="Global search query"),
    db: Session = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
   
    if q is None or not q.strip():
        all_clients = db.query(Client).all()
        return all_clients

    search_query = q.strip()
    

    if search_query.startswith("+") or (search_query.startswith("8") and len(search_query) == 11):
        results = search_clients_advanced(db=db, phone=search_query)
        return results

    elif search_query.isdigit():
        results = search_clients_advanced(db=db, account_number=search_query)
        return results

    else:
        if len(search_query) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail='For Full Name search, a minimum of 3 characters is required!'
            )
        results = search_clients_advanced(db=db, full_name=search_query)
        return results



@router.post('/', response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_new_client(client: ClientCreate, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_client = get_client_by_account(db, account_number=client.account_number)
    if db_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client with this account number already exists')
    return create_client(db=db, client=client)

@router.put('/{account_number}', response_model=ClientResponse)
def update_client_by_account(account_number: str, payload: ClientCreate, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    if getattr(current_user, "role", None) == "front_office":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin and back-office users can update.")
    db_client = get_client_by_account(db, account_number=account_number)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client not found')
    return update_client(db=db, client_obj=db_client, payload=payload)

@router.delete('/{account_number}', status_code=status.HTTP_200_OK)
def delete_client_by_account(account_number: str, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    if getattr(current_user, "role", None) == "front_office":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin and back-office users can delete.")
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