from typing import Type

from sqlalchemy.orm import Session

import models
import schemas


def get_author_by_name(db: Session, author_name: str) -> Type[models.Author] | None:
    return db.query(models.Author).filter(models.Author.name == author_name).first()


def get_authors(db: Session) -> list[Type[models.Author]]:
    return db.query(models.Author).all()


def create_author(db: Session, author: schemas.AuthorCreate) -> models.Author:
    db_author = models.Author(name=author.name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_books(db: Session) -> list[Type[models.Book]]:
    return db.query(models.Book).all()


def add_book(db: Session, book: schemas.BookCreate, author_id: int) -> models.Book:
    db_book = models.Book(
       **book.dict(),
       author_id=author_id
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
