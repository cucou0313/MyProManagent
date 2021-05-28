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

from Models.MyModel import DBSession, OperateLog, User, OperateType


def create_log():
    session = DBSession()

    task_id = str(uuid.uuid4())
    count = random.randint(10, 30)
    print "本次预计生成 %d 条数据" % count
    for i in range(count):
        log_id = str(uuid.uuid4())
        operate_type = "E%d" % random.randint(1, 15)
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


if __name__ == '__main__':
    # create_type()
    # create_user()
    create_log()
