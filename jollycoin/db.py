from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import create_engine, event, exc
from sqlalchemy import Column, Index, Boolean, BigInteger, Float, Numeric, String, DateTime, Text
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import Pool

from .config import Config


@event.listens_for(Pool, 'checkout')
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()
    
    cursor.close()


# try:
#     engine = create_engine(
#         Config.DB,
#         isolation_level='REPEATABLE_READ',
#     )
# except Exception as e:
#     engine = create_engine(
#         Config.DB,
#         isolation_level='SERIALIZABLE',
#     )

engine = create_engine(
    Config.DB,
    isolation_level='REPEATABLE_READ',
)

Session = sessionmaker(bind=engine)


class StringLike(TypeDecorator):
    impl = String


    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        
        return None


    def process_result_value(self, value, dialect):
        if value is not None:
            return int(value)

        return value


class _Base:
    created_at = Column(DateTime(), default=datetime.utcnow)
    updated_at = Column(DateTime(), onupdate=datetime.utcnow)


    def to_dict(model_instance, query_instance=None):
        if hasattr(model_instance, '__table__'):
            return {
                c.name: getattr(model_instance, c.name)
                for c in model_instance.__table__.columns
            }
        else:
            cols = query_instance.column_descriptions
            
            return {
                cols[i]['name']: model_instance[i]
                for i in range(len(cols))
            }


    @classmethod
    def from_dict(cls, dict, model_instance):
        for c in model_instance.__table__.columns:
            setattr(model_instance, c.name, dict[c.name])


Base = declarative_base(cls=_Base)


class TransactionModel(Base):
    __tablename__ = 'transaction_v1'
    block_id = Column(String(64), default=None, index=True)
    confirmed = Column(Boolean, default=False, index=True)

    version = Column(String(8))
    id = Column(String(64), primary_key=True)
    time = Column(String(64))
    time_dt = Column(DateTime, index=True)
    time_ts = Column(BigInteger, index=True)
    sender_address = Column(String(65), index=True)
    recipient_address = Column(String(65), index=True)
    sender_public_key = Column(String(256))
    amount = Column(StringLike(128))
    fee = Column(StringLike(128))
    signature = Column(String(256))
    hash = Column(String(64))
    message = Column(Text)


class BlockModel(Base):
    __tablename__ = 'block_v1'
    version = Column(String(8))
    height = Column(BigInteger, index=True, unique=True)
    id = Column(String(64), primary_key=True)
    prev_hash = Column(String(64))
    time = Column(String(64))
    time_dt = Column(DateTime, index=True)
    time_ts = Column(BigInteger, index=True)
    transactions = Column(Text)
    merkle_root = Column(String(64))
    difficulty = Column(StringLike(128))
    nonce = Column(StringLike(128))
    hash = Column(String(64))
    message = Column(Text)


# create all tables
Base.metadata.create_all(engine)
