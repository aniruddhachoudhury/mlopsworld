from __future__ import absolute_import, division, print_function, unicode_literals
import os
import click
import dill
import json
import uuid
import random
import shutil
import os.path
import logging
import numpy as np
import pandas as pd
from absl import app
from absl import flags
import tensorflow as tf
from storage import Storage
from tensorflow import keras
from tensorboard.plugins.hparams import api as hp










def model_fn(hparams,metrics):
    """Create a Keras model with the given hyperparameters.
    Args:
      hparams: A dict mapping hyperparameters in `HPARAMS` to values.
      seed: A hashable object to be used as a random seed (e.g., to
        construct dropout layers in the model).
    Returns:
      A compiled Keras model.
    """
    #rng = random.Random(seed)

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Input(shape=(9,)))
    # Add fully connected layers.
    dense_neurons = hparams[HP_NUM_UNITS]
    for _ in range(hparams[HP_DENSE_LAYERS]):
        model.add(tf.keras.layers.Dense(dense_neurons, kernel_initializer=hparams[HP_INTIALIZER], activation="relu"))
        dense_neurons *= 2
    model.add(tf.keras.layers.Dropout(hparams[HP_DROPOUT], )) #seed=rng.random()
    
    for _ in range(hparams[HP_DENSE_LAYERS]):
        model.add(tf.keras.layers.Dense(dense_neurons, kernel_initializer=hparams[HP_INTIALIZER], activation="relu"))
        dense_neurons /= 2
    # Add the final output layer.
    model.add(tf.keras.layers.Dropout(hparams[HP_DROPOUT]))
    model.add(tf.keras.layers.Dense(OUTPUT_CLASSES, activation="sigmoid"))

    model.compile(
        loss=keras.losses.BinaryCrossentropy(),
        optimizer=hparams[HP_OPTIMIZER],
        metrics=metrics,
    )
    return model


def make_model_hpo(hparams,metrics,data,epochs,batch_size):

      ((x_train, y_train), (x_test, y_test))=data
      model=model_fn(hparams,metrics)
      early_stopping = tf.keras.callbacks.EarlyStopping(
                    verbose=1,
                    mode='max',
                    restore_best_weights=True)
      resampled_history = model.fit(
                    x=x_train,
                    y=y_train,
                    epochs=1*epochs,
                    validation_data=(x_test, y_test),
                    callbacks=[tf.keras.callbacks.TensorBoard(tensorboard_logs),  # log metrics
                        hp.KerasCallback(tensorboard_logs, hparams)])
      resampled_results = model.evaluate(x_test, y_test,batch_size=batch_size,verbose=0)
      return resampled_results[0],resampled_results[1]
    
def run(run_dir, hparams,data,metrics,epochs,batch_size):
  with tf.summary.create_file_writer(run_dir).as_default():
    hp.hparams(hparams) 
    _,accuracy=make_model_hpo(hparams,metrics,data,epochs,batch_size)
    tf.summary.scalar(BINARY_ACCURACY, accuracy, step=1)
    return accuracy

