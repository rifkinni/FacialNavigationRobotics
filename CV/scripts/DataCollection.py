import os
import pygame
import time
import cv2
import numpy as np
from ImageManipulation import ImageManipulation

class DirManager(object):
  """handles image directory
  """
  def __init__(self, width=-1, frameRate=0):
    self.width = width #screen width
    self.frameRate = frameRate #pixels between photos

  def mkdirs(self):
    """ creates directories to store images in local storage if they don't already exist
    """
    try: #make an images directory
      os.mkdir('images')
    except OSError: #if it already exists
      pass

    i = 0
    while i <=self.width:
      #create folders for each yaw and pitch of the face
      try:
        os.mkdir('images/{0}_400'.format(i))
        os.mkdir('images/400_{0}'.format(i))
      except OSError:
        pass
      i += self.frameRate

  def getDirFiles(self):
    """ gets all files in the image directory and their labels
    returns: list of tuples (full file path, x coordinate, y coordinate)
    """
    files = []
    parentDir = os.getcwd() + '/images'
    for dirName in os.listdir(parentDir):
      directory = os.path.join(parentDir, dirName)
      x, y = dirName.split('_')
      for _file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, _file)):
          files.append((os.path.join(directory, _file), x, y))
    return files

class DataCollection(DirManager):
  """Move a pygame dot around a screen, take and save photos at various angles
  """
  def __init__(self):
    self.width = 800 #screen width
    self.height = 800 #screen height
    self.frameRate = 50 #pixels between photos
    self.mkdirs()
    self.ImManipulator = ImageManipulation()
    self.ImManipulator.camera.showVideoOnStartUp() 
    self.screen  = self.initializeScreen()
    self.intakeData() #collect data
    del(self.ImManipulator.camera.cam) #clean up
    self.compressAll() #compress images


  def initializeScreen(self):
    """ starts screen for ball to be monitored on
        returns : pygame screen """

    white = (255,255,255)
    black = (0,0,0)
    sleepTime = .005 
    pygame.init()
    screen = pygame.display.set_mode((self.width,self.height))
    pygame.draw.circle(screen, white, (self.width/2,self.height/2), 5)
    pygame.display.update()
    time.sleep(sleepTime)
    return screen

  def updateScreen(self, x, y):
    """updates location of ball on screen
      inputs: x, y  - position of ball
    """

    white = (255,255,255)
    black = (0,0,0)
    sleepTime = .001

    self.screen.fill(black)
    pygame.draw.circle(self.screen, white, (x,y), 5)
    pygame.display.update()
    time.sleep(sleepTime)

  def intakeData(self):
    """ run function for intaking data
    """

    self.timestamp = time.time() #arbitrary unique id
    x=self.width/2
    y=self.height/2

    # moves ball to right of screen
    while x < self.width:
      self.updateScreen(x, y)
      if x%self.frameRate == 0:
        self.ImManipulator.getCameraImage('{0}_{1}/{2}'.format(x, y, self.timestamp))
      x+=1
    
    # moves ball to left of screen
    while x >0:
      self.updateScreen(x, y)
      if x%self.frameRate == 0:
         self.ImManipulator.getCameraImage('{0}_{1}/{2}'.format(x, y, self.timestamp))
      x-=1

    #moves ball to center of screen
    while x<self.width/2:
      self.updateScreen(x, y)
      if x%self.frameRate == 0:
        self.ImManipulator.getCameraImage('{0}_{1}/{2}'.format(x, y, self.timestamp))
      x+=1

    #moves ball to top of screen
    while y < self.height:
      self.updateScreen(x, y)
      if y%self.frameRate == 0:
        self.ImManipulator.getCameraImage('{0}_{1}/{2}'.format(x, y, self.timestamp))
      y+=1

    # moves ball to bottom of screen
    while y >0:
      self.updateScreen(x, y)
      if y%self.frameRate == 0:
        self.ImManipulator.getCameraImage('{0}_{1}/{2}'.format(x, y, self.timestamp))
      y-=1

    # moves ball to center of screen
    while y<self.height/2:
      self.updateScreen(x, y)
      if y%self.frameRate == 0:
        self.ImManipulator.getCameraImage('{0}_{1}/{2}'.format(x, y, self.timestamp))
      y+=1

  
  def compressAll(self):
    """compressess all of the images saves over them in local storage
    """
    for (_file, _, _) in self.getDirFiles():
      im = cv2.imread(_file)
      if type(im) == np.ndarray:
        newIm = self.ImManipulator.compressImage(im)
        cv2.imwrite(_file, newIm)




if __name__ == '__main__':
  DataCollection()