import os
import sys
import glob
import yaml
import json
import random
import tarfile
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.applications import resnet50

from dvclive.keras import DvcLiveCallback
import modeling

if len(sys.argv) != 2:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython prepare.py data-file\n")
    sys.exit(1)

params = yaml.safe_load(open("params.yaml"))["train"]
print(params)

train = 'data'/Path(params['train'])
test = 'data'/Path(params['test'])
output = Path(sys.argv[1])

_image_feature_description = {
    'image': tf.io.FixedLenFeature([], tf.string),
    'label': tf.io.FixedLenFeature([], tf.int64),
}

def _parse_image_function(example_proto):
    features = tf.io.parse_single_example(example_proto, _image_feature_description)
    image = tf.io.decode_png(features['image'], channels=3) # tf.io.decode_raw(features['image'], tf.uint8)
    image = tf.image.resize(image, [224, 224])
    image = resnet50.preprocess_input(image)

    label = tf.cast(features['label'], tf.int32)

    return image, label

def _read_dataset(epochs, batch_size, channel):
    filenames = glob.glob(str(channel/'*.tfrecord'))
    dataset = tf.data.TFRecordDataset(filenames)

    dataset = dataset.map(_parse_image_function, num_parallel_calls=4)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    dataset = dataset.repeat(epochs)
    dataset = dataset.shuffle(buffer_size=10 * batch_size)
    dataset = dataset.batch(batch_size, drop_remainder=True)      

    return dataset

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def run_train():
    train_size = params['train_size']
    train_step_size = train_size // params['batch_size']

    train_ds = _read_dataset(params['epoch'], params['batch_size'], train)
    test_ds = _read_dataset(params['epoch'], params['batch_size'], test)

    dvcCallback = DvcLiveCallback()

    m = modeling._build_keras_model()
    m = modeling._compile(m, float(params['lr']))

    m.fit(
        train_ds,
        epochs=params['epoch'],
        steps_per_epoch=train_step_size,
        validation_data=test_ds,
        callbacks=[dvcCallback])

    m.save(output, 
           save_format='tf', 
           signatures=modeling._get_signature(m)) 

    make_tarfile(f'{output}.tar.gz', output)

run_train()