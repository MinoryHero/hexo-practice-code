import numpy as np
import os
import urllib
import gzip
import struct
import mxnet as mx
import matplotlib.pyplot as plt
from sklearn import datasets
import logging


def download_data(url, force_download=False):
    fname = url.split("/")[-1]
    if force_download or not os.path.exists(fname):
        urllib.request.urlretrieve(url, fname)
    return fname


def read_data(label_url, image_url):
    with gzip.open(download_data(label_url)) as flbl:
        magic, num = struct.unpack(">II", flbl.read(8))
        label = np.fromstring(flbl.read(), dtype=np.int8)
    with gzip.open(download_data(image_url), 'rb') as fimg:
        magic, num, rows, cols = struct.unpack(">IIII", fimg.read(16))
        image = np.fromstring(fimg.read(), dtype=np.uint8).reshape(
            len(label), rows, cols)
    return (label, image)


path = 'http://yann.lecun.com/exdb/mnist/'
(train_lbl, train_img) = read_data(
    path + 'train-labels-idx1-ubyte.gz', path + 'train-images-idx3-ubyte.gz')
(val_lbl, val_img) = read_data(
    path + 't10k-labels-idx1-ubyte.gz', path + 't10k-images-idx3-ubyte.gz')

for i in range(10):
    plt.subplot(1, 10, i + 1)
    plt.imshow(train_img[i], cmap='Greys_r')
    plt.axis('off')
# plt.show()
print('label: %s' % (train_lbl[0:10],))


def to4d(img):
    return img.reshape(img.shape[0], 1, 28, 28).astype(np.float32) / 255


to4d(train_img).shape
train_img.shape
train_img[0].shape
type(train_img[0])
batch_size = 100
train_iter = mx.io.NDArrayIter(
    to4d(train_img), train_lbl, batch_size, shuffle=True)
val_iter = mx.io.NDArrayIter(to4d(val_img), val_lbl, batch_size)
tmp = val_iter.getlabel()
type(tmp[0])
data = mx.sym.Variable('data')
data = mx.sym.Flatten(data=data)
fc1 = mx.sym.FullyConnected(data=data, name='fc1', num_hidden=128)
act1 = mx.sym.Activation(data=fc1, name='relu1', act_type='relu')
fc2 = mx.sym.FullyConnected(data=act1, name='fc2', num_hidden=64)
act2 = mx.sym.Activation(data=fc2, name='relu2', act_type='relu')
fc3 = mx.sym.FullyConnected(data=act2, name='fc3', num_hidden=10)
mlp = mx.sym.SoftmaxOutput(data=fc3, name='softmax')
shape = {'data': (batch_size, 1, 28, 28)}
mx.viz.plot_network(symbol=mlp, shape=shape)
logging.getLogger().setLevel(logging.DEBUG)
model = mx.mod.Module(symbol=mlp, context=mx.gpu(), data_names=[
                      'data'], label_names=['softmax_label'])
model.fit(train_data=train_iter, eval_data=val_iter, optimizer='sgd',
          optimizer_params={'learning_rate': 0.1},
          eval_metric='acc', num_epoch=10)
plt.imshow(val_img[0], cmap='Greys_r')
prob = model.predict(val_iter).asnumpy()[0]
assert max(prob) > 0.99, "Low prediction accuracy."
print('Classified as %d with probability %f' % (prob.argmax(), max(prob)))
# prob = model.predict(to4d(val_img[0:1]))[0]
# assert max(prob) > 0.99, "Low prediction accuracy."
# print('Classified as %d with probability %f' % (prob.argmax(), max(prob)))
valid_acc = model.score(val_iter, eval_metric='acc')
list(valid_acc)

data = mx.sym.Variable('data')
conv1 = mx.sym.Convolution(data=data, kernel=(5, 5), num_filter=20)
tanh1 = mx.sym.Activation(data=conv1, act_type='tanh')
pool1 = mx.sym.Pooling(data=tanh1, pool_type='max',
                       kernel=(2, 2), stride=(2, 2))
conv2 = mx.sym.Convolution(data=pool1, kernel=(5, 5), num_filter=50)
tanh2 = mx.sym.Activation(data=conv2, act_type='tanh')
pool2 = mx.sym.Pooling(data=tanh2, pool_type='max',
                       kernel=(2, 2), stride=(2, 2))
flatten = mx.sym.Flatten(data=pool2)
fc1 = mx.sym.FullyConnected(data=flatten, num_hidden=500)
tanh3 = mx.sym.Activation(data=fc1, act_type='tanh')
fc2 = mx.sym.FullyConnected(data=tanh3, num_hidden=10)
lenet = mx.sym.SoftmaxOutput(data=fc2, name='softmax')
mx.viz.plot_network(symbol=lenet, shape=shape)
logging.getLogger().setLevel(logging.DEBUG)
conv_mod = mx.mod.Module(symbol=lenet, data_names=['data'], label_names=[
                         'softmax_label'], context=mx.gpu())
conv_mod.fit(train_data=train_iter, eval_data=val_iter, optimizer='sgd',
             optimizer_params={'learning_rate': 0.1},
             eval_metric='acc', num_epoch=10)
prob = conv_mod.predict(val_iter).asnumpy()[0]
