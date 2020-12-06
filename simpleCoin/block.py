from ast import literal_eval
import hashlib


class Block:
    def __init__(self, index=-1, timestamp=-1, data=-1, proof=-1, previous_hash=-1):
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
        self.proof = proof
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def __str__(self):
        return f"Index:{self.index}"

    def __repr__(self):
        return f"Index:{self.index}"

    def hash_block(self):
        """Creates the unique hash for the block. It uses sha256."""
        sha = hashlib.sha256()
        string = (str(self.index) + str(self.timestamp)
                  + str(self.data) + str(self.proof)
                  + str(self.previous_hash))
        sha.update(string.encode('utf-8'))
        return sha.hexdigest()

    def exportjson(self):
        return {
            "index": int(self.index),
            "timestamp": str(self.timestamp),
            "proof": int(self.proof),
            "data": self.data,
            "previous": str(self.previous_hash),
            "hash": str(self.hash)
        }

    def importjson(self, json):
        self.index = int(json['index'])
        self.timestamp = float(json['timestamp'])
        self.proof = int(json['proof'])
        self.data = json['data']
        self.previous_hash = str(json['previous'])
        self.hash = self.hash_block()
