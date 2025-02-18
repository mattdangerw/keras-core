import numpy as np

from keras_core import layers
from keras_core import testing
from keras_core.layers.rnn.rnn_test import OneStateRNNCell
from keras_core.layers.rnn.rnn_test import TwoStatesRNNCell


class StackedRNNTest(testing.TestCase):
    def test_basics(self):
        self.run_layer_test(
            layers.RNN,
            init_kwargs={
                "cell": [
                    OneStateRNNCell(3),
                    OneStateRNNCell(4),
                    OneStateRNNCell(5),
                ],
            },
            input_shape=(2, 3, 4),
            expected_output_shape=(2, 5),
            expected_num_trainable_weights=6,
            expected_num_non_trainable_weights=0,
            expected_num_seed_generators=0,
            supports_masking=True,
            custom_objects={"OneStateRNNCell": OneStateRNNCell},
        )
        self.run_layer_test(
            layers.RNN,
            init_kwargs={
                "cell": [
                    OneStateRNNCell(3),
                    OneStateRNNCell(4),
                    OneStateRNNCell(5),
                ],
                "return_sequences": True,
            },
            input_shape=(2, 3, 4),
            expected_output_shape=(2, 3, 5),
            expected_num_trainable_weights=6,
            expected_num_non_trainable_weights=0,
            expected_num_seed_generators=0,
            supports_masking=True,
            custom_objects={"OneStateRNNCell": OneStateRNNCell},
        )
        # Two-state case.
        self.run_layer_test(
            layers.RNN,
            init_kwargs={
                "cell": [
                    TwoStatesRNNCell(3),
                    TwoStatesRNNCell(4),
                    TwoStatesRNNCell(5),
                ],
            },
            input_shape=(2, 3, 4),
            expected_output_shape=(2, 5),
            expected_num_trainable_weights=9,
            expected_num_non_trainable_weights=0,
            expected_num_seed_generators=0,
            supports_masking=True,
            custom_objects={"TwoStatesRNNCell": TwoStatesRNNCell},
        )
        self.run_layer_test(
            layers.RNN,
            init_kwargs={
                "cell": [
                    TwoStatesRNNCell(3),
                    TwoStatesRNNCell(4),
                    TwoStatesRNNCell(5),
                ],
                "return_sequences": True,
            },
            input_shape=(2, 3, 4),
            expected_output_shape=(2, 3, 5),
            expected_num_trainable_weights=9,
            expected_num_non_trainable_weights=0,
            expected_num_seed_generators=0,
            supports_masking=True,
            custom_objects={"TwoStatesRNNCell": TwoStatesRNNCell},
        )

    def test_correctness_single_state_stack(self):
        sequence = np.arange(24).reshape((2, 3, 4)).astype("float32")
        layer = layers.RNN([OneStateRNNCell(3), OneStateRNNCell(2)])
        output = layer(sequence)
        self.assertAllClose(
            np.array([[786.0, 786.0], [4386.0, 4386.0]]), output
        )

        layer = layers.RNN(
            [OneStateRNNCell(3), OneStateRNNCell(2)], return_sequences=True
        )
        output = layer(sequence)
        self.assertAllClose(
            np.array(
                [
                    [[18.0, 18.0], [156.0, 156.0], [786.0, 786.0]],
                    [[162.0, 162.0], [1020.0, 1020.0], [4386.0, 4386.0]],
                ]
            ),
            output,
        )

        layer = layers.RNN(
            [OneStateRNNCell(3), OneStateRNNCell(2)], return_state=True
        )
        output, state_1, state_2 = layer(sequence)
        self.assertAllClose(
            np.array([[786.0, 786.0], [4386.0, 4386.0]]), output
        )
        self.assertAllClose(
            np.array([[158.0, 158.0, 158.0], [782.0, 782.0, 782.0]]), state_1
        )
        self.assertAllClose(
            np.array([[786.0, 786.0], [4386.0, 4386.0]]), state_2
        )

        layer = layers.RNN(
            [OneStateRNNCell(3), OneStateRNNCell(2)],
            return_sequences=True,
            return_state=True,
        )
        output, state_1, state_2 = layer(sequence)
        self.assertAllClose(
            np.array(
                [
                    [[18.0, 18.0], [156.0, 156.0], [786.0, 786.0]],
                    [[162.0, 162.0], [1020.0, 1020.0], [4386.0, 4386.0]],
                ]
            ),
            output,
        )
        self.assertAllClose(
            np.array([[158.0, 158.0, 158.0], [782.0, 782.0, 782.0]]), state_1
        )
        self.assertAllClose(
            np.array([[786.0, 786.0], [4386.0, 4386.0]]), state_2
        )

    def test_correctness_two_states_stack(self):
        sequence = np.arange(24).reshape((2, 3, 4)).astype("float32")
        layer = layers.RNN([TwoStatesRNNCell(3), TwoStatesRNNCell(2)])
        output = layer(sequence)
        self.assertAllClose(
            np.array([[3144.0, 3144.0], [17544.0, 17544.0]]), output
        )

        layer = layers.RNN(
            [TwoStatesRNNCell(3), TwoStatesRNNCell(2)], return_sequences=True
        )
        output = layer(sequence)
        self.assertAllClose(
            np.array(
                [
                    [[72.0, 72.0], [624.0, 624.0], [3144.0, 3144.0]],
                    [[648.0, 648.0], [4080.0, 4080.0], [17544.0, 17544.0]],
                ]
            ),
            output,
        )

        layer = layers.RNN(
            [TwoStatesRNNCell(3), TwoStatesRNNCell(2)], return_state=True
        )
        output, state_1, state_2 = layer(sequence)

        self.assertAllClose(
            np.array([[3144.0, 3144.0], [17544.0, 17544.0]]), output
        )
        self.assertAllClose(
            np.array([[158.0, 158.0, 158.0], [782.0, 782.0, 782.0]]), state_1[0]
        )
        self.assertAllClose(
            np.array([[158.0, 158.0, 158.0], [782.0, 782.0, 782.0]]), state_1[1]
        )
        self.assertAllClose(
            np.array([[1572.0, 1572.0], [8772.0, 8772.0]]), state_2[0]
        )
        self.assertAllClose(
            np.array([[1572.0, 1572.0], [8772.0, 8772.0]]), state_2[1]
        )

    def test_statefullness_single_state_stack(self):
        sequence = np.arange(24).reshape((2, 3, 4)).astype("float32")
        layer = layers.RNN(
            [OneStateRNNCell(3), OneStateRNNCell(2)], stateful=True
        )
        layer(sequence)
        output = layer(sequence)
        self.assertAllClose(
            np.array([[34092.0, 34092.0], [173196.0, 173196.0]]), output
        )

    def test_statefullness_two_states_stack(self):
        sequence = np.arange(24).reshape((2, 3, 4)).astype("float32")
        layer = layers.RNN(
            [TwoStatesRNNCell(3), TwoStatesRNNCell(2)], stateful=True
        )
        layer(sequence)
        output = layer(sequence)
        self.assertAllClose(
            np.array([[136368.0, 136368.0], [692784.0, 692784.0]]), output
        )
