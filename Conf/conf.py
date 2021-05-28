# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-26 20:50
IDE: PyCharm
"""
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

task_queue = Queue()

if __name__ == '__main__':
    print MYSQL_SETTING
