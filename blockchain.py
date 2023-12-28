import hashlib
import time
import requests
from urllib.parse import urlparse

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute.hash()
        #Index - pozicija blocka u blockchainu
        #Transactions - lista transakcija u blocku
        #Timestamp = vrijeme kada je block napravljen
        #Previous_hash = prijasnji block 
        #nonce = vrijednost koja se koristi u miningu i POF
        #self.hash = hash ovog blocka koji se racuna pomocu compute_hash

    def compute_hash(self):
        block_string = f"{self.index}{self.transactions}{self.timestamp}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
        #Ova metoda racuna hash blocka

class blockchain:
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.create_genesis_block()
        #Inicijalizacija blockchaina sa praznom listom
        
    def create_genesis_block(self):
         genesis_block = Block(0, [], time.time(), "0")
         self.chain.append(genesis_block)
        #Prvi block u blockchainu
    
    def add_new_block(self, block):
        self.chain.append(block)
        #Dodaje novi block u blockchain

    def last_block(self):
        return self. chain[-1]
        #Vraca zadnji block u blockchainu
    
    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def valid_chain(self, chain):
        #Validacija Blockchaina
        #Prvi block nakon genesisa
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]

            #Sadasnji hash blocka
            if current_block['hash'] != self.hash_block(current_block):
                return False

            #Prijasnji hash blocka
            if current_block['previous_hash'] != previous_block['hash']:
                return False

        return True