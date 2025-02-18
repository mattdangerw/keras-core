import sys

from keras_core import backend as backend_module


def in_tf_graph():
    if "tensorflow" in sys.modules:
        import tensorflow as tf

        return not tf.executing_eagerly()
    return False


class DynamicBackend:
    """A class that can be used to switch from one backend to another.

    Usage:

    ```python
    backend = DynamicBackend("tensorflow")
    y = backend.square(tf.constant(...))
    backend.set_backend("jax")
    y = backend.square(jax.numpy.array(...))
    ```

    Args:
        backend: Initial backend to use (string).
    """

    def __init__(self, backend=None):
        self._backend = backend or backend_module.backend()

    def set_backend(self, backend):
        self._backend = backend

    def reset(self):
        self._backend = backend_module.backend()

    def __getattr__(self, name):
        if self._backend == "tensorflow":
            from keras_core.backend import tensorflow as tf_backend

            return getattr(tf_backend, name)
        if self._backend == "jax":
            from keras_core.backend import jax as jax_backend

            return getattr(jax_backend, name)
        if self._backend == "torch":
            from keras_core.backend import torch as torch_backend

            return getattr(torch_backend, name)
