from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import *
from schemas import *
import auth
from datetime import datetime


def get_user_by_username(db : Session , username:str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db : Session , email:str):
    return db.query(User).filter(User.email == email).first()

def create_user(db :Session , user : UserCreate):
    hashed_pwd = auth.get_password_pash(user.password)
    db_user = User(username=user.username , email=user.email , full_name=user.full_name , role=user.role , hashed_pasword=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_client_by_account(db:Session , account_number:str):
    return db.query(Client).filter(Client.account_number == account_number).first()

def create_client(db :Session , client : ClientCreate):
    db_client = Client(account_number=client.account_number,full_name=client.full_name,phone=client.phone, email=client.email,address=client.address)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def create_ticket(db: Session, ticket: TicketCreate, creator_id: int):
    today = datetime.utcnow().strftime("%Y%m%d")
    
    total_tickets = db.query(Ticket).count()
    ticket_number = f"TKT-{today}-{total_tickets + 1:04d}"

    db_ticket = Ticket(ticket_number=ticket_number,client_id=ticket.client_id,created_by_id=creator_id,category=ticket.category,priority=ticket.priority,title=ticket.title,description=ticket.description,status=TicketStatus.new)
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
        query = query.join(Client).filter(
            or_(
                Ticket.ticket_number.ilike(search),
                Ticket.title.ilike(search),
                Client.full_name.ilike(search)
            )
        )

    total_count = query.count()

    skip = (page - 1) * size
    db_items = query.order_by(Ticket.created_at.desc()).offset(skip).limit(size).all()

    items = []
    for t in db_items:
        items.append(TicketListItem(
            id=t.id,
            ticket_number=t.ticket_number,
            client_full_name=t.client.full_name,
            client_phone=t.client.phone,
            category=t.category,
            priority=t.priority,
            status=t.status,
            title=t.title,
            assigned_to_name=t.assigned_to.full_name if t.assigned_to else None,
            created_at=t.created_at
        ))

    return TicketListResponse(total_count=total_count,page=page,size=size,items=items)



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
        cancelled=db.query(Ticket).filter(Ticket.status == TicketStatus.cancelled).count()
    )