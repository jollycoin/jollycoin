__version__ = '1.0.4'

import os
import json
import random
import asyncio
import hashlib
import argparse
# from contextlib import contextmanager, asynccontextmanager

from aiohttp import web, ClientSession
import aiohttp_cors
import requests

from jollycoin.config import Config
from jollycoin import log


# parse argv
parser = argparse.ArgumentParser(description='JollyCoin/JLC Node')
parser.add_argument('--host', type=str, default=Config.HOST, help='Host')
parser.add_argument('--port', type=int, default=Config.PORT, help='Port')
parser.add_argument('--db', type=str, default=Config.DB, help='Database URI')
parser.add_argument('--coordinator', type=str, default=Config.COORDINATOR, help='Coordinator URI')
parser.add_argument('--no-sync', action='store_true')
parser.add_argument('--no-mine', action='store_true')
parser.add_argument('--generate-genesis-block', action='store_true')
parser.add_argument('--miner-address', default=Config.MINER_ADDRESS, help='Miner address')
args = parser.parse_args()

# update config
Config.HOST = args.host
Config.PORT = args.port
Config.DB = args.db
Config.COORDINATOR = args.coordinator
Config.NO_SYNC = args.no_sync
Config.NO_MINE = args.no_mine
Config.GENERATE_GENESIS_BLOCK = args.generate_genesis_block
Config.MINER_ADDRESS = args.miner_address


from jollycoin.db import Session, BlockModel, TransactionModel
from jollycoin.blockchain import Blockchain, BlockchainError
from jollycoin.block import Block, BlockError
from jollycoin.transaction import Transaction, TransactionError
from jollycoin import crypto


# blockchain
blockchain = Blockchain()

# aiohttp routes
routes = web.RouteTableDef()

# locks
Lock = asyncio.Lock

# @asynccontextmanager
# async def Lock(*args, **kwds):
#     yield None

session_lock = Lock()


#
# stats
#
@routes.get('/v1/stats')
@routes.post('/v1/stats')
async def v1_stats(request):
    # calc
    async with session_lock:
        session = Session()

        try:
            # total_supply_amonut
            total_supply_amonut = blockchain.get_total_supply_amount(session)

            # circulating_supply_amonut
            circulating_supply_amonut = total_supply_amonut

            # volume
            volume = blockchain.get_volume(session)

            # hourly_volume
            hourly_volume = blockchain.get_hourly_volume(session)

            # daily_volume
            daily_volume = blockchain.get_daily_volume(session)

            # monthly_volume
            monthly_volume = blockchain.get_monthly_volume(session)
        except Exception as e:
            log.error(f'v1_stats error [0]: {e!r}')

            response = {
                'status': 'error',
                'message': 'system error',
            }

            return web.json_response(response)
        finally:
            session.close()

    # fixed max supply
    max_supply_amonut = blockchain.get_max_supply_amount()

    response = {
        'status': 'success',
        'name': 'JollyCoin',
        'symbol': 'JLC',
        'total_supply': total_supply_amonut,
        'circulating_supply': circulating_supply_amonut,
        'max_supply': max_supply_amonut,
        'volume': volume,
        'hourly_volume': hourly_volume,
        'daily_volume': daily_volume,
        'monthly_volume': monthly_volume,
    }

    return web.json_response(response)


#
# difficulty
#
@routes.post('/v1/difficulty')
async def v1_difficulty(request):
    response = {
        'status': 'success',
        'difficulty': blockchain.difficulty,
    }

    return web.json_response(response)


#
# reward
#
@routes.post('/v1/reward')
async def v1_reward(request):
    response = {
        'status': 'success',
        'reward': blockchain.reward_amount,
    }

    return web.json_response(response)


#
# fee
#
@routes.post('/v1/fee')
async def v1_fee(request):
    response = {
        'status': 'success',
        'fee': blockchain.fee_amount,
    }

    return web.json_response(response)


