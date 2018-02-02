import hashlib
import json
from time import time
from urllib.parse import urlparse

import requests


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # create the genesis block with no predecessors when the blockchain is initiated
        self.new_block(previous_hash=1, proof=100)

        # unique node addresses, no duplicates
        self.nodes = set()

    '''
    the proof is the result of mining / proof of work
    the goal of PoW (proof of work) is to find a number which solves a problem/challenge
    the number must be difficult to find, but easy to verify computationally
    PoW algorithm is called the Hashcash
    mining is finding numbers from this hashcash. A successful mining is awarded with a coin,
    in a transaction. The numbers are easily verifiable
    
    the following PoW is to find a number p that when hashed with the previous pow will produce a hash 
    value with 4 leading 0s
    
    the more these numbers are checked for, the more time it takes to produce a pow
    '''

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    def register_node(self, address):
        """
        Add a new node to the list of nodes maintaining the blockchain
        :param address: in the format of http://<IP>:<PORT>
        :return:
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Check if the blockchain is valid in terms of proof and hash
        :param chain:
        :return:
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n----------------\n")
            # verify hash integrity
            if block['previous_hash'] != self.hash(last_block):
                return False

            # verify proof integrity
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Consensus
        Our rule: longest valid chain is the authoritative

        :return: True if conflicts were found and resolved, False if no conflicts found
        """
        neighbours = self.nodes
        new_chain = None

        # anything that goes beyond should replace my existing one
        max_length = len(self.chain)

        # check chains from all nodes
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                their_length = response.json()['length']
                their_chain = response.json()['chain']

                # check if theirs is longer
                if their_length < max_length and self.valid_chain(their_chain):
                    max_length = their_length
                    new_chain = their_chain

        # after going through the neighbour list
        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    '''
    Anatomy of a block
    
        block = {
            'index': 1,
            'timestamp': 1506057125.900785,
            'transactions': [
                {
                    'sender': "8527147fe1f5426f9dd545de4b27ee00",
                    'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
                    'amount': 5,
                }
            ],
            'proof': 324984774000,
            'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        }
    '''

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
            # if previous_hash is None, the last item of the chain will be taken
        }

        # new block, so new transaction list, reset the staging area
        self.current_transactions = []

        # add block to chain
        self.chain.append(block)

        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        # index of te block that will hold this transaction
        # because these transactions will go to the next block to be created
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # ordered dictionary
        # TODO: what dictionary?
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # return the last item in the chain
        return self.chain[-1]
