#!/usr/bin/env python

import rospy
from visualization_msgs.msg import Marker
from std_msgs.msg import Header, ColorRGBA
from geometry_msgs.msg import Twist, Vector3, Point, Quaternion
import cv2
from ImageManipulation import ImageManipulation

from RidgeRegression import RidgeModel

import numpy as np


class Predictor(object):

  def __init__(self):
    rospy.init_node('CV')
    self.ImManipulator = ImageManipulation()
    ridge = RidgeModel()
    self.ridge = ridge.ridge #the model
    self.previous12values =  ([0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]) #values to average

    #initialize publisher and twist for neato
    self.twistPub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    self.markerPub = rospy.Publisher('/yaw_pitch', Marker, queue_size=10)
    self.twist = Twist()
    self.marker = self.createMarker()
    self.r = rospy.Rate(10)

  def avgList(self, listInput):
    """ helper function that finds average of a list
        inputs: listInput - list of integers or floats
        outputs: average of all items in list"""

    return sum(listInput)/len(listInput)

  def sendToNeato(self, currentYaw, currentPitch):
    """ sends yaw and pitch to Neato 
        inputs: currentYaw - average of previous 12 yaw readings
                currentPitch - average of previous 12 pitch readings"""

    self.twist.angular.z = (currentYaw-400) * -0.005
    # Multiply by -1 to invert direction. Multiply by .001 to make much smaller. Add .8 to adjust range from -.8 -> 0  to 0->.8
    self.twist.linear.x = ((currentPitch) * -.001) + .8
    
    self.marker.pose.position = Point(x=currentYaw, y=currentPitch, z=0)
    self.twistPub.publish(self.twist)
    self.markerPub.publish(self.marker)
    self.r.sleep()

  def updateAverage(self, currentYaw, currentPitch):
    """ updates the calculation of the moving average of Yaw and pitch
        inputs - currentYaw - most recent yaw reading
                 currentPitch - most recent pitch reading"""

    del self.previous12values[0][0]
    del self.previous12values[1][0]  
    self.previous12values[0].append(currentYaw)
    self.previous12values[1].append(currentPitch)
    newYaw = self.avgList(self.previous12values[0])
    newPitch = self.avgList(self.previous12values[1])
    return newYaw, newPitch

  def createMarker(self):
    marker = Marker()
    marker.header = Header(stamp=rospy.Time.now(), frame_id="odom")
    marker.id = 1
    marker.type = Marker.SPHERE
    marker.action = Marker.ADD
    marker.pose.orientation = Quaternion(x=0, y=0, z=0, w=1)
    marker.scale = Vector3(x=.1, y=.1, z=.1)
    marker.color = ColorRGBA(a=1, r=0, g=1, b=0)
    return marker

  def run(self):
    """
    gets face data, runs it through the model, and publishes to the robot
    returns: running boolean
    """
    im = self.ImManipulator.detectFaces() 
    if self.ImManipulator.faces != (): #if faces are detected
      im = self.ImManipulator.cropImage(im)
      im = self.ImManipulator.reshapeImage(im)
      yaw, pitch = self.ridge.predict(im) #predict yaw and pitch
      newYaw, newPitch = self.updateAverage(yaw, pitch) #get averages
      self.sendToNeato(newYaw, newPitch) #move robot
    else:
      # if no face detected, stop moving
      self.twist.angular.z = 0
      self.twist.linear.x = 0
      self.twistPub.publish(self.twist)


    if cv2.waitKey(1) & 0xFF == ord('q'): #exit on q
      cv2.waitKey(1)
      return False
    return True


p = Predictor()
while p.run():
  pass