from common.identification import generate_ECDSA_keys
from pprint import pprint
import time
import hashlib
import requests
import json

from block import Block


MINER_ADDRESS = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"


def create_genesis_block():
    """To create each block, it needs the hash of the previous one. First
    block has no previous, so it must be created manually (with index zero
     and arbitrary previous hash)"""
    return Block(0, time.time(), {
        "proof-of-work": 9,
        "transactions": None},
        "0")


def node_url(ip, port):
    return f"http://{ip}:{port}"


class Miner:
    def __init__(self, ip_address, port, peers):
        print(f"[INITIALIZING] Miner initialized on {ip_address}:{port}")
        print(f"[KNOWN PEERS] {peers}\n")

        self.url = f"http://{ip_address}:{port}"
        self.ip = ip_address
        self.port = port

        self.peers = peers
        self.public_key, self.private_key = generate_ECDSA_keys()

        self.blockchain = []
        if consensus := self.consensus():
            print(f"[FOUND CHAIN] Found longer chain from peers")
            self.blockchain = consensus
            print("[UPDATED BLOCKCHAIN]")
            pprint(self.blockchain)
        else:
            if len(self.peers) == 0:
                print("[INITIALIZING GENESIS BLOCK] Do not have peers")
            else:
                print("[INITIALIZING GENESIS BLOCK] Could not find longer chain from peers")
            self.blockchain = [create_genesis_block()]

        """ Stores the transactions that this node has in a list.
        If the node you sent the transaction adds a block
        it will get accepted, but there is a chance it gets
        discarded and your transaction goes back as if it was never
        processed"""
        self.pending_transactions = []

    def validate_blockchain(self, blockchain):
        """Validate the submitted chain. If hashes are not correct, return false
        block(str): json
        """
        for i in range(len(blockchain) - 1):
            # if block is genesis block
            if blockchain[i].index == 0:
                # genesis block should have previous_hash equal to "0"
                if blockchain[i].previous_hash != "0":
                    return False
            else:
                if blockchain[i].previous_hash != blockchain[i - 1].hash:
                    return False
        return True

    def find_new_chains(self):
        # Get the blockchains of every other node
        other_chains = []
        for peer in self.peers:
            # Get their chains using a GET request
            peer_ip = peer[0]
            peer_port = peer[1]

            found_blockchain = []

            payload = {"ip": self.ip, "port": self.port}
            url = node_url(peer_ip, peer_port) + "/blocks"
            blockchain_json = requests.get(url=url, params=payload).content

            if blockchain_json is not None:
                blockchain_json = json.loads(blockchain_json)
                for block_json in blockchain_json:
                    temp = Block()
                    temp.importjson(block_json)

                    # TODO: add validate(temp), store previous proof and current inside blocks
                    found_blockchain.append(temp)

            # Verify other node block is correct
            validated = self.validate_blockchain(found_blockchain)
            if validated:
                # Add it to our list
                other_chains.append(found_blockchain)
        return other_chains

    def consensus(self):
        if self.peers != []:
            # Get the blocks from other nodes
            other_chains = self.find_new_chains()
            # If our chain isn't longest, then we store the longest chain
            longest_chain = self.blockchain
            for chain in other_chains:
                if len(longest_chain) < len(chain):
                    longest_chain = chain
            # If the longest chain wasn't ours, then we set our chain to the longest
            if longest_chain == self.blockchain:
                # Keep searching for proof
                return False
            else:
                # Give up searching proof, update chain and start over again
                return longest_chain
        else:
            return False

    def valid_proof(self, last_proof, proof):
        """
            proof is valid if hash of last_proof + proof strings will have 5 leading zeroes
        """
        work = 6
        effort = f"{last_proof}{proof}".encode()
        effort_hash = hashlib.sha256(effort).hexdigest()
        return effort_hash[:work] == "0" * work

    def proof_of_work(self, last_proof):
        # Creates a variable that we will use to find our next proof of work
        incrementer = last_proof + 1
        # Keep incrementing the incrementer until it's equal to a number divisible by 9
        # and the proof of work of the previous block in the chain
        start_time = int(time.time())

        while not self.valid_proof(last_proof, incrementer):
            incrementer += 1
            # Check if any node found the solution every 60 seconds
            if (int(time.time() - start_time)) % 60 == 0:
                # If any other node got the proof, stop searching
                new_blockchain = self.consensus()
                if new_blockchain:
                    # (False: another node got proof first, new blockchain)
                    return False, new_blockchain
            time.sleep(1)
        # Once that number is found, we can return it as a proof of our work
        return incrementer, self.blockchain

    def mine(self, a):
        a.send(self.blockchain)
        requests.get(url=self.url + '/blocks', params={'update': MINER_ADDRESS})
        while True:
            print("[MINER] Mining New Block")
            last_block = self.blockchain[-1]
            last_proof = last_block.data['proof-of-work']

            proof = self.proof_of_work(last_proof)
            if not proof[0]:
                print("[SOMEONE FOUND PROOF]")
                # Update blockchain and save it to file
                self.blockchain = proof[1]
                a.send(self.blockchain)
                pprint(self.blockchain)
                requests.get(url=self.url + '/blocks', params={'update': MINER_ADDRESS})
                continue
            else:
                print("[FOUND PROOF]")

                # Once we find a valid proof of work, we know we can mine a block so
                # ...we reward the miner by adding a transaction
                # First we load all pending transactions sent to the node server
                self.pending_transactions = requests.get(url=self.url + '/txion',
                                                         params={'update': MINER_ADDRESS}).content
                print("Transactions:", self.pending_transactions)
                self.pending_transactions = json.loads(self.pending_transactions)

                if len(self.pending_transactions) == 0:
                    continue

                # Then we add the mining reward
                self.pending_transactions.append({
                    "from": "network",
                    "to": MINER_ADDRESS,
                    "amount": 1})
                # Now we can gather the data needed to create the new block
                new_block_data = {
                    "proof-of-work": proof[0],
                    "transactions": list(self.pending_transactions)
                }
                new_block_index = last_block.index + 1
                new_block_timestamp = time.time()
                last_block_hash = last_block.hash
                # Empty transaction list
                self.pending_transactions = []
                # Now create the new block
                mined_block = Block(new_block_index, new_block_timestamp, new_block_data, last_block_hash)
                self.blockchain.append(mined_block)
                # Let the client know this node mined a block
                print(json.dumps({"index": new_block_index,
                                  "timestamp": str(new_block_timestamp),
                                  "data": new_block_data,
                                  "hash": last_block_hash
                                  }) + "\n")
                a.send(self.blockchain)
                payload = {'update': MINER_ADDRESS, 'peers': self.peers}
                requests.get(url=self.url + '/blocks', params=payload)
                pprint(self.blockchain)
