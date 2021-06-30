

sentinel update-config watch-syslog-sklearn-3 '{"config":"logstream","logfile":"stream","sklearn":[{"naive_bayes.MultinomialNB":["eventMessage","messageType","category"]},{"naive_bayes.BernoulliNB":["eventMessage","messageType","category"],"TfidfVectorizer":{}},{"neural_network.MLPClassifier":["eventMessage","messageType","category"],"HashingVectorizer":{"n_features": 20},"train_test_split":{"test_size": 0.2,"random_state": 21},"classifier":{"hidden_layer_sizes":"150,100,50","max_iter":300,"activation":"relu","solver":"adam","random_state":1}}]}'



sentinel update-config watch-syslog-sklearn-3 '{"config":"logstream","logfile":"stream","sklearn":[{"naive_bayes.MultinomialNB":["eventMessage","messageType","category"],"CountVectorizer":{}},{"naive_bayes.BernoulliNB":["eventMessage","messageType","category"],"CountVectorizer":{},"train_test_split":{}},{"neural_network.MLPClassifier":["eventMessage","messageType","category"],"HashingVectorizer":{"n_features": 20},"train_test_split":{"test_size": 0.2,"random_state": 21},"classifier":{"hidden_layer_sizes":"150,100,50","max_iter":300,"activation":"relu","solver":"adam","random_state":1}}]}'




sentinel update-config watch-syslog-sklearn-3 '{"config":"logstream","logfile":"stream","sklearn":[{"naive_bayes.MultinomialNB":["eventMessage","messageType","category"],"CountVectorizer":[],"train_test_split":[]},{"naive_bayes.BernoulliNB":["eventMessage","messageType","category"],"CountVectorizer":[],"train_test_split":[]},{"neural_network.MLPClassifier":["eventMessage","messageType","category"],"CountVectorizer":[],"train_test_split":[{"test_size": 0.2},{"random_state": 21}]}]}'

sentinel update-config watch-syslog-sklearn-3 '{"config":"logstream","logfile":"stream","sklearn":[{"naive_bayes.MultinomialNB":["eventMessage","messageType","category"]},{"naive_bayes.BernoulliNB":["eventMessage","messageType","category"]},{"neural_network.MLPClassifier":["eventMessage","messageType","category"],"CountVectorizer":[],"train_test_split":[{"test_size": 0.2},{"random_state": 21}]}]}'


sentinel update-config watch-syslog-sklearn-3 '{"config":"logstream","logfile":"stream","sklearn":[{"neural_network.MLPClassifier":["eventMessage","messageType","category"],"CountVectorizer":[],"train_test_split":[{"test_size": 0.2,"random_state": 21}],"classifier":[{"hidden_layer_sizes":"150,100,50"}]}]}'


sentinel update-config watch-syslog-sklearn-3 '{"config":"logstream","logfile":"stream","sklearn":[{"neural_network.MLPClassifier":["eventMessage","messageType","category"],"CountVectorizer":{},"train_test_split":{"test_size": 0.2,"random_state": 21},"classifier":{"hidden_layer_sizes":"150,100,50","max_iter":300,"activation":"relu","solver":"adam","random_state":1}}]}'

sentinel update-config watch-syslog-sklearn-3 '{"config":"logstream","logfile":"stream","sklearn":[{"neural_network.MLPClassifier":["eventMessage","messageType","category"],"HashingVectorizer":{"n_features": 20},"train_test_split":{"test_size": 0.2,"random_state": 21},"classifier":{"hidden_layer_sizes":"150,100,50","max_iter":300,"activation":"relu","solver":"adam","random_state":1}}]}'




