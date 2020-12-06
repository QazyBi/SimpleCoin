from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.blockchain


def add_pk(pk):
    """
    pk (str): a public key to add to the collection
    """
    db.pks.insert_one({'pk': pk})


def find_pk(pk):
    """
    pk (str): a public key to find (check if exists)
    returns True if exists, otherwise False
    """
    result = db.pks.find_one({'pk': pk})
    return not not result


def drop_all():
    """
    drops all the public keys
    """
    db.pks.drop()
