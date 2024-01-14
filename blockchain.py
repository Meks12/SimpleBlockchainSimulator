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
        #Ova metoda racuna hash blocka

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
        #Prvi block u blockchainu
    
   # def add_new_block(self, block):
    #    self.chain.append(block)
     #   #Dodaje novi block u blockchain

    def last_block(self):
        return self. chain[-1]
        #Vraca zadnji block u blockchainu
    
    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
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
    
    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL format')

    def mine(self):
        if not self.unconfirmed_transactions:
            return None

        last_block = self.last_block()
        proof = self.proof_of_work(last_block.proof)

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash,
                          proof=proof)
        new_block.hash = new_block.compute_hash()
        self.chain.append(new_block)
        self.unconfirmed_transactions = []
        return new_block

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
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to node {node}: {e}")
                continue  

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False
        #Metoda prolazi kroz cvorove te provjerava njihovu kopiju blockchaina
        #provjerava "chainove" te ih usporeduje

    