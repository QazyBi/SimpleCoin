from flask import Flask, request
from multiprocessing import Process, Pipe
import json
import requests
import sys

from common.identification import validate_signature
from block import Block
from miner import Miner


def welcome_msg():
    print("""       =========================================\n
        SIMPLE COIN v1.0.0 - BLOCKCHAIN SYSTEM\n
       =========================================\n\n
        You can find more help at: https://github.com/cosme12/SimpleCoin\n
        Make sure you are using the latest version or you may end in
        a parallel chain.\n\n\n""")


node = Flask(__name__)

""" Stores the transactions that this node has in a list.
If the node you sent the transaction adds a block
it will get accepted, but there is a chance it gets
discarded and your transaction goes back as if it was never
processed"""
NODE_PENDING_TRANSACTIONS = []
BLOCKCHAIN = []
NEW_PEERS = []
MINER_ADDRESS = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"


@node.route('/new_peers', methods=['GET'])
def get_new_peers():
    global NEW_PEERS
    new_peers_json = json.dumps(NEW_PEERS)
    NEW_PEERS = []
    return new_peers_json


@node.route('/blocks', methods=['GET'])
def get_blocks():
    # Load current blockchain. Only you should update your blockchain
    if request.args.get("update") == MINER_ADDRESS:
        global BLOCKCHAIN
        BLOCKCHAIN = b.recv()
    else:
        ip = request.args.get("ip")
        port = request.args.get("port")
        address_tuple = (ip, int(port))
        if address_tuple not in NEW_PEERS:
            print(f"[ADD PEER] New peer added {ip}:{port}")
            NEW_PEERS.append(address_tuple)

    chain_to_send = BLOCKCHAIN
    # Converts our blocks into dictionaries so we can send them as json objects later
    chain_to_send_json = []
    for block in chain_to_send:
        chain_to_send_json.append(block.exportjson())

    # Send our chain to whomever requested it
    chain_to_send = json.dumps(chain_to_send_json)
    return chain_to_send


@node.route('/txion', methods=['GET', 'POST'])
def transaction():
    """Each transaction sent to this node gets validated and submitted.
    Then it waits to be added to the blockchain. Transactions only move
    coins, they don't create it.
    """
    if request.method == 'POST':
        # On each new POST request, we extract the transaction data
        new_txion = request.get_json()
        # Then we add the transaction to our list
        if validate_signature(new_txion['from'], new_txion['signature'], new_txion['message']):
            NODE_PENDING_TRANSACTIONS.append(new_txion)
            # Because the transaction was successfully
            # submitted, we log it to our console
            print("New transaction")
            print("FROM: {0}".format(new_txion['from']))
            print("TO: {0}".format(new_txion['to']))
            print("AMOUNT: {0}\n".format(new_txion['amount']))

            # Push to all other available nodes
            peers = request.args.get("peers")
            if peers is not None:
                for peer in peers:
                    if peer[0] != request.remote_addr:
                        try:
                            headers = {"Content-Type": "application/json"}
                            requests.post(peer[0] + ":" + peer[1] + "/txion", json=new_txion, headers=headers)
                        except Exception:
                            print(Exception)
            return "Transaction submission successful\n"
            # Then we let the client know it worked out
            return "Transaction submission successful\n"
        else:
            return "Transaction submission failed. Wrong signature\n"
    # Send pending transactions to the mining process
    elif request.method == 'GET' and request.args.get("update") == MINER_ADDRESS:
        pending = json.dumps(NODE_PENDING_TRANSACTIONS)
        # Empty transaction list
        NODE_PENDING_TRANSACTIONS[:] = []
        return pending


@node.route('/block', methods=['POST'])
def get_block():
    global BLOCKCHAIN
    ip = request.remote_addr
    new_block_json = request.get_json()
    new_block = Block()
    print("trying to receieve a block from", ip)
    new_block.importjson(new_block_json)
    # validation = validate(new_block)
    if new_block.previous_hash == BLOCKCHAIN[len(BLOCKCHAIN) - 1].previous_hash:  # validation and
        ip = request.args.get("ip")
        port = request.args.get("port")
        address_tuple = (ip, int(port))
        if address_tuple not in NEW_PEERS:
            print(f"[ADD PEER] New peer added {ip}:{port}")
            NEW_PEERS.append(address_tuple)

        BLOCKCHAIN.append(new_block)
    else:
        # print("val", validation, "nbph", new_block.previous_hash,
        # "aph", BLOCKCHAIN[len(BLOCKCHAIN) - 1].previous_hash)
        return "500"

    return "200"


def help():
    print("miner_ip:miner_port [peer_ip:peer_port]")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        help()
        exit()
    miner_addr = sys.argv[1].split(":")
    ip = miner_addr[0]
    port = int(miner_addr[1])

    peers = [peer_addr.split(":") for peer_addr in sys.argv[2:]]
    peers = [(peer[0], int(peer[1])) for peer in peers]

    miner = Miner(ip, port, peers)

    # Start mining
    a, b = Pipe()
    p1 = Process(target=miner.mine, args=(a,))
    p1.start()
    # Start server to receive transactions
    p2 = Process(target=node.run(host=ip, port=port), args=(b,))
    p2.start()
