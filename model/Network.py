# -*- coding: utf-8 -*-
from keras.models import Graph
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import PReLU
from encoder import SIZE


def createModel():
    model = Graph()

    model.add_input(name="cards", input_shape=(52*9,))
    model.add_input(name="state", input_shape=(81+8*8,))
    model.add_input(name="bet", input_shape=(1,))

    model.add_node(layer=Dense(1024), name="cards1", input="cards")
    model.add_node(layer=Activation("relu"), name="cards1Act", input="cards1")
    model.add_node(layer=BatchNormalization, name='card1Norm', input='cards1Act')

    model.add_node(layer=Dense(1024), name="cards2", input="cards1Norm")
    model.add_node(layer=Activation("relu"), name="cards2Act", input="cards2")
    model.add_node(layer=BatchNormalization, name='card2Norm', input='cards2Act')

    model.add_node(layer=Dense(1024), name="sum", inputs=["cards2Norm", "state", "bet"])
    model.add_node(layer=Activation("relu"), name="sumAct", input="sum")
    model.add_node(layer=BatchNormalization, name='sumNorm', input='sumAct')

    model.add_node(layer=Dense(1), name="res", input="sumNorm")
    model.add_node(layer=Activation("linear"), name="resAct", input="res")

    model.add_output(name='output', input='resAct')

    model.compile('adam', {'output':'mse'})
    return model