import hashlib
from ast import literal_eval


class Block:
    def __init__(self, index=-1, timestamp=-1, proof=-1, transactions=-1, previous_hash=-1):
        """Returns a new Block object. Each block is "chained" to its previous
        by calling its unique hash.

        Args:
            index (int): Block number.
            timestamp (int): Block creation timestamp.
            proof (str): Proof of Work.
            transactions (list of dictionaries): Transactions contained in this block.
            previous_hash (str): String representing previous block unique hash.

        Attrib:
            index (int): Block number.
            timestamp (int): Block creation timestamp.
            proof (str): Proof of Work.
            transactions (list of dictionaries): Transactions contained in this block.
            previous_hash(str): String representing previous block unique hash.
            hash(str): Current block unique hash.

        """
        self.index = index
        self.timestamp = timestamp
        self.proof = proof
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def __str__(self):
        return f"Index:{self.index} Timestamp:{self.timestamp} Pow:{self.proof}\
                Transactions:{self.transactions} Previous_hash:{self.previous_hash} Hash:{self.hash}"

    def __repr__(self):
        return f"Index:{self.index} Timestamp:{self.timestamp} Pow:{self.proof}\
                Transactions:{self.transactions} Previous_hash:{self.previous_hash} Hash:{self.hash}"

    def hash_block(self):
        """Creates the unique hash for the block. It uses sha256."""
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.timestamp) + str(self.proof) + str(self.transactions) + str(self.previous_hash)).encode('utf-8'))
        return sha.hexdigest()

    def exportjson(self):
        return {
            "index": str(self.index),
            "timestamp": str(self.timestamp),
            "proof": str(self.proof),
            "transactions": str(self.transactions),
            "previous": str(self.previous_hash),
            "hash": str(self.hash)
        }

    def importjson(self, json):
        self.index = int(json['index'])
        self.timestamp = float(json['timestamp'])
        self.proof = str(json['proof'])
        self.transactions = json['transactions']
        self.previous_hash = str(json['previous'])
        self.hash = self.hash_block()
