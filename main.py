from fastapi import FastAPI, HTTPException
from blockchain import Blockchain, Block
import requests
from typing import List
from pydantic import BaseModel

app = FastAPI()
blockchain = Blockchain()

class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float 

class NodeRegister(BaseModel):
    address: str

@app.post("/transactions/new")
async def add_transaction(transaction: Transaction):
    transaction_data = transaction.model_dump()
    blockchain.add_new_transaction(transaction_data)
    for node in blockchain.nodes:
        if node != "your_node_identifier": #Treba ovdje logiku stavit
            requests.post(f'http://{node}/transactions/new', json=transaction_data)
    return {"message": "Transaction will be added to blockchain"}
    # Prima nove tranksakcije i dodaje ih u blockchain

@app.get("/mine")
def mine():
    new_block = blockchain.mine()
    if new_block:
        for node in blockchain.nodes:
            if node!= "your_node_identifier": #Treba ovdje logiku staviti
                requests.post(f'http://{node}/blocks/new', json=new_block.__dict__)
        return{"message": "New block has been forged", "block": new_block.__dict__}
    return HTTPException(status_code=500, detail="Mining failed")
    #Rudarenje novih blokova 
        

class Node(BaseModel):
    address: str

@app.post("/nodes/register")
def register_node(node: Node):
    blockchain.register_node(node.address)
    return {"message": "New node added", "total_nodes in blockchain": list(blockchain.nodes)}
    #Registriranje novog cvora u blockchain

@app.get("/nodes/resolve")
def consensus_algorithm():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {"message": "Our chain has been replaced", "new_chain is": blockchain.chain}
    else:
        response = {"message": "Our chain is accurate (authoritative)", "chain": blockchain.chain}
    return response
    #Sluzi za provjeravanje najduzeg chain-a uz pomoc konsenzus algoritma

@app.get("/chain")
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return {"length": len(chain_data), "chain": chain_data}
    #Dohvaca blockchain i vraca vrijednost bloka i duzinu blockchaina