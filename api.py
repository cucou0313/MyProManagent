# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-31 18:16
IDE: PyCharm
"""
import traceback

from flask import Flask, request

from Conf import conf
from utils.mylogger import get_logger
from Dao.ListenData import log_parse

logger = get_logger("api")

app = Flask(__name__)


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
            "errCode": 0,
            "sss": conf.check_rules
        }
    except Exception, e:
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return {"errMsg": str(e), "errCode": 1}


def flask_run(host, port, debug=True):
    app.debug = debug
    app.run(host=host, port=port)


if __name__ == '__main__':
    flask_run(host="0.0.0.0", port=12306)
