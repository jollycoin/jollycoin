 
class Config:
    '''
    Global config used in different parts of code. It is not thread-safe.
    '''
    HOST = '0.0.0.0'
    PORT = 8080
    DB = 'sqlite:///node.db'
    COORDINATOR = 'https://api.jollycoin.org'
    NO_SYNC = False
    NO_MINE = False
    GENERATE_GENESIS_BLOCK = False
    MINER_ADDRESS = None