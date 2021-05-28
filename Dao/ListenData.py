# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-27 10:54
IDE: PyCharm
"""
import random
import time
import traceback
import uuid

from Conf.conf import task_queue, listen_interval
from Models.MyModel import DBSession, OperateLog
from sqlalchemy.sql import func
from utils.mylogger import get_logger

logger = get_logger("listen")


def listen_data():
    """
    1. 持续监听mysql入库日志
    2. 将其中 完成标识的 任务放入 task_queue队列
    """
    session = DBSession()
    logger.info("start to listen...")
    # 获取当前最新id
    id = session.query(func.max(OperateLog.id)).first()[0]
    logger.debug("从 id 开始: %d" % id)

    while True:
        try:
            # 每十秒取最新时间段内的数据
            time.sleep(listen_interval)
            # 每次查询前更新session缓存
            session.commit()
            res = session.query(OperateLog).filter(OperateLog.id > id).all()
            logger.debug("新入数据:%d" % len(res))
            id = id + len(res)
            logger.debug("当前id: %d" % id)

            for row in res:
                print row.to_dict()
                task_queue.put(row.task_id)
                print task_queue.queue
                # print row.user.user_name
                # print row.operate_type.type_name
        except Exception as e:
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    listen_data()
