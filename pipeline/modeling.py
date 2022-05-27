import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras import Sequential
from tensorflow.keras.layers import InputLayer, Dropout, Dense
from tensorflow.keras.optimizers import Adam

def _get_serve_image_fn(model):
  @tf.function
  def serve_image_fn(image_tensor):
    return model(image_tensor)

  return serve_image_fn

def _get_signature(model): 
  signatures = {
      'serving_default':
          _get_serve_image_fn(model).get_concrete_function(
              tf.TensorSpec(
                  shape=[None, 224, 224, 3],
                  dtype=tf.float32,
                  name='image'))
  }

  return signatures  

def _build_keras_model(num_class=10):
    base_model = ResNet50(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
        pooling='max')
    base_model.trainable = False

    model = Sequential([
        InputLayer(input_shape=(224, 224, 3)),
        base_model,
        Dropout(0.1),
        Dense(num_class, activation='softmax')
    ])

    return model

def _compile(model_to_fit, learning_rate):
  model_to_fit.compile(
      loss='sparse_categorical_crossentropy',
      optimizer=Adam(learning_rate=learning_rate),
      metrics=['sparse_categorical_accuracy'])

  return model_to_fit