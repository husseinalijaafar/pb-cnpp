
from tensorflow import keras
from tensorflow.keras.layers import Input, Conv2D, Dropout
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

import numpy as np

# input_path = '../data_2/maze_10x10_rnd/'
input_path = '../resources/dat_files/64x64_15k_combined/'
# input_path = '../data_2/maze_15x15_rnd/'
# input_path = '../data_2/maze_20x20_rnd/'
# input_path = '../data_2/maze_30x30_rnd/'

print('Load data ...')
x = np.loadtxt(input_path + 'inputs.dat')
s_map = np.loadtxt(input_path + 's_maps.dat')
g_map = np.loadtxt(input_path + 'g_maps.dat')
y = np.loadtxt(input_path + 'outputs.dat')

m = x.shape[0] #there are 30.000 samples in the dataset
n = int(np.sqrt(x.shape[1]))

### Data split
#used 8000 b4 for training by accident
n_train = 28000 #number of training samples; first n_train samples in the data set are used for training 
n_test = m - n_train #the last n_test samples are used for testing

print('Transform data ...')
x = x.reshape(m,n,n)
s_map = s_map.reshape(m,n,n)
g_map = g_map.reshape(m,n,n)
y = y.reshape(m,n,n)

x3d = np.zeros((m,n,n,3))
x3d[:,:,:,0] = x
x3d[:,:,:,1] = s_map
x3d[:,:,:,2] = g_map
del x, s_map, g_map

x_train = x3d[0:n_train,:,:,:]
y_train = y[0:n_train,:,:]
x_test = x3d[n_train:m,:,:,:]
y_test = y[n_train:m,:,:]
del x3d, y


x = Input(shape=(None, None, 3))

net = Conv2D(filters=64, kernel_size=[3, 3], strides=[1, 1], padding="same", kernel_initializer='orthogonal', activation='relu')(x)
net = BatchNormalization()(net)
for i in range(19):
	net = Conv2D(filters=64, kernel_size=[3, 3], strides=[1, 1], padding="same", kernel_initializer='orthogonal', activation='relu')(net)
	net = BatchNormalization()(net)
	
net = Conv2D(filters=1, kernel_size=[3, 3], strides=[1, 1], padding="same", kernel_initializer='orthogonal', activation='sigmoid')(net)
net = BatchNormalization()(net)	
net = Dropout(0.10)(net)

model = Model(inputs=x,outputs=net)
model.summary()

early_stop = EarlyStopping(monitor='val_acc', min_delta=0, patience=10, verbose=1, mode='auto')
save_weights = ModelCheckpoint(filepath='weights_2d_30k_combined_2.hf5', monitor='val_acc',verbose=1, save_best_only=True)

print('Train network ...')
model.compile(optimizer='adam',loss='mse',metrics=['accuracy'])
model.fit(x_train.reshape(n_train,n,n,3), y_train.reshape(n_train,n,n,1), batch_size=64, validation_split=1/14, epochs=100, verbose=1, callbacks=[early_stop, save_weights])

print('Save trained model ...')
model.load_weights('weights_2d_30k_combined_2.hf5')
model.save("model_2d_30k_combined_2.hf5")

print('Test network ...')
model=load_model("model_2d_30k_combined_2.hf5")
score = model.evaluate(x_test.reshape(n_test,n,n,3), y_test.reshape(n_test,n,n,1), verbose=1)
print('test_acc:', score[1])



