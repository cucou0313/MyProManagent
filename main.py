# coding=utf-8
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-27 10:54
IDE: PyCharm
"""
import threading

from Conf.conf import task_queue
from Dao.CheckData import tasks_assign
from Dao.ListenData import listen_data

if __name__ == '__main__':
    p = threading.Thread(target=listen_data)
    p.start()
    # task_queue.put("1ab9d706-346e-4f41-a361-6d9961bdefcc")
    tasks_assign()
