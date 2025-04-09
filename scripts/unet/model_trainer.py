import tensorflow as tf
import numpy as np

class ModelTrainer:
    def __init__(self, ImageDataLoader, ModelBuilder):
        self.ImageDataLoader = ImageDataLoader
        self.ModelBuilder = ModelBuilder

    def train(self, epochs=1):
        # todo this part is redundant, make main provide the test and train set
        train_dataset, test_dataset = self.ImageDataLoader.load_data()

        model = self.ModelBuilder.compileModel()

        history = model.fit(
            train_dataset,
            validation_data=test_dataset,
            epochs=epochs
        )

        model.save('unet_model.keras', save_format='keras')
        model.save('unet_model.h5')

        print("Training complete! Model saved as 'unet_model.keras")
        return history


    def predict(self, image_path):
        """Predict the output using the trained model."""
        image = self.ImageDataLoader.preprocess_image(image_path)  # Preprocess the image
        # return image
        image = tf.expand_dims(image, axis=0)  # Add batch dimension

        model = tf.keras.models.load_model('unet_model.keras')  # Load the trained model
        prediction = model.predict(image)

        # Post-process the prediction (e.g., threshold for binary segmentation)
        prediction = (prediction > 0.5).astype(np.uint8)  # Threshold for binary output

        # Squeeze the result to remove unnecessary dimensions
        prediction = prediction.squeeze()  # Remove the batch and channel dimensions

        # Display the result using matplotlib
        import matplotlib.pyplot as plt
        plt.imshow(prediction, cmap='gray')
        plt.show()

        return prediction