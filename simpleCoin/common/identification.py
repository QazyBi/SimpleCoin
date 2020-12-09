import time
import base64
import ecdsa


def generate_ECDSA_keys(filename=None):
    """This function takes care of creating your private and public (your address) keys.
    It's very important you don't lose any of them or those wallets will be lost
    forever. If someone else get access to your private key, you risk losing your coins.

    private_key: str
    public_ley: base64 (to make it shorter)
    """
    sk = ecdsa.SigningKey.generate(
        curve=ecdsa.SECP256k1)  # this is your sign (private key)
    private_key = sk.to_string().hex()  # convert your private key to hex
    vk = sk.get_verifying_key()  # this is your verification key (public key)
    public_key = vk.to_string().hex()
    # we are going to encode the public key to make it shorter
    public_key = base64.b64encode(bytes.fromhex(public_key))

    if filename == None:
        filename = input("Write the name of your new address: ") + ".txt"
    with open(filename, "w") as f:
        f.write("Private key: {0}\nWallet address / Public key: {1}".format(private_key, public_key.decode()))
    print("Your new address and private key are now in the file {0}".format(filename))

    return public_key, private_key


def sign_ECDSA_msg(private_key):
    """Sign the message to be sent
    private_key: must be hex

    return
    signature: base64 (to make it shorter)
    message: str
    """
    # Get timestamp, round it, make it into a string and encode it to bytes
    message = str(round(time.time()))
    bmessage = message.encode()
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    signature = base64.b64encode(sk.sign(bmessage))
    return signature, message


def validate_signature(public_key, signature, message):
    """Verifies if the signature is correct. This is used to prove
    it's you (and not someone else) trying to do a transaction with your
    address. Called when a user tries to submit a new transaction.
    """
    public_key = (base64.b64decode(public_key)).hex()
    signature = base64.b64decode(signature)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
    # Try changing into an if/else statement as except is too broad.
    try:
        return vk.verify(signature, message.encode())
    except Exception:
        return False
