import hashlib
import time

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