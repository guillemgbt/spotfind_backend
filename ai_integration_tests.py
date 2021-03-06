import os
import django
import cv2
import matplotlib.image as mpimg


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotfind_backend.settings")
django.setup()

from spotfind_drone.AI.is_lot_cnn import IsLotCNN
from spotfind_drone.AI.pk_lot_detector import *


def predict_drone_img_to_isLot_prob():
    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    img = cv2.imread(img_path)
    cnn = IsLotCNN()
    out = cnn.predict(image=img)
    print('-> PROB: {} being lot for image {}'.format(out, img_path))


def predict_drone_img_lot_detection_frcnn_resnet50():
    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    detector = FasterRCNNResnet50PKLotDetector()
    boxes = detector.get_classification_from_path(img_path=img_path, confidence=0.8)

    box = boxes[0].get_box()
    occ = boxes[0].get_class()
    confidence = boxes[0].confidence
    print('-> First PKLot detection with FRCNNResnet50: {}, {}, at {} confidance level'.format(box, occ, confidence))


def predict_drone_img_lot_detection_ssd_mobilenet_v2():
    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    detector = SSDMobilenetV2PKLotDetector()
    boxes = detector.get_classification_from_path(img_path=img_path, confidence=0.8)

    box = boxes[0].get_box()
    occ = boxes[0].get_class()
    confidence = boxes[0].confidence
    print('-> First PKLot detection with SSdMobilenetV2: {}, {}, at {} confidance level'.format(box, occ, confidence))


def predict_drone_img_lot_detection_ssd_inception():
    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    detector = SSDInceptionPKLotDetector()
    boxes = detector.get_classification_from_path(img_path=img_path, confidence=0.8)

    box = boxes[0].get_box()
    occ = boxes[0].get_class()
    confidence = boxes[0].confidence
    print('-> First PKLot detection with SSDInception: {}, {}, at {} confidance level'.format(box, occ, confidence))


def predict_drone_img_lot_detection_frcnn_inception():
    img_path = 'spotfind_drone/test_drone_images/2.jpg'
    detector = FasterRCNNInceptionPKLotDetector()
    boxes = detector.get_classification_from_path(img_path=img_path, confidence=0.8)

    box = boxes[0].get_box()
    occ = boxes[0].get_class()
    confidence = boxes[0].confidence
    print('-> First PKLot detection with FasterRCNNInception: {}, {}, at {} confidance level'.format(box, occ, confidence))


def main():
    predict_drone_img_to_isLot_prob()
    predict_drone_img_lot_detection_frcnn_resnet50()
    predict_drone_img_lot_detection_ssd_mobilenet_v2()
    predict_drone_img_lot_detection_ssd_inception()
    predict_drone_img_lot_detection_frcnn_inception()


if __name__ == "__main__":
    main()

