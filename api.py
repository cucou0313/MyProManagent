# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-31 18:16
IDE: PyCharm
"""
import json
import time
import traceback

from flask import Flask, request

from Conf import conf
from Dao.RuleInit import rules_init
from utils.mylogger import get_logger
from Dao.ListenData import log_parse
from Models.MyModel import DBSession, CheckRule, CheckRes
from flask_paginate import get_page_parameter

logger = get_logger("api")

app = Flask(__name__)
session = DBSession()


# ------------------日志入库------------------
@app.route('/save_log', methods=['POST'])
def save_log():
    """
    设计为可接受多条数据

    post_data = {
        "data": [{},{}...]
    }
    """
    try:
        assert request.data, "post is none."
        data = request.json.get("data")
        assert data and isinstance(data, list), "illegal data"

        print data
        log_parse(data)
        return {
            "msg": "save log success.",
            "errCode": 0
        }
    except Exception, e:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return {"errMsg": str(e), "errCode": 1}


# ------------------规则配置------------------
@app.route('/rules', methods=["GET", "POST", "PUT", "DELETE"])
def rules():
    try:
        # 127.0.0.1:12306/rules?id=1&order=id asc
        if request.method == "GET":
            rule_id = request.args.get("id")
            # 默认以id 升序
            order = request.args.get("order", "id asc")
            order1, order2 = order.split(' ')
            column = getattr(CheckRule, order1)
            if order2 == 'asc':
                order_by = column.asc()
            else:
                order_by = column.desc()
            # sql = '''select * from check_rule order by %s''' % order
            if rule_id:
                res = session.query(CheckRule).filter(CheckRule.id == rule_id).order_by(order_by).all()
            else:
                res = session.query(CheckRule).order_by(order_by).all()
                # cursor = session.execute(sql)
                # res = cursor.fetchall()
            return {
                "msg": "get rule success.",
                "errCode": 0,
                "data": [x.to_dict() for x in res]
            }
        # post_data = {
        #     "rule_type": 1,
        #     "rule_name": "头尾检测test1",
        #     "head": " E1, E2 ",
        #     "tail": "E8 , E19"
        # }
        elif request.method == "POST":
            assert request.data, "post is none."
            update_data = request.json
            update_data.update({
                "datetime": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            assert "rule_type" in update_data and "rule_name" in update_data, "no valid data"
            new_data = CheckRule(**update_data)
            session.add(new_data)
            session.commit()

            # 启用新规则
            conf.check_rules = rules_init()
            return {
                "msg": "insert a new rule success.",
                "errCode": 0
            }
        # {
        #     "context_back": null,
        #     "context_pre": null,
        #     "datetime": null,
        #     "file_include": null,
        #     "head": " E1, E2 ",
        #     "id": 1,
        #     "overall_include": null,
        #     "part": null,
        #     "partial_time": null,
        #     "rule_name": "头尾检测test1",
        #     "rule_type": 1,
        #     "tail": "E8 , E19"
        # }
        elif request.method == "PUT":
            assert request.data, "post is none."
            update_data = request.json
            rule_id = update_data.get("id")
            assert rule_id, '无规则id'
            res = session.query(CheckRule).filter(CheckRule.id == rule_id).update(update_data)
            assert res, "更新错误,id可能不存在"
            session.commit()

            # 启用新规则
            conf.check_rules = rules_init()
            return {
                "msg": "update rule success,id=%s" % rule_id,
                "errCode": 0
            }
        # 127.0.0.1:12306/rules?id=1
        elif request.method == "DELETE":
            rule_id = request.args.get("id")
            assert rule_id, '无规则id'
            print rule_id
            res = session.query(CheckRule).filter(CheckRule.id == rule_id).delete()
            # res是受影响的行数,res=0可能是不存在对应id行
            assert res, "删除错误,id可能不存在"
            session.commit()

            # 启用新规则
            conf.check_rules = rules_init()
            return {
                "msg": "del rule success,id=%s" % rule_id,
                "errCode": 0
            }
    except Exception, e:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return {"errMsg": str(e), "errCode": 1}


# ------------------结果显示------------------
@app.route('/check_res', methods=['GET'])
def check_res():
    PER_PAGE = 10  # 每页的结果数量
    page = request.args.get('page', 1)  # 获取页码，默认为第一页
    print page
    total = session.query(CheckRes).count()  # 总共的结果数量
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    # pagination = Pagination()
    # res = session.query(CheckRes).group_by(CheckRes.task_id).all()
    # res = session.query(CheckRes).all()
    res = session.query(CheckRes).order_by(CheckRes.datetime.desc()).slice(start, end)
    # res = session.query(CheckRes).group_by(CheckRes.task_id).slice(start, end)

    print res[0].datetime

    data = []
    for x in res:
        log = {
            "内容": x.content,
            "时间": str(x.datetime),
            "卷宗ID": x.task_id,
            "日志位置": x.operate_log_id,
            "原始日志": x.operate_log.to_dict()
        }
        data.append(log)

    return {
        "msg": "get check result success.",
        "errCode": 0,
        "data": data
    }


def flask_run(host, port, debug=True):
    app.debug = debug
    app.run(host=host, port=port)


if __name__ == '__main__':
    flask_run(host="0.0.0.0", port=12306)