#
# address info
#
@routes.post('/v1/get-address-info')
async def v1_get_address_info(request):
    data = await request.json()
    address = data['address']

    async with session_lock:
        session = Session()
        
        try:
            address_info = blockchain.get_address_info(session, address, check=False)
        except BlockchainError as e:
            log.error(f'v1_get_address_info error [0]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_get_address_info error [1]: {e!r}')
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()
            session = None
    
    response = {
        'status': 'success',
        'address': address_info['address'],
        'n_confirmed_transactions': len(address_info['confirmed_transactions']),
        'n_unconfirmed_transactions': len(address_info['unconfirmed_transactions']),
        'confirmed_transactions': [tx.to_dict() for tx in address_info['confirmed_transactions']],
        'unconfirmed_transactions': [tx.to_dict() for tx in address_info['unconfirmed_transactions']],
        
        'confirmed_total_received': address_info['confirmed_total_received'],
        'confirmed_total_sent': address_info['confirmed_total_sent'],
        'confirmed_total_fee': address_info['confirmed_total_fee'],
        'confirmed_balance': address_info['confirmed_balance'],

        'unconfirmed_total_received': address_info['unconfirmed_total_received'],
        'unconfirmed_total_sent': address_info['unconfirmed_total_sent'],
        'unconfirmed_total_fee': address_info['unconfirmed_total_fee'],
        'unconfirmed_balance': address_info['unconfirmed_balance'],

        'total_received': address_info['total_received'],
        'total_sent': address_info['total_sent'],
        'total_fee': address_info['total_fee'],
        'balance': address_info['balance'],
    }

    return web.json_response(response)


#
# transaction
#
@routes.post('/v1/transaction/get')
async def v1_transaction_get(request):
    data = await request.json()
    transaction_id = data['transaction_id']

    async with session_lock:
        session = Session()

        try:
            transaction = blockchain.get_transaction(session, transaction_id)
            transaction = transaction.to_dict()
        except BlockchainError as e:
            log.error(f'v1_transaction_get error [0]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_transaction_get error [1]: {e!r}')
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()

    response = {
        'status': 'success',
        'transaction': transaction,
    }

    return web.json_response(response)


@routes.post('/v1/transaction/get-range')
async def v1_transaction_get_range(request):
    data = await request.json()
    start = data.get('start', 0)
    end = data.get('end', None)
    is_reversed = data.get('is_reversed', False)
    
    async with session_lock:
        session = Session()
        
        try:    
            transactions = blockchain.get_transactions_range(session, start, end, is_reversed)
            transactions = [tx.to_dict() for tx in transactions]
            n_transactions = blockchain.get_n_transactions(session)
        except BlockchainError as e:
            log.error(f'v1_transaction_get_range error [0]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_transaction_get_range error [1]: {e!r}')
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()

    response = {
        'status': 'success',
        'transactions': transactions,
        'n_transactions': n_transactions,
    }

    return web.json_response(response)


#
# unconfirmed transactions
#
@routes.post('/v1/unconfirmed-transaction/get')
async def v1_unconfirmed_transaction_get(request):
    data = await request.json()
    transaction_id = data['transaction_id']

    async with session_lock:
        session = Session()
        
        try:
            transaction = blockchain.get_unconfirmed_transaction(session, transaction_id)
            transaction = transaction.to_dict()
        except BlockchainError as e:
            log.error(f'v1_unconfirmed_transaction_get error [0]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_unconfirmed_transaction_get error [1]: {e!r}')
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()

    response = {
        'status': 'success',
        'transaction': transaction,
    }

    return web.json_response(response)


@routes.post('/v1/unconfirmed-transaction/get-range')
async def v1_unconfirmed_transaction_get_range(request):
    data = await request.json()
    start = data['start']
    end = data.get('end', None)
    is_reversed = data.get('is_reversed', False)

    async with session_lock:
        session = Session()
        
        try:
            unconfirmed_transactions = blockchain.get_unconfirmed_transactions_range(session, start, end, is_reversed)
            unconfirmed_transactions = [tx.to_dict() for tx in unconfirmed_transactions]
            n_unconfirmed_transactions = blockchain.get_n_unconfirmed_transactions(session)
        except BlockchainError as e:
            log.error(f'v1_unconfirmed_transaction_get_range error [0]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_unconfirmed_transaction_get_range error [1]: {e!r}')
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()

    response = {
        'status': 'success',
        'unconfirmed_transactions': unconfirmed_transactions,
        'n_unconfirmed_transactions': n_unconfirmed_transactions,
    }

    return web.json_response(response)


