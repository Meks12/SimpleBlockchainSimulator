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

@app.get("/chain")
def get_chain():
    chain_data = [block.__dict__ for block in blockchain.chain]
    return {"length": len(chain_data), "chain": chain_data}
    #Dohvaca blockchain i vraca vrijednost bloka i duzinu blockchaina

@app.post("/transactions/new")
def add_transaction(transaction: dict):
    # dodavanje transakcije u bc
    return {"message": "Transaction will be added"}