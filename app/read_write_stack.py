# -*- coding: utf-8 -*-
import os
import time 
import cv2
import gc
import threading 
from app.infer_utils import people_queue_recog
from app.get_monitor_roi import analyse_monitor_person_info
from app.email_reminder import send_email_remind
from app.record_queue_person_nums import write_detectionInfo_into_xlsx, clear_detectionInfo_into_xlsx


queue_lock = threading.Lock()
lst_lock = threading.Lock()


def check_input_resource(input_resource):
    """
    检查输入源头是否是有效的分析源

    :param input_resource: (mp4 avi rtsp) 为 str 类型 or 电脑前置摄像头(0) 为 int 类型
    :return True or False: bool 型
    """
    if isinstance(input_resource, str):
        if input_resource.startswith("rtsp"):
            print ('-------input resource is a rstp stream-------')
        elif input_resource.endswith(('mp4', 'avi')):
            print ('-------input resource is a mp4 stream--------')
            if not os.path.exists(input_resource):
                print ('input video(mp4 or avi) path is a wrong path!!!')
                return False 
    elif isinstance(input_resource, int):
        print ('-------input resource is a built-in camera-------')

    try:
        cap = cv2.VideoCapture(input_resource)
        if cap.isOpened():
            cap.release()
            print ('input resource has checked, its is ok...')
            return True 
        else:
            return False 
    except Exception as error:
        print ('input resource has something wrong conditinon: {}!!!'.format(error))
        return False 
    

def write_stack(stack, cam, top, skip_frame_nums):
    """
    往缓冲栈中写入图像数据帧，以供后续AI模块推理分析

    :param stack: Manager.list对象
    :param cam: 摄像头参数，可能是视频格式、rtsp流、自带的摄像头，str or int 类型
    :param top: 缓冲栈最大容量，int 类型
    :return: None
    """
    skip_frame_nums = max(skip_frame_nums, 20) # 不能设置太小，以至于频繁处理图像造成队列迅速堵住
    cap = cv2.VideoCapture(cam)
    accu_frame_index = 0
    while True:
        _, img = cap.read()
        if _:
            accu_frame_index += 1
            if accu_frame_index == skip_frame_nums:
                accu_frame_index = 0
                # print ('add a frame from camera <<<<<<<<<<<<<<<<<<<<')
                queue_lock.acquire()
                stack.put(img)
                queue_lock.release()

            if stack.qsize() >= top:
                print ("current stack size reach max: {}, need to wait a moment".format(stack.qsize()))
                # 需要等一会，让读取和识别模块处理一下
                time.sleep(5)
        else:
            print ('--------GET INPUT STREAM OVER OR FAIL--------')
            break 
    cap.release()


def read_stack(stack, lst, max_img_frame_nums):
    """
    从缓冲栈中读取图像帧，并做 AI 识别，并将识别后的信息放入新的缓冲栈

    :param stack: Manager.Queue对象
    :param lst: Manager.list 对象
    :param max_img_frame_nums: stack 里允许存在的最大容量，int 型
    :return: None
    """
    while True:
        if stack.qsize():
            queue_lock.acquire()
            frame = stack.get()
            queue_lock.release()
            # print ('get a frame from stack >>>>>>>>>>>>>>>>>>>>>>>>>>')
            person_coords_info = people_queue_recog(frame)

            if len(lst) <= max_img_frame_nums:
                # 为了数据传输的快速性以及邮件附加当前图像，有必要对实际的图像帧进行压缩
                height, width = frame.shape[:2]
                frame = cv2.resize(frame, (width//2, height//2))
                lst_lock.acquire()
                lst.append((frame, person_coords_info))
                lst_lock.release()
            # print ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')


def read_person_info(lst, email_cfg_info_object, min_person_queue_nums):
    """
    从缓冲栈中读取识别信息，并定时分析当前检测到的人数是否满足上报要求，若满足则发送邮件提醒（人数信息和排队画面图像）

    :param lst: 缓冲栈，Manager.list 对象
    :param email_cfg_info_object: EMAIL_CONFIG_INO 对象，在 read_write_Stack.py 中定义
    :param min_person_queue_nums: int 型，最少人数提醒的阈值，在app/config/params.yml 中设置
    :return: None
    """
    every_gap_time = email_cfg_info_object.email_report_gap_time 
    email_content_template = email_cfg_info_object.email_content_template
    # 辅助函数，初始化的时候可以清空记录的xlsx表格，便于正确记录新的一次测试数据
    clear_detectionInfo_into_xlsx('record/detect_result.xlsx', 'test_sheet')
    print ('-----------email gap time: {} seconds--------------'.format(every_gap_time))
    # print ('email content template:', email_content_template)
    begin_time = time.time()
    while True:
        if len(lst):
            lst_lock.acquire()
            frame, recog_person_info = lst.pop() 
            lst_lock.release()
            # print ('get person info from stack begin ----------------------')
            # for person_coord_info in recog_person_info:
            #     print ('person: {} from list'.format(person_coord_info))
            end_time = time.time()
            # 定时去看是否满足条件，从而去发送邮件提醒
            if (end_time-begin_time >= every_gap_time):
                print ('It is time to send email!!!!!!')

                in_roi_person_nums = analyse_monitor_person_info(recog_person_info) 
                # 该函数用于记录定期识别到的人数信息，将信息存储在record文件夹下的xlsx表格中
                write_detectionInfo_into_xlsx('record/detect_result.xlsx', 'test_sheet', in_roi_person_nums)
                # 该函数将定时上报时对应的图片也保存下来
                # cv2.imwrite("tmp/{}.jpg".format(end_time), frame)
                
                if in_roi_person_nums <= min_person_queue_nums:
                    print ("{} person are in queue for covid19 test...".format(in_roi_person_nums))
                    email_cfg_info_object.email_content_template = email_content_template.replace('[]', str(in_roi_person_nums))
                    send_email_remind(email_cfg_info_object, frame)
                    print ('send email over!')

                begin_time = end_time 
            # print ('get person info from stack over -----------------------')