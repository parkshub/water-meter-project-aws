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
parser.add_argument('--batch_size', type=int, default=2, help='Batch size')
parser.add_argument('--epochs', type=int, default=1, help='Number of epochs')
parser.add_argument('--lr_rate', type=float, default=0.001, help='Learning rate')
parser.add_argument('--zero', type=float, default=1.0, help='Zero weight')
parser.add_argument('--one', type=float, default=5.0, help='One weight')
parser.add_argument('--loss', type=str, choices=['bce', 'weighted_bce', 'combo'], default='weighted_bce', help='Loss function (bce, weighted_bce, combo)')
parser.add_argument('--lr_decay', action='store_true', help='Enable learning rate decay')
parser.add_argument('--aug', action='store_true', help='Enable data augmentation')

args = parser.parse_args()

model_config = {
    'input_shape': (args.height, args.width, 1),
    'lr_rate': args.lr_rate,
    'zero_weight': args.zero,
    'one_weight': args.one,
    'loss_type': args.loss,
    'lr_decay': args.lr_decay,
}

pipeline_config = {
    'height': args.height, 
    'width': args.width, 
    'batch_size': args.batch_size,
    'aug': args.aug
}

print(
    f"""
    ------------------------------
    epochs={args.epochs}
    shape=({model_config.input_shape}, 1)
    learning_rate={model_config.lr_rate}
    learning_rate_decay={model_config.lr_decay}
    loss_fn={model_config.loss_type}
    zero_weight={model_config.zero_weight}
    one_weight={model_config.one_weight}
    augmentation={pipeline_config.aug}
    ------------------------------
    """)

data_loader = ImageDataLoader(**pipeline_config)

model_builder = ModelBuilder(**model_config)

trainer = ModelTrainer(data_loader, model_builder)
history = trainer.train(epochs=args.epochs)

with open('unet_training_history.pkl', 'wb') as f:
    pickle.dump(history.history, f)