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

class Blockchain:
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

    def hash_block(block):
        block_string = f"{block['index']}{block['transactions']}{block['timestamp']}{block['previous_hash']}{block['nonce']}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
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
    
    def resolve_conflicts(self):
        #Metoda prolazi kroz cvorove te provjerava njihovu kopiju blockchaina
        #provjerava "chainove" te ih usporeduje
        neighbours = self.nodes
        new_chain = None
        max_lenght = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_lenght and self.valid_chain(chain):
                    max_lenght = length
                    new_chain = chain
        
        if new_chain:
            self.chain = new_chain
            return True

        return False