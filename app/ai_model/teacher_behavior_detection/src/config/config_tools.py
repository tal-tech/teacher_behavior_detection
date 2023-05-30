import json
import os

is_debug = False

base_path = os.path.dirname(os.path.realpath(__file__))
if is_debug:
    model_dir = '/share/hy/godeye/teacher_behavior_detection_models/roberta_wwm_ext_large_new'
else:
    data_dir = os.path.join(base_path, '../../data')
    model_dir = os.path.join(data_dir, 'roberta_wwm_ext_large')

test_data_dir = os.path.join(base_path, '../../test_data')

config = {"model_dir": model_dir,
          "model_name": "roberta_wwm_ext_large",
          "batch_size": 64,
          "num_labels": 9,
          }
