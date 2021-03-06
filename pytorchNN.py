from __future__ import print_function
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as tfun
from myutils import *
from nnutils import *
from sklearn.utils import shuffle
from torch.autograd import Variable
import torchvision.models as models


def test_pytorch_nn():
    net = Net()
    print(net)

    params = list(net.parameters())  
    print(len(params))   # list of major params matrices
    print(params[0].size())  # conv1's .weight

    input = torch.randn(1, 1, 32, 32)  # initial dummy input
    output = net(input)
    target = torch.arange(1, 11)  # a dummy target, for example
    target = target.view(1, -1)  # what is this ??
    criterion = nn.MSELoss()

    loss = criterion(output, target)
    print('loss tree',loss)
    print(loss.grad_fn)  # MSELoss
    print(loss.grad_fn.next_functions[0][0])  # Linear
    print(loss.grad_fn.next_functions[0][0].next_functions[0][0])  # ReLU

    # backprop
    loss.backward()
    print('conv1.bias.grad after backward')
    print(net.conv1.bias.grad)

    # sample backprop otpmizer
    import torch.optim as optim
    optimizer = optim.SGD(net.parameters(), lr=0.01) # learning rate 0.01 / for each parameter matrix

    # in your training loop:
    for epoch in range(500):
        optimizer.zero_grad()   # zero the gradient buffers
        output = net(input)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()    # Does the update
        if (epoch % 100 == 0):
            print('Epoch %s MSE %s' % (epoch, loss))

    print('conv1.bias.grad after optimizer')
    print(net.conv1.bias.grad)
    print ('--training done---')

    print('--test start---')
    test_input = torch.randn(1, 1, 32, 32)  # initial dummy input
    print ('input',test_input)
    print ('output/prediction',net.forward(test_input))   # returns activation

# apply higher level nn.Net lib to text
def test_pytorch_nn_gaga(t=1000):
    torch.set_printoptions(threshold=20, edgeitems=7)
    net = GagaNet()
    print(net) # print structure

    # get test data
    data, yarr, features, fnames = getGagaData(maxrows=500, maxfeatures=500, gtype=None, stopwords='english')
    
    xMatrix = shuffle(data, random_state=0)
    yArr = shuffle(yarr, random_state=0)
    partition = int(.70*len(yArr))
    trainingX = xMatrix[:partition]
    trainingY = yArr[:partition]
    testX = xMatrix[partition:]
    testY = yArr[partition:]

    input = torch.tensor(xMatrix, dtype=torch.float)  # m x 500
    target = torch.tensor(yArr, dtype=torch.float).view(-1,1)    # 1 x m
    test_input = torch.tensor(testX, dtype=torch.float)  # m x 500
    test_target =torch.tensor(testY, dtype=torch.float).view(-1,1)

    criterion = nn.MSELoss()
    output = net(input)
    loss = criterion(output, target)
    print('loss tree',loss)
    print(loss.grad_fn)  # MSELoss
    print(loss.grad_fn.next_functions[0][0])  # Linear

    # backprop
    loss.backward()
    print('net.inp.weight after backward')
    print(net.inp.weight)
 #   print(net.inp.weight.grad)

    # sample backprop otpmizer
    import torch.optim as optim
    optimizer = optim.SGD(net.parameters(), lr=0.01) # learning rate 0.01 / for each parameter matrix

    # in your training loop:
    for epoch in range(2500):
        optimizer.zero_grad()   # zero the gradient buffers
        output = net(input)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()    # Does the update
        if (epoch % 250 == 0):
            print('Epoch %s MSE %s' % (epoch, loss))

    print('net.inp.weight after gradient descent')
    print(net.inp.weight)
    print ('--training done---')

    test_res = net.forward(test_input)
    test_res_round = test_res.round()
    test_diff = test_res_round - test_target
    print ('output', test_res.view(1,-1))  
    print ('output rounded', test_res_round.view(1,-1))  
    print ('expected output', test_target.view(1,-1))  
    print ('err / total, %', test_diff.abs().sum().item(), len(test_diff),(len(test_diff)- test_diff.abs().sum().item()) / (len(test_diff)))


from torch.autograd import Variable
import torch.nn.functional as F

class SimpleRNN(rotch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleRNN, self).__init__()

        self.hidden_size = hidden_size

        self.i2h = nn.Linear(input_size + hidden_size, hidden_size)
        self.i2o = nn.Linear(input_size + hidden_size, output_size)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        combined = torch.cat((input, hidden), 1)
        hidden = self.i2h(combined)
        output = self.i2o(combined)
        output = self.softmax(output)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, self.hidden_size)

# n_hidden = 128
# rnn = SimpleRNN(n_letters, n_hidden, n_categories)

class SimpleCNN(torch.nn.Module):    
    #Our batch shape for input x is (3, 32, 32)
    
    def __init__(self):
        super(SimpleCNN, self).__init__()
        
        #Input channels = 3, output channels = 18
        self.conv1 = torch.nn.Conv2d(3, 18, kernel_size=3, stride=1, padding=1)
        self.pool = torch.nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        
        #4608 input features, 64 output features (see sizing flow below)
        self.fc1 = torch.nn.Linear(18 * 16 * 16, 64)
        
        #64 input features, 10 output features for our 10 defined classes
        self.fc2 = torch.nn.Linear(64, 10)
        
    def forward(self, x):
        
        #Computes the activation of the first convolution
        #Size changes from (3, 32, 32) to (18, 32, 32)
        x = F.relu(self.conv1(x))
        
        #Size changes from (18, 32, 32) to (18, 16, 16)
        x = self.pool(x)
        
        #Reshape data to input to the input layer of the neural net
        #Size changes from (18, 16, 16) to (1, 4608)
        #Recall that the -1 infers this dimension from the other given dimension
        x = x.view(-1, 18 * 16 *16)
        
        #Computes the activation of the first fully connected layer
        #Size changes from (1, 4608) to (1, 64)
        x = F.relu(self.fc1(x))
        
        #Computes the second fully connected layer (activation applied later)
        #Size changes from (1, 64) to (1, 10)
        x = self.fc2(x)
        return(x)
        
import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-t', help='batch size', type=int)
args = vars(parser.parse_args())

_t = args['t']

test_pytorch_nn_gaga(_t)
#test_pytorch_nn()

