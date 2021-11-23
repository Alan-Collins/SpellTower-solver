#!/usr/bin/env python3

import sys
from PIL import Image
import pytesseract
import cv2

def find_top_bottom(image):
	"""Find the top and bottom of the grid of letters
	
	Scans from the top of the image until it finds the first white or
	blue pixel after the band of colour at the top of the playspace.

	Repeat from the bottom. Search until first white or blue pixel with
	no band to worry about.

	Args:
	  image (PIL.Image instance):
		The image to be processed, read in using PIL.Image.open().
	  
	Returns:
	  (top, bottom) (tuple of ints):
	    y location of top of first grid square an bottom of the last
	"""

	height = image.height

	# Start at first pixel and track which pixel we are checking
	y = 0 

	# Record whether we've traversed the first white band yet
	traversed_first = False

	while y < height:
		# Check the pixel at x = 10 to avoid border colour
		colour = image.getpixel((10,y))
		
		# If we haven't finished the first white band, check if colour
		# is still white. If not we've finished the first white band.
		if not traversed_first:
			if colour != (255,255,255):
				traversed_first = True
			y+=1
			continue

		# If traversed_first == True and we see white or blue,
		# we've finished.
		if colour in [(255,255,255), (0, 174, 239), (0, 178, 239)]:
			top = y
			break


		# If we get this far, we're still in the coloured band up top.
		y+=1

	# Now find the bottom. It should be after the black and grey pixels
	y = image.height-1

	while y > 0:

		colour = image.getpixel((10,y))

		if colour in [(255,255,255), (0, 174, 239), (0, 178, 239)]:
			bottom = y
			break
		y-=1

	return (top, bottom)


infile = sys.argv[1]

image = Image.open(infile)

print(find_top_bottom(image))

