from keras.models import Model, load_model
from keras.layers import Input, LSTM, Permute, Reshape
from keras.layers.core import Lambda
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.pooling import MaxPooling2D
from keras.layers.merging import concatenate  #Evelyn changed merge to merging
import tensorflow as tf

def build_Unet(num_feature=12):
    inputs = Input( ( 35, 46, num_feature ), name='model_input')

    c1 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block1_Conv1') (inputs)    # 56, 120
    c1 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block1_Conv2') (c1)   # 56, 120
    p1 = MaxPooling2D((2, 2), name='Block1_MaxPool', padding='same') (c1)   # 28, 60

    c2 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block2_Conv1') (p1)   # 28, 60
    c2 = Conv2D(512, (3, 3), activation='softplus', padding='same', name='Block2_Conv2') (c2)   # 28, 60
    p2 = MaxPooling2D((2, 2), name='Block2_MaxPool', padding='same') (c2)   # 14, 30

    c3 = Conv2D(512, (3, 3), activation='softplus', padding='same', name='Block3_Conv1') (p2)   # 14, 30
    c3 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block3_Conv2') (c3)   # 14, 30
    p3 = MaxPooling2D((2, 2), name='Block3_MaxPool', padding='same') (c3)  # 7, 15

    c4 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block4_Conv1') (p3) # 7, 15
    c4 = Conv2D(1024, (3, 3), activation='softplus', padding='same', name='Block4_Conv2') (c4) # 7, 15

    c4 = Permute((3, 1, 2), name='Block4_Permute1') (c4)
    c4 = Reshape((-1, 30), name='Block4_Reshape') (c4)
    f4 = Permute((2, 1), name='Block4_Permute2') (c4)  # 20 x 512

    lstm = LSTM(1024, return_sequences=True, name='LSTM1') (f4)
    lstm = LSTM(1024, return_sequences=True, name='LSTM2') (lstm)

    resh = Reshape( (5, 6, 1024) , name='Block5_Reshape') (lstm)

    u5 = Conv2DTranspose(512, (2, 2), strides=(2, 2), padding='same', name='Block5_UpConv') (resh)  # 14 x 30
    # u5_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, 0, 0, -1]))(u5)
    # c2_cropped = Lambda(lambda x: tf.slice(x, [0, 0, 0, 0], [-1, 0, 0, -1]))(c2) 
    u5_comb = concatenate([u5, c3])  # 9 x 12
    c5 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block5_Conv1') (u5_comb)  # 14 x 30
    c5 = Conv2D(256, (3, 3), activation='softplus', padding='same', name='Block5_Conv2') (c5)  # 14 x 30

    u6 = Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same', name='Block6_UpConv') (c5)  # 28 x 60
    u6_comb = concatenate([u6, c2])
    c6 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block6_Conv1') (u6_comb)  # 28 x 60
    c6 = Conv2D(128, (3, 3), activation='softplus', padding='same', name='Block6_Conv2') (c6)  # 28 x 60

    u7 = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same', name='Block7_UpConv') (c6)  # 56, 120
    u7_comb = concatenate([u7, c1])
    c7 = Conv2D(64, (3, 3), activation='softplus', padding='same', name='Block7_Conv1') (u7_comb)  # 56, 120
    c7 = Conv2D(64, (3, 3), activation='softplus', padding='same', name='Block7_Conv2') (c7)  # 56, 120

    outputs = Conv2D(1, (1, 1), activation='softplus', name='model_output') (c7)

    # prepare model here
    model = Model(inputs=[inputs], outputs=[outputs])

    return model



class Unet():

    def __init__(self, num_feature=12):
        self.model = build_Unet(num_feature)

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
