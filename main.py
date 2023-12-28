"""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"} """

from fastapi import FastAPI
from blockchain import Blockchain
from pydantic import BaseModel

app = FastAPI()
blockchain = Blockchain()