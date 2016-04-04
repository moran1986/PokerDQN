# -*- coding: utf-8 -*-
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import PReLU
from encoder import SIZE


def createModel():
    model = Sequential()

    model.add(Dense(1024, input_shape=(SIZE,)))
    model.add(PReLU())
    #model.add(BatchNormalization())
    #model.add(Dropout(0.5))

    model.add(Dense(1024))
    model.add(PReLU())
    #model.add(BatchNormalization())
    #model.add(Dropout(0.5))

    #model.add(Dense(2048))
    #model.add(PReLU())
    #model.add(BatchNormalization())
    #model.add(Dropout(0.5))

    #model.add(Dense(2048))
    #model.add(PReLU())
    #model.add(BatchNormalization())
    #model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('linear')) #linear output so we can have range of real-valued outputs

    model.compile(loss='mse', optimizer='adam')
    return model