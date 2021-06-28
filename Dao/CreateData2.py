# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-27 10:44
IDE: PyCharm
"""
import json
import random
import time
import traceback
import uuid

import requests

from Models.MyModel import DBSession, OperateLog, User, OperateType, CheckRule, RuleType


def create_event():
    events = []
    count = 0
    # 1============================================侦查机关:控告、检举书,控告、检举笔录，自首书,讯问、勘验、检查、搜查笔录，
    # 立案报告，案件侦查终结报告，提请批准逮捕书，逮捕证，通缉令 14
    events.append('E1')
    events.append('E9')
    count += 1
    count1 = 1
    # flag0=0
    # flag1=0
    # for i in range(5):

    n0 = random.randint(12, 20)
    # while 1:
    for i in range(n0):
        # if count1==14:break
        m = random.randint(0, 4)
        if m == 0:
            # flag0=1
            events.append('E10')
        else:
            # flag1=1
            events.append('E9')
            count1 += 1
            count = count + 1
    # print('上传数', count)

    for i in range(2):
        m = random.randint(0, 1)
        if m == 1:
            events.append('E10')
    events.append('E3')
    # 2=============================================
    events.append('E4')
    m = random.randint(0, 5)
    for i in range(m):
        events.append('E10')
    events.append('E20')
    events.append('E3')
    # 3=============================================
    events.append('E4')
    arrange = ['E5', 'E6', 'E18']
    random.shuffle(arrange)
    # print(arrange)
    events.extend(arrange)
    # print(events)
    events.append('E3')
    # 4=============================================检察机关：主要有起诉(免于起诉)决定，批准(不批准)逮捕决定，起诉书，
    # 抗诉书，补充侦查意见书  5
    events.append('E4')

    n0 = random.randint(3, 10)
    for i in range(n0):
        m = random.randint(0, 4)
        if m == 0:
            events.append('E10')
        else:
            events.append('E9')
            count = count + 1
    # print('上传数', count)

    for i in range(2):
        m = random.randint(0, 1)
        if m == 1:
            events.append('E10')

    # checks = ['E15','E16','E17']
    c0 = 0
    c1 = 0
    c2 = 0
    # print(count)
    for i in range(count):
        events.append('E15')
        events.append('E16')
        events.append('E17')

    sum = count
    # print(sum)
    count = 0
    events.append('E7')
    events.append('E3')
    # 5=3=============================================
    events.append('E4')
    arrange = ['E5', 'E6', 'E18']
    random.shuffle(arrange)
    # print(arrange)
    events.extend(arrange)
    # print(events)
    events.append('E3')
    # 6=4=============================================审判机关:主要有诉状，开庭通知书，案件审理终结报告，调解书，判决书，
    # 裁定书，执行通知书，审判庭笔录,合议庭评议笔录,宣判笔录，刑事判决布告 11
    events.append('E4')

    n0 = random.randint(11, 20)
    # while 1:
    for i in range(n0):
        m = random.randint(0, 4)
        if m == 0:
            events.append('E10')
        else:
            events.append('E9')
            count = count + 1
    # print('上传数', sum + count)

    for i in range(2):
        m = random.randint(0, 1)
        if m == 1:
            events.append('E10')

    for i in range(count):
        events.append('E15')
        events.append('E16')
        events.append('E17')

    events.append('E7')
    sum += count
    # print(sum)
    m = random.randint(int(sum / 2), sum * 2)
    for i in range(m):
        events.append('E10')
    events.append('E3')
    # 7=============================================
    events.append('E4')
    m = random.randint(int(sum / 4), int(sum / 2))
    for i in range(m):
        events.append('E10')
    events.append('E8')
    return events


def create_log(event):
    session = DBSession()
    task_id = str(uuid.uuid4())
    file = []
    checkE15 = []
    checkE16 = []
    checkE17 = []
    for item in event:
        # task_id = str(uuid.uuid4())
        log_id = str(uuid.uuid4())
        operate_type = "%s" % item
        # print operate_type
        if operate_type == "E9":
            file_id = str(uuid.uuid4())
            file.append(file_id)
            checkE15.append(file_id)
            checkE16.append(file_id)
            checkE17.append(file_id)
        elif operate_type == "E15":
            n = random.randint(0, len(checkE15) - 1)
            file_id = str(checkE15[n])
            del checkE15[n]
            # pass
        elif operate_type == 'E16':
            n = random.randint(0, len(checkE16) - 1)
            file_id = str(checkE16[n])
            del checkE16[n]
        elif operate_type == 'E17':
            n = random.randint(0, len(checkE17) - 1)
            file_id = str(checkE17[n])
            del checkE17[n]
        else:
            file_id = ""
        datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        user_id = random.randint(1, 3)
        # file_id = ""
        val = (task_id, log_id, operate_type, datetime, user_id, file_id)
        try:
            # new_data = OperateLog(task_id=task_id, log_id=log_id, file_id=file_id, type=operate_type, user_id=user_id,
            #                       datetime=datetime)
            # session.add(new_data)
            # session.commit()
            data = {
                "task_id": task_id,
                "log_id": log_id,
                "file_id": file_id,
                "type": operate_type,
                "user_id": user_id,
                "datetime": datetime,
            }
            http_post(data)
            time.sleep(random.randint(1, 3))
        except Exception as e:
            print traceback.format_exc()
            session.close()
        else:
            print "mysql insert success:", val

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
        build_rule_json({"rule_name": "头尾检测test1", "rule_type": 1, "head": " E1", "tail": "E8 , E19",
                         "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "完整性检测test1", "rule_type": 2, "overall_include": " E1,E2,E3,E4",
                         "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "文件检测test1", "rule_type": 3, "file_include": "E15,E16,E17",
                         "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test1", "rule_type": 4, "context_pre": "E1,E4,E20",
                         "context_back": "E9,E10,E11,E12,E13", "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test3", "rule_type": 4, "context_pre": "E4",
                         "context_back": "E5,E6,E18", "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test3", "rule_type": 4, "context_pre": "E5,E6,E18",
                         "context_back": "E3", "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test3", "rule_type": 4, "context_pre": "E3",
                         "context_back": "E4", "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
        build_rule_json({"rule_name": "上下文顺序检测test4", "rule_type": 4, "context_pre": "E9,E10,E11,E12,E13",
                         "context_back": "E5,E6,E18,E19,E20", "datetime": time.strftime("%Y-%m-%d %H:%M:%S")}),
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


def http_post(data):
    if isinstance(data, dict):
        datas = {
            "data": [data]
        }
        url = "http://127.0.0.1:12306/save_log"
        res = requests.post(url=url, json=datas)
        print res.json()


if __name__ == '__main__':
    # create_type()
    # create_user()
    # create_log()
    # create_ruletype()
    # create_rule()

    event = create_event()
    # print event
    create_log(event)
