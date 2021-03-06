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
		  loc (tuple of ints):
		    Where in the game_grid the square is found.
	"""
	def __init__(self, letter, behaviour, loc):
		self.letter = letter
		self.behaviour = behaviour
		self.loc = loc
		

class Word():
	"""Class to contain the words identified in game_grid
	
		Attributes:
		  word (str):
		    The sequence of characters identified as a word.
		  locs (list of tuples of ints):
		    list of location of each character of word in game grid.
		  bonus_sqs (list of GameSquare instances):
		    the GameSquares in the bonus locations.
		  bonus_locs (list of tuples of ints):
		    list of locations of bonus tiles that will be removed by
		    this word and will be used for scoring.
		  bonus_letters (str):
		    The letters in the bonus squares.
		  score (int):
		    Score of this word.

	"""
	def __init__(self, word, locs, bonus_sqs=[], bonus_locs=[], score=0,
		bonus_letters=''):
		self.word = word
		self.locs = locs
		self.bonus_sqs = bonus_sqs
		self.bonus_locs = bonus_locs
		self.bonus_letters = bonus_letters
		self.score = score


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

	for y, line in enumerate(grid):
		row = []
		for x, square in enumerate(line):
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

			# It classifies I as | due to the typeface in spell tower.
			if letter == '|':
				letter = 'I'

			# It classifies P as D so catch that by checking the bottom
			# of the loop in the P. That line should be lower down in D
			if letter == 'D':
				if threshold_img[90,120] == 0:
					letter = 'P'

			row.append(GameSquare(
				letter=letter, behaviour=behaviour, loc=(y,x)))
		game_grid.append(row)

	return game_grid


def calc_score(word, score_dict):
	"""Calculates score of a word based on simple rules.
	
	Calculates score for words based on what seems to be the scoring
	system used in spell tower:

	The scrabble letter score of the letters in the word + the bonus
	letters in surrounding tiles are summed and multiplied by the length
	of the word.

	Args:
	  word (Word instance):
		Word instance containing information about the word
	  score_dict (dict):
		Characters as keys, their corresponding integer score as values

	Returns:
	  Int score of the provided word
	"""

	score = 0



	for c in word.word.upper(): # Ensure upper case and go letter by letter
		score += score_dict[c]


	bonus_score = 0
	for c in word.bonus_letters.upper():
		bonus_score += score_dict[c]

	score = (score+bonus_score) * len(word.word)


	return score


def identify_words(grid, start, fragments_dict, current_word,
	current_locs, score_dict):
	"""

	Args:
	  grid (list of lists):
	    game grid
	  start (tuple):
	    x and y coordinate of the starting character of the words to
	    build
	  fragments_dict (dict):
	    Dict of all possible words and their constituent fragments.
	  current_word (str):
	    The letters that have been added to the word so far.
	  current_locs (list of tuples or ints):
	    The locations of letters added to the word so far.
	  score_dict (dict):
		Characters as keys, their corresponding integer score as values

	Yields:
	  Word instance of every word, its string and a list of its 
	  coordinates in the game grid from start to finish of the word. 
	  e.g.
	  	('apple', [(0,1), (1,1), (1,2), (2,3), (2,2)])
	"""
	y,x = start

	grid_w = len(grid[0])
	grid_h = len(grid)

	for i in range(y-1,y+2):
		if i < 0 or i >= grid_h:
			continue

		for j in range(x-1, x+2):
			if j < 0 or j >= grid_w:
				continue

			if (i,j) in current_locs:
				continue

			# If square has been removed, continue
			if not grid[i][j]:
				continue

			letter = grid[i][j].letter.lower()
			if letter == '':
				continue

			new_word = current_word+letter

			if new_word not in fragments_dict:
				continue

			if fragments_dict[new_word] == 'w':
				locs = current_locs + [(i,j)]
				finished_word = Word(new_word,locs)
				finished_word = identify_bonus(finished_word, grid)
				finished_word.score = calc_score(finished_word, score_dict)
				yield finished_word

			elif fragments_dict[new_word]== 'b':
				locs = current_locs + [(i,j)]
				for word in identify_words(grid, (i,j), fragments_dict, 
					new_word, locs, score_dict):
					word = identify_bonus(word, grid)
					word.score = calc_score(word, score_dict)
					yield word
				finished_word = Word(new_word,locs)
				finished_word = identify_bonus(finished_word, grid)
				finished_word.score = calc_score(finished_word, score_dict)
				yield finished_word
				
			else:
				locs = current_locs + [(i,j)]
				for word in identify_words(grid, (i,j), fragments_dict, 
					new_word, locs, score_dict):
					word = identify_bonus(word, grid)
					word.score = calc_score(word, score_dict)
					yield word


def print_game(game_grid, word=None):
	"""Prints the game grid to the terminal with optional word highlight

	Prints the letters of the game in a grid arrangement in the terminal.
	If a Word is specified then the letters of the word and bonus tiles
	arround the word (if applicable) are highlighted with a different
	colour.

	Args:
	  game_grid (list of lists of GameSquare instances):
		The tiles in the game in an array.
	  word (Word instance):
		A words to be highlighted
	"""

	cols = {
	'Bold': '\u001b[1m',
	'Underline': '\u001b[4m',
	'Black': '\u001b[30m',
	'Red': '\u001b[31m',
	'Green': '\u001b[32m',
	'Yellow': '\u001b[33m',
	'Blue': '\u001b[34m',
	'Magenta': '\u001b[35m',
	'Cyan': '\u001b[36m',
	'White': '\u001b[37m',
	'Reset': '\u001b[0m'
	}
	
	# If highlighting a word, extract relevant locations.
	if word:
		print('Word: {}\nScore: {}'.format(word.word, word.score))
	word_idxs = word.locs if word else []
	bonus_idxs = word.bonus_locs if word else []
	string = ''
	for line in game_grid:
		line_squares = []
		for square in line:
			if not square:
				line_squares.append('{}{}{}'.format(
					cols['Black'],
					'-',
					cols['Reset']
					))
				continue
			
			# To align columns, empty strings must be set to a space
			if square.letter == '':
				letter = ' '
			else:
				letter = square.letter
			# Colour the first and last letter differently to make clear
			if square.loc in word_idxs:
				if square.loc == word_idxs[0]:
					col = cols['Cyan']
				elif square.loc == word_idxs[-1]:
					col = cols['Yellow']
				else:
					col = cols['Green']
				line_squares.append('{}{}{}{}{}'.format(
					cols['Underline'],
					cols['Bold'],
					col,
					letter,
					cols['Reset']
					))
			elif square.loc in bonus_idxs:
				line_squares.append('{}{}{}{}{}'.format(
					cols['Underline'],
					cols['Bold'],
					cols['Magenta'],
					letter,
					cols['Reset']
					))
			else:
				line_squares.append(letter)
		string += ' '.join(line_squares) + '\n'

	print(string)


def identify_bonus(word, game_grid):
	"""Identify the letters surrounding a word that will be scored.
	
	Based on word length and the behaviour of squares in the word,
	identify letters in the game grid that will be included in scoring
	and removed from play.

	Args:
	  word (Word instance):
		A words to be highlighted
	  game_grid (list of lists of GameSquare instances):
		The tiles in the game in an array.

	Returns:
	  word (Word instance)
	  Adds bonus information to the provided word instance and returns
	  modified object
	"""
	
	blocs = [] # bonus locations

	for wloc in word.locs:
		y,x = wloc
		wsquare = game_grid[y][x]


		if wsquare.behaviour == 'blue':
			# If it's blue add the whole row
			for square in game_grid[y]:
				if not square:
					continue
				if square.loc != (y,x):
					blocs.append(square)
			# And the square above and below it
			for loc in [(y-1, x), (y+1, x)]:
				# If outside of game grid skip
				if loc[0] < 0 or loc[0] >= len(game_grid):
					continue
				# If square removed skip
				if not game_grid[loc[0]][loc[1]]:
					continue
				if loc not in word.locs:
					blocs.append(game_grid[loc[0]][loc[1]])
			continue

		# Adjacent letters are only added for 5 letter words and longer.
		if len(word.word) < 5:
			continue
		# else square must be white so check all adjacent squares
		for i in [y-1, y+1]:
			j = x
			# If outside of game grid skip
			if i < 0 or i >= len(game_grid):
				continue
			if (i,j) in word.locs: # Don't inlcude word squares
				continue
			if not game_grid[i][j]:
					continue

			blocs.append(game_grid[i][j])

		for j in [x-1, x+1]:
			i = y
			# If outside of game grid skip
			if j < 0 or j >= len(game_grid[0]):
				continue
			if not game_grid[i][j]:
					continue
			if (i,j) in word.locs: # Don't inlcude word squares
				continue

			blocs.append(game_grid[i][j])
	word.bonus_sqs = blocs
	word.bonus_locs = [i.loc for i in word.bonus_sqs]
	word.bonus_letters = ''.join([i.letter for i in word.bonus_sqs])
	if len(word.bonus_letters) != 0:
		word.bonus_letters += word.word

	return word


def remove_word(word, grid):
	"""Remove word and associated bonus squares from play.
	
	Removes word and bonus squares from game grid and adjusts position
	of all squares so that removed squares are moved to the top of the
	grid.

	Args:
	  word (Word instance):
		A words to be highlighted
	  game_grid (list of lists of GameSquare instances):
		The tiles in the game in an array.

	Returns:
	  grid (List of lists of GameSquare instances of None)
	  Removed squares are replaced with None. Remaining squares are
	  GameSpace instances.
	"""

	for loc in word.locs:
		y,x = loc
		grid[y][x] = None

	for loc in word.bonus_locs:
		y,x = loc
		grid[y][x] = None

	for x in range(len(grid[0])):
		repeat = True # Keep track of whether another pass is needed.
		while repeat:
			repeat = False # set to true if a switch is perfomed.
			for y in range(1, len(grid)):
				# if the square is None but the square above is not
				if not grid[y][x] and grid[y-1][x]:
					grid[y][x], grid[y-1][x] = grid[y-1][x], grid[y][x]
					grid[y][x].loc = (y,x)
					repeat=True

	return grid


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

	
	words = [1] # Initialize for while loop
	score = 0
	used_words = []

	while len(words) > 0:
		words = []
		for y in range(len(game_grid)):
			for x in range(len(game_grid[0])):
				if game_grid[y][x]:
					words += [i for i in identify_words(game_grid,(y,x),
						indexed_dict, game_grid[y][x].letter.lower(), [(y,x)],
						letter_scores)]

		words.sort(key=lambda x: x.score, reverse=True)

		if len(words) > 0:

			score += words[0].score
			used_words.append(words[0].word)
		
			print_game(game_grid, words[0])

			game_grid = remove_word(words[0], game_grid)

			print_game(game_grid)

	print('Final score was {}\n\nWords found:\n{}'.format(score,
		'\n'.join(used_words)))



if __name__ == '__main__':
	main()
