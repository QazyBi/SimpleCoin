from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.blockchain


def add_transaction(transaction):
    """
    transaction (Transaction): a transaction to add to the collection
    """
    db.transactions.insert_one(transaction.dic_form)


def read_all_transations(repr=None):
    """
    repr (json or None): how to represent the result. if None the result will be a list of Transaction class objects,
                                                      if 'json' the result will be a list of dictionaries
    """
    return find_transaction(repr=repr)


def find_transaction(from_pk=None, to_pk=None, amount=None, repr=None):
    """
    from_pk (str): public key of a sender
    to_pk (str): public key of a receiver
    amount (str): amount to send
    repr (json or None): how to represent the result. if None the result will be a list of Transaction class objects,
                                                      if 'json' the result will be a list of dictionaries
    """
    dic = {}
    if from_pk:
        dic['from'] = from_pk
    if to_pk:
        dic['to'] = to_pk
    if amount:
        dic['amount'] = amount
    cursor = db.transactions.find(dic)
    result = []
    for tr in cursor:
        tr_obj = Transaction(tr['from'], tr['to'],
                             tr['amount'], tr['timestamp'])
        result.append(tr_obj.dic_form if repr == 'json' else tr_obj)
    return result


def drop_all():
    """
    can be called at the beginning to clear the transactions collection if needed
    """
    db.transactions.drop()


class Transaction:
    def __init__(self, from_pk, to_pk, amount, timestamp):
        """
        Attributes:
        from_pk (str): public key of a sender
        to_pk (str): public key of a receiver
        amount (str): amount to send
        timestamp: UTC time
        """
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