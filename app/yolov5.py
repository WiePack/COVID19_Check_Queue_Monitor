# -*- coding: utf-8 -*-
"""
yolov5 模型推理模块
"""
import numpy as np 
import os
import cv2

class YOLOV5:
    def __init__(self, modelPath, prob_threshold=0.25, iou_threshold=0.45):
        self.image_shape = (640, 640)
        self.prob_threshold = prob_threshold
        self.iou_threshold = iou_threshold
        self.net = cv2.dnn.readNet(modelPath)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    @property
    def name(self):
        return self.__class__.__name__

    def pre_process(self, img):
        row, col = img.shape[:2]
        _max = max(col, row)
        result = np.zeros((_max, _max, 3), np.uint8)
        result[0:row, 0:col] = img 
        blob = cv2.dnn.blobFromImage(result, 1/255.0, self.image_shape, swapRB=True, crop=False)
        return blob 

    def infer(self, blob):
        self.net.setInput(blob)
        preds = self.net.forward()
        return preds

    def post_process(self, preds, max_width_height):
        confidences = []
        boxes = []
        output_data = preds[0]
        rows = output_data.shape[0]

        x_factor = max_width_height / self.image_shape[0]
        y_factor =  max_width_height / self.image_shape[1]

        for r in range(rows):
            row = output_data[r]
            confidence = row[4]
            if confidence >= self.prob_threshold:
                classes_scores = row[5:]
                _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
                class_id = max_indx[1]
                if (classes_scores[class_id] > self.prob_threshold):
                    confidences.append(confidence)
                    x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
                    left = int((x - 0.5 * w) * x_factor)
                    top = int((y - 0.5 * h) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)
                    box = np.array([left, top, width, height])
                    boxes.append(box.tolist())

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.prob_threshold, self.iou_threshold) 

        detect_result_info = []

        for i in indexes:
            detect_info = []
            boxes[i] = [boxes[i][0], boxes[i][1], boxes[i][0]+boxes[i][2]-1, boxes[i][1]+boxes[i][3]-1] # 重新组合成我们想要的形式
            detect_info.extend(boxes[i])
            detect_info.append(round(confidences[i], 2))
            detect_result_info.append(detect_info)

        return detect_result_info