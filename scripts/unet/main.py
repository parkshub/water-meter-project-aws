from scripts.unet.data_loader import ImageDataLoader
from scripts.unet.model_builder import ModelBuilder
from scripts.unet.model_trainer import ModelTrainer

# Initialize
data_loader = ImageDataLoader(512, 512, 32)
model_builder = ModelBuilder((512, 512, 1))

# Feed them to trainer
trainer = ModelTrainer(data_loader, model_builder)
trainer.train(epochs=1)