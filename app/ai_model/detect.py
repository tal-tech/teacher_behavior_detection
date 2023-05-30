#coding:utf-8
import os
import threading
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import sys
base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base_path,'./teacher_behavior_detection'))
sys.path.append(os.path.join(base_path,'./teacher_behavior_detection/src/auto_text_classifier'))
from src.teacher_behavior_detection import detect as model_detect

m_locker = threading.Lock()

def detect(*args,**kvargs):
    with m_locker:
        return model_detect(*args,**kvargs)

