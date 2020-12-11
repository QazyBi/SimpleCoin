from pymongo import MongoClient
from block import Block

GENESIS = 0
class BlockchainDB:
    def __init__(self, IP, PORT):
        """
        IP (str): IP for mongodb, e.g. 127.0.0.1
        PORT (int): PORT for mongodb, e.g. 27017
        """
        client = MongoClient(IP, PORT)
        db = client.blockchain
        self.collection = db.blockchain
        # drop the previously stored blockchain
        self.drop_all()

    def add_block(self, block):
        """
        block (Block): a block to add to the collection
        """
        global GENESIS
        if block['index'] == 0 and GENESIS > 0:
            return
        elif block['index'] == 0:
            GENESIS += 1
        return self.collection.insert_one(block)

    def update_blockchain(self, blockchain):
        self.drop_all()
        if not blockchain:
            return
        for block in blockchain:
            self.add_block(block)

    def read_all_blocks(self, repr=None):
        """
        repr (json or None): how to represent the result. if None the result will be a list of Transaction class objects,
                                                        if 'json' the result will be a list of dictionaries
        """
        return self.find_block(repr=repr)

    def find_block(self, index=None, timestamp=None, transactions=None, proof=None, previous_hash=None, hash_block=None, repr=None):
        """
        from_pk (str): public key of a sender
        to_pk (str): public key of a receiver
        amount (str): amount to send
        repr (json or None): how to represent the result. if None the result will be a list of Block class objects,
                                                        if 'json' the result will be a list of dictionaries
        """
        dic = {}
        if index:
            dic['index'] = index
        if timestamp:
            dic['timestamp'] = timestamp
        if transactions:
            dic['transactions'] = transactions
        if proof:
            dic['proof'] = proof
        if previous_hash:
            dic['previous_hash'] = previous_hash
        if hash_block:
            dic['hash_block'] = hash_block
        cursor = self.collection.find(dic, {'_id': 0})
        result = []
        for b in cursor:
            block = Block()
            block.importjson(b)
            result.append(block.exportjson() if repr == 'json' else block)
        return result

    def drop_all(self):
        """
        can be called at the beginning to clear the blocks collection if needed
        """
        self.collection.drop()
