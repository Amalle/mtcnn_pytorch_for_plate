import sys
sys.path.append('./')

import argparse
import os
import pickle

import time

import numpy as np

import tools.vision as vision
import config
import cv2
from tools.train_detect import MtcnnDetector
from tools.imagedb import ImageDB
from tools.image_reader import TestImageLoader
from tools.utils import IoU, convert_to_square

os.environ['CUDA_DEVICE_ORDER'] = "PCI_BUS_ID"
os.environ['CUDA_VISIBLE_DEVICES'] = "1"


def gen_rnet_data(data_dir, anno_file, pnet_model_file, prefix_path='', use_cuda=True, vis=False):
    # load the pnet and pnet_detector

    mtcnn_detector = MtcnnDetector(p_model_path=pnet_model_file,
                                   r_model_path=None,
                                   o_model_path=None,
                                   min_face_size=12,
                                   use_cuda=True)
    device = mtcnn_detector.device

    imagedb = ImageDB(anno_file, mode="test", prefix_path=prefix_path)
    imdb = imagedb.load_imdb()
    image_reader = TestImageLoader(imdb, 1, False)

    all_boxes = []
    batch_idx = 0

    for databatch in image_reader:
        if batch_idx % 100 == 0:
            print("%d images done" % batch_idx)
        im = databatch
        t = time.time()
        boxes, boxes_align = mtcnn_detector.detect_pnet(im)
        if boxes_align is None:
            all_boxes.append(np.array([]))
            continue
        if vis:
            vision.vis_face(im, boxes_align)

        t1 = time.time() - t
        print('time cost for image {} / {} : {:.4f}'.format(batch_idx, image_reader.size, t1))
        all_boxes.append(boxes_align)
        batch_idx += 1

    save_path = config.TRAIN_DATA_DIR
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    save_file = os.path.join(
        save_path, "pnet_detections_%d.pkl" % int(time.time()))

    with open(save_file, 'wb') as f:
        pickle.dump(all_boxes, f, pickle.HIGHEST_PROTOCOL)

    # save_file = '/home/liujing/Codes/MTCNN/data/pnet_detections_1532530263.pkl'
    get_rnet_sample_data(data_dir, anno_file, save_file, prefix_path)


