import math

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


class sha256:
    def __init__(self, message: bytes=None):
        self.digest = hashes.Hash(hashes.SHA256(), backend=default_backend())

        if message is not None:
            self.digest.update(message)


    def update(self, message: bytes):
        self.digest.update(message)
        return self

    
    def digest(self):
        digest = self.digest.finalize()
        return digest


    def hexdigest(self):
        digest = self.digest.finalize()
        hexdigest = digest.hex()
        return hexdigest


def generate_private_key() -> str:
    # private key
    _private_key = ec.generate_private_key(
        ec.SECP256K1(),
        default_backend(),
    )

    private_key_int = _private_key.private_numbers().private_value
    byte_length = int(math.ceil(private_key_int.bit_length() / 8))
    private_key_bytes = private_key_int.to_bytes(byte_length, byteorder='big')
    private_key = private_key_bytes.hex()
    return private_key


def get_public_key(private_key: str):
    # private key
    private_key_bytes = bytes.fromhex(private_key)
    private_key_int = int.from_bytes(private_key_bytes, byteorder='big')
    
    _private_key = ec.derive_private_key(
        private_key_int,
        ec.SECP256K1(),
        default_backend(),
    )

    # public key
    _public_key = _private_key.public_key()
    public_key_bytes = _public_key.public_numbers().encode_point()
    public_key = public_key_bytes.hex()
    return public_key


def get_address(public_key: str) -> str:
    # public key
    public_key_bytes = bytes.fromhex(public_key)
    
    # address
    address = sha256(public_key_bytes).hexdigest()
    address = f'J{address}'
    return address


def generate_private_public_address_key() -> (str, str):
    # private key
    _private_key = ec.generate_private_key(
        ec.SECP256K1(),
        default_backend(),
    )

    private_key_int = _private_key.private_numbers().private_value
    byte_length = int(math.ceil(private_key_int.bit_length() / 8))
    private_key_bytes = private_key_int.to_bytes(byte_length, byteorder='big')
    private_key = private_key_bytes.hex()

    # public key
    _public_key = _private_key.public_key()
    public_key_bytes = _public_key.public_numbers().encode_point()
    public_key = public_key_bytes.hex()

    # address
    address = sha256(public_key_bytes).hexdigest()
    address = f'J{address}'

    return private_key, public_key, address


def sign_message(private_key: str, message: str) -> str:
    # private key
    private_key_bytes = bytes.fromhex(private_key)
    private_key_int = int.from_bytes(private_key_bytes, byteorder='big')
    
    _private_key = ec.derive_private_key(
        private_key_int,
        ec.SECP256K1(),
        default_backend(),
    )

    # sign
    message_bytes = message.encode()

    signature_bytes = _private_key.sign(
        message_bytes,
        ec.ECDSA(hashes.SHA256()),
    )

    signature = signature_bytes.hex()
    return signature


def verify_message(public_key: str, signature: str, message: str) -> bool:
    # public key
    public_key_bytes = bytes.fromhex(public_key)
    signature_bytes = bytes.fromhex(signature)
    
    _public_key_numbers = ec.EllipticCurvePublicNumbers.from_encoded_point(
        ec.SECP256K1(),
        public_key_bytes,
    )

    _public_key = _public_key_numbers.public_key(default_backend())

    # verify
    message_bytes = message.encode()

    try:
        _public_key.verify(
            signature_bytes,
            message_bytes,
            ec.ECDSA(hashes.SHA256()),
        )

        verified = True
    except Exception as e:
        verified = False
    
    return verified


if __name__ == '__main__':
    sk0 = generate_private_key()
    pk0 = get_public_key(sk0)
    addr0 = get_address(pk0)
    print(f'sk0: {sk0!r}')
    print(f'pk0: {pk0!r}')
    print(f'addr0: {addr0!r}')

    sk1, pk1, addr1 = generate_private_public_address_key()
    print(f'sk1: {sk1!r}')
    print(f'pk1: {pk1!r}')
    print(f'addr1: {addr1!r}')

    sig0 = sign_message(sk0, '{}')
    verif0 = verify_message(pk0, sig0, '{}')
    print(f'verif0: {verif0!r}')

    sig1 = sign_message(sk1, '[]')
    verif1 = verify_message(pk1, sig1, '[]')
    print(f'verif1: {verif1!r}')
