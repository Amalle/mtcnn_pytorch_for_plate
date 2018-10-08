#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-8-1 上午9:08
# @Author  : xiezheng
# @Site    : 
# @File    : test_youModel_images.py

import time
import sys
import pathlib
import logging
import cv2
from tools.train_detect import MtcnnDetector

logger = logging.getLogger("app")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
console_handler.formatter = formatter  # 也可以直接给formatter赋值

plate_color = ['blue','yellow','green','white','black']
plate_layer = ['single','double']
plate_type  = ['tradition','new_energy']


def draw_images(img, bboxs, landmarks, attrs, color=(0,255,0)):  # 在图片上绘制人脸框及特征点
    num_face = bboxs.shape[0]
    for i in range(num_face):
        cv2.rectangle(img, (int(bboxs[i, 0]), int(bboxs[i, 1])), (int(
            bboxs[i, 2]), int(bboxs[i, 3])), color, 3)
    if landmarks != []:
        for p in landmarks:
            for i in range(4):
                cv2.circle(img, (int(p[2 * i]), int(p[2 * i + 1])), 3, (0,0,255), -1)
    i = 0
    if attrs != []:
        for a in attrs:
            txt = plate_color[a[0]]+' '+plate_layer[a[1]]+' '+plate_type[a[2]]
            cv2.putText(img,txt,(int(bboxs[i, 0]), int(bboxs[i, 1])),cv2.FONT_HERSHEY_COMPLEX,2,(0,0,255),5)
            i += 1
    return img


if __name__ == '__main__':
    mtcnn_detector = MtcnnDetector(p_model_path="./plate_annotations/pnet/log_bs512_lr0.010_0930/check_point/model_050.pth",
                                   r_model_path="./plate_annotations/rnet/log_bs512_lr0.001_0930/check_point/model_050.pth",
                                   o_model_path="./plate_annotations/onet/log_bs512_lr0.001_0930/check_point/model_050.pth",
                                   min_face_size=60,
                                   use_cuda=False)   # 加载模型参数，构造检测器
    logger.info("Init the MtcnnDetector.")
    project_root = pathlib.Path()
    inputPath = project_root / "data" / "test_new_energy"
    outputPath = project_root / "data" / "test_new_energy/results"
    outputPath.mkdir(exist_ok=True)

    start = time.time()
    corr = 0
    count = 0
    for num, input_img_filename in enumerate(inputPath.iterdir()):
        logger.info("Start to process No.{} image.".format(num))
        img_name = input_img_filename.name
        logger.info("The name of the image is {}.".format(img_name))

        img = cv2.imread(str(input_img_filename))
        if img is None:
            continue
        RGB_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        bboxs, landmarks, attrs, pboxes, rboxes = mtcnn_detector.detect_face(RGB_image)  # 检测得到bboxs以及特征点
        if len(bboxs) > 0:
            corr += 1
        img = draw_images(img, pboxes, [], [], (255,0,0))
        img = draw_images(img, rboxes, [], [], (0,255,255))
        img = draw_images(img, bboxs, landmarks, attrs)  # 得到绘制人脸框及特征点的图片
        savePath = outputPath / img_name  # 图片保存路径
        logger.info("Process complete. Save image to {}.".format(str(savePath)))

        cv2.imwrite(str(savePath), img)  # 保存图片
        count += 1
    
    print(float(corr)/count)

    logger.info("Finish all the images.")
    logger.info("Elapsed time: {:.3f}s".format(time.time() - start))