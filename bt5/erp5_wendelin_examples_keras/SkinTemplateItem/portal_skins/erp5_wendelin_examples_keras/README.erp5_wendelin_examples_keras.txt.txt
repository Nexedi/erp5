You need a wendelin instance that contains keras.
Use this software release to built it.
https://lab.nexedi.com/nexedi/slapos/raw/master/software/wendelin/software-kerastensorflow.cfg

call_keras_vgg16_predict
--------------------------
You can use a trained neural network for image classification.

call_train_keras and call_read_keras_log
--------------------------------------------
You can train and save and load neural network. Call call_train_keras, you can run a model training and save the model in a data stream. Next time you run, it loads the model from the data stream and continue training. You can use call_read_keras_log to read keras output.
