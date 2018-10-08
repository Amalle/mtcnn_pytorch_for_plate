import sys
sys.path.append('./')

import os
import argparse
import numpy as np
import cv2
import numpy.random as npr
from tools.utils import IoU
import config


def gen_pnet_data(data_dir, anno_file, prefix):
    neg_save_dir = os.path.join(data_dir, "12/negative")
    pos_save_dir = os.path.join(data_dir, "12/positive")
    part_save_dir = os.path.join(data_dir, "12/part")

    for dir_path in [neg_save_dir, pos_save_dir, part_save_dir]:  # make
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

#     save_dir = os.path.join(data_dir, "pnet")
#     if not os.path.exists(save_dir):
#         os.mkdir(save_dir)

    post_save_file = os.path.join(
        config.ANNO_STORE_DIR, config.PNET_POSTIVE_ANNO_FILENAME)
    neg_save_file = os.path.join(
        config.ANNO_STORE_DIR, config.PNET_NEGATIVE_ANNO_FILENAME)
    part_save_file = os.path.join(
        config.ANNO_STORE_DIR, config.PNET_PART_ANNO_FILENAME)

    f1 = open(post_save_file, 'w')
    f2 = open(neg_save_file, 'w')
    f3 = open(part_save_file, 'w')

    with open(anno_file, 'r') as f:
        annotations = f.readlines()

    num = len(annotations)
    print("%d pics in total" % num)

    p_idx = 0  # positive examples index
    n_idx = 0  # negative examples index
    d_idx = 0  # partface examples index
    idx = 0  # pics index
    box_idx = 0  # boxes index

    for annotation in annotations:
        annotation = annotation.strip().split(' ')
        im_path = os.path.join(prefix, annotation[0])  # image_path
        print(im_path)
        bbox = list(map(float, annotation[1:]))  # map()函数是将func作用于seq中的每一个元素，并将所有的调用的结果作为一个list返回
        boxes = np.array(bbox, dtype=np.int32).reshape(-1, 4)  # N*4 dim array
        img = cv2.imread(im_path)
        idx += 1

        if idx % 100 == 0:
            print(idx, "images done")

        height, width, channel = img.shape

        neg_num = 0
        while neg_num < 50:
            size = npr.randint(12, min(width, height) / 2)
            nx = npr.randint(0, width - size)
            ny = npr.randint(0, height - size)
            crop_box = np.array([nx, ny, nx + size, ny + size])

            Iou = IoU(crop_box, boxes)

            if np.max(Iou) < 0.3:
                # Iou with all gts must below 0.3
                save_file = os.path.join(neg_save_dir, "%s.jpg" % n_idx)  # save neg image
                f2.write(save_file + ' 0\n')
                cropped_im = img[ny: ny + size, nx: nx + size, :]
                resized_im = cv2.resize(cropped_im, (12, 12), interpolation=cv2.INTER_LINEAR)
                cv2.imwrite(save_file, resized_im)
                n_idx += 1
                neg_num += 1

        for box in boxes:
            # box (x_left, y_top, x_right, y_bottom)
            x1, y1, x2, y2 = box
            w = x2 - x1
            h = y2 - y1

            # ignore small faces
            # in case the ground truth boxes of small faces are not accurate
            if max(w, h) < 40 or x1 < 0 or y1 < 0:
                continue

            # generate negative examples that have overlap with gt
            for i in range(5):
                size = npr.randint(12, min(width, height) / 2)
                # delta_x and delta_y are offsets of (x1, y1)
                delta_x = npr.randint(max(-size, -x1), w)
                delta_y = npr.randint(max(-size, -y1), h)
                nx1 = max(0, x1 + delta_x)
                ny1 = max(0, y1 + delta_y)

                if nx1 + size > width or ny1 + size > height:
                    continue
                crop_box = np.array([nx1, ny1, nx1 + size, ny1 + size])
                Iou = IoU(crop_box, boxes)

                if np.max(Iou) < 0.3:
                    # Iou with all gts must below 0.3
                    save_file = os.path.join(neg_save_dir, "%s.jpg" % n_idx)
                    cropped_im = img[ny1: ny1 + size, nx1: nx1 + size, :]
                    resized_im = cv2.resize(cropped_im, (12, 12), interpolation=cv2.INTER_LINEAR)
                    f2.write(save_file + ' 0\n')  # neg samples with label 0
                    cv2.imwrite(save_file, resized_im)
                    n_idx += 1

            # generate positive examples and part faces
            # 每个box随机生成50个box，Iou>=0.65的作为positive examples，0.4<=Iou<0.65的作为part faces，其他忽略
            for i in range(50):
                # size = npr.randint(int(min(w, h) * 0.8),
                #                    np.ceil(1.25 * max(w, h)))
                size_w = npr.randint(int(w * 0.8), np.ceil(1.25 * w))
                # size_h = npr.randint(int(h * 0.8), np.ceil(1.25 * h))
                size_h = int(size_w * h/w)

                # delta here is the offset of box center
                delta_x = npr.randint(-w * 0.2, w * 0.2)
                delta_y = npr.randint(-h * 0.2, h * 0.2)

                nx1 = int(max(x1 + w / 2 + delta_x - size_w / 2, 0))
                ny1 = int(max(y1 + h / 2 + delta_y - size_h / 2, 0))
                nx2 = int(nx1 + size_w)
                ny2 = int(ny1 + size_h)

                if nx2 >= width or ny2 >= height:
                    continue
                crop_box = np.array([nx1, ny1, nx2, ny2])

                # bbox偏移量的计算，由 x1 = nx1 + float(size)*offset_x1 推导而来
                offset_x1 = (x1 - nx1) / float(size_w)
                offset_y1 = (y1 - ny1) / float(size_h)
                offset_x2 = (x2 - nx2) / float(size_w)
                offset_y2 = (y2 - ny2) / float(size_h)

                cropped_im = img[ny1: ny2, nx1: nx2, :]
                resized_im = cv2.resize(
                    cropped_im, (12, 12), interpolation=cv2.INTER_LINEAR)

                box_ = box.reshape(1, -1)
                if IoU(crop_box, box_) >= 0.7:
                    save_file = os.path.join(pos_save_dir, "%s.jpg" % p_idx)
                    f1.write(save_file + ' 1 %.2f %.2f %.2f %.2f\n' %
                             (offset_x1, offset_y1, offset_x2, offset_y2))
                    cv2.imwrite(save_file, resized_im)
                    p_idx += 1
                elif IoU(crop_box, box_) >= 0.4:
                    save_file = os.path.join(part_save_dir, "%s.jpg" % d_idx)
                    f3.write(save_file + ' -1 %.2f %.2f %.2f %.2f\n' %
                             (offset_x1, offset_y1, offset_x2, offset_y2))
                    cv2.imwrite(save_file, resized_im)
                    d_idx += 1
            box_idx += 1
        print("%s/%s images done, pos: %s part: %s neg: %s" %
                (idx, num, p_idx, d_idx, n_idx))

    f1.close()
    f2.close()
    f3.close()


def parse_args():
    parser = argparse.ArgumentParser(description='generate pnet training data',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--face_traindata_store', dest='traindata_store', help='face train data temporary folder',
                        default=config.TRAIN_DATA_DIR, type=str)
    parser.add_argument('--anno_file', dest='annotation_file', help='wider face original annotation file',
                        default=os.path.join(config.ANNO_STORE_DIR, "image_list.txt"), type=str)
    parser.add_argument('--prefix_path', dest='prefix_path', help='annotation file image prefix root path',
                        default='/users/maqiao/DNN/MTCNN/data20180925', type=str)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    gen_pnet_data(args.traindata_store, args.annotation_file, args.prefix_path)
