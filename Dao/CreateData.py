# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-27 10:44
IDE: PyCharm
"""
import random
import time
import traceback
import uuid

from Models.MyModel import DBSession, OperateLog, User, OperateType, CheckRule, RuleType


def create_log():
    """
    E1开始  E8结束
    """
    session = DBSession()

    task_id = str(uuid.uuid4())
    count = random.randint(10, 30)

    operate_list = (2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
    print "本次预计生成 %d 条数据" % count
    for i in range(count):
        log_id = str(uuid.uuid4())

        if i == 0:
            operate_type = "E1"
        elif i == count - 1:
            operate_type = "E8"
        else:
            operate_type = "E%d" % random.choice(operate_list)

        datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        user_id = random.randint(1, 3)
        file_id = str(uuid.uuid4()) if random.randint(1, 5) == 1 else ""
        val = (task_id, log_id, operate_type, datetime, user_id, file_id)
        try:
            new_data = OperateLog(task_id=task_id, log_id=log_id, file_id=file_id, type=operate_type, user_id=user_id,
                                  datetime=datetime)
            session.add(new_data)
            session.commit()
            time.sleep(random.randint(1, 3))
        except Exception as e:
            print traceback.format_exc()
            session.close()
            break
        else:
            print "mysql insert %d success:" % (i + 1), val

        session.close()


def create_user():
    session = DBSession()

    print "本次预计生成3条数据"
    for i in range(1, 4):
        user_id = i
        user_name = "user_%d" % i
        try:
            new_data = User(user_id=user_id, user_name=user_name)
            session.add(new_data)
            session.commit()
        except Exception as e:
            print traceback.format_exc()
            session.close()
            break
        else:
            print "mysql insert %d success:" % i

        session.close()


def create_type():
    session = DBSession()

    print "本次预计生成 30 条数据"
    for i in range(1, 31):
        operate_type = "E%d" % i
        type_name = "this is %s" % operate_type
        try:
            new_data = OperateType(type=operate_type, type_name=type_name)
            session.add(new_data)
            session.commit()
            time.sleep(random.randint(1, 3))
        except Exception as e:
            print traceback.format_exc()
            session.close()
            break
        else:
            print "mysql insert %d success:" % i

        session.close()


def create_ruletype():
    session = DBSession()
    rule_type = [
        {"rule_type": 1, "type_name": "头尾检测"},
        {"rule_type": 2, "type_name": "完整性检测"},
        {"rule_type": 3, "type_name": "文件检测"},
        {"rule_type": 4, "type_name": "上下文顺序检测"},
        {"rule_type": 5, "type_name": "局部时限检测"},
    ]
    try:
        session.execute(
            RuleType.__table__.insert(),
            rule_type
        )
        session.commit()
    except Exception as e:
        print traceback.format_exc()
        session.close()

    session.close()


def create_rule():
    session = DBSession()
    rules = [
        build_rule_json({"rule_name": "头尾检测test1", "rule_type": 1, "head": " E1, E2 ", "tail": "E8 , E19",
                         "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "完整性检测test1", "rule_type": 2, "overall_include": " E1,E2,E3,E4",
                         "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "文件检测test1", "rule_type": 3, "file_include": "E15,E16,E17",
                         "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test1", "rule_type": 4, "context_pre": "E20",
                         "context_back": "E9,E10,E11,E12,E13", "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test2", "rule_type": 4, "context_pre": "E4",
                         "context_back": "E5,E6，E9,E10,E11,E12,E13，E18",
                         "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test3", "rule_type": 4, "context_pre": "E3",
                         "context_back": "E4", "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test4", "rule_type": 4, "context_pre": "E1",
                         "context_back": "E9,E10,E11,E12,E13", "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "局部时限检测test1", "rule_type": 5, "part": "E4,E3", "partial_time": 10,
                         "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
    ]
    try:
        session.execute(
            CheckRule.__table__.insert(),
            rules
        )

        session.commit()
    except Exception as e:
        traceback.print_exc()
        session.close()

    session.close()


def build_rule_json(arg):
    return {
        "rule_type": arg.get("rule_type"),
        "rule_name": arg.get("rule_name", ""),
        "head": arg.get("head", ""),
        "tail": arg.get("tail", ""),
        "overall_include": arg.get("overall_include", ""),
        "file_include": arg.get("file_include", ""),
        "context_pre": arg.get("context_pre", ""),
        "context_back": arg.get("context_back", ""),
        "part": arg.get("part", ""),
        "partial_time": arg.get("partial_time", 0),
        "datetime": arg.get("datetime", time.strftime("%Y-%m-%d %H:%M:%S")),
    }


if __name__ == '__main__':
    # create_type()
    # create_user()
    # create_log()
    # create_ruletype()
    create_rule()
