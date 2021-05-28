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

import Conf.conf
from Models.MyModel import DBSession, OperateLog
from sqlalchemy.sql import func


def listen_data():
    session = DBSession()
    print "start to listen..."
    # 获取当前最新id
    id = session.query(func.max(OperateLog.id)).first()[0]
    print "id", id

    while True:
        try:
            # 每十秒取最新时间段内的数据
            time.sleep(10)
            # 每次查询前更新session缓存
            session.commit()
            res = session.query(OperateLog).filter(OperateLog.id > id).all()
            print time.strftime("%Y-%m-%d %H:%M:%S"), "新入数据:%d" % len(res)
            id = id + len(res)
            print "id", id

            for row in res:
                print row.to_dict()
                Conf.conf.task_queue.put(row.task_id)
                print Conf.conf.task_queue.queue
                # print row.user.user_name
                # print row.operate_type.type_name
        except Exception as e:
            print traceback.format_exc()


if __name__ == '__main__':
    listen_data()
