#!/usr/bin/env python

import sys
import json

def main():
	with open(sys.argv[1], 'r') as fin:
		words = [i for i in json.load(fin) if len(i) >2]


if __name__ == '__main__':
	main()	
