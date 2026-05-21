import enum
from datetime import datetime

from sqlalchemy import Column , Integer , String , Boolean , DateTime , Text , ForeignKey , Enum
from database import Base

class UserRole(str , enum.Enum):
    superadmin = 'superadmin'
    front_office = 'front_office'
    back_office = 'back_office'

class TicketCategory(str , enum.Enum):
    complaint = 'complaint'
    request = 'request'
    consultation = 'consultation'
    technical = 'tecnical'
    billing = 'billing'

class TicketPriority(str , enum.Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    urgent = 'urgent'

class TicketStatus(str , enum.Enum):
    new = 'new'
    accepted = 'accepted'
    in_progress = 'in_progress'
    peding = 'peding'
    resolved = 'resolved'
    rejected = 'rejected'
    cancelled = 'cancelled'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer , primary_key=True , index=True , autoincrement=True)
    username = Column(String , unique=True , nullable=False , index=True)
    email = Column(String , unique=True , nullable=False , index=True)
    full_name = Column(String , nullable=False)
    hashed_password = Column(String , nullable=False)
    role = Column(Enum(UserRole) , default=UserRole.front_office , nullable=False)
    is_active = Column(Boolean , default=True , nullable=False)
    created_at = Column(DateTime , default=datetime.utcnow , nullable=False)


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_number = Column(String(20), unique=True, nullable=False, index=True) 
    full_name = Column(String, nullable=False, index=True)                  
    phone = Column(String(20), nullable=False, index=True)                       
    email = Column(String, nullable=True)                                   
    address = Column(String, nullable=True)                                 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)   


class TIcket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer , primary_key=True , index=True , autoincrement=True)
    ticket_number = Column(String(20) , unique=True , nullable=False , index=True)
    client_id = Column(Integer , ForeignKey('clients.id', ondelete="CASCADE") , nullable=False)
    created_by_id = Column(Integer ,ForeignKey('users.id'), nullable=True)
    assigned_to_id = Column(Integer , ForeignKey("users.id") , nullable=True)
    category = Column(Enum(TicketCategory) , nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.medium , nullable=False)
    status = Column(Enum(TicketStatus) , default=TicketStatus.new , nullable=False)
    title = Column(String , nullable=False)
    description = Column(Text , nullable=False)
    created_at = Column(DateTime , default=datetime.utcnow , nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow , onupdate=datetime.utcnow, nullable=False)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)                                          
    is_internal = Column(Boolean, default=False, nullable=False)                
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)           
    field_changed = Column(String(50), nullable=False)                           
    old_value = Column(String(200), nullable=True)                              
    new_value = Column(String(200), nullable=True)                              
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)