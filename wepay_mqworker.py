# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'Kinslayer'

import pika
import json
import logging
import logging.handlers
import traceback
import os
from sqlalchemy.exc import DataError
import time
ISOTIMEFORMAT='%Y-%m-%d %X'
print time.strftime( ISOTIMEFORMAT, time.localtime() )


import sys
import platform
from daemon import Daemon
from sqlalchemy.orm import sessionmaker
from models import Package
import utils
from contextlib import contextmanager
import settings


Session = sessionmaker(bind=settings.engine)

log = logging.getLogger('wepay_mqworker')

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def callback(ch, method, properties, body):
    try:
        log.info('Receive message = %s', body)
        adict = json.loads(body)
        mthd = adict['method']
        params = adict['params']
        if mthd == 'new_package':
            insert_package_to_db(params)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except (ValueError, DataError), ex:
        #因为出现一个非法订单, total_fee过大, 导致的队列阻塞
        errmsg = traceback.format_exc()
        log.error(errmsg)
        log.error("ignore this message because this message contains invalid data")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception, ex:
        errmsg = traceback.format_exc()
        log.error(errmsg)


def insert_package_to_db(params):
    assert isinstance(params, dict)
    if 'id' in params:  #去除不必要的id键值
        params.pop('id')
    pkg = utils.dict_to_obj(params, Package)
    with session_scope() as session:
        session.add(pkg)
        #session.flush()


def startTask():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='wepay_host_package_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='wepay_host_package_queue')
    channel.start_consuming()


class MyDaemonApp(Daemon):
    def run(self):
        startTask()


def linuxTask():
    daemon = MyDaemonApp('/tmp/wepay_host_package_wroker.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "usage: %s start|stop|restart" % sys.argv[0]
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)


def init_log(logger, file_name, log_level=logging.INFO):
    handler = logging.handlers.RotatingFileHandler(file_name,maxBytes=10*1024*1024,backupCount=5)
    formatter = logging.Formatter("[%(asctime)s] [%(filename)s]: %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger



if __name__ == '__main__':
    try:
        init_log(log, os.path.join(settings.logpath, 'mqworker.log'))
        log.info("mq worker start...")
        system = platform.system()
        if system == "Windows":
            DEBUG = True
            #startTask()
        elif system == "Linux":
            DEBUG = False
            linuxTask()
    except Exception, ex:
        errmsg = traceback.format_exc()
        log.error(errmsg)
        print errmsg
