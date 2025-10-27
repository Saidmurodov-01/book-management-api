from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal
from typing import List, Optional

router = APIRouter(prefix="/books", tags=["Books"])

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET all books
@router.get("/", response_model=List[schemas.Book])
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

# GET one book by ID
@router.get("/{book_id}", response_model=schemas.Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# POST create a new book
@router.post("/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    new_book = models.Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

# PUT update a book
@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, updated_book: schemas.BookCreate, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in updated_book.dict().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

# DELETE a book
@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"detail": "Book deleted"}

# SEARCH books by title or author
@router.get("/search", response_model=List[schemas.Book])
def search_books(search: str, db: Session = Depends(get_db)):
    results = db.query(models.Book).filter(
        (models.Book.title.ilike(f"%{search}%")) |
        (models.Book.author.ilike(f"%{search}%"))
    ).all()
    return results

# FILTER books by year range
@router.get("/filter", response_model=List[schemas.Book])
def filter_books(min: Optional[int] = None, max: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Book)
    if min is not None:
        query = query.filter(models.Book.year >= min)
    if max is not None:
        query = query.filter(models.Book.year <= max)
    return query.all()