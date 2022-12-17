# -*- coding: utf-8 -*-
"""
项目主程序
"""
import os 
from multiprocessing import Process, Manager
from app.read_write_stack import write_stack, read_stack, read_person_info, check_input_resource
from app.read_cfg_yml import load_input_source_info, load_monitor_person_queue_info, load_email_info


if __name__ == '__main__':
    main_dir = os.getcwd()
    
    is_load_source_params_successed, input_resource, max_img_frame_nums, skip_frame_nums = load_input_source_info(main_dir)
    if not is_load_source_params_successed:
        print ('load source params fail!!!')
        quit()
    
    is_load_monitor_params_successed, min_person_queue_nums = load_monitor_person_queue_info(main_dir)
    if not is_load_monitor_params_successed:
        print ('load monitor_info params fail!!!')
        quit()

    is_load_email_params_successed, email_cfg_info_object = load_email_info(main_dir)
    if not is_load_email_params_successed:
        print ('load email info params fail!!!')
        quit()

    if not check_input_resource(input_resource):
        print ('input resource is not right! pls check whether it is right format!')
        quit()

    q = Manager().Queue()
    l = Manager().list()

    pw = Process(target=write_stack, args=(q, input_resource, max_img_frame_nums, skip_frame_nums))
    pr = Process(target=read_stack, args=(q, l, max_img_frame_nums))

    lr = Process(target=read_person_info, args=(l, email_cfg_info_object, min_person_queue_nums))
    pw.start()
    pr.start()
    lr.start()

    pr.join()
    lr.join()

    pw.terminate()