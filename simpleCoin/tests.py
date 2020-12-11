from common.identification import sign_ECDSA_msg
from miner import Miner, create_genesis_block
from block import Block
import requests
import json
import time
import pprint


def test_post_transactions(addr_from, addr_to, private_key, amount):
    signature, message = sign_ECDSA_msg(private_key)
    payload = {"from": addr_from,
               "to": addr_to,
               "amount": amount,
               "signature": signature.decode(),
               "message": message,
               "ttl": 2,  # time to live - how many times this message will be readressed
               }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url + "/transaction", json=payload, headers=headers).content
    print(response)


def test_get_transactions():
    response = requests.get(url + "/transaction").content
    print(json.loads(response))


def test_get_blocks():
    response = requests.get(url + "/blocks").content
    print(json.loads(response))


def test_get_join():
    response = requests.get(url + "/join").content
    print(pprint.pprint(json.loads(response)))


def test_validate_blockchain_valid_chain():
    m = Miner(ip, port, work, miner_key)
    blockchain = []
    b0 = create_genesis_block()
    blockchain.append(b0)

    b1 = Block(index=1,
               timestamp=time.time(),
               transactions=[],
               proof=24013649,
               previous_hash=b0.hash)
    blockchain.append(b1)

    assert m.validate_blockchain(blockchain)


def test_validate_blockchain_invalid_chain():
    m = Miner(ip, port, work, miner_key)
    blockchain = []
    b0 = create_genesis_block()
    blockchain.append(b0)

    b1 = Block(index=1,
               timestamp=time.time(),
               transactions=[],
               proof=24013649,
               previous_hash="1719d0824d66e0286eff77ff3e883a3f6b9eb746c96f16a0b331464794e29791")
    blockchain.append(b1)

    assert m.validate_blockchain(blockchain) is False


def test_find_new_chains():
    peers = [(ip, port - 1), (ip, port)]

    m = Miner(ip, port, work, miner_key)

    for other_chain in m.find_new_chains(peers):
        other_chain_json = [block.exportjson() for block in other_chain]
        pprint.pprint(other_chain_json)


ip = "127.0.0.1"
port = 5000
work = 6
miner_key = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"
url = f"http://{ip}:{port}"

# PUT EXISTING KEYS!
private_key_q = ""
public_key_q = ""

public_key_a = ""
private_key_a = ""

test_validate_blockchain_valid_chain()
test_validate_blockchain_invalid_chain()

# test_find_new_chains()

# test_get_blocks()
# test_get_join()
# test_post_transactions(public_key_q, public_key_w, private_key_q, 123456)
# test_get_transactions()
