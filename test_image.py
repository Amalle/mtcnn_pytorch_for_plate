<<<<<<< HEAD
import time
import sys
import pathlib
import logging
import cv2
from tools.test_detect import MtcnnDetector

logger = logging.getLogger("app")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
console_handler.formatter = formatter

def draw_images(img, bboxs, landmarks):
    num_face = bboxs.shape[0]
    for i in range(num_face):
        cv2.rectangle(img, (int(bboxs[i, 0]), int(bboxs[i, 1])), (int(
            bboxs[i, 2]), int(bboxs[i, 3])), (0, 255, 0), 3)
    for p in landmarks:
        for i in range(5):
            cv2.circle(img, (int(p[2 * i]), int(p[2 * i + 1])), 6, (0, 0, 255), -1)
    return img


if __name__ == '__main__':
    mtcnn_detector = MtcnnDetector(min_face_size=24, use_cuda=False)
    logger.info("Init the MtcnnDetector.")
    project_root = pathlib.Path()
    inputPath = project_root / "data" / "test_images"
    outputPath = project_root / "data" / "you_result"
    outputPath.mkdir(exist_ok=True)

    start = time.time()
    for num, input_img_filename in enumerate(inputPath.iterdir()):
        logger.info("Start to process No.{} image.".format(num))
        img_name = input_img_filename.name
        logger.info("The name of the image is {}.".format(img_name))

        img = cv2.imread(str(input_img_filename))
        RGB_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        bboxs, landmarks = mtcnn_detector.detect_face(RGB_image)
        img = draw_images(img, bboxs, landmarks)
        savePath = outputPath / img_name
        logger.info("Process complete. Save image to {}.".format(str(savePath)))

        cv2.imwrite(str(savePath), img)

    logger.info("Finish all the images.")
    logger.info("Elapsed time: {:.3f}s".format(time.time() - start))
=======
import time
import sys
import pathlib
import logging
import cv2
from tools.test_detect import MtcnnDetector

logger = logging.getLogger("app")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
console_handler.formatter = formatter

def draw_images(img, bboxs, landmarks):
    num_face = bboxs.shape[0]
    for i in range(num_face):
        cv2.rectangle(img, (int(bboxs[i, 0]), int(bboxs[i, 1])), (int(
            bboxs[i, 2]), int(bboxs[i, 3])), (0, 255, 0), 3)
    for p in landmarks:
        for i in range(5):
            cv2.circle(img, (int(p[2 * i]), int(p[2 * i + 1])), 6, (0, 0, 255), -1)
    return img


if __name__ == '__main__':
    mtcnn_detector = MtcnnDetector(min_face_size=24, use_cuda=False)
    logger.info("Init the MtcnnDetector.")
    project_root = pathlib.Path()
    inputPath = project_root / "data" / "test_images"
    outputPath = project_root / "data" / "you_result"
    outputPath.mkdir(exist_ok=True)

    start = time.time()
    for num, input_img_filename in enumerate(inputPath.iterdir()):
        logger.info("Start to process No.{} image.".format(num))
        img_name = input_img_filename.name
        logger.info("The name of the image is {}.".format(img_name))

        img = cv2.imread(str(input_img_filename))
        RGB_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        bboxs, landmarks = mtcnn_detector.detect_face(RGB_image)
        img = draw_images(img, bboxs, landmarks)
        savePath = outputPath / img_name
        logger.info("Process complete. Save image to {}.".format(str(savePath)))

        cv2.imwrite(str(savePath), img)

    logger.info("Finish all the images.")
    logger.info("Elapsed time: {:.3f}s".format(time.time() - start))
>>>>>>> e88472f491f7a4a8e9162d955659f88a773c3ea0
