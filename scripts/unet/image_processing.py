# import tensorflow as tf
# import os
# import random
# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt
# import numpy as np
#
# # Settings
# TARGET_HEIGHT = 512
# TARGET_WIDTH = 512
# GRID_ROWS = 4
# GRID_COLS = 4
#
# def preprocess_image(image_path):
#     image = tf.io.read_file(image_path)
#     image = tf.io.decode_png(image, channels=1)  # Grayscale
#     image = tf.image.resize(image, [TARGET_HEIGHT, TARGET_WIDTH])
#     image = tf.squeeze(image, axis=-1)  # Remove last dimension for plotting
#     return image.numpy()
#
# # Get image list
# image_folder = os.path.join(os.getcwd(), 'data', 'images')
# image_list = os.listdir(image_folder)
#
# # Pick random 16 images
# selected_images = random.sample(image_list, GRID_ROWS * GRID_COLS)
#
# # Plot
# fig, axes = plt.subplots(GRID_ROWS, GRID_COLS, figsize=(12, 12))
#
# for ax, img_name in zip(axes.flat, selected_images):
#     img_path = os.path.join(image_folder, img_name)
#     image = preprocess_image(img_path)
#     ax.imshow(image, cmap='gray')
#     ax.axis('off')
#
# plt.tight_layout()
# plt.show()
