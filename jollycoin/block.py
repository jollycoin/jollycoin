from decimal import Decimal
from datetime import datetime
from collections import OrderedDict
from typing import List, Dict, Sequence, TypeVar
import math
import json
import random

from .transaction import Transaction
from .merkle import Merkle
from . import crypto


# we require it defined like this because of python3.6
# it will be overwritten once Block class is defined
Block = TypeVar('Block')


class BlockError(Exception):
    pass


class Block:
    def __init__(self: Block,
                 version: str,
                 height: int,
                 id_: str,
                 prev_hash: str,
                 time_: str,
                 transactions: List[Transaction],
                 merkle_root: str,
                 difficulty: int,
                 nonce: int,
                 hash_: str,
                 check: bool=True):
        assert version == '1.0'
        self.version = version
        self.height = height
        self.id = id_
        self.prev_hash = prev_hash
        self.time = time_
        self.transactions = transactions
        self.merkle_root = merkle_root
        self.difficulty = difficulty
        self.nonce = nonce
        self.hash = hash_

        if check:
            if not self.verify_hash():
                raise BlockError('wrong hash')

            if not self.verify_merkle_root():
                raise BlockError('wrong merkle root')

            if not self.verify_nonce():
                raise BlockError('wrong nonce')


    def __repr__(self: Block) -> str:
        return f'<{self.__class__.__name__} id: {self.id!r}, prev_hash: {self.prev_hash!r}, *n_transactions: {len(self.transactions)}, nonce: {self.nonce!r}, hash: {self.hash!r}>'


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


    def to_dict(self: Block, without: Sequence[str]=()) -> OrderedDict:
        data = OrderedDict([
            ['version', self.version],
            ['height', self.height],
            ['id', self.id],
            ['prev_hash', self.prev_hash],
            ['time', self.time],
            ['transactions', [tx.to_dict() for tx in self.transactions]],
            ['merkle_root', self.merkle_root],
            ['difficulty', self.difficulty],
            ['nonce', self.nonce],
            ['hash', self.hash],
        ])

        for k in without:
            del data[k]

        return data


    @classmethod
    def from_dict(cls: type, data: Dict, check: bool=True) -> Block:
        # verify transactions, but skip reward transaction
        if data['height'] == 0:
            transactions = []
            
            for tx_data in data['transactions']:
                tx = Transaction.from_dict(tx_data, check=False)
                transactions.append(tx)
        else:
            transactions = [
                Transaction.from_dict(data['transactions'][0], check=False)
            ]

            for tx_data in data['transactions'][1:]:
                tx = Transaction.from_dict(tx_data, check=True)
                transactions.append(tx)

        # create block
        b = Block(
            version=data['version'],
            height=data['height'],
            id_=data['id'],
            prev_hash=data['prev_hash'],
            time_=data['time'],
            transactions=transactions,
            merkle_root=data['merkle_root'],
            difficulty=data['difficulty'],
            nonce=data['nonce'],
            hash_=data['hash'],
            check=check,
        )

        return b


    def serialize(self: Block) -> str:
        data = self.to_dict()
        message = json.dumps(data)
        return message


    @classmethod
    def deserialize(cls: type, message: str, check: bool=True) -> Block:
        data = json.loads(message)
        b = Block.from_dict(data, check=check)
        return b

    
    def verify(self: Block) -> bool:
        if not self.verify_hash():
            return False

        if not self.verify_merkle_root():
            return False

        if not self.verify_nonce():
            return False

        return True


    def verify_hash(self: Block) -> bool:
        # print(f'Block.verify_hash: {self.hash!r} {self.calc_hash()!r}')
        return self.hash == self.calc_hash()


    def verify_merkle_root(self: Block) -> bool:
        return self.merkle_root == self.calc_merkel_root()


    def verify_nonce(self: Block) -> bool:
        m = self.to_dict(without=['nonce', 'hash'])
        m = json.dumps(m)
        m = m.encode()

        sha256 = crypto.sha256
        difficulty = self.difficulty
        nonce = self.nonce

        byte_length = int(math.ceil(nonce.bit_length() / 8))
        n = nonce.to_bytes(byte_length, byteorder='big')

        h = sha256()
        h.update(m)
        h.update(n)
        hd = h.hexdigest()
        d = int(hd, 16)

        if d < difficulty:
            return True

        return False


    def calc_merkel_root(self: Block) -> str:
        m = Merkle()

        for tx in self.transactions:
            try:
                m.add_leaf(tx.hash)
            except ValueError as e:
                raise BlockError(f'wrong transaction hash: {tx.hash!r}')

        m.make_tree()
        r = m.get_merkle_root()
        return r


    def calc_hash(self: Block) -> str:
        data = OrderedDict([
            ['version', self.version],
            ['height', self.height],
            ['id', self.id],
            ['prev_hash', self.prev_hash],
            ['time', self.time],
            ['transactions', [tx.to_dict() for tx in self.transactions]],
            ['merkle_root', self.merkle_root],
            ['difficulty', self.difficulty],
            ['nonce', self.nonce],
            # without hash
        ])

        message = json.dumps(data)
        message_bytes = message.encode()
        hash_ = crypto.sha256(message_bytes).hexdigest()
        return hash_


    def calc_nonce(self: Block) -> int:
        sha256 = crypto.sha256
        difficulty = self.difficulty
        
        m = self.to_dict(without=['nonce', 'hash'])
        m = json.dumps(m)
        m = m.encode()

        found = False
        nonce = 0

        while not found:
            byte_length = int(math.ceil(nonce.bit_length() / 8))
            n = nonce.to_bytes(byte_length, byteorder='big')

            h = sha256()
            h.update(m)
            h.update(n)
            hd = h.hexdigest()
            d = int(hd, 16)

            if d < difficulty:
                found = True
                break

            nonce += 1

        return nonce


    def iter_calc_nonce(self: Block, iterations: int=100_000) -> int:
        sha256 = crypto.sha256
        difficulty = self.difficulty
        
        m = self.to_dict(without=['nonce', 'hash'])
        m = json.dumps(m)
        m = m.encode()

        found = False
        nonce = 0

        while not found:
            for i in range(iterations):
                byte_length = int(math.ceil(nonce.bit_length() / 8))
                n = nonce.to_bytes(byte_length, byteorder='big')

                h = sha256()
                h.update(m)
                h.update(n)
                hd = h.hexdigest()
                d = int(hd, 16)

                if d < difficulty:
                    found = True
                    break
                else:
                    nonce += 1

            yield found, nonce


    def mine(self: Block) -> Block:
        '''
        Finds nonce, in-place updates block (self), then returns updated object.
        Have in mind that this method mutates block (self).
        '''
        if not self.merkle_root:
            self.merkle_root = self.calc_merkel_root()

        nonce = self.calc_nonce()
        self.nonce = nonce
        self.hash = self.calc_hash()
        return self


    def get_transaction(self: Block, transaction_id: str) -> Transaction:
        for tx in self.transactions:
            if tx.id == transaction_id:
                return tx

        raise ValueError(f'unknown transaction id {transaction_id!r}')


if __name__ == '__main__':
    import random
    import hashlib
    import datetime

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

    tx1 = Transaction(
        version='1.0',
        id_=Transaction.gen_random_id(),
        time_=Transaction.get_time_now(),
        sender_address=addr1,
        recipient_address=addr0,
        sender_public_key=pk1,
        amount=2_000_000_000,
        fee=1_000,
        signature=None,
        hash_=None,
        check=False,
    ).sign(sk1)
    
    b0 = Block(
        version='1.0',
        height=0,
        id_=Block.gen_random_id(),
        prev_hash=None,
        time_=Block.get_time_now(),
        transactions=[tx0, tx1],
        merkle_root=None,
        difficulty=0x0000ffffffffffff_ffffffffffffffff_ffffffffffffffff_ffffffffffffffff,
        nonce=None,
        hash_=None,
        check=False,
    ).mine()

    b0d = b0.to_dict()
    # b0d['nonce'] = 0
    print(b0d)
    print(Block.from_dict(b0d))
