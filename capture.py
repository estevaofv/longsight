#!/usr/bin/env python
"""Simple Python script to capture images from a webcam.

Uses the OpenCV libray via its cv2 interface, see:
http://opencv.willowgarage.com/wiki/

Tested under Mac OS X 10.7 "Lion", but should work under
Linux and Windows as well.
"""
import sys
import time
import itertools
from optparse import OptionParser
try:
    import cv #TODO - Where do the property constants live in cv2?
    import cv2
except ImportError:
    sys.stderr.write("Please install OpenCV and the cv and cv2 Python interfaces\n")
    sys.exit(1)

parser = OptionParser(add_help_option=False, usage="""Capture series for webcam frames.

Example usage to capture 10 frames at 1280x960 and name them 'New Moon XXX.png', use:
-n 10 -w 1280 -h 960 -m "New Moon "
""")
parser.add_option("-?", "--help",
                  action="help",
                  help="Show help")
parser.add_option("-m", "--name",
                  help="Filename prefix")
parser.add_option("-n", "--number", type="int",
                  help="Number of frames (default is infinite)")
parser.add_option("-h", "--height", type="int",
                  help="Resolution height in pixels")
parser.add_option("-w", "--width", type="int",
                  help="Resolution width in pixels")
parser.add_option("-d", "--device", type="int", default=0,
                  help="Which camera device?")
parser.add_option("-v", "--verbose", action="store_true",
                  help="Verbose output (debug)")
(options, args) = parser.parse_args()

def get_resolution(video_capture):
    return video_capture.get(cv.CV_CAP_PROP_FRAME_WIDTH), \
           video_capture.get(cv.CV_CAP_PROP_FRAME_HEIGHT)

def set_resolution(video_capture, width, height):
    video_capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, width)
    video_capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, height)
    w, h = get_resolution(video_capture)
    assert (width, height) == (w, h), \
        "Failed to set resolution to %i x %i, got %i x %i" \
        % (width, height, w, h)
    return width, height

def debug(video_capture):
    for prop, name in [
        (cv.CV_CAP_PROP_MODE, "Mode"),
        (cv.CV_CAP_PROP_BRIGHTNESS, "Brightness"),
        (cv.CV_CAP_PROP_CONTRAST, "Contrast"),
        (cv.CV_CAP_PROP_SATURATION, "Saturation"),
        (cv.CV_CAP_PROP_HUE, "Hue"),
        (cv.CV_CAP_PROP_GAIN, "Gain"),
        (cv.CV_CAP_PROP_EXPOSURE, "Exposure"),
        ]:
        value = video_capture.get(prop)
        if value == 0:
            print " - %s not available" % name
        else:
            print " - %s = %r" % (name, value)

#TODO - Date stamp to avoid over-writting
#template = "%04i%02i%02i-%02i:%02i:%02.2f"
template = "%05i"
if options.name:
    template = options.name.replace("%","%%") + template
template += ".png"

vidcap = cv2.VideoCapture()
assert vidcap.open(options.device)
if options.verbose:
    debug(vidcap)

if options.width and options.height:
    set_resolution(vidcap, options.width, options.height)
elif options.width or options.height:
    sys.stderr("Must supply height AND width (or neither)\n")
    sys.exit(1)
w, h = get_resolution(vidcap)

if options.number:
    frames = xrange(options.number)
else:
    frames = itertools.count()
if options.verbose:
    print "Starting..."
start = time.time()
for f in frames:
    retval, image = vidcap.read()
    filename = template % f
    assert retval, retval
    assert image is not None, image
    assert w, h == image.size
    assert cv2.imwrite(filename, image)
    if options.verbose:
        print "%s - frame %i" % (filename, f)
print "Approx %0.1ffps" % (float(f) / (time.time()-start))
if options.verbose:
    print "Done"
    debug(vidcap)
vidcap.release()
sys.exit(0)
