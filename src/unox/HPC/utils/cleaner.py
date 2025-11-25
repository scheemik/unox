import numpy as np
import glob

flist = glob.glob('stage1/x/*.npy')
for file in flist:
	data = np.load(file)
	data[np.where(np.isnan(data))] = 0
	print(file, data.shape)
	print(file[:8]+'_clean'+file[8:] )

flist = glob.glob('stage2/x/*.npy')
for file in flist:
	data = np.load(file)
	data[np.where(np.isnan(data))] = 0
	print(file, data.shape)

flist = glob.glob('stage1/y/*.npy')
for file in flist:
	data = np.load(file)
	data[np.where(np.isnan(data))] = 0
	data = data*1e12
	print(file, data.shape)

flist = glob.glob('stage2/y/*.npy')
for file in flist:
	data = np.load(file)
	data[np.where(np.isnan(data))] = 0
	data = data*1e12
	print(file, data.shape)