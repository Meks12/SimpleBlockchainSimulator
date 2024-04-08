from fastapi import FastAPI, HTTPException
from blockchain import Blockchain, Block
import requests
import time
from threading import Thread
from typing import List
from pydantic import BaseModel
import os 

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware konfiguracija
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Explicitly allow GET and POST methods
    allow_headers=["*"],
)


KNOWN_NODES = os.getenv('KNOWN_NODES', '').split(',')


NODE_ADDRESS = os.getenv('NODE_ADDRESS', 'http://127.0.0.1:8000')

app = FastAPI()
blockchain = Blockchain()

class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float 

class NodeRegister(BaseModel):
    address: str

@app.on_event("startup")
async def startup_event():
    register_with_discovery_node()
    register_with_known_nodes()
    start_refresh_task()


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

@app.get("/nodes/discover")
async def discover_nodes():
    return {"nodes": list(blockchain.nodes)}

def register_with_known_nodes():
    local_node_address = NODE_ADDRESS
    for node in KNOWN_NODES:
        if node:  # Provjera da node adresa nije prazna
            try:
                # Pokušaj registracije kod svakog poznatog node-a
                requests.post(f"http://{node}/nodes/register", json={"address": local_node_address})
            except requests.exceptions.RequestException as e:
                print(f"Error during registration with {node}: {e}")

def register_with_discovery_node():
    discovery_node_url = "http://127.0.0.1:8000" 
    local_node_address = NODE_ADDRESS
    try:
        requests.post(f"{discovery_node_url}/nodes/register", json={"address": local_node_address})
        response = requests.get(f"{discovery_node_url}/nodes/discover")
        if response.status_code == 200:
            nodes = response.json().get("nodes", [])
            for node in nodes:
                blockchain.register_node(node)
    except requests.exceptions.RequestException as e:
        print(f"Error during node discovery and registration: {e}")

def refresh_node_list():
    while True:
        try:
            discovery_node_url = "http://127.0.0.1:8000/nodes/discover"
            response = requests.get(discovery_node_url)
            if response.status_code == 200:
                nodes = response.json().get("nodes", [])
                for node in nodes:
                    full_node_url = f"http://{node}"
                    if full_node_url not in blockchain.nodes:
                        blockchain.register_node(full_node_url)
        except Exception as e:
            print(f"Error during node discovery refresh: {e}")
        time.sleep(60)  
def start_refresh_task():
    thread = Thread(target=refresh_node_list)
    thread.start()