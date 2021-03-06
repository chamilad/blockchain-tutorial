from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain

'''
This is an HTTP server to interact with the blockchain.

The new transaction request body should look like the following

====================
{
 "sender": "my address",
 "recipient": "someone else's address",
 "amount": 5
}
====================

This server runs on port 5000
'''

app = Flask(__name__)
# unique node id
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

'''
What to do in mining
1. Calculate PoW
2. Reward with a new transaction of 1
3. Create a new block in the chain
'''


@app.route('/mine', methods=['GET'])
def mine():
    # 1. Calc PoW
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])

    # 2. Reward 1 coin with a transaction
    # recipient is us, because we mined it precious!!
    blockchain.new_transaction(sender=0, recipient=node_identifier, amount=1)

    # 3. Create a new block
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'New block forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # sanitation
    required = ['sender', 'recipient', 'amount']
    # TODO: check 'all' functionality
    if not all(k in values for k in required):
        return "Missing values", 400

    # request looks good, create transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to the Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


'''
Blockchains are distributed, which requires a verification step to check whether we are operating on the same 
blockchain. This is called consensus.

Nodes should be aware of other nodes in the network. i.e. there should be a registry of nodes.
'''


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a list of node addresses.", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': "New nodes have been added",
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': "Our chain was replaced",
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    print(f'Node ID: {node_identifier}')
    app.run(host='0.0.0.0', port=5000)
