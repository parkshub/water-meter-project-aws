from tensorflow.keras import models
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, Concatenate

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
        x, skip_connections, inputs = self.buildEncoder()
        x = self.buildBottleneck(x)
        outputs = self.buildDecoder(x, skip_connections)
        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.model = model

        return model
