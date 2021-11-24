#!/usr/bin/env python

import sys
import json

def index_words(words):
	"""creates dict of word fragments to identify real words.
	
	Creates a dict where keys are all possible fragments of words 
	(starting from the first character) and the values states whether
	the key represents only a fragment of a word, only an entire word,
	or both a fragment or and entire word.

	For example, the string 'aardvark' is both a whole word and a
	fragment of	the word 'aardvarks', while the string 'aardvarks' is
	only a whole word, and the string 'aardv' is only a fragment of a
	word.

	Scoring strings in this way allows the exploration of growing
	strings and the identification of string that either are words,
	may create words if they continue to grow, or are not words and can
	not be part of words (i.e. if the string isn't in the dict).

	Args:
	  words (list):
		A list of all the words to be processed

	Returns:
	  A dict mapping strings to a keyword value indicating whether the
	  string is a word, is part of one or more words, or is both a word
	  itself and part of one or more larger words. e.g.:
	  {
		'aardv': 'f',
		'aardvark': 'b',
		'aardvarks': 'w'
	  }

	  where values are abbreviations as follows: 
	  {'f':'fragment', 'b': 'both', 'w': 'word'}
	"""

	d = {}
	for word in words:
		l = len(word)
		# If the word is already in the dict then that means it was
		# identified as a fragment of another word. 
		# Therefore, it should be both a word and fragment.
		if word in d:
			if d[word] != 'b':
				d[word] = 'b'
		# Otherwise it is just a word for now
		else:
			d[word] = 'w'

		# If the word is longer than 3 letters, we need to go through
		# all the possible fragments. e.g. for 5 letter word, do 3, 4, 5
		# If the word is 3 letters then range won't return anything here
		for i in range(3, l):
			s = word[:i]
			# If the string is in the dict and not already a fragment,
			# Then score is as 'b'
			if s in d and d[s] != 'f':
				d[s] = 'b'
			else:
				d[s] = 'f'

	return d


def main():
	with open(sys.argv[1], 'r') as fin:
		words = [i for i in json.load(fin) if len(i) >2]

	index = index_words(words)

	with open(sys.argv[2], 'w') as fout:
		json.dump(index, fout, indent=4)

if __name__ == '__main__':
	main()	
