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


@app.route('/mine', methods=['GET'])
def mine():
    return "We'll mine a block"


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
