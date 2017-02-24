import warnings
import numpy as np
from keras import backend as K
from keras import __version__ as keras_version
from keras.models import Sequential
from keras.models import model_from_config
from keras.optimizers import optimizer_from_config
from keras import optimizers

def save_model(model, model_store=None):
  data = {}
  data['keras_version'] = keras_version
  data['model_config'] = {'class_name':model.__class__.__name__,
                          'config':model.get_config()}

  # save weights
  if hasattr(model, 'flattened_layers'):
    # Support for legacy Sequential/Merge behavior.
    flattened_layers = model.flattened_layers
  else:
    flattened_layers = model.layers

  data['layer_names'] = [layer.name for layer in flattened_layers]
  layer_group = {}
  for layer in flattened_layers:
    group = layer_group[layer.name] = {}
    symbolic_weights = layer.weights
    weight_values = K.batch_get_value(symbolic_weights)
    weight_names = []
    for i, (w, val) in enumerate(zip(symbolic_weights, weight_values)):
      if hasattr(w, 'name') and w.name:
        name = str(w.name)
      else:
        name = 'param_' + str(i)
      weight_names.append(name)
    group['weight_names'] = weight_names
    group['weight_values'] = []
    for name, val in zip(weight_names, weight_values):
      group['weight_values'].append(val.copy())
    data['model_weights'] = layer_group

  if hasattr(model, 'optimizer'):
    if isinstance(model.optimizer, optimizers.TFOptimizer):
      warnings.warn(
        'TensorFlow optimizers do not '
        'make it possible to access '
        'optimizer attributes or optimizer state '
        'after instantiation. '
        'As a result, we cannot save the optimizer '
        'as part of the model save file.'
        'You will have to compile your model again after loading it. '
        'Prefer using a Keras optimizer instead '
        '(see keras.io/optimizers).')
    else:
      data['training_config'] = {
        'optimizer_config':{
          'class_name':model.optimizer.__class__.__name__,
          'config':model.optimizer.get_config()},
        'loss': model.loss,
        'metrics': model.metrics,
        'sample_weight_mode': model.sample_weight_mode,
        'loss_weights': model.loss_weights,
      }

      # save optimizer weights
      symbolic_weights = getattr(model.optimizer, 'weights')
      if symbolic_weights:
        data['optimizer_weights'] = {}
        weight_values = K.batch_get_value(symbolic_weights)
        weight_names = []
        for i, (w, val) in enumerate(zip(symbolic_weights, weight_values)):
          if hasattr(w, 'name') and w.name:
            name = str(w.name)
          else:
            name = 'param_' + str(i)
          weight_names.append(name)
        data['optimizer_weights']['weight_names'] = weight_names
        data['optimizer_weights']['weight_values'] = []
        for name, val in zip(weight_names, weight_values):
          data['optimizer_weights']['weight_values'].append(val.copy())
  return data

def load_model(data):
  # instantiate model
  model_config = data['model_config']
  if model_config is None:
    raise ValueError('No model found in config file.')

  model = model_from_config(model_config)
  if hasattr(model, 'flattened_layers'):
    # Support for legacy Sequential/Merge behavior.
    flattened_layers = model.flattened_layers
  else:
    flattened_layers = model.layers

  filtered_layers = []
  for layer in flattened_layers:
    weights = layer.weights
    if weights:
      filtered_layers.append(layer)

  flattened_layers = filtered_layers

  layer_names = data['layer_names']
  filtered_layer_names = []
  for name in layer_names:
    weight_dict = data['model_weights'][name]
    weight_names = weight_dict['weight_names']
    if len(weight_names):
      filtered_layer_names.append(name)
  layer_names = filtered_layer_names
  if len(layer_names) != len(flattened_layers):
    raise ValueError('You are trying to load a weight file '
                     'containing ' + str(len(layer_names)) +
                     ' layers into a model with ' +
                     str(len(flattened_layers)) + ' layers.')

  # We batch weight value assignments in a single backend call
  # which provides a speedup in TensorFlow.
  weight_value_tuples = []
  for k, name in enumerate(layer_names):
    weight_dict = data['model_weights'][name]
    weight_names = weight_dict['weight_names']
    weight_values = weight_dict['weight_values']
    layer = flattened_layers[k]
    symbolic_weights = layer.weights
    if len(weight_values) != len(symbolic_weights):
      raise ValueError('Layer #' + str(k) +
                       ' (named "' + layer.name +
                       '" in the current model) was found to '
                       'correspond to layer ' + name +
                       ' in the save file. '
                       'However the new layer ' + layer.name +
                       ' expects ' + str(len(symbolic_weights)) +
                       ' weights, but the saved weights have ' +
                       str(len(weight_values)) +
                       ' elements.')
    if layer.__class__.__name__ == 'Convolution1D':
      # This is for backwards compatibility with
      # the old Conv1D weights format.
      w = weight_values[0]
      shape = w.shape
      if shape[:2] != (layer.filter_length, 1) or shape[3] != layer.nb_filter:
        # Legacy shape:
        # (self.nb_filter, input_dim, self.filter_length, 1)
        assert shape[0] == layer.nb_filter and shape[2:] == (layer.filter_length, 1)
        w = np.transpose(w, (2, 3, 1, 0))
        weight_values[0] = w
    weight_value_tuples += zip(symbolic_weights, weight_values)
  K.batch_set_value(weight_value_tuples)

  # instantiate optimizer
  training_config = data.get('training_config')
  if training_config is None:
    warnings.warn('No training configuration found in save file: '
                  'the model was *not* compiled. Compile it manually.')
    return model
  optimizer_config = training_config['optimizer_config']
  optimizer = optimizer_from_config(optimizer_config)

  # recover loss functions and metrics
  loss = training_config['loss']
  metrics = training_config['metrics']
  sample_weight_mode = training_config['sample_weight_mode']
  loss_weights = training_config['loss_weights']

  # compile model
  model.compile(optimizer=optimizer,
                loss=loss,
                metrics=metrics,
                loss_weights=loss_weights,
                sample_weight_mode=sample_weight_mode)

  # set optimizer weights
  if 'optimizer_weights' in data:
    # build train function (to get weight updates)
    if isinstance(model, Sequential):
      model.model._make_train_function()
    else:
      model._make_train_function()
    optimizer_weights_dict = data['optimizer_weights']
    optimizer_weight_names = optimizer_weights_dict['weight_names']
    optimizer_weight_values = optimizer_weights_dict['weight_values']
    model.optimizer.set_weights(optimizer_weight_values)
  return model