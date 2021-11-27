# SpellTower-solver

A script to solve the android and iOS game SpellTower Puzzle mode by choosing the highest scoring possible words.

## Installation

SpellTower-solver is a Python script that uses command-line interface and produces output to the terminal. It will work on Linux or MacOS as well as Windows throuhg WSL.

SpellTower-solver uses tesseract and open-CV to process screenshots of SpellTower in order to build the initial game state. These dependencies can be installed using the following command:

`conda create -n st-solver python>3.6 -c conda-forge tesseract pytesseract opencv`

Installation of SpellTower-solver is as simple as cloning this repository.

## Usage

SpellTower-solver takes as input a .PNG image of a spelltower and outputs a representation of the playspace at each step in the game. 

Basic usage: `./st-solver.py screenshot.png`

### Example

SpellTower-solver processes the provided image using openCV and tesseract to identify the letters contained in each square as well as colour information that determines the behaviour of the square.

After identifying the contents of each square, it shows a text representation of the gamespace in which the highest scoring word is highlighted. For the example screenshot included in this repository produces the following output indicating the best word identified:

![Example_output.png!](https://github.com/Alan-Collins/SpellTower-solver/blob/main/images/Initial_output.png)

ANSI colours are used to highlight the squares that are involved in the selected word:
* The first letter in the word is blue
* The last letter in the word is yellow
* all other letters in the word are green
* Surrounding letters that will be included in the score and removed from play are in purple.

The word and its estimated score are printed about the grid. N.B. The score is sometimes wrong for long as I can't figure out how scoring differs for long vs short words.

The best word will then be "used", resulting in all letters in the word and all bonus letters being removed from the playspace. An updated playspace is then printed to the terminal and the process repeated.
Once no more words can be found, the estimated total score and a list of all words found is printed to the terminal.
