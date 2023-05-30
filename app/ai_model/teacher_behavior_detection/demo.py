import os
import json
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import sys
base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base_path,'src/auto_text_classifier'))
from src.teacher_behavior_detection import detect


if __name__ == "__main__":
    input_text = [
        {
            "text": "你做的真棒！",
            "begin_time": 1326750,
            "end_time": 1332165
        },
        {
            "text": "记得做笔记啊。",
            "begin_time": 1326751,
            "end_time": 1332165
        },
        {
            "text": "这个选A是不是？",
            "begin_time": 1326752,
            "end_time": 1332165,
        },
        {
            "text": "我今天吃了大米饭",
            "begin_time": 13131313,
            "end_time": 133216512
        },
        {
            "text": "啊啊啊啊",
            "begin_time": 13131313,
            "end_time": 133216512
        },
        {
            "text": "包括不同种了飞机水，就看到了吗？",
            "begin_time": 1326752,
            "end_time": 1332165
        },
        {
            "text": "总结归纳一下文章主旨",
            "begin_time": 1326752,
            "end_time": 1332165
        }
    ]

    # 测试用
    for i in range(1):
        result = detect(input_text, keywords_scene='qingqing')
        # print(json.dumps(result, indent=4, ensure_ascii=False))
