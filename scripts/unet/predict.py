import os
import sys
import random
import pickle
import tensorflow as tf
from scripts.unet.data_loader import ImageDataLoader
from scripts.unet.model_builder import ModelBuilder
from scripts.unet.model_trainer import ModelTrainer
from scripts.unet.model_predict import ModelPredictor
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt



root_dir = os.getcwd()


# Build path to 'data/images' and 'data/masks'
image_folder = os.path.join(root_dir, 'data', 'images')
mask_folder = os.path.join(root_dir, 'data', 'masks')

random_image = random.randint(0, len(os.listdir(image_folder)) - 1)

image_path = os.path.join(image_folder, os.listdir(image_folder)[random_image])
mask_path = os.path.join(mask_folder, os.listdir(mask_folder)[random_image])
print(image_path, mask_path)

data_loader = ImageDataLoader(512, 512, 2)
predictor = ModelPredictor(data_loader, 'h5')

predicted_image = predictor.predict(image_path)
predictor.graph_test_result(predicted_image, image_path)

plt.imshow(predicted_image)
plt.axis('off')  # no axis ticks
plt.title('Predicted Image')
plt.show()