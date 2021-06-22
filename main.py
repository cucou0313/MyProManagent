# coding=utf-8
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-27 10:54
IDE: PyCharm
"""
import threading
import time

from Conf import conf
from Dao.CheckData import tasks_assign
from Dao.RuleInit import rules_init
from api import flask_run

if __name__ == '__main__':
    p = threading.Thread(target=tasks_assign)
    p.start()
    # conf.check_rules = rules_init()
    # conf.task_queue.put("76408b1b-1d87-4d2f-bc25-7930a5057307")
    # tasks_assign()

    conf.check_rules = rules_init()
    flask_run(host="0.0.0.0", port=12306)
