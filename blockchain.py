import requests
import hashlib
import time
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

    def compute_hash(self):
        block_string = f"{self.index}{self.transactions}{self.timestamp}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'proof': self.proof,
            'nonce': self.nonce,
            'hash': self.hash
        }

    @staticmethod
    def from_dict(block_data):
        block = Block(
            index=block_data['index'],
            transactions=block_data['transactions'],
            timestamp=block_data['timestamp'],
            previous_hash=block_data['previous_hash'],
            proof=block_data['proof'],
            nonce=block_data.get('nonce', 0)
        )
        block.hash = block_data['hash']  
        return block

class Blockchain:
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.create_genesis_block()
        self.unconfirmed_transactions = []

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0", 100)
        self.chain.append(genesis_block)

    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

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
        last_proof = last_block.proof
        proof = self.proof_of_work(last_proof)
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash,
                          proof=proof)
        self.chain.append(new_block)
        self.unconfirmed_transactions = []
        return new_block

    def resolve_conflicts(self):
        new_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain_data = response.json()['chain']
                
                chain = [Block.from_dict(block) for block in chain_data]
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False

    def is_chain_valid(self, chain):
        if len(chain) == 0:
            return True
        previous_block = chain[0]
        for i in range(1, len(chain)):
            block = chain[i]
            if block.hash != block.compute_hash() or block.previous_hash != previous_block.hash:
                return False
            previous_block = block
        return True

    def get_unconfirmed_transactions(self):
        return self.unconfirmed_transactions