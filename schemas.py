from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class UserBase(BaseModel):
    name: str = ""
    phone: str = ""
    password: str = ""
    email: str = ""
    country: str = ""
    profilePic: str = ""

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    sender: str
    receiver: str
    message: str
    timestamp: int
    messageType: str = "text"
    fileUrl: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    class Config:
        from_attributes = True

class ApiResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None

class StatusCreate(BaseModel):
    userId: str
    fileUrl: Optional[str] = None
    mediaUrl: Optional[str] = None
    mediaType: str = "image"
    audioUrl: Optional[str] = None
    caption: Optional[str] = None
    timestamp: int

class GroupCreate(BaseModel):
    groupId: str
    name: str
    createdBy: str
    members: List[str] # List of phone numbers
    timestamp: int

class StatusCommentCreate(BaseModel):
    statusId: int
    userId: str
    text: str
    timestamp: int

class ContactCreate(BaseModel):
    ownerId: str
    contactPhone: str
