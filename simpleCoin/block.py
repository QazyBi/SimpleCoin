from hashlib import sha256


class Block:
    def __init__(self, index=-1, timestamp=-1, transactions=-1, proof=-1, previous_hash=-1):
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
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def __repr__(self):
        return f"Index:{self.index} Timestamp:{self.timestamp} \nPow:{self.proof}\
                \nTransactions:{self.transactions} \nPrevious_hash:{self.previous_hash} \nHash:{self.hash}\n"

    def hash_block(self):
        """Creates the unique hash for the block. It uses sha256."""
        sha = sha256()
        string = (str(self.index) + str(self.timestamp)
                  + str(self.transactions) + str(self.proof)
                  + str(self.previous_hash))
        sha.update(string.encode('utf-8'))
        return sha.hexdigest()

    def exportjson(self):
        return {
            "index": int(self.index),
            "timestamp": str(self.timestamp),
            "proof": int(self.proof),
            "transactions": self.transactions,
            "previous": str(self.previous_hash),
            "hash": str(self.hash)
        }

    def importjson(self, json):
        self.index = int(json['index'])
        self.timestamp = json['timestamp']
        self.proof = int(json['proof'])
        self.transactions = json['transactions']
        self.previous_hash = str(json['previous'])
        self.hash = str(json['hash'])
