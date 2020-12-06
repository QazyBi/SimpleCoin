from multiprocessing import Manager, Process
from flask import Flask, request, jsonify
from typing import List, Tuple
import requests
import sys
import json

from common.identification import validate_signature
from miner import Miner


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
        for transaction in block['data']['transactions']:
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


# NOT TESTED
@node.route('/block', methods=['POST'])
def post_block():
    block = request.get_json()
    if valid_block(block):
        print("[MINER] APPENDED NEW BLOCK TO THE BLOCKCHAIN")
        blockchain.append(block)
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
    return json.dumps(getvalue_blockchain())


@node.route('/transaction', methods=['GET', 'POST'])
def get_post_transaction():
    """POST method appends transaction to the transactions list
    """
    if request.method == 'POST':
        # On each new POST request, we extract the transaction data
        new_transaction = request.get_json()
        new_transaction['ttl'] -= 1
        # Then we add the transaction to our list
        valid_signature = validate_signature(new_transaction['from'],
                                             new_transaction['signature'],
                                             new_transaction['message'])
        if valid_signature:
            # We create new dict object to store only needed info
            transaction = {
                'from': new_transaction['from'],
                'to': new_transaction['to'],
                'amount': new_transaction['amount'],
                'signature': new_transaction['signature'],
                'message': new_transaction['message'],
                # 'timestamp': time.time(),
            }

            transactions.append(transaction)
            print_transaction(transaction)
            broadcast_to_peers('transaction', new_transaction, peers, new_transaction['ttl'])

            # Then we let the client know it worked out
            return "Transaction submission successful\n"
        else:
            return "Transaction submission failed. Wrong signature\n"
    else:
        return json.dumps(getvalue_transactions())


def help():
    print("miner_ip:miner_port [peer_ip:peer_port]")


def cli():
    """Function to parse user input from command line

    Example use cases:
        python web_server.py 127.0.0.1:5000
        python web_server.py 127.0.0.1:5000 127.0.0.1:5001 127.0.0.1:5002
    """
    if len(sys.argv) < 2:
        help()
        exit()
    miner_addr = sys.argv[1].split(":")
    ip = miner_addr[0]
    port = int(miner_addr[1])
    node_peers = [peer_addr.split(":") for peer_addr in sys.argv[2:]]
    node_peers = [(peer[0], int(peer[1])) for peer in node_peers]
    print(f"NODE PEERS: {node_peers}")
    return ip, port, node_peers


if __name__ == '__main__':
    # variable work determines number of leading zeroes needed to have hash(f"{last_proof}{proof}")
    work = 6  # better to put 6
    # change to auto generation
    miner_key = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"

    ip, port, node_peers = cli()
    with Manager() as manager:
        blockchain = manager.list([])
        transactions = manager.list([])
        peers: List[Tuple[str, int]] = manager.list([])

        peers.extend(node_peers)

        miner = Miner(ip, port, work, miner_key)
        miner_process = Process(target=miner.run, args=(blockchain, transactions, peers))
        miner_process.start()

        web_server = Process(target=node.run(host=ip, port=port), args=(blockchain, transactions))
        web_server.start()
