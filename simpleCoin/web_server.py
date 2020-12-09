from multiprocessing import Manager, Process
from flask import Flask, request, jsonify
from typing import List, Tuple
import requests
import sys
import json
from datetime import datetime

from common.identification import validate_signature, generate_ECDSA_keys
from miner import Miner

from blockchain_db import BlockchainDB
from public_keys_db import PublicKeysDB


node = Flask(__name__)


def broadcast_to_peers(route: str, data, peers: List[Tuple[str, int]], ttl):
    try:
        if ttl > 0:
            print(f"[SENDING TO PEERS] {data} \n{peers}")
            for peer in peers:
                url = f'http://{peer[0]}:{peer[1]}/{route}'
                print(f"[POST DATA] to {url}")
                data['ttl'] = ttl
                print(data)
                headers = {"Content-Type": "application/json"}
                requests.post(url, json=data, headers=headers)
    except Exception:
        pass


def print_transaction(new_transaction):
    print("New transaction")
    print("FROM: {0}".format(new_transaction['from']))
    print("TO: {0}".format(new_transaction['to']))
    print("AMOUNT: {0}\n".format(new_transaction['amount']))


# IMPLEMENT
def valid_block(block):
    # check block data
    # check whether such block exists in the chain
    if block not in blockchain:
        return True
    else:
        return False


def update_transactions(blockchain, transactions):
    for block in blockchain:
        for transaction in block['transactions']:
            try:
                transactions.remove(transaction)
            except Exception:
                pass


def getvalue_blockchain():
    return blockchain._getvalue()


def getvalue_transactions():
    return transactions._getvalue()


def getvalue_peers():
    return peers._getvalue()


def add_peer(request):
    ip = request.args.get("ip")
    port = request.args.get("port")

    if ip is not None and port is not None:
        address_tuple = (ip, int(port))
        if address_tuple not in peers:
            print(f"[ADD PEER] New peer added {ip}:{port}")
            peers.append(address_tuple)


@node.route('/join', methods=['GET'])
def join():
    add_peer(request)
    return jsonify(blockchain=getvalue_blockchain(),
                   transactions=getvalue_transactions(),
                   peers=getvalue_peers()
                   )


@node.route('/block', methods=['POST'])
def post_block():
    block = request.get_json()
    if valid_block(block):
        print("[MINER] APPENDED NEW BLOCK TO THE BLOCKCHAIN")
        blockchain.append(block)
        print("[MINER] ADD NEW BLOCK TO THE DATABASE")
        blockchain_db.add_block(block)
        block['ttl'] -= 1
        update_transactions(blockchain, transactions)
        broadcast_to_peers('block', block, peers, block['ttl'])
        return "Block submission successful\n"
    else:
        return "Block submission unsuccessful\n"


@node.route('/peers', methods=['GET'])
def get_peers():
    """GET method returns miner node's peers
    """
    return json.dumps(getvalue_peers())


@node.route('/blocks', methods=['GET'])
def get_blocks():
    """GET method returns current blockchain on the miner node
    """
    return jsonify(blockchain_db.read_all_blocks(repr='json'))


@node.route('/transaction', methods=['GET', 'POST'])
def get_post_transaction():
    """POST method appends transaction to the transactions list
    """
    if request.method == 'POST':
        # On each new POST request, we extract the transaction data
        new_transaction = request.get_json()
        new_transaction['ttl'] -= 1

        if valid_transaction(new_transaction):
            # We create new dict object to store only needed info
            transaction = {
                'from': new_transaction['from'],
                'to': new_transaction['to'],
                'amount': new_transaction['amount'],
                'signature': new_transaction['signature'],
                'message': new_transaction['message'],
                'timestamp': str(datetime.utcnow())
            }

            transactions.append(transaction)
            print_transaction(transaction)
            broadcast_to_peers('transaction', new_transaction,
                               peers, new_transaction['ttl'])

            # Then we let the client know it worked out
            return "Transaction submission successful\n"
        else:
            return "Transaction submission failed. Check your signature or the receiver's public key\n"
    else:
        return json.dumps(getvalue_transactions())


@node.route('/new_public_key', methods=['POST'])
def store_new_pk():
    json = request.get_json()
    json['ttl'] -= 1
    public_key = json['public_key']
    public_keys_db.add_pk(public_key)
    broadcast_to_peers('new_public_key', json, peers, json['ttl'])
    return


def valid_transaction(new_transaction):
    sender_exists = public_keys_db.find_pk(new_transaction['from'])
    receiver_exists = public_keys_db.find_pk(new_transaction['to'])
    if not sender_exists or not receiver_exists:
        return False

    valid_signature = validate_signature(new_transaction['from'],
                                         new_transaction['signature'],
                                         new_transaction['message'])

    if not valid_signature:
        return False
    return True


def help():
    print("miner_ip:miner_port [peer_ip:peer_port]")


def cli():
    """Function to parse user input from command line

    Example use case (steps):
        1. python web_server.py 127.0.0.1:5001 27017
        2. python web_server.py 127.0.0.1:5002 27018 127.0.0.1:5001
        3. python web_server.py 127.0.0.1:5000 27019 127.0.0.1:5001 127.0.0.1:5002
    """
    if len(sys.argv) < 3:
        help()
        exit()
    miner_addr = sys.argv[1].split(":")
    ip = miner_addr[0]
    port = int(miner_addr[1])
    mongo_port = int(sys.argv[2])
    node_peers = [peer_addr.split(":") for peer_addr in sys.argv[3:]]
    node_peers = [(peer[0], int(peer[1])) for peer in node_peers]
    print(f"NODE PEERS: {node_peers}")
    return ip, port, mongo_port, node_peers


if __name__ == '__main__':
    # variable work determines number of leading zeroes needed to have hash(f"{last_proof}{proof}")
    work = 6  # better to put 6
    # change to auto generation
    miner_public_key, miner_private_key = generate_ECDSA_keys()

    ip, port, mongo_port, node_peers = cli()
    with Manager() as manager:
        blockchain = manager.list([])
        transactions = manager.list([])
        peers: List[Tuple[str, int]] = manager.list([])

        peers.extend(node_peers)
        # connect a database for storing the blockchain
        blockchain_db = BlockchainDB(IP=ip, PORT=mongo_port)
        # connect a database for storing public keys of the users
        public_keys_db = PublicKeysDB(IP=ip, PORT=mongo_port)
        miner = Miner(ip, port, work, miner_public_key)
        miner_process = Process(target=miner.run, args=(
            blockchain, transactions, peers))
        miner_process.start()

        web_server = Process(target=node.run(host=ip, port=port, debug=True), args=(
            blockchain, transactions, blockchain_db, public_keys_db))
        web_server.start()
