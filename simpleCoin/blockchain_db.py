from pymongo import MongoClient
from block import Block

client, db, collection = None, None, None


class BlockchainDB:
    def __init__(self, IP, PORT):
        global client, collection, db
        client = MongoClient(IP, PORT)
        db = client.blockchain
        collection = db.blockchain

    def add_block(self, block: Block):
        """
        block (Block): a block to add to the collection
        """
        collection.insert_one(block.exportjson())

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
        cursor = collection.find(dic)
        result = []
        for b in cursor:
            block = Block()
            result.append(block.importjson(b)
                          if repr == 'json' else block)
        return result

    def drop_all(self):
        """
        can be called at the beginning to clear the blocks collection if needed
        """
        collection.drop()
