# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-06-05 12:09
IDE: PyCharm
"""
import traceback
from datetime import datetime

from Models.MyModel import DBSession, CheckRule
from utils.mylogger import get_logger

logger = get_logger("rule_init")
session = DBSession()


def rules_init():
    """
    初始化加载所有检测包到 check_rules
    """
    logger.info("load check rule to check_rules.")
    try:
        sess = DBSession()
        sess.commit()

        check_rules = {
            "1": {
                "head": [],
                "tail": []
            },
            "2": [],
            "3": [],
            "4": [],
            "5": [],
        }

        rules = sess.query(CheckRule).all()
        assert len(rules), "无检测包."

        for rule in rules:
            # 头尾
            if rule.rule_type == 1:
                check_rules["1"]["head"] += rule_parse(rule.head)
                check_rules["1"]["tail"] += rule_parse(rule.tail)
            # 完整
            elif rule.rule_type == 2:
                check_rules["2"] += rule_parse(rule.overall_include)
            # 文件
            elif rule.rule_type == 3:
                check_rules["3"] += rule_parse(rule.file_include)
            # 顺序
            elif rule.rule_type == 4:
                check_rules["4"].append({
                    "context_pre": rule_parse(rule.context_pre),
                    "context_back": rule_parse(rule.context_back),
                })
            # 顺序
            elif rule.rule_type == 5:
                check_rules["5"].append({
                    "part": rule_parse(rule.part),
                    "partial_time": rule.partial_time,
                })

        # 去重
        check_rules["1"]["head"] = list(set(check_rules["1"]["head"]))
        check_rules["1"]["tail"] = list(set(check_rules["1"]["tail"]))
        check_rules["2"] = list(set(check_rules["2"]))
        check_rules["3"] = list(set(check_rules["3"]))
        return check_rules
    except Exception as e:
        traceback.print_exc()
        logger.error(traceback.format_exc())


def rule_parse(rule):
    """
    将 “E1,E2...” 解析为 list
    """
    if not isinstance(rule, basestring):
        return []
    rule = rule.replace(' ', '')
    res = rule.split(",")
    res = [x for x in res if x]
    return res


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
