from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    description: str


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    author_id: int

    class Config:
        from_attributes = True


class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int
    name: str

    class Config:
        from_attributes = True
