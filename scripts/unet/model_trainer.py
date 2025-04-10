import tensorflow as tf
import numpy as np
import matplotlib
# matplotlib.use('TkAgg')
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class ModelTrainer:
    def __init__(self, ImageDataLoader, ModelBuilder):
        self.ImageDataLoader = ImageDataLoader
        self.ModelBuilder = ModelBuilder

    def train(self, epochs=1):
        train_dataset, test_dataset = self.ImageDataLoader.load_data()

        model = self.ModelBuilder.compileModel()

        example_batch = next(iter(test_dataset))
        example_image = example_batch[0][0]  # One image
        example_mask = example_batch[1][0]  # Corresponding mask

        class DisplayCallback(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                pred = self.model.predict(tf.expand_dims(example_image, axis=0))[0]

                pred_03 = (pred > 0.3).astype("uint8")  # Threshold 0.3
                pred_05 = (pred > 0.5).astype("uint8")  # Threshold 0.5

                pred_03 = tf.squeeze(pred_03)
                pred_05 = tf.squeeze(pred_05)

                plt.figure(figsize=(15, 5))

                plt.subplot(1, 4, 1)
                plt.imshow(tf.squeeze(example_image), cmap='gray')
                plt.title('Input Image')

                plt.subplot(1, 4, 2)
                plt.imshow(tf.squeeze(example_mask), cmap='gray')
                plt.title('True Mask')

                plt.subplot(1, 4, 3)
                plt.imshow(pred_03, cmap='gray')
                plt.title(f'Pred @ 0.3')

                plt.subplot(1, 4, 4)
                plt.imshow(pred_05, cmap='gray')
                plt.title(f'Pred @ 0.5')

                plt.tight_layout()
                plt.savefig(f"prediction_epoch_{epoch + 1}.png")
                plt.close()

        history = model.fit(
            train_dataset,
            validation_data=test_dataset,
            epochs=epochs,
            callbacks=[DisplayCallback()]
        )

        model.save('unet_model.keras', save_format='keras')
        model.save('unet_model.h5')

        print("Training complete! Model saved as 'unet_model.keras")
        return history

