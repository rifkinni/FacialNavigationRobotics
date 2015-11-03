import numpy as np
from sklearn import linear_model
from DataCollection import DirManager
import cv2


class RidgeModel(DirManager):
  """
  aggregates the training data and fits a model to it
  """
  def __init__(self, alpha=.1):
    self.X_train, self.Y_train = self.getTrainingData()
    self.ridge = linear_model.Ridge(alpha=alpha) #make the model
    self.ridge.fit(self.X_train, self.Y_train) #fit the model

  def getTrainingData(self):
    """Collect data from compressed images and convert to X_training and Y_training
    returns: X_train - training set for x values
             Y_train - training set of y values """
    X_train = []
    Y_train = []
    for (_file, x, y) in self.getDirFiles():
      im = cv2.imread(_file, 0)
      if im.shape == (24, 24):
        reshaped = np.reshape(im, 576)
        X_train.append(reshaped)
        Y_train.append((x,y))

    return (X_train, Y_train) #training data