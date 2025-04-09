import pickle
import argparse
from scripts.unet.data_loader import ImageDataLoader
from scripts.unet.model_builder import ModelBuilder
from scripts.unet.model_trainer import ModelTrainer

parser = argparse.ArgumentParser(description="Train UNet model")
parser.add_argument('--height', type=int, default=512, help='Target image height')
parser.add_argument('--width', type=int, default=512, help='Target image width')
parser.add_argument('--batch_size', type=int, default=2, help='Batch size')
parser.add_argument('--epochs', type=int, default=1, help='Number of epochs')
args = parser.parse_args()

print('\n', args.height, args.width, args.batch_size, args.epochs, '\n')

data_loader = ImageDataLoader(args.height, args.width, args.batch_size)
model_builder = ModelBuilder((args.height, args.width, 1))

trainer = ModelTrainer(data_loader, model_builder)
history = trainer.train(epochs=args.epochs)

with open('unet_training_history.pkl', 'wb') as f:
    pickle.dump(history.history, f)