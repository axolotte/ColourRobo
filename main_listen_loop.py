""" Cannot be tested on simulated robot

    Repeats color when heard.
"""

import sys
import time
import almath
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
from math import pi, sin, atan2
from vision.vision_showimages import ImageWidget
from PyQt4.QtGui import QApplication
from optparse import OptionParser
from vision.color_recognition import ColorDetectionModule

NAO_IP = "nao2.local"
PORT = 9559
CameraID = 1

# Global variable to store the ColourOrder module instance
ColourOrder = None
memory = None
ColorDetection = None
colorBlob = None


class ColourOrderModule(ALModule):
    """ A simple module able to react
    to speech events

    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")
        self.blobProxy = ALProxy("ALColorBlobDetection")
        self.motionProxy  = ALProxy("ALMotion")
        self.postureProxy = ALProxy("ALRobotPosture")
        self.postureProxy.goToPosture("Stand", 0.5)
        self.moovementProxy = ALProxy("ALAutonomousMoves")
        self.moovementProxy.setExpressiveListeningEnabled(False) #hoer auf rumzuzappeln
        self.distance = 1365#mm x-distance between camera and blob = b

        global memory
        memory = ALProxy("ALMemory")

        speech = ALProxy("ALSpeechRecognition")

        #module for detecting color through vision
        #global ColorDetection
        #ColorDetection = ColorDetectionModule("ColorDetection")

        # List of colours which can be recognized
        speech.pause(True)
        speech.setVocabulary(["red", "blue", "black", "green"], False)
        speech.pause(False)

        # Subscribe to the WordRecognized event:
        memory.subscribeToEvent("WordRecognized",
            "ColourOrder",
           "onColorHeard")
        #for video stream
        '''
        app = QApplication(sys.argv)
        myWidget = ImageWidget(NAO_IP, PORT, CameraID)
        myWidget.show()
        '''


    def onColorHeard(self, *_args):
        """ This will be called each time a colour order (spoken) is
        detected.

        """
        #read recognized word from memory
        words = memory.getData("WordRecognized")

        # Unsubscribe to the event when reacting,
        # to avoid repetitions
        memory.unsubscribeToEvent("WordRecognized",
            "ColourOrder")

        color = words[0]
        str = "I'll look for a %s blob!"%color
        #self.tts.say(str)
        print str
        #time.sleep(30)
        if color == "red":
            red = 255
            green = 0
            blue = 0
        elif color == "blue":
            red = 100
            green = 50
            blue = 255
        elif color == "green":
            red = 0
            green = 255
            blue = 0
        elif color == "black":
            red = 255
            green = 255
            blue = 255
        else:
            self.tts.say("Weird! I should no be able to see this color!")

        #Call ColorDetection from vision module, so colour can be recgonized
        #subscribes to BlopDetection event

        self.subscribeToBlopDetection(red, green, blue)
        time.sleep(2)

    def subscribeToBlopDetection(self, red, green, blue):
        """subscribe to blop event"""

        self.blobProxy.setColor(red, green, blue, 50)
        #self.blobProxy.setObjectProperties(10, 5) TODO testen ob das der abstand ist
        self.blobProxy.setObjectProperties(10, self.distance/1000)



        memory.subscribeToEvent("ALTracker/ColorBlobDetected",
                                "ColourOrder",
                                "onColorDetected")


        print("subscribe to Blop")

    def onColorDetected(self, *_args):
        """ This will be called each time a color is
        detected.

        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions

        memory.unsubscribeToEvent("ALTracker/ColorBlobDetected",
                                  "ColourOrder")

        circle_coordinates = self.blobProxy.getCircle()
        if not circle_coordinates:
            print "Circle to small"
            # Subscribe again to the event
            memory.subscribeToEvent("ALTracker/ColorBlobDetected",
                                      "ColourOrder", "onColorDetected")
        else:
            print "circle_coordinates = %s"%circle_coordinates
            str = "I can see one over there!"
            #self.tts.say(str)
            print str
            self.point_at_circle(circle_coordinates[0])
            time.sleep(2)

            # Subscribe again to the event
            memory.subscribeToEvent("WordRecognized",
                "ColourOrder",
                "onColorHeard")


    def point_at_circle(self, x_value_pic):


        # Wake up robot-----------------------------------------------------
        self.motionProxy.wakeUp()

        # Calculate angle of arm in order to point at blob------------------
        # set fixet roboter values
        camera_horizontal_angle = 60.97*almath.TO_RAD #=alhpa
        dy_shoulder = 98#mm #98mm wenn genau mitte bei keiner kopfdrehung
        if dy_shoulder < 32:
            print "WARNING! blob is too close for pointing!"

        print"y value of blob in percent from left pic side is %s"%x_value_pic

        # use sin(alpha)/a = sin(beta)/b to get horizon_length

        print"distance of blob is %s"%self.distance

        horizon_length = 2*self.distance*sin(camera_horizontal_angle/2)/sin(90-camera_horizontal_angle/2) #=a, betha=180-90-60.97/2
        #horizon_length = 600

        print"Horizon length is %s"%horizon_length

        x_length = x_value_pic * horizon_length
        print"y length of blob in percent from left pic side is %s"%x_length

        distance_to_center = abs(x_length - (horizon_length/2))
        print"y distance of blob to robot center is %s"%distance_to_center

        if x_value_pic > 0.5:#user right arm
            target = "RArm"
            ellbow_roll = -pi/2

            distance_to_shoulder = dy_shoulder-distance_to_center #TODO checken was passiert wenn negativ? (weiter rechts als re. schulter)
            angle_for_pointing = atan2(distance_to_shoulder, self.distance)
            handName = "RHand"

        else:
            target = "LArm"
            distance_to_shoulder = distance_to_center-dy_shoulder
            ellbow_roll = pi/2
            angle_for_pointing = atan2(distance_to_shoulder, self.distance)
            handName = "LHand"

        print"y distance of blob to robots right shoulder is %s"%distance_to_shoulder

        targetAngles  = [0, angle_for_pointing,ellbow_roll,0,0,90]

        print "angle = %s"%(angle_for_pointing*almath.TO_DEG)

        #moove arm --------------------------------------------------------
        maxSpeedFraction = 0.2
        self.motionProxy.angleInterpolationWithSpeed(target, targetAngles, maxSpeedFraction)
        self.motionProxy.openHand(handName);

        time.sleep(5)

        targetAngles = [pi/2,0,0,0,0,0]
        self.motionProxy.angleInterpolationWithSpeed(target, targetAngles, maxSpeedFraction)

    def exit_program(self):
        self.motionProxy.rest()

def main():
    """ Main entry point

    """
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
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port


    # Warning: ColourOrder must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global ColourOrder
    ColourOrder = ColourOrderModule("ColourOrder")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        ColourOrder.exit_program()
        myBroker.shutdown()
        sys.exit(0)
    #TODO
    #Fotos machen
    '''
    [E] 6107 qitype.dynamicobject: 	ALPythonModule::execute
	calling ColourOrder.onColorDetected
    <type 'exceptions.TypeError'>
    'NoneType' object has no attribute '__getitem__'

    '''



if __name__ == "__main__":
    main()
