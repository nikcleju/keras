"""Tests for utils."""

from absl.testing import parameterized
from keras import layers
from keras.dtensor import utils

import numpy as np
import tensorflow.compat.v2 as tf

from keras.dtensor.tests import test_util
from tensorflow.dtensor import python as dtensor  # pylint: disable=g-direct-tensorflow-import


class UtilsTest(test_util.DTensorBaseTest):

  def setUp(self):
    super(UtilsTest, self).setUp()
    global_ids = test_util.create_device_ids_array((2, 2))
    local_device_ids = np.ravel(global_ids).tolist()
    mesh_dict = {
        'CPU':
            dtensor.Mesh(['X', 'Y'], global_ids,
                         local_device_ids,
                         test_util.create_device_list((2, 2), 'CPU'))
    }
    self.mesh = self.configTestMesh(mesh_dict)
    self.layout = dtensor.Layout.replicated(self.mesh, rank=1)

  @parameterized.named_parameters(
      ('Dense', layers.Dense, {'units': 4}, ['kernel_layout', 'bias_layout']),
      ('Conv2D', layers.Conv2D, {'filters': 2, 'kernel_size': 3},
       ['kernel_layout', 'bias_layout']),
      ('BatchNorm', layers.BatchNormalization, {},
       ['beta_layout', 'gamma_layout', 'moving_mean_layout',
        'moving_variance_layout']),
      ('Embedding', layers.Embedding, {'input_dim': 100, 'output_dim': 20},
       ['embeddings_layout']),
      (' PReLU', layers. PReLU, {}, ['alpha_layout']),
      ('SeparableConv2D', layers.SeparableConv2D,
       {'filters': 2, 'kernel_size': 3},
       ['depthwise_layout', 'pointwise_layout', 'bias_layout']),
      # TODO(scottzhu): Probably add more coverage for all the layers.
  )
  def test_all_layout_decorator(self, layer_cls, init_args, layout_args):

    layer_cls.__init__ = utils.allow_initializer_layout(layer_cls.__init__)

    # Make sure we don't set the layout attribute if the init kwargs is not
    # provided.
    layer = layer_cls(**init_args)
    for layout_arg in layout_args:
      self.assertFalse(hasattr(layer, layout_arg))

    layout_kwargs = {k: self.layout for k in layout_args}
    init_args.update(layout_kwargs)
    layer = layer_cls(**init_args)

    for layout_arg in layout_args:
      self.assertEqual(getattr(layer, layout_arg), self.layout)


if __name__ == '__main__':
  tf.test.main()
