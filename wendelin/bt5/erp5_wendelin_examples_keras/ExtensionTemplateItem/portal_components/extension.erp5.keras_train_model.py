import numpy as np
import time
import transaction

class Progbar(object):

  def output(self, data):
    self.output1(str(data))

  def __init__(self, target, width=30, verbose=1, interval=0.01, output=None):
    """Dislays a progress bar.

    # Arguments:
        target: Total number of steps expected.
        interval: Minimum visual progress update interval (in seconds).
    """
    self.width = width
    self.target = target
    self.sum_values = {}
    self.unique_values = []
    self.start = time.time()
    self.last_update = 0
    self.interval = interval
    self.total_width = 0
    self.seen_so_far = 0
    self.verbose = verbose
    self.output1 = output

  def update(self, current, values=None, force=False):
    """Updates the progress bar.

    # Arguments
        current: Index of current step.
        values: List of tuples (name, value_for_last_step).
            The progress bar will display averages for these values.
        force: Whether to force visual progress update.
    """

    if values in None:
      values = []

    for k, v in values:
      if k not in self.sum_values:
        self.sum_values[k] = [v * (current - self.seen_so_far),
                                  current - self.seen_so_far]
        self.unique_values.append(k)
      else:
        self.sum_values[k][0] += v * (current - self.seen_so_far)
        self.sum_values[k][1] += (current - self.seen_so_far)
    self.seen_so_far = current

    now = time.time()
    if self.verbose == 1:
      if not force and (now - self.last_update) < self.interval:
        return

      prev_total_width = self.total_width
      #self.output('\b' * prev_total_width)
      self.output('\r')

      numdigits = int(np.floor(np.log10(self.target))) + 1
      barstr = '%%%dd/%%%dd [' % (numdigits, numdigits)
      bar = barstr % (current, self.target)
      prog = float(current) / self.target
      prog_width = int(self.width * prog)
      if prog_width > 0:
        bar += ('=' * (prog_width - 1))
        if current < self.target:
          bar += '>'
        else:
          bar += '='
        bar += ('.' * (self.width - prog_width))
        bar += ']'
        self.output(bar)
        self.total_width = len(bar)

        if current:
          time_per_unit = (now - self.start) / current
        else:
          time_per_unit = 0
        eta = time_per_unit * (self.target - current)
        info = ''
        if current < self.target:
          info += ' - ETA: %ds' % eta
        else:
          info += ' - %ds' % (now - self.start)
        for k in self.unique_values:
          info += ' - %s:' % k
          if isinstance(self.sum_values[k], list):
            avg = self.sum_values[k][0] / max(1, self.sum_values[k][1])
            if abs(avg) > 1e-3:
              info += ' %.4f' % avg
            else:
              info += ' %.4e' % avg
          else:
            info += ' %s' % self.sum_values[k]

        self.total_width += len(info)
        if prev_total_width > self.total_width:
          info += ((prev_total_width - self.total_width) * ' ')

        self.output(info)

        if current >= self.target:
          self.output('\r\n')

    if self.verbose == 2:
      if current >= self.target:
        info = '%ds' % (now - self.start)
        for k in self.unique_values:
          info += ' - %s:' % k
          avg = self.sum_values[k][0] / max(1, self.sum_values[k][1])
          if avg > 1e-3:
            info += ' %.4f' % avg
          else:
            info += ' %.4e' % avg
          self.output(info + "\r\n")

    self.last_update = now

  def add(self, n, values=None):
    if values is None:
      values = []

    self.update(self.seen_so_far + n, values)


from keras.callbacks import ProgbarLogger as OriginalProgbarLogger # pylint:disable=import-error

class ProgbarLogger(OriginalProgbarLogger):

  def __init__(self, output, verbose=0):
    self.output = output
    self.verbose = verbose

  def on_epoch_begin(self, epoch, logs=None):
    if self.verbose:
      self.output('Epoch %d/%d\r\n' % (epoch + 1, self.nb_epoch))
      self.progbar = Progbar(target=self.params['nb_sample'],
                             verbose=1, output=self.output)
    self.seen = 0

  def on_epoch_end(self, epoch, logs=None):
    super(ProgbarLogger, self).on_epoch_end(epoch, logs)
    if epoch % 10 == 0:
      transaction.commit()


seed = 7
np.random.seed(seed)

from cStringIO import StringIO
import cPickle
def save(portal, value):
  data_stream = portal.data_stream_module.wendelin_examples_keras_nn
  data_stream.edit(file=StringIO(cPickle.dumps(value)))

def load(portal):
  data_stream = portal.data_stream_module.wendelin_examples_keras_nn
  data = data_stream.getData()
  if data:
    return cPickle.loads(data)
  else:
    return None

def train(portal):
  # This is just a demo of keras.
  # 1. you can use keras.
  # 2. you can save trained model.
  # 3. you can load trained model.
  # from cStringIO import StringIO
  import tensorflow as tf # pylint:disable=import-error
  sess = tf.Session()
  from keras import backend as K # pylint:disable=import-error
  K.set_session(sess)

  stream = portal.data_stream_module.wendelin_examples_keras_log
  def output(value):
    stream.appendData(value)

  saved_model_data = load(portal)
  if saved_model_data is not None:
    model = portal.keras_load_model(saved_model_data)
  else:
    from keras.models import Sequential # pylint:disable=import-error
    from keras.layers import Dense # pylint:disable=import-error
    model = Sequential()
    model.add(Dense(12, input_dim=8, init='uniform', activation='relu'))
    model.add(Dense(8, init='uniform', activation='relu'))
    model.add(Dense(1, init='uniform', activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

  dataset = np.loadtxt(StringIO(str(portal.portal_skins.erp5_wendelin_examples_keras['pima.csv'])), delimiter=',')
  X = dataset[:, 0:8]
  Y = dataset[:, 8]

  model.fit(X, Y, nb_epoch=20, batch_size=10, callbacks=[ProgbarLogger(output)])
  scores = model.evaluate(X, Y)
  output('%s: %.2f%%' % (model.metrics_names[1], scores[1]*100))
  model_dict = portal.keras_save_model(model)
  K.clear_session()
  save(portal, model_dict)
  return model_dict
