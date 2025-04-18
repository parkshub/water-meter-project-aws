import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import tensorflow as tf
print("TF is using GPU:", tf.config.list_physical_devices('GPU'))
import pickle
import argparse
from scripts.unet.data_loader import ImageDataLoader
from scripts.unet.model_builder import ModelBuilder
from scripts.unet.model_trainer import ModelTrainer

cwd = os.getcwd()

if cwd not in sys.path:
    sys.path.append(cwd)

parser = argparse.ArgumentParser(description="Train UNet model")
parser.add_argument('--height', type=int, default=512, help='Target image height')
parser.add_argument('--width', type=int, default=512, help='Target image width')
parser.add_argument('--batch_size', type=int, default=1, help='Batch size')
parser.add_argument('--epochs', type=int, default=1, help='Number of epochs')
parser.add_argument('--lr_rate', type=float, default=0.001, help='Learning Rate')
parser.add_argument('--zero', type=float, default=1.0, help='Zero Weight')
parser.add_argument('--one', type=float, default=5.0, help='One Weight')
args = parser.parse_args()

data_loader = ImageDataLoader(args.height, args.width, args.batch_size)
model_builder = ModelBuilder((args.height, args.width, 1), args.lr_rate, args.zero, args.one)
trainer = ModelTrainer(data_loader, model_builder)
history = trainer.train(epochs=args.epochs)

with open('unet_training_history.pkl', 'wb') as f:
    pickle.dump(history.history, f)