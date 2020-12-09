from pymongo import MongoClient


class PublicKeysDB:
    def __init__(self, IP, PORT):
        """
        IP (str): IP for mongodb, e.g. 127.0.0.1
        PORT (int): PORT for mongodb, e.g. 27017
        """
        client = MongoClient(IP, PORT)
        db = client.blockchain
        self.collection = db.public_keys
        # uncomment the line below if you want to clean the collection with public keys in the beginning
        # self.drop_all()

    def add_pk(self, pk):
        """
        pk (str): a public key to add to the collection
        """
        self.collection.insert_one({'pk': pk})

    def find_pk(self, pk):
        """
        pk (str): a public key to find (check if exists)
        returns True if exists, otherwise False
        """
        result = self.collection.find_one({'pk': pk}, {'_id': 0})
        return not not result

    def drop_all(self):
        """
        drops all the public keys
        """
        self.collection.drop()
