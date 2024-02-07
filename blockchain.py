import hashlib
import time
import requests
from urllib.parse import urlparse

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, proof, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.proof = proof
        self.nonce = nonce
        self.hash = self.compute_hash()
        #Index - pozicija blocka u blockchainu
        #Transactions - lista transakcija u blocku
        #Timestamp = vrijeme kada je block napravljen
        #Previous_hash = prijasnji block 
        #nonce = vrijednost koja se koristi u miningu i POF
        #self.hash = hash ovog blocka koji se racuna pomocu compute_hash

    def compute_hash(self):
        block_string = f"{self.index}{self.transactions}{self.timestamp}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
        #Ova metoda kreira hash blocka za osiguranje integriteta

class Blockchain:
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.create_genesis_block()
        self.unconfirmed_transactions = []
        #Inicijalizacija blockchaina sa praznom listom
        
    def create_genesis_block(self):
         genesis_block = Block(0, [], time.time(), "0", proof=100)
         genesis_block.hash = genesis_block.compute_hash()
         self.chain.append(genesis_block)
        #Prvi block u blockchainu sa predefiniranim vrijednostima

    def last_block(self):
        return self. chain[-1]
        #Vraca zadnji block u blockchainu
    
    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof
        #Metoda proof of work - vjerojatno treba dorada
    
    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
        #Validira ako proof_value rjesava pof zadatak

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
        #Dodaje novu transakciju na listu transakcija koje cekaju sljedeci "mined node"

    def add_new_block(self, block, proof):
        last_block = self.last_block()
        if last_block.hash != block.previous_hash or not self.valid_proof(last_block.proof, proof):
            return False
        block.hash = block.compute_hash()
        self.chain.append(block)
        return True
        #Dodaje novi block u blockchain nakon validacije te provjere prethodnog hasha - potencijalna dorada
    
    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL format')
        #Dodaje cvor u mrezu ostalih cvorova

    def mine(self):
        if not self.unconfirmed_transactions:
            return None

        last_block = self.last_block()
        last_proof = last_block.proof
        proof = self.proof_of_work(last_proof)

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash,
                          proof=proof)
        new_block.hash = new_block.compute_hash()
        self.chain.append(new_block)
        self.unconfirmed_transactions = []
        
        return new_block
        #Mining novih blokova, izvrsavanje pof algoritma i dodavanje novog bloka u sustav - dorada 

    def hash_block(block):
        block_string = f"{block['index']}{block['transactions']}{block['timestamp']}{block['previous_hash']}{block['nonce']}"
        return hashlib.sha256(block_string.encode()).hexdigest()
        #Racuna hash blocka

    def is_chain_valid(self, chain):
        #Validacija Blockchaina
        #Prvi block nakon genesisa
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]

            #Sadasnji hash blocka
            if current_block.hash != current_block.compute_hash():
                return False

            #Prijasnji hash blocka
            if current_block.previous_hash != previous_block.hash:
                return False
            
        return True
    
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
      
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False
    def validate_and_add_block(self, block_data):
        new_block = Block(
            index=block_data["index"],
            transactions=[Transaction(sender=tx["sender"], recipient=tx["recipient"], amount=tx["amount"]) for tx in block_data["transactions"]],
            timestamp=block_data["timestamp"],
            previous_hash=block_data["previous_hash"],
            proof=block_data["proof"],
            nonce=block_data.get("nonce", 0)
        )
        if new_block.previous_hash != self.chain[-1].hash:
            return False
        last_proof = self.chain[-1].proof
        if not self.valid_proof(last_proof, new_block.proof):
            return False
        self.chain.append(new_block)
        self.unconfirmed_transactions = []