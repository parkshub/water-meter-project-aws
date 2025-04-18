import os
import sys
import random
import pickle
import tensorflow as tf
from scripts.unet.data_loader import ImageDataLoader
from scripts.unet.model_predict import ModelPredictor
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def get_random_image():
    root_dir = os.getcwd()
    image_folder = os.path.join(root_dir, 'data', 'images')
    mask_folder = os.path.join(root_dir, 'data', 'masks')

    random_image = random.randint(0, len(os.listdir(image_folder)) - 1)

    image_path = os.path.join(image_folder, os.listdir(image_folder)[random_image])
    mask_path = os.path.join(mask_folder, os.listdir(mask_folder)[random_image])

    print(image_path, mask_path)

    return image_path, mask_path

image_path, mask_path = get_random_image()

data_loader = ImageDataLoader(512, 512, 2)
predictor = ModelPredictor(data_loader, 'keras')

# predicting unet
predicted_image = predictor.predict_unet(image_path)
predictor.graph_test_result(predicted_image, image_path)

# showing unet prediction
plt.imshow(predicted_image)
plt.axis('off')  # no axis ticks
plt.title('Predicted Image')
plt.show()

# showing number prediction
a = predictor.predict_number(predicted_image, image_path)

print(a)