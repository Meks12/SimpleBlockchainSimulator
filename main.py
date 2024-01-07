from fastapi import FastAPI
from blockchain import Blockchain
from pydantic import BaseModel

app = FastAPI()
blockchain = Blockchain()

class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float 

@app.post("/transactions/new")
def add_transaction(transaction: Transaction):
    blockchain.add_new_transaction(transaction.model_dump())
    return {"message": "Transaction will be added to blockchain"}

@app.get("/mine")
def mine_unconfirmed_transactions():
    #Mining novog blocka
    return {"Message" "New block has been mined"}

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
    chain_data = [block.__dict__ for block in blockchain.chain]
    return {"length": len(chain_data), "chain": chain_data}
    #Dohvaca blockchain i vraca vrijednost bloka i duzinu blockchaina