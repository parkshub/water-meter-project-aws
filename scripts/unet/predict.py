import os
from scripts.unet.data_loader import ImageDataLoader
from scripts.unet.model_builder import ModelBuilder
from scripts.unet.model_trainer import ModelTrainer
import os
import random
import tensorflow as tf

# Check if running in an interactive environment (e.g., Jupyter Notebook)
try:
    # In scripts, __file__ will be defined
    script_dir = os.path.dirname(__file__)
except NameError:
    # In interactive environments, use the current working directory
    script_dir = os.getcwd()

# Get the root directory (two levels up)

root_dir = os.getcwd()

# Build path to 'data/images' and 'data/masks'
image_folder = os.path.join(root_dir, 'data', 'images')
mask_folder = os.path.join(root_dir, 'data', 'masks')

random_image = random.randint(0, len(os.listdir(image_folder)))

image_path = os.path.join(image_folder, os.listdir(image_folder)[random_image])
mask_path = os.path.join(mask_folder, os.listdir(mask_folder)[random_image])
image_path, mask_path

data_loader = ImageDataLoader(512, 512, 2)
model_builder = ModelBuilder((512, 512, 1))
trainer = ModelTrainer(data_loader, model_builder)

model = tf.keras.models.load_model('unet_model.keras')

image = model.predict(image_path)