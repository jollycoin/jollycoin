from typing import List, Dict
from decimal import Decimal
from datetime import datetime, timedelta
import json

from sqlalchemy import func
from aiohttp import ClientSession
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import requests

from .config import Config
from .db import Session, TransactionModel, BlockModel
from .block import Block
from .transaction import Transaction
from . import log


class BlockchainError(Exception):
    pass


class Blockchain:
    def __init__(self):
        # self.difficulty = 0x000000ffffffffff_ffffffffffffffff_ffffffffffffffff_ffffffffffffffff # NOTE: original difficulty
        self.difficulty = 0x00000fffffffffff_ffffffffffffffff_ffffffffffffffff_ffffffffffffffff # NOTE: temp easier difficulty
        # self.difficulty = 0x00ffffffffffffff_ffffffffffffffff_ffffffffffffffff_ffffffffffffffff # NOTE: temp very easier difficulty
        self.reward_amount = 1_000_000
        self.fee_amount = 1_000
        self.max_supply_amount = 21_000_000 * 1_000_000


    def get_difficulty(self) -> int:
        return self.difficulty


    def set_difficulty(self, difficulty: int):
        self.difficulty = difficulty


    def get_reward_amount(self) -> int:
        return self.reward_amount


    def set_reward_amount(self, reward_amount: int):
        self.reward_amount = reward_amount


    def get_fee_amount(self) -> int:
        return self.fee_amount


    def set_fee_amount(self, fee_amount: int):
        self.fee_amount = fee_amount


    def get_max_supply_amount(self) -> int:
        return self.max_supply_amount


    def get_total_supply_amount(self, session: Session) -> int:
        q = session.query(func.sum(TransactionModel.amount).label('total_supply_amonut'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        r = q.one()
        total_supply_amonut = r.total_supply_amonut or 0.0
        return total_supply_amonut


    def get_volume(self, session: Session) -> Dict[str, int]:
        # volume_1h
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(hours=1))
        r = q.one()
        volume_1h = r.volume or 0.0

        # volume_8h
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(hours=2))
        r = q.one()
        volume_8h = r.volume or 0.0

        # volume_12h
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(hours=12))
        r = q.one()
        volume_12h = r.volume or 0.0

        # volume_24h
        # volume_1d
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(hours=24))
        r = q.one()
        volume_24h = r.volume or 0.0
        volume_1d = volume_24h

        # volume_2d
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=2))
        r = q.one()
        volume_2d = r.volume or 0.

        # volume_3d
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=3))
        r = q.one()
        volume_3d = r.volume or 0.0

        # volume_5d
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=5))
        r = q.one()
        volume_5d = r.volume or 0.0

        # volume_7d
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=7))
        r = q.one()
        volume_7d = r.volume or 0.0

        # volume_10d
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=10))
        r = q.one()
        volume_10d = r.volume or 0.0

        # volume_15d
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=15))
        r = q.one()
        volume_15d = r.volume or 0.0

        # volume_30d
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=30))
        r = q.one()
        volume_30d = r.volume or 0.0

        # volume_1m
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - relativedelta(months=1))
        r = q.one()
        volume_1m = r.volume or 0.0

        # volume_2m
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - relativedelta(months=2))
        r = q.one()
        volume_2m = r.volume or 0.0

        # volume_3m
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - relativedelta(months=3))
        r = q.one()
        volume_3m = r.volume or 0.0

        # volume_6m
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - relativedelta(months=6))
        r = q.one()
        volume_6m = r.volume or 0.0

        # volume_12m
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - relativedelta(months=12))
        r = q.one()
        volume_12m = r.volume or 0.0
        volume_1y = volume_12m

        # volume_2y
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - relativedelta(months=2 * 12))
        r = q.one()
        volume_2y = r.volume or 0.0

        # volume_3y
        q = session.query(func.sum(TransactionModel.amount).label('volume'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == None)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - relativedelta(months=3 * 12))
        r = q.one()
        volume_3y = r.volume or 0.0

        # volume
        volume = {
            '1h': volume_1h,
            '8h': volume_8h,
            '12h': volume_12h,
            '24h': volume_24h,
            '1d': volume_1d,
            '2d': volume_2d,
            '3d': volume_3d,
            '5d': volume_5d,
            '7d': volume_7d,
            '10d': volume_10d,
            '15d': volume_15d,
            '30d': volume_30d,
            '1m': volume_1m,
            '2m': volume_2m,
            '3m': volume_3m,
            '6m': volume_6m,
            '12m': volume_12m,
            '1y': volume_1y,
            '2y': volume_2y,
            '3y': volume_3y,
        }

        return volume


    def get_hourly_volume(self, session: Session) -> int:
        volume = []

        for i in range(23, -1, -1):
            dt = datetime.utcnow() - timedelta(hours=i)

            q = session.query(func.sum(TransactionModel.amount).label('volume'))
            q = q.filter(TransactionModel.confirmed == True)
            q = q.filter(TransactionModel.sender_address == None)
            q = q.filter(TransactionModel.time_dt >= dt)
            r = q.one()
            v = r.volume or 0.0

            volume.append([dt.isoformat(), v])

        return volume


    def get_daily_volume(self, session: Session) -> int:
        volume = []

        for i in range(31, -1, -1):
            dt = datetime.utcnow() - timedelta(days=i)

            q = session.query(func.sum(TransactionModel.amount).label('volume'))
            q = q.filter(TransactionModel.confirmed == True)
            q = q.filter(TransactionModel.sender_address == None)
            q = q.filter(TransactionModel.time_dt >= dt)
            r = q.one()
            v = r.volume or 0.0

            volume.append([dt.isoformat(), v])

        return volume


    def get_monthly_volume(self, session: Session) -> int:
        volume = []

        for i in range(35, -1, -1):
            dt = datetime.utcnow() - relativedelta(months=i)

            q = session.query(func.sum(TransactionModel.amount).label('volume'))
            q = q.filter(TransactionModel.confirmed == True)
            q = q.filter(TransactionModel.sender_address == None)
            q = q.filter(TransactionModel.time_dt >= dt)
            r = q.one()
            v = r.volume or 0.0

            volume.append([dt.isoformat(), v])

        return volume


    #
    # address info
    #
    @classmethod
    def is_valid_address(cls, address: str) -> bool:
        if len(address) != 65:
            return False

        if address[0] != 'J':
            return False

        valid_chars = '0123456789abcdef'

        for c in address[1:]:
            if c not in valid_chars:
                return False

        return True


    def get_address_info(self, session: Session, address: str, check: bool = True,
                         return_confirmed_transactions: bool = True,
                         return_unconfirmed_transactions: bool = True) -> Dict[str, int]:
        confirmed_transactions = []
        unconfirmed_transactions = []
        
        confirmed_total_received = 0
        confirmed_total_sent = 0
        confirmed_total_fee = 0
        confirmed_balance = 0

        unconfirmed_total_received = 0
        unconfirmed_total_sent = 0
        unconfirmed_total_fee = 0
        unconfirmed_balance = 0

        # confirmed transaction sender_address
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == address)
        transactions_rows = q.all()

        for tx_row in transactions_rows:
            tx = Transaction(
                version=tx_row.version,
                id_=tx_row.id,
                time_=tx_row.time,
                sender_address=tx_row.sender_address,
                recipient_address=tx_row.recipient_address,
                sender_public_key=tx_row.sender_public_key,
                amount=tx_row.amount,
                fee=tx_row.fee,
                signature=tx_row.signature,
                hash_=tx_row.hash,
                check=True if check and tx_row.sender_address else False,
            )

            confirmed_total_sent += tx.amount
            confirmed_total_fee += tx.fee

            if return_confirmed_transactions:
                confirmed_transactions.append(tx)

        # confirmed transaction recipient_address
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.recipient_address == address)
        transactions_rows = q.all()

        for tx_row in transactions_rows:
            tx = Transaction(
                version=tx_row.version,
                id_=tx_row.id,
                time_=tx_row.time,
                sender_address=tx_row.sender_address,
                recipient_address=tx_row.recipient_address,
                sender_public_key=tx_row.sender_public_key,
                amount=tx_row.amount,
                fee=tx_row.fee,
                signature=tx_row.signature,
                hash_=tx_row.hash,
                check=True if check and tx_row.sender_address else False,
            )

            confirmed_total_received += tx.amount

            if return_confirmed_transactions:
                confirmed_transactions.append(tx)

        confirmed_balance = confirmed_total_received - confirmed_total_sent - confirmed_total_fee

        # unconfirmed transaction sender_address
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == False)
        q = q.filter(TransactionModel.sender_address == address)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=1))
        q = q.filter(TransactionModel.amount >= 0)
        q = q.filter(TransactionModel.fee >= 0)
        transactions_rows = q.all()

        for tx_row in transactions_rows:
            tx = Transaction(
                version=tx_row.version,
                id_=tx_row.id,
                time_=tx_row.time,
                sender_address=tx_row.sender_address,
                recipient_address=tx_row.recipient_address,
                sender_public_key=tx_row.sender_public_key,
                amount=tx_row.amount,
                fee=tx_row.fee,
                signature=tx_row.signature,
                hash_=tx_row.hash,
                check=True if check and tx_row.sender_address else False,
            )

            unconfirmed_total_sent += tx.amount
            unconfirmed_total_fee += tx.fee

            if return_unconfirmed_transactions:
                unconfirmed_transactions.append(tx)

        # unconfirmed transaction recipient_address
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == False)
        q = q.filter(TransactionModel.recipient_address == address)
        q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=1))
        q = q.filter(TransactionModel.amount >= 0)
        q = q.filter(TransactionModel.fee >= 0)
        transactions_rows = q.all()

        for tx_row in transactions_rows:
            tx = Transaction(
                version=tx_row.version,
                id_=tx_row.id,
                time_=tx_row.time,
                sender_address=tx_row.sender_address,
                recipient_address=tx_row.recipient_address,
                sender_public_key=tx_row.sender_public_key,
                amount=tx_row.amount,
                fee=tx_row.fee,
                signature=tx_row.signature,
                hash_=tx_row.hash,
                check=True if check and tx_row.sender_address else False,
            )

            unconfirmed_total_received += tx.amount

            if return_unconfirmed_transactions:
                unconfirmed_transactions.append(tx)

        unconfirmed_balance = unconfirmed_total_received - unconfirmed_total_sent - unconfirmed_total_fee

        # total
        total_received = confirmed_total_received + unconfirmed_total_received
        total_sent = confirmed_total_sent + unconfirmed_total_sent
        total_fee = confirmed_total_fee + unconfirmed_total_fee
        balance = confirmed_balance + unconfirmed_balance

        return {
            'address': address,
            'confirmed_transactions': confirmed_transactions,
            'unconfirmed_transactions': unconfirmed_transactions,
            
            'confirmed_total_received': confirmed_total_received,
            'confirmed_total_sent': confirmed_total_sent,
            'confirmed_total_fee': confirmed_total_fee,
            'confirmed_balance': confirmed_balance,
            'unconfirmed_total_received': unconfirmed_total_received,
            'unconfirmed_total_sent': unconfirmed_total_sent,
            'unconfirmed_total_fee': unconfirmed_total_fee,
            'unconfirmed_balance': unconfirmed_balance,
            'total_received': total_received,
            'total_sent': total_sent,
            'total_fee': total_fee,
            'balance': balance,   
        }


    def _get_address_info_confirmed_balance(self, session: Session, address: str) -> int:
        # optimized call
        confirmed_total_received = 0
        confirmed_total_sent = 0
        confirmed_total_fee = 0
        confirmed_balance = 0

        # confirmed_total_sent
        q = session.query(func.sum(TransactionModel.amount).label('confirmed_total_sent'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == address)
        r = q.one()
        confirmed_total_sent = r.confirmed_total_sent or 0.0

        # confirmed_total_fee
        q = session.query(func.sum(TransactionModel.fee).label('confirmed_total_fee'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.sender_address == address)
        r = q.one()
        confirmed_total_fee = r.confirmed_total_fee or 0.0

        # confirmed_total_received
        q = session.query(func.sum(TransactionModel.amount).label('confirmed_total_received'))
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.recipient_address == address)
        r = q.one()
        confirmed_total_received = r.confirmed_total_received or 0.0

        # confirmed_balance
        confirmed_balance = confirmed_total_received - confirmed_total_sent - confirmed_total_fee
        return confirmed_balance


    #
    # transaction
    #
    def get_transaction(self, session: Session, transaction_id: str) -> Transaction:
        # check `transaction` database
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.id == transaction_id)
        tx_row = q.first()

        if not tx_row:
            raise BlockchainError('unknown transaction')

        tx_dict = tx_row.to_dict()
        tx = Transaction.from_dict(tx_dict, check=False)

        # verify transaction ?
        # if not tx.verify():
        #    raise BlockchainError('transaction could not be verified')

        return tx


    def get_transactions_range(self, session: Session, start: int, end: int=None, is_reversed: bool=False) -> List[Transaction]:
        if end is None:
            end = start + 15_000

        assert isinstance(start, int)
        assert isinstance(end, int)
        assert isinstance(is_reversed, bool)
        assert start < end
        assert end - start <= 15_000

        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == True)
        q = q.order_by(TransactionModel.time_dt.desc() if is_reversed else TransactionModel.time_dt.asc())
        q = q.offset(start)
        q = q.limit(end - start)
        transactions_rows = q.all()
        transactions = []

        for transaction_row in transactions_rows:
            tx = Transaction(
                version=transaction_row.version,
                id_=transaction_row.id,
                time_=transaction_row.time,
                sender_address=transaction_row.sender_address,
                recipient_address=transaction_row.recipient_address,
                sender_public_key=transaction_row.sender_public_key,
                amount=transaction_row.amount,
                fee=transaction_row.fee,
                signature=transaction_row.signature,
                hash_=transaction_row.hash,
                check=False,
            )

            transactions.append(tx)

        return transactions


    def get_n_transactions(self, session: Session) -> int:
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == True)
        n = q.count()
        return n


    #
    # unconfirmed transactions
    #
    def get_unconfirmed_transaction(self, session: Session, transaction_id: str) -> Transaction:
        # check unconfirmed transactions
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.id == transaction_id)
        q = q.filter(TransactionModel.confirmed == False)
        # q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=1))
        q = q.filter(TransactionModel.amount >= 0)
        q = q.filter(TransactionModel.fee >= 0)
        tx_row = q.first()

        if not tx_row:
            raise BlockchainError('unknown unconfirmed transaction')

        tx_dict = tx_row.to_dict()
        tx = Transaction.from_dict(tx_dict)
        
        # verify transaction
        if not tx.verify():
            raise BlockchainError('unconfirmed transaction could not be verified')

        return tx


    def get_unconfirmed_transactions_range(self, session: Session, start: int, end: int=None, is_reversed: bool=False) -> List[Transaction]:
        if end is None:
            end = start + 10_000

        assert isinstance(start, int)
        assert isinstance(end, int)
        assert isinstance(is_reversed, bool)
        assert start < end
        assert end - start <= 10_000

        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == False)
        q = q.order_by(TransactionModel.time_dt.desc() if is_reversed else TransactionModel.time_dt.asc())
        # q = q.filter(TransactionModel.time_dt >= datetime.utcnow() - timedelta(days=1))
        q = q.filter(TransactionModel.amount >= 0)
        q = q.filter(TransactionModel.fee >= 0)
        q = q.offset(start)
        q = q.limit(end - start)
        transactions_rows = q.all()
        transactions = []

        for transaction_row in transactions_rows:
            # filter bad transactions
            if transaction_row.sender_address and not self.is_valid_address(transaction_row.sender_address):
                log.warn(f'skipping bad sender address {transaction_row.sender_address!r}')
                continue

            if not self.is_valid_address(transaction_row.recipient_address):
                log.warn(f'skipping bad recipient address {transaction_row.recipient_address!r}')
                continue

            # transaction
            tx = Transaction(
                version=transaction_row.version,
                id_=transaction_row.id,
                time_=transaction_row.time,
                sender_address=transaction_row.sender_address,
                recipient_address=transaction_row.recipient_address,
                sender_public_key=transaction_row.sender_public_key,
                amount=transaction_row.amount,
                fee=transaction_row.fee,
                signature=transaction_row.signature,
                hash_=transaction_row.hash,
            )

            transactions.append(tx)

        return transactions


    def get_n_unconfirmed_transactions(self, session: Session) -> int:
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == False)
        q = q.filter(TransactionModel.amount >= 0)
        q = q.filter(TransactionModel.fee >= 0)
        n = q.count()
        return n


    def add_unconfirmed_transaction(self, session: Session, transaction: Transaction):
        # check amount
        if transaction.amount < 0:
            raise BlockchainError('negative value')

        # check fee
        if transaction.fee < self.fee_amount:
            raise BlockchainError('not enough fee')

        # verify transaction
        if not transaction.verify():
            raise BlockchainError('transaction could not be verified')

        # check if transaction is already confirmed
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.id == transaction.id)
        tx_row = q.first()

        if tx_row:
            raise BlockchainError('transaction already confirmed')

        # check if unconfirmed transaction is already known
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == False)
        q = q.filter(TransactionModel.id == transaction.id)
        tx_row = q.first()

        if tx_row:
            raise BlockchainError('transaction already in unconfirmed transactions')

        # add to unconfirmed transactions
        tx_row = TransactionModel(
            block_id=None,
            confirmed=False,

            version=transaction.version,
            id=transaction.id,
            time=transaction.time,
            time_dt=parse(transaction.time),
            time_ts=parse(transaction.time).timestamp(),
            sender_address=transaction.sender_address,
            recipient_address=transaction.recipient_address,
            sender_public_key=transaction.sender_public_key,
            amount=transaction.amount,
            fee=transaction.fee,
            signature=transaction.signature,
            hash=transaction.hash,
            message=transaction.serialize(),
        )

        session.add(tx_row)
        session.flush()


    #
    # block
    #
    def get_block(self, session: Session, block_id: str) -> Block:
        q = session.query(BlockModel)
        q = q.filter(BlockModel.id == block_id)
        block_row = q.first()

        if not block_row:
            raise BlockchainError('block does not exist')

        transactions = json.loads(block_row.transactions)
        transactions = [
            Transaction.from_dict(tx, check=True if block_row.height > 0 and i > 0 else False)
            for i, tx in enumerate(transactions)
        ]

        b = Block(
            version=block_row.version,
            height=block_row.height,
            id_=block_row.id,
            prev_hash=block_row.prev_hash,
            time_=block_row.time,
            transactions=transactions,
            merkle_root=block_row.merkle_root,
            difficulty=block_row.difficulty,
            nonce=block_row.nonce,
            hash_=block_row.hash,
            check=False,
        )

        return b


    def get_last_block(self, session: Session) -> Block:
        # NOTE: used by node/miner only
        q = session.query(BlockModel)
        q = q.order_by(BlockModel.height.desc())
        block_row = q.first()

        if not block_row:
            return None

        transactions = json.loads(block_row.transactions)
        transactions = [
            Transaction.from_dict(tx, check=True if block_row.height > 0 and i > 0 else False)
            for i, tx in enumerate(transactions)
        ]

        b = Block(
            version=block_row.version,
            height=block_row.height,
            id_=block_row.id,
            prev_hash=block_row.prev_hash,
            time_=block_row.time,
            transactions=transactions,
            merkle_root=block_row.merkle_root,
            difficulty=block_row.difficulty,
            nonce=block_row.nonce,
            hash_=block_row.hash,
        )

        return b


    def get_blocks_range(self, session: Session, start: int, end: int=None, is_reversed: bool=False) -> List[Block]:
        if end is None:
            end = start + 15_000

        assert isinstance(start, int)
        assert isinstance(end, int)
        assert isinstance(is_reversed, bool)
        assert start < end
        assert end - start <= 15_000

        q = session.query(BlockModel)
        q = q.order_by(BlockModel.height.desc() if is_reversed else BlockModel.height.asc())
        q = q.offset(start)
        q = q.limit(end - start)
        blocks_rows = q.all()
        blocks = []

        for block_row in blocks_rows:
            transactions = json.loads(block_row.transactions)
            transactions = [
                Transaction.from_dict(tx, check=True if block_row.height > 0 and i > 0 else False)
                for i, tx in enumerate(transactions)
            ]

            # print(f'block_row: {block_row.to_dict()!r}')

            b = Block(
                version=block_row.version,
                height=block_row.height,
                id_=block_row.id,
                prev_hash=block_row.prev_hash,
                time_=block_row.time,
                transactions=transactions,
                merkle_root=block_row.merkle_root,
                difficulty=block_row.difficulty,
                nonce=block_row.nonce,
                hash_=block_row.hash,
            )

            blocks.append(b)

        return blocks


    def get_n_blocks(self, session: Session) -> int:
        q = session.query(BlockModel)
        n = q.count()
        return n


    def add_block(self, session: Session, block: Block, check_difficulty=True):
        # check difficulty
        if check_difficulty:
            if self.difficulty != block.difficulty:
                log.warn(f'current difficulty {self.difficulty}')
                log.warn(f'difficulty block {block.difficulty}')
                raise BlockchainError('difficulty does not match')

        # verify block
        if not block.verify():
            raise BlockchainError('block could not be verified')

        # check first/reward transaction
        # TODO: specialized functions for checking correctness of transactions fields
        if block.height > 0:
            reward_transaction = block.transactions[0]

            if reward_transaction.version != '1.0':
                raise BlockchainError('wrong reward transaction: version')

            if len(reward_transaction.id) != 64:
                raise BlockchainError('wrong reward transaction: id')

            try:
                parse(reward_transaction.time)
            except ValueError as e:
                raise BlockchainError('wrong reward transaction: time')

            if reward_transaction.sender_address != None:
                raise BlockchainError('wrong reward transaction: sender_address')

            if not self.is_valid_address(reward_transaction.recipient_address):
                raise BlockchainError(
                    'wrong reward transaction: recipient_address '
                    f'{reward_transaction.recipient_address!r}'
                )

            if reward_transaction.sender_public_key != None:
                raise BlockchainError('wrong reward transaction: sender_public_key')

            if reward_transaction.signature != None:
                raise BlockchainError('wrong reward transaction: signature')

            # calculate allowed_reward_amount
            allowed_reward_amount = self.reward_amount

            for tx in block.transactions[1:]:
                allowed_reward_amount += tx.fee

            if reward_transaction.amount < 0 or reward_transaction.amount > allowed_reward_amount:
                raise BlockchainError(
                    'wrong reward transaction: amount'
                    f'{reward_transaction.amount!r}'
                )

            if reward_transaction.fee != 0:
                raise BlockchainError(
                    'wrong reward transaction: fee'
                    f'{reward_transaction.fee!r}'
                )

            # check rest of transactions
            # TODO: specialized functions for checking correctness of transactions fields
            for tx in block.transactions[1:]:
                if tx.version != '1.0':
                    raise BlockchainError('wrong transaction: version')

                if len(tx.id) != 64:
                    raise BlockchainError('wrong transaction: id')

                try:
                    parse(tx.time)
                except ValueError as e:
                    raise BlockchainError('wrong transaction: time')

                if not self.is_valid_address(tx.sender_address):
                    raise BlockchainError(
                        'wrong transaction: sender_address'
                        f'{tx.recipient_address!r}'
                    )

                if not self.is_valid_address(tx.recipient_address):
                    raise BlockchainError(
                        'wrong transaction: recipient_address'
                        f'{tx.recipient_address!r}'
                    )

                if tx.amount < 0:
                    raise BlockchainError('wrong transaction: amount')

                if tx.fee < 0 or tx.fee < self.fee_amount:
                    raise BlockchainError('wrong transaction: fee')

        # check if block already exists
        q = session.query(BlockModel)
        q = q.filter(
            (BlockModel.id == block.id) |
            (BlockModel.height == block.height))
        block_row = q.first()

        if block_row:
            raise BlockchainError('block already exists')

        # check previous block
        if block.height > 0:
            # check previous block height
            q = session.query(BlockModel)
            q = q.filter(BlockModel.height == block.height - 1)
            prev_block_row = q.first()

            if not prev_block_row:
                raise BlockchainError('wrong previous block')

            # check previous block hash
            if block.prev_hash != prev_block_row.hash:
                raise BlockchainError('wrong previous block hash')

        # check double spent transactions
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == True)
        q = q.filter(TransactionModel.id.in_([tx.id for tx in block.transactions]))
        c = q.count()

        if c > 0:
            # some of transactions already in blockchain
            raise BlockchainError('double spent')

        # check if addresses which send funds already have enough funds
        # NOTE: genesis block - assume that all transactions are correct
        if block.height > 0:
            # plain block
            send_by_address = {}
            addresses = [tx.sender_address for tx in block.transactions if tx.sender_address]

            # skip first/reward transaction
            # first/reward transaction is already checked above
            for tx in block.transactions[1:]:
                try:
                    send_by_address[tx.sender_address] += tx.amount + tx.fee
                except KeyError as e:
                    send_by_address[tx.sender_address] = tx.amount + tx.fee

            for address in addresses:
                address_info_confirmed_balance = self._get_address_info_confirmed_balance(session, address)
                transfer_amount = send_by_address[address]

                if address_info_confirmed_balance < transfer_amount:
                    raise BlockchainError(f'not enough funds, from sender address {address!r} trying to send {transfer_amount}, but balance is {address_info_confirmed_balance}')

        # add block
        block_row = BlockModel(
            version=block.version,
            height=block.height,
            id=block.id,
            prev_hash=block.prev_hash,
            time=block.time,
            time_dt=parse(block.time),
            time_ts=parse(block.time).timestamp(),
            transactions=json.dumps([tx.to_dict() for tx in block.transactions]),
            merkle_root=block.merkle_root,
            difficulty=block.difficulty,
            nonce=block.nonce,
            hash=block.hash,
            message=block.serialize(),
        )

        session.add(block_row)
        session.flush()

        # NOTE: confirm first already known unconfirmed transactions
        #       then add new just confirmed transactions
        
        # confirm known transactions
        q = session.query(TransactionModel)
        q = q.filter(TransactionModel.confirmed == False)
        q = q.filter(TransactionModel.id.in_([tx.id for tx in block.transactions]))
        unconfirmed_transactions_rows = q.all()

        for tx_row in unconfirmed_transactions_rows:
            tx_row.block = block.id
            tx_row.confirmed = True

        unconfirmed_transactions_rows_ids = set([tx_row.id for tx_row in unconfirmed_transactions_rows])
        
        # new confirmed transactions
        new_transactions_rows = []

        for tx in block.transactions:
            if tx.id in unconfirmed_transactions_rows_ids:
                continue

            tx_row = TransactionModel(
                block_id=block.id,
                confirmed=True,

                version=tx.version,
                id=tx.id,
                time=tx.time,
                time_dt=parse(tx.time),
                time_ts=parse(tx.time).timestamp(),
                sender_address=tx.sender_address,
                recipient_address=tx.recipient_address,
                sender_public_key=tx.sender_public_key,
                amount=tx.amount,
                fee=tx.fee,
                signature=tx.signature,
                hash=tx.hash,
                message=tx.serialize(),
            )

            session.add(tx_row)

        session.flush()


    def add_blocks(self, session: Session, blocks: List[Block], check_difficulty=True):
        # NOTE: used by node/miner only
        for block in blocks:
            self.add_block(session, block, check_difficulty)


    def verify_block(self, block: Block) -> bool:
        return block.verify()


    def mine_block(self, block: Block) -> Block:
        b = block.mine()
        return b


    async def submit_block(self, block: Block) -> bool:
        async with ClientSession() as client_session:
            url = f'{Config.COORDINATOR}/v1/block/add'
            data = {'block': block.to_dict()}

            async with client_session.post(url, json=data) as res:
                data = await res.json()
                # log.debug(data)

                if data['status'] == 'error':
                    raise BlockchainError(f'could not submit block: {data!r}')

        return True