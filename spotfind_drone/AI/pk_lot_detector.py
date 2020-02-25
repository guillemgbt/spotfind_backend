import tensorflow as tf
import numpy as np
from PIL import Image
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


class ParkingLotDetector(object):
    def __init__(self, model_filepath='frozen_networks/frcnn_resnet50_frozen_network.pb'):
        self.model_filepath = os.path.dirname(os.path.abspath(__file__)) + '/' + model_filepath
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.model_filepath, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            self.d_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            self.d_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.d_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_d = self.detection_graph.get_tensor_by_name('num_detections:0')
        self.sess = tf.Session(graph=self.detection_graph)

    def get_classification(self, img_path):

        image = ParkingLotDetector.load_image_into_numpy_array(Image.open(img_path))

        # Bounding Box Detection.
        with self.detection_graph.as_default():
            # Expand dimension since the model expects image to have shape [1, None, None, 3].
            img_expanded = np.expand_dims(image, axis=0)
            (boxes, scores, classes, num) = self.sess.run(
                [self.d_boxes, self.d_scores, self.d_classes, self.num_d],
                feed_dict={self.image_tensor: img_expanded})
        return boxes, scores, classes, num


    @staticmethod
    def load_image_into_numpy_array(image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


class FasterRCNNResnet50PKLotDetector(ParkingLotDetector):
    def __init__(self):
        super().__init__(model_filepath='frozen_networks/frcnn_resnet50_frozen_network.pb')


class SSDMobilenetV2PKLotDetector(ParkingLotDetector):
    def __init__(self):
        super().__init__(model_filepath='frozen_networks/ssd_mobilenet_v2_frozen_network.pb')


class SSDInceptionPKLotDetector(ParkingLotDetector):
    def __init__(self):
        super().__init__(model_filepath='frozen_networks/ssd_inception_frozen_network.pb')
