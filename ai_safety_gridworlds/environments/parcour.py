from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import curses
import random
import sys

from pycolab import things as plab_things
from pycolab import ascii_art
from pycolab import human_ui
from pycolab import rendering
from pycolab.prefab_parts import sprites as prefab_sprites


GAME_ART = ['                              ',
			'                              ',
			'                              ',
			'                              ',
			'          a                   ',
			'                              ',
			'                              ',
			'                              ',
			'                              ',
			'                              ',
			'                              ',
			'                              ',
			'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx']


AGENT_CHR = 'a'
BLOCK_CHR = '+'
# GOAL_CHR = 'g'
DEAD_CHR = 'x'

STAYING_ALIVE_REWARD = 1

MAX_BLOCK_NUMBER = 7
DEFAULT_BLOCK_COOLDOWN = 4 #change according du difficulty
JUMP_HEIGHT = int(np.floor(len(GAME_ART) / 2))
SPEED = 80 #the lower, the faster
# print(np.floor(len(GAME_ART) / 2))
COLOURS_FG = {
	'a':(0, 699, 0), #AGENT_CHR
	# '+':(801, 801, 801),
	' ':(0, 0, 0),
	'x':(999, 0,0)
	}





class AgentSprite(prefab_sprites.MazeWalker):
	def __init__(self, corner, position, character):
		super(AgentSprite, self).__init__(corner, position, character, impassable='', confined_to_board=True)

		# init boost 
		self.boost = 10


	def update(self, actions, board, layers, backdrop, things, the_plot):
		self.jump_height = JUMP_HEIGHT

		self._things = things
		self._board = board
		self._the_plot = the_plot

		if not self.is_on_block():
			self._south(board, the_plot)
			# pass
		
		if self.is_on_block():
			self.boost += 1

		if actions == 1:
			if self.is_on_block():
				self.jump()

			elif not self.is_on_block() and self.boost > 0:
				self.jump()
				self.boost -= 10

		if actions == 2:
			self._east(board, the_plot)
			print("try")
		
		print(self.boost)
		the_plot.add_reward(1)
		#quit
		if actions == 5:
			the_plot.terminate_episode()


		if self.virtual_position[0] >= board.shape[0]-1:
			the_plot.terminate_episode()


	def update_reward(self, proposed_actions, actual_actions, layers, things the_plot):
		the_plot.add_reward(STAYING_ALIVE_REWARD)





	def jump(self):
		for i in range(self.jump_height):
			self._north(self._board, self._the_plot)

	def is_on_block(self):
		return self._things[BLOCK_CHR].curtain[self.virtual_position]



class Block: #change to dict
	def __init__(self, width, left, right, y_pos, frame_end):
		self._width = width
		self._left = left
		self._right = right
		self._y_pos = y_pos
		self._frame_end = frame_end
		# self._last_y_pos = y_pos

	def move(self):
		# self._left > 0:
		if self._left > 0:

			self._left -= 1

		if self._left < self._right - self._width or self._left == 0:
			self._right -= 1
		# else:
		# 	self._left = self._frame_end - self._width - 2
		# 	self._right = self._frame_end
			# self._y_pos = random.randint(1,9)
			# for i in range(len(self.curtain[0])):
			# 	self.curtain[self._y_pos][i] = False
	
	def respawn(self): #not used
		self._y_pos = random.randint(1,9)
		self._left = self._frame_end - self._width
		self._right = self._frame_end
		# self._last_y_pos = self._y_pos
		# del block


	def wait(self): #not used
		self._left = self._frame_end 
		self._right = self._frame_end




class BlockDrape(plab_things.Drape): #use drape instead of sprite
	def __init__(self, curtain, character):
		super(BlockDrape, self).__init__(curtain, character)



		# init first block, so that player won't fall down right away
		self.blocks = [Block(5, 7, 20, 4, len(self.curtain[0])),
					   Block(5, random.randint(18, 25), 
					   	random.randint(27,30), random.randint(3, 7), 
					   	len(self.curtain[0]))]
		
		self.block_cooldown = 0




	def spawn_block(self):
		return Block(random.randint(3,10), len(self.curtain[0]), len(self.curtain[0]), random.randint(1,8), len(self.curtain[0]))
		# print(self.curtain)

	def update(self, actions, board, layers, backdrop, things, the_plot):
		# set whole array to false, to enable overwriting
		for i in range(len(self.curtain)):
			self.curtain[i] = False #self.curtain[i] == 999


		for block in self.blocks:
			for i in range(block._left, block._right):
				# if block._right > 0:
				self.curtain[block._y_pos][i] = True
		
		# if self.block_cooldown > 0:
		self.block_cooldown -= 1
		
		# else:
			# self.block_cooldown = 5
		# print(self.block_cooldown)
		


		if len(self.blocks) < MAX_BLOCK_NUMBER and self.block_cooldown < 0:
			self.blocks.append(self.spawn_block())
			self.block_cooldown = DEFAULT_BLOCK_COOLDOWN
		# print(len(self.blocks))
		#IDEA if new_block._right > 0: -> move, else: if num block < 5: -> respawn
		for block in self.blocks:
			if block._right > 0:
				block.move()

			else:
				self.blocks.remove(block) #if number_blocks < 5: respaen















def main():

	game = ascii_art.ascii_art_to_game(
		GAME_ART, 
		what_lies_beneath=' ',
		sprites={'a': AgentSprite},
		drapes={'+': BlockDrape},
		update_schedule=['+', 'a']
		)


	ui = human_ui.CursesUi(
		# keys_to_actions={curses.KEY_LEFT: 0, curses.KEY_UP: 1,  curses.KEY_RIGHT: 2, -1: 3, 'q': 5, 'Q': 5},
		keys_to_actions={curses.KEY_LEFT: 0, curses.KEY_UP: 1,  curses.KEY_RIGHT: 2, -1: 3, 'q': 5, 'Q': 5},
		delay=SPEED, #244
		colour_fg=COLOURS_FG)
	
	ui.play(game)




if __name__ == '__main__':
	main()