@routes.post('/v1/unconfirmed-transaction/add')
async def v1_unconfirmed_transaction_add(request):
    data = await request.json()
    tx_data = data['transaction']

    # create transaction out of dict
    try:
        tx = Transaction.from_dict(tx_data)
    except TransactionError as e:
        log.error(f'v1_unconfirmed_transaction_add error [0]: {e!r}')
        response = {'status': 'error', 'message': str(e)}
        return web.json_response(response)
    except Exception as e:
        log.error(f'v1_unconfirmed_transaction_add error [1]: {e!r}')
        response = {'status': 'error', 'message': 'system error'}
        return web.json_response(response)

    # add to unconfirmed transactions
    async with session_lock:
        session = Session()

        try:
            blockchain.add_unconfirmed_transaction(session, tx)
            session.commit()
        except BlockchainError as e:
            log.error(f'v1_unconfirmed_transaction_add error [2]: {e!r}')
            session.rollback()
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_unconfirmed_transaction_add error [3]: {e!r}')
            session.rollback()
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()

    response = {'status': 'success'}
    return web.json_response(response)


#
# block
#
@routes.post('/v1/block/get')
async def v1_block_get(request):
    data = await request.json()
    block_id = data['block_id']

    async with session_lock:
        session = Session()
        
        try:
            block = blockchain.get_block(session, block_id)
            block = block.to_dict()
        except BlockError as e:
            log.error(f'v1_block_get error [0]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except BlockchainError as e:
            log.error(f'v1_block_get error [1]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_block_get error [2]: {e!r}')
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()

    response = {
        'status': 'success',
        'block': block,
    }

    return web.json_response(response)


@routes.post('/v1/block/get-range')
async def v1_block_get_blocks_range(request):
    data = await request.json()
    start = data.get('start', 0)
    end = data.get('end', None)
    is_reversed = data.get('is_reversed', False)

    async with session_lock:
        session = Session()

        try:
            blocks = blockchain.get_blocks_range(session, start, end, is_reversed)
            blocks = [b.to_dict() for b in blocks]
            n_blocks = blockchain.get_n_blocks(session)
        except BlockError as e:
            log.error(f'v1_block_get_blocks_range error [0]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except BlockchainError as e:
            log.error(f'v1_block_get_blocks_range error [1]: {e!r}')
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_block_get_blocks_range error [2]: {e!r}')
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()

    response = {
        'status': 'success',
        'blocks': blocks,
        'n_blocks': n_blocks,
    }

    return web.json_response(response)


@routes.post('/v1/block/add')
async def v1_block_add(request):
    # NOTE: this is where mined blocks are submitted
    data = await request.json()
    block = data['block']
    
    # create block from dict
    try:
        block = Block.from_dict(block)
        log.warn(f'v1_block_add block: {block}')
    except BlockError as e:
        log.error(f'v1_block_add error [0]: {e!r}')
        response = {'status': 'error', 'message': str(e)}
        return web.json_response(response)
    except Exception as e:
        log.error(f'v1_block_add error [1]: {e!r}')
        response = {'status': 'error', 'message': 'system error'}
        return web.json_response(response)

    # add block
    async with session_lock:
        session = Session()
        
        try:
            blockchain.add_block(session, block)
            session.commit()
        except BlockchainError as e:
            log.error(f'v1_block_add error [2]: {e!r}')
            session.rollback()
            response = {'status': 'error', 'message': str(e)}
            return web.json_response(response)
        except Exception as e:
            log.error(f'v1_block_add error [3]: {e!r}')
            session.rollback()
            response = {'status': 'error', 'message': 'system error'}
            return web.json_response(response)
        finally:
            session.close()
            session = None

    response = {'status': 'success'}
    return web.json_response(response)

#
# sync difficulty
#
async def sync_difficulty():
    log.info('Started sync difficulty')

    async with ClientSession() as client_session:
        while True:
            # difficulty
            url = f'{Config.COORDINATOR}/v1/difficulty'
            data = {}

            try:
                async with client_session.post(url, json=data) as res:
                    data = await res.json()
                    # log.debug(data)
            except Exception as e:
                log.error(e)
                await asyncio.sleep(10.0)
                continue

            if data['status'] == 'error' or 'difficulty' not in data:
                log.warn('could not get difficulty, retrying...')
                await asyncio.sleep(10.0)
                continue

            difficulty = data['difficulty']

            if difficulty != blockchain.difficulty:
                log.warn(f'old difficulty: {blockchain.difficulty}')
                log.warn(f'new difficulty: {difficulty}')
                blockchain.set_difficulty(difficulty)

            await asyncio.sleep(10.0)

    log.info('Stopped sync difficulty')

#
# sync blockchain
#
async def sync_blockchain():
    log.info('Begin blockchain sync')

    # get last known block from local blockchain
    async with session_lock:
        session = Session()
        last_block = blockchain.get_last_block(session)
        session.close()

    if last_block:
        start = last_block.height + 1
    else:
        start = 0

    # sync with coordinator node
    async with ClientSession() as client_session:
        while True:
            url = f'{Config.COORDINATOR}/v1/block/get-range'
            data = {'start': start}

            try:
                async with client_session.post(url, json=data) as res:
                    data = await res.json()
                    # log.debug(data)
            except Exception as e:
                log.error(e)
                await asyncio.sleep(10.0)
                continue

            if data['status'] == 'error' or 'blocks' not in data:
                # raise Blockchain('could not sync with blockchain')
                log.warn('could not sync with blockchain, retrying...')
                await asyncio.sleep(10.0)
                continue

            try:
                blocks = data['blocks']
                blocks = [Block.from_dict(b) for b in blocks]
            except BlockError as e:
                # raise Block('could not create block')
                log.warn('could not create block, retrying...')
                await asyncio.sleep(10.0)
                continue
            except Exception as e:
                log.warn('could not create block, retrying...')
                await asyncio.sleep(10.0)
                continue

            # add blocks to local blockchain
            async with session_lock:
                session = Session()

                try:
                    blockchain.add_blocks(session, blocks, check_difficulty=False)
                    session.commit()
                except BlockchainError as e:
                    session.rollback()
                    # raise BlockchainError(e)
                    log.warn(f'could not add blocks to local blockchain, retrying...')
                    await asyncio.sleep(10.0)
                    continue
                except Exception as e:
                    session.rollback()
                    # raise BlockchainError(e)
                    log.warn(f'could not add blocks to local blockchain, retrying...')
                    await asyncio.sleep(10.0)
                    continue
                finally:
                    session.close()

            # get last known block from local blockchain
            async with session_lock:
                session = Session()
                last_block = blockchain.get_last_block(session)
                session.close()

            start = last_block.height + 1
            await asyncio.sleep(5.0)

    log.info('End blockchain sync')


#
# mine blocks
#
async def mine_blocks():
    log.info('Started mining')

    async with ClientSession() as client_session:
        while True:
            # unconfirmed transactions
            url = f'{Config.COORDINATOR}/v1/unconfirmed-transaction/get-range'
            # data = {'start': 0, 'end': 1000}
            data = {'start': 0, 'end': 200}

            try:
                async with client_session.post(url, json=data) as res:
                    data = await res.json()
                    log.debug(f'fetched n_unconfirmed_transactions {data["n_unconfirmed_transactions"]!r}')
            except Exception as e:
                log.error(f'mine_blocks error [0]: {e!r}')
                log.warn(f'mine_blocks data [0]: {data!r}')
                await asyncio.sleep(10.0)
                continue

            if data['status'] == 'error' or 'unconfirmed_transactions' not in data:
                log.warn('could not get unconfirmed transactions, retrying...')
                await asyncio.sleep(10.0)
                continue

            log.debug(f'unconfirmed_transactions: {data["unconfirmed_transactions"]!r}')

            # build transactions
            transactions = []

            async with session_lock:
                session = Session()

                for n in data['unconfirmed_transactions']:
                    # filter bad transactions
                    sender_address = n['sender_address']
                    recipient_address = n['recipient_address']

                    if sender_address:
                        if not blockchain.is_valid_address(sender_address):
                            log.warn(f'skipping bad sender address {sender_address!r}')
                            continue

                        confirmed_balance = blockchain._get_address_info_confirmed_balance(session, sender_address)
                        transfer_amount = n['amount'] + n['fee']

                        if confirmed_balance < transfer_amount:
                            log.warn(f'not enough funds, from sender address {sender_address!r} trying to send {transfer_amount}, but balance is {confirmed_balance}: {n!r}')
                            continue

                    if not blockchain.is_valid_address(recipient_address):
                        log.warn(f'skipping bad recipient address {recipient_address!r}')
                        continue

                    # transaction
                    tx = Transaction.from_dict(n)
                    transactions.append(tx)

                session.close()
                session = None

            # log.debug(f'transactions: {transactions!r}')

            # check balances
            # skip transactions which do not have enough funds on sender_address
            addresses = set([tx.sender_address for tx in transactions if tx.sender_address])
            
            async with session_lock:
                session = Session()
                
                addresses_balances = {
                    # a: blockchain.get_address_info(session, a)['confirmed_balance']
                    a: blockchain._get_address_info_confirmed_balance(session, a)
                    for a in addresses
                }

                session.close()

            _transactions = []

            for tx in transactions:
                confirmed_balance = addresses_balances[tx.sender_address]

                if confirmed_balance < (tx.amount + tx.fee):
                    log.warn(f'not enough as balance, confirmed_balance: {confirmed_balance!r}, amount: {tx.amount!r}, fee: {tx.fee}')
                    continue
                
                confirmed_balance -= (tx.amount + tx.fee)
                addresses_balances[tx.sender_address] = confirmed_balance
                _transactions.append(tx)

            transactions = _transactions
            
            # calculate allowed_reward_amount
            allowed_reward_amount = blockchain.reward_amount

            for tx in transactions:
                allowed_reward_amount += tx.fee

            # reward transaction
            reward_transaction = Transaction(
                version='1.0',
                id_=Transaction.gen_random_id(),
                time_=Transaction.get_time_now(),
                sender_address=None,
                recipient_address=Config.MINER_ADDRESS,
                sender_public_key=None,
                amount=allowed_reward_amount,
                fee=0,
                signature=None,
                hash_=None,
                check=False,
            )

            reward_transaction.hash = reward_transaction.calc_hash()
            transactions = [reward_transaction] + transactions

            # previous block
            async with session_lock:
                session = Session()

                try:
                    prev_block = blockchain.get_last_block(session)
                except Exception as e:
                    log.warn('could not get previous block, skipping...')
                    await asyncio.sleep(5.0)
                    continue
                finally:
                    session.close()

            # create block
            block = Block(
                version='1.0',
                height=(prev_block.height + 1) if prev_block else 0,
                id_=Block.gen_random_id(),
                prev_hash=prev_block.hash if prev_block else None,
                time_=Block.get_time_now(),
                transactions=transactions,
                merkle_root=None,
                difficulty=blockchain.difficulty,
                nonce=None,
                hash_=None,
                check=False,
            )

            # mine
            log.debug(f'block mining beginning: {block}')
            block.mine()
            log.debug(f'block mining finihed: {block}')

            # submit just mined block
            try:
                status = await blockchain.submit_block(block)
            except BlockchainError as e:
                log.warn('unsuccessful block submission [0], sleeping...')
                log.error(e)
                await asyncio.sleep(30.0)
                continue
            except Exception as e:
                log.warn('unsuccessful block submission [1], sleeping...')
                log.error(e)
                await asyncio.sleep(30.0)
                continue

            if not status:
                log.warn('unsuccessful block submission [2], sleeping...')
                log.error(e)
                await asyncio.sleep(30.0)
                continue

            await asyncio.sleep(5.0)

    log.info('Stopped mining')


# genesis block
def create_genesis_block():
    session = Session()
    q = session.query(BlockModel)
    c = q.count()

    if c > 0:
        log.warn('genesis block exists')
        return

    log.warn('creating genesis block because it does not exist')
    
    # genesis addresses and amounts
    genesis_address_amount = [
        ['Jc5024e763ea2eeb0e68e44152d895fca4f5f373f60e65bf9364330cbe5517632', 795920000000],
        ['J5eb72193c9cdbdb14924edbf95bf88e018e93f5f9defa610c6f9a54dc0bb4da8', 811200000000],
        ['J1866de96453ea664e916fd04484dffe6c2533dede299c5aec9c538f13ee3d0ce', 818399999999],
        ['Jb2312524afedfe48fff9b49a24b413ae0717402500c499ead0005af6f6315c4d', 799760000000],
        ['J838c007aa820b6772b1c092adfaf40fc2b21d6f54f20a9c0e34a619c01a1881f', 809600000000],
        ['Je5eea4e6a1269f3975ccd16701f12809e399eb5ecb8d1ddc64baf6a627e73c62', 754240000000],
        ['Jc1ff7861000a8506e537fc554b1cdb2498bb0b2a8ce70a4548b17acd62a09725', 751360000000],
        ['Ja33ae09819c841bc3c8ea0ce8830a65b545241527f4c2fc81b251799ac61cc98', 858000000000],
        ['Jbe8d87881bfcacd3b371fb6670469cb4014451c8f73e944bf130cf11bd966fda', 798240000000],
        ['J2181b2a1d5ed26d33a449fd40574458e14c1f653bdeda07c2424e7e14abfab4f', 742080000000],
        ['J83b2d1b0cf0f9b7c94e0ec7e25918d82c72604c8fcc3c1fd7014e7aa60a2ee42', 826160000000],
        ['Jd7781f58e3c653fd708e65878a7d19db6379a9e677793f4b2fb4a4558bd95690', 789680000000],
        ['Jed88d5cbfbcb8d383ad2f890e378facddf31254ee3d6dbfc355b917132b45c6f', 730640000000],
        ['Je0df36e6f3709a344ab2c0f01799169ce7b9d7dc66906bffb01531a2d6f015d3', 793600000000],
        ['Jd602639c78a8840efb422a11af881505a92ec7143bd4338b6f8c1fa865a4ab2d', 849119999999],
        ['J45d42264ec7a3e4e806f20d70fbe91188dc269ddb0fdce6c42de86395c6ac818', 724480000000],
        ['J300055aadb2454fb841135efa17892c6c6148635d4f41ee6305911de8cfd2155', 878560000000],
        ['J1b1db8b140d771ac0f6d78af40cfa3c606c44756635bfb631df0b6efe35e93ae', 871840000000],
        ['Je326b489aba0db2e47c41baebddc68a464bc3ba46f627477b9f50b8407f76e97', 804320000000],
        ['J6e8df54dc3b032235c74c1034908cb70c7b6525c09678f2898bb5cc669ead0ee', 792800000002],
    ]

    # check if distributed initial coin amonuts total 16M
    assert sum([n[1] for n in genesis_address_amount]) == 16_000_000_000_000
    genesis_transactions = []

    for address, amount in genesis_address_amount:
        # genesis transactions do not have sender
        # so they are not required to be signed
        # similiar to reward transactions for mined blocks
        tx = Transaction(
            version='1.0',
            id_=Transaction.gen_random_id(),
            time_='2018-06-01T12:00:00.000000',
            sender_address=None,
            recipient_address=address,
            sender_public_key=None,
            amount=amount,
            fee=0,
            signature=None,
            hash_=None,
            check=False,
        )

        tx.hash = tx.calc_hash()
        genesis_transactions.append(tx)

    genesis_block = Block(
        version='1.0',
        height=0,
        id_=Block.gen_random_id(),
        prev_hash=None,
        time_='2018-06-01T12:00:00.000000',
        transactions=genesis_transactions,
        merkle_root=None,
        difficulty=blockchain.difficulty,
        nonce=None,
        hash_=None,
        check=False,
    ).mine()

    blockchain.add_block(session, genesis_block)
    session.commit()
    session.close()
    log.warn('genesis block created')


# create genesis block
if Config.GENERATE_GENESIS_BLOCK:
    create_genesis_block()

# check mining address
if not Config.MINER_ADDRESS:
    if os.path.exists('miner_key.json'):
        with open('miner_key.json', 'r') as f:
            data = json.load(f)
    else:
        sk, pk, a = crypto.generate_private_public_address_key()

        data = {
            'private_key': sk,
            'public_key': pk,
            'address': a,
        }

        with open('miner_key.json', 'w') as f:
            json.dump(data, f)

    Config.MINER_ADDRESS = data['address']

# sync difficulty
if Config.NO_SYNC:
    log.warn('Skipping difficulty sync')
else:
    asyncio.ensure_future(sync_difficulty())

# upon start of node, first sync node with current blockchain, or skip it
if Config.NO_SYNC:
    log.warn('Skipping blockchain sync')
else:
    asyncio.ensure_future(sync_blockchain())

# skip mining
if Config.NO_MINE:
    log.warn('Skipping mining')
else:
    asyncio.ensure_future(mine_blocks())

# web app
app = web.Application()
app.add_routes(routes)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

# Configure CORS on all routes.
for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    web.run_app(app, host=Config.HOST, port=Config.PORT)
