# -*- encoding: UTF-8 -*-

'''Cartesian control: With this Nao can point on given coordinates'''

from optparse import OptionParser
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import motion
import almath
import time
from math import pi, sin
import sys
#TODO Linker Arm nicht zurückfahren, nicht gegen bein schlagen (v regulieren), Hand drehen, Koordinaten berechen,
NAO_IP = "nao2.local"
#AO_IP = "localhost"

class Moovement():
    def __init__(self):
        ''' Example showing a path of two positions
        Warning: Needs a PoseInit before executing
        '''
        self.colorAngle = 0
        self.motionProxy  = ALProxy("ALMotion")
        self.postureProxy = ALProxy("ALRobotPosture")
        self.moovementProxy = ALProxy("ALAutonomousMoves") #hoer auf rumzuzappeln

        self.moovementProxy.setExpressiveListeningEnabled(False)

        # Wake up robot--------------------------------------------------------
        self.motionProxy.wakeUp()

        # Send robot to Stand Init---------------------------------------------
        self.postureProxy.goToPosture("StandInit", 0.5)


        # Point with right arm at given color-blob ----------------------------
        self.colorAngle = 0 #<30
        maxSpeedFraction = 0.2 # Using 20% of maximum joint speed
        #if self.colorAngle < 90:
        names  = "RArm"
        targetAngles     = [0, self.colorAngle*almath.TO_RAD, -pi/2,0,0,0]
        #else:
        #targetAngles     = [0, 0,0,0,0,0]
        self.motionProxy.angleInterpolationWithSpeed(names, targetAngles, maxSpeedFraction)
        time.sleep(3)
        self.motionProxy.rest()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    naoBroker = ALBroker("naoBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port

    # Warning: pose must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global traverse
    traverse = Moovement()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        naoBroker.shutdown()
        sys.exit(0)
