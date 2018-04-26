# -*- encoding: UTF-8 -*-
import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

NAO_IP = "nao2.local"
#NAO_IP = "localhost"


# Global variable to store the HumanGreeter module instance
colorBlob = None
memory = None


class ColorDetection(ALModule):
    """ A simple module able to react
    to colordetection events

    """
    def __init__(self, name):
        #TODO nur einmal!!
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")

        # Subscribe to the ColorRecognition event:
        global memory
        memory = ALProxy("ALMemory")
        self._blobProxy = ALProxy("ALColorBlobDetection")
        self._blobProxy.setColor(255,0,0, 50)
        self._blobProxy.setObjectProperties(10, 5, "Circle")
        self.photoCaptureProxy = ALProxy("ALPhotoCapture")
        self.photoCaptureProxy.setResolution(2)
        self.photoCaptureProxy.setPictureFormat("jpg")


        memory.subscribeToEvent("ALTracker/ColorBlobDetected",
            "colorBlob",
            "onColorDetected")

    def onColorDetected(self, *_args):
        """ This will be called each time a face is
        detected.

        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        self._getCircle = self._blobProxy.getCircle()
        print self._getCircle
        memory.unsubscribeToEvent("ALTracker/ColorBlobDetected",
            "colorBlob")
        self.photoCaptureProxy.takePictures(3, "/home/nao/recordings/cameras/", "image")
        #self.tts.say("I can see that color!")
        print self.photoCaptureProxy.getCameraID()
        # Subscribe again to the event
        memory.subscribeToEvent("ALTracker/ColorBlobDetected",
            "colorBlob",
            "onColorDetected")


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
    colorBroker = ALBroker("colorBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port


    # Warning: colorBlob must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global colorBlob
    colorBlob = ColorDetection("colorBlob")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        colorBroker.shutdown()
        sys.exit(0)



if __name__ == "__main__":
    main()
