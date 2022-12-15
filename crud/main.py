from fastapi import FastAPI, Depends, Response, status, HTTPException
import schemas, models, webtoken, oauth2
from database import engine, get_db
from sqlalchemy.orm import Session
from typing import List
from hashing import Hash
from passlib.context import CryptContext

app = FastAPI()

models.Base.metadata.create_all(engine)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post('/user', status_code=status.HTTP_201_CREATED, tags=['users'])
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    hashed_password = password_context.hash(request.password)

    new_user = models.User(name=request.name,
                           email_address=request.email_address,
                           password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.delete('/user/{id]', status_code=status.HTTP_204_NO_CONTENT, tags=['users'])
def delete_user(id, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} not exists")

    user.delete(synchronize_session=False)
    db.commit()
    return 'done'

@app.get('/user', status_code=200, response_model=List[schemas.ShowUser], tags=['users'])
def list_all_user(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    return users

@app.get('/user/{id}', status_code=200, response_model=schemas.ShowUser, tags=['users'])
def show_user(id, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} not exists")
    return user

@app.put('/user/{id}', status_code=status.HTTP_202_ACCEPTED, tags=['users'])
def update_user(id, request: schemas.User, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} not exists")

    user.update(request)
    db.commit()
    return 'updated'

@app.post('/login', tags=['Authentication'])
def login(request: schemas.Login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email_address == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Invalid credentials')
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Incorrect password")

    access_token = webtoken.create_access_token(data={"sub": user.email_address})
    return {'access_token': access_token, 'token_type': 'bearer'}
