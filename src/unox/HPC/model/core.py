import keras
from keras import Model, Input
from keras.layers import LSTM, Permute, Reshape
from keras.layers import Lambda
from keras.layers import Conv2D, Conv2DTranspose
from keras.layers import MaxPooling2D
from keras.layers import concatenate
from keras.regularizers import L1, L2, L1L2
import tensorflow as tf
import math

@keras.saving.register_keras_serializable(package="unox", name="build_Unet")
def build_Unet(
    input_shape,
    n_c_fltr=128,
    k_size=(3,3),
    p_size=(2,2),
    act_reg=None,
    act_reg_factor=0.0001,
):
    """ Build the Unet.

        Construct the architecture of the Unet model based on the given parameters.

        Parameters
        ----------
        input_shape : `tuple` of `int`
            The shape of the input (n_lat, n_lon, n_in_vars), where n_lat is the
            number of latitude grid cells, n_lon is the number of longitude grid
            cells, and n_in_vars is the number of input variables.
        n_c_fltr : `int`, optional
            The number of filters for the initial convolutional layer.
        k_size : `tuple` of `int`, optional
            The kernel size to use in the convolutional layers.
        p_size : `tuple` of `int`, optional
            The factors by which to downscale in the Max Pooling layers.
        act_reg : `str`, optional
            The name of the regularization function (of type keras.regularizers.Regularizer) to apply to the activations of the layers.
        act_reg_factor : `float`, optional
            The regularization factor to apply to the activations of the layers.

        Returns
        -------
        model : `keras.Model`
            The constructed Unet model.
    """
    # Verify argument types
    if not isinstance(input_shape, tuple):
        raise TypeError(f"(build_Unet) `input_shape` must be a tuple. Got type: {type(input_shape)}")
    for i in range(len(input_shape)):
        if not isinstance(input_shape[i], int):
            raise TypeError(f"(build_Unet) `input_shape` must be a tuple of integers. Got type: {type(input_shape[i])} for element {i} in the tuple.")
    if not isinstance(n_c_fltr, int):
        raise TypeError(f"(build_Unet) `n_c_fltr` must be an integer. Got type: {type(n_c_fltr)}")
    if not isinstance(k_size, tuple):
        raise TypeError(f"(build_Unet) `k_size` must be a tuple. Got type: {type(k_size)}")
    for i in range(len(k_size)):
        if not isinstance(k_size[i], int):
            raise TypeError(f"(build_Unet) `k_size` must be a tuple of integers. Got type: {type(k_size[i])} for element {i} in the tuple.")
    if not isinstance(p_size, tuple):
        raise TypeError(f"(build_Unet) `p_size` must be a tuple. Got type: {type(p_size)}")
    for i in range(len(p_size)):
        if not isinstance(p_size[i], int):
            raise TypeError(f"(build_Unet) `p_size` must be a tuple of integers. Got type: {type(p_size[i])} for element {i} in the tuple.")
    if not isinstance(act_reg, (str, type(None))):
        raise TypeError(f"(build_Unet) `act_reg` must be a string or `None`. Got type: {type(act_reg)}")
    if not isinstance(act_reg_factor, (int, float)):
        raise TypeError(f"(build_Unet) `act_reg_factor` must be a number. Got type: {type(act_reg_factor)}")


    # Initialize with the input layer having the specified shape from `input_shape`
    inputs = Input( input_shape, name='model_input') # (None, 56, 120, 9)
    print(f"Using activity regularizer {act_reg} with the factor: {act_reg_factor}")
    # Set the regularizer function
    if isinstance(act_reg, type(None)) or act_reg == 'None':
        act_reg = None
    elif act_reg == 'L1':
        act_reg = L1(act_reg_factor)
    elif act_reg == 'L2':
        act_reg = L2(act_reg_factor)
    elif act_reg == 'L1L2':
        act_reg = L1L2(act_reg_factor)
    else:
        raise ValueError(f"(build_Unet) `act_reg` must be one of 'L1', 'L2', or 'L1L2'. Got: {act_reg}")

    # Note: When "None" is listed as a dimension length, it is actually the length of the time dimension.

    ### Block 1
    # Conv2D(filters, kernel_size, **kwargs)
    ## filters is the dimension of the output space, the number of filters in the convolution
    c1 = Conv2D(n_c_fltr, k_size, activation='softplus', padding='same', name='Block1_Conv1',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (inputs) # (None, 56, 120, 128)
    c1 = Conv2D(n_c_fltr*2, k_size, activation='softplus', padding='same', name='Block1_Conv2',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c1) # (None, 56, 120, 256)
    # Calculate the shape of layer c1
    c1_shape = (input_shape[0], input_shape[1], n_c_fltr*2)
    # MaxPooling2D(pool_size, **kwargs)
    p1 = MaxPooling2D(p_size, name='Block1_MaxPool', padding='same') (c1) # (None, 28, 60, 256)

    ### Block 2
    c2 = Conv2D(n_c_fltr*2, k_size, activation='softplus', padding='same', name='Block2_Conv1',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (p1) # (None, 28, 60, 256)
    c2 = Conv2D(n_c_fltr*4, k_size, activation='softplus', padding='same', name='Block2_Conv2',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c2) # (None, 28, 60, 512)
    # Calculate the shape of layer c2
    c2_shape = (int(math.ceil(c1_shape[0]/2)), int(math.ceil(c1_shape[1]/2)), n_c_fltr*4)
    p2 = MaxPooling2D(p_size, name='Block2_MaxPool', padding='same') (c2) # (None, 14, 30, 512)

    ### Block 3
    c3 = Conv2D(n_c_fltr*4, k_size, activation='softplus', padding='same', name='Block3_Conv1',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (p2) # (None, 14, 30, 512)
    c3 = Conv2D(n_c_fltr*8, k_size, activation='softplus', padding='same', name='Block3_Conv2',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c3) # (None, 14, 30, 1024)
    # Calculate the shape of layer c3
    c3_shape = (int(math.ceil(c2_shape[0]/2)), int(math.ceil(c2_shape[1]/2)), n_c_fltr*8)
    p3 = MaxPooling2D(p_size, name='Block3_MaxPool', padding='same') (c3) # (None, 7, 15, 1024)

    ### Block 4
    c4 = Conv2D(n_c_fltr*8, k_size, activation='softplus', padding='same', name='Block4_Conv1',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (p3) # (None, 7, 15, 1024)
    c4 = Conv2D(n_c_fltr*8, k_size, activation='softplus', padding='same', name='Block4_Conv2',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c4) # (None, 7, 15, 1024)
    # Calculate the shape of layer c4
    c4_shape = (int(math.ceil(c3_shape[0]/2)), int(math.ceil(c3_shape[1]/2)), n_c_fltr*8)

    # Prepare layer for LSTM cells
    c4 = Permute((3, 1, 2), name='Block4_Permute1') (c4) # (None, 1024, 7, 15)
    # Stack the "lat" and "lon" dimensions by combining them
    c4_reshape = c4_shape[0] * c4_shape[1]
    c4 = Reshape((-1, c4_reshape), name='Block4_Reshape') (c4) # (None, 1024, 105=7*15)
    f4 = Permute((2, 1), name='Block4_Permute2') (c4) # (None, 105, 1024)

    # RNN - Recurrent Neural Networks
    lstm = LSTM(n_c_fltr*8, return_sequences=True, name='LSTM1',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (f4) # (None, 105, 1024)
    lstm = LSTM(n_c_fltr*8, return_sequences=True, name='LSTM2',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (lstm) # (None, 105, 1024)

    resh = Reshape(c4_shape , name='Block5_Reshape') (lstm) # (None, 7, 15, 1024)

    ### Block 5
    u5 = Conv2DTranspose(n_c_fltr*4, (2, 2), strides=(2, 2), padding='same', name='Block5_UpConv',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (resh) # (None, 14, 30, 512)
    # tf.slice(input_, begin, size)
    ## "begin is zero-based; size is one-based. If size[i] is -1, all remaining elements in dimension i are included in the slice."
    # Cropping only necessary for u5 if c3 had an odd number length of dimension, to make sure it isn't off by 1 after halving
    u5_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, c3_shape[0], c3_shape[1], -1]), output_shape=(c3_shape[0], c3_shape[1], n_c_fltr*4))(u5) # (None, 14, 30, 512)
    # Start 1/4 of the way through each dimension, such that you crop out half the entries, but all along the edges
    c2_crop_idx = [int(c2_shape[0]/4), int(c2_shape[1]/4)]
    c2_cropped = Lambda(lambda x: tf.slice(x, [0, c2_crop_idx[0], c2_crop_idx[1], 0], [-1, c3_shape[0], c3_shape[1], -1]), output_shape=(c3_shape[0], c3_shape[1], n_c_fltr*4))(c2) # (None, 14, 30, 512)
    # Residual learning connection
    # A `Concatenate` layer requires inputs with matching shapes except for the concatenation axis.
    u5_comb = concatenate([u5_cropped, c3, c2_cropped])  # (None, 14, 30, 2048)
    c5 = Conv2D(n_c_fltr*2, k_size, activation='softplus', padding='same', name='Block5_Conv1',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (u5_comb) # (None, 14, 30, 256)
    c5 = Conv2D(n_c_fltr*2, k_size, activation='softplus', padding='same', name='Block5_Conv2',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c5) # (None, 14, 30, 256)

    ### Block 6
    u6 = Conv2DTranspose(n_c_fltr*2, (2, 2), strides=(2, 2), padding='same', name='Block6_UpConv',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c5) # (None, 28, 60, 256)
    u6_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, c2_shape[0], c2_shape[1], -1]))(u6) # (None, 28, 60, 256)
    # Start 1/4 of the way through each dimension, such that you crop out half the entries, but all along the edges
    c1_crop_idx = [int(c1_shape[0]/4), int(c1_shape[1]/4)]
    c1_cropped = Lambda(lambda x: tf.slice(x, [0, c1_crop_idx[0], c1_crop_idx[1], 0], [-1, c2_shape[0], c2_shape[1], -1]))(c1) # (None, 28, 60, 256)
    # Residual learning connection
    u6_comb = concatenate([u6_cropped, c2, c1_cropped]) # (None, 28, 60, 1024)
    c6 = Conv2D(n_c_fltr, k_size, activation='softplus', padding='same', name='Block6_Conv1',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (u6_comb) # (None, 28, 60, 128)
    c6 = Conv2D(n_c_fltr, k_size, activation='softplus', padding='same', name='Block6_Conv2',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c6) # (None, 28, 60, 128)

    ### Block 7
    u7 = Conv2DTranspose(n_c_fltr, (2, 2), strides=(2, 2), padding='same', name='Block7_UpConv',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c6) # (None, 56, 120, 128)
    u7_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, c1_shape[0], c1_shape[1], -1]))(u7) # (None, 56, 120, 128)
    # Residual learning connection
    u7_comb = concatenate([u7_cropped, c1]) # (None, 56, 120, 384)
    c7 = Conv2D(n_c_fltr//2, k_size, activation='softplus', padding='same', name='Block7_Conv1',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (u7_comb) # (None, 56, 120, 64)
    c7 = Conv2D(n_c_fltr//2, k_size, activation='softplus', padding='same', name='Block7_Conv2',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c7) # (None, 56, 120, 64)

    outputs = Conv2D(1, (1, 1), activation='softplus', name='model_output',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=act_reg,
                ) (c7) # (None, 56, 120, 1)

    # prepare model here
    model = Model(inputs=[inputs], outputs=[outputs])

    return model

@keras.saving.register_keras_serializable(package="unox")
class Unet():

    def __init__(self):
        self.model = None
    
    def build(self, input_shape, **kwargs):
        self.model = build_Unet(input_shape, **kwargs)

    def compile(self, optimizer, loss, **kwargs):
        self.model.compile(optimizer=optimizer, loss=loss, **kwargs)

    # def info(self):
    #     self.model.summary()

    def train(self, *args, **kwargs):
        self.model.fit( *args, **kwargs )

    def predict(self, x):
        return self.model.predict(x)

    def summary(self):
        self.model.summary()

    def load_weights(self, filename):
        self.model.load_weights(filename)

    def save_model(self, modelname):
        self.model.save(modelname)
    
    def get_config(self):
        config = super().get_config()
        # Update the config dictionary with any custom attributes
        config.update(
            {
                'model': self.model,
            }
        )
        return config
