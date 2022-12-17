# -*- coding: utf-8 -*-
"""
获取监控核酸队伍人群的模块，包括 人为配置的核酸监控区域读取、判断模型检测到的人是否在核酸队伍里、统计核酸队伍的实际人数
"""
import cv2 
import numpy as np 
import json 

CV_VERSION = cv2.__version__


def get_covid19_monitor_roi_contour():
    """
    获取提前在 region.json 中配置好的核酸队伍检测区域（可以是不规则的多边形）
 
    :return: contour 类型，由 findContours 函数找出的目标区域的最外侧轮廓
    """

    # 在示例图像上配置检测区域，相关的参数会自动保存到json文件里
    json_file_path = 'app/config/region.json' # 对应 assets/region.jpg 
    with open(json_file_path) as file:
        file_data = json.load(file)
    # print ('json file data content:', file_data)

    # 原图的尺寸，来源于相机本身
    ori_height = file_data["imageHeight"]
    ori_width = file_data["imageWidth"]

    # 获取配置的多边形区域，这一步在json文件里已经配置好
    all_pts_coords = file_data["shapes"][0]["points"]
    # 在图像上配置生成的坐标都是float型，这里需要提前转换为整型，便于后续处理
    all_pts_coords = [(int(x), int(y)) for x, y in all_pts_coords]
    print ("pre_config ROI all points:", all_pts_coords)

    roi_points_num = len(all_pts_coords)
    template_img = np.zeros((ori_height, ori_width), np.uint8)
    
    for j in range(roi_points_num):
        cv2.line(template_img, all_pts_coords[j], all_pts_coords[(j+1)%roi_points_num], 255, 1, 8)

    # cv2.imwrite("roi_drawline.jpg", template_img)

    # 注意：同一个findContours函数，opencv 3 和 opencv4 的返回值不同
    contours_info = cv2.findContours(template_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # opencv3 and opencv4 has different results
    # print ("-----opencv version: {}-----".format(CV_VERSION))
    # print ('len of contour:', len(contours_info))

    if len(contours_info) == 3: # opencv3，findContours return 3 results: img、contours(what we wanted)、hierarchy
        return  contours_info[1][0]
    elif len(contours_info) == 2: # opencv4，findContours return 2 results: contours(what we wanted)、hierarchy
        return  contours_info[0][0]


def judge_person_in_hesuan_roi(person_detail_info, roi_contour):
    """
    判断识别出的人体是否位于预先配置好的region区域，即人体坐标是否在region.json配置区域内
    
    :param person_detail_info: list 类型，含有4个值：人体的左上角x坐标、左上角y坐标、右下角x坐标、右下角y坐标
    :param roi_contour: contour 类型，由 findContours 函数找出的目标区域的最外侧轮廓
    :return: True(在区域内) or False（不在区域）
    """
    x1, y1, x2, y2 = person_detail_info
    # print ('check person info:', person_detail_info)
    
    # 人体的中心是否在设定的区域内
    x_center = (x1+x2)//2
    y_center = (y1+y2)//2

    # print ('x y center:', x_center, y_center)
    # print (type(x_center), type(y_center))

    # debug，检查识别出的轮廓，是否和预期一致
    # x, y, w, h = cv2.boundingRect(roi_contour)
    # print ("contour cfg:", x, y, w, h)

    dis = cv2.pointPolygonTest(roi_contour, (x_center, y_center), True); 

    return True if dis>=0 else False 


def analyse_monitor_person_info(recog_person_info):
    """
    分析核酸队伍中的人体信息

    :param recog_person_info: list 类型，含有若干个list，每个list含有5个值：人体的左上角x坐标、左上角y坐标、右下角x坐标、右下角y坐标、置信度
    :return: int 类型，即识别出的人体中，实际处于监控区域内的总个数（画面里识别出的人，并不一定都在核酸监控的区域内）
    """
    test_roi_contour = get_covid19_monitor_roi_contour()

    in_roi_person_nums = 0
    for x1,y1,x2,y2,conf in recog_person_info:
        person_coord = [x1,y1,x2,y2]
        if (judge_person_in_hesuan_roi(person_coord, test_roi_contour)):
            in_roi_person_nums += 1

    return in_roi_person_nums