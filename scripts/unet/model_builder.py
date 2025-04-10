import tensorflow as tf
from tensorflow.keras import models
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, Concatenate
from tensorflow.keras.optimizers import Adam


def weighted_binary_crossentropy(zero_weight=1.0, one_weight=15.0):
    def loss(y_true, y_pred):
        bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
        weight_vector = y_true * one_weight + (1. - y_true) * zero_weight
        weight_vector = tf.squeeze(weight_vector, axis=-1)
        weighted_bce = weight_vector * bce
        return tf.reduce_mean(weighted_bce)

    return loss


class ModelBuilder:
    def __init__(self, input_shape):
        self.input_shape = input_shape
        self.model = None

    def buildEncoder(self):
        skip_connections = []
        inputs = Input(shape=self.input_shape)

        x = Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
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

        # train_dataset, test_dataset = self.ImageDataLoader.load_data()
        x, skip_connections, inputs = self.buildEncoder()
        x = self.buildBottleneck(x)
        outputs = self.buildDecoder(x, skip_connections)
        model = models.Model(inputs=inputs, outputs=outputs)
        # model.compile(optimizer=Adam(learning_rate=1e-4), loss='binary_crossentropy', metrics=['accuracy'])
        model.compile(
            # loss='binary_crossentropy',
            metrics=['accuracy'],
            loss=weighted_binary_crossentropy(zero_weight=1.0, one_weight=5.0),
        )

        self.model = model

        return model
