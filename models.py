from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    country = Column(String)
    profilePic = Column(String)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    receiver = Column(String, index=True)
    message = Column(Text)
    timestamp = Column(Integer)
    messageType = Column(String, default="text")
    fileUrl = Column(String, nullable=True)

class Status(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String, index=True)
    fileUrl = Column(String, nullable=True)
    mediaType = Column(String, default="image") # "image" or "video"
    audioUrl = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    timestamp = Column(Integer)

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    groupId = Column(String, unique=True, index=True)
    name = Column(String)
    createdBy = Column(String)
    timestamp = Column(Integer)

class GroupMember(Base):
    __tablename__ = "group_members"
    id = Column(Integer, primary_key=True, index=True)
    groupId = Column(String, ForeignKey("groups.groupId"))
    userPhone = Column(String, ForeignKey("users.phone"))

class StatusComment(Base):
    __tablename__ = "status_comments"
    id = Column(Integer, primary_key=True, index=True)
    statusId = Column(Integer, ForeignKey("statuses.id"))
    userId = Column(String)
    text = Column(String)
    timestamp = Column(Integer)

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    ownerId = Column(String, index=True) # The user who owns this contact list
    contactPhone = Column(String, index=True) # The phone number of the contact
