import keras
from keras import Model, Input
from keras.layers import LSTM, Permute, Reshape
from keras.layers import Lambda
from keras.layers import Conv2D, Conv2DTranspose
from keras.layers import MaxPooling2D
from keras.layers import concatenate
# import tensorflow as tf

@keras.saving.register_keras_serializable(package="unox", name="build_Unet")
def build_Unet():
    inputs = Input( ( 35, 46, 9 ), name='model_input')

    c1 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block1_Conv1') (inputs)    # 35, 46
    c1 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block1_Conv2') (c1)   # 35, 46
    p1 = MaxPooling2D((2, 2), name='Block1_MaxPool', padding='same') (c1)   # 18 23

    c2 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block2_Conv1') (p1)   # 18 23
    c2 = Conv2D(512, (3, 3), activation='softplus', padding='same', name='Block2_Conv2') (c2)   # 18 23
    p2 = MaxPooling2D((2, 2), name='Block2_MaxPool', padding='same') (c2)   # 9 12

    c3 = Conv2D(512, (3, 3), activation='softplus', padding='same', name='Block3_Conv1') (p2)   # 9 12
    c3 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block3_Conv2') (c3)   # 9 12
    p3 = MaxPooling2D((2, 2), name='Block3_MaxPool', padding='same') (c3)  # 5 x 6


    c4 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block4_Conv1') (p3) # 5 x 6
    c4 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block4_Conv2') (c4) # 5 x 6

    c4 = Permute((3, 1, 2), name='Block4_Permute1') (c4)
    c4 = Reshape((-1, 30), name='Block4_Reshape') (c4)
    f4 = Permute((2, 1), name='Block4_Permute2') (c4)  # 20 x 512

    lstm = LSTM(1024, return_sequences=True, name='LSTM1') (f4)
    lstm = LSTM(1024, return_sequences=True, name='LSTM2') (lstm)

    resh = Reshape( (5 , 6, 1024) , name='Block5_Reshape') (lstm)

    u5 = Conv2DTranspose(512, (2, 2), strides=(2, 2), padding='same', name='Block5_UpConv') (resh) # (None, 10, 12, 512)
    # tf.slice(input_, begin, size)
    ## "begin is zero-based; size is one-based. If size[i] is -1, all remaining elements in dimension i are included in the slice."
    u5_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, 9, 12, -1]), output_shape=(9, 12, 512))(u5) # (None, 9, 12, 512)
    c2_cropped = Lambda(lambda x: tf.slice(x, [0, 4, 6, 0], [-1, 9, 12, -1]), output_shape=(9, 12, 512))(c2) # (None, 9, 12, 512)
    # A `Concatenate` layer requires inputs with matching shapes except for the concatenation axis.
    u5_comb = concatenate([u5_cropped, c3, c2_cropped])  # (None, 9, 12, 2048)
    c5 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block5_Conv1') (u5_comb)  # (None, 9, 12, 256)
    c5 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block5_Conv2') (c5)  # (None, 9, 12, 256)

    u6 = Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same', name='Block6_UpConv') (c5)  # 18 x 24
    u6_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, 18, 23, -1]))(u6)
    c1_cropped = Lambda(lambda x: tf.slice(x, [0, 8, 11, 0], [-1, 18, 23, -1]))(c1)
    u6_comb = concatenate([u6_cropped, c2, c1_cropped])
    c6 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block6_Conv1') (u6_comb)  # 18 x 24
    c6 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block6_Conv2') (c6)  # 18 x 24

    u7 = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same', name='Block7_UpConv') (c6)  # 36, 46
    u7_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, 35, 46, -1]))(u7)  # 35, 46
    u7_comb = concatenate([u7_cropped, c1])
    c7 = Conv2D(64, (3, 3), activation='softplus', padding='same', name='Block7_Conv1') (u7_comb)  # 35, 46
    c7 = Conv2D(64, (3, 3), activation='softplus', padding='same', name='Block7_Conv2') (c7)  # 35, 46

    outputs = Conv2D(1, (1, 1), activation='softplus', name='model_output') (c7)

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
