# -*- coding: utf-8 -*-
"""
读取所有配置文件（yaml）的模块
"""
import os 
import yaml
from app.yolov5 import YOLOV5


class EMAIL_CONFIG_INO(object):
    def __init__(self, sender_account, sender_pwd, recv_account, email_subject, email_content_template, report_time):
        self.email_sender_account_usr = sender_account
        self.emial_sender_account_pwd = sender_pwd
        self.email_receiver_account_usr = recv_account
        self.email_subject = email_subject
        self.email_content_template = email_content_template
        self.email_report_gap_time = report_time


class MODEL_CONFIG_INFO(object):
    def __init__(self, classes, detect_instance):
        self.classes = classes 
        self.model_object = detect_instance 


def load_input_source_info(main_dir):
    """
    载入输入源头的参数，比如rtsp、mp4、avi等

    :param main_dir: str 型，配置文件所在的目录
    :returns: True(False)、input_source(str or int 型)、max_img_frame_nums_in_buffer(int 型), skip_frame_nums_to_infer_img(int 型)
    """
    yml_config_path = os.path.join(main_dir, 'app', 'config', 'params.yml')
    if not os.path.exists(yml_config_path):
        print ('--------- source config file not exist!!! pls check whether params.yml exist or not ------------')
        return False, 0, 100, 30

    # follow codes require early version yaml version: <= 5.1
    # file = io.open(yml_config_path, 'r', encoding='utf-8')
    # file_data = file.read()
    # file.close()
    # data = yaml.load(file_data)
    # input_source = data['input_source']
    # max_img_frame_nums_in_buffer = data['max_img_frame_nums']
    # skip_frame_nums_to_infer_img = data['skip_frame_nums']

    # follow codes requires higher yaml version: > 5.1
    with open(yml_config_path, encoding='utf-8') as fs:
        cont = yaml.load(fs, Loader=yaml.FullLoader)
        # print ('cont:', cont)

        input_source = cont['input_source']
        max_img_frame_nums_in_buffer= cont['max_img_frame_nums']
        skip_frame_nums_to_infer_img = cont['skip_frame_nums']

    return True, input_source, max_img_frame_nums_in_buffer, skip_frame_nums_to_infer_img


def load_monitor_person_queue_info(main_dir):
    """
    载入监控信息的参数，比如设定监控到排队少于某个阈值后，通过邮件提醒

    :param main_dir: str 型，配置文件所在的目录
    :returns True(False)、min_person_queue_nums(int 型)
    """
    yml_config_path = os.path.join(main_dir, 'app', 'config', 'params.yml')
    if not os.path.exists(yml_config_path):
        print ('--------- monitor info file not exist!!! pls check whether params.yml exist or not ------------')
        return False, 10

    # follow codes requires higher yaml version: >= 5.1
    with open(yml_config_path, encoding='utf-8') as fs:
        cont = yaml.load(fs, Loader=yaml.FullLoader)
        # print ('cont:', cont)
        min_person_queue_nums = cont['min_person_queue_nums']
        
    return True, min_person_queue_nums


def load_email_info(main_dir):
    """
    载入邮件信息参数，比如发送方、接收方的账户名、密码等

    :param main_dir: str 型，配置文件所在的目录
    :returs: True(False)、email_cfg_info_object(EMAIL_CONFIG_INO 对象)
    """
    yml_config_path = os.path.join(main_dir, 'app', 'config', 'params.yml')
    if not os.path.exists(yml_config_path):
        print ('--------- email info file not exist!!! pls check whether params.yml exist or not ------------')
        return False, EMAIL_CONFIG_INO('', '', '', 'Wrong emal cfg info', 30)

    # follow codes requires higher yaml version: >= 5.1
    with open(yml_config_path, encoding='utf-8') as fs:
        cont = yaml.load(fs, Loader=yaml.FullLoader)
        # print ('cont:', cont)
        email_report_gap_time = cont['every_report_by_email_gap_time']
        email_sender_account_usr = cont['email_sender_account_usr']
        emial_sender_account_pwd = cont['email_sender_account_pwd']
        email_receiver_account_usr = cont['email_receiver_account_usr']
        email_subject = cont['email_subject']
        email_content_template = cont['emial_content_template']
    
    email_cfg_info_object = EMAIL_CONFIG_INO(email_sender_account_usr, emial_sender_account_pwd, 
                                             email_receiver_account_usr, email_subject, 
                                             email_content_template, email_report_gap_time)

    return True, email_cfg_info_object 


def load_model_info(main_dir):
    """
    载入模型参数信息，比如模型地址、置信度阈值等

    :param main_dir: str 型，配置文件所在的目录
    :returs: True(False)、model_info_object(MODEL_CONFIG_INFO 对象)
    """
    yml_config_path = os.path.join(main_dir, 'app', 'config', 'params.yml')
    if not os.path.exists(yml_config_path):
        print ('--------- model info file not exist!!! pls check whether params.yml exist or not ------------')
        det = YOLOV5('model/covid19_test_queue_monitor.onnx') # 2个阈值有默认值，所以没写
        return False, MODEL_CONFIG_INFO(['person'], det) 

    # follow codes requires higher yaml version: >= 5.1
    with open(yml_config_path, encoding='utf-8') as fs:
        cont = yaml.load(fs, Loader=yaml.FullLoader)
        # print ('model info cont:', cont)
        classes = cont['classes']
        model_path = cont['model_path']
        conf_threshold = cont['conf_threshold']
        iou_threshold = cont['iou_threshold']
    
    if not os.path.exists(model_path):
        print ('------- AI model path not exist!!! pls check whether AI model path exist or not -------')
        det = YOLOV5('model/covid19_test_queue_monitor.onnx') # 2个阈值有默认值，所以没写
        return False, MODEL_CONFIG_INFO(['person'], det) 

    # model_info_instance = NanoDet(model_path, conf_threshold, iou_threshold)
    model_info_instance = YOLOV5(model_path, conf_threshold, iou_threshold)
    model_info_object = MODEL_CONFIG_INFO(classes, model_info_instance)

    return True, model_info_object
