import tensorflow as tf
from tensorflow.keras import models
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, Concatenate, Dropout
from tensorflow.keras.optimizers import Adam
import tensorflow.keras.backend as K

def weighted_binary_crossentropy(y_true, y_pred, zero_weight, one_weight):
    bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    weight_vector = y_true * one_weight + (1. - y_true) * zero_weight
    weight_vector = tf.squeeze(weight_vector, axis=-1)
    weighted_bce = weight_vector * bce
    return tf.reduce_mean(weighted_bce)


def dice_coefficient(y_true, y_pred, smooth=1):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

def total_variation_loss(y_pred):
    return tf.reduce_mean(tf.image.total_variation(y_pred))

def combined_segmentation_loss(zero_weight=1.0, one_weight=5.0):
    def loss(y_true, y_pred):
        weighted_bce = weighted_binary_crossentropy(y_true, y_pred, zero_weight, one_weight)
        dice = dice_coefficient(y_true, y_pred)
        # tv = total_variation_loss(y_pred)

        # return dice + 0.5 * weighted_bce + 0.1 * tv
        return dice + 0.5 * weighted_bce
    return loss


class ModelBuilder:
    def __init__(self, input_shape, lr_rate=0.001, zero_weight=1.0, one_weight=5.0):
        self.input_shape = input_shape
        self.lr_rate = lr_rate
        self.zero_weight = zero_weight
        self.one_weight = one_weight
        self.model = None
        print(
            f"""
            ------------------------------
            shape=({self.input_shape}, 1)
            learning_rate={self.lr_rate}
            zero_weight={self.zero_weight}
            one_weight={self.one_weight}
            ------------------------------
            """)

    def buildEncoder(self):
        skip_connections = []
        inputs = Input(shape=self.input_shape)

        x = Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        x = Dropout(0.1)(x)
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

    def buildBottleneck(self, x):
        x = Conv2D(1024, (3, 3), activation='relu', padding='same')(x)
        x = Conv2D(1024, (3, 3), activation='relu', padding='same')(x)
        # x = Dropout(0.1)(x)
        # todo: consider using conv2dtranspose
        x = UpSampling2D(size=(2, 2))(x)
        x = Conv2D(512, (2, 2), activation='relu', padding='same')(x)

        return x

    def buildDecoder(self, x, skip_connections):
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

    def compileModel(self):

        x, skip_connections, inputs = self.buildEncoder()
        x = self.buildBottleneck(x)
        outputs = self.buildDecoder(x, skip_connections)
        model = models.Model(inputs=inputs, outputs=outputs)

        lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
            initial_learning_rate=self.lr_rate,
            decay_steps=10 * 100,
            decay_rate=0.9,
            staircase=True
        )
        
        model.compile(
            optimizer=Adam(learning_rate=lr_schedule),
            loss=combined_segmentation_loss(zero_weight=self.zero_weight, one_weight=self.one_weight),
            metrics=[dice_coefficient],
        )

        self.model = model

        return model
