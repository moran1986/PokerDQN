# -*- coding: utf-8 -*-
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from encoder import SIZE


def createModel():
    model = Sequential()

    model.add(Dense(2048, input_shape=(SIZE,)))
    model.add(Activation('relu'))
    #model.add(Dropout(0.2)) I'm not using dropout, but maybe you wanna give it a try?

    model.add(Dense(2048))
    model.add(Activation('relu'))
    #model.add(Dropout(0.2))

    model.add(Dense(2048))
    model.add(Activation('relu'))
    #model.add(Dropout(0.2))

    model.add(Dense(2048))
    model.add(Activation('relu'))
    #model.add(Dropout(0.2))

    model.add(Dense(1))
    model.add(Activation('linear')) #linear output so we can have range of real-valued outputs

    model.compile(loss='mse', optimizer='adam')
    return model