@click.command()
@click.option('--epochs', default=10)
@click.option('--batch-size', default=4)
@click.option('--tensorboard-gcs-logs', default='gs://feastproject/taxi/logs')
def train_model(epochs,batch_size,tensorboard_gcs_logs):
        


        global BINARY_ACCURACY 
        global OUTPUT_CLASSES
        global tensorboard_logs
        global HP_NUM_UNITS
        global HP_DENSE_LAYERS
        global HP_DROPOUT
        global HP_OPTIMIZER
        global HP_INTIALIZER



        tensorboard_logs="/mnt/hyparams/"
        
        with open("/mnt/training.data", 'rb') as in_f:
                x_train= dill.load(in_f)
       

        with open("/mnt/validation.data", 'rb') as in_f:
                x_test= dill.load(in_f)
        
        with open("/mnt/trainingtarget.data", 'rb') as in_f:
                y_train= dill.load(in_f)
  
       
        with open("/mnt/validationtarget.data", 'rb') as in_f:
                y_test= dill.load(in_f)



        metrics = [
                keras.metrics.BinaryAccuracy(name='accuracy'),
                 ]

        OUTPUT_CLASSES = 1

       
        HP_NUM_UNITS = hp.HParam('num_units', hp.Discrete([8,16,32]))
        HP_DENSE_LAYERS = hp.HParam("dense_layers", hp.Discrete([1, 3]))
        HP_DROPOUT = hp.HParam("dropout", hp.RealInterval(0.1, 0.4))
        HP_OPTIMIZER = hp.HParam("optimizer", hp.Discrete(["adam", "adagrad","sgd"]))
        HP_INTIALIZER= hp.HParam("intializer", hp.Discrete(["glorot_uniform", "random_uniform"]))



        HPARAMS = [
                    HP_NUM_UNITS,
                    HP_DENSE_LAYERS,
                    HP_DROPOUT,
                    HP_OPTIMIZER,
                    HP_INTIALIZER
                  ]


   
        BINARY_ACCURACY = 'accuracy'   

        METRICS=[ hp.Metric(BINARY_ACCURACY, display_name='accuracy')]


        with tf.summary.create_file_writer(tensorboard_logs).as_default():
            hp.hparams_config(
                        hparams=HPARAMS,
                        metrics=METRICS        
                             )


        session_num = 0

        model_results=pd.DataFrame()

        NO_UNITS=[]
        DROP_OUT=[]
        OPTIMIZER=[]
        INTIALIZER=[]
        DENSE_LAYERS=[]
        ACCURACY=[]

        # Tensorflow Hyperparameter
        data=((x_train, y_train), (x_test, y_test))

        for dense_layers in HP_DENSE_LAYERS.domain.values: 
            for num_units in HP_NUM_UNITS.domain.values:
                for dropout_rate in (HP_DROPOUT.domain.min_value, HP_DROPOUT.domain.max_value):
                    for optimizer in HP_OPTIMIZER.domain.values:
                        for intializer in HP_INTIALIZER.domain.values:

                                hparams = {
                                    HP_NUM_UNITS: num_units,
                                    HP_DROPOUT: dropout_rate,
                                    HP_OPTIMIZER: optimizer,
                                    HP_INTIALIZER: intializer,
                                    HP_DENSE_LAYERS: dense_layers
                                }
                                NO_UNITS.append(num_units)
                                DROP_OUT.append(dropout_rate)
                                OPTIMIZER.append(optimizer)
                                INTIALIZER.append(intializer)
                                DENSE_LAYERS.append(dense_layers)

                                run_name = "run-%d" % session_num
                                print('--- Starting trial: %s' % run_name)
                                print({h.name: hparams[h] for h in hparams})
                                accuracy=run(tensorboard_logs + run_name, hparams,data,metrics,epochs,batch_size)
                                ACCURACY.append(accuracy)
                                session_num += 1


        model_results['Number_Of_Units']=NO_UNITS
        model_results['Optimizer']=OPTIMIZER
        model_results['Intializer']=INTIALIZER
        model_results['Dense_Layers']=DENSE_LAYERS
        model_results['Drop_out']=DROP_OUT
        model_results['Accuracy']=ACCURACY

        model_results.to_csv('/mnt/results.csv',index=False)

        


         
        unique = uuid.uuid4().hex[:12]
        tensor_path=os.path.join(tensorboard_gcs_logs,unique)
       
        Storage.upload(tensorboard_logs,tensor_path)
        
        metadata = {
                'outputs': [{
                        'type': 'tensorboard',
                        'source': tensor_path,        
                }]
                }
        with open("/mlpipeline-ui-metadata.json", 'w') as f:
                json.dump(metadata,f)
        
    
   
if __name__ == "__main__":
    train_model()