import cv2
import numpy as np

class ImageManipulation(object):
  
  def __init__(self):
    self.camera = Camera()

  def compressImage(self, im):
    """compresses Images to 24 by 24 pixel images
    input: im - image intakeData
    returns: compressed image """

    squareSize = im.shape[0]/24 # number of pixels on 1 side of the square that will become an averaged pixel
    posY = 0
    newIm = np.ndarray((24, 24, 3)) # creating array for compressed image
    while posY < im.shape[1]:
      posX = 0
      while posX < im.shape[0]:   # go across
        a = im[posX: posX + squareSize, posY: posY + squareSize] #crop image to one square
        #sum the BGR values across the square
        sumB, sumG, sumR = [0, 0, 0]
        for i in range(squareSize):
          for j in range(squareSize):
            try:
              sumB += a[i][j][0]
              sumG += a[i][j][1]
              sumR += a[i][j][2]
            except IndexError: #we were getting sporadic errors here
              print squareSize
              print im.shape
              
        sumB = sumB/(squareSize)**2 #get the average BGR values
        sumG = sumG/(squareSize)**2
        sumR = sumR/(squareSize)**2

        #update one pixel in the compressed image array
        try:
         newIm[posX/squareSize][posY/squareSize] = [sumB, sumG, sumR]
        except IndexError: #and also here
          print squareSize
          print posX
          print posX/squareSize
          print posY/squareSize
        #increment to the next square for compression
        posX += squareSize
      posY += squareSize
    return newIm


  def getCameraImage(self, name):
    """takes in image from camera, identifies face in the image and saves the image
    inputs: name - filename
    """

    retval, im = self.camera.cam.read() #take webcam photo
    self.faces = self.camera.face_cascade.detectMultiScale(im, scaleFactor=1.2, minSize=(20,20)) #detect faces
    if self.faces!= (): #if faces are found
      im = self.cropImage(im) #crop to face

      #save images
      _file = "images/" + name + ".png"
      cv2.imwrite(_file, im)
  
  def detectFaces(self):
    """ captures image and displays rectangle around detected faces
        returns: frame: camera image 
    """
    ret, frame = self.camera.cam.read()
    self.faces = self.camera.face_cascade.detectMultiScale(frame, scaleFactor=1.2, minSize=(20,20))
    for (x,y,w,h) in self.faces:
      cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255))
    cv2.imshow('frame',frame)
    cv2.waitKey(1)
    return frame

  def reshapeImage(self, im):
    """ gray-scales and reshapes an image to a 576x1 array
        inputs: im - image to be manipulated
        returns: reshaped image
    """

    compressed = self.compressImage(im)
    compressed = np.asarray(compressed, dtype=np.uint8)
    gray = cv2.cvtColor(compressed, cv2.COLOR_BGR2GRAY )
    reshaped = np.reshape(gray, 576)
    return reshaped

  def cropImage(self, im):
    """ crops image to be a square that includes only the face
        input:  im - the full image to crop
        returns: cropped image """

    #choose largest detected face
    maxIndex, maxSize = [0, 0];
    for i, f in enumerate(self.faces):
      size = (f[2])*(f[3])
      if size > maxSize:
        maxIndex = i
        maxSize = size
    
    faceData = self.faces[maxIndex]
    (x,y,w,h) = faceData

    #crop such that image is a square and dimension is multiple of 24
    squareSize = max([w, h])
    if squareSize%24 >0:
      try:
        im = im[y:y + squareSize + 24 - squareSize%24, x:x + squareSize + 24 - squareSize%24]
      except IndexError:
        im = im[y:y + squareSize - squareSize%24, x:x + squareSize - squareSize%24]
    else:
      im = im[y:y + squareSize, x:x + squareSize]
    return im


class Camera(object):
  """
  takes photo and video
  """
  def __init__(self):
    self.cam = self.initializeCamera()
    self.face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt.xml')
  
  def initializeCamera(self):
    """ helper function to initialize camera
    returns: camera object"""

    camera_port = 0
    camera = cv2.VideoCapture(camera_port) 

    #gets rid of first 10 seconds so that camera focuses
    for i in xrange(10):
      retval, im = camera.read()

    return camera

  def showVideoOnStartUp(self):
    """
    show camera video and mark faces before starting data collection
    """
    while True: #show video and mark detected faces
      ret, frame = self.cam.read()
      faces = self.face_cascade.detectMultiScale(frame, scaleFactor=1.2, minSize=(20,20))
      for (x,y,w,h) in faces:
        #draws rectangle on face
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255))
      cv2.imshow('frame',frame)
      #press q to exit
      if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.waitKey(1)
        cv2.destroyWindow('frame')
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        return
    time.sleep(1)