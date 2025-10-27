from fastapi import FastAPI
from app.routers import books

app = FastAPI()

app.include_router(books.router)