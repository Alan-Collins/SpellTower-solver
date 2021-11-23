#!/usr/bin/env python3

import sys
from PIL import Image
import pytesseract
import cv2

def find_top(image):
	"""Find the top of the grid of letters
	
	Scans from the top of the image until it finds the first white pixel
	after the band of colour at the top of the playspace.

	Args:
	  image (PIL.Image instance):
		The image to be processed, read in using PIL.Image.open().
	  
	Returns:
	  y (int):
	    y location of top of first grid square
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
			return y


		# If we get this far, we're still in the coloured band up top.
		y+=1


infile = sys.argv[1]

image = Image.open(infile)

print(find_top(image))


# for x in range(390, 410):
# 	print(image.getpixel((x,340)))
