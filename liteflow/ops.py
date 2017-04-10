"""Various tensot operators."""

import tensorflow as tf


def _trim(tensor, width):
    """Trim the tensor along the -1 axis to the target width."""
    begin = [0, 0, 0]
    size = tf.concat([tf.shape(tensor)[:2], [width]], axis=0)
    trimmed = tf.slice(tensor, begin=begin, size=size)
    return trimmed


def trim(tensor, width):
    """Trim the tensor on the -1 axis.

    Trims a given 3D tensor of shape `[batch, length, in_width]` to
    a smaller tensor of shape `[batch, length, width]`, along the -1
    axis. If the `width` argument is greater or equal than the actual
    width of the tensor, no operation is performed.

    Arguments:
      tensor: a 3D tf.Tensor of shape `[batch, length, in_width]`.
      width: a `int` representing the target value of the 3rd
        dimension of the output tensor.

    Returns:
      a 3D tensor of shape `[batch, length, width]` where the
        third dimension is the minimum between the input width
        and the value of the `width` argument.

    Example:
    ```python
    # t is a tensor like:
    # [[[1, 1, 1],
        [2, 2, 2],
        [3, 3, 3]],
        [7, 7, 7],
        [8, 8, 8],
        [9, 9, 9]]]

    q = trim(t, 2)

    # q is a tensor like:
    # [[[1, 1],
        [2, 2],
        [3, 3]],
        [7, 7],
        [8, 8],
        [9, 9]]]
    ```
    """
    return tf.cond(
        tf.less_equal(tf.shape(tensor)[-1], width),
        lambda: tensor,
        lambda: _trim(tensor, width))


def _pad(tensor, width):
    """Pad the tensor along the -1 axis to the target width."""
    diff = width - tf.shape(tensor)[-1]
    paddings = [[0, 0], [0, 0], [0, diff]]
    padded = tf.pad(tensor, paddings, "CONSTANT")
    return padded


def pad(tensor, width):
    """Padd the tensor on the -1 axis.

    Trims a given 3D tensor of shape `[batch, length, in_width]` to
    a larger tensor of shape `[batch, length, width]`, on the -1
    axis. If the `width` argument is less or equal than the actual
    width of the tensor, no operation is performed.

    Arguments:
      tensor: a 3D tf.Tensor of shape `[batch, length, in_width]`.
      width: a `int` representing the target value of the 3rd
        dimension of the output tensor.

    Returns:
      a 3D tensor of shape `[batch, length, width]` where the
        third dimension is the maximum between the input width
        and the value of the `width` argument.

    Example:
    ```python
    # t is a tensor like:
    # [[[1, 1, 1],
        [2, 2, 2],
        [3, 3, 3]],
        [7, 7, 7],
        [8, 8, 8],
        [9, 9, 9]]]

    q = pad(t, 4)

    # q is a tensor like:
    # [[[1, 1, 1, 0],
        [2, 2, 2, 0],
        [3, 3, 3, 0]],
        [7, 7, 7, 0],
        [8, 8, 8, 0],
        [9, 9, 9, 0]]]
    ```
    """
    return tf.cond(
        tf.greater_equal(tf.shape(tensor)[-1], width),
        lambda: tensor,
        lambda: _pad(tensor, width))


def _fit(tensor, width):
    actual = tf.shape(tensor)[-1]
    result = tf.cond(tf.greater(actual, width),
                     lambda: _trim(tensor, width),  # trim
                     lambda: _pad(tensor, width))  # pad
    return result


