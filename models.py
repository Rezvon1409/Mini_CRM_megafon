import enum
from datetime import datetime

from sqlalchemy import Column , Integer , String , Boolean , DateTime , Text , ForeignKey , Enum
from sqlalchemy.orm import relationship
from database import Base

class UserRole(str , enum.Enum):
    superadmin = 'superadmin'
    front_office = 'front_office'
    back_office = 'back_office'

class TicketCategory(str , enum.Enum):
    complaint = 'complaint'
    request = 'request'
    consultation = 'consultation'
    technical = 'technical'
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
    pending = 'pending'
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


    created_tickets = relationship("Ticket" , back_populates='created_by' ,foreign_keys='[Ticket.created_by_id]')
    assingned_tickets = relationship("Ticket" , back_populates="assigned_to" , foreign_keys='[Ticket.assigned_to_id]')
    comments = relationship("Comment" , back_populates='user')
    history_records = relationship('TicketHistory' , back_populates='user')



class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_number = Column(String(20), unique=True, nullable=False, index=True) 
    full_name = Column(String, nullable=False, index=True)                  
    phone = Column(String(20), nullable=False, index=True)                       
    email = Column(String, nullable=True)                                   
    address = Column(String, nullable=True)                                 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  


    tickets = relationship('Ticket' , back_populates='client' , cascade='all , delete-orphan') 


class Ticket(Base):
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


    client = relationship('Client', back_populates='tickets')
    created_by = relationship('User', back_populates='created_tickets' , foreign_keys=[created_by_id])
    assigned_to = relationship('User' , back_populates='assigned_tickets' , foreign_keys=[assigned_to_id])
    comments = relationship('Comment' , back_populates='ticket' , cascade='all , delete-orphan')
    history = relationship('TicketHIstory' , back_populates='ticket' , cascade='all , delete-orphan')


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)                                          
    is_internal = Column(Boolean, default=False, nullable=False)                
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    ticket = relationship('Ticket' , back_populates='comments')
    user = relationship("User" , back_populates='comments')

class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)           
    field_changed = Column(String, nullable=False)                           
    old_value = Column(String, nullable=True)                              
    new_value = Column(String, nullable=True)                              
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    ticket = relationship("Ticket", back_populates="history")
    user = relationship("User", back_populates="history_records")