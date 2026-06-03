from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Client, Ticket, Comment
import crud
from schemas import TicketCreate, TicketListItem, TicketFilterParams, TicketListResponse, TicketDetailResponse, TicketUpdateFull, DashboardStats
from permission import allow_ticket_creation, allow_ticket_modification, allow_view_dashboard  

router = APIRouter(tags=["Tickets"])


@router.post('/', response_model=TicketListItem, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: TicketCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(allow_ticket_creation)
):
    client = db.query(Client).filter(Client.id == ticket.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Client not found. Please create the client first.'
        )
    
    new_ticket = crud.create_ticket(db=db, ticket=ticket, creator_id=current_user.id)
    new_ticket.client_full_name = client.full_name
    new_ticket.client_phone = client.phone
    return new_ticket


@router.post('/search', response_model=TicketListResponse)
def get_filtered_tickets(
    filters: TicketFilterParams,
    page: int = 1,
    size: int = 10, 
    db: Session = Depends(get_db), 
    current_user = Depends(allow_view_dashboard)
):
    has_status = hasattr(filters, 'status') and filters.status and filters.status != "all"
    has_priority = hasattr(filters, 'priority') and filters.priority and filters.priority != "all"

    if not has_status and not has_priority:
        tickets_count = db.query(Ticket).count()
        offset = (page - 1) * size
        all_tickets = db.query(Ticket).offset(offset).limit(size).all()
        
        for ticket in all_tickets:
            client = db.query(Client).filter(Client.id == ticket.client_id).first()
            if client:
                ticket.client_full_name = client.full_name
                ticket.client_phone = client.phone
        
        return {
            "total_count": tickets_count,
            "page": page,
            "size": size,
            "items": all_tickets
        }

    return crud.get_tickets_filtered(db=db, filters=filters, page=page, size=size)


@router.get('/{ticket_id}', response_model=TicketDetailResponse)
def get_ticket_details(
    ticket_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(allow_view_dashboard)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Ticket not found'
        )
    return ticket


@router.delete('/{ticket_id}', status_code=status.HTTP_200_OK)
def delete_ticket_by_id(
    ticket_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(allow_view_dashboard) 
):
    user_role = getattr(current_user, "role", None)
    if user_role not in ["back_office", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only back-office and admin users can delete tickets."
        )
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Ticket not found'
        )
    
    crud.delete_ticket(db=db, ticket_obj=ticket)
    return {"detail": "Ticket deleted successfully"}


@router.put("/{ticket_id}", response_model=TicketDetailResponse)
def update_ticket_status_or_assignment(
    ticket_id: int, 
    payload: TicketUpdateFull, 
    db: Session = Depends(get_db), 
    current_user = Depends(allow_view_dashboard) 
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ticket not found."
        )
    
    user_role = getattr(current_user, "role", None)
    if user_role == "front_office":
        if (payload.status and payload.status != ticket.status) or (payload.assigned_to_id and payload.assigned_to_id != ticket.assigned_to_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Front-office operators cannot change the ticket status or assignee! They can only add comments."
            )

    if hasattr(payload, "comment_text") and payload.comment_text:
        new_comment = Comment(text=payload.comment_text, ticket_id=ticket.id, user_id=current_user.id)
        db.add(new_comment)
        db.commit() 

    crud.update_ticket(db=db, ticket=ticket, payload=payload, user_id=current_user.id)
    db.refresh(ticket)
    return ticket


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_crm_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(allow_view_dashboard)
):
    return crud.get_dashboard_stats(db=db)