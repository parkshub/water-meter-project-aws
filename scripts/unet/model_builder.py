import tensorflow as tf
from tensorflow.keras import models
import tensorflow.keras.backend as K
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, Concatenate, Dropout


class ModelBuilder:
    def __init__(self, input_shape, lr_rate=0.001, zero_weight=1.0, one_weight=5.0, loss_type='weighted_bce', lr_decay=False):
        self.input_shape = input_shape
        self.lr_rate = lr_rate
        self.zero_weight = zero_weight
        self.one_weight = one_weight
        self.model = None
        self.loss_type = loss_type
        self.lr_decay = lr_decay

    def get_loss_function(self):
        if self.loss_type == 'bce':
            return tf.keras.losses.BinaryCrossentropy()
        elif self.loss_type == 'weighted_bce':
            return self.weighted_binary_crossentropy()
        elif self.loss_type == 'combo':
            return self.combined_segmentation_loss()
        else:
            raise ValueError(f"Unknown loss type: {self.loss_type}")
        
    def weighted_binary_crossentropy(self):
        def loss(y_true, y_pred):
            bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
            weights = y_true * self.one_weight + (1.0 - y_true) * self.zero_weight
            bce = bce * tf.squeeze(weights, axis=-1) if len(weights.shape) == 4 else bce * weights
            return tf.reduce_mean(bce)
        return loss

    def dice_coefficient(self, y_true, y_pred, smooth=1):
        y_true_f = K.flatten(y_true)
        y_pred_f = K.flatten(y_pred)
        intersection = K.sum(y_true_f * y_pred_f)
        return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

    def total_variation_loss(self, y_pred):
        return tf.reduce_mean(tf.image.total_variation(y_pred))

    def combined_segmentation_loss(self):
        bce_loss_fn = self.weighted_binary_crossentropy()
        def loss(y_true, y_pred):
            bce = bce_loss_fn(y_true, y_pred)
            dice = self.dice_coefficient(y_true, y_pred)
            return dice + 0.5 * bce
        return loss
    
    def get_optimizer(self):
        if self.lr_decay:
            lr = tf.keras.optimizers.schedules.ExponentialDecay(
                initial_learning_rate=self.lr_rate,
                decay_steps=10 * 100,
                decay_rate=0.9,
                staircase=True
            )
        else:
            lr = self.lr_rate

        return Adam(learning_rate=lr)


    def build_encoder(self):
        skip_connections = []
        inputs = Input(shape=self.input_shape)

        x = Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        # x = Dropout(0.1)(x)
        skip_connections.append(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)

        x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
        skip_connections.append(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)

        x = Conv2D(256, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(256, (3, 3), activation='relu', padding='same')(x)
        skip_connections.append(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)

        x = Conv2D(512, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(512, (3, 3), activation='relu', padding='same')(x)
        skip_connections.append(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)

        return x, skip_connections, inputs

    def build_bottleneck(self, x):
        x = Conv2D(1024, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(1024, (3, 3), activation='relu', padding='same')(x)
        # x = Dropout(0.1)(x)
        # todo: consider using conv2dtranspose
        x = UpSampling2D(size=(2, 2))(x)
        x = Conv2D(512, (2, 2), activation='relu', padding='same')(x)

        return x

    def build_decoder(self, x, skip_connections):
        x = Concatenate()([x, skip_connections[3]])
        x = Conv2D(512, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(512, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D(size=(2, 2))(x)

        x = Concatenate()([x, skip_connections[2]])
        x = Conv2D(256, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(256, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D(size=(2, 2))(x)

        x = Concatenate()([x, skip_connections[1]])
        x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D(size=(2, 2))(x)

        x = Concatenate()([x, skip_connections[0]])
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)

        x = Conv2D(1, (1, 1), activation='sigmoid')(x)

        return x

    def compile_model(self):

        x, skip_connections, inputs = self.build_encoder()
        x = self.build_bottleneck(x)
        outputs = self.build_decoder(x, skip_connections)
        model = models.Model(inputs=inputs, outputs=outputs)

        optimizer = self.get_optimizer()
        loss_fn = self.get_loss_function()

        model.compile(
            optimizer=optimizer,
            loss=loss_fn,
            metrics=[self.dice_coefficient],
        )

        self.model = model

        return model
