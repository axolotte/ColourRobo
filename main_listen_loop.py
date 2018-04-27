""" Cannot be tested on simulated robot

    Repeats color when heard.
"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser
from vision.color_recognition import ColorDetectionModule

NAO_IP = "nao2.local"


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
        # TO DO: give port and IP to proxy??
        self.tts = ALProxy("ALTextToSpeech")
        self.blobProxy = ALProxy("ALColorBlobDetection")

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
        str = "You said %s"%color
        self.tts.say(str)

        #time.sleep(30)
        if color = "red":
            red = 255
            green = 0
            blue = 0
        else if color = "blue":
            red = 0
            green = 0
            blue = 255
        else if color = "green":
            red = 0
            green = 255
            blue = 0
        else if color = "black":
            red = 255
            green = 255
            blue = 255
        else:
            self.tts.say("Weird! I should no be able to see this color!")

        #Call ColorDetection from vision module, so colour can be recgonized
        #subscribes to BlopDetection event
        self.subscribeToBlopDetection(red, green, blue)

        # Subscribe again to the event
        memory.subscribeToEvent("WordRecognized",
            "ColourOrder",
            "onColorHeard")

    def subscribeToBlopDetection(self, red, green, blue):
        """subscribe to blop event"""

        self.blobProxy.setColor(red, gree, blue, 50)
        self.blobProxy.setObjectProperties(10, 5, "Circle")


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
        circle_coordinates = self.blobProxy.getCircle()
        print "colorseen"
        print circle_coordinates

        memory.unsubscribeToEvent("ALTracker/ColorBlobDetected",
                                  "ColourOrder")

        point_at_circle(circle_coordinates[0])

        # Subscribe again to the event
        #memory.subscribeToEvent("ALTracker/ColorBlobDetected",
        #                        "ColourOrder",
        #                        "onColorDetected")

        def point_at_circle(self, x_value_pic):
            motionProxy  = ALProxy("ALMotion")
            moovementProxy = ALProxy("ALAutonomousMoves")
            moovementProxy.setExpressiveListeningEnabled(False) #hoer auf rumzuzappeln

            # Wake up robot-----------------------------------------------------
            motionProxy.wakeUp()

            # Calculate angle of arm in order to point at blob------------------
            # set fixet roboter values
            camera_horizontal_angle = 60.97*almath.TO_RAD #=alhpa
            dy_shoulder = 98#mm #98mm wenn genau mitte bei keiner kopfdrehung

            print"y value of blob in percent from left pic side is %s"%x_value_pic

            # use sin(alpha)/a = sin(beta)/b to get horizon_length
            distance = 240#mm x-distance between camera and blob = b
            print"distance of blob is %s"%distance

            horizon_length = 2*distance*sin(camera_horizontal_angle)/sin(90-camera_horizontal_angle) #=a, betha=180-90-60.97
            print"horizon length of is %s"%horizon_length

            x_length = x_value_pic * horizon_length
            print"y length of blob in percent from left pic side is %s"%x_length

            distance_to_center = abs(x_length - (horizon_length/2))
            print"y distance of blob to robot center is %s"%distance_to_center

            if x_value_pic > 0.5:
                distance_to_shoulder = dy_shoulder-distance_to_center #TODO checken was passiert wenn negativ? (weiter rechts als re. schulter)
                target = "RArm"
                wrist_angle = -pi/2
                angle_for_pointing = atan2(distance, distance_to_shoulder)
                handName = "RHand"

            else:
                distance_to_shoulder = dy_shoulder-distance_to_center
                target = "LArm"
                wrist_angle = pi/2
                angle_for_pointing = -atan2(distance, distance_to_shoulder)
                handName = "LHand"

            print"y distance of blob to robots right shoulder is %s"%distance_to_shoulder

            targetAngles  = [0, angle_for_pointing,wrist_angle,0,0,0]
            print "angle = %s"%(angle_for_pointing*almath.TO_DEG)

            #moove arm --------------------------------------------------------
            maxSpeedFraction = 0.2
            motionProxy.angleInterpolationWithSpeed(target, targetAngles, maxSpeedFraction)
            motionProxy.openHand(handName);

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
        myBroker.shutdown()
        sys.exit(0)



if __name__ == "__main__":
    main()
