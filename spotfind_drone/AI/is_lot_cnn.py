import tensorflow as tf
import numpy as np
import os



class IsLotCNN(object):

    def __init__(self, model_filepath='frozen_networks/is_lot_frozen_network.pb'):
        self.model_filepath = os.path.dirname(os.path.abspath(__file__))+'/'+model_filepath
        self.load_graph(model_filepath=self.model_filepath)

    def load_graph(self, model_filepath):
        self.graph = tf.Graph()
        self.sess = tf.InteractiveSession(graph=self.graph)

        with tf.gfile.GFile(model_filepath, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())

        self.input = tf.placeholder(np.float32, shape = [None, 128, 128, 1], name='input')
        self.keep_prob = tf.placeholder(tf.float32, name='keep_prob')

        tf.import_graph_def(graph_def, {'input': self.input, 'keep_prob': self.keep_prob})

    def predict(self, data):
        output_tensor = self.graph.get_tensor_by_name("import/output:0")
        output = self.sess.run(output_tensor, feed_dict={self.input: data, self.keep_prob: 1.0})

        return output
