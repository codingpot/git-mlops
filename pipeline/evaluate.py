import sys
import yaml
import json
import glob
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import resnet50

if len(sys.argv) != 2:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython prepare.py data-file\n")
    sys.exit(1)

params = yaml.safe_load(open("params.yaml"))["evaluate"]
print(params)    

test = 'data'/Path(params['test'])
model_path = Path(sys.argv[1])
METRICS_FILE = params['metrics']

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

def _read_dataset(batch_size, channel):
    filenames = glob.glob(str(channel/'*.tfrecord'))
    dataset = tf.data.TFRecordDataset(filenames)

    dataset = dataset.map(_parse_image_function, num_parallel_calls=4)
    dataset = dataset.batch(batch_size)
    return dataset

def evaluate_model():
    model = keras.models.load_model(model_path)

    test_ds = _read_dataset(params['batch_size'], test)

    metrics_dict = model.evaluate(
        test_ds,
        return_dict=True,
    )

    with open(METRICS_FILE, "w") as f:
        f.write(json.dumps(metrics_dict))

evaluate_model()