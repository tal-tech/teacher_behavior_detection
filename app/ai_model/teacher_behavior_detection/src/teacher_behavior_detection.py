import pandas as pd
from src.find_start import model
from src.config.keywords_config import keywords_cfg
import traceback

# 映射具体问句
LABEL_TOPIC_MAPPING = {
    0: '鼓励',
    1: '引导',
    2: '总结',
    3: '寒暄',
    4: '笔记',
    5: '复述',
    6: '复习',
    7: '举例',
    8: '其他',
}


def detect(text_list, keywords_scene=None):

    if len(text_list) == 0:
        return {"msg": "success", "code": 0, "data": []}

    try:
        df = pd.DataFrame(text_list)
        df.fillna("", inplace=True)

    except:
        return {"msg": "input format error,detail is {}".format(traceback.format_exc()), "code": -1, "data": {}}

    try:
        for col in ['text', 'begin_time', 'end_time']:
            if col not in df.columns:
                return {"msg": "miss col {}".format(col), "code": -1, "data": []}
        # 检测句子类型
        df['label'] = model.predict_list(df['text'])

        # v1.1: 支持自定义词表
        if keywords_scene is not None:
            try:
                keywords_this_scene = keywords_cfg.get(keywords_scene, {})
            except:
                return {"msg": "please check keywords_scene", "code": -1, "data": []}
            # print(keywords_this_scene)
            df = keywords_filter_func(df, keywords_this_scene)

        # v1.0: 只留下指定类别
        df = df[df['label'].isin([0, 1, 2, 3, 4, 5, 6, 7])].reset_index(drop=True)
        df['label_name'] = df['label'].map(LABEL_TOPIC_MAPPING)

        # 包装结果
        if df.shape[0] == 0:
            data = {}
        else:
            detail = df.apply(lambda x: {'begin_time': int(x['begin_time']), 'end_time': int(x['end_time']),
                                                'text': x['text'],
                                                'label': x['label_name']}, axis=1).tolist()
            data = {"text_result": detail, 'num': df.shape[0], 'class_type_result': []}
            label_name_count = df['label_name'].value_counts().to_dict()
            for name in ['鼓励', '引导', '总结', '寒暄', '笔记', '复述', '复习', '举例']:
                data['class_type_result'].append({'class_type': name, 'num': label_name_count.get(name, 0)})
        return {"msg": "success", "code": 0, "data": data}

    except:
        return {"msg": "error happened", "code": -1, "data": {}}


def keywords_filter_func(df, keywords_this_scene):

    '''
    对df进行每行的遍历，如果模型判断属于指定的类别，但没有关键词，则改为负例(label=8)
    :param df: 输入的结果dataframe.
    :param keywords_this_scene: 关键词表, {2: ['思路', '技巧', '套路', '概括', '总结', '归纳', '梳理', '小结'],
    4: ['笔记', '记下', '拍', '照']}
    :return:
    '''
    row_nums = df.shape[0]
    for r in range(row_nums):
        # print(df.loc[r]['text'])
        # print(df.iloc[r]['label'])
        k_ = keywords_this_scene.get(df.iloc[r]['label'], [])
        # print(k_)

        # 没有设置词表的类别自动跳过
        if len(k_):
            # 如果
            if not k_is_in(df.iloc[r]['text'], k_):
                df.loc[r, 'label'] = 8
    return df


def k_is_in(t, keywords):
    for k in keywords:
        if k in t:
            return True
    return False


if __name__ == '__main__':
    pass
