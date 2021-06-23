
```
sentinel update-config watch-syslog-sklearn-2 '{"config":"logstream","logfile":"stream","sklearn":[{"neural_network.MLPClassifier":["eventMessage","messageType","category"]}]}'
```

https://scikit-learn.org/stable/modules/neural_networks_supervised.html

Multi-layer Perceptron (MLP) is a supervised learning algorithm.  
Class MLPClassifier implements a multi-layer perceptron (MLP) algorithm that trains using Backpropagation.  

from sklearn.neural_network import MLPClassifier



