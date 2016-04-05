# -*- coding: utf-8 -*-
from keras.models import Graph
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import PReLU
from encoder import SIZE


def createModel():
    model = Graph()

    model.add_input(name="cards", input_shape=(52*9,))
    model.add_input(name="state", input_shape=(81+7*8,))
    model.add_input(name="bet", input_shape=(1,))

    model.add_node(layer=Dense(512), name="cards1", input="cards")
    model.add_node(layer=PReLU(), name="cards1Act", input="cards1")

    model.add_node(layer=Dense(512), name="cards2", input="cards1Act")
    model.add_node(layer=PReLU(), name="cards2Act", input="cards2")

    model.add_node(layer=Dense(1024), name="sum", inputs=["cards2Act", "state", "bet"])
    model.add_node(layer=PReLU(), name="sumAct", input="sum")

    model.add_node(layer=Dense(1), name="res", input="sumAct")
    model.add_node(layer=Activation("linear"), name="resAct", input="res")

    model.add_output(name='output', input='resAct')

    model.compile('adam', {'output':'mse'})
    return model