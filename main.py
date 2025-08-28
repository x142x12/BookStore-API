#this is the main file, contain api/endpoints that we uses.
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import models
from schemas import BookCreate, BookUpdate  
from database import engine, SessionLocal
from auth import get_current_user, get_user_exception



app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()



class BookStore(BaseModel):
    title: str
    author: str
    price: float
    published_date: datetime
    created_at: datetime
    updated_at: datetime
    user_id: int



@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.BookStore).all()



# @app.get("/bookstore/user")
# async def read_all_user(user: dict= Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     return db.query(models.BookStore)\
#         .filter(models.BookStore.user_id == user.get("id"))\
#         .all()    
#     return books 

# @app.get("/bookstore/user")
# async def read_all_user( user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     return db.query(models.BookStore)\
#         .filter(models.BookStore.user_id == user.get("id"))\
#         .all()
   
@app.get("/bookstore/user")
async def read_all_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    print("Current user ID:", user.get("id"))  # Add this line
    return db.query(models.BookStore)\
        .filter(models.BookStore.user_id == user.get("id"))\
        .all()   



@app.post("/book")
async def create_book(book: BookCreate, 
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception
     
    book_model = models.BookStore(
        title=book.title,
        author=book.author,
        price=book.price,
        published_date=book.published_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=user.get("id")
       )
    
    db.add(book_model)
    db.commit()
    db.refresh(book_model)

    return book_model



@app.get("/book/{book_id}")
async def get_book(book_id: int,
                   user: dict = Depends(get_current_user), 
                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    book = db.query(models.BookStore)\
        .filter(models.BookStore.id == book_id)\
        .filter(models.BookStore.user_id == user.get("id"))\
        .first()
    if book is not None:
        return book
    raise HTTPException(status_code=404, detail="Book not found")



@app.put("/book/{book_id}")
async def update_book(book_id: int, 
                      book: BookUpdate, 
                      user: dict = Depends(get_current_user), 
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception
    
    book_model = db.query(models.BookStore)\
        .filter(models.BookStore.id == book_id)\
        .filter(models.BookStore.user_id == user.get("id"))\
        .first()
        
    if book_model is None:
        raise http_exception()
    if book.title is not None:
        book_model.title = book.title
    if book.author is not None:
        book_model.author = book.author
    if book.price is not None:
        book_model.price = book.price
    if book.published_date is not None:
        book_model.published_date = book.published_date
    if book.created_at is not None:
        book_model.created_at = book.created_at
    if book.updated_at is not None:
        book_model.updated_at = book.updated_at
    if book.user_id is not None:
        book_model.user_id = book.user_id               
        

    #book_model.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(book_model)
    
    return successful_response(200)



@app.get("/books")
async def search(
    limit: int = 10,
    author: Optional[str] = None,
    title: Optional[str] = None,
    db: Session = Depends(get_db)):
    
    query = db.query(models.BookStore)

    if author:
        query = query.filter(models.BookStore.author.ilike(f"%{author}%"))
    if title:
        query = query.filter(models.BookStore.title.ilike(f"%{title}%"))

    return query.limit(limit).all()



@app.delete("/{book_id}")
async def delete_book(book_id: int,
                      user: dict = Depends(get_current_user),
                      db:Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    book_model = db.query(models.BookStore)\
        .filter(models.BookStore.id == book_id)\
        .filter(models.BookStore.user_id == user.get("id"))\
        .first()
                    
    if book_model is None:
        raise http_exception()
    
    db.query(models.BookStore)\
        .filter(models.BookStore.id == book_id)\
        .delete()
        
    db.commit()        
    
    return successful_response(200)



def successful_response(status_code: int):
     return {
        'status': status_code,
        'transaction': 'Successful'
    } 
 
 
 
def http_exception():
    return HTTPException(status_code = 404, detail="Book not found")     