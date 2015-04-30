# -*- coding: utf-8 -*-
__author__ = 'Kinslayer'

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Package(Base):
    __tablename__ = u'package'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_type = Column(String(8), server_default=u'WX')
    body = Column(String(128), nullable=False)
    attach = Column(String(128))
    partner = Column(String(64), nullable=False)
    out_trade_no = Column(String(32), nullable=False)
    total_fee = Column(Integer, nullable=False, server_default=u'0')
    fee_type = Column(Integer, server_default=u'1')
    notify_url = Column(String(255), nullable=False)
    spbill_create_ip = Column(String(15), nullable=False)
    time_start = Column(String(14))
    time_expire = Column(String(14))
    transeport_fee = Column(Integer)
    product_fee = Column(Integer)
    goodstag = Column(String(16))
    input_charset = Column(String(16), nullable=False, server_default=u'GBK')
    create_time = Column(String(14), nullable=False)

if __name__ == '__main__':
    import settings
    metadata.create_all(settings.engine)