def get_rnet_sample_data(data_dir, anno_file, det_boxes_file, prefix_path):
    neg_save_dir = os.path.join(data_dir, "24/negative")
    pos_save_dir = os.path.join(data_dir, "24/positive")
    part_save_dir = os.path.join(data_dir, "24/part")

    for dir_path in [neg_save_dir, pos_save_dir, part_save_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # load ground truth from annotation file
    # format of each line: image/path [x1, y1, x2, y2] for each gt_box in this image
    with open(anno_file, 'r') as f:
        annotations = f.readlines()

    image_size = 24
    im_idx_list = list()
    gt_boxes_list = list()
    num_of_images = len(annotations)
    print("processing %d images in total" % num_of_images)
    for annotation in annotations:
        # for i in range(10):
        annotation = annotation.strip().split(' ')
        # annotation = annotations[i].strip().split(' ')
        im_idx = os.path.join(prefix_path, annotation[0])
        boxes = list(map(float, annotation[1:]))
        boxes = np.array(boxes, dtype=np.float32).reshape(-1, 4)
        im_idx_list.append(im_idx)
        gt_boxes_list.append(boxes)

    save_path = config.ANNO_STORE_DIR
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    f1 = open(os.path.join(save_path, 'pos_%d.txt' % image_size), 'w')
    f2 = open(os.path.join(save_path, 'neg_%d.txt' % image_size), 'w')
    f3 = open(os.path.join(save_path, 'part_%d.txt' % image_size), 'w')

    det_handle = open(det_boxes_file, 'rb')
    det_boxes = pickle.load(det_handle)
    print(len(det_boxes), num_of_images)
    assert len(det_boxes) == num_of_images, "incorrect detections or ground truths"

    # index of neg, pos and part face, used as their image names
    n_idx = 0
    p_idx = 0
    d_idx = 0
    image_done = 0
    for im_idx, dets, gts in zip(im_idx_list, det_boxes, gt_boxes_list):
        image_done += 1
        if image_done % 100 == 0:
            print("%d images done" % image_done)
        if dets.shape[0] == 0:
            continue
        img = cv2.imread(im_idx)
        # dets = convert_to_square(dets)
        dets[:, 0:4] = np.round(dets[:, 0:4])

        # each image have at most 50 neg_samples
        cur_n_idx = 0
        for box in dets:
            x_left, y_top, x_right, y_bottom = box[0:4].astype(int)
            width = x_right - x_left
            height = y_bottom - y_top
            # ignore box that is too small or beyond image border
            if width < 20 or height < 20 or x_left <= 0 or y_top <= 0 or x_right >= img.shape[1] or y_bottom >= img.shape[0]:
                continue
            # compute intersection over union(IoU) between current box and all gt boxes
            Iou = IoU(box, gts)
            cropped_im = img[y_top:y_bottom, x_left:x_right, :]
            resized_im = cv2.resize(cropped_im, (image_size, image_size),
                                    interpolation=cv2.INTER_LINEAR)
            # save negative images and write label

            if np.max(Iou) < 0.3:
                # Iou with all gts must below 0.3
                cur_n_idx += 1
                if cur_n_idx <= 50:
                    save_file = os.path.join(neg_save_dir, "%s.jpg" % n_idx)
                    f2.write(save_file + ' 0\n')
                    cv2.imwrite(save_file, resized_im)
                    n_idx += 1
            else:
                # find gt_box with the highest iou
                idx = np.argmax(Iou)
                assigned_gt = gts[idx]
                x1, y1, x2, y2 = assigned_gt

                # compute bbox reg label
                offset_x1 = (x1 - x_left) / float(width)
                offset_y1 = (y1 - y_top) / float(height)
                offset_x2 = (x2 - x_right) / float(width)
                offset_y2 = (y2 - y_bottom) / float(height)

                # save positive and part-face images and write labels
                if np.max(Iou) >= 0.65:
                    save_file = os.path.join(pos_save_dir, "%s.jpg" % p_idx)
                    f1.write(save_file + ' 1 %.2f %.2f %.2f %.2f\n' % (
                        offset_x1, offset_y1, offset_x2, offset_y2))
                    cv2.imwrite(save_file, resized_im)
                    p_idx += 1

                elif np.max(Iou) >= 0.4:
                    save_file = os.path.join(part_save_dir, "%s.jpg" % d_idx)
                    f3.write(save_file + ' -1 %.2f %.2f %.2f %.2f\n' % (
                        offset_x1, offset_y1, offset_x2, offset_y2))
                    cv2.imwrite(save_file, resized_im)
                    d_idx += 1
        print("%s images done, pos: %s part: %s neg: %s" %
                  (im_idx, p_idx, d_idx, n_idx))

    f1.close()
    f2.close()
    f3.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Test mtcnn',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--face_traindata_store', dest='traindata_store', help='dface train data temporary folder',
                        default=config.TRAIN_DATA_DIR, type=str)
    parser.add_argument('--anno_file', dest='annotation_file', help='wider face original annotation file',
                        default=os.path.join(config.ANNO_STORE_DIR, "image_list.txt"), type=str)
    parser.add_argument('--pmodel_file', dest='pnet_model_file', help='PNet model file path',
                        default='/users/maqiao/DNN/MTCNN/mtcnn_pytorch/plate_annotations/pnet/log_bs512_lr0.010_0907/check_point/model_050.pth', type=str)
    parser.add_argument('--gpu', dest='use_cuda', help='with gpu',
                        default=config.USE_CUDA, type=bool)
    parser.add_argument('--prefix_path', dest='prefix_path', help='annotation file image prefix root path',
                        default='/users/maqiao/DNN/MTCNN/data20180925', type=str)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    gen_rnet_data(args.traindata_store, args.annotation_file,
                  args.pnet_model_file, args.prefix_path, args.use_cuda)
