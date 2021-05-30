# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-28 20:31
IDE: PyCharm
"""
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import logging

logging.basicConfig()

import random
import traceback
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from Conf.conf import task_queue, workers_num
from utils.mylogger import get_logger
from Models.MyModel import DBSession, OperateLog, CheckRes

logger = get_logger("check")

executor = ThreadPoolExecutor(max_workers=workers_num)

session = DBSession()


def check(task_id):
    """
    流程检测

    :param task_id: 卷宗ID
    :return: 检测结果
    """
    logger.info("start check task_id:%s" % task_id)
    try:
        # 获取该卷宗的所有关联日志
        session.commit()
        res = session.query(OperateLog).filter(OperateLog.task_id == task_id).all()
        assert len(res), "卷宗 %s 无法获取关联日志." % task_id

        # 关联日志
        log_list = []
        # 操作列表
        operate_list = []
        # 文件操作
        file_map = {}
        # 错误日志
        error_list = []

        for row in res:
            log = {
                "id": row.id,
                "task_id": row.task_id,
                "type": row.type,
                "log_id": row.log_id,
                "file_id": row.file_id,
                "datetime": row.datetime,
                "user_name": row.user.user_name,
                "type_name": row.operate_type.type_name,
                "error": "--"
            }
            log_list.append(log)
            operate_list.append(row.type)
            # 同一file_id的操作放在一个key下的列表中
            if log["file_id"]:
                if not file_map.get(log["file_id"]):
                    file_map[log["file_id"]] = []
                file_map[log["file_id"]] += [row.type]

        log_list_len = len(log_list)
        logger.info("卷宗 task_id:%s 包含 %d 日志" % (task_id, log_list_len))
        logger.info("卷宗 task_id:%s 的 操作列表如下:" % task_id)
        logger.info(operate_list)

        # ----------------------------检测逻辑----------------------------

        # >>>>>>>>>>>>>>>>>1. 检测文件操作完整性
        # r1: IF 存在文件（file_id）AND [未通过清晰度检查（E15） OR 完整性检查（E16） OR 一致性检查（E17）]
        # THEN 提取上传该文件的日志，输出卷宗号(task_id)，时间，哪步检查未通过等
        logger.info(">>>>>>>>>>>>>>>>>1. 检测文件操作完整性")
        logger.info("卷宗 %s 存在 %d 个文件" % (task_id, len(file_map)))
        for file_id in file_map:
            b, r = compare_list(file_map[file_id], ["E15", "E16", "E17"])
            # 不包含且存在缺少项
            if not b and r:
                for t in r:
                    error_list.append(build_err_json({
                        "task_id": task_id,
                        "error": "文件 %s 缺少操作%s" % (file_id, t)
                    }))

        # >>>>>>>>>>>>>>>>>2. 检测操作头
        # r4: IF 第一个操作为创建卷宗（E1） THEN 正确
        logger.info(">>>>>>>>>>>>>>>>>2. 检测操作头")
        if log_list[0].get("type") != "E1":
            log_list[0]["error"] = "第一个操作:{type},应为创建卷宗（E1）".format(**log_list[0])
            error_list.append(build_err_json(log_list[0]))

        # >>>>>>>>>>>>>>>>>3. 检测操作间
        logger.info(">>>>>>>>>>>>>>>>>3. 检测操作间")
        for index in range(1, log_list_len - 1):
            log = log_list[index]
            next_log = log_list[index + 1]
            error = ""

            # r5: IF 创建卷宗（E1）
            # AND [上传文件（E9） OR 阅读文件（E10）OR 修改文件（E11）OR 重新上传（E12）OR 删除文件（E13）] THEN 正确
            if log["type"] == "E1":
                if next_log["type"] not in ("E9", "E10", "E11", "E12", "E13"):
                    error = "流程错误,%s->%s" % (log["type"], next_log["type"])

            # r8: IF 移送卷宗（E3） THEN 接收卷宗（E4）正确
            if log["type"] == "E3":
                if next_log["type"] != "E4":
                    error = "流程错误,%s->%s" % (log["type"], next_log["type"])

            # r9: IF 接收卷宗（E4）
            # THEN  [上传文件（E9） OR 阅读文件（E10）OR 修改文件（E11）OR 重新上传（E12）OR 删除文件（E13）]
            # r14: IF接收卷宗（E4）
            # THEN 卷宗权限管理（E5） OR 模板选择（E6）OR 移送下一办理人（E18）
            if log["type"] == "E4":
                if next_log["type"] not in ("E5", "E6", "E18", "E9", "E10", "E11", "E12", "E13"):
                    error = "流程错误,%s->%s" % (log["type"], next_log["type"])

            # r6: IF [上传文件（E9） OR 阅读文件（E10）OR 修改文件（E11）OR 重新上传（E12）OR 删除文件（E13）]
            # THEN [上传文件（E9） OR 阅读文件（E10）OR 修改文件（E11）OR 重新上传（E12）OR 删除文件（E13）]
            # r7: IF [上传文件（E9） OR 阅读文件（E10）OR 修改文件（E11）OR 重新上传（E12）OR 删除文件（E13）]
            # THEN 移送卷宗（E3）
            # r10: IF [上传文件（E9） OR 阅读文件（E10）OR 修改文件（E11）OR 重新上传（E12）OR 删除文件（E13）]
            # THEN 不受理案件（E19） OR 受理案件（E20）
            # r13: IF [上传文件（E9） OR 阅读文件（E10）OR 修改文件（E11）OR 重新上传（E12）OR 删除文件（E13）]
            # THEN 卷宗权限管理（E5） OR 模板选择（E6）OR 移送下一办理人（E18）
            if log["type"] in ("E9", "E10", "E11", "E12", "E13"):
                if next_log["type"] not in ("E3", "E9", "E10", "E11", "E12", "E13", "E19", "E20", "E5", "E6", "E18"):
                    error = "流程错误,%s->%s" % (log["type"], next_log["type"])

            # r12: IF受理案件（E20）
            # THEN [上传文件（E9） OR 阅读文件（E10）OR 修改文件（E11）OR 重新上传（E12）OR 删除文件（E13）]
            if log["type"] == "E20":
                if next_log["type"] not in ("E9", "E10", "E11", "E12", "E13"):
                    error = "流程错误,%s->%s" % (log["type"], next_log["type"])

            # r15: IF卷宗权限管理（E5） OR 模板选择（E6）OR 移送下一办理人（E18）
            # THEN 移送卷宗（E3）
            if log["type"] in ("E5", "E6", "E18"):
                if next_log["type"] != "E3":
                    error = "流程错误,%s->%s" % (log["type"], next_log["type"])

            if error:
                log["error"] = error
                error_list.append(build_err_json(log))

        # >>>>>>>>>>>>>>>>>4. 检测操作尾
        # r16: IF 最后一个操作为卷宗结案（E8） THEN 正确
        logger.info(">>>>>>>>>>>>>>>>>4. 检测操作尾")
        if log_list[-1].get("type") != "E8":
            log_list[-1]["error"] = "最后一个操作:{type},应为卷宗结案（E8）".format(**log_list[-1])
            error_list.append(build_err_json(log_list[-1]))

        return error_list
    except Exception as e:
        logger.error(traceback.format_exc())


def callback(future):
    """
    check 线程的完成时回调方法 结果写回数据库

    :param future: ThreadPoolExecutor 实例
    """
    error_list = future.result()
    if error_list:
        logger.info("start to insert %d error log." % len(error_list))
        try:
            # 批量写
            session.execute(
                CheckRes.__table__.insert(),
                error_list
            )
            session.commit()
            logger.info("insert success.")
        except Exception as e:
            logger.error(traceback.format_exc())


def tasks_assign():
    """
    1.持续监听 task_queue 的新入任务

    2.为任务分配执行线程
    """
    while True:
        try:
            job_list = []
            if task_queue.qsize():
                logger.info("task_queue.qsize():%d" % task_queue.qsize())
                for _ in range(task_queue.qsize()):
                    x = task_queue.get_nowait()
                    job_list.append(x)
                for id in job_list:
                    future = executor.submit(check, id)
                    future.add_done_callback(callback)
            time.sleep(2)
        except Exception as e:
            logger.error(traceback.format_exc())


def build_err_json(log):
    """
    构建 CheckRes 错误日志格式

    :return: json
    """
    return {
        "task_id": log.get("task_id"),
        "content": log.get("error"),
        "operate_log_id": log.get("id"),
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S")
    }


def compare_list(main, must):
    """
    1.判断 must 列表是否是 main 的子集,即必须项都已完成

    2.不是子集时，返回 main 中缺少的操作

    :param main: 已经发生的操作集
    :param must: 必须包含的操作集
    :return: bool,[]
    """
    if not isinstance(main, list) or not isinstance(must, list):
        return False, []
    # 包含,子集
    if set(must) <= set(main):
        return True, []
    # 缺失的操作集
    miss_list = [x for x in must if x not in main]
    return False, miss_list


if __name__ == '__main__':
    # tasks_assign()
    # content = "发现卷宗 {task_id} 在 {datetime},用户 {user_name} 的操作 {type}({type_name}) 存在错误:{error}"
    # log = {
    #     "task_id": "row.task_id",
    #     "type": "E1",
    #     "log_id": "row.log_id",
    #     "file_id": "row.file_id",
    #     "datetime": "row.datetime",
    #     "user_name": "ueser_1",
    #     "type_name": "E1 name",
    #     "error": None
    # }
    # print content.format(**log)

    ls = []
    for i in range(100):
        log = {
            "task_id": "%d" % random.randint(1, 50),
            "error": "this is error %d" % i
        }
        ls.append(build_err_json(log))
    # 批量写
    session.execute(
        CheckRes.__table__.insert(),
        ls
    )
    session.commit()
