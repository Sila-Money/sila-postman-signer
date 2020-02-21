import sha3
import uuid

from eth_account import Account


def hash_message(msg):
    ''' Hashes a message string using the SHA3
        Keccak256 algorithm; returns the hash.
    '''
    k = sha3.keccak_256()
    k.update(msg)
    return k.hexdigest()


def sign_message(msg, private_key):
    ''' Accepts a message and a private key.
        Returns a signature string (with any "0x" prefix removed).
    '''
    signed_message = Account._sign_hash(hash_message(msg), private_key=private_key)
    sig_hx = signed_message.signature.hex()
    return str(sig_hx.replace("0x", ""))


def generate_private_key():
    ''' Generates a private key with a random UUID as entropy. '''
    test_account = Account.create(str(uuid.uuid4()))
    private_key = test_account.key.hex()
    return private_key.split('0x')[-1]


def get_private_key_address(private_key):
    ''' Gets the public address of a private key. '''
    return Account.from_key(private_key).address
