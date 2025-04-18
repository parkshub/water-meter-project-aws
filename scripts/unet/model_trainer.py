import tensorflow as tf
import numpy as np
import matplotlib
# matplotlib.use('TkAgg')
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

class ModelTrainer:
    def __init__(self, ImageDataLoader, ModelBuilder):
        self.ImageDataLoader = ImageDataLoader
        self.ModelBuilder = ModelBuilder

    def train(self, epochs=1):
        train_dataset, test_dataset = self.ImageDataLoader.load_data()

        model = self.ModelBuilder.compileModel()

        # Get one example from train and test
        train_batch = next(iter(train_dataset))
        test_batch = next(iter(test_dataset))

        train_image = train_batch[0][0]
        train_mask = train_batch[1][0]
        test_image = test_batch[0][0]
        test_mask = test_batch[1][0]

        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        )

        checkpoint_h5 = ModelCheckpoint(
            filepath='best_model.h5',
            monitor='val_loss',
            save_best_only=True,
            mode='min',
            verbose=1
        )

        checkpoint_keras = ModelCheckpoint(
            filepath='best_model.keras',
            monitor='val_loss',
            save_best_only=True,
            mode='min',
            verbose=1
        )

        class DisplayCallback(tf.keras.callbacks.Callback):
            def __init__(self, train_example, test_example):
                super().__init__()
                self.train_image, self.train_mask = train_example
                self.test_image, self.test_mask = test_example

            def on_epoch_end(self, epoch, logs=None):
                def predict_and_threshold(img):
                    pred = self.model.predict(tf.expand_dims(img, axis=0))[0]
                    pred_03 = (pred > 0.3).astype("uint8")
                    pred_05 = (pred > 0.5).astype("uint8")
                    return tf.squeeze(pred_03), tf.squeeze(pred_05)

                train_pred_03, train_pred_05 = predict_and_threshold(self.train_image)
                test_pred_03, test_pred_05 = predict_and_threshold(self.test_image)

                plt.figure(figsize=(15, 10))

                # Row 1: Train
                plt.subplot(2, 4, 1)
                plt.imshow(tf.squeeze(self.train_image), cmap='gray')
                plt.title('Train Input')

                plt.subplot(2, 4, 2)
                plt.imshow(tf.squeeze(self.train_mask), cmap='gray')
                plt.title('Train Mask')

                plt.subplot(2, 4, 3)
                plt.imshow(train_pred_03, cmap='gray')
                plt.title('Train Pred @ 0.3')

                plt.subplot(2, 4, 4)
                plt.imshow(train_pred_05, cmap='gray')
                plt.title('Train Pred @ 0.5')

                # Row 2: Test
                plt.subplot(2, 4, 5)
                plt.imshow(tf.squeeze(self.test_image), cmap='gray')
                plt.title('Test Input')

                plt.subplot(2, 4, 6)
                plt.imshow(tf.squeeze(self.test_mask), cmap='gray')
                plt.title('Test Mask')

                plt.subplot(2, 4, 7)
                plt.imshow(test_pred_03, cmap='gray')
                plt.title('Test Pred @ 0.3')

                plt.subplot(2, 4, 8)
                plt.imshow(test_pred_05, cmap='gray')
                plt.title('Test Pred @ 0.5')

                plt.tight_layout()
                plt.savefig(f"prediction_epoch_{epoch + 1}.png")
                plt.close()


        history = model.fit(
            train_dataset,
            validation_data=test_dataset,
            epochs=epochs,
            callbacks=[DisplayCallback((train_image, train_mask), (test_image, test_mask)), checkpoint_h5, checkpoint_keras, early_stop]
        )

        model.save('unet_model.keras', save_format='keras')
        model.save('unet_model.h5')

        print("Training complete! Model saved as 'unet_model.keras")
        return history

