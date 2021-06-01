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
from Dao.ListenData import rules_init
from api import flask_run

if __name__ == '__main__':
    # p = threading.Thread(target=listen_data)
    # p.start()
    # conf.task_queue.put("d9d00051-4c08-493b-86ea-43f2ca439d08")
    # tasks_assign()
    conf.check_rules = rules_init()
    flask_run(host="0.0.0.0", port=12306)
