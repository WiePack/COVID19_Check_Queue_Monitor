# -*- coding: utf-8 -*-
"""
AI 推理调用模块，使用的是基于yolov5s的模型
"""
import os 
import time 
from app.read_cfg_yml import load_model_info


main_dir = os.getcwd()
is_load_model_params_successed, model_info_object = load_model_info(main_dir)
model = model_info_object.model_object
classes = model_info_object.classes 


def people_queue_recog(frame):
    """
    对输入的图像帧进行AI推理识别
    
    :param frame: numpy.ndarray类型
    :return person_coords_info: list 类型，包含5个值：人体的左上角x坐标、左上角y坐标、右下角x坐标、右下角y坐标、置信度（2位有效数字）
    """
    if not is_load_model_params_successed:
        print ('----- load model.yml fail!!! -----')
        return []
        
    height, width = frame.shape[:2]
    height_width_max = max(height, width)
    input_blob = model.pre_process(frame) # global model
    preds = model.infer(input_blob)
    person_coords_info = model.post_process(preds, height_width_max)
    
    print ('person info in [whole image]: total person: {}, detail coord info: {}'.format(len(person_coords_info), person_coords_info))

    return person_coords_info