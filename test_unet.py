#test code based on Unet_Chinese_NOx example_code.ipynb
from utils.functions import r2_keras
from utils.functions import msenonzero
from utils.functions import data_split
from model.core import Unet
from tensorflow.keras.optimizers import Adam
from keras.callbacks import CSVLogger, EarlyStopping, ModelCheckpoint
import numpy as np
import glob
import sys
import os 


try:
  savedir = sys.argv[1] + '/'
except:
  savedir = 'output_test_unet/'  #directory to save output in

try:
  os.mkdir(savedir)
except FileExistsError:
  print(savedir+' exists')

try:
  os.mkdir(savedir+'stage1_output/')
except FileExistsError:
  print('stage1_output/ exists')
try:
  os.mkdir(savedir+'stage2_output/')
except FileExistsError:
  print('stage2_output/ exists')

unet = Unet()
opt = Adam(lr=1e-5) 

unet.compile(optimizer=opt, loss=msenonzero, metrics=[r2_keras, msenonzero])
unet.summary()


x_files = sorted(glob.glob('sample_data/stage1/x/X_20*.npy'))
y_files = sorted(glob.glob('sample_data/stage1/y/Y_20*.npy'))


xtrain_files, ytrain_files = x_files[:14], y_files[:14]
file0 = np.load(xtrain_files[0])
print(file0.shape)
xtrain = np.concatenate([ np.load(s) for s in xtrain_files], axis=0)
ytrain = np.concatenate([ np.load(s) for s in ytrain_files], axis=0)
print(xtrain.shape, ytrain.shape)

#xtrain = xtrain[:,:,:,:9]
print(xtrain.shape)

# split into training, validation, and test sets
xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, 0.9)
print(xtrain.shape, ytrain.shape, xvalid.shape, yvalid.shape)


csv_logger = CSVLogger( savedir+'unet_stage1_log.csv', append=True, separator=';')
earlystopper = EarlyStopping(patience=15, verbose=1)
checkpointer = ModelCheckpoint(savedir+'unet_checkpt_{val_loss:.2f}_{r2_keras:.2f}_stage1.h5', verbose=1, save_best_only=True)
print("begin training stage 1")
unet.train(xtrain, ytrain, validation_data=(xvalid, yvalid), 
           batch_size=30, epochs=250, callbacks=[earlystopper, checkpointer, csv_logger], shuffle=True)
unet.save_model(savedir+'unet_stage1_model.h5')

#Generate predictions for evaluation
### Load testing data sets
xtest_files = x_files[14:]

### Predict using Unet
for x in xtest_files:
    xnow = np.load(x)#[:,:,:,:9]
    pred = unet.predict(xnow)
    np.save(savedir+'stage1_output/pred_' + x.split('/')[-1], pred)

#for y in y_files[14:]:
#    ynow = np.load(y)
#    pred = unet.predict(ynow)
#    np.save(savedir+'stage1_output/ypred_' + y.split('/')[-1], pred)


x_files = sorted(glob.glob('sample_data/stage2/x/X_20*.npy'))
y_files = sorted(glob.glob('sample_data/stage2/y/Y_20*.npy'))
print(x_files, y_files)
xtrain_files, ytrain_files = x_files[:5], y_files[:5]
xtrain = np.concatenate([ np.load(s) for s in xtrain_files], axis=0)
#xtrain = xtrain[:,:,:,:9] #definitely not the right way to make the data the right size

ytrain = np.concatenate([ np.load(s) for s in ytrain_files], axis=0)
# print(xtrain.shape, ytrain.shape)

# split into training, validation, and test sets
xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, 0.9)
# print(xtrain.shape, ytrain.shape, xvalid.shape, yvalid.shape)

unet.load_weights(savedir+'unet_stage1_model.h5')


#stage 2 training
csv_logger = CSVLogger( savedir+'unet_stage2_log.csv', append=True, separator=';')
earlystopper = EarlyStopping(patience=15, verbose=1)
checkpointer = ModelCheckpoint(savedir+'unet_checkpt_{val_loss:.2f}_{r2_keras:.2f}_stage2.h5', verbose=1, save_best_only=True)

print('begin training stage 2')
unet.train(xtrain, ytrain, validation_data=(xvalid, yvalid), 
           batch_size=30, epochs=250, callbacks=[earlystopper, checkpointer, csv_logger], shuffle=True)
unet.save_model(savedir+'unet_stage2_model.h5')


#Generate predictions for evaluation
### Load testing data sets
xtest_files = x_files[5:]
print(xtest_files)

### Predict using Unet
for x in xtest_files:
    xnow = np.load(x)#[:,:,:,:9]
    pred = unet.predict(xnow)
    np.save(savedir+'stage2_output/pred_' + x.split('/')[-1], pred)

#for y in y_files[14:]:
#    ynow = np.load(y)
#    pred = unet.predict(ynow)
#    np.save(savedir+'stage2_output/ypred_' + y.split('/')[-1], pred)







