import os
import time
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

import models, schemas
from database import SessionLocal, engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OfflineChatApp Backend")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/register", response_model=schemas.ApiResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if db_user:
        return {"status": "error", "message": "Phone number already registered", "data": None}
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "User registered successfully", "data": user.dict()}

@app.post("/login", response_model=schemas.ApiResponse)
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.phone == user.phone,
        models.User.password == user.password
    ).first()
    
    if not db_user:
        return {"status": "error", "message": "Invalid phone or password", "data": None}
    
    return {"status": "success", "message": "Login successful", "data": schemas.UserResponse.from_orm(db_user).dict()}

@app.get("/getUsers", response_model=schemas.ApiResponse)
def check_user(phone: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone == phone).first()
    if not db_user:
         return {"status": "error", "message": "User not found", "data": None}
    return {"status": "success", "message": "User found", "data": schemas.UserResponse.from_orm(db_user).dict()}

@app.get("/getAllUsers", response_model=schemas.ApiResponse)
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    data = [schemas.UserResponse.from_orm(u).dict() for u in users]
    return {"status": "success", "message": "Users retrieved", "data": data}

@app.post("/sendMessage", response_model=schemas.ApiResponse)
def send_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    new_msg = models.Message(**msg.dict())
    db.add(new_msg)
    db.commit()
    return {"status": "success", "message": "Message sent", "data": None}

@app.get("/getMessages", response_model=schemas.ApiResponse)
def get_messages(user1: str, user2: str, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        ((models.Message.sender == user1) & (models.Message.receiver == user2)) |
        ((models.Message.sender == user2) & (models.Message.receiver == user1))
    ).order_by(models.Message.timestamp.asc()).all()
    
    data = [schemas.MessageResponse.from_orm(m).dict() for m in messages]
    return {"status": "success", "message": "Messages retrieved", "data": data}

@app.post("/upload", response_model=schemas.ApiResponse)
async def upload_file(file: UploadFile = File(...), filename: str = ""):
    file_location = os.path.join(UPLOAD_DIR, filename or file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    file_url = f"/uploads/{filename or file.filename}"
    return {"status": "success", "message": "File uploaded", "data": {"url": file_url, "fileUrl": file_url}}

# Serve uploaded files if needed
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/deleteUser", response_model=schemas.ApiResponse)
def delete_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return {"status": "success", "message": "User deleted", "data": None}

@app.post("/updateProfile", response_model=schemas.ApiResponse)
def update_profile(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if db_user:
        for key, value in user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return {"status": "success", "message": "Profile updated", "data": schemas.UserResponse.from_orm(db_user).dict()}
    return {"status": "error", "message": "User not found", "data": None}

# Group Management
@app.post("/group/create", response_model=schemas.ApiResponse)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    db_group = db.query(models.Group).filter(models.Group.groupId == group.groupId).first()
    if db_group:
        return {"status": "error", "message": "Group ID already exists", "data": None}
    
    # Exclude 'members' from dict as it's not in the Group model
    group_data = group.dict()
    members = group_data.pop("members", [])
    
    new_group = models.Group(**group_data)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    # Add members
    for phone in members:
        db_member = models.GroupMember(groupId=new_group.groupId, userPhone=phone)
        db.add(db_member)
    db.commit()
    
    return {"status": "success", "message": "Group created successfully", "data": group.dict()}

@app.get("/group/list", response_model=schemas.ApiResponse)
def list_groups(userId: Optional[str] = None, db: Session = Depends(get_db)):
    if userId:
        # Get groups where user is a member
        group_ids = db.query(models.GroupMember.groupId).filter(models.GroupMember.userPhone == userId).all()
        ids = [g[0] for g in group_ids]
        groups = db.query(models.Group).filter(models.Group.groupId.in_(ids) | (models.Group.createdBy == userId)).all()
    else:
        groups = db.query(models.Group).all()
        
    data = [dict(id=g.id, groupId=g.groupId, name=g.name, createdBy=g.createdBy, timestamp=g.timestamp) for g in groups]
    return {"status": "success", "message": "Groups retrieved", "data": data}

@app.post("/group/delete", response_model=schemas.ApiResponse)
def delete_group(groupId: str, db: Session = Depends(get_db)):
    db_group = db.query(models.Group).filter(models.Group.groupId == groupId).first()
    if db_group:
        db.delete(db_group)
        db.commit()
        return {"status": "success", "message": "Group deleted", "data": None}
    return {"status": "error", "message": "Group not found", "data": None}

# Status Management
@app.post("/status/create", response_model=schemas.ApiResponse)
def create_status(status: schemas.StatusCreate, db: Session = Depends(get_db)):
    status_dict = status.dict()
    if status.mediaUrl and not status.fileUrl:
        status_dict["fileUrl"] = status.mediaUrl
    status_dict.pop("mediaUrl", None)

    new_status = models.Status(**status_dict)
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    return {"status": "success", "message": "Status created", "data": status_dict}

@app.get("/status/list", response_model=List[dict])
def list_statuses(userId: str, db: Session = Depends(get_db)):
    # Return statuses from the last 24 hours
    current_time = int(time.time() * 1000)
    one_day_ago = current_time - (24 * 60 * 60 * 1000)
    
    # Get contacts of this user
    contacts = db.query(models.Contact.contactPhone).filter(models.Contact.ownerId == userId).all()
    contact_list = [c[0] for c in contacts]
    contact_list.append(userId) # Include self
    
    statuses = db.query(models.Status).filter(
        (models.Status.timestamp > one_day_ago) & 
        (models.Status.userId.in_(contact_list))
    ).all()
    
    result = []
    for s in statuses:
        # Get comments for this status
        comments = db.query(models.StatusComment).filter(models.StatusComment.statusId == s.id).all()
        comment_data = [dict(userId=c.userId, text=c.text, timestamp=c.timestamp) for c in comments]
        
        result.append(dict(
            id=s.id, 
            user_id=s.userId, 
            media_url=s.fileUrl, 
            media_type=s.mediaType,
            audio_url=s.audioUrl, 
            caption=s.caption, 
            timestamp=s.timestamp,
            comments=comment_data
        ))
    return result

@app.post("/status/comment", response_model=schemas.ApiResponse)
def status_comment(comment: schemas.StatusCommentCreate, db: Session = Depends(get_db)):
    new_comment = models.StatusComment(**comment.dict())
    db.add(new_comment)
    db.commit()
    return {"status": "success", "message": "Comment posted", "data": None}

# Contact Management
@app.post("/contact/add", response_model=schemas.ApiResponse)
def add_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(
        models.Contact.ownerId == contact.ownerId,
        models.Contact.contactPhone == contact.contactPhone
    ).first()
    if db_contact:
        return {"status": "success", "message": "Contact already exists", "data": None}
    
    new_contact = models.Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    return {"status": "success", "message": "Contact added", "data": None}

@app.get("/contact/list", response_model=schemas.ApiResponse)
def list_contacts(userId: str, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).filter(models.Contact.ownerId == userId).all()
    data = [dict(phone=c.contactPhone) for c in contacts]
    return {"status": "success", "message": "Contacts retrieved", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
