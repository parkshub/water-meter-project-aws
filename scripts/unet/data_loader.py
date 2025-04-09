import os
import tensorflow as tf
from sklearn.model_selection import train_test_split


class ImageDataLoader:
    def __init__(self, target_height, target_width, batch_size):
        self.target_height = target_height
        self.target_width = target_width
        self.batch_size = batch_size
        self.grid_rows = 4
        self.grid_cols = 4
        self.image_folder = os.path.join(os.getcwd(), 'data', 'images')
        self.mask_folder = os.path.join(os.getcwd(), 'data', 'masks')

    def extract_paths(self):
        image_paths = sorted([os.path.join(self.image_folder, image) for image in os.listdir(self.image_folder)])
        mask_paths = sorted([os.path.join(self.mask_folder, mask) for mask in os.listdir(self.mask_folder)])

        train_img_paths, test_img_paths, train_mask_paths, test_mask_paths = train_test_split(
            image_paths, mask_paths, test_size=0.2, random_state=42
        )

        return (train_img_paths, train_mask_paths), (test_img_paths, test_mask_paths)

    def preprocess_image(self, image_path, mask_path=None):
        image = tf.io.read_file(image_path)
        image = tf.io.decode_png(image, channels=1)
        image = tf.image.resize(image, [self.target_height, self.target_width])
        image = tf.cast(image, tf.float32) / 255.0

        if mask_path is not None:
            mask = tf.io.read_file(mask_path)
            mask = tf.io.decode_png(mask, channels=1)
            mask = tf.image.resize(mask, [self.target_height, self.target_width], method='nearest')
            mask = tf.cast(mask, tf.float32) / 255.0

            return image, mask

        return image

    def create_dataset_pipeline(self, image_paths, mask_paths, train_set=True):
        dataset = tf.data.Dataset.from_tensor_slices((image_paths, mask_paths))
        dataset = dataset.map(self.preprocess_image, num_parallel_calls=tf.data.AUTOTUNE)

        if train_set:
            dataset = dataset.shuffle(len(image_paths)).batch(self.batch_size).prefetch(tf.data.AUTOTUNE)
        else:
            dataset = dataset.batch(self.batch_size).prefetch(tf.data.AUTOTUNE)

        return dataset

    def load_data(self):
        (train_img_paths, train_mask_paths), (test_img_paths, test_mask_paths) = self.extract_paths()
        train_dataset = self.create_dataset_pipeline(train_img_paths, train_mask_paths, train_set=True)
        test_dataset = self.create_dataset_pipeline(test_img_paths, test_mask_paths, train_set=False)

        return train_dataset, test_dataset

    def plot_data(self):
        import matplotlib
        import random
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt

        image_paths = [os.path.join(self.image_folder, image) for image in os.listdir(self.image_folder)]
        random_images = random.sample(image_paths, 9)
        fig, axes = plt.subplots(3, 3, figsize=(10, 10))

        for ax, img_path in zip(axes.flatten(), random_images):
            img = plt.imread(img_path)
            ax.imshow(img)
            ax.axis('off')

        plt.tight_layout()
        plt.show()