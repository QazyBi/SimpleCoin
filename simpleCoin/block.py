import hashlib
from ast import literal_eval


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        """Returns a new Block object. Each block is "chained" to its previous
        by calling its unique hash.

        Args:
            index (int): Block number.
            timestamp (int): Block creation timestamp.
            data (str): Data to be sent.
            previous_hash(str): String representing previous block unique hash.

        Attrib:
            index (int): Block number.
            timestamp (int): Block creation timestamp.
            data (str): Data to be sent.
            previous_hash(str): String representing previous block unique hash.
            hash(str): Current block unique hash.

        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        """Creates the unique hash for the block. It uses sha256."""
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode('utf-8'))
        return sha.hexdigest()

    def exportjson(self):
        return {
            "index": str(self.index),
            "timestamp": str(self.timestamp),
            "pow": str(self.proof_of_work),
            "effort": str(self.effort),
            "data": str(self.data),
            "previous": str(self.previous_hash),
            "hash": str(self.hash)
        }

    def importjson(self, json):
        self.index = int(json['index'])
        self.timestamp = float(json['timestamp'])
        self.proof_of_work = str(json['pow'])
        self.effort = str(json['effort'])
        self.data = literal_eval(json['data'])
        self.previous_hash = str(json['previous'])
        self.hash = self.hash_block()
