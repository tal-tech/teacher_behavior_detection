import json
import time
import threading
import random
import datetime
from queue import Queue
from app.common.redis_client import RedisClient
from concurrent.futures  import ThreadPoolExecutor
from app.common.logger import logger
from app.common.config import Config
from app.common.errcode import MyExcept, Status
from app.common.singleton import SingletonIns

QUEUE_NAME = "teacher-behavior"

@SingletonIns
class TaskQueue(object):
    def __init__(self):
        self._processing = None
        self._redis = RedisClient()
        self._task_thread = threading.Thread(target=self._process_task, daemon=True)        

    def start(self, handle_task_fn):
        if not handle_task_fn:
            raise Exception("handler fn cannot be None")
        self._handle_task_fn = handle_task_fn

        self._processing = True
        self._task_thread.start()

    def _process_task(self):
        while self._processing:
            try:
                result = self._redis.execute("BLPOP", QUEUE_NAME, 10)
                if result is None:
                    continue
                req_str = result[1].decode("utf-8")
            except Exception as e:
                logger.alert(Status.READ_QUEUE_FAILED, e)
                time.sleep(1)
                continue

            try:
                task_info = json.loads(req_str)
                self._handle_task_fn(task_info)
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error("process task error {}".format(e))

    def add_task(self, task_info):
        if not self._processing:
            logger.warn("add task after queue stoped")
            return
        req_str = json.dumps(task_info, ensure_ascii=False)
        # add task to redis QUEUE_NAME
        op_res = self._redis.execute("RPUSH", QUEUE_NAME, req_str)
        if not isinstance(op_res, int) and op_res == 0:
            raise Exception("add task to redis error {}".format(op_res))

    def stop(self):
        self._processing = False
        self._task_thread.join()
