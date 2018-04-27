# -*- encoding: UTF-8 -*-
# Get an image from NAO. Display it and save it using PIL.

import sys
import time
import vision_definitions
import almath
# Python Image Library
from PIL import Image
from math import pi, atan2, sin
from naoqi import ALProxy


def showNaoImage(IP, PORT):
  """
  First get an image from Nao, then show it on the screen with PIL.
  """
  camProxy = ALProxy("ALVideoDevice", IP, PORT)
  resolution = 2    # VGA
  colorSpace = 11   # RGB

  videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)
  camProxy.setParam(vision_definitions.kCameraSelectID, 1) #1=Kinn, 0=Stirn
  t0 = time.time()

   # Get a camera image.
  # image[6] contains the image data passed as an array of ASCII chars.
  naoImage = camProxy.getImageRemote(videoClient)

  t1 = time.time()

  # Time the image transfer.
  print("acquisition delay ", t1 - t0)

  camProxy.unsubscribe(videoClient)


  # Now we work with the image returned and save it as a PNG  using ImageDraw
  # package.

  # Get the image size and pixel array.
  imageWidth = naoImage[0]
  imageHeight = naoImage[1]
  array = naoImage[6]

  # Create a PIL Image from our pixel array.
  im = Image.frombytes("RGB", (imageWidth, imageHeight), array)

  # Save the image.
  im.save("camImage.png", "PNG")

  im.show()

def get_in_position():
    colorAngle = 0
    motionProxy  = ALProxy("ALMotion", IP, PORT)
    postureProxy = ALProxy("ALRobotPosture", IP, PORT)
    moovementProxy = ALProxy("ALAutonomousMoves", IP, PORT) #hoer auf rumzuzappeln
    moovementProxy.setExpressiveListeningEnabled(False)

    # Wake up robot--------------------------------------------------------
    motionProxy.wakeUp()

    # Send robot to Stand Init---------------------------------------------
    #postureProxy.goToPosture("StandInit", 0.5)


    # Point with right arm at given color-blob ----------------------------
    #colorAngle = 0 #<30
    maxSpeedFraction = 0.2 # Using 20% of maximum joint speed
    #if colorAngle < 90:
    #names  = "RArm"
    #targetAngles     = [0, colorAngle*almath.TO_RAD, -pi/2,0,0,0]

    #else:
    #targetAngles     = [0, 0,0,0,0,0]
    #motionProxy.angleInterpolationWithSpeed(names, targetAngles, maxSpeedFraction)

    #Point###########
    camera_horizontal_angle = 60.97*almath.TO_RAD #=alhpa
    distance = 240#mm x-distance between camera and blob = b
    #sin(alpha)/a = sin(beta)/b
    print"distance of blob is %s"%distance
    horizon_length = 2*distance*sin(camera_horizontal_angle)/sin(90-camera_horizontal_angle)
    print"horizon length of is %s"%horizon_length

    x_value_pic = 0.0 #TODO use parameter then
    print"y value of blob in percent from left pic side is %s"%x_value_pic

    x_length = x_value_pic * horizon_length
    print"y length of blob in percent from left pic side is %s"%x_length

    distance_to_center = abs(x_length - (horizon_length/2))
    print"y distance of blob to robot center is %s"%distance_to_center

    dy_shoulder = 98#mm #98mm wenn genau mitte bei keiner kopfdrehung
    if x_value_pic > 0.5:
        distance_to_shoulder = dy_shoulder-distance_to_center #TODO checken was passiert wenn negativ? (weiter rechts als re. schulter)
        target = "RArm"
        wrist_angle = -pi/2
        angle_for_pointing = atan2(distance, distance_to_shoulder)

    else:
        distance_to_shoulder = dy_shoulder-distance_to_center
        target = "LArm"
        wrist_angle = pi/2
        angle_for_pointing = -atan2(distance, distance_to_shoulder)
    print"y distance of blob to robots right shoulder is %s"%distance_to_shoulder

    targetAngles     = [0, angle_for_pointing,wrist_angle,0,0,0]
    print "angle = %s"%(angle_for_pointing*almath.TO_DEG)
    names  = "RShoulderRoll"
    motionProxy.angleInterpolationWithSpeed(target, targetAngles, maxSpeedFraction)
    #################

    return motionProxy

if __name__ == '__main__':
  IP = "nao2.local"  # Replace here with your NaoQi's IP address.
  PORT = 9559

  # Read IP address from first argument if any.
  if len(sys.argv) > 1:
    IP = sys.argv[1]
  motionProxy = get_in_position()
  #naoImage = showNaoImage(IP, PORT)
  time.sleep(5)
  motionProxy.rest()
