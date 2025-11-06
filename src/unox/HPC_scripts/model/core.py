import keras
from keras import Model, Input
from keras.layers import LSTM, Permute, Reshape
from keras.layers import Lambda
from keras.layers import Conv2D, Conv2DTranspose
from keras.layers import MaxPooling2D
from keras.layers import concatenate
import tensorflow as tf

@keras.saving.register_keras_serializable(package="unox", name="build_Unet")
def build_Unet():
    inputs = Input( ( 56, 120, 9 ), name='model_input') # (None, 56, 120, 9)

    # Conv2D(filters, kernel_size, **kwargs)
    ## filters is the dimension of the output space, the number of filters in the convolution
    c1 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block1_Conv1') (inputs) # (None, 56, 120, 128)
    c1 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block1_Conv2') (c1) # (None, 56, 120, 256)
    p1 = MaxPooling2D((2, 2), name='Block1_MaxPool', padding='same') (c1) # (None, 28, 60, 256)

    c2 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block2_Conv1') (p1) # (None, 28, 60, 256)
    c2 = Conv2D(512, (3, 3), activation='softplus', padding='same', name='Block2_Conv2') (c2) # (None, 28, 60, 512)
    p2 = MaxPooling2D((2, 2), name='Block2_MaxPool', padding='same') (c2) # (None, 14, 30, 512)

    c3 = Conv2D(512, (3, 3), activation='softplus', padding='same', name='Block3_Conv1') (p2) # (None, 14, 30, 512)
    c3 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block3_Conv2') (c3) # (None, 14, 30, 1024)
    p3 = MaxPooling2D((2, 2), name='Block3_MaxPool', padding='same') (c3) # (None, 7, 15, 1024)

    c4 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block4_Conv1') (p3) # (None, 7, 15, 1024)
    c4 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block4_Conv2') (c4) # (None, 7, 15, 1024)

    c4 = Permute((3, 1, 2), name='Block4_Permute1') (c4) # (None, 1024, 7, 15)
    c4 = Reshape((-1, 105), name='Block4_Reshape') (c4) # (None, 1024, 105=7*15)
    f4 = Permute((2, 1), name='Block4_Permute2') (c4) # (None, 105, 1024)

    # RNN - Recurrent Neural Networks
    lstm = LSTM(1024, return_sequences=True, name='LSTM1') (f4) # (None, 105, 1024)
    lstm = LSTM(1024, return_sequences=True, name='LSTM2') (lstm) # (None, 105, 1024)

    resh = Reshape( (7, 15, 1024) , name='Block5_Reshape') (lstm) # (None, 7, 15, 1024)

    u5 = Conv2DTranspose(512, (2, 2), strides=(2, 2), padding='same', name='Block5_UpConv') (resh) # (None, 14, 30, 512)
    # tf.slice(input_, begin, size)
    ## "begin is zero-based; size is one-based. If size[i] is -1, all remaining elements in dimension i are included in the slice."
    # I think u5 might only need to be cropped if there was an odd number length of dimension, to make sure it isn't off by 1 after halving
    u5_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, 14, 30, -1]), output_shape=(14, 30, 512))(u5) # (None, 14, 30, 512)
    # I don't know exactly why the begin here is [0, 7, 15, 0]. My guess is that it is c2 size divided by 4, such that the middle is taken
    # with a quarter left on all sides
    c2_cropped = Lambda(lambda x: tf.slice(x, [0, 7, 15, 0], [-1, 14, 30, -1]), output_shape=(14, 30, 512))(c2) # (None, 14, 30, 512)
    # A `Concatenate` layer requires inputs with matching shapes except for the concatenation axis.
    u5_comb = concatenate([u5_cropped, c3, c2_cropped])  # (None, 14, 30, 2048)
    c5 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block5_Conv1') (u5_comb) # (None, 14, 30, 256)
    c5 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block5_Conv2') (c5) # (None, 14, 30, 256)

    u6 = Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same', name='Block6_UpConv') (c5) # (None, 28, 60, 256)
    u6_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, 28, 60, -1]))(u6) # (None, 28, 60, 256)
    # I don't know exactly why the begin here is [0, 14, 30, 0]. My guess is that it is c1 size divided by 4, such that the middle is taken
    # with a quarter left on all sides
    c1_cropped = Lambda(lambda x: tf.slice(x, [0, 14, 30, 0], [-1, 28, 60, -1]))(c1) # (None, 28, 60, 256)
    u6_comb = concatenate([u6_cropped, c2, c1_cropped]) # (None, 28, 60, 1024)
    c6 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block6_Conv1') (u6_comb) # (None, 28, 60, 128)
    c6 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block6_Conv2') (c6) # (None, 28, 60, 128)

    u7 = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same', name='Block7_UpConv') (c6) # (None, 56, 120, 128)
    u7_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, 56, 120, -1]))(u7) # (None, 56, 120, 128)
    u7_comb = concatenate([u7_cropped, c1]) # (None, 56, 120, 384)
    c7 = Conv2D(64, (3, 3), activation='softplus', padding='same', name='Block7_Conv1') (u7_comb) # (None, 56, 120, 64)
    c7 = Conv2D(64, (3, 3), activation='softplus', padding='same', name='Block7_Conv2') (c7) # (None, 56, 120, 64)

    outputs = Conv2D(1, (1, 1), activation='softplus', name='model_output') (c7) # (None, 56, 120, 1)

    # prepare model here
    model = Model(inputs=[inputs], outputs=[outputs])

    return model

@keras.saving.register_keras_serializable(package="unox")
class Unet():

    def __init__(self):
        self.model = build_Unet()

    def compile(self, optimizer, loss, **kwargs):
        self.model.compile(optimizer=optimizer, loss=loss, **kwargs)

    def info(self):
        self.model.summary()

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
