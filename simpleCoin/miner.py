from block import Block
import requests
import hashlib
from datetime import datetime
import json


def create_genesis_block():
    """To create each block, it needs the hash of the previous one. First
    block has no previous, so it must be created manually (with index zero
    and arbitrary previous hash)"""
    return Block(index=0,
                 timestamp=str(datetime.utcnow()),
                 transactions=[],
                 proof=9,
                 previous_hash="0")


def node_url(ip, port):
    return f"http://{ip}:{port}"


class Miner:
    def __init__(self, ip, port, work, key):
        self.ip = ip
        self.port = port
        self.address = [self.ip, self.port]
        self.work = work
        self.key = key

    def update_peers(self, current_peers, other_miner_peers):
        new_peers = [
            peer for peer in other_miner_peers if peer not in current_peers and peer != self.address]
        return current_peers + new_peers

    def set_up(self, blockchain, transactions, peers):
        for peer in peers:
            payload = {
                "ip": self.ip,
                "port": self.port,
            }
            url = f'http://{peer[0]}:{peer[1]}/join'
            response = requests.get(url, params=payload).content
            if response is not None:
                data = json.loads(response)
                print(
                    f"[MINER] JOINING TO PEER'S({peer[0]}:{peer[1]}) NETWORK ")
                # print(f"[MINER] Blockchain: {data['blockchain']}")
                # print(f"[MINER] Transactions: {data['transactions']}")
                # print(f"[MINER] Peers: {self.update_peers(peers, data['peers'])}")
                return data['blockchain'], data['transactions'], self.update_peers(peers, data['peers'])
        return False

    def validate_blockchain(self, blockchain):
        """Validate the submitted chain. If hashes are not correct, return false
        block(str): json
        """
        # for i in range(len(blockchain)):
        #     # if block is genesis block
        #     if blockchain[i].index == 0:
        #         # genesis block should have previous_hash equal to "0"
        #         if blockchain[i].previous_hash != "0":
        #             return False
        #     elif blockchain[i].previous_hash != blockchain[i - 1].hash:
        #         return False
        return True

    def find_new_chains(self, peers):
        # print("[FINDING CHAINS] looking for other blockchains")

        # Get the blockchains of every other node
        other_chains = []
        for peer in peers:
            # Get their chains using a GET request
            peer_ip = peer[0]
            peer_port = peer[1]

            payload = {"ip": self.ip, "port": self.port}
            url = node_url(peer_ip, peer_port) + "/blocks"
            blockchain_json = requests.get(url=url, params=payload).content

            # Verify other node block is correct
            if self.validate_blockchain(blockchain_json):
                # Add it to our list
                other_chains.append(blockchain_json)
        return other_chains

    # NOT TESTED, but seems fine/joinain, peers):
    def consensus(self, blockchain, peers):
        # Get the blocks from other nodes
        other_chains = self.find_new_chains(peers)
        # If our chain isn't longest, then we store the longest chain
        longest_chain = blockchain
        for chain in other_chains:
            if len(longest_chain) < len(chain):
                longest_chain = chain
        # If the longest chain wasn't ours, then we set our chain to the longest
        if longest_chain == blockchain:
            # Keep searching for proof
            print("[NO CONSENSUS] NOT FOUND LONGER CHAIN")
            return False
        else:
            print("[CONSENSUS] FOUND NEW CHAIN")
            # Give up searching proof, update chain and start over again
            return longest_chain

    def valid_proof(self, last_proof, proof):
        """
            proof is valid if hash of last_proof + proof strings will have 5 leading zeroes
        """
        effort = f"{last_proof}{proof}".encode()
        effort_hash = hashlib.sha256(effort).hexdigest()
        return effort_hash[:self.work] == "0" * self.work

    # NOT TESTED IN CASE CONSENSUS = True; TODO: consensus search time depends from work
    def proof_of_work(self, blockchain, peers):
        last_block = blockchain[-1]
        last_proof = last_block['proof']

        # Creates a variable that we will use to find our next proof of work
        incrementer = last_proof + 1

        # Keep incrementing the incrementer until it's equal to a number divisible by 9
        # and the proof of work of the previous block in the chain
        while not self.valid_proof(last_proof, incrementer):
            # print("[GUESSING PROOF OF WORK]")
            incrementer += 1

            # Check if any node found the solution every 10 million iteration
            if incrementer % 10000000 == 0:
                print(f"[MINER] INCREMENT:{incrementer}")
                # If any other node got the proof, stop searching
                if new_blockchain := self.consensus(blockchain, peers):
                    return False, new_blockchain
        # Once that number is found, we can return it as a proof of our work
        return True, incrementer

    def reward_transaction(self):
        return {"from": "network",
                "to": self.key,
                "amount": 1}

    def jsonify_blockchain(self, blockchain):
        r = []
        for block in blockchain:
            print(block)
            r.append(block)
        return r

    # NOT TESTED IN CASE CONSENSUS = True
    def mine(self, blockchain, transactions, peers):
        if response := self.set_up(blockchain, transactions, peers):
            blockchain[:] = response[0]
            # print("\n\n\n***\n", type(response[0]), type([]))
            url = f'http://{self.ip}:{self.port}/blocks'
            requests.post(url, json=self.jsonify_blockchain(blockchain))
            transactions[:] = response[1]
            peers[:] = response[2]
        else:
            print("[MINER] CREATE GENESIS BLOCK")
            genesis_block = create_genesis_block()
            blockchain.append(genesis_block.exportjson())
            # send it to the server so that it's stored in the database
            genesis_block_json = genesis_block.exportjson()
            genesis_block_json['ttl'] = 2
            requests.post(url=node_url(self.ip, self.port) + "/block",
                          headers={"Content-Type": "application/json"},
                          json=genesis_block_json)

        print("[MINER] START MINING")
        while True:
            # function returns boolean variable and either proof or new blockchain
            response = self.proof_of_work(blockchain, peers)
            last_block = blockchain[-1]
            if not response[0]:
                blockchain[:] = response[1]
                url = f'http://{self.ip}:{self.port}/block'
                requests.post(url, json=self.jsonify_blockchain(blockchain))

                print("[MINER] SOMEONE FOUND PROOF")
            elif self.valid_proof(last_block['proof'], response[1]):
                proof = response[1]
                print("[MINER] FOUND PROOF")

                # Once we find a valid proof of work, we know we can mine a block so
                # ...we reward the miner by adding a transaction
                if len(transactions) == 0:
                    continue
                print("[MINER] MAKING BLOCK")
                # Then we add the mining reward
                transactions.append(self.reward_transaction())
                # Now create the new block
                mined_block = Block(index=last_block['index'] + 1,
                                    timestamp=str(datetime.utcnow()),
                                    transactions=list(transactions),
                                    proof=proof,
                                    previous_hash=last_block['hash'])

                # Empty transaction list
                transactions[:] = []

                block_json = mined_block.exportjson()
                block_json['ttl'] = 2
                requests.post(url=node_url(self.ip, self.port) + "/block",
                              headers={"Content-Type": "application/json"},
                              json=block_json)
