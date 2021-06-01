# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-28 20:31
IDE: PyCharm
"""
import json
import sys
from datetime import datetime

from Dao.ListenData import rules_init

reload(sys)
sys.setdefaultencoding('utf8')
import logging

logging.basicConfig()

import random
import traceback
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from Conf import conf
from utils.mylogger import get_logger
from Models.MyModel import DBSession, OperateLog, CheckRes

logger = get_logger("check")

executor = ThreadPoolExecutor(max_workers=conf.workers_num)

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
        time.sleep(0.1)
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
                file_map[log["file_id"]].append(row.type)

        log_list_len = len(log_list)
        logger.info("卷宗 task_id:%s 包含 %d 日志" % (task_id, log_list_len))
        logger.info("卷宗 task_id:%s 的 操作列表如下:" % task_id)
        logger.info(operate_list)

        # ----------------------------检测逻辑----------------------------
        if not conf.check_rules:
            logger.info("当前没有检测规则.")
            return error_list

        # >>>>>>>>>>>>>>>>>1. 头尾检测
        logger.info(">>>>>>>>>>>>>>>>>1. 头尾检测")
        head = conf.check_rules.get("1", {}).get("head", [])
        tail = conf.check_rules.get("1", {}).get("tail", [])
        if head and log_list[0].get("type") not in head:
            log_list[0]["error"] = "头检测错误,第一个操作:%s,应为:%s" % (
                log_list[0].get("type"), head
            )
            error_list.append(build_err_json(log_list[0]))
        if tail and log_list[-1].get("type") not in tail:
            log_list[-1]["error"] = "尾检测错误,最后一个操作:%s,应为:%s" % (
                log_list[-1].get("type"), tail
            )
            error_list.append(build_err_json(log_list[-1]))

        # >>>>>>>>>>>>>>>>>2. 完整性检测
        logger.info(">>>>>>>>>>>>>>>>>2. 完整性检测")
        overall_include = conf.check_rules.get("2", [])
        if overall_include:
            b, r = compare_list(operate_list, overall_include)
            # 不包含且存在缺少项
            if not b and r:
                error_list.append(build_err_json({
                    "task_id": task_id,
                    "error": "完整性检测错误,缺少操作:%s" % r
                }))

        # >>>>>>>>>>>>>>>>>3. 文件检测
        logger.info(">>>>>>>>>>>>>>>>>3. 文件检测")
        logger.info("卷宗 %s 存在 %d 个文件" % (task_id, len(file_map)))
        file_include = conf.check_rules.get("3", [])
        if file_include:
            for file_id in file_map:
                b, r = compare_list(file_map[file_id], file_include)
                # 不包含且存在缺少项
                if not b and r:
                    error_list.append(build_err_json({
                        "task_id": task_id,
                        "error": "文件 %s 检测错误,缺少操作:%s" % (file_id, r)
                    }))

        # >>>>>>>>>>>>>>>>>4. 上下文顺序检测
        logger.info(">>>>>>>>>>>>>>>>>4. 上下文顺序检测")
        context = conf.check_rules.get("4", [])
        if context:
            for index in range(log_list_len - 1):
                log = log_list[index]
                next_log = log_list[index + 1]
                error = ""

                for each_ct in context:
                    context_pre = each_ct.get("context_pre", [])
                    context_back = each_ct.get("context_back", [])
                    if not context_pre or not context_back:
                        break

                    if log["type"] in context_pre and \
                            next_log["type"] not in context_back:
                        error = "上下文顺序检测错误,%s->%s" % (log["type"], next_log["type"])

                if error:
                    log["error"] = error
                    error_list.append(build_err_json(log))

        # >>>>>>>>>>>>>>>>>5. 局部时限检测
        logger.info(">>>>>>>>>>>>>>>>>5. 局部时限检测")
        part_info = conf.check_rules.get("5", [])
        if part_info:
            for each_part in part_info:
                part = each_part.get("part", [])
                partial_time = each_part.get("partial_time", 0)
                if part and partial_time > 0:
                    part_res = get_part(operate_list, part)
                    if part_res:
                        # 每一对局部首位 索引
                        for each_res in part_res:
                            pre_log = log_list[each_res[0]]
                            back_log = log_list[each_res[1]]
                            if not time_diff(back_log["datetime"], pre_log["datetime"], partial_time):
                                back_log["error"] = "局部时限检测错误,该操作超出设定时限:%dm" % partial_time
                                error_list.append(build_err_json(back_log))

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
            if conf.task_queue.qsize():
                logger.info("task_queue.qsize():%d" % conf.task_queue.qsize())
                for _ in range(conf.task_queue.qsize()):
                    x = conf.task_queue.get_nowait()
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


def time_diff(time1, time2, limit):
    """
    计算 两个时间差 是否在时限内
    """
    try:
        assert limit > 0, "limit value error."
        time_1_struct = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
        time_2_struct = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
        total_seconds = (time_2_struct - time_1_struct).total_seconds()
        minutes = int(total_seconds / 60)
        if minutes <= limit:
            return True
        return False
    except Exception, e:
        logger.error(traceback.format_exc())
        return False


def get_part(operate_list, part):
    """
    获取所有 操作列表中的符合条件的区域起点和结束 索引
    """
    try:
        res = []
        pre = part[0]
        back = part[1]
        # 先找到第一个元素的所有索引
        pre_index_list = [x for x in range(len(operate_list)) if operate_list[x] == pre]
        print "pre_index_list", pre_index_list
        if len(pre_index_list) == 0:
            return res
        # 末尾追加None,表示最后一次查找到列表尾巴
        pre_index_list.append(None)
        print "pre_index_list append", pre_index_list
        for i in range(len(pre_index_list) - 1):
            index1 = pre_index_list[i]
            index2 = pre_index_list[i + 1]
            r = list_find(operate_list, back, index1, index2)
            if r >= 0:
                res.append([index1, r])
        return res
    except Exception, e:
        traceback.print_exc()
        return []


def list_find(lt, target, start=None, stop=None):
    """
    list.index 方法在找不到元素时报ValueError
    """
    try:
        if start and not stop:
            res = lt.index(target, start)
        elif start:
            res = lt.index(target, start, stop)
        else:
            res = lt.index(target)
        return res
    except ValueError, e:
        return -1


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

    # lll = ["E3", "E2", "E4", "E3", "E5", "E10", "E3", "E7", "E4", "E4"]
    # print get_part(lll, ["E4", "E3"])

    conf.check_rules = rules_init()
    for err in check("1ab9d706-346e-4f41-a361-6d9961bdefcc"):
        print json.dumps(err, ensure_ascii=False)
