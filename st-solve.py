#!/usr/bin/env python3

import sys
from PIL import Image
import pytesseract
import cv2
from math import ceil

def find_top_bottom(image):
	"""Find the top and bottom of the grid of letters
	
		Scans from the top of the image until it finds the first white
		or blue pixel after the band of colour at the top of the grid.

		Repeat from the bottom. Search until first white or blue pixel
		with no band to worry about.

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


def find_grid(top, bottom, left, right, nrow, ncol):
	"""Figure out the boundaries of the squares in a grid.
	
		Given locations the top, bottom, left, and right limits of a 
		grid as well as the number of squares in each row and column,
		returns the boundaries of each square in the grid.
	
		Args:
		  top (int):
		    Upper boundary of grid
		  bottom (int):
			Lower boundary of grid
		  left (int):
		    Left-most boundary of grid
		  right (int):
		    Right-most boundary of grid
		  nrow (int):
		    Number of rows of squares
		  ncol (int):
		    Number of columns of squares
	
		Returns:
		  List of lists of tuples describing the boundaries of each
		  square in the grid. Each square is represented by a tuple
		  describing square's location as follows:
		    (top, bottom, left, right)
		  Each row of squares is organized into a list, and the rows are
		  organized into the uppermost list.

		  Therefore, a simple grid of 4 squares:

		  	1	2
		  	3	4
		  is represented as follows:
		    [
		     [
		      (top1,bottom1,left1,right1),
		      (top2,bottom2,left2,right2)
		     ],
		     [
		      (top3,bottom3,left3,right3),
		      (top4,bottom4,left4,right4)
		     ],
		    ]
	"""

	grid = []

	square_height = ceil((bottom-top) /nrow)
	square_width = ceil((right-left) /ncol)

	# Make sure the range includes the bottom and top values.
	col_end = bottom if (bottom-top) %nrow ==0 else bottom+square_height
	row_end = right if (right-left) %ncol ==0 else right+square_width

	for i in range(top, col_end, square_height):
		row = []
		for j in range(left, row_end, square_width):
			row.append((i, i+square_height, j, j+square_width))
		grid.append(row)

	return grid


infile = sys.argv[1]

image = Image.open(infile)

top, bottom = find_top_bottom(image)

grid = find_grid(top, bottom, 0, image.width, 12, 8)
