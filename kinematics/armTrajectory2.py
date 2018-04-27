# -*- encoding: UTF-8 -*-

'''Cartesian control: Arm trajectory example'''
''' This example is only compatible with NAO '''
import motion
import almath
import time
from math import pi
import sys
from naoqi import ALProxy
from optparse import OptionParser
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

NAO_IP = "nao2.local"

class Moovement():
    def __init__(self):
        ''' Example showing a path of two positions
        Warning: Needs a PoseInit before executing
        '''

        motionProxy  = ALProxy("ALMotion")
        postureProxy = ALProxy("ALRobotPosture")

        # Wake up robot
        motionProxy.wakeUp()

        # Send robot to Stand Init
        postureProxy.goToPosture("StandZero", 0.5)
        time.sleep(2)

        effector   = "RArm"
        frame      = motion.FRAME_TORSO
        axisMask   = almath.AXIS_MASK_VEL # just control position
        useSensorValues = False
        x = 0.3
        y = 0.03
        z = 0
        path = []
        currentTf = motionProxy.getTransform(effector, frame, useSensorValues)
        targetTf  = almath.Transform(currentTf)
        targetTf.r1_c4 += 0.3#0.03 # x
        targetTf.r2_c4 += 0.03#0.03 # y
        #targetTf.r3.c4 += 0.023 # z
        #289.9533996582031, -29.3204345703125, 23.041688919067383
        path.append(list(targetTf.toVector()))
        path.append(currentTf)

        # Go to the target and back again
        times      = [2.0, 4.0] # seconds

        #motionProxy.transformInterpolations(effector, frame, path, axisMask, times)

        # Go to rest position
        motionProxy.rest()

    def scale_down(x, y, z):
        arm_lenght = 209.7
        scalefactor = sqrt(x**2+y**2+z**2)/arm_lenght
        arm_x = x/scalefactor
        arm_y = y/scalefactor
        arm_z = z/scalefactor
        return arm_x, arm_y, arm_z

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
