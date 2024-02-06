from fastapi import FastAPI, HTTPException
from blockchain import Blockchain, Block
import requests
from typing import List
from pydantic import BaseModel
import os 

NODE_ADDRESS = os.getenv('NODE_ADDRESS', 'http://127.0.0.1:8000')

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
        if node != NODE_ADDRESS: 
            requests.post(f'http://{node}/transactions/new', json=transaction_data)
    return {"message": "Transaction will be added to blockchain"}
    # Prima nove tranksakcije i dodaje ih u blockchain


@app.get("/mine")
def mine():
    new_block = blockchain.mine()
    if new_block:
        block_data = {
            "index": new_block.index,
            "transactions": new_block.transactions,  
            "timestamp": new_block.timestamp,
            "previous_hash": new_block.previous_hash,
            "proof": new_block.proof,
            "nonce": new_block.nonce,
            "hash": new_block.hash
        }
        for node in blockchain.nodes:
            if node != NODE_ADDRESS:
                try:
                    requests.post(f'{node}/blocks/new', json=block_data)
                except requests.exceptions.RequestException as e:
                    print(f"Error broadcasting block to {node}: {e}")
        return {"message": "New block has been forged", "block": block_data}
    else:
        return HTTPException(status_code=500, detail="Failed to mine a new block")
    #Rudarenje novih blokova 
        

@app.post("/nodes/register")
def register_node(node: NodeRegister):
    blockchain.register_node(node.address)
    return {"message": "New node added", "total_nodes in blockchain": list(blockchain.nodes)}
    #Registriranje novog cvora u blockchain

@app.post("/blocks/new")
def recieve_new_block(block: dict):
    #Trebam logiku ovdje staviti
    if blockchain.validate_and_add_block(block):
        return {"message": "Block added to the chain"}
    return HTTPException(status_code=400, detail="Invalid block")

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