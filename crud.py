from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import User, Client, Ticket, TicketHistory, TicketStatus
from schemas import UserCreate, ClientCreate, TicketCreate, TicketUpdateFull, TicketListItem, TicketListResponse, TicketFilterParams, DashboardStats
import auth
from datetime import datetime


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):
    hashed_pwd = auth.get_password_hash(user.password)  
    db_user = User( username=user.username,  email=user.email,  full_name=user.full_name,  role=user.role, hashed_password=hashed_pwd )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_client_by_account(db: Session, account_number: str):
    return db.query(Client).filter(Client.account_number == account_number).first()


def create_client(db: Session, client: ClientCreate):
    db_client = Client( account_number=client.account_number, full_name=client.full_name, phone=client.phone,  email=client.email, address=client.address)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def create_ticket(db: Session, ticket: TicketCreate, creator_id: int):
    today = datetime.utcnow().strftime("%Y%m%d")
    total_tickets = db.query(Ticket).count()
    ticket_number = f"TKT-{today}-{total_tickets + 1:04d}"

    db_ticket = Ticket(ticket_number=ticket_number, client_id=ticket.client_id, created_by_id=creator_id,category=ticket.category,priority=ticket.priority,title=ticket.title,description=ticket.description,status=TicketStatus.new)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def get_tickets_filtered(db: Session, filters: TicketFilterParams, page: int = 1, size: int = 10):
    query = db.query(Ticket)

    if filters.status:
        query = query.filter(Ticket.status == filters.status)
        
    if filters.priority:
        query = query.filter(Ticket.priority == filters.priority)
        
    if filters.category:
        query = query.filter(Ticket.category == filters.category)
        
    if filters.assigned_to_id:
        query = query.filter(Ticket.assigned_to_id == filters.assigned_to_id)

    if filters.search_query:
        search = f"%{filters.search_query}%"
        query = query.join(Client).filter(or_(Ticket.ticket_number.ilike(search), Ticket.title.ilike(search),Client.full_name.ilike(search))
)

    total_count = query.count()
    skip = (page - 1) * size
    db_items = query.order_by(Ticket.created_at.desc()).offset(skip).limit(size).all()

    items = []
    for t in db_items:
        items.append(TicketListItem(id=t.id,ticket_number=t.ticket_number,client_full_name=t.client.full_name,client_phone=t.client.phone,category=t.category, priority=t.priority, status=t.status,title=t.title,assigned_to_name=t.assigned_to.full_name if t.assigned_to else None,created_at=t.created_at))

    return TicketListResponse(total_count=total_count, page=page, size=size, items=items)



def update_ticket(db: Session, ticket: Ticket, payload: TicketUpdateFull, user_id: int):
    update_data = payload.model_dump(exclude_unset=True)

    for field, new_value in update_data.items():
        if new_value is not None:
            old_value = getattr(ticket, field)
    
            if old_value != new_value:
                old_val_str = old_value.value if hasattr(old_value, 'value') else str(old_value)
                new_val_str = new_value.value if hasattr(new_value, 'value') else str(new_value)

                history_entry = TicketHistory( ticket_id=ticket.id, user_id=user_id, field_changed=field, old_value=old_val_str if old_value else None,new_value=new_val_str )
                db.add(history_entry)
                setattr(ticket, field, new_value)

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket


def get_dashboard_stats(db: Session):
    total = db.query(Ticket).count()
    
    return DashboardStats(
        total=total,
        new_count=db.query(Ticket).filter(Ticket.status == TicketStatus.new).count(),
        accepted=db.query(Ticket).filter(Ticket.status == TicketStatus.accepted).count(),
        in_progress=db.query(Ticket).filter(Ticket.status == TicketStatus.in_progress).count(),
        pending=db.query(Ticket).filter(Ticket.status == TicketStatus.pending).count(),
        resolved=db.query(Ticket).filter(Ticket.status == TicketStatus.resolved).count(),
        rejected=db.query(Ticket).filter(Ticket.status == TicketStatus.rejected).count(),
        cancelled=db.query(Ticket).filter(Ticket.status == TicketStatus.cancelled).count())