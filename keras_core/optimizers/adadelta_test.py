import numpy as np

from keras_core import backend
from keras_core import testing
from keras_core.optimizers.adadelta import Adadelta


class AdadeltaTest(testing.TestCase):
    def test_config(self):
        optimizer = Adadelta(
            learning_rate=0.5,
            rho=0.9,
            epsilon=1e-5,
        )
        self.run_class_serialization_test(optimizer)

    def test_single_step(self):
        optimizer = Adadelta(learning_rate=0.5)
        grads = np.array([1.0, 6.0, 7.0, 2.0])
        vars = backend.Variable([1.0, 2.0, 3.0, 4.0])
        optimizer.apply_gradients(zip([grads], [vars]))
        self.assertAllClose(
            vars, [0.9993, 1.9993, 2.9993, 3.9993], rtol=1e-4, atol=1e-4
        )

    def test_weight_decay(self):
        grads, var1, var2, var3 = (
            np.zeros(()),
            backend.Variable(2.0),
            backend.Variable(2.0, name="exclude"),
            backend.Variable(2.0),
        )
        optimizer_1 = Adadelta(learning_rate=1.0, weight_decay=0.004)
        optimizer_1.apply_gradients(zip([grads], [var1]))

        optimizer_2 = Adadelta(learning_rate=1.0, weight_decay=0.004)
        optimizer_2.exclude_from_weight_decay(var_names=["exclude"])
        optimizer_2.apply_gradients(zip([grads, grads], [var1, var2]))

        optimizer_3 = Adadelta(learning_rate=1.0, weight_decay=0.004)
        optimizer_3.exclude_from_weight_decay(var_list=[var3])
        optimizer_3.apply_gradients(zip([grads, grads], [var1, var3]))

        self.assertAlmostEqual(var1.numpy(), 1.9760959, decimal=6)
        self.assertAlmostEqual(var2.numpy(), 2.0, decimal=6)
        self.assertAlmostEqual(var3.numpy(), 2.0, decimal=6)

    def test_correctness_with_golden(self):
        optimizer = Adadelta(learning_rate=1.0, rho=0.8, epsilon=1e-6)

        x = backend.Variable(np.ones([10]))
        grads = np.arange(0.1, 1.1, 0.1)
        first_grads = np.full((10,), 0.01)

        golden = np.tile(
            [[0.9978], [0.9947], [0.9915], [0.9882], [0.9849]], (1, 10)
        )

        optimizer.apply_gradients(zip([first_grads], [x]))
        for i in range(5):
            self.assertAllClose(x, golden[i], rtol=5e-4, atol=5e-4)
            optimizer.apply_gradients(zip([grads], [x]))

    def test_clip_norm(self):
        optimizer = Adadelta(clipnorm=1)
        grad = [np.array([100.0, 100.0])]
        clipped_grad = optimizer._clip_gradients(grad)
        self.assertAllClose(clipped_grad[0], [2**0.5 / 2, 2**0.5 / 2])

    def test_clip_value(self):
        optimizer = Adadelta(clipvalue=1)
        grad = [np.array([100.0, 100.0])]
        clipped_grad = optimizer._clip_gradients(grad)
        self.assertAllClose(clipped_grad[0], [1.0, 1.0])
