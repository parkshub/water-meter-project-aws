class ModelTrainer:
    def __init__(self, ImageDataLoader, ModelBuilder):
        self.ImageDataLoader = ImageDataLoader
        self.ModelBuilder = ModelBuilder

    def train(self, epochs=1):
        train_dataset, test_dataset = self.ImageDataLoader.load_data()

        model = self.ModelBuilder.compileModel()

        history = model.fit(
            train_dataset,
            validation_data=test_dataset,
            epochs=epochs
        )

        model.save('unet_model.h5')

        print("Training complete! Model saved as 'unet_model.h5'")
        return history
