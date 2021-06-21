# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-27 10:54
IDE: PyCharm
"""
import json
import sys
import uuid

reload(sys)
sys.setdefaultencoding('utf8')
import random
import time
import traceback

from Conf import conf
from Models.MyModel import DBSession, OperateLog, CheckRule
from sqlalchemy.sql import func
from utils.mylogger import get_logger
from RuleInit import time_diff

logger = get_logger("listen")
session = DBSession()


def listen_data():
    """
    1.持续监听mysql入库日志

    2.将其中 完成标识的 任务放入 task_queue队列
    """
    session = DBSession()
    logger.info("start to listen...")
    # 获取当前最新id
    id = session.query(func.max(OperateLog.id)).first()[0]
    logger.info("从 id 开始: %d" % id)

    while True:
        try:
            # 每十秒取最新时间段内的数据
            time.sleep(conf.listen_interval)
            # 每次查询前更新session缓存
            session.commit()
            res = session.query(OperateLog).filter(OperateLog.id > id).all()
            if len(res):
                logger.info("新入数据:%d" % len(res))
                id = id + len(res)
                logger.info("当前id: %d" % id)

            for row in res:
                if row.type == "E9":
                    logger.info("卷宗 %s 结束,放入预检测队列" % row.task_id)
                    conf.task_queue.put(row.task_id)
                    # print task_queue.queue
                    # print row.user.user_name
                    # print row.operate_type.type_name
        except Exception as e:
            logger.error(traceback.format_exc())


def check_task_map():
    while True:
        for task_id in conf.task_map:
            time1 = conf.task_map[task_id]
            time2 = time.strftime("%Y-%m-%d %H:%M:%S")
            # 超时
            if not time_diff(time1, time2, conf.overtime):
                # 修改前加线程锁
                conf.task_map_lock.acquire()
                del conf.task_map[task_id]
                conf.task_map_lock.release()
                logger.info("卷宗 %s 超时,放入预检测队列" % task_id)
                conf.task_queue.put(task_id)
        time.sleep(60)


def build_log_json(data):
    """
    构建 OperateLog 日志格式

    :param data: [{},{}...]
    :return: [{},{}...]
    """
    res = []
    for log in data:
        if log.get("task_id"):
            res.append({
                "task_id": log.get("task_id", ""),
                "log_id": log.get("log_id", str(uuid.uuid4())),
                "file_id": log.get("file_id", ""),
                "type": log.get("type", ""),
                "user_id": log.get("user_id", 0),
                "datetime": log.get("datetime", time.strftime("%Y-%m-%d %H:%M:%S")),
            })
    assert res, "no valid data."
    return res


def log_parse(data):
    """
    1.监听 并 入库日志

    2.将其中 完成标识的 任务放入 task_queue队列
    """
    try:
        logs = build_log_json(data)

        logger.info("get logs:%s" % len(logs))
        # save log 批量写
        session.execute(
            OperateLog.__table__.insert(),
            logs
        )
        session.commit()
        logger.info("insert success.")

        end_flag = conf.check_rules.get("1", {}).get("tail", [])
        # 修改前加线程锁
        conf.task_map_lock.acquire()
        for log in logs:
            # 更新时间
            conf.task_map[log["task_id"]] = log["datetime"]
            # 如果设定了结束状态标识
            if end_flag:
                if log["type"] in end_flag:
                    del conf.task_map[log["task_id"]]
                    logger.info("卷宗 %s 结束,放入预检测队列" % log["task_id"])
                    conf.task_queue.put(log["task_id"])
                    # print task_queue.queue
                    # print row.user.user_name
                    # print row.operate_type.type_name
        conf.task_map_lock.release()

    except Exception, e:
        traceback.print_exc()
        logger.error(traceback.format_exc())




if __name__ == '__main__':
    res = rules_init()
    print json.dumps(res, ensure_ascii=False, indent=4)
