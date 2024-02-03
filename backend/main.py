import logging
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import crud
import models
import schemas

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db() -> Generator[SessionLocal, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health/")
def health() -> str:
    return "Ok"


@app.get("/authors/", response_model=list[schemas.Author])
def authors(db: Session = Depends(get_db)):
    logger.info(f"Received request to get all authors")
    return crud.get_authors(db)


@app.post("/authors/", response_model=schemas.Author)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)) -> schemas.Author:
    logger.info(f"Received request to create author: {author.name}")
    existing_author = crud.get_author_by_name(db, author.name)

    if existing_author:
        logger.exception(f"Author name already exists")
        raise HTTPException(status_code=400, detail="Author already exists")

    created_author = crud.create_author(db=db, author=author)
    logger.info(f"Author: {author.name} created")
    return created_author


@app.get("/books/", response_model=list[schemas.Book])
def books(db: Session = Depends(get_db)):
    logger.info(f"Received request to get all books")
    return crud.get_books(db)


@app.post("/books/", response_model=schemas.Book)
def add_book(book: schemas.BookCreate, author_name: str, db: Session = Depends(get_db)):
    logger.info(f"Received request to add a book: {book} with author name: {author_name}")
    author = crud.get_author_by_name(db, author_name)

    if not author:
        logger.info(f"No author found with the name: {author_name}. Creating a new author.")
        author = crud.create_author(db, schemas.AuthorCreate(name=author_name))
    elif book.title in [x.title for x in author.books]:
        logger.exception(f"Book with title: {book.title} for author {author_name} already exists")
        raise HTTPException(status_code=409, detail="Book title with that author already exists")

    added_book = crud.add_book(db, book, author.id)
    logger.info(f"Book: {book.title} added for author: {author_name}")

    return added_book


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000, host="localhost")
