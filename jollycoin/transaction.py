from typing import TypeVar, Dict
from decimal import Decimal
from datetime import datetime
from collections import OrderedDict
import json
import random

from . import crypto


# we require it defined like this because of python3.6
# it will be overwritten once Transaction class is defined
Transaction = TypeVar('Transaction')


class TransactionError(Exception):
    pass


class Transaction:
    def __init__(self: Transaction,
                 version: str,
                 id_: str,
                 time_: str,
                 sender_address: str,
                 recipient_address: str,
                 sender_public_key: str,
                 amount: int,
                 fee: int,
                 signature: str,
                 hash_: str,
                 check: bool=True):
        assert version == '1.0'
        self.version = version
        self.id = id_
        self.time = time_
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.sender_public_key = sender_public_key
        self.amount = None if amount is None else int(amount)
        self.fee = None if fee is None else int(fee)
        self.signature = signature
        self.hash = hash_

        if check:
            if not self.verify_hash():
                raise TransactionError('invalid hash')

            if not self.verify_signature():
                raise TransactionError('invalid signature')


    @classmethod
    def gen_random_id(cls) -> str:
        r = random.randint(0, 2 ** 256)
        r = r.to_bytes(32, byteorder='big')
        r = crypto.sha256(r)
        r = r.hexdigest()
        return r


    @classmethod
    def get_time_now(cls) -> str:
        return datetime.utcnow().isoformat()


    def to_dict(self: Transaction) -> OrderedDict:
        data = OrderedDict([
            ['version', self.version],
            ['id', self.id],
            ['time', self.time],
            ['sender_address', self.sender_address],
            ['recipient_address', self.recipient_address],
            ['sender_public_key', self.sender_public_key],
            ['amount', int(self.amount)],
            ['fee', int(self.fee)],
            ['signature', self.signature],
            ['hash', self.hash],
        ])

        return data


    @classmethod
    def from_dict(cls: type, data: Dict, check: bool=True) -> Transaction:
        tx = Transaction(
            version=data['version'],
            id_=data['id'],
            time_=data['time'],
            sender_address=data['sender_address'],
            recipient_address=data['recipient_address'],
            sender_public_key=data['sender_public_key'],
            amount=data['amount'],
            fee=data['fee'],
            signature=data['signature'],
            hash_=data['hash'],
            check=check,
        )

        return tx


    def serialize(self: Transaction) -> str:
        data = self.to_dict()
        message = json.dumps(data)
        return message


    @classmethod
    def deserialize(cls: type, message: str, check: bool=True) -> Transaction:
        data = json.loads(message)
        tx = Transaction.from_dict(data, check=check)
        return tx


    def verify(self: Transaction) -> bool:
        if not self.verify_hash():
            return False

        if not self.verify_signature():
            return False

        return True


    def verify_signature(self: Transaction) -> bool:
        data = OrderedDict([
            ['version', self.version],
            ['id', self.id],
            ['time', self.time],
            ['sender_address', self.sender_address],
            ['recipient_address', self.recipient_address],
            ['sender_public_key', self.sender_public_key],
            ['amount', self.amount],
            ['fee', self.fee],
            # without signature
            # without hash
        ])

        message = json.dumps(data)
        
        return crypto.verify_message(self.sender_public_key,
                                     self.signature,
                                     message)


    def verify_hash(self: Transaction) -> bool:
        return self.hash == self.calc_hash()


    def calc_hash(self: Transaction) -> str:
        data = OrderedDict([
            ['version', self.version],
            ['id', self.id],
            ['time', self.time],
            ['sender_address', self.sender_address],
            ['recipient_address', self.recipient_address],
            ['sender_public_key', self.sender_public_key],
            ['amount', self.amount],
            ['fee', self.fee],
            ['signature', self.signature],
            # without hash
        ])

        message = json.dumps(data)
        message_bytes = message.encode()
        hash_ = crypto.sha256(message_bytes).hexdigest()
        return hash_


    def sign(self: Transaction, private_key: str) -> str:
        data = OrderedDict([
            ['version', self.version],
            ['id', self.id],
            ['time', self.time],
            ['sender_address', self.sender_address],
            ['recipient_address', self.recipient_address],
            ['sender_public_key', self.sender_public_key],
            ['amount', self.amount],
            ['fee', self.fee],
            # without signature
            # without hash
        ])

        message = json.dumps(data)
        signature = crypto.sign_message(private_key, message)
        self.signature = signature
        self.hash = self.calc_hash()
        return self


def test1():
    sk0, pk0, addr0 = crypto.generate_private_public_address_key()
    sk1, pk1, addr1 = crypto.generate_private_public_address_key()

    tx0 = Transaction(
        version='1.0',
        id_=Transaction.gen_random_id(),
        time_=Transaction.get_time_now(),
        sender_address=addr0,
        recipient_address=addr1,
        sender_public_key=pk0,
        amount=1_000_000_000,
        fee=1_000,
        signature=None,
        hash_=None,
        check=False,
    ).sign(sk0)

    msg0 = tx0.serialize()
    print(msg0)

    tx1 = Transaction.deserialize(msg0)
    print(tx1.verify_signature())


def test2():
    sk0, pk0, addr0 = crypto.generate_private_public_address_key()
    sk1, pk1, addr1 = crypto.generate_private_public_address_key()

    tx0 = Transaction(
        version='1.0',
        id_=Transaction.gen_random_id(),
        time_=Transaction.get_time_now(),
        sender_address=addr0,
        recipient_address=addr1,
        sender_public_key=pk0,
        amount=1_000_000_000,
        fee=1_000,
        signature=None,
        hash_=None,
        check=False,
    ).sign(sk0)

    msg0 = tx0.serialize()
    print(msg0)

    tx1 = Transaction.deserialize(msg0)
    print(tx1.verify_signature())


if __name__ == '__main__':
    test2()
