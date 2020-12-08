from pymongo import MongoClient

client, db, collection = None, None, None

class PublicKeysDB:
    def __init__(self, IP, PORT):
        global client, collection, db
        client = MongoClient(IP, PORT)
        db = client.blockchain
        collection = db.public_keys


    def add_pk(self, pk):
        """
        pk (str): a public key to add to the collection
        """
        collection.insert_one({'pk': pk})


    def find_pk(self, pk):
        """
        pk (str): a public key to find (check if exists)
        returns True if exists, otherwise False
        """
        result = collection.find_one({'pk': pk})
        return not not result


    def drop_all(self):
        """
        drops all the public keys
        """
        collection.drop()
