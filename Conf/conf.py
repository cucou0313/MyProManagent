# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-26 20:50
IDE: PyCharm
"""
import os
import threading
from Queue import Queue

# MySql
conn = None
cursor = None

# mysql_host = "10.181.111.180"
mysql_host = "192.168.25.132"
mysql_db_user = "root"
mysql_db_psw = "root"
# mysql_db_psw = "zrb3021183"
mysql_db_name = "myprocmanager"

MYSQL_SETTING = "mysql://{user}:{psw}@{host}:{port}/{name}?charset=utf8".format(
    user=mysql_db_user, psw=mysql_db_psw, host=mysql_host, port=3306, name=mysql_db_name)

# 检测任务队列,线程并发模式,进程不能直接对queue进行内存共享
task_queue = Queue()
# 并行线程数量
workers_num = 2
# 监听日志间隔
listen_interval = 5

# 检测规则包
check_rules = None
# 监听使用,负责卷宗业务的整体超时检测
task_map = {}
task_map_lock = threading.Lock()
# 超时时间
overtime = 24 * 60

# log
# 日志级别
Level = 'DEBUG'
# 日志目录
LogPath = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))) + os.sep + "logs"

if __name__ == '__main__':
    print MYSQL_SETTING
