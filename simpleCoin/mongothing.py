from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.blockchain


def add_transaction(transaction):
    db.transactions.insert_one(transaction.dic_form)


def read_all_transations():
    return find_transaction()


def find_transaction(from_pk=None, to_pk=None, amount=None):
    dic = {}
    if from_pk:
        dic['from'] = from_pk
    if to_pk:
        dic['to'] = to_pk
    if amount:
        dic['amount'] = amount
    cursor = db.transactions.find(dic)
    result = []
    for transaction in cursor:
        result.append(transaction)
    return result


def drop_all():
    db.transactions.drop()


class Transaction:
    def __init__(self, from_pk, to_pk, amount, timestamp):
        self.from_pk = from_pk
        self.to_pk = to_pk
        self.amount = amount
        self.timestamp = timestamp
        self.dic_form = self.to_dict()

    def to_dict(self):
        dic = {'from': self.from_pk,
               'to': self.to_pk,
               'amount': self.amount,
               'timestamp': self.timestamp}
        return dic
