import sys
import pandas as pd
import time
import os
import sys
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "6"
base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base_path, 'src/auto_text_classifier'))
topic_arg = sys.argv[1]

MAPPING = {
    'praise': 0,
    'example': 7,
    'note': 4,
}


def test_core():
    from atc.utils.metrics_utils import get_multi_class_report
    from src.teacher_behavior_detection import model

    df = pd.read_csv('test_data/{}.csv'.format(topic_arg))
    df.fillna("", inplace=True)
    tic = time.time()
    df['pred'] = model.predict_list(df['text'])
    df['pred_binary'] = -1

    toc = time.time()

    # 预测结果是9分类，计算指标时映射到具体类别的0和1.(负例要求高)
    df.loc[df.pred != MAPPING[topic_arg], 'pred_binary'] = 0
    df.loc[df.pred == MAPPING[topic_arg], 'pred_binary'] = 1
    # print(df)
    result = get_multi_class_report(df['label'], df['pred_binary'])
    n = df.shape[0]
    print(result)
    print("Run {} sentences use batch=64,spend time is {:.2f}s,{:.2f} it/s".format(n, toc-tic, n/(toc-tic)))


if __name__ == "__main__":
    # /workspace/projects_2020/godeye/teacher_behavior_detection
    for i in range(2000):
        test_core()
    # test_find_end()
    pass