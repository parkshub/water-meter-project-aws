import os
import numpy as np
import tensorflow as tf

class ModelPredictor:
    def __init__(self, ImageDataLoader, model='keras'):
        self.ImageDataLoader = ImageDataLoader
        self.model = model
    def predict(self, image_path):
        """Predict the output using the trained model."""
        image = self.ImageDataLoader.preprocess_image(image_path)  # Preprocess the image
        # return image
        image = tf.expand_dims(image, axis=0)  # Add batch dimension

        model = tf.keras.models.load_model(f'unet_model.{self.model}')  # Load the trained model
        prediction = model.predict(image)

        # Post-process the prediction (e.g., threshold for binary segmentation)
        prediction = (prediction > 0.5).astype(np.uint8)  # Threshold for binary output

        # Squeeze the result to remove unnecessary dimensions
        prediction = prediction.squeeze()  # Remove the batch and channel dimensions

        # Display the result using matplotlib


        return prediction

    def graph_test_result(self, prediction, image_path):
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        import numpy as np
        import os

        # Extract paths
        image_name = image_path.split('\\')[-1]
        root_dir = os.getcwd()
        collage_folder = os.path.join(root_dir, 'data', 'collage')
        collage_path = os.path.join(collage_folder, image_name)

        # Load images
        original = mpimg.imread(image_path)
        collage = mpimg.imread(collage_path)

        # If original image is grayscale, convert to RGB for overlay
        if original.ndim == 2:
            original = np.stack([original] * 3, axis=-1)

        # Resize prediction if needed
        if prediction.shape != original.shape[:2]:
            from skimage.transform import resize
            prediction = resize(prediction, original.shape[:2], preserve_range=True)

        # Plotting
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        # Left plot: original + prediction overlay
        axes[0].imshow(original)
        axes[0].imshow(prediction, cmap='jet', alpha=0.4)  # 'jet' colormap for colorful overlay
        axes[0].set_title('Original + Prediction')
        axes[0].axis('off')

        # Right plot: collage image
        axes[1].imshow(collage)
        axes[1].set_title('Collage Image')
        axes[1].axis('off')

        plt.tight_layout()
        plt.show()
