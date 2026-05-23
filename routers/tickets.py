from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Client, Ticket
import crud
from schemas import TicketCreate, TicketListItem, TicketFilterParams, TicketListResponse, TicketDetailResponse, TicketUpdateFull, DashboardStats
from permission import allow_ticket_creation, allow_ticket_modification, allow_view_dashboard  

router = APIRouter(prefix='/tickets', tags=["Tickets"])


@router.post('/', response_model=TicketListItem, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db), current_user = Depends(allow_ticket_creation)):
    client = db.query(Client).filter(Client.id == ticket.client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client not found. Please create the client first.')
    return crud.create_ticket(db=db, ticket=ticket, creator_id=current_user.id)  


@router.post('/search', response_model=TicketListResponse)
def get_filtered_tickets(filters: TicketFilterParams,page: int = 1,size: int = 10, db: Session = Depends(get_db), current_user = Depends(allow_view_dashboard)):
    return crud.get_tickets_filtered(db=db, filters=filters, page=page, size=size)



@router.get('/{ticket_id}', response_model=TicketDetailResponse)
def get_ticket_details(ticket_id: int, db: Session = Depends(get_db), current_user = Depends(allow_view_dashboard)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ticket not found')
    return ticket



@router.put("/{ticket_id}", response_model=TicketDetailResponse)
def update_ticket_status_or_assignment( ticket_id: int,  payload: TicketUpdateFull, db: Session = Depends(get_db), current_user = Depends(allow_ticket_modification)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Ticket not found.")
    return crud.update_ticket(db=db, ticket=ticket, payload=payload, user_id=current_user.id)


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_crm_dashboard_stats(db: Session = Depends(get_db),current_user = Depends(allow_view_dashboard)):
    return crud.get_dashboard_stats(db=db)