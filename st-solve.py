#!/usr/bin/env python3

import sys
from PIL import Image
from math import ceil
import numpy as np
import json

import pytesseract
import cv2

		
class GameSquare():
	"""Class to contain the letter and attributes in each square in grid
	
		Attributes:
		  letter (str):
		    Which alphabet character is here.
		  behaviour (str):
		    How does this square behave? Options: 
		      ['white', 'blue', 'grey']
	"""
	def __init__(self, letter, behaviour):
		self.letter = letter
		self.behaviour = behaviour
		

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


def find_grid(left, top, right, bottom, nrow, ncol):
	"""Figure out the boundaries of the squares in a grid.
	
	Given locations the top, bottom, left, and right limits of a 
	grid as well as the number of squares in each row and column,
	returns the boundaries of each square in the grid.

	Args:
	  left (int):
	    Left-most boundary of grid
	  top (int):
	    Upper boundary of grid
	  right (int):
	    Right-most boundary of grid
	  bottom (int):
		Lower boundary of grid
	  nrow (int):
	    Number of rows of squares
	  ncol (int):
	    Number of columns of squares

	Returns:
	  List of lists of tuples describing the boundaries of each
	  square in the grid. Each square is represented by a tuple
	  describing square's location as follows:
	    (left, top, right, bottom)
	  Each row of squares is organized into a list, and the rows are
	  organized into the uppermost list.

	  Therefore, a simple grid of 4 squares:

	  	1	2
	  	3	4
	  is represented as follows:
	    [
	     [
	      (left1,top1,right1,bottom1),
	      (left2,top2,right2,bottom2)
	     ],
	     [
	      (left3,top3,right3,bottom3),
	      (left4,top4,right4,bottom4)
	     ],
	    ]
	"""

	grid = []

	square_height = ceil((bottom-top) /nrow)
	square_width = ceil((right-left) /ncol)

	for i in range(top, bottom, square_height):
		row = []
		for j in range(left, right, square_width):
			row.append((j, i, j+square_width, i+square_height))
		grid.append(row)

	return grid


def identify_square(colour):
	"""Identify square attributes based on colour"""

	if colour == (255, 255, 255):
		return 'white'


	elif colour in [(0, 174, 239), (0, 178, 239)]:
		return 'blue'


	elif colour in [(49, 53, 49), (58, 53, 58)]:
		return 'grey'


	else:
		raise ValueError("Colour not recognised.")



def populate_grid(image, grid):
	"""Populate a grid with GameSquare instances representing the game.
	
	Works through the provided grid of square boundaries, crops the
	corresponding parts of the provided image, and extracts the letter
	and square type information from that image.

	Args:
	  image (PIL.Image instance):
		The image to be processed, read in using PIL.Image.open().
	  grid (list of lists of tuples):
		List of lists of tuples describing the boundaries of each
	    square in the grid. Each square is represented by a tuple
	    describing square's location as follows:
	      (left, top, right, bottom)
	    Each row of squares is organized into a list, and the rows are
	    organized into the uppermost list.

	Returns:
	  List of lists of GameSquare instances.
	"""

	game_grid = []

	for i in grid:
		row = []
		for square in i:
			cropped = image.crop(square)
			cols = cropped.getcolors()
			cols.sort(key=lambda x: x[0], reverse=True)

			behaviour = identify_square(cols[0][1])

			# Need to convert image pixels to numpy array for cv2
			cv_image = np.array(cropped) 
			# Convert RGB to BGR 
			cv_image = cv_image[:, :, ::-1].copy() 

			gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

			threshold_img = cv2.threshold(
				gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

			# Use --psm 10 as docs state:
			# 10 = Treat the image as a single character.
			letter = pytesseract.image_to_string(
					threshold_img, config=r'--psm 10', 
					lang='eng',
					).strip()

			# This is rubbish at spotting Qs so if it's blue and called
			# C then it is really a Q as the game doesn't spawn blue Cs
			if behaviour == 'blue' and letter == 'C':
				letter = 'Q'

			row.append(GameSquare(letter=letter, behaviour=behaviour))

		game_grid.append(row)

	return game_grid


def main():

	with open('indexed_dict.json') as fin:
		indexed_dict = json.load(fin)

	with open('letter_scores.json') as fin:
		letter_scores = json.load(fin)

	image = Image.open(sys.argv[1])

	top, bottom = find_top_bottom(image)

	grid = find_grid(
		left=0,
		top=top-2,
		right=image.width,
		bottom=bottom,
		nrow=12,
		ncol=8)

	game_grid = populate_grid(image, grid)

	print(game_grid)


if __name__ == '__main__':
	main()
