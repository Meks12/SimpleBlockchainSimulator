from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from urllib.parse import urlparse
import requests
import os
from threading import Thread
import time

from blockchain import Blockchain, Block

app = FastAPI()

# Dodavanje CORS middleware za dozvoljavanje zahtjeva iz različitih izvora
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ovo dozvoljava sve origin, prilagodite prema potrebi
    allow_credentials=True,
    allow_methods=["*"],  # Dozvoljava sve metode
    allow_headers=["*"],  # Dozvoljava sve header-e
)

blockchain = Blockchain()
nodes = set()

class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float 

class NodeRegister(BaseModel):
    address: str

@app.on_event("startup")
async def startup_event():
    register_with_discovery_node()
    start_refresh_task()

@app.post("/transactions/new")
async def add_transaction(request: Request, transaction: Transaction):
    transaction_data = transaction.dict()
    blockchain.add_new_transaction(transaction_data)
    client_host = str(request.client.host)
    for node in nodes:
        if "http://" + client_host not in node:  # Pretpostavljamo da adrese node-a uključuju http://
            requests.post(f'{node}/transactions/new', json=transaction_data)
    return {"message": "Transaction will be added to blockchain"}

@app.get("/transactions/unconfirmed")
async def get_unconfirmed_transactions():
    return {"unconfirmed_transactions": blockchain.get_unconfirmed_transactions()}

@app.get("/mine")
def mine(request: Request):
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
        client_host = str(request.client.host)
        for node in nodes:
            if "http://" + client_host not in node:
                try:
                    requests.post(f'{node}/blocks/new', json=block_data)
                except requests.exceptions.RequestException as e:
                    print(f"Error broadcasting block to {node}: {e}")
        return {"message": "New block has been forged", "block": block_data}
    else:
        return HTTPException(status_code=500, detail="Failed to mine a new block")

@app.post("/nodes/register")
def register_node(node: NodeRegister):
    parsed_url = urlparse(node.address)
    valid_address = parsed_url.netloc or parsed_url.path
    if valid_address and valid_address not in blockchain.nodes:
        blockchain.nodes.add(valid_address)
        nodes.add(node.address)  # Maintain local and blockchain node sets
        return {"message": "New node added", "total_nodes": list(blockchain.nodes)}
    else:
        return HTTPException(status_code=400, detail="Invalid or duplicate node address")


#@app.post("/register")
#async def register_node(node_address: str):
#   nodes.add(node_address)
#    return {"status": "success", "message": "Node registered"}

@app.get("/nodes")
async def get_nodes():
    return {"nodes": list(nodes)}

@app.get("/nodes/resolve")
def consensus_algorithm():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {"message": "Our chain has been replaced", "new_chain": blockchain.chain}
    else:
        response = {"message": "Our chain is authoritative", "chain": blockchain.chain}
    return response

@app.get("/chain")
def get_chain():
    chain_data = [block.__dict__ for block in blockchain.chain]
    return {"length": len(chain_data), "chain": chain_data}

def register_with_discovery_node():
    # Potencijalna implementacija za registraciju s centralnim discovery nodeom
    pass

def start_refresh_task():
    thread = Thread(target=refresh_node_list)
    thread.start()

def refresh_node_list():
    while True:
        try:
            for node in list(nodes): 
                response = requests.get(f"http://{node}/nodes")
                if response.status_code == 200:
                    new_nodes = response.json().get("nodes", [])
                    nodes.update(new_nodes)  
        except Exception as e:
            print(f"Error during node discovery refresh: {e}")
        time.sleep(60)