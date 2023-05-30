import time
import threading
import requests
import traceback
import json
from queue import Queue
from app.common.errcode import MyExcept, Status
from app.ai_model.detect import detect
from app.api import dataflow
from concurrent.futures  import ThreadPoolExecutor
from app.common.logger import logger
from app.common.config import Config

THREAD_POOL_SIZE = 10
CALLBACK_RETRY_COUNT = 3
CALLBACK_TIMEOUT = 10
PAAS_STAT_RETRY_COUNT = 3
PAAS_STAT_TIMEOUT = 10

class Worker():
    def __init__(self, mq_process):
        self._mq_process = mq_process
        self._queue = Queue()
        self._t_callback = threading.Thread(target=self._process_callback, daemon=True)
        self._t_callback.start()
        self._callback_thread_pool = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)
        self._config = Config()

    def work(self, task_info):
        callback = task_info["callback"]
        input_text = task_info["input_text"]
        start_time = task_info["start_time"]
        request_id = task_info["request_id"]
        app_key = task_info["app_key"]
        api_id = task_info["api_id"]
        api_type = task_info["api_type"]
        trace_id = task_info["trace_id"]

        model_consume = 0
        response_data = {
            "requestId": request_id,
        }
        try:
            model_start_time = time.time()
            try:
                if app_key == self._config.qingqing_appkey:
                    behavior_result = detect(input_text, keywords_scene='qingqing')
                    logger.info('{}-model for qingqing'.format(request_id))
                else:
                    behavior_result = detect(input_text)
                logger.info('{}-model return :{}'.format(request_id, behavior_result))
                if "code" in behavior_result:
                    code = behavior_result['code']
                    if code == -1:
                        raise MyExcept(Status.INPUT_TEXT_TYPE_ERROR)
                if not "data" in behavior_result:
                    raise MyExcept(Status.ALGORITHM_ERROR)
                data = behavior_result["data"]
                if data != {}:
                    response_detail = data['text_result']
                    response_num = data['num']
                    response_class = data['class_type_result']
                    response_data['data'] = {}
                    response_data['data']['text_result'] = response_detail
                    response_data['data']['total_num'] = response_num
                    response_data['data']['class_type_result'] = response_class
                else:
                    response_data['data'] = {}
                    response_data['data']['text_result'] = []
                    response_data['data']['total_num'] = 0
                    response_data['data']['class_type_result'] = [
                        {"class_type": "鼓励", "num": 0},
                        {"class_type": "引导", "num": 0},
                        {"class_type": "总结", "num": 0},
                        {"class_type": "寒暄", "num": 0},
                        {"class_type": "笔记", "num": 0},
                        {"class_type": "复述", "num": 0},
                        {"class_type": "复习", "num": 0},
                        {"class_type": "举例", "num": 0}
                    ]
            except Exception as e:
                raise MyExcept(Status.PARAMS_MODEL_ERROR, detail=e)
            model_consume = time.time() - model_start_time

            # response_data['data'] = behavior_result["data"]
            response_data['code'] = Status.SUCCESS.err_code()
            response_data['msg'] = Status.SUCCESS.err_msg()
        except MyExcept as e:
            response_data['code'] = e.err_code
            response_data['msg'] = e.err_msg
            response_data['data'] = {}
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            response_data['code'] = Status.UNKNOWN_ERROR.err_code()
            response_data['msg'] = Status.UNKNOWN_ERROR.err_msg()
        finally:
            end_time = int(1000 * time.time())
            req_json = {
                "callback": callback,
                "input_text": input_text,
            }
            logger.info('async=>request: %s, trace_id: %s, response: %s %s', request_id, trace_id, response_data['code'], response_data['msg'])

            dataflow(self._mq_process, request_id, app_key, api_id, api_type, start_time, end_time, req_json, response_data, model_consume)
        self._queue.put((callback, response_data, model_consume))

    def _process_callback(self):
        while True:
            task_info = self._queue.get(block=True)
            if not task_info:
                break
            self._callback_thread_pool.submit(self._callback, task_info)

    def _callback(self, task_info):
        callback, response, model_consume = task_info
        #callback
        retry = 0
        err_msg = ""
        while retry < CALLBACK_RETRY_COUNT:
            logger.info(callback)
            try:
                resp = requests.post(url=callback, data=json.dumps(response, ensure_ascii=False).encode(),
                    timeout=CALLBACK_TIMEOUT, headers={"Content-Type":"application/json"})
                logger.info('call_back info:{}'.format(response))
            except Exception as e:
                logger.error(e)
                retry = 3
                break
            if resp.status_code == 200:
                break
            err_msg = "{} {}".format(resp.status_code, resp.content.decode())
            retry += 1
        if retry == CALLBACK_RETRY_COUNT:
            logger.alert(Status.CALLBACK_FAILED, err_msg)
        #paas stat
        retry = 0
        err_msg = ""
        while retry < PAAS_STAT_RETRY_COUNT:
            url = "{}/asyncApiCallback?requestId={}&code={}&msg={}&duration={}".format(self._config.paas_stat_host,
                    response["requestId"], response["code"], response["msg"], model_consume)
            try:
                resp = requests.get(url, timeout=PAAS_STAT_TIMEOUT, headers={"Content-Type":"application/json"})
            except Exception as e:
                logger.alert(Status.PAAS_STAT_FAILED, e)
                break
            if resp.status_code == 200:
                break
            err_msg = "{} {}".format(resp.status_code, resp.content.decode())
            retry += 1
        if retry == PAAS_STAT_RETRY_COUNT:
            logger.alert(Status.PAAS_STAT_FAILED, err_msg)
    
    def stop(self):
        self._queue.put(None)
        self._t_callback.join()