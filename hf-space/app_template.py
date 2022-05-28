from os import walk
import tarfile
import gradio as gr
from huggingface_hub import hf_hub_download
from tensorflow import keras
from tensorflow.keras.applications import resnet50

def load_model(tar_file: str='outputs/model.tar.gz'):
    tar_file = tarfile.open(tar_file)
    tar_file.extractall('.')
    tar_file.close()

    model_path = 'model'
    return keras.models.load_model(model_path)

filepath = hf_hub_download(repo_id='$MODEL_REPO_ID', filename='outputs/model.tar.gz', force_filename='model.tar.gz')
model = load_model(tar_file=filepath)
labels = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

def classify_image(inp):
  inp = inp.reshape((-1, 224, 224, 3))
  inp = resnet50.preprocess_input(inp)

  prediction = model.predict(inp).flatten()
  confidences = {labels[i]: float(prediction[i]) for i in range(10)}
  return confidences

iface = gr.Interface(fn=classify_image, 
             inputs=gr.inputs.Image(shape=(224, 224)),
             outputs=gr.outputs.Label(num_top_classes=3)).launch()
iface.launch()

