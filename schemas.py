from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
import re
from typing import Optional, List
from datetime import datetime
from models import UserRole, TicketCategory, TicketPriority, TicketStatus



class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr 
    full_name: str = Field(..., min_length=3, max_length=50)
    role: UserRole 

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserChangePassword(BaseModel):
    old_password: str 
    new_password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserSimple(BaseModel):
    id: int
    full_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)




class ClientBase(BaseModel):
    account_number: str = Field(..., min_length=5, max_length=20, description="Megafon client personal account number")
    full_name: str = Field(..., min_length=3, max_length=50, description="Full name of the client")
    phone: str = Field(..., description="Client phone number in Tajikistan format, e.g., +992927777777")
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=200)

    
    @field_validator('phone')
    @classmethod
    def validate_tj_phone(cls, value: str):
        clean_phone = value.replace(" ", "")
        pattern = r'^(\+?992)?(50|55|77|88|90|91|92|93|98|44|33)\d{7}$'
        if not re.match(pattern, clean_phone):
            raise ValueError("Invalid phone number! Correct format is +99292XXXXXXX")
        return clean_phone

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClientSearch(BaseModel):
    id: int
    account_number: str
    full_name: str
    phone: str

    model_config = ConfigDict(from_attributes=True)



class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1)
    is_internal: bool = False

class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    user: UserSimple
    text: str
    is_internal: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)




class HistoryResponse(BaseModel):
    id: int
    user: UserSimple
    field_changed: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)




class TicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Subject of the ticket")
    description: str = Field(..., min_length=5, description="Detailed explanation of the issue")
    category: TicketCategory
    priority: TicketPriority = TicketPriority.medium

class TicketCreate(TicketBase):
    client_id: int

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    assigned_to_id: Optional[int] = None

class TicketResponse(TicketBase):
    id: int
    ticket_number: str
    client: ClientSearch
    created_by: UserSimple
    assigned_to: Optional[UserSimple] = None
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TicketDetailResponse(TicketResponse):
    comments: List[CommentResponse] = []
    history: List[HistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)

class TicketUpdateFull(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to_id: Optional[int] = None

class TicketListItem(BaseModel):
    id: int
    ticket_number: str
    client_full_name: str
    client_phone: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    title: str
    assigned_to_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TicketListResponse(BaseModel):
    total_count: int
    page: int
    size: int
    items: List[TicketListItem]

    model_config = ConfigDict(from_attributes=True)

class TicketFilterParams(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assigned_to_id: Optional[int] = None
    search_query: Optional[str] = Field(None, description='Search across ticket number or client name')




class ClientDetailResponse(ClientResponse):
    tickets: List[TicketListItem] = []

    model_config = ConfigDict(from_attributes=True)



class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token : str
    token_type: str = 'bearer'

    model_config = ConfigDict(from_attributes=True)
    
class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None

class DashboardStats(BaseModel):
    total: int
    new_count: int
    accepted: int
    in_progress: int
    pending: int
    resolved: int
    rejected: int
    cancelled: int