def fit(tensor, width):
    """Trim or pad the tensor on the -1 axis to a given width.

    Adapt a 3D tensor of shape `[batch, length, width_in]` to the shape
    `[batch, length, width]` trimming the extra values or padding with
    `0.0` the missing ones. If the value of `width` is the same of
    the `width_in`, no operation is performed.

    Arguments:
      tensor: a 3D tf.Tensor of shape `[batch, length, in_width]`.
      width: a `int` representing the target value of the 3rd
        dimension of the output tensor.

    Returns:
      a 3D tensor of shape `[batch, length, width]`.

    Example:
    ```python
    # Example 1.
    # if the target width is the same,
    # no operation is performed on the tensor.
    #
    # t is a tensor like:
    # [[[1, 1, 1],
        [2, 2, 2],
        [3, 3, 3]],
        [7, 7, 7],
        [8, 8, 8],
        [9, 9, 9]]]

    q = fit(t, 3)

    # q is a tensor exactly like:
    # [[[1, 1, 1],
        [2, 2, 2],
        [3, 3, 3]],
        [7, 7, 7],
        [8, 8, 8],
        [9, 9, 9]]]


    # Example 2.
    # if the target width is smaller, the
    # tensor gets trimmed along the -1 axis.
    #
    # t is a tensor like:
    # [[[1, 1, 1],
        [2, 2, 2],
        [3, 3, 3]],
        [7, 7, 7],
        [8, 8, 8],
        [9, 9, 9]]]

    q = fit(t, 2)

    # q is a tensor like:
    # [[[1, 1],
        [2, 2],
        [3, 3]],
        [7, 7],
        [8, 8],
        [9, 9]]]


    # Example 3.
    # if the target width is larger than the
    # intial one, he tensor gets padded with
    # 0.0 along the -1 axis.
    #
    # t is a tensor like:
    # [[[1, 1, 1],
        [2, 2, 2],
        [3, 3, 3]],
        [7, 7, 7],
        [8, 8, 8],
        [9, 9, 9]]]

    q = fit(t, 4)

    # q is a tensor like
    # [[[1, 1, 1, 0],
        [2, 2, 2, 0],
        [3, 3, 3, 0]],
        [7, 7, 7, 0],
        [8, 8, 8, 0],
        [9, 9, 9, 0]]]
    ```
    """
    actual = tf.shape(tensor)[-1]
    result = tf.cond(tf.equal(actual, width),
                     lambda: tensor,
                     lambda: _fit(tensor, width))
    return result


def softmax(logits, mask=None, name='softmax'):
    """Masked softmax along the -1 axis.

    Apply the softmax operator along the -1 axis to the tensor
    where the masked elements do not partecipate and are replaced
    with `0.0` in the resulting tensor.

    Arguments:
      logits: a tensor of any shape.
      mask: a tensor of the exactly same shape of `logits` made of `1.0` or `0.0`.
      name: `str`, the name of the scope of the operator.

    Returns:
      a tensor of the same shape of `logits` containing the softmax of the
        input values evaluated only on the elements allowed by the mask
        (`0.0` otherwise).

    Example:
    >>> import tensorflow as tf
    >>> from liteflow import ops
    >>> logits = tf.constant([[3.0, 1.0, 0.2, 23.0],
                              [1.0, 23.0, 0.2, 3.0],
                              [23.0, 0.2, 3.0, 1.0]],
                             dtype=tf.float32)
    >>> mask = tf.constant([[1.0, 1.0, 1.0, 0.0],
                            [1.0, 0.0, 1.0, 1.0],
                            [0.0, 1.0, 1.0, 1.0]],
                           dtype=tf.float32)
    >>> softmax = ops.softmax(logits, mask=mask)
    >>> with tf.Session() as sess:
    >>>     sess.run(tf.global_variables_initializer())
    >>>     print sess.run(softmax)

    [[ 0.83601874  0.11314283  0.05083835  0.        ]
     [ 0.11314284  0.          0.05083836  0.8360188 ]
     [ 0.          0.05083836  0.8360188   0.11314284]]
    """
    if mask is None:
        return tf.nn.softmax(logits, dim=-1, name=name)

    with tf.variable_scope(name) as _:
        exps = tf.exp(logits)
        masked = (exps * mask)
        sums = tf.reduce_sum(masked, axis=-1, keep_dims=True)
        return masked/sums
