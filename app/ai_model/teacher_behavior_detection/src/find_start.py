from atc.models.aml import AML
from src.config.config_tools import config


ai = AML(save_dir="tmp")
model_name = config['model_name']
Model, model_config = ai.get_model_config(model_name)

save_dir = config['model_dir']
model_config = {"save_dir": save_dir, "model_dir": save_dir, 'num_labels': config['num_labels']}
model = Model(model_config)
model.load_model(model.model_path)