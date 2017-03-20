# -*- coding: UTF-8 -*-
# Python 2.7.8
# Libtcod 1.5.1
##########################################################################################
#                                                                                        #
#                                Armoured Commander II                                   #
#                                                                                        #
##########################################################################################
#                                                                                        #
#                          Project re-started July 25, 2016                              #
#                                                                                        #
##########################################################################################
#
#    Copyright (c) 2016-2017 Gregory Adam Scott (sudasana@gmail.com)
#
#    This file is part of Armoured Commander II.
#
#    Armoured Commander II is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Armoured Commander II is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Armoured Commander II, in the form of a file named "gpl.txt".
#    If not, see <http://www.gnu.org/licenses/>.
#
#    xp_loader.py is covered under a MIT License (MIT) and is Copyright (c) 2015
#    Sean Hagar; see XpLoader_LICENSE.txt for more info.
#


##########################################################################################
#                                                                                        #
#       The author does not condone any of the events or ideologies depicted herein      #
#                                                                                        #
##########################################################################################

##### Libraries #####
import libtcodpy as libtcod				# The Doryen Library
import ConfigParser					# for saving and loading settings
import time						# for animation timing
from random import choice, shuffle, sample
from operator import itemgetter
from textwrap import wrap				# for breaking up strings
from math import floor, cos, sin, sqrt			# for math
from math import degrees, atan2, ceil			# for heading calculation
import shelve						# for saving and loading games
import os, sys						# for OS-related stuff
import xp_loader, gzip					# for loading xp image files
import xml.etree.ElementTree as xml			# ElementTree library for xml

# needed for py2exe
import dbhash, anydbm					
from encodings import hex_codec, ascii, utf_8, cp850



##########################################################################################
#                                   Constant Definitions                                 #
#                                   You can rely on them                                 #
##########################################################################################

# debug constants: should all be set to False in any distribution version
VIEW_ALL = False				# human player can see all hexes on viewport
SHOW_TERRAIN_GEN = False			# display terrain generation in progress


NAME = 'Armoured Commander II'
VERSION = 'Proof of Concept 2'				# determines saved game compatability
SUBVERSION = ''						# descriptive, no effect on compatability
DATAPATH = 'data/'.replace('/', os.sep)			# path to data files
LIMIT_FPS = 50						# maximum screen refreshes per second
WINDOW_WIDTH = 83					# width of game window in characters
WINDOW_HEIGHT = 60					# height "
WINDOW_XM = int(WINDOW_WIDTH/2)				# horizontal center of game window
WINDOW_YM = int(WINDOW_HEIGHT/2)			# vertical "
#PI = 3.141592653589793					# good enough for the JPL, good enough for us

# gradient animated effect for main menu
GRADIENT = [
	libtcod.Color(51, 51, 51), libtcod.Color(64, 64, 64), libtcod.Color(128, 128, 128),
	libtcod.Color(192, 192, 192), libtcod.Color(255, 255, 255), libtcod.Color(192, 192, 192),
	libtcod.Color(128, 128, 128), libtcod.Color(64, 64, 64), libtcod.Color(51, 51, 51),
	libtcod.Color(51, 51, 51)
]

# Game engine constants, can be tweaked for slightly different results
MAX_LOS_DISTANCE = 13				# maximum distance that a Line of Sight can be drawn
ELEVATION_M = 20.0				# each elevation level represents x meters of height
MP_ALLOWANCE = 12				# how many MP each unit has for each Movement phase

# Weapon stat constants, will be tweaked for realism and balance
# id : display name, long range rating, maximum range, area fire strength, point fire strength
WEAPON_STATS = {
	'rifles': ['Rifles', '', 2, 1, 0, 'small_arms'],
	'rifles_mgs': ['Rifles and MGs', '', 2, 4, 0, 'small_arms'],
	'at_rifle': ['AT Rifle', '', 3, 0, 2, 'gun'],
	'hmg': ['HMG', '', 3, 6, 2, 'mg'],
	'vehicle_mg': ['MG', '', 2, 4, 0, 'mg'],
	'vehicle_mgs' : ['MGs', '', 2, 6, 0, 'mg'],
	'twin_vehicle_mgs' : ['Twin MGs', '', 2, 8, 0, 'mg'],
	'vehicle_aa_mg': ['AA MG', '', 2, 4, 0, 'mg'],
	'vehicle_aa_hmg': ['AA HMG', '', 3, 8, 2, 'mg'],
	'20L' : ['20mm', 'L', 4, 2, 4, 'gun'],
	'37' : ['37mm', '', 4, 4, 4, 'gun'],
	'37L' : ['37mm', 'L', 5, 2, 6, 'gun'],
	'47' : ['47mm', '', 6, 3, 8, 'gun']
}


# turn phases, in order
PHASE_LIST = ['Movement', 'Shooting', 'Close Combat']

# Colour definitions
OPEN_GROUND_COL = libtcod.Color(0, 64, 0)
RIVER_BG_COL = libtcod.Color(0, 0, 217)			# background color for river edges
DIRT_ROAD_COL = libtcod.Color(50, 40, 25)		# background color for dirt roads

NEUTRAL_OBJ_COL = libtcod.Color(0, 255, 255)		# neutral objective color
ENEMY_OBJ_COL = libtcod.Color(255, 31, 0)		# enemy-held "
FRIENDLY_OBJ_COL = libtcod.Color(50, 255, 0)		# friendly-held "

PORTRAIT_BG_COL = libtcod.Color(217, 108, 0)		# background color for unit portraits
HIGHLIGHT_COLOR = libtcod.Color(51, 153, 255)		# text highlight colour
HIGHLIGHT_BG_COLOR = libtcod.Color(0, 50, 100)		# text background highlight colour - blue
HIGHLIGHT_BG_COLOR2 = libtcod.Color(32, 64, 0)		# text background highlight colour - green

WEAPON_LIST_COLOR = libtcod.Color(25, 25, 90)		# background for weapon list in PSG console
SELECTED_WEAPON_COLOR = libtcod.Color(50, 50, 150)	# " selected weapon

TARGET_HL_COL = libtcod.Color(55, 0, 0)			# target highlight background color 
SELECTED_HL_COL = libtcod.Color(100, 255, 255)		# selected PSG highlight colour
ENEMY_HL_COL = libtcod.Color(40, 0, 0)
INACTIVE_COL = libtcod.Color(100, 100, 100)		# inactive option color
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency

KEY_HIGHLIGHT_COLOR = libtcod.Color(70, 170, 255)	# highlight for key commands

# Descriptor definitions
MORALE_DESC = {
	'7' : 'Reluctant', '6' : 'Regular', '5' : 'Confident', '4' : 'Fearless', '3' : 'Fanatic'
}
SKILL_DESC = {
	'7': 'Green', '6' : '2nd Line', '5' : '1st Line', '4' : 'Veteran', '3' : 'Elite'
}

MONTH_NAMES = [
	'', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
	'September', 'October', 'November', 'December'
]

DESTHEX = [(0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0)]	# change in hx, hy values for hexes in each direction
PLOT_DIR = [(0,-1), (1,-1), (1,1), (0,1), (-1,1), (-1,-1)]	# position of direction indicator
TURRET_CHAR = [254, 47, 92, 254, 47, 92]			# characters to use for turret display

# pre-calculated hexpairs and second hex step for lines of sight along hexspines
HEXSPINES = {
	30: [(0,-1), (1,-1), (1,-2)],
	90: [(1,-1), (1,0), (2,-1)],
	150: [(1,0), (0,1), (1,1)],
	210: [(0,1), (-1,1), (1,2)],
	270: [(-1,1), (-1,0), (-2,1)],
	330: [(-1,0), (0,-1), (-1,-1)]
}

# tile locations of hex edges
HEX_EDGE_TILES = [(-1,-2), (0,-2), (1,-2), (2,-1), (3,0), (2,1), (1,2), (0,2), (-1,2),
	(-2,1), (-3,0), (-2,-1)]


# option codes, key codes, and directional arrows to use for rotate/move commands
MOVE_COMMANDS = [
	(5, 'Q', chr(231)), (0, 'W', chr(24)), (1, 'E', chr(228)), (4, 'A', chr(230)),
	(3, 'S', chr(25)), (2, 'D', chr(229))
]


# fire table values
# highest column that is not more than attack strength is used
# number is the final dice roll to equal or beat for: Morale Check, -1 Step, -2 Steps, etc.
# if 0, then not possible

FIRE_TABLE = [
	[11, 12, 0, 0, 0, 0, 0, 0, 0, 0],		# AF 0
	[10, 11, 0, 0, 0, 0, 0, 0, 0, 0],		# AF 1
	[9, 11, 0, 0, 0, 0, 0, 0, 0, 0],		# AF 2
	[9, 10, 0, 0, 0, 0, 0, 0, 0, 0],		# AF 3
	[8, 10, 0, 0, 0, 0, 0, 0, 0, 0],		# AF 4 / PF 1
	[8, 9, 0, 0, 0, 0, 0, 0, 0, 0],			# AF 5 
	[7, 9, 12, 0, 0, 0, 0, 0, 0, 0],		# AF 6
	[6, 9, 12, 0, 0, 0, 0, 0, 0, 0],		# AF 7 / PF 2
	[6, 9, 11, 12, 0, 0, 0, 0, 0, 0],		# AF 9
	[6, 8, 11, 12, 0, 0, 0, 0, 0, 0],		# AF 11 / PF 3
	[5, 8, 10, 11, 0, 0, 0, 0, 0, 0],		# AF 14 / PF 4
	[4, 7, 9, 11, 12, 0, 0, 0, 0, 0],		# AF 17 / PF 5
	[3, 7, 9, 10, 11, 12, 0, 0, 0, 0]		# AF 21 / PF 6
]                                                   
MAX_FIRE_TABLE_COLUMN = len(FIRE_TABLE)

# AF, PF strengths to use for each column above
FIRE_TABLE_ROWS = [
	(0,0),(1,0),(2,0),(3,0),(4,1),(5,0),(6,0),(7,2),(9,0),(11,3),(14,4),(17,5),(21,6)
]

# column shifts for differentials in point strength vs. armour rating
# FUTURE: will need to adjust to that they are fair
AP_MODS = {
	5:3,
	4:2,
	3:1,
	2:0,
	1:-1,
	0:-2,
	-1:-4,
	-2:-8
}
MAX_AP_DIFF = 5
MIN_AP_DIFF = -2



##########################################################################################
#                                         Classes                                        #
##########################################################################################

# animation handler
# keeps track of animations in progress and updates the animation console layer
class AnimHandler:
	def __init__(self):
		
		# TEMP testing rain animation effect
		#self.raindrops = []
		#for i in range(20):
		#	x = libtcod.random_get_int(0, 0, 56)
		#	y = libtcod.random_get_int(0, 0, 56)
		#	lifetime = libtcod.random_get_int(0, 4, 7)
		#	self.raindrops.append([x, y, lifetime])
		
		self.update_timer = time.time()
	
	# update animation statuses and animation console
	def Update(self):
		
		# TEMP
		return
		
		# not time to update yet
		if time.time() - self.update_timer <= 0.1: return False
		
		self.update_timer = time.time()
		
		# update raindrop position and lifetime
		for drop in self.raindrops:
			drop[0] += 1
			drop[1] += 1
			drop[2] -= 1
			if drop[0] > 56 or drop[1] > 56 or drop[2] == 0:
				# reposition as new raindrop
				drop[0] = libtcod.random_get_int(0, 0, 56)
				drop[1] = libtcod.random_get_int(0, 0, 56)
				drop[2] = libtcod.random_get_int(0, 4, 7)
		
		# draw to console
		libtcod.console_clear(anim_con)
		for drop in self.raindrops:
			if drop[2] == 1:
				char = '*'
			else:
				char = chr(92)
			libtcod.console_put_char_ex(anim_con, drop[0], drop[1], char,
				libtcod.light_blue, libtcod.black)
		
		return True


# AI: used to determine actions of non-player-controlled units
class AI:
	def __init__(self, owner):
		self.owner = owner			# the PSG for whom this AI instance is
	
	# return a scored list of best possible attacks on this target
	def GetBestAttacks(self, target):
		
		distance = GetHexDistance(self.owner.hx, self.owner.hy, target.hx, target.hy)
		
		# will hold list of following: (final column, weapon, target, area_fire, at_attack)
		attack_list = []
		
		# run through available weapons
		for weapon in self.owner.weapon_list:
			# out of range
			if distance > weapon.stats['max_range']:
				continue
				
			# point fire target but not spotted
			if target.pf_target and not target.af_target and not target.spotted:
				continue

			# area fire target but no area fire possible
			if target.af_target and not target.pf_target and weapon.stats['area_strength'] == 0:
				continue
			
			# point fire target but no point fire possible
			if target.pf_target and not target.af_target and weapon.stats['point_strength'] == 0:
				continue
			
			# not in LoS
			visible_hexes = GetLoS(self.owner.hx, self.owner.hy, target.hx, target.hy)
			if (target.hx, target.hy) not in visible_hexes:
				continue
			
			# determine if a pivot would be required
			pivot_required = False
			if not self.owner.infantry:
				bearing = GetRelativeBearing(self.owner, target)
				if 30 < bearing < 330:
					pivot_required = True
			
			# calculate column of attack and add to attack list
			if weapon.stats['area_strength'] > 0 and target.af_target:
				attack_obj = CalcAttack(self.owner, weapon, target, True, assume_pivot=pivot_required)
				attack_list.append((attack_obj.final_column, weapon, target, True, False))
			
			if weapon.stats['point_strength'] > 0 and target.pf_target:
				attack_obj = CalcAttack(self.owner, weapon, target, False, assume_pivot=pivot_required)
				attack_list.append((attack_obj.final_column, weapon, target, False, False))
	
			del attack_obj
	
		# check for possible anti-tank attack
		if self.owner.infantry and target.vehicle and target.armour is not None and distance == 0:
			attack_obj = CalcAttack(self.owner, None, target, False, at_attack=True)
			attack_list.append((attack_obj.final_column, None, target, False, True))
		
		# no attacks possible
		if len(attack_list) == 0:
			return None
		
		return attack_list
		
	
	# randomly choose and execute and action for the current phase
	def DoPhaseAction(self):
		
		# Movement Phase actions
		if scenario.GetCurrentPhase() == 'Movement':
			# TEMP - no move actions
			return
		
		# Shooting Phase actions
		elif scenario.GetCurrentPhase() == 'Shooting':
			
			print 'AI Shooting Phase Action for: ' + self.owner.GetName(true_name=True)
			
			# build list of possible targets
			target_list = []
			for psg in scenario.psg_list:
				# same team!
				if psg.owning_player == self.owner.owning_player: continue
				
				# no line of sight
				if (psg.hx, psg.hy) not in GetLoS(self.owner.hx, self.owner.hy, psg.hx, psg.hy): continue
				
				target_list.append(psg)
			
			if len(target_list) == 0:
				print 'AI: No possible targets'
				return
			
			text = 'AI: Found ' + str(len(target_list)) + ' possible target'
			if len(target_list) > 1: text += 's'
			print text
			
			# select best attacks
			attack_list = []
			for psg in target_list:
				target_attack_list = self.GetBestAttacks(psg)
				if target_attack_list is not None:
					attack_list.extend(target_attack_list)
			
			# could not find any attacks
			if len(attack_list) == 0:
				print 'AI: No attacks possible'
				return
			
			text = 'AI: got a list of ' + str(len(attack_list)) + ' possible attack'
			if len(attack_list) > 1: text += 's'
			print text
			
			sorted(attack_list,key=itemgetter(0))
			
			# choose best attack and initiate it
			(final_column, weapon, target, area_fire, at_attack) = attack_list[0]
			
			InitAttack(self.owner, weapon, target, area_fire, at_attack=at_attack)
		

# terrain type: determines effect of different types of map hex terrain
class TerrainType:
	def __init__(self):
		self.console = []
		self.display_name = ''
		self.los_height = 0
		self.base_image = ''
		self.af_modifier = 0
		self.pf_modifier = 0
		self.water = False
		self.difficult = False
		self.very_difficult = False
		
	# load base image and generate other elevations
	def GenerateConsoles(self):
		for elevation in range(4):
			self.console.append(libtcod.console_new(7, 5))
			libtcod.console_blit(LoadXP(self.base_image), 0, 0, 7, 5, self.console[elevation], 0, 0)
			libtcod.console_set_key_color(self.console[elevation], KEY_COLOR)
		
		# apply colour modifier to elevations 0, 2, 3
		for elevation in [0, 2, 3]:
			for y in range(5):
				for x in range(7):
					bg = libtcod.console_get_char_background(self.console[elevation],x,y)
					if bg == KEY_COLOR: continue
					
					if elevation == 0:
						bg = bg * 0.9
					elif elevation == 2:
						bg = bg * 1.1
					else:
						bg = bg * 1.2
					libtcod.console_set_char_background(self.console[elevation],x,y,bg)


# Attack class, used for attack objects holding scores to use in an attack
# generated by CalcAttack
class Attack:
	def __init__(self, attacker, weapon, target):
		self.attacker = attacker
		self.weapon = weapon
		self.target = target
		self.area_fire = False
		self.point_fire = False
		self.at_attack = False
		self.attack_strength = 0
		self.column_modifiers = []
		self.final_column = 0
		self.outcome_list = []


# a single option in a CommandMenu list
class MenuOption:
	def __init__(self, option_id, key_code, option_text, desc, inactive):
		self.option_id = option_id	# unique id of this option
		self.key_code = key_code	# the key used to activate this option
		self.option_text = option_text	# text displayed for this option
		self.desc = desc		# description of this option
		self.inactive = inactive	# option is currently inactive

		# wrap option text
		# calculate total length of first line
		width = len(self.key_code) + 6 + len(self.option_text)
		if width > 23:
			wrap_w = 23 - (len(self.key_code) + 6)
			self.option_text_lines = wrap(self.option_text, wrap_w)
		else:
			self.option_text_lines = [self.option_text]
		# calculate display height
		self.h = len(self.option_text_lines)


# a list of options for the player
class CommandMenu:
	def __init__(self, menu_id):
		self.menu_id = menu_id			# a unique id for this menu
		self.cmd_list = []			# list of commands
		self.selected_option = None		# currently selected command
	
	# clear any existing menu options
	def Clear(self):
		self.cmd_list = []
		#self.selected_option = None
	
	# add an option to the menu
	def AddOption(self, option_id, key_code, option_text, desc=None, inactive=False):
		new_option = MenuOption(option_id, key_code, option_text, desc, inactive)
		self.cmd_list.append(new_option)
		# if we're adding the first option, select it
		if len(self.cmd_list) == 1:
			self.selected_option = self.cmd_list[0]
		return new_option
	
	# return the option_id associated with keyboard input
	def GetOptionByKey(self):
		key_char = chr(key.c).lower()
		for option in self.cmd_list:
			if option.key_code.lower() == key_char:
				return option
			if option.key_code == 'Enter' and key.vk == libtcod.KEY_ENTER:
				return option
			if option.key_code == 'Tab' and key.vk == libtcod.KEY_TAB:
				return option
			if option.key_code == 'Space' and key.vk == libtcod.KEY_SPACE:
				return option
			if option.key_code == 'Backspace' and key.vk == libtcod.KEY_BACKSPACE:
				return option
			if option.key_code == 'Esc' and key.vk == libtcod.KEY_ESCAPE:
				return option
		return None
	
	# shift selection to next or previous option
	def SelectNextOption(self, reverse=False):
		# no options in list, abort
		if len(self.cmd_list) == 0:
			return
		n = self.cmd_list.index(self.selected_option)
		if reverse:
			if n == 0:
				n = len(self.cmd_list)-1
			else:
				n -= 1
		else:
			if n == len(self.cmd_list)-1:
				n = 0
			else:
				n += 1
		self.selected_option = self.cmd_list[n]
	
	# returns the currently selected option, returning None if this option is inactive
	def GetSelectedOption(self):
		option = self.selected_option
		if option.inactive:
			return None
		return option
	
	# display the menu to the specified console
	def DisplayMe(self, console, x, y, w):
		original_fg = libtcod.console_get_default_foreground(console)
		original_bg = libtcod.console_get_default_background(console)
		
		# menu is empty
		if len(self.cmd_list) == 0:
			libtcod.console_set_default_foreground(console, libtcod.dark_grey)
			libtcod.console_print(console, x, y, 'None')
			libtcod.console_set_default_foreground(console, original_fg)
			return
		
		n = 0
		for menu_option in self.cmd_list:
			
			# display command key text
			if menu_option.inactive:
				libtcod.console_set_default_foreground(console, INACTIVE_COL)
			else:
				libtcod.console_set_default_foreground(console, KEY_HIGHLIGHT_COLOR)
			libtcod.console_print(console, x, y+n, menu_option.key_code)
			
			# display command text lines
			if not menu_option.inactive:
				libtcod.console_set_default_foreground(console, libtcod.white)
			
			for line in menu_option.option_text_lines:
				libtcod.console_print(console, x+6, y+n, line)
				n+=1
			
			# reset display colour
			libtcod.console_set_default_foreground(console, original_fg)
			
		# highlight any selected option and display description if any
		max_n = n
		n = 0
		for menu_option in self.cmd_list:
			if self.selected_option == menu_option:
				libtcod.console_set_default_background(console, HIGHLIGHT_BG_COLOR)
				libtcod.console_rect(console, x, y+n, w, menu_option.h, False, libtcod.BKGND_SET)
				libtcod.console_set_default_background(console, original_bg)
				
				if menu_option.desc is not None:
					if menu_option.inactive:
						libtcod.console_set_default_foreground(console, libtcod.dark_grey)
					else:
						libtcod.console_set_default_foreground(console, libtcod.white)
					lines = wrap(menu_option.desc, w)
					# we re-use n here since we don't need it anymore
					n = 0
					for line in lines:
						libtcod.console_print(console, x, y+max_n+2+n,	line)
						n += 1
				
				break
						
			n += menu_option.h
		libtcod.console_set_default_foreground(console, original_fg)
		

# Platoon-Sized Group class
# represents a platoon, squadron, battery, etc.
class PSG:
	def __init__(self, name, unit_id, num_steps):
		self.unit_id = unit_id			# unique ID for unit type of this PSG
		self.name = name			# name, eg. 'Tank Squadron'
		self.step_name = ''			# name of individual teams / vehicles w/in this PSG
		self.num_steps = num_steps		# number of unit steps in this PSG
		self.portrait = None			# portrait filename if any
		self.ai = AI(self)			# pointer to AI instance
		self.owning_player = None		# player that controls this PSG; set later
		self.op_value = 0			# operations point value
		
		self.hx = -1				# hex location of this PSG, will be set
		self.hy = -1				#   by PlaceAt()
		self.screen_x = 0			# draw location on the screen
		self.screen_y = 0			#   set by DrawMe()
		self.anim_x = 0				# animation location in console
		self.anim_y = 0
		
		self.spotted = False			# PSG has been spotted by an enemy unit
		
		self.facing = None			# facing direction: guns and vehicles must have this set
		
		self.movement_class = ''		# movement class
		self.armour = None			# armour factors if any
		
		self.weapon_list = []			# list of weapons
		self.selected_weapon = None		# currently selected weapon
		
		self.target_list = []			# list of possible targets
		self.target_psg = None			# currently targeted PSG
		
		self.acquired_target = None		# PSG has acquired this unit as target
		self.acquired_by = []			# PSG has been acquired by this unit(s)
		
		self.assault_target = None		# PSG is locked into assaulting this hex location
		
		self.infantry = False			# PSG type flags
		self.gun = False
		self.vehicle = False
		
		self.af_target = False			# PSG can be targeted by area fire
		self.pf_target = False			# " point fire
		
		self.gun_shield = False			# unit has a gun shield
		
		self.recce = False			# unit has recce abilities (not used yet)
		self.unreliable = False			# vehicle unit may suffer breakdowns
		
		self.display_char = ''			# character to display on map, set below
		
		self.skill_lvl = 7			# skill and morale levels; can be set later
		self.morale_lvl = 7
		
		# action flags
		self.moved = False
		self.fired = False
		self.changed_facing = False
		
		# status levels and flags
		#self.dug_in = False			# only infantry units and guns can dig in
		#self.hull_down = -1			# only vehicles can be hull down, number
							#   is direction
		
		self.pin_points = 0
		self.suppressed = False			# move N/A, attacks less effective
		
		#self.bogged = False			# move N/A
		#self.broken = False			# move/fire N/A, must rout unless armoured
		#self.melee = False			# held in melee
		
		self.max_mp = MP_ALLOWANCE		# maximum Movement Points per turn
		self.mp = self.max_mp			# current mp
		
		# load stats from data file
		self.LoadStats()
		
		# set area/point fire target status
		if self.infantry:
			self.af_target = True
		elif (self.vehicle and self.armour is None) or self.gun:
			self.af_target = True
			self.pf_target = True
		elif self.vehicle and self.armour:
			self.pf_target = True
		
		# set initial display character
		self.display_char = self.GetDisplayChar()
		
		# select first weapon by default
		if len(self.weapon_list) > 0:
			self.selected_weapon = self.weapon_list[0]

	# get the base range in hexes that this PSG will be spotted by an enemy unit
	def GetSpotRange(self):
		
		# base distance
		if self.vehicle:
			spot_range = 6
		else:
			spot_range = 3
		
		if self.recce: spot_range -= 2
		
		# protective terrain
		map_hex = GetHexAt(self.hx, self.hy)
		if map_hex.terrain_type.af_modifier < 0 or map_hex.terrain_type.pf_modifier < 0:
			spot_range -= 1
		else:
			spot_range += 2
		
		# fired, moved, or pinned: apply worst one
		if self.fired:
			spot_range += 4
		elif self.moved:
			spot_range += 2
		elif self.pin_points > 0:
			spot_range -= 1
		
		# skill modifier
		if self.skill_lvl <= 4:
			spot_range -= 1
		
		return spot_range

	# try to place this PSG into the target hex, if not possible, place in random adjacent hex
	def PlaceAt(self, hx, hy):
		hex_list = [(hx, hy)]
		adjacent_list = GetAdjacentHexesOnMap(hx, hy)
		shuffle(adjacent_list)
		hex_list.extend(adjacent_list)
		for (hx1, hy1) in hex_list:
			map_hex = GetHexAt(hx1, hy1)
			if map_hex is None: continue
			if map_hex.IsOccupied() > -1: continue
			if map_hex.terrain_type.water: continue
			self.hx = hx1
			self.hy = hy1
			return
		print 'ERROR: unable to place PSG into or near ' + str(hx) + ',' + str(hy)

	# return description of PSG
	# if using real name, transcode it to handle any special characters in it
	# if true_name, return the real identity of this PSG no matter what
	def GetName(self, true_name=False):
		if not true_name:
			if self.owning_player == 1 and not self.spotted:
				return 'Possible Enemy PSG'
		return self.name.decode('utf8').encode('IBM850')

	# return the name of a single step within this PSG
	def GetStepName(self):
		return self.step_name.decode('utf8').encode('IBM850')

	# cycle selected weapon in list
	def SelectNextWeapon(self):
		if len(self.weapon_list) == 0: return
		if self.selected_weapon is None:
			self.selected_weapon = self.weapon_list[0]
			return
		if self.selected_weapon == self.weapon_list[-1]:
			self.selected_weapon = self.weapon_list[0]
			return
		n = self.weapon_list.index(self.selected_weapon)
		self.selected_weapon = self.weapon_list[n+1]

	# select next possible target for shooting
	def SelectNextTarget(self):
		# if no target list yet, try to build one
		if len(self.target_list) == 0:
			
			if self.selected_weapon is None:
				print 'ERROR: tried to build a target list but no weapon selected!'
				return
			
			for psg in scenario.psg_list:
				if psg.owning_player == 0: continue
				
				# check assaults in progress
				if self.assault_target is not None:
					(hx, hy) = self.assault_target
					if psg.hx != hx or psg.hy != hy:
						continue
				
				# check range
				max_range = self.selected_weapon.stats['max_range']
				if GetHexDistance(self.hx, self.hy, psg.hx, psg.hy) > max_range:
					continue
				# check LoS
				visible_hexes = GetLoS(self.hx, self.hy, psg.hx, psg.hy)
				if (psg.hx, psg.hy) not in visible_hexes:
					continue
				# add target to list
				self.target_list.append(psg)
		
		# no possible targets
		if len(self.target_list) == 0:
			return

		# no target selected yet, select the first one
		if self.target_psg is None:
			self.target_psg = self.target_list[0]
			return
		
		# last target in list selected, select the first one
		if self.target_psg == self.target_list[-1]:
			self.target_psg = self.target_list[0]
			return
		
		# select next target
		n = self.target_list.index(self.target_psg)
		self.target_psg = self.target_list[n+1]

	# clear any acquired target links between this PSG and any other
	def ClearAcquiredTargets(self):
		self.acquired_target = None
		self.acquired_by = []
		for psg in scenario.psg_list:
			if self in psg.acquired_by:
				psg.acquired_by.remove(self)
			if psg.acquired_target == self:
				psg.acquired_target = None

	# remove one step from this PSG
	def RemoveStep(self):
		self.num_steps -= 1
		if self.num_steps == 0:
			self.DestroyMe()
			UpdateUnitConsole()

	# remove this PSG from the game
	def DestroyMe(self):
		text = self.GetName() + ' has been destroyed!'
		Message(self.screen_x, self.screen_y, text)
		scenario.psg_list.remove(self)
		# clear acquired target records
		self.ClearAcquiredTargets()
		UpdateUnitConsole()

	# do any automatic actions for start of current phase
	def ResetForPhase(self):
		
		# clear any targets and selected weapon
		self.target_list = []
		self.target_psg = None
		self.selected_weapon = None
		
		# start of movement phase
		if scenario.GetCurrentPhase() == 'Movement':
			self.mp = self.max_mp
			self.moved = False
			self.changed_facing = False
			self.assault_target = None
		# start of shooting phase
		elif scenario.GetCurrentPhase() == 'Shooting':
			self.fired = False
			self.SelectNextWeapon()

	# roll for recovery from negative statuses
	# TODO: move into its own phase eventually
	def DoRecoveryTests(self):
		if not self.suppressed and self.pin_points == 0:
			return
		
		# test to rally from supression
		if self.suppressed:
			if self.MoraleCheck(0):
				self.UnSuppressMe()
			# lose 1 PP either way
			self.pin_points -= 1
			text = self.GetName() + ' now has ' + str(self.pin_points) + ' pin point'
			if self.pin_points != 1: text += 's'
			Message(self.screen_x, self.screen_y, text)
			return
		
		if self.pin_points == 0:
			return
		
		# test to remove pin points and avoid being suppressed
		if self.MoraleCheck(0):
			
			if self.pin_points == 1:
				lost_points = 1
			else:
				lost_points = int(ceil(self.pin_points / 2))
			self.pin_points -= lost_points
			text = self.GetName() + ' loses ' + str(lost_points) + ' pin point'
			if lost_points != 1: text += 's'
			Message(self.screen_x, self.screen_y, text)
			return
		
		# test failed, unit is suppressed
		self.SuppressMe()
			

	# load the baseline stats for this PSG from XML data file
	def LoadStats(self):
		# find the unit type entry in the data file
		root = xml.parse(DATAPATH + 'unit_defs.xml')
		item_list = root.findall('unit_def')
		for item in item_list:
			# this is the one we need
			if item.find('id').text == self.unit_id:
				if item.find('portrait') is not None:
					self.portrait = item.find('portrait').text
				self.step_name = item.find('name').text.encode('utf8')
				
				# movement class
				self.movement_class = item.find('movement_class').text
				
				# adjust maximum MP for slow and fast vehicles
				if self.movement_class == 'Slow Tank':
					self.max_mp -= 4
					self.mp = self.max_mp
				elif self.movement_class == 'Fast Tank':
					self.max_mp += 4
					self.mp = self.max_mp
				
				# weapon info
				weapon_list = item.findall('weapon')
				if weapon_list is not None:
					for weapon_item in weapon_list:
						new_weapon = SpawnWeapon(weapon_item)
						self.weapon_list.append(new_weapon)
				
				# infantry stats if any
				if item.find('infantry') is not None:
					self.infantry = True
				
				# vehicle stats if any
				if item.find('vehicle') is not None:
					self.vehicle = True
					if item.find('size_class') is not None:
						self.size_class = item.find('size_class').text
					else:
						self.size_class = 'Normal'
					if item.find('armour') is not None:
						self.armour = {}
						armour_ratings = item.find('armour')
						self.armour['front'] = int(armour_ratings.find('front').text)
						self.armour['side'] = int(armour_ratings.find('side').text)
					if item.find('recce') is not None: self.recce = True
					if item.find('unreliable') is not None: self.unreliable = True
				
				# gun stats
				elif item.find('gun') is not None:
					self.gun = True
					self.deployed = True
					#self.emplaced = True	# not used yet
					if item.find('size_class') is not None:
						self.size_class = item.find('size_class').text
					else:
						self.size_class = 'Normal'
					if item.find('gun_shield') is not None:
						self.gun_shield = True
				
				# OP value set for entire unit
				if item.find('op_value') is not None:
					self.op_value = self.num_steps * int(item.find('op_value').text)
				
				return
		
		print 'ERROR: Could not find unit stats for: ' + self.unit_id
	

	# this PSG has been revealed 
	def SpotMe(self):
		self.spotted = True

		# update unit console to display
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		
		# show message
		if self.owning_player == 0:
			text = 'Your '
		else:
			text = 'Enemy '
		text += self.GetName() + ' has been spotted!'
		Message(self.screen_x, self.screen_y, text)
	
	# regain unspotted status for this PSG
	def HideMe(self):
		# update console and screen to make sure unit has finished move animation
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		if self.owning_player == 0:
			text = self.GetName() + ' is now Unspotted'
		else:
			text = 'Lost contact with ' + self.GetName()
		Message(self.screen_x, self.screen_y, text)
		self.spotted = False
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
	
	# get display character to be used on hex map
	def GetDisplayChar(self):
		
		# enemy Hidden PSG
		if self.owning_player == 1 and not self.spotted:
			return '?'
		
		# infantry
		if self.infantry:
			return 176
		
		# gun, set according to deployed status / hull facing
		if self.gun:
			if not self.deployed:
				return 124
			elif self.facing in [5, 0, 1]:
				return 232
			elif self.facing in [2, 3, 4]:
				return 233
			else:
				return '!'		# should not happen
		
		# vehicle
		if self.vehicle:
			# tank
			if self.movement_class in ['Slow Tank', 'Tank', 'Fast Tank']:
				return 9
			# other, eg. armoured car
			else:
				return 7

		# default
		return '!'

	# draw this PSG to the unit console
	def DrawMe(self):
		
		# calculate draw position
		if self.anim_x == 0 or self.anim_y == 0:
			(x,y) = PlotHex(self.hx, self.hy)
		# position override for animations
		else:
			x = self.anim_x
			y = self.anim_y
			
		# record draw position on screen
		self.screen_x = x + 26
		self.screen_y = y + 3
		
		self.display_char = self.GetDisplayChar()
		
		# determine foreground color to use
		if self.owning_player == 1:
			if not self.spotted:
				col = libtcod.dark_red
			else:
				col = libtcod.red
		else:	
			if not self.spotted:
				col = libtcod.light_grey
			else:
				col = libtcod.white
		libtcod.console_put_char_ex(unit_con, x, y, self.display_char, col,
			libtcod.black)
		
		# determine if we need to display a turret
		if not self.gun and not self.vehicle: return
		if self.owning_player == 1 and not self.spotted: return
		
		# determine location to draw turret character
		x_mod, y_mod = PLOT_DIR[self.facing]
		char = TURRET_CHAR[self.facing]
		libtcod.console_put_char_ex(unit_con, x+x_mod, y+y_mod, char, col, libtcod.black)
	
	# pivot the this PSG to face the given direction
	def PivotToFace(self, direction):
		if self.facing is None: return
		self.facing = direction
		self.changed_facing = True
		
	# determine if this PSG is able to move into the target hex
	def CheckMoveInto(self, new_hx, new_hy):
		if self.movement_class == 'Gun': return False
		if (new_hx, new_hy) not in scenario.hex_map.hexes: return False
		direction = GetDirectionToAdjacent(self.hx, self.hy, new_hx, new_hy)
		if direction < 0: return False
		map_hex = GetHexAt(new_hx, new_hy)
		if map_hex.IsOccupied() == self.owning_player: return False
		if map_hex.terrain_type.water: return False
		return True
	
	# try to move this PSG into the target hex
	# vehicles must be facing this direction to move, or can do a reverse move
	# returns True if the move was successful
	def MoveInto(self, new_hx, new_hy, free_move=False):
		
		# make sure move is allowed
		if not self.CheckMoveInto(new_hx, new_hy):
			return False
		
		map_hex1 = GetHexAt(self.hx, self.hy)
		map_hex2 = GetHexAt(new_hx, new_hy)
		
		if not free_move:
			# get MP cost of move, return false if not enough
			mp_cost = GetMPCostToMove(self, map_hex1, map_hex2)
			if mp_cost > self.mp: return False
			
			# check for unreliable effect
			if self.unreliable:
				d1, d2, roll = Roll2D6()
				if roll <= 3:
					extra_cost = libtcod.random_get_int(0, 1, 6)
					if mp_cost + extra_cost > self.mp:
						extra_cost = self.mp - mp_cost
					if mp_cost > 0:
						mp_cost += extra_cost
						if not (self.owning_player == 1 and not self.spotted):
							text = self.GetName() + ' suffers a breakdown, +'
							text += str(extra_cost) + 'MP cost!'
							Message(self.screen_x, self.screen_y, text)
						
			# spend the mp
			self.mp -= mp_cost
		
		# see if a pivot is required
		if self.movement_class != 'Infantry':
			if self.facing is not None:
				pause_time = config.getint('ArmCom2', 'animation_speed') * 2
				direction = GetDirectionToAdjacent(self.hx, self.hy,
					new_hx, new_hy)
				self.PivotToFace(direction)
				UpdateUnitConsole()
				DrawScreenConsoles()
				libtcod.console_flush()
				Wait(pause_time)
		
		# display movement animation
		pause_time = config.getint('ArmCom2', 'animation_speed') * 3
		(x1,y1) = PlotHex(self.hx, self.hy)
		(x2,y2) = PlotHex(new_hx, new_hy)
		line = GetLine(x1,y1,x2,y2)
		for (x,y) in line[1:-1]:
			self.anim_x = x
			self.anim_y = y
			UpdateUnitConsole()
			DrawScreenConsoles()
			libtcod.console_flush()
			Wait(pause_time)
		
		self.anim_x = 0
		self.anim_y = 0
		self.hx = new_hx
		self.hy = new_hy
		
		# set action flag for next activation
		self.moved = True
		
		# clear any acquired targets
		self.ClearAcquiredTargets()
		
		# recalculate FoV if needed
		if self.owning_player == 0:
			scenario.hex_map.CalcFoV()
			UpdateMapFoVConsole()
			scenario.DoSpotCheck()
		
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		
		# check for objective capture
		map_hex2.CheckCapture()
		
		return True
	
	# resolve an attack against this PSG
	def ResolveAttack(self, attack_obj):
		
		# clear and "Backspace to Cancel" and "Enter to Roll" line
		libtcod.console_print_ex(attack_con, 13, 53, libtcod.BKGND_NONE,
			libtcod.CENTER, '                   ')
		libtcod.console_print_ex(attack_con, 13, 54, libtcod.BKGND_NONE,
			libtcod.CENTER, '             ')
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 3)
		libtcod.console_flush()
		
		# do dice roll and display animation
		pause_time = config.getint('ArmCom2', 'animation_speed') * 8
		for i in range(5):
			d1, d2, roll = Roll2D6()
			DrawDie(attack_con, 9, 42, d1)
			DrawDie(attack_con, 14, 42, d2)
			libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 3)
			libtcod.console_flush()
			Wait(pause_time)
		
		# display roll result on attack console
		libtcod.console_print_ex(attack_con, 13, 48, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Roll: ' + str(roll))
		
		# determine result
		result_row = None
		for score in reversed(attack_obj.final_column):
			if score == 0: continue
			if score <= roll:
				result_row = attack_obj.final_column.index(score)
				break
		
		if attack_obj.at_attack:
			if 2 <= roll <= 3:
				text = 'Attacking Step Lost'
			elif result_row is None:
				text = 'No Effect'
			else:
				if result_row == 0:
					text = 'No Effect'
				else:
					text = str(result_row) + ' step loss'
		else:
			if result_row is None:
				text = 'No Effect'
			elif result_row == 0:
				text = '+1 Pin Point'	
			else:
				text = str(result_row) + ' step loss'
			
		libtcod.console_print_ex(attack_con, 13, 50, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		libtcod.console_print_ex(attack_con, 13, 54, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Enter to Continue')
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 3)
		libtcod.console_flush()
		WaitForEnter()
		
		# apply attacker step loss result or no result
		if attack_obj.at_attack:
			if 2 <= roll <= 3:
				attack_obj.RemoveStep()
				return
			elif result_row == 0:
				return
		
		if result_row is None: return
		
		# apply result to target: step loss
		if result_row >= 1:
			for i in range(result_row):
				self.RemoveStep()
				# PSG has been destroyed
				if self not in scenario.psg_list:
					return
			
			text = self.GetName() + ' has been reduced to ' + str(self.num_steps) + ' step'
			if self.num_steps > 1: text += 's'
			Message(self.screen_x, self.screen_y, text)
		
		# apply pin point
		self.pin_points += 1
		text = self.GetName() + ' now has ' + str(self.pin_points) + ' pin point'
		if self.pin_points > 1: text += 's'
		Message(self.screen_x, self.screen_y, text)
		
		# already suppressed
		if self.suppressed: return
		
		# never suppressed in close combat
		if GetHexDistance(self.hx, self.hy, attack_obj.attacker.hx, attack_obj.attacker.hy) == 0:
			return

		# test for suppression
		if not self.MoraleCheck(0):
			self.SuppressMe()
		
	
	# perform a morale check for this PSG
	def MoraleCheck(self, modifier):
		
		# calculate effective morale level
		morale_lvl = self.morale_lvl
		
		# modifier provided by test conditions
		morale_lvl += modifier
		
		# protective terrain
		map_hex = GetHexAt(self.hx, self.hy)
		if map_hex.terrain_type.af_modifier > 0 or map_hex.terrain_type.pf_modifier > 0:
			morale_lvl -= 1
		
		# normalize
		if morale_lvl < 3:
			morale_lvl = 3
		elif morale_lvl > 10:
			morale_lvl = 10
		
		# do the roll
		d1, d2, roll = Roll2D6()
		
		# apply pin points
		roll -= self.pin_points
		
		if roll >= morale_lvl:
			return True
		return False
	
	# suppress this unit
	def SuppressMe(self):
		self.suppressed = True
		text = self.GetName() + ' has failed its morale check and is suppressed.'
		Message(self.screen_x, self.screen_y, text)
	
	# unit recovers from being suppressed
	def UnSuppressMe(self):
		self.suppressed = False
		text = self.GetName() + ' has rallied and recovers from being suppressed.'
		Message(self.screen_x, self.screen_y, text)
	
	# take a skill test, returning True if passed
	def SkillTest(self, modifier):
		skill_lvl = self.skill_lvl - modifier
		d1, d2, roll = Roll2D6()
		if roll <= skill_lvl:
			return True
		return False
	
	# have this unit retreat to an adjacent hex, triggered eg. in Close Combat
	def RetreatToSafety(self):
		
		# guns cannot retreat
		if self.movement_class == 'Gun':
			text = self.GetName() + ' cannot retreat!'
			Message(self.screen_x, self.screen_y, text)
			self.DestroyMe()
			return
		
		# build a list of possible destinations
		hex_list = []
		for direction in range(6):
			(hx, hy) = GetAdjacentHex(self.hx, self.hy, direction)
			if (hx, hy) not in scenario.hex_map.hexes: continue
			map_hex = GetHexAt(hx, hy)
			if map_hex.IsOccupied() > -1: continue
			if map_hex.terrain_type.water: continue
			hex_list.append((hx, hy))
		
		# no possible place to go
		if len(hex_list) == 0:
			text = self.GetName() + ' has no place to retreat!'
			Message(self.screen_x, self.screen_y, text)
			self.DestroyMe()
			return
		
		# FUTURE: choose location based on terrain modifier and distance from known enemy
		(hx, hy) = choice(hex_list)
		self.MoveInto(hx, hy, free_move=True)


# spawn a PSG into a scenario
def SpawnPSG(name, unit_id, num_steps):
	new_psg = PSG(name, unit_id, num_steps)
	scenario.psg_list.append(new_psg)
	return new_psg


# Weapon class: represents a weapon carried by or mounted on a unit
class Weapon:
	def __init__(self, stats):
		self.stats = stats
		

# a single terrain hex on the game map
# must have elevation and terrain type set before use
class MapHex:
	def __init__(self, hx, hy):
		self.hx = hx
		self.hy = hy
		self.elevation = None
		self.terrain_type = None
		
		self.objective = False			# hex is an objecrtive
		self.held_by = None			# if objective, currently held by this player
		
		self.river_edges = []			# list of adjacent hexes with
							#   which this hex shares a river edge
		self.dirt_road_links = []		# list of directions in which
							#   this hex is connected by
							#   a dirt road
		
		self.vis_to_player = False		# hex is currently visible to human player
		
		# Pathfinding stuff
		self.parent = None
		self.g = 0
		self.h = 0
		self.f = 0
	
	# set hex elevation
	# FUTURE: set up impassible cliff edges in this and adjacent hexes if required
	def SetElevation(self, new_elevation):
		self.elevation = new_elevation
	
	# set hex terrain
	def SetTerrainType(self, new_terrain_type):
		for terrain_type in terrain_types:
			if terrain_type.display_name == new_terrain_type:
				self.terrain_type = terrain_type
				return
		print 'ERROR: Terrain type not found: ' + new_terrain_type
	
	# returns owning player number if there is a PSG in this hex
	# otherwise -1 if empty
	def IsOccupied(self):
		for psg in scenario.psg_list:
			if psg.hx == self.hx and psg.hy == self.hy:
				return psg.owning_player
		return -1

	# reset pathfinding info for this map hex
	def ClearPathInfo(self):
		self.parent = None
		self.g = 0
		self.h = 0
		self.f = 0
	
	# check to see if this hex has been captured
	def CheckCapture(self, no_message=False):
		# this hex is not an objective
		if self.objective is False: return
		
		resident_psg = None
		for psg in scenario.psg_list:
			if psg.hx == self.hx and psg.hy == self.hy:
				resident_psg = psg
				break
		
		# no PSG in this hex
		if resident_psg is None: return
		
		# already held by this player
		if self.held_by is not None:
			if self.held_by == resident_psg.owning_player:
				return
		
		# captured!
		self.held_by = resident_psg.owning_player
		
		if not no_message:
			if self.held_by == 0:
				text = 'You have'
			else:
				text = 'The enemy has'
			text += ' captured this objective!'
			(x,y) = PlotHex(self.hx, self.hy)
			Message(x+26, y+3, text)
		
		UpdateGUIConsole()


# a map of hexes for use in a campaign day
class HexMap:
	def __init__(self, w, h):
		# record map width and height
		self.w = w
		self.h = h
		# lists of hexes along each edge
		self.top_edge_hexes = []
		self.right_edge_hexes = []
		self.bottom_edge_hexes = []
		self.left_edge_hexes = []
		
		# generate map hexes
		self.hexes = {}
		for hx in range(w):
			hy_start = 0 - hx//2
			hy_end = hy_start + h
			for hy in range(hy_start, hy_end):
				self.hexes[(hx,hy)] = MapHex(hx, hy)
				# add to edge lists if on edge of map
				if hx == 0:
					self.left_edge_hexes.append((hx, hy))
				elif hx == w-1:
					self.right_edge_hexes.append((hx, hy))
				elif hy == hy_start:
					self.top_edge_hexes.append((hx, hy))
				elif hy == hy_end-1:
					self.bottom_edge_hexes.append((hx, hy))
				
		self.vp_matrix = {}			# map viewport matrix
	
	# try to place an objective in the given hex, and place it nearby if this hex
	#   is impassible
	def AddObjectiveAt(self, hx, hy):
		hex_list = [(hx, hy)]
		adjacent_list = GetAdjacentHexesOnMap(hx, hy)
		shuffle(adjacent_list)
		hex_list.extend(adjacent_list)
		for (hx1, hy1) in hex_list:
			map_hex = GetHexAt(hx1, hy1)
			if not map_hex.terrain_type.water:
				map_hex.objective = True
				scenario.objective_hexes.append(map_hex)
				return
	
	# calculate field of view for human player
	def CalcFoV(self):
		
		# set all hexes to not visible to start
		for (hx, hy) in scenario.hex_map.hexes:
			scenario.hex_map.hexes[(hx, hy)].vis_to_player = False
		
		# debug mode
		if VIEW_ALL:
			for (hx, hy) in scenario.hex_map.hexes:
				scenario.hex_map.hexes[(hx, hy)].vis_to_player = True
			return
		
		# set all hex locations of player units to visible
		for psg in scenario.psg_list:
			if psg.owning_player == 1: continue
			scenario.hex_map.hexes[(hx, hy)].vis_to_player = True
		
		# run through each player unit and raycast to each map hex
		#start_time = time.time()
		for psg in scenario.psg_list:
			if psg.owning_player == 1: continue
			for (hx, hy) in scenario.hex_map.hexes:
				# skip already visible hexes
				if scenario.hex_map.hexes[(hx, hy)].vis_to_player: continue
				los_line = GetLoS(psg.hx, psg.hy, hx, hy)
				if (hx, hy) in los_line:
					scenario.hex_map.hexes[(hx, hy)].vis_to_player = True
		#end_time = time.time()
		#time_taken = round((end_time - start_time) * 1000, 3) 
		#print 'FoV raycasting finished: Took ' + str(time_taken) + ' ms.'

	# set a given hex on the campaign day map to a terrain type
	def SetHexTerrainType(self, hx, hy, terrain_type):
		self.hexes[(hx,hy)].terrain_type = terrain_type


# holds information about a scenario in progress
# on creation, also set the map size
class Scenario:
	def __init__(self, map_w, map_h):
		
		self.anim = AnimHandler()		# animation handler
		
		self.map_index = {}			# dictionary of console locations that
							#   correspond to map hexes
		
		self.name = ''				# scenario name
		self.battlefront = ''			# text description of battlefront
		self.year = 0				# current calendar year
		self.month = 0				# current calendar month
		self.hour = 0				# current time
		self.minute = 0
		
		self.hour_limit = 0			# time at which scenario ends
		self.minute_limit = 0
		self.time_limit_winner = 1		# player who wins if time limit is reached
		
		self.active_player = 0			# currently active player (0 or 1)
		self.current_phase = 0			# current action phase (full list defined by PHASE_LIST)
		
		self.psg_list = []			# list of all platoon-sized groups in play
		self.active_psg = None			# currently active PSG
		
		self.player_direction = 3		# direction of player-friendly forces
		self.enemy_direction = 0		# direction of enemy forces
		
		# scenario end variables
		self.winner = None			# number of player that has won the scenario,
							#   None if no winner yet
		self.end_text = ''			# description of how scenario ended
		
		self.cmd_menu = CommandMenu('scenario_menu')		# current command menu for player
		self.active_cmd_menu = None				# currently active command menu
		
		#self.messages = []			# FUTURE: list of stored game messages for review
		
		# create the hex map
		self.hex_map = HexMap(map_w, map_h)
		self.objective_hexes = []			# list of objective hexes
	
	# procedurally generate an Order of Battle for the AI player
	def GenerateEnemyOOB(self):
		
		psg_type_lists = {
			'Tank': [],
			'Gun': [],
			'Infantry': [],
			'Armoured Car': []
		}
		enemy_oob = []
		
		# TEMP - hardcoded
		enemy_nation = 'Poland'
		oob_op_budget = 400
		spawn_chances = {
			'Tank': 40,
			'Gun': 30,
			'Infantry': 20,
			'Armoured Car': 10
		}
		
		# load the order of battle definitions XML and build a list of possible PSG types
		#  for this nation
		psg_defs_item = None
		root = xml.parse(DATAPATH + 'oob_defs.xml')
		nation_list = root.findall('nation')
		for item in nation_list:
			if item.find('name').text == enemy_nation:
				psg_defs_item = item.find('psg_defs')
				break
		
		# could not find nation
		if psg_defs_item is None:
			print 'ERROR: Could not find PSG type definitions for nation: ' + enemy_nation
			return
		
		for item in psg_defs_item.findall('psg'):
			new_psg = {}
			new_psg['name'] = item.find('name').text
			category = item.find('category').text
			new_psg['category'] = category
			new_psg['unit_id'] = item.find('unit_id').text
			new_psg['min_steps'] = int(item.find('min_steps').text)
			new_psg['max_steps'] = int(item.find('max_steps').text)
			new_psg['skill_lvl'] = int(item.find('skill_lvl').text)
			new_psg['morale_lvl'] = int(item.find('morale_lvl').text)
			psg_type_lists[category].append(new_psg)
		
		# start selecting units until point limit is reached
		for tries in range(100):
			
			# randomly select a category of unit
			roll = libtcod.random_get_int(0, 1, 100)
			for key, value in spawn_chances.iteritems():
				if roll <= value:
					category = key
					break
				roll -= value
			
			psg_type = choice(psg_type_lists[category])
			num_steps = libtcod.random_get_int(0, psg_type['min_steps'],
				psg_type['max_steps'])
			
			new_psg = PSG(psg_type['name'], psg_type['unit_id'], num_steps)
			
			# not enough points remaining for this unit, skip
			if oob_op_budget < new_psg.op_value:
				del new_psg
				continue
			
			new_psg.owning_player = 1
			new_psg.facing = 3
			new_psg.skill_lvl = psg_type['skill_lvl']
			new_psg.morale_lvl = psg_type['morale_lvl']
			
			enemy_oob.append(new_psg)
			
			oob_op_budget -= new_psg.op_value
			
			#print ('DEBUG: spawned a ' + psg_type['name'] + ' unit with ' + 
			#	str(num_steps) + ' steps worth ' + str(new_psg.op_value) +
			#	' points')
		
		# add the list of enemy units into the scenario
		self.psg_list.extend(enemy_oob)
		
		# place units into map w/ PlaceAt()
		for psg in enemy_oob:
			
			# if infantry or gun, try to place into an objective first
			if psg.infantry or psg.gun:
				for map_hex in self.objective_hexes:
					if map_hex.IsOccupied() == -1:
						psg.PlaceAt(map_hex.hx, map_hex.hy)
						break
			# placment on objective was a success
			if psg.hx != -1 or psg.hy != -1:
				continue
			
			# choose a random map hex
			for tries in range(300):
				(hx, hy) = choice(self.hex_map.hexes.keys())
				# too close to bottom edge
				if hy + 6 >= 0 - hx//2 + self.hex_map.h:
					continue
				psg.PlaceAt(hx, hy)
				break
	
	
	# check for scenario end and set up data if so
	def CheckForEnd(self):
		
		# objective capture win
		all_objectives_captured = True
		for map_hex in self.objective_hexes:
			if map_hex.held_by is None:
				all_objectives_captured = False
				break
			if map_hex.held_by == 1:
				all_objectives_captured = False
				break
		
		if all_objectives_captured:
			self.winner = 0
			self.end_text = 'You have captured all objectives and won this scenario.'
			return
		
		# one side has no PSGs in play
		psgs_in_play = [0,0]
		for psg in self.psg_list:
			psgs_in_play[psg.owning_player] += 1
		if psgs_in_play[0] == 0:
			self.winner = 1
		elif psgs_in_play[1] == 0:
			self.winner = 0
		if self.winner is not None:
			if self.winner == 0:
				self.end_text += 'The enemy has no units remaining, you have'
			else:
				self.end_text += 'You have no units remaining, the enemy has'
			self.end_text += ' won this scenario.'
			return
		
		# time limit has been reached
		if self.minute == self.minute_limit and self.hour == self.hour_limit:
			self.winner = self.time_limit_winner
			self.end_text = 'The time limit for this scenario has been reached. '
			if self.winner == 0:
				self.end_text += 'You have'
			else:
				self.end_text += 'The enemy has'
			self.end_text += ' won this scenario.'
	
	# display a screen of info about a completed scenario
	def DisplayEndScreen(self):
		# use the buffer console to darken the screen background
		libtcod.console_clear(con)
		libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0, 
			0.0, 0.7)
		libtcod.console_rect(0, 4, 10, 80, 40, True, libtcod.BKGND_SET)
		
		lines = wrap(self.end_text, 26)
		y = 16
		for line in lines:
			libtcod.console_print_ex(0, WINDOW_XM, y, libtcod.BKGND_NONE,
				libtcod.CENTER, line)
			y+=1
		
		libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM+2, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Press [Enter] to Return to Main Menu')
		libtcod.console_flush()
		WaitForEnter()
	
	# resolve all close combats for this phase
	def ResolveCloseCombats(self):
		
		cc_psg_list = []
		
		for psg in self.psg_list:
			if psg.owning_player != self.active_player: continue
			if psg.assault_target is not None:
				cc_psg_list.append(psg)
		
		# no combats to resolve
		if len(cc_psg_list) == 0: return
		
		# FUTURE: sort list by MP remaining
		for attacker in cc_psg_list:
			
			# get target psg, clear assault target
			(hx, hy) = attacker.assault_target
			target = GetPSGAt(hx, hy)
			attacker.assault_target = None
			UpdateGUIConsole()
			DrawScreenConsoles()
			libtcod.console_flush()
			
			# clear both units' acquired targets
			attacker.ClearAcquiredTargets()
			if target is not None:
				target.ClearAcquiredTargets()
			
			# if target has been destroyed, take location
			if target is None:
				attacker.MoveInto(hx, hy, free_move=True)
				continue
			else:
				# if target location now occupied by an ally, cancel attack
				if target.owning_player == attacker.owning_player:
					continue
			
			# show message
			text = attacker.GetName() + ' assaults ' + target.GetName()
			Message(attacker.screen_x, attacker.screen_y, text)
			
			# do initial half-move animation
			pause_time = config.getint('ArmCom2', 'animation_speed') * 3
			(x1,y1) = PlotHex(attacker.hx, attacker.hy)
			(x2,y2) = PlotHex(target.hx, target.hy)
			line = GetLine(x1,y1,x2,y2)
			for (x,y) in line[1:2]:
				attacker.anim_x = x
				attacker.anim_y = y
				UpdateUnitConsole()
				DrawScreenConsoles()
				libtcod.console_flush()
				Wait(pause_time)
			
			# defensive fire: automatically choose best attack possible
			attack_list = target.ai.GetBestAttacks(attacker)
			if attack_list is None:
				text = 'No defensive fire possible'
				Message(target.screen_x, target.screen_y, text)
			else:
				sorted(attack_list,key=itemgetter(0))
				(final_column, weapon, null, area_fire, at_attack) = attack_list[0]
				text = target.GetName() + ' conducts defensive fire'
				Message(target.screen_x, target.screen_y, text)
				InitAttack(target, weapon, attacker, area_fire, at_attack=at_attack)
			
			# attacker was destroyed by defensive fire
			if attacker not in scenario.psg_list:
				continue
			
			# record original position and move attacker to target hex
			attacker_retreat_hx = attacker.hx
			attacker_retreat_hy = attacker.hy
			attacker.hx = target.hx
			attacker.hy = target.hy
			
			# if attacker has been Suppressed, it must fall back; skip attack loop
			if attacker.suppressed:
				text = attacker.GetName() + ' must break off attack'
				Message(attacker.screen_x, attacker.screen_y, text)
				attacker_won = False
				exit_attack = True
			else:
				
				# attacker and defender are spotted if not already
				if not target.spotted:
					target.SpotMe()
				if not attacker.spotted:
					attacker.SpotMe()
				
				# set flags to start attack loop
				exit_attack = False
				attacker_won = True
				attacker_steps = attacker.num_steps
				target_steps = target.num_steps
				
			while not exit_attack:
				
				# assaulting platoon attacks
				text = attacker.GetName() + ' attacks in close combat'
				Message(attacker.screen_x, attacker.screen_y, text)
				attack_list = attacker.ai.GetBestAttacks(target)
				
				if attack_list is None:
					text = 'Attacker cannot damage ' + target.GetName() + ' and must break off'
					Message(attacker.screen_x, attacker.screen_y, text)
					attacker_won = False
					exit_attack = True
					continue
				
				# pick best attack and do it
				sorted(attack_list,key=itemgetter(0))
				(final_column, weapon, null, area_fire, at_attack) = attack_list[0]
				InitAttack(attacker, weapon, target, area_fire, at_attack=at_attack)
				
				# if defender is dead, exit
				if target not in scenario.psg_list:
					exit_attack = True
					continue
				
				# defender is still alive, must pass a morale check to continue if has lost any steps
				if target.num_steps < target_steps:
					target_steps = target.num_steps
					if not target.MoraleCheck(0):
						text = target.GetName() + ' fails its morale check and must withdraw'
						Message(target.screen_x, target.screen_y, text)
						target.RetreatToSafety()
						exit_attack = True
						continue
				
				# defender gets an attack
				text = target.GetName() + ' attacks in close combat'
				Message(target.screen_x, target.screen_y, text)
				attack_list = target.ai.GetBestAttacks(attacker)
				
				if attack_list is None:
					text = target.GetName() + ' cannot damage attacker and must withdraw'
					Message(target.screen_x, target.screen_y, text)
					target.RetreatToSafety()
					exit_attack = True
					continue
				
				# pick best attack and do it
				sorted(attack_list,key=itemgetter(0))
				(final_column, weapon, null, area_fire, at_attack) = attack_list[0]
				InitAttack(target, weapon, attacker, area_fire, at_attack=at_attack)
				
				# if attacker is dead, exit
				if attacker not in scenario.psg_list:
					attacker_won = False
					exit_attack = True
					continue
				
				# attacker is still alive, must pass a morale check to continue if lost any steps
				if attacker.num_steps < attacker_steps:
					attacker_steps = attacker.num_steps
					if not attacker.MoraleCheck(0):
						text = attacker.GetName() + ' fails its morale check and must break off attack'
						Message(attacker.screen_x, attacker.screen_y, text)
						attacker_won = False
						exit_attack = True
						continue
			
			# attacker is dead, nothing more to do here
			if attacker not in scenario.psg_list:
				continue
			
			# move attacker into centre of new hex or into retreat area
			if not attacker_won:
				attacker.hx = attacker_retreat_hx
				attacker.hy = attacker_retreat_hy
				# TODO: pivot if required?
				
			pause_time = config.getint('ArmCom2', 'animation_speed') * 3
			(x2,y2) = PlotHex(attacker.hx, attacker.hy)
			line = GetLine(attacker.anim_x,attacker.anim_y,x2,y2)
			for (x,y) in line[1:]:
				attacker.anim_x = x
				attacker.anim_y = y
				UpdateUnitConsole()
				DrawScreenConsoles()
				libtcod.console_flush()
				Wait(pause_time)
			
			# reset attacker's animation location
			attacker.anim_x = 0
			attacker.anim_y = 0
			UpdateUnitConsole()
			DrawScreenConsoles()
			libtcod.console_flush()
			
			# recalculate FoV if needed
			if attacker.owning_player == 0:
				scenario.hex_map.CalcFoV()
				UpdateMapFoVConsole()
				scenario.DoSpotCheck()
			
			# check for objective capture
			GetHexAt(attacker.hx, attacker.hy).CheckCapture()
	
	# return a text string for the current turn phase
	def GetCurrentPhase(self):
		return PHASE_LIST[self.current_phase]
	
	# do enemy AI actions for this phase
	def DoAIPhase(self):
		# build a list of units that can be activated this phase
		activate_list = []
		for psg in self.psg_list:
			if psg.owning_player == 0: continue
			activate_list.append(psg)
		shuffle(activate_list)
		for psg in activate_list:
			psg.ai.DoPhaseAction()
	
	# end of turn, advance the scenario clock by one turn
	def AdvanceClock(self):
		self.minute += 15
		if self.minute >= 60:
			self.minute -= 60
			self.hour += 1
	
	# set current turn phase
	def SetPhase(self, new_phase):
		self.current_phase = PHASE_LIST.index(new_phase)
	
	# finish up current phase, start new phase (and possibly new turn as well)
	def NextPhase(self):
		
		# Movement -> Shooting Phase
		if self.GetCurrentPhase() == 'Movement':
			self.SetPhase('Shooting')
			self.active_cmd_menu = 'shooting_root'
		
		# Shooting -> Close Combat
		elif self.GetCurrentPhase() == 'Shooting':
			
			self.SetPhase('Close Combat')
			self.active_cmd_menu = 'cc_root'
			self.active_psg = None
			
		# Close Combat Phase -> New Active Player and Movement Phase
		elif self.GetCurrentPhase() == 'Close Combat':
			
			if self.active_player == 0:
				self.active_player = 1
				self.active_psg = None
			else:
				# end of turn, check for scenario end
				self.CheckForEnd()
				if self.winner is not None:
					# display scenario report
					self.DisplayEndScreen()
					# delete saved game
					EraseGame()
					return
				self.AdvanceClock()
				UpdateScenInfoConsole()
				self.active_player = 0
				scenario.SelectNextPSG()
			self.SetPhase('Movement')
			self.active_cmd_menu = 'movement_root'
			for psg in self.psg_list:
				if psg.owning_player == self.active_player:
					psg.DoRecoveryTests()
		
		# do automatic actions for active player's units for this phase
		for psg in self.psg_list:
			if psg.owning_player == self.active_player:
				psg.ResetForPhase()
		
		UpdatePSGConsole()
		self.BuildCmdMenu()
		SaveGame()
	
	# check to see if any units are spotted by enemy forces or regain unspotted status
	def DoSpotCheck(self):
		
		spotted_psgs = []
		unspotted_psgs = []
		
		# assume that all PSGs should be unspotted
		for psg in self.psg_list:
			unspotted_psgs.append(psg)
		
		# check all possible enemy pairs
		for psg1 in self.psg_list:
			for psg2 in self.psg_list:
				# both units are on same side
				if psg1.owning_player == psg2.owning_player:
					continue
				
				# check for no LoS
				if (psg2.hx, psg2.hy) not in GetLoS(psg1.hx, psg1.hy, psg2.hx, psg2.hy):
					continue
				
				# if psg2 was spotted, it won't lose this status if any enemy unit is in LoS
				if psg2.spotted and psg2 in unspotted_psgs:
					unspotted_psgs.remove(psg2)
					spotted_psgs.append(psg2)
					continue
				
				# calculate spot range for psg2
				spot_range = psg2.GetSpotRange()
				# add any bonuses for spotting unit
				if psg1.recce: spot_range += 2
				
				if GetHexDistance(psg1.hx, psg1.hy, psg2.hx, psg2.hy) <= spot_range:
				
					# psg2 has been spotted by psg1
					if psg2 in unspotted_psgs:
						unspotted_psgs.remove(psg2)
						spotted_psgs.append(psg2)
		
		# finally, go through lists and check for any changes in status
		for psg in spotted_psgs:
			if not psg.spotted:
				psg.SpotMe()
		for psg in unspotted_psgs:
			if psg.spotted:
				psg.HideMe()
	
	# select the next player PSG; or the first one in the list if none selected
	def SelectNextPSG(self):
		
		player_psgs = []
		for psg in self.psg_list:
			if psg.owning_player == 0: player_psgs.append(psg)
		
		if len(player_psgs) == 0:
			print 'ERROR: No player PSGs to select!'
			return
		
		# none selected yet, select the first one in the list
		if self.active_psg is None:
			self.active_psg = player_psgs[0]
			return
		
		found_current = False
		for psg in player_psgs:
			
			# we found the currently active PSG
			if self.active_psg == psg:
				found_current = True
			else:
				# we already found the active PSG and have found another, so
				#   select this one
				if found_current:
					self.active_psg = psg
					return
	
		# if we get here, we could not find a new psg to select, select the first in list
		self.active_psg = player_psgs[0]
	
	# rebuild a list of commands for the command menu based on current phase and
	#   game state
	def BuildCmdMenu(self):
		
		# clear any existing command menu
		self.cmd_menu.Clear()
		
		# don't display anything if human player is not active
		if scenario.active_player != 0:
			UpdateCmdConsole()
			return
		
		# movement phase menu - units committed to an assault can't otherwise move
		if self.active_cmd_menu == 'movement_root' and scenario.active_psg.assault_target is None:
			
			# run through six possible rotate/move directions and build commands
			for (direction, key_code, char) in MOVE_COMMANDS:
				
				if not scenario.active_psg.infantry:
					if scenario.active_psg.facing != direction:
						cmd = 'rotate_' + str(direction)
						desc = 'Face ' + char
						self.cmd_menu.AddOption(cmd, key_code, desc)
						# FUTURE: disable rotate if not allowed
						continue
				
				map_hex1 = GetHexAt(scenario.active_psg.hx, scenario.active_psg.hy)
				
				cmd = 'move_' + str(direction)
				desc = 'Move ' + char
				
				(hx, hy) = GetAdjacentHex(scenario.active_psg.hx,
					scenario.active_psg.hy, direction)
				map_hex2 = GetHexAt(hx, hy)
				
				# no map hex there
				if map_hex2 is None:
					menu_option = self.cmd_menu.AddOption(cmd, key_code, desc)
					menu_option.desc = 'Cannot move off map'
					menu_option.inactive = True
					continue
				
				# if target hex contains an enemy unit, change to assault action
				if map_hex2.IsOccupied() == 1:
					cmd = 'assault_' + str(direction)
					desc = 'Assault ' + char
					
				menu_option = self.cmd_menu.AddOption(cmd, key_code, desc)
				
				# disable move command if move not allowed or not possible
				if scenario.active_psg.suppressed:
					menu_option.desc = 'Cannot move when Suppressed'
					menu_option.inactive = True
					continue
				
				if not scenario.active_psg.CheckMoveInto(hx, hy):
					menu_option.inactive = True
					menu_option.desc = 'Cannot move into this hex'
					continue
				
				mp_cost = GetMPCostToMove(scenario.active_psg, map_hex1, map_hex2)
				if mp_cost > scenario.active_psg.mp:
					menu_option.inactive = True
					menu_option.desc = 'Not enough MP'
					
				# TODO: check that this unit could damage unit it's trying to assault
			
		# shooting phase menu
		elif self.active_cmd_menu == 'shooting_root':
			if not scenario.active_psg.fired:
				self.cmd_menu.AddOption('next_weapon', 'W', 'Next Weapon')
				self.cmd_menu.AddOption('next_target', 'T', 'Next Target')
				menu_option = self.cmd_menu.AddOption('fire_area', 'A', 'Area Fire')
				
				# Conditions under which Area Fire not Possible:
				if scenario.active_psg.selected_weapon.stats['area_strength'] == 0:
					menu_option.inactive = True
					menu_option.desc = 'Current weapon has no Area Fire attack'
				if scenario.active_psg.target_psg is None:
					menu_option.inactive = True
					menu_option.desc = 'No target selected'
				else:
					if not scenario.active_psg.target_psg.af_target:
						menu_option.inactive = True
						menu_option.desc = 'Target cannot be harmed by Area Fire attacks'
				
				menu_option = self.cmd_menu.AddOption('fire_point', 'P', 'Point Fire')
				
				# Conditions under which Point Fire not Possible:
				if scenario.active_psg.selected_weapon.stats['point_strength'] == 0:
					menu_option.inactive = True
					menu_option.desc = 'Current weapon has no Point Fire attack'
				if scenario.active_psg.target_psg is None:
					menu_option.inactive = True
					menu_option.desc = 'No target selected'
				else:
					if not scenario.active_psg.target_psg.pf_target:
						menu_option.inactive = True
						menu_option.desc = 'Target cannot be harmed by Point Fire attacks'
					# PF attacks have to be on spotted units
					elif not scenario.active_psg.target_psg.spotted:
						menu_option.inactive = True
						menu_option.desc = 'Point attacks must be against spotted targets'
		
		# both movement and shooting root menus get this commands
		if self.active_cmd_menu in ['movement_root', 'shooting_root']:
			self.cmd_menu.AddOption('select_unit', 'Tab', 'Next Unit')
			
		# all root menus get this command
		self.cmd_menu.AddOption('next_phase', 'Space', 'Next Phase')
		
		UpdateCmdConsole()



##########################################################################################
#                                     General Functions                                  #
##########################################################################################

# load terrain type definitions
def LoadTerrainTypes():
	terrain_types = []
	root = xml.parse(DATAPATH + 'terrain_type_defs.xml')
	item_list = root.findall('terrain_def')
	for item in item_list:
		new_type = TerrainType()
		new_type.display_name = item.find('display_name').text
		new_type.los_height = int(item.find('los_height').text)
		new_type.base_image = item.find('base_image').text
		new_type.af_modifier = int(item.find('af_modifier').text)
		new_type.pf_modifier = int(item.find('pf_modifier').text)
		if item.find('water') is not None:
			new_type.water = True
		if item.find('difficult') is not None:
			new_type.difficult = True
		elif item.find('very_difficult') is not None:
			new_type.very_difficult = True
		terrain_types.append(new_type)
		# set up internal stuff for this terrain type
		new_type.GenerateConsoles()
	return terrain_types


# save the current game in progress
def SaveGame():
	save = shelve.open('savegame', 'n')
	save['scenario'] = scenario
	save.close()


# load a saved game
def LoadGame():
	global scenario
	save = shelve.open('savegame')
	scenario = save['scenario']
	save.close()


# remove a saved game, either because the scenario is over or the player abandoned it
def EraseGame():
	os.remove('savegame')


# calculate an area or point fire attack
#   if at_attack is true, this is a close combat infantry attack on an armoured vehicle target,
#   and weapon is not used in calculation
def CalcAttack(attacker, weapon, target, area_fire, assume_pivot=False, at_attack=False):
	# create a new attack object
	attack_obj = Attack(attacker, weapon, target)
	
	# determine if this is an area or point fire attack
	if area_fire:
		attack_obj.area_fire = True
	else:
		attack_obj.point_fire = True
	if at_attack:
		attack_obj.at_attack = True
	
	# determine distance to target
	distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
	
	# determine base attack strength or steps firing
	if area_fire:
		attack_strength = weapon.stats['area_strength']
		if attacker.infantry:
			if distance == 1:
				attack_strength += int(ceil(attacker.num_steps / 2))
			elif distance == 0:
				attack_strength += attacker.num_steps
		else:
			attack_strength = attack_strength * attacker.num_steps
		
	else:
		attack_strength = attacker.num_steps
		if at_attack:
			attack_strength = int(ceil(attack_strength / 2))
		
	attack_obj.attack_strength = attack_strength
	
	# determine starting column
	column = 0
	for (af, pf) in FIRE_TABLE_ROWS:
		# last column
		if (af, pf) == FIRE_TABLE_ROWS[-1]:
			break
		
		# check next column
		(af2, pf2) = FIRE_TABLE_ROWS[column+1]
		
		if area_fire:
			if af2 > attack_strength:
				break
		else:
			if pf2 > attack_strength:
				break
		column += 1
	
	###################################
	# Calculate and apply column shifts
	###################################
	
	# Range Modifiers
	
	# AF range modifiers
	if attack_obj.area_fire:
		if distance == 0:
			attack_obj.column_modifiers.append(('Close Combat Range', 3))
		elif distance == 1:
			attack_obj.column_modifiers.append(('Point Blank Range', 2))
		elif distance == 2:
			attack_obj.column_modifiers.append(('Close Range', 1))
		elif distance == 4:
			attack_obj.column_modifiers.append(('Normal Range', -1))
		elif distance <= 6:
			attack_obj.column_modifiers.append(('Long Range', -2))
		elif distance <= 8:
			attack_obj.column_modifiers.append(('Very Long Range', -3))
		else:
			attack_obj.column_modifiers.append(('Extreme Range', -6))
	
	# PF range modifier
	elif not attack_obj.at_attack:
		max_range = weapon.stats['max_range']
		multipler = 0.5	
		if weapon.stats['long_range'] == 'L':
			multipler = 0.75
		elif weapon.stats['long_range'] == 'LL':
			multipler = 1.0
		normal_range = int(ceil(float(max_range) * multipler))
		close_range = int(ceil(float(normal_range) * 0.5))
		
		if distance == 0:
			attack_obj.column_modifiers.append(('Close Combat Range', -2))
		elif distance <= close_range:
			attack_obj.column_modifiers.append(('Close Range', 5))
		elif distance <= normal_range:
			attack_obj.column_modifiers.append(('Normal Range', 3))
	
	# get target terrain info
	map_hex = GetHexAt(target.hx, target.hy)
	af_modifier = map_hex.terrain_type.af_modifier
	pf_modifier = map_hex.terrain_type.pf_modifier
	
	# following only apply if not in CC
	if distance > 0:
	
		# attacker suppressed
		if attacker.suppressed:
			attack_obj.column_modifiers.append(('Attacker Suppressed', -3))	
		
		# attacker moved or changed facing
		if attacker.moved:
			attack_obj.column_modifiers.append(('Attacker Moved', -2))
		elif assume_pivot or attacker.changed_facing:
			attack_obj.column_modifiers.append(('Attacker Pivoted', -1))
		
		# PF acquired target
		if attack_obj.point_fire and attacker.acquired_target is not None:
			if attacker.acquired_target == target:
				attack_obj.column_modifiers.append(('Acquired Target', 1))
		
		# unspotted target (only possible with AF)
		if not target.spotted:
			attack_obj.column_modifiers.append(('Target Unspotted', -3))
	
		# infantry movement in no cover
		if target.infantry and target.moved and pf_modifier == 0:
			attack_obj.column_modifiers.append(('Target Moved, No Protective Cover', 2))
		
		# vehicle movement
		if target.vehicle and target.moved:
			attack_obj.column_modifiers.append(('Target Vehicle Moved', -2))
		
		# PF attack, target size modifier
		if attack_obj.point_fire:
			if target.size_class != 'Normal':
				if target.size_class == 'Very Small':
					attack_obj.column_modifiers.append(('Very Small Target', -2))
				elif target.size_class == 'Small':
					attack_obj.column_modifiers.append(('Small Target', -1))
		
		# AF attack, target has gun shield, attack in front facing
		if attack_obj.area_fire and target.gun and target.gun_shield:
			if GetFacing(attacker, target) == 'front':
				attack_obj.column_modifiers.append(('Gun Shield', -2))
	
	# AT attack modifiers
	if attack_obj.at_attack:
		# dense terrain helps infantry attacking AFVs
		if pf_modifier != 0:
			attack_obj.column_modifiers.append(('AT Attack in ' + map_hex.terrain_type.display_name,
				0 - pf_modifier))
	
	# modifiers only used in non-AT attacks
	else:
		# target terrain modifiers
		if attack_obj.area_fire:
			if af_modifier != 0:
				attack_obj.column_modifiers.append((map_hex.terrain_type.display_name,
					af_modifier))
		else:
			if pf_modifier != 0:
				attack_obj.column_modifiers.append((map_hex.terrain_type.display_name,
					pf_modifier))
	
		# Armour Modifier
		if attack_obj.point_fire and target.vehicle:
			if target.armour is not None:
				ap = weapon.stats['point_strength']
				if distance > normal_range:
					ap = int(ceil(ap / 2))
				facing = GetFacing(attacker, target)
				ap_diff = ap - target.armour[facing]
				if ap_diff > MAX_AP_DIFF: ap_diff = MAX_AP_DIFF
				if ap_diff < MIN_AP_DIFF: ap_diff = MIN_AP_DIFF
				mod = AP_MODS[ap_diff]
				text = 'AP ' + str(ap) + ' vs Armour ' + str(target.armour[facing])
				attack_obj.column_modifiers.append((text, mod))
			else:
				attack_obj.column_modifiers.append(('Unarmoured', 2))
	
	# TODO: gun shields
	
	
	# apply column modifiers
	for (text, mod) in attack_obj.column_modifiers:
		column += mod
	
	# normalize final column
	# FUTURE: if column is less than 0, no chance of effect
	if column < 0:
		column = 0
	elif column > MAX_FIRE_TABLE_COLUMN - 1:
		column = MAX_FIRE_TABLE_COLUMN - 1
		
	final_column = FIRE_TABLE[column]
	attack_obj.final_column = final_column
	
	# build list of possible final outcomes
	if attack_obj.at_attack:
		attack_obj.outcome_list.append(('2-3', 'Attacker Step Lost'))
	else:
		attack_obj.outcome_list.append((str(final_column[0]) + '+', 'Morale Check'))
	n = 1
	for result in final_column[1:]:
		# if result not possible, stop building list
		if result == 0: break
		text1 = str(result) + '+'
		text2 = str(n) + ' step loss'
		attack_obj.outcome_list.append((text1, text2))
		n+=1

	return attack_obj


# spawns a weapon and loads its stats from a given XML item
def SpawnWeapon(item):
	stats = {}
	
	# get info from weapon stat constant
	if item.text not in WEAPON_STATS:
		print 'ERROR: Could not find stats for weapon type: ' + item.text
		return
	
	stat_list = WEAPON_STATS[item.text]
	stats['name'] = stat_list[0]
	stats['long_range'] = stat_list[1]
	stats['max_range'] = stat_list[2]
	stats['area_strength'] = stat_list[3]
	stats['point_strength'] = stat_list[4]
	stats['class'] = stat_list[5]
	
	return Weapon(stats)


# load a console image from an .xp file
def LoadXP(filename):
	xp_file = gzip.open(DATAPATH + filename)
	raw_data = xp_file.read()
	xp_file.close()
	xp_data = xp_loader.load_xp_string(raw_data)
	console = libtcod.console_new(xp_data['width'], xp_data['height'])
	xp_loader.load_layer_to_console(console, xp_data['layer_data'][0])
	return console


# returns the hex object at the given hex coordinate if it exists on the map
def GetHexAt(hx, hy):
	if (hx, hy) in scenario.hex_map.hexes:
		return scenario.hex_map.hexes[(hx, hy)]
	return None


# returns the PSG located in this hex
def GetPSGAt(hx, hy):
	for psg in scenario.psg_list:
		if psg.hx == hx and psg.hy == hy:
			return psg
	return None


# returns the three orthographic grid locations on given hex edge relative to x,y
def GetEdgeTiles(x, y, direction):
	if direction == 0:
		return [(x-1,y-2), (x,y-2), (x+1,y-2)]
	elif direction == 1:
		return [(x+1,y-2), (x+2,y-1), (x+3,y)]
	elif direction == 2:
		return [(x+3,y), (x+2,y+1), (x+1,y+2)]
	elif direction == 3:
		return [(x+1,y+2), (x,y+2), (x-1,y+2)]
	elif direction == 4:
		return [(x-1,y+2), (x-2,y+1), (x-3,y)]
	elif direction == 5:
		return [(x-3,y), (x-2,y-1), (x-1,y-2)]
		

# constrain a direction to a value 0-5
def ConstrainDir(direction):
	while direction < 0:
		direction += 6
	while direction > 5:
		direction -= 6
	return direction


# combine two directions and return the result
def CombineDirs(dir1, dir2):
	direction = dir1 - dir2
	return ConstrainDir(direction)


# plot the center of a given in-game hex on the viewport console
def PlotHex(hx, hy):
	x = hx*4
	y = (hy*4) + (hx*2)
	return (x+4,y+3)


# plot an ideal hex onto an orthographic grid
# the 3000.0 acts like a resolution multiplier for the final result, seems to work for purpose
def PlotIdealHex(hx, hy):
	(x, y, z) = GetCubeCoords(hx, hy)
	sx = 3000.0 * 3.0 / 2.0 * float(x)
	sy = 3000.0 * sqrt(3) * (float(z) + (float(x) / 2.0))
	return (int(sx), int(sy))


# rotates a hex location around 0,0 clockwise r times
def RotateHex(hx, hy, r):
	# convert to cube coords
	(xx, yy, zz) = GetCubeCoords(hx, hy)
	for r in range(r):
		xx, yy, zz = -zz, -xx, -yy
	# convert back to hex coords
	return(int(xx + (zz - zz&1) / 2), zz)


# returns the adjacent hex in a given direction
def GetAdjacentHex(hx, hy, direction):
	(hx_mod, hy_mod) = DESTHEX[direction]
	return (hx+hx_mod, hy+hy_mod)


# returns a list of adjacent hexes, skipping hexes not on the game map
def GetAdjacentHexesOnMap(hx, hy):
	hex_list = []
	for d in range(6):
		(hx_mod, hy_mod) = DESTHEX[d]
		hx2 = hx+hx_mod
		hy2 = hy+hy_mod
		# hex is on the game map
		if (hx2, hy2) in scenario.hex_map.hexes:
			hex_list.append((hx2, hy2))
	return hex_list
	

# returns the direction to an adjacent hex
def GetDirectionToAdjacent(hx1, hy1, hx2, hy2):
	hx_mod = hx2 - hx1
	hy_mod = hy2 - hy1
	if (hx_mod, hy_mod) in DESTHEX:
		return DESTHEX.index((hx_mod, hy_mod))
	# hex is not adjacent
	return -1


# returns the best facing to point in the direction of the target hex
def GetDirectionToward(hx1, hy1, hx2, hy2):
	
	(x1, y1) = PlotHex(hx1, hy1)
	(x2, y2) = PlotHex(hx2, hy2)
	bearing = GetBearing(x1, y1, x2, y2)
	
	if bearing >= 330 or bearing <= 30:
		return 0
	elif bearing <= 90:
		return 1
	elif bearing >= 270:
		return 5
	elif bearing <= 150:
		return 2
	elif bearing >= 210:
		return 4
	return 3


# returns arrow character used to indicate given direction
def GetDirectionalArrow(direction):
	if direction == 0:
		return chr(24)
	elif direction == 1:
		return chr(228)
	elif direction == 2:
		return chr(229)
	elif direction == 3:
		return chr(25)
	elif direction == 4:
		return chr(230)
	elif direction == 5:
		return chr(231)
	print 'ERROR: Direction not recognized: ' + str(direction)
	return ''


# transforms an hx, hy hex location to cube coordinates
def GetCubeCoords(hx, hy):
	x = int(hx - (hy - hy&1) / 2)
	z = hy
	y = 0 - hx - z
	return (x, y, z)


# returns distance in hexes between two hexes
def GetHexDistance(hx1, hy1, hx2, hy2):
	(x1, y1, z1) = GetCubeCoords(hx1, hy1)
	(x2, y2, z2) = GetCubeCoords(hx2, hy2)
	return int((abs(x1-x2) + abs(y1-y2) + abs(z1-z2)) / 2)
	

# return a list of hexes along a line from hex1 to hex2
# adapted from http://www.redblobgames.com/grids/hexagons/implementation.html#line-drawing
# TODO: not used at present, might be useful later on?
def GetHexLine(hx1, hy1, hx2, hy2):
	
	def Lerp(a, b, t):
		a = float(a)
		b = float(b)
		return a + (b - a) * t
	
	def CubeRound(x, y, z):
		rx = round(x)
		ry = round(y)
		rz = round(z)
		x_diff = abs(rx - x)
		y_diff = abs(ry - y)
		z_diff = abs(rz - z)
		if x_diff > y_diff and x_diff > z_diff:
			rx = 0 - ry - rz
		elif y_diff > z_diff:
			ry = 0 - rx - rz
		else:
			rz = 0 - rx - ry
		return (int(rx), int(ry), int(rz))

	# get cube coordinates and distance between start and end hexes
	# (repeated here from GetHexDistance because we need more than just the distance)
	(x1, y1, z1) = GetCubeCoords(hx1, hy1)
	(x2, y2, z2) = GetCubeCoords(hx2, hy2)
	distance = int((abs(x1-x2) + abs(y1-y2) + abs(z1-z2)) / 2)
	
	hex_list = []
	
	for i in range(distance+1):
		t = 1.0 / float(distance) * float(i)
		x = Lerp(x1, x2, t)
		y = Lerp(y1, y2, t)
		z = Lerp(z1, z2, t)
		(x,y,z) = CubeRound(x,y,z)
		# convert from cube to hex coordinates and add to list
		hex_list.append((x, z))

	return hex_list


# returns a ring of hexes around a center point for a given radius
# NOTE: may include hex locations that are not actually part of the game map
# TODO: improve this
def GetHexRing(hx, hy, radius):
	hex_list = []
	if radius == 0: return hex_list
	# get starting point
	hx -= radius
	hy += radius
	direction = 0
	for hex_side in range(6):
		for hex_steps in range(radius):
			hex_list.append((hx, hy))
			(hx, hy) = GetAdjacentHex(hx, hy, direction)
		direction += 1
	return hex_list


# returns all hexes within radius of given hex location, not including the location itself
# does not return hexes that are not part of the game map
def GetHexesWithin(hx, hy, radius):
	hex_list = []
	for d in range(1, radius+1):
		ring_list = GetHexRing(hx, hy, d)
		for (hx1, hy1) in ring_list:
			if (hx1, hy1) not in scenario.hex_map.hexes: continue
			hex_list.append((hx1, hy1))
	return hex_list


# returns a rectangular area of hexes with given width and height,
#  hx, hy being the top left corner hex
def GetHexRect(hx, hy, w, h):
	hex_list = []
	for x in range(w):
		# run down hex column
		for y in range(h):
			hex_list.append((hx, hy))
			hy += 1
		# move to new column
		hy -= h
		if hx % 2 == 0:
			# even -> odd column, direction 2
			direction = 2
		else:
			# odd -> even column, direction 1
			direction = 1
		(hx, hy) = GetAdjacentHex(hx, hy, direction)
	return hex_list


# calculate the MP required to move into the target hex
# most units have 12 MP max, fast tanks have 16
def GetMPCostToMove(psg, map_hex1, map_hex2):
	
	# check if linked by road
	road = False
	direction = GetDirectionToAdjacent(map_hex1.hx, map_hex1.hy, map_hex2.hx, map_hex2.hy)
	if direction in map_hex1.dirt_road_links:
		road = True
	
	if psg.movement_class == 'Infantry':
		if road:
			cost = 4
		else:
			cost = 6
	
	elif psg.movement_class == 'Wheeled':
		if road:
			cost = 2
		elif map_hex2.terrain_type.difficult:
			cost = 12
		else:
			cost = 4
	
	elif psg.movement_class in ['Slow Tank', 'Tank', 'Fast Tank']:
		if road:
			cost = 3
		elif map_hex2.terrain_type.difficult:
			cost = 6
		else:
			cost = 4
	
	elif psg.movement_class == 'Slow Tank':
		cost = 6

	return cost
	


# returns a path from one hex to another, avoiding impassible and difficult terrain
# based on function from ArmCom 1, which was based on:
# http://stackoverflow.com/questions/4159331/python-speed-up-an-a-star-pathfinding-algorithm
# http://www.policyalmanac.org/games/aStarTutorial.htm
def GetHexPath(hx1, hy1, hx2, hy2, movement_class=None, road_path=False):
	
	# retrace a set of nodes and return the best path
	def RetracePath(end_node):
		path = []
		node = end_node
		done = False
		while not done:
			path.append((node.hx, node.hy))
			if node.parent is None: break	# we've reached the end
			node = node.parent	
		path.reverse()
		return path
	
	# clear any old pathfinding info
	for key, map_hex in scenario.hex_map.hexes.iteritems():
		map_hex.ClearPathInfo()
	
	node1 = GetHexAt(hx1, hy1)
	node2 = GetHexAt(hx2, hy2)
	open_list = set()	# contains the nodes that may be traversed by the path
	closed_list = set()	# contains the nodes that will be traversed by the path
	start = node1
	start.h = GetHexDistance(node1.hx, node1.hy, node2.hx, node2.hy)
	start.f = start.g + start.h
	end = node2
	open_list.add(start)		# add the start node to the open list
	last_good_node = None
	
	while open_list:
		
		# grab the node with the best H value from the list of open nodes
		current = sorted(open_list, key=lambda inst:inst.f)[0]
		
		# we've reached our destination
		if current == end:
			return RetracePath(current)
		
		# move this node from the open to the closed list
		open_list.remove(current)
		closed_list.add(current)
		
		# add the nodes connected to this one to the open list
		for direction in range(6):
			
			# get the hex coordinates in this direction
			hx, hy = GetAdjacentHex(current.hx, current.hy, direction)
			
			# no map hex in this direction
			if (hx, hy) not in scenario.hex_map.hexes: continue
			
			node = GetHexAt(hx, hy)
			
			# ignore nodes on closed list
			if node in closed_list: continue
			
			# ignore impassible nodes
			if node.terrain_type.water: continue
			
			# TODO: calculate movement cost
			if movement_class is not None:
				cost = 1
			
			# we're creating a path for a road
			elif road_path:
				
				# prefer to use already-existing roads
				if direction in current.dirt_road_links:
					cost = -5
				
				# prefer to pass through villages if possible
				if node.terrain_type.display_name == 'Wooden Village':
					cost = -5
				elif node.terrain_type.difficult:
					cost = 5
				else:
					cost = 3
				
				if node.elevation > current.elevation:
					cost = cost * 3
				
			g = current.g + cost
			
			# if not in open list, add it
			if node not in open_list:
				node.g = g
				node.h = GetHexDistance(node.hx, node.hy, node2.hx, node2.hy)
				node.f = node.g + node.h
				node.parent = current
				open_list.add(node)
			# if already in open list, check to see if can make a better path
			else:
				if g < node.g:
					node.parent = current
					node.g = g
					node.f = node.g + node.h
	
	# no path possible
	#print 'GetHexPath() Error: No path possible'
	return []

# Bresenham's Line Algorithm (based on an implementation on the roguebasin wiki)
# returns a series of x, y points along a line
# if los is true, does not include the starting location in the line
def GetLine(x1, y1, x2, y2, los=False):
	points = []
	issteep = abs(y2-y1) > abs(x2-x1)
	if issteep:
		x1, y1 = y1, x1
		x2, y2 = y2, x2
	rev = False
	if x1 > x2:
		x1, x2 = x2, x1
		y1, y2 = y2, y1
		rev = True
	deltax = x2 - x1
	deltay = abs(y2-y1)
	error = int(deltax / 2)
	y = y1
	
	if y1 < y2:
		ystep = 1
	else:
		ystep = -1
	for x in range(x1, x2 + 1):
		if issteep:
			points.append((y, x))
		else:
			points.append((x, y))
		error -= deltay
		if error < 0:
			y += ystep
			error += deltax
			
	# Reverse the list if the coordinates were reversed
	if rev:
		points.reverse()
	
	# chop off the first location if we're doing line of sight
	if los and len(points) > 1:
		points = points[1:]
	
	return points


# return the end point of a line starting from x,y with length l and angle a
# NOT USED RIGHT NOW BUT MAY BE USEFUL IN FUTURE
#def PlotLine(x1, y1, l, a):
#	a = RectifyHeading(a-90)
#	x2 = int(x1 + (l * cos(a*PI/180.0)))
#	y2 = int(y1 + (l * sin(a*PI/180.0))) 
#	return (x2, y2)


# wait for a specified amount of miliseconds, refreshing the screen in the meantime
def Wait(wait_time):
	# added this to avoid the spinning wheel of death in Windows
	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
	libtcod.sys_sleep_milli(wait_time)
	# emergency exit
	if libtcod.console_is_window_closed(): sys.exit()


# wait for player to press enter before continuing
# option to allow backspace pressed instead, returns True if so 
# TODO: keep updating animations while waiting
def WaitForEnter(allow_cancel=False):
	end_pause = False
	cancel = False
	while not end_pause:
		# get input from user
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		
		# emergency exit from game
		if libtcod.console_is_window_closed():
			sys.exit()
		
		elif key.vk == libtcod.KEY_ENTER: 
			end_pause = True
		
		elif key.vk == libtcod.KEY_BACKSPACE and allow_cancel:
			end_pause = True
			cancel = True
		
		# refresh the screen
		libtcod.console_flush()
	
	# wait for key to be released
	while libtcod.console_is_key_pressed(libtcod.KEY_ENTER) or libtcod.console_is_key_pressed(libtcod.KEY_BACKSPACE):
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		libtcod.console_flush()
	
	if allow_cancel and cancel:
		return True
	return False


# get a confirmation from the player that they really want to do this
def GetConfirmation(text):
	
	lines = wrap(text, 20)
	y = WINDOW_YM - int(len(lines) / 2)
	libtcod.console_set_default_background(0, libtcod.darker_red)
	libtcod.console_rect(0, 30, y-1, 22, len(lines)+4, True, libtcod.BKGND_SET)
	libtcod.console_set_default_background(0, libtcod.black)
	for line in lines:
		libtcod.console_print_ex(0, WINDOW_XM, y, libtcod.BKGND_NONE,
			libtcod.CENTER, line)
		y += 1
	y += 1
	libtcod.console_set_default_foreground(0, HIGHLIGHT_COLOR)
	libtcod.console_print(0, 32, y, 'Enter')
	libtcod.console_print(0, 43, y, 'ESC')
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_print(0, 38, y, 'Yes')
	libtcod.console_print(0, 47, y, 'No')
	
	exit_menu = False
	while not exit_menu:
		
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		if libtcod.console_is_window_closed(): return False
		if key is None: continue
		if key.vk == libtcod.KEY_ENTER:
			return True
		elif key.vk == libtcod.KEY_ESCAPE:
			return False


# return the result of a 2D6 roll
def Roll2D6():
	d1 = libtcod.random_get_int(0, 1, 6)
	d2 = libtcod.random_get_int(0, 1, 6)
	return d1, d2, (d1+d2)


# returns a heading from 0-359 degrees
def RectifyHeading(h):
	while h < 0: h += 360
	while h > 359: h -= 360
	return h


# returns the compass bearing from x1, y1 to x2, y2
def GetBearing(x1, y1, x2, y2):
	return int((degrees(atan2((y2 - y1), (x2 - x1))) + 90.0) % 360)


# assuming an observer in hx1, hy1 looking at hx2, hy2, returns a list of visible hexes
# along this line of sight
# used in HexMap.CalcFoV() and psg.SelectNextTarget()
def GetLoS(hx1, hy1, hx2, hy2):
	
	# handle same hex and adjacent hex cases first
	if hx1 == hx2 and hy1 == hy2:
		return [(hx1, hy1)]
	distance = GetHexDistance(hx1, hy1, hx2, hy2)
	if distance == 1:
		return [(hx1, hy1), (hx2, hy2)]
	
	# build list of hexes along LoS first
	hex_list = []
	
	# lines of sight along hex spines need a special procedure
	(x1, y1) = PlotIdealHex(hx1, hy1)
	(x2, y2) = PlotIdealHex(hx2, hy2)
	los_bearing = GetBearing(x1, y1, x2, y2)
	
	mod_list = None
	if los_bearing in [30, 90, 150, 210, 270, 330]:
		mod_list = HEXSPINES[los_bearing]
		
		# start with first hex
		hx = hx1
		hy = hy1
		
		while hx != hx2 or hy != hy2:
			# break if we've gone off map
			if (hx, hy) not in scenario.hex_map.hexes: break
			
			# emergency escape in case of stuck loop
			if libtcod.console_is_window_closed(): sys.exit()
			
			# add the next three hexes to the list
			for (xm, ym) in mod_list:
				new_hx = hx + xm
				new_hy = hy + ym
				hex_list.append((new_hx, new_hy))
			(hx, hy) = hex_list[-1]
	
	else:
		hex_list = GetHexLine(hx1, hy1, hx2, hy2)
		# remove first hex in list, since this is the observer's hex
		hex_list.pop(0)
	
	# now that list is built, step through the list, checking elevations along the way
	# add visible hexes to a final list
	visible_hexes = []
	observer_elevation = float(GetHexAt(hx1, hy1).elevation)
	los_slope = None
	
	# run through the list of hexes, starting with the first adjacent one from observer
	hexpair = None
	hexpair_elevation = 0
	for (hx, hy) in hex_list:
		
		if (hx, hy) not in scenario.hex_map.hexes:
			continue
		if GetHexDistance(hx1, hy1, hx, hy) > MAX_LOS_DISTANCE:
			continue
		
		map_hex = scenario.hex_map.hexes[(hx, hy)]
		elevation = (float(map_hex.elevation) - observer_elevation) * ELEVATION_M
		
		# if we're on a hexspine, we need to compare some pairs of hexes
		if mod_list is not None:
			index = hex_list.index((hx, hy))
			# hexes 0,3,6... are stored for comparison
			if index % 3 == 0:
				hexpair = (hx, hy)
				hexpair_elevation = elevation
				continue
			# hexes 1,4,7... are compared with stored value
			elif (index - 1) % 4 == 0:
				if hexpair_elevation < elevation:
					elevation = hexpair_elevation
		
		# calculate slope from observer to floor of this hex and to terrain top
		floor_slope = elevation / float(GetHexDistance(hx1, hy1, hx, hy)) * 160.0
		terrain_top_slope = (elevation + float(map_hex.terrain_type.los_height)) / float(GetHexDistance(hx1, hy1, hx, hy)) * 160.0
		
		# determine visibility
		
		# if this is an adjacent hex, it's automatically visible
		if los_slope is None:
			visible_hexes.append((hx, hy))
			# use the terrain top for future visibility
			los_slope = terrain_top_slope
		
		# otherwise, compare against current LoS slope
		else:
			if floor_slope >= los_slope:
				visible_hexes.append((hx, hy))
				# if hexspine, check for also making first part of a hexpair
				# visible as well
				if hexpair is not None:
					visible_hexes.append(hexpair)
					hexpair = None
		
			# if terrain top slope is larger than previous los_slope, replace
			if terrain_top_slope > los_slope:
				los_slope = terrain_top_slope

	return visible_hexes


# get the bearing from psg1 to psg2, rotated for psg1's facing
def GetRelativeBearing(psg1, psg2):
	(x1, y1) = PlotHex(psg1.hx, psg1.hy)
	(x2, y2) = PlotHex(psg2.hx, psg2.hy)
	bearing = GetBearing(x1, y1, x2, y2)
	return RectifyHeading(bearing - (psg1.facing * 60))


# get the relative facing of one PSG from the pov of another PSG
# psg1 is the observer, psg2 is being observed
def GetFacing(attacker, target):
	bearing = GetRelativeBearing(target, attacker)
	if bearing >= 300 or bearing <= 60:
		return 'front'
	return 'side'


# initiate an attack by one PSG on another
def InitAttack(attacker, weapon, target, area_fire, at_attack=False):
	
	distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
	
	# determine if a pivot would be required
	pivot_required = False
	if not attacker.infantry and distance > 0:
		bearing = GetRelativeBearing(attacker, target)
		if 30 < bearing < 330:
			pivot_required = True

	# send information to CalcAttack, which will return an Attack object with the
	#   calculated stats to use for the attack
	attack_obj = CalcAttack(attacker, weapon, target, area_fire,
		assume_pivot=pivot_required, at_attack=at_attack)
	
	# do the pivot if it was required
	if pivot_required:
		direction = GetDirectionToward(attacker.hx, attacker.hy, target.hx,
			target.hy)
		attacker.PivotToFace(direction)
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_blit(attack_con, 0, 0, 0, 0, 0, 0, 3)
		libtcod.console_flush()
	
	# if not close combat and player wasn't attacker, display LoS from attacker to target
	if distance > 0 and attacker.owning_player == 1:
		line = GetLine(attacker.screen_x, attacker.screen_y, target.screen_x,
			target.screen_y)
		for (x,y) in line[2:-2]:
			libtcod.console_set_char(0, x, y, 250)
			libtcod.console_set_char_foreground(0, x, y, libtcod.red)
			libtcod.console_flush()
			libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
			Wait(15)
	
	# display attack console for this attack
	DisplayAttack(attack_obj)
	
	cancel_attack = WaitForEnter(allow_cancel=True)
	
	# player has chance to cancel a ranged attack at this point
	if attacker.owning_player == 0 and distance > 0 and cancel_attack:
		return
	
	# set fired flag and clear the selected target
	attacker.fired = True
	attacker.target_psg = None
	
	# clear any LoS drawn above from screen, but keep attack console visible
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	libtcod.console_blit(attack_con, 0, 0, 0, 0, 0, 0, 3)
	libtcod.console_flush()
	
	# display appropriate attack animation
	if not at_attack:
		if weapon.stats['class'] == 'gun':
			GunAttackAnimation(attack_obj)
		elif weapon.stats['class'] == 'mg':
			MGAttackAnimation(attack_obj)
	
	# resolve attack
	target.ResolveAttack(attack_obj)
	
	# clear attacker's selected weapon
	attacker.selected_weapon = None
	
	# handle newly acquired target
	if distance > 0 and not area_fire:
		if attacker.acquired_target is None:
			attacker.acquired_target = target
			target.acquired_by.append(attacker)
		else:
			# attacker had a different acquired target
			if attacker.acquired_target != target:
				for psg in scenario.psg_list:
					if attacker in psg.acquired_by:
						psg.acquired_by.remove(attacker)
				attacker.acquired_target = target
				target.acquired_by.append(attacker)
	
	# check for spotting changes as a result of this attack
	scenario.DoSpotCheck()


# display the factors and odds for an attack on the screen
def DisplayAttack(attack_obj):
	libtcod.console_clear(attack_con)
	
	# display the background outline
	temp = LoadXP('ArmCom2_attack_bkg.xp')
	libtcod.console_blit(temp, 0, 0, 0, 0, attack_con, 0, 0)
	del temp
	
	# title
	libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR)
	libtcod.console_rect(attack_con, 1, 1, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 13, 1, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Attack Resolution')
	
	if attack_obj.at_attack:
		text = 'Anti-Tank'
	elif attack_obj.area_fire:
		text = 'Area Fire'
	else:
		text = 'Point Fire'
	text += ' attack by'
	libtcod.console_print_ex(attack_con, 13, 3, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	text = attack_obj.attacker.GetName()
	libtcod.console_print_ex(attack_con, 13, 4, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	if attack_obj.at_attack:
		text = 'against'
	else:
		text = 'firing ' + attack_obj.weapon.stats['name'] + ' at'
	libtcod.console_print_ex(attack_con, 13, 5, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	libtcod.console_print_ex(attack_con, 13, 6, libtcod.BKGND_NONE,
		libtcod.CENTER, attack_obj.target.GetName())
	
	# base firepower or steps firing
	libtcod.console_rect(attack_con, 1, 8, 24, 1, False, libtcod.BKGND_SET)
	if attack_obj.area_fire:
		text = 'Total Firepower: '
	else:
		text = 'Steps Firing: '
	text += str(attack_obj.attack_strength)
	libtcod.console_print_ex(attack_con, 13, 8, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	# list of column shift modifiers
	libtcod.console_rect(attack_con, 1, 10, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 13, 10, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Attack Modifiers')
	y = 12
	if len(attack_obj.column_modifiers) == 0:
		libtcod.console_print_ex(attack_con, 13, y, libtcod.BKGND_NONE,
			libtcod.CENTER, 'None')
	for (text, mod) in attack_obj.column_modifiers:
		
		lines = wrap(text, 18, subsequent_indent = ' ')
		for line in lines:
			libtcod.console_print(attack_con, 2, y, line)
			y += 1
		y -= 1
		mod_text = str(mod)
		if mod > 0: mod_text = '+' + mod_text
		libtcod.console_print_ex(attack_con, 23, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, mod_text)
		y += 1
	
	# list of final possible outcomes
	libtcod.console_rect(attack_con, 1, 31, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 13, 31, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Possible Results')
	
	y = 33
	for (text1, text2) in attack_obj.outcome_list:
		libtcod.console_print(attack_con, 2, y, text1)
		libtcod.console_print_ex(attack_con, 23, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text2)
		y += 1
	
	distance = GetHexDistance(attack_obj.attacker.hx, attack_obj.attacker.hy,
		attack_obj.target.hx, attack_obj.target.hy)
	if attack_obj.attacker.owning_player == 0 and distance > 0:
		libtcod.console_print_ex(attack_con, 13, 53, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Backspace to Cancel')
	libtcod.console_print_ex(attack_con, 13, 54, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Enter to Roll')
	
	libtcod.console_set_default_background(attack_con, libtcod.black)
	
	# display console on screen
	libtcod.console_blit(attack_con, 0, 0, 0, 0, 0, 0, 3)
	libtcod.console_flush()


# draw a representation of a die face to the console
def DrawDie(console, x, y, d):
	libtcod.console_blit(dice, 0+((d-1)*3), 0, 3, 3, console, x, y)
	

# fill the hex map with terrain
def GenerateTerrain():
	
	def ShowTerrainGeneration():
		if not SHOW_TERRAIN_GEN: return
		libtcod.console_clear(0)
		UpdateMapTerrainConsole()
		libtcod.console_blit(map_terrain_con, 0, 0, 0, 0, 0, 26, 3)
		libtcod.console_flush()
		Wait(500)
	
	# try to create a road from one edge of the map to the other
	def CreateRoad(vertical=True):
		
		road_finished = False
		while not road_finished:
		
			if vertical:
				hex_list1 = scenario.hex_map.bottom_edge_hexes
				hex_list2 = scenario.hex_map.top_edge_hexes
			else:
				hex_list1 = scenario.hex_map.left_edge_hexes
				hex_list2 = scenario.hex_map.right_edge_hexes
			
			# select start and end hexes
			good_hex = False
			while not good_hex:
				(hx1, hy1) = choice(hex_list1)
				map_hex = GetHexAt(hx1, hy1)
				if not map_hex.terrain_type.water:
					good_hex = True
			
			good_hex = False
			while not good_hex:
				(hx2, hy2) = choice(hex_list2)
				map_hex = GetHexAt(hx2, hy2)
				if not map_hex.terrain_type.water:
					good_hex = True
				
			path = GetHexPath(hx1, hy1, hx2, hy2, road_path=True)
			
			# no path was possible
			if len(path) == 0:
				continue
			
			# create the road
			for n in range(len(path)):
				(hx1, hy1) = path[n]
				if n+1 < len(path):
					hx2, hy2 = path[n+1]
					direction = GetDirectionToAdjacent(hx1, hy1, hx2, hy2)
					map_hex = GetHexAt(hx1, hy1)
					map_hex.dirt_road_links.append(direction)
					
					direction = GetDirectionToAdjacent(hx2, hy2, hx1, hy1)
					map_hex = GetHexAt(hx2, hy2)
					map_hex.dirt_road_links.append(direction)
					
					if SHOW_TERRAIN_GEN:
						libtcod.console_clear(0)
						UpdateMapTerrainConsole()
						libtcod.console_blit(map_terrain_con, 0, 0, 0, 0, 0, 26, 3)
						libtcod.console_flush()
						Wait(80)
			
			road_finished = True
	
	
	# create a local list of all hx, hy locations in map
	map_hex_list = []
	for key, map_hex in scenario.hex_map.hexes.iteritems():
		map_hex_list.append((map_hex.hx, map_hex.hy))
	
	
	# clear map
	for (hx, hy) in map_hex_list:
		map_hex = GetHexAt(hx, hy)
		map_hex.SetTerrainType('Fields')
		map_hex.SetElevation(1)
		map_hex.dirt_road_links = []
	
	ShowTerrainGeneration()
	
	##################################################################################
	#                                 Elevation                                      #
	##################################################################################
	
	# FUTURE: will used and will be supplied by battleground settings
	#smoothness = 0.9
	
	for terrain_pass in range(3):
		hex_list = []
		
		# determine upper left corner, width, and height of hill area
		(hx_start, hy_start) = choice(map_hex_list)
		hill_width = libtcod.random_get_int(0, 3, 6)
		hill_height = libtcod.random_get_int(0, 3, 6)
		hx_start -= int(hill_width / 2)
		hy_start -= int(hill_height / 2)
		
		# get a rectangle of hex locations
		hex_rect = GetHexRect(hx_start, hy_start, hill_width, hill_height)
		
		# determine how many points to use for hill generation
		min_points = int(len(hex_rect) / 10)
		max_points = int(len(hex_rect) / 3)
		hill_points = libtcod.random_get_int(0, min_points, max_points)
		
		# build a list of hill locations around random points
		for i in range(hill_points):
			(hx, hy) = choice(hex_rect)
			hex_list.append((hx, hy))
			for direction in range(6):
				hex_list.append(GetAdjacentHex(hx, hy, direction))
		
		# apply the hill locations if they are on map
		for (hx, hy) in hex_list:
			map_hex = GetHexAt(hx, hy)
			if map_hex is not None:
				map_hex.SetElevation(2)
		
	ShowTerrainGeneration()
	
	##################################################################################
	#                                  Forests                                       #
	##################################################################################
	
	# must be 2+
	forest_size = 6
	
	for terrain_pass in range(4):
		hex_list = []
		(hx_start, hy_start) = choice(map_hex_list)
		width = libtcod.random_get_int(0, 1, forest_size-1)
		height = forest_size - width
		hx_start -= int(width / 2)
		hy_start -= int(height / 2)
		
		# get a rectangle of hex locations
		hex_rect = GetHexRect(hx_start, hy_start, width, height)
		
		# apply forest locations if they are on map
		for (hx, hy) in hex_rect:
			map_hex = GetHexAt(hx, hy)
			if map_hex is not None:
				# small chance of gaps in area
				if libtcod.random_get_int(0, 1, 15) == 1:
					continue
				map_hex.SetTerrainType('Sparse Forest')
	ShowTerrainGeneration()
	
	##################################################################################
	#                                 Villages                                       #
	##################################################################################
	
	d1, d2, roll = Roll2D6()
	
	if roll <= 3:
		num_villages = 4
	elif roll <= 5:
		num_villages = 3
	elif roll <= 7:
		num_villages = 2
	elif roll <= 10:
		num_villages = 1
	else:
		num_villages = 0
	
	for terrain_pass in range(num_villages):
		# determine size of village in hexes: 1,1,1,2,3 hexes total
		village_size = libtcod.random_get_int(0, 1, 5) - 2
		if village_size < 1: village_size = 1
		
		# find centre of village
		shuffle(map_hex_list)
		for (hx, hy) in map_hex_list:
			map_hex = GetHexAt(hx, hy)
			if map_hex.terrain_type.display_name == 'Sparse Forest':
				continue
			map_hex.SetTerrainType('Wooden Village')
			
			# handle large villages; if extra hexes fall off map they won't
			#  be added
			if village_size > 1:
				for extra_hex in range(village_size-1):
					(hx2, hy2) = GetAdjacentHex(hx, hy, libtcod.random_get_int(0, 0, 5))
					map_hex = GetHexAt(hx2, hy2)
					if map_hex is not None:
						map_hex.SetTerrainType('Wooden Village')
				
			break
	ShowTerrainGeneration()
	
	##################################################################################
	#                                Tall Fields                                     #
	##################################################################################
	
	for terrain_pass in range(4):
		hex_list = []
		(hx_start, hy_start) = choice(map_hex_list)
		width = libtcod.random_get_int(0, 2, 4)
		height = libtcod.random_get_int(0, 2, 4)
		hx_start -= int(width / 2)
		hy_start -= int(height / 2)
		
		# get a rectangle of hex locations
		hex_rect = GetHexRect(hx_start, hy_start, width, height)
		
		# apply forest locations if they are on map
		for (hx, hy) in hex_rect:
			map_hex = GetHexAt(hx, hy)
			if map_hex is not None:
				
				# don't overwrite villages
				if map_hex.terrain_type.display_name == 'Wooden Village':
					continue
				# small chance of overwriting forest
				if map_hex.terrain_type.display_name == 'Sparse Forest':
					if libtcod.random_get_int(0, 1, 10) <= 9:
						continue
				map_hex.SetTerrainType('Tall Fields')
	ShowTerrainGeneration()
	
	##################################################################################
	#                                   Ponds                                        #
	##################################################################################
	
	num_ponds = libtcod.random_get_int(0, 0, 4)
	for terrain_pass in range(num_ponds):
		shuffle(map_hex_list)
		for (hx, hy) in map_hex_list:
			map_hex = GetHexAt(hx, hy)
			if map_hex.terrain_type.display_name != 'Fields':
				continue
			if map_hex.elevation != 1:
				continue
			map_hex.SetTerrainType('Pond')
			break
	if num_ponds > 0:
		ShowTerrainGeneration()
	
	##################################################################################
	#                                   Roads                                        #
	##################################################################################
	
	# add two roads
	CreateRoad()
	CreateRoad(vertical=False)
	
	ShowTerrainGeneration()



##########################################################################################
#                                 Scenario Animations                                    #
##########################################################################################

# TODO: combine into one function

# display a gun projectile fire animation
def GunAttackAnimation(attack_obj):
	
	# use draw locations, but we'll be drawing to the GUI console so modify
	x1, y1 = attack_obj.attacker.screen_x-26, attack_obj.attacker.screen_y-3
	x2, y2 = attack_obj.target.screen_x-26, attack_obj.target.screen_y-3
	
	# projectile animation
	line = GetLine(x1, y1, x2, y2, los=True)
	
	pause_time = config.getint('ArmCom2', 'animation_speed') * 3
	pause_time2 = int(pause_time / 2)
	
	for (x, y) in line:
		UpdateGUIConsole()
		libtcod.console_put_char_ex(map_gui_con, x, y, 250, libtcod.white, libtcod.black)
		DrawScreenConsoles()
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 3)
		libtcod.console_flush()
		Wait(pause_time)
	
	# final explosion animation
	(x,y) = line[-1]
	for i in range(10):
		UpdateGUIConsole()
		col = choice([libtcod.red, libtcod.yellow, libtcod.grey])
		libtcod.console_put_char_ex(map_gui_con, x, y, '*',
			col, libtcod.black)
		DrawScreenConsoles()
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 3)
		libtcod.console_flush()
		Wait(pause_time2)
		
	libtcod.console_clear(map_gui_con)
	DrawScreenConsoles()
	libtcod.console_flush()


# display an MG fire animation
def MGAttackAnimation(attack_obj):
	
	# use draw locations, but we'll be drawing to the GUI console so modify
	x1, y1 = attack_obj.attacker.screen_x-26, attack_obj.attacker.screen_y-3
	x2, y2 = attack_obj.target.screen_x-26, attack_obj.target.screen_y-3
	
	line = GetLine(x1, y1, x2, y2, los=True)
	
	pause_time = config.getint('ArmCom2', 'animation_speed') * 2
	
	for i in range(20):
		(x,y) = choice(line[:-1])
		libtcod.console_clear(map_gui_con)
		libtcod.console_put_char_ex(map_gui_con, x, y, 250, libtcod.red, libtcod.black)
		DrawScreenConsoles()
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 3)
		libtcod.console_flush()
		Wait(pause_time)
	
	libtcod.console_clear(map_gui_con)
	DrawScreenConsoles()
	libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 3)
	libtcod.console_flush()


# display an animated message overtop the map viewport
def Message(x, y, text):
	
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0)
	lines = wrap(text, 16)
	
	# reposition messages that would appear off-screen
	if x < 30:
		x = 30
	if x > WINDOW_WIDTH - 8:
		x = WINDOW_WIDTH - 8
	if y < 6:
		y = 6
	elif y+len(lines) > WINDOW_HEIGHT - 2:
		y = WINDOW_HEIGHT - 2 - len(lines)
	
	n = 1
	for line in lines:
		libtcod.console_print_ex(0, x, y+n, libtcod.BKGND_SET, libtcod.CENTER, line)
		n+=1
	libtcod.console_flush()
	Wait(config.getint('ArmCom2', 'message_pause_time'))
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0)
	libtcod.console_flush()


# draw the map terrain console
# each hex is 5x5 cells, but edges overlap with adjacent hexes
# also record the console cells covered by this hex depiction
def UpdateMapTerrainConsole():
	libtcod.console_set_default_background(map_terrain_con, libtcod.black)
	libtcod.console_clear(map_terrain_con)
	
	for elevation in range(4):
		for (hx, hy) in scenario.hex_map.hexes:
			map_hex = GetHexAt(hx, hy)
			if map_hex.elevation != elevation: continue
			(x,y) = PlotHex(hx, hy)
			h_con = map_hex.terrain_type.console[map_hex.elevation]
			libtcod.console_blit(h_con, 0, 0, 0, 0, map_terrain_con, x-3, y-2)
			
			for x1 in range(x-1, x+2):
				scenario.map_index[(x1,y-1)] = (hx, hy)
				scenario.map_index[(x1,y+1)] = (hx, hy)
			for x1 in range(x-2, x+3):
				scenario.map_index[(x1,y)] = (hx, hy)
	
	# draw roads and rivers overtop
	for key, map_hex in scenario.hex_map.hexes.items():
		
		# river edges		
		#if map_hex.river_edges:
	
		#	(x,y) = PlotHex(map_hex.hx, map_hex.hy)
			
		#	for map_hex2 in map_hex.river_edges:
		#		direction = GetDirectionToAdjacent(map_hex.hx, map_hex.hy, map_hex2.hx, map_hex2.hy)
		#		for (rx,ry) in GetEdgeTiles(x, y, direction):
		#			libtcod.console_set_char_background(map_terrain_con, rx, ry, RIVER_BG_COL, flag=libtcod.BKGND_SET)
		
		# dirt roads
		if len(map_hex.dirt_road_links) > 0:
			
			for direction in map_hex.dirt_road_links:
				
				# paint road
				(x1, y1) = PlotHex(map_hex.hx, map_hex.hy)
				(x2, y2) = GetEdgeTiles(x1, y1, direction)[1]
				
				line = GetLine(x1, y1, x2, y2)
				for (x, y) in line:
					libtcod.console_set_char_background(map_terrain_con, x, y, DIRT_ROAD_COL, libtcod.BKGND_SET)
					
					# if character is not blank or hex edge, remove it
					if libtcod.console_get_char(map_terrain_con, x, y) not in [0, 250]:
						libtcod.console_set_char(map_terrain_con, x, y, 0)


# draw the Field of View overlay for the player, darkening map hexes that are not currently visible
def UpdateMapFoVConsole():
	libtcod.console_clear(map_fov_con)
	temp = LoadXP('ArmCom2_tile_fov.xp')
	libtcod.console_set_key_color(temp, libtcod.black)
	for (hx, hy) in scenario.hex_map.hexes:
		map_hex = GetHexAt(hx, hy)
		if map_hex.vis_to_player:
			(x,y) = PlotHex(hx, hy)
			libtcod.console_blit(temp, 0, 0, 0, 0, map_fov_con, x-3, y-2)
	del temp


# updates the map viewport gui layer
def UpdateGUIConsole():
	libtcod.console_clear(map_gui_con)
	
	# highlight objective hexes
	for map_hex in scenario.objective_hexes:
		(x,y) = PlotHex(map_hex.hx, map_hex.hy)
		if map_hex.held_by is None:
			col = NEUTRAL_OBJ_COL
		else:
			if map_hex.held_by == 0:
				col = FRIENDLY_OBJ_COL
			else:
				col = ENEMY_OBJ_COL
		for (xm,ym) in [(-2, -1),(-2, 1),(2, -1),(2, 1)]:
			libtcod.console_put_char_ex(map_gui_con, x+xm, y+ym, 249, col,
				libtcod.black)
	
	# show assaults
	for psg in scenario.psg_list:
		if psg.assault_target is not None:
			(hx, hy) = psg.assault_target
			direction = GetDirectionToAdjacent(psg.hx, psg.hy, hx, hy)
			char = GetDirectionalArrow(direction)
			(x, y) = PlotHex(psg.hx, psg.hy)
			tile_list = GetEdgeTiles(x, y, direction)
			for (x,y) in tile_list:
				libtcod.console_put_char_ex(map_gui_con, x, y, char,
					libtcod.red, libtcod.black)
		

# run through active PSGs and draw them to the unit console
def UpdateUnitConsole():
	libtcod.console_clear(unit_con)
	for psg in scenario.psg_list:
		psg.DrawMe()


# updates the selected PSG info console
def UpdatePSGConsole():
	libtcod.console_clear(psg_con)
	
	if scenario.active_psg is None:
		return
	
	# create a local pointer to the currently active PSG
	psg = scenario.active_psg
	
	# PSG name
	libtcod.console_print(psg_con, 0, 0, psg.GetName())
	
	# unit type
	libtcod.console_set_default_foreground(psg_con, HIGHLIGHT_COLOR)
	libtcod.console_print(psg_con, 0, 1, psg.GetStepName())
	libtcod.console_set_default_foreground(psg_con, libtcod.white)
	
	# number of steps in unit
	text = 'x' + str(psg.num_steps)
	libtcod.console_print_ex(psg_con, 23, 1, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	
	# vehicle portrait
	libtcod.console_set_default_background(psg_con, PORTRAIT_BG_COL)
	libtcod.console_rect(psg_con, 0, 2, 24, 8, False, libtcod.BKGND_SET)
	libtcod.console_set_default_background(psg_con, libtcod.black)
	
	if psg.portrait is not None:
		temp = LoadXP(psg.portrait)
		if temp is not None:
			x = 13 - int(libtcod.console_get_width(temp) / 2)
			libtcod.console_blit(temp, 0, 0, 0, 0, psg_con, x, 2)
		else:
			print 'ERROR: unit portrait not found: ' + psg.portrait
	
	# unit special skills
	libtcod.console_set_default_foreground(psg_con, libtcod.black)
	if psg.recce:
		libtcod.console_print(psg_con, 0, 2, 'Recce')
	
	libtcod.console_set_default_foreground(psg_con, libtcod.white)
	
	# morale and skill levels
	libtcod.console_set_default_background(psg_con, libtcod.dark_grey)
	libtcod.console_rect(psg_con, 0, 10, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print(psg_con, 0, 10, MORALE_DESC[str(psg.morale_lvl)])
	libtcod.console_print_ex(psg_con, 23, 10, libtcod.BKGND_NONE, libtcod.RIGHT,
		SKILL_DESC[str(psg.skill_lvl)])
	
	# weapon list
	# TODO: only show max three, allow scrolling
	libtcod.console_set_default_foreground(psg_con, libtcod.grey)
	libtcod.console_print_ex(psg_con, 23, 11, libtcod.BKGND_NONE, libtcod.RIGHT,
		'Rng AF PF')
	libtcod.console_set_default_foreground(psg_con, libtcod.white)
	y = 12
	libtcod.console_set_default_background(psg_con, HIGHLIGHT_BG_COLOR)
	
	for weapon in psg.weapon_list:
		libtcod.console_set_default_background(psg_con, WEAPON_LIST_COLOR)
		# highlight selected weapon if in shooting phase
		if scenario.GetCurrentPhase() == 'Shooting' and psg.selected_weapon is not None:
			if weapon == psg.selected_weapon:
				libtcod.console_set_default_background(psg_con, SELECTED_WEAPON_COLOR)
		libtcod.console_rect(psg_con, 0, y, 24, 1, False, libtcod.BKGND_SET)
		libtcod.console_print(psg_con, 0, y, weapon.stats['name'])
		text = str(weapon.stats['max_range']) + weapon.stats['long_range']
		libtcod.console_print_ex(psg_con, 17, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
		if weapon.stats['area_strength'] == 0:
			text = '-'
		else:
			text = str(weapon.stats['area_strength'])
		libtcod.console_print_ex(psg_con, 20, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
		if weapon.stats['point_strength'] == 0:
			text = '-'
		else:
			text = str(weapon.stats['point_strength'])
		libtcod.console_print_ex(psg_con, 23, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
		y += 1
	
	# armour ratings if any
	if psg.armour:
		text = ('Armour ' + str(psg.armour['front']) + '/' + str(psg.armour['side']))
		libtcod.console_print(psg_con, 0, 16, text)
	
	# Movement class
	libtcod.console_set_default_foreground(psg_con, libtcod.green)
	libtcod.console_print_ex(psg_con, 23, 16, libtcod.BKGND_NONE,
		libtcod.RIGHT, psg.movement_class)
	
	# display MP if in movement phase
	if scenario.GetCurrentPhase() == 'Movement':
		text = str(psg.mp) + '/' + str(psg.max_mp) + ' MP'
		libtcod.console_print_ex(psg_con, 23, 17, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
	
	# status flags
	libtcod.console_set_default_foreground(psg_con, libtcod.lighter_blue)
	libtcod.console_set_default_background(psg_con, HIGHLIGHT_BG_COLOR)
	libtcod.console_rect(psg_con, 0, 19, 24, 1, False, libtcod.BKGND_SET)
	
	# movement- and position-related flags
	if psg.moved:
		libtcod.console_print(psg_con, 0, 19, 'Moved')
	elif psg.changed_facing:
		libtcod.console_print(psg_con, 0, 19, 'Changed Facing')
	
	# fired last turn
	if psg.fired:
		libtcod.console_print_ex(psg_con, 23, 19, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'Fired')
	
	# negative statuses
	libtcod.console_set_default_foreground(psg_con, libtcod.light_red)
	libtcod.console_set_default_background(psg_con, libtcod.darkest_red)
	libtcod.console_rect(psg_con, 0, 20, 24, 1, False, libtcod.BKGND_SET)
	
	if psg.pin_points > 0:
		libtcod.console_print(psg_con, 0, 20, 'Pin Pts: ' + str(psg.pin_points))
	if psg.suppressed:
		libtcod.console_print_ex(psg_con, 23, 20, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'Suppressed')
	
	libtcod.console_set_default_foreground(psg_con, libtcod.white)
	libtcod.console_set_default_background(psg_con, libtcod.black)


# updates the command console
def UpdateCmdConsole():
	libtcod.console_clear(cmd_con)
	libtcod.console_set_default_background(cmd_con, HIGHLIGHT_BG_COLOR)
	libtcod.console_rect(cmd_con, 0, 0, 24, 2, False, libtcod.BKGND_SET)
	if scenario.active_player == 0:
		text = 'Player'
	else:
		text = 'Enemy'
	text += ' Turn'
	libtcod.console_print_ex(cmd_con, 12, 0, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	text = scenario.GetCurrentPhase()
	libtcod.console_print_ex(cmd_con, 12, 1, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	libtcod.console_set_default_background(cmd_con, libtcod.black)
	scenario.cmd_menu.DisplayMe(cmd_con, 0, 3, 24)


# draw scenario info to the scenario info console
def UpdateScenInfoConsole():
	libtcod.console_clear(scen_info_con)
	
	# scenario name and time remaining
	libtcod.console_set_default_foreground(scen_info_con, HIGHLIGHT_COLOR)
	libtcod.console_print(scen_info_con, 0, 0, scenario.name)
	libtcod.console_set_default_foreground(scen_info_con, libtcod.light_grey)
	hr = scenario.hour_limit - scenario.hour
	mr = scenario.minute_limit - scenario.minute
	if mr < 0:
		hr -= 1
		mr += 60
	text = '-' + str(hr) + ':' + str(mr).zfill(2)
	libtcod.console_print(scen_info_con, 0, 1, text)
	
	# scenario battlefront, current and time
	libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
	libtcod.console_print_ex(scen_info_con, 42, 0, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.battlefront)
	text = MONTH_NAMES[scenario.month] + ' ' + str(scenario.year)
	libtcod.console_print_ex(scen_info_con, 42, 1, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	text = str(scenario.hour) + ':' + str(scenario.minute).zfill(2)
	libtcod.console_print_ex(scen_info_con, 42, 2, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	
	# TODO: pull wind and weather info from scenario object
	text = 'No Wind, Clear'
	libtcod.console_print_ex(scen_info_con, 82, 0, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	
	# TODO: pull light and visibility info from scenario object
	text = ''
	libtcod.console_print_ex(scen_info_con, 82, 1, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)


# update the map hex info console based on current mouse location
def UpdateHexInfoConsole():
	libtcod.console_clear(hex_info_con)
	
	# mouse cursor outside of map area
	if mouse.cx < 26: return
	
	x = mouse.cx - 26
	y = mouse.cy - 3
	
	if (x,y) in scenario.map_index:
		(hx, hy) = scenario.map_index[(x,y)]
		map_hex = GetHexAt(hx, hy)
		
		# coordinates and elevation
		text = str(map_hex.hx) + ',' + str(map_hex.hy) + ':'
		elevation = int(map_hex.terrain_type.los_height + (map_hex.elevation * ELEVATION_M))
		text += str(elevation) + 'm'
		libtcod.console_print(hex_info_con, 0, 0, text)
		
		# objective status
		if map_hex.objective:
			libtcod.console_print_ex(hex_info_con, 23, 0, libtcod.BKGND_NONE,
				libtcod.RIGHT, 'Objective')

		# hex terrain type
		libtcod.console_print(hex_info_con, 0, 1, map_hex.terrain_type.display_name)

		# road status
		if len(map_hex.dirt_road_links) > 0:
			libtcod.console_print_ex(hex_info_con, 23, 1, libtcod.BKGND_NONE,
				libtcod.RIGHT, 'Dirt Road')
		
		# PSG present
		for psg in scenario.psg_list:
			if psg.hx == map_hex.hx and psg.hy == map_hex.hy:
				if psg.owning_player == 1:
					libtcod.console_set_default_foreground(hex_info_con, libtcod.red)
				else:
					libtcod.console_set_default_foreground(hex_info_con, HIGHLIGHT_COLOR)
				
				lines = wrap(psg.GetName(), 23)
				n = 0
				for line in lines[:2]:
					libtcod.console_print(hex_info_con, 0, 3+n, line)
					n += 1
				libtcod.console_set_default_foreground(hex_info_con, libtcod.white)
				
				if psg.owning_player == 1 and not psg.spotted:
					return

				# name of squads/vehicles and number of steps in PSG
				text = psg.GetStepName() + ' x' + str(psg.num_steps)
				libtcod.console_print(hex_info_con, 0, 3+n, text)
				
				if psg.suppressed:
					libtcod.console_print(hex_info_con, 0, 6, 'Suppressed')
				if not psg.spotted:
					libtcod.console_print_ex(hex_info_con, 23, 6,
						libtcod.BKGND_NONE, libtcod.RIGHT,
						'Unspotted')
				return
		

# layer the display consoles onto the screen
def DrawScreenConsoles():
	libtcod.console_clear(con)
	
	# map viewport layers
	libtcod.console_blit(bkg_console, 0, 0, 0, 0, con, 0, 3)		# grey outline
	libtcod.console_blit(map_terrain_con, 0, 0, 0, 0, con, 26, 3)		# map terrain
	libtcod.console_blit(map_fov_con, 0, 0, 0, 0, con, 26, 3, 0.7, 0.7)	# map FoV overlay
	libtcod.console_blit(unit_con, 0, 0, 0, 0, con, 26, 3, 1.0, 0.0)	# map unit layer
	libtcod.console_blit(map_gui_con, 0, 0, 0, 0, con, 26, 3, 1.0, 0.0)	# map GUI layer

	# highlight selected PSG if any
	# TODO: integrate into GUI console?
	if scenario.active_psg is not None:
		libtcod.console_set_char_background(con, scenario.active_psg.screen_x,
			scenario.active_psg.screen_y, SELECTED_HL_COL, flag=libtcod.BKGND_SET)
		
		# only highlight hex if not in move animation
		if scenario.active_psg.anim_x == 0 and scenario.active_psg.anim_y == 0:
		
			for (xm, ym) in HEX_EDGE_TILES:
				x = scenario.active_psg.screen_x+xm
				y = scenario.active_psg.screen_y+ym
				if libtcod.console_get_char(con, x, y) == 250:
					libtcod.console_set_char_foreground(con, x, y, SELECTED_HL_COL)
	
		# highlight targeted PSG if any
		psg = scenario.active_psg.target_psg
		if psg is not None:
			libtcod.console_set_char_background(con, psg.screen_x, psg.screen_y,
				TARGET_HL_COL, flag=libtcod.BKGND_SET)
			
			# TEMP - show LoS hexes
			#los_line = GetLoS(scenario.active_psg.hx, scenario.active_psg.hy,
			#	psg.hx, psg.hy)
			
			#for (hx, hy) in los_line:
			#	(x,y) = PlotHex(hx, hy)
			#	x += 26
			#	y += 3
			#	libtcod.console_set_char(con, x, y, 250)
			#	libtcod.console_set_char_foreground(con, x, y, libtcod.red)
			
			# draw LoS line
			line = GetLine(scenario.active_psg.screen_x, scenario.active_psg.screen_y,
				psg.screen_x, psg.screen_y)
			for (x, y) in line[2:-1]:
				libtcod.console_set_char(con, x, y, 250)
				libtcod.console_set_char_foreground(con, x, y, libtcod.red)
	
	libtcod.console_blit(anim_con, 0, 0, 0, 0, con, 26, 3, 1.0, 0.0)	# animation layer
	
	# left column consoles
	libtcod.console_blit(psg_con, 0, 0, 0, 0, con, 1, 4)
	libtcod.console_blit(cmd_con, 0, 0, 0, 0, con, 1, 26)
	libtcod.console_blit(hex_info_con, 0, 0, 0, 0, con, 1, 52)
	
	# scenario info
	libtcod.console_blit(scen_info_con, 0, 0, 0, 0, con, 0, 0)
	
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)


##########################################################################################
#                                     In-Game Menus                                      #
##########################################################################################

# display a summary of the scenario in progress or about to be started
def ScenarioSummary():
	# use the buffer console to darken the screen background
	libtcod.console_clear(con)
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0, 
		0.0, 0.7)
	# load menu background
	temp = LoadXP('ArmCom2_scen_summary.xp')
	libtcod.console_set_default_foreground(temp, libtcod.white)
	libtcod.console_set_default_background(temp, libtcod.black)
	
	# display scenario information
	libtcod.console_print_ex(temp, 14, 1, libtcod.BKGND_NONE, libtcod.CENTER,
		'Scenario')
	libtcod.console_set_default_foreground(temp, HIGHLIGHT_COLOR)
	libtcod.console_print_ex(temp, 14, 2, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.name)
	libtcod.console_set_default_foreground(temp, libtcod.white)
	
	# scenario description
	lines = wrap(scenario.description, 25)
	n = 0
	for line in lines:
		libtcod.console_print(temp, 2, 5+n, line)
		n += 1
	
	# battlefront, date, and start time
	libtcod.console_print_ex(temp, 14, 20, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.battlefront)
	text = MONTH_NAMES[scenario.month] + ' ' + str(scenario.year)
	libtcod.console_print_ex(temp, 14, 21, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	text = str(scenario.hour) + ':' + str(scenario.minute).zfill(2)
	libtcod.console_print_ex(temp, 14, 22, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	
	# forces on both sides
	# TODO: this info should be part of scenario object as well
	libtcod.console_set_default_foreground(temp, HIGHLIGHT_COLOR)
	libtcod.console_print(temp, 2, 25, 'Your Forces')
	libtcod.console_print(temp, 2, 31, 'Expected Resistance')
	libtcod.console_set_default_foreground(temp, libtcod.white)
	libtcod.console_print(temp, 3, 26, 'German Heer')
	libtcod.console_print(temp, 3, 27, 'Armoured Battlegroup')
	libtcod.console_print(temp, 3, 32, 'Polish Army')
	libtcod.console_print(temp, 3, 33, 'Armoured and Infantry')
	
	# objectives
	libtcod.console_set_default_foreground(temp, HIGHLIGHT_COLOR)
	libtcod.console_print(temp, 2, 38, 'Objectives')
	libtcod.console_set_default_foreground(temp, libtcod.white)
	text = (scenario.objectives + ' by ' + str(scenario.hour_limit) + ':' +
		str(scenario.minute_limit).zfill(2))
	lines = wrap(text, 25)
	n = 0
	for line in lines:
		libtcod.console_print(temp, 2, 40+n, line)
		n += 1
	
	# list of menu commands
	libtcod.console_set_default_foreground(temp, HIGHLIGHT_COLOR)
	libtcod.console_print(temp, 2, 52, 'ESC')
	libtcod.console_print(temp, 16, 52, 'Enter')
	libtcod.console_set_default_foreground(temp, libtcod.white)
	libtcod.console_print(temp, 6, 52, 'Cancel')
	libtcod.console_print(temp, 22, 52, 'Start')
	
	libtcod.console_blit(temp, 0, 0, 0, 0, 0, 26, 3)
	del temp
	
	exit_menu = False
	while not exit_menu:
		
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		if libtcod.console_is_window_closed(): return False
		if key is None: continue
		if key.vk == libtcod.KEY_ENTER:
			return True
		elif key.vk == libtcod.KEY_ESCAPE:
			return False
	

# display the root scenario menu
def ScenarioMenu():
	
	def UpdateScreen():
		libtcod.console_blit(scen_menu_con, 0, 0, 0, 0, con, 5, 3)
		cmd_menu.DisplayMe(con, WINDOW_XM-12, 24, 25)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	# darken the screen background
	libtcod.console_blit(darken_con, 0, 0, 0, 0, con, 0, 0, 0.0, 0.7)
	
	# build menu of basic options
	cmd_menu = CommandMenu('scenario_menu')
	cmd_menu.AddOption('save_and_quit', 'Q', 'Save and Quit', desc='Save the scenario ' +
		'in progress and quit to main menu')
	cmd_menu.AddOption('return', 'Esc', 'Return to Scenario', desc='Return and continue ' +
		'playing the scenario in progress')
	cmd_menu.AddOption('abandon', 'A', 'Abandon Scenario', desc='Abandon the scenario ' +
		'in progress, erasing saved game, and quit to main menu')
	
	UpdateScreen()
	
	exit_menu = False
	while not exit_menu:
		
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		if key is None: continue
		
		# select previous or next menu option
		if key.vk == libtcod.KEY_UP:
			cmd_menu.SelectNextOption(reverse=True)
			UpdateScreen()
			continue
			
		elif key.vk == libtcod.KEY_DOWN:
			cmd_menu.SelectNextOption()
			UpdateScreen()
			continue
		
		# activate selected menu option
		elif key.vk == libtcod.KEY_ENTER:
			option = cmd_menu.GetSelectedOption()
		
		# see if we pressed a key associated with a menu option
		else:
			option = cmd_menu.GetOptionByKey()
		
		if option is None: continue
		
		# select this option and highlight it
		cmd_menu.selected_option = option
		UpdateScreen()
		libtcod.console_flush()
		
		# selected an inactive menu option
		if option.inactive: continue
		
		if option.option_id == 'save_and_quit':
			SaveGame()
			return True
		elif option.option_id == 'return':
			return False
		elif option.option_id == 'abandon':
			text = ('Are you sure? This will erase the currently saved scenario ' +
				'in progress')
			if GetConfirmation(text):
				EraseGame()
				return True
			UpdateScreen()
		

def DoScenario(load_savegame=False):
	
	global scenario, terrain_types
	# screen consoles
	global scen_menu_con, bkg_console, map_terrain_con, map_fov_con, map_gui_con
	global unit_con, psg_con, anim_con, cmd_con, attack_con, scen_info_con
	global hex_info_con, grey_hex_con
	global dice
	
	def UpdateScreen():
		UpdateMapFoVConsole()
		UpdateUnitConsole()
		UpdateGUIConsole()
		UpdatePSGConsole()
		UpdateCmdConsole()
		DrawScreenConsoles()
	
	# create screen consoles
	
	# background console
	bkg_console = LoadXP('ArmCom2_bkg.xp')
	
	# main menu console
	scen_menu_con = LoadXP('ArmCom2_menu.xp')
	libtcod.console_set_default_background(scen_menu_con, libtcod.black)
	libtcod.console_set_default_foreground(scen_menu_con, libtcod.white)
	libtcod.console_print_ex(scen_menu_con, 37, 2, libtcod.BKGND_NONE, libtcod.CENTER,
		VERSION + SUBVERSION)
	
	# map terrain console
	map_terrain_con = libtcod.console_new(57, 57)
	libtcod.console_set_default_background(map_terrain_con, libtcod.black)
	libtcod.console_set_default_foreground(map_terrain_con, libtcod.white)
	libtcod.console_clear(map_terrain_con)
	
	# field of view overlay console
	map_fov_con = libtcod.console_new(57, 57)
	libtcod.console_set_default_background(map_fov_con, libtcod.black)
	libtcod.console_set_default_foreground(map_fov_con, libtcod.white)
	libtcod.console_set_key_color(map_fov_con, KEY_COLOR)
	libtcod.console_clear(map_fov_con)
	
	# map gui console
	map_gui_con = libtcod.console_new(57, 57)
	libtcod.console_set_default_background(map_gui_con, KEY_COLOR)
	libtcod.console_set_default_foreground(map_gui_con, libtcod.white)
	libtcod.console_set_key_color(map_gui_con, KEY_COLOR)
	libtcod.console_clear(map_gui_con)
	
	# unit layer console
	unit_con = libtcod.console_new(57, 57)
	libtcod.console_set_default_background(unit_con, KEY_COLOR)
	libtcod.console_set_default_foreground(unit_con, libtcod.grey)
	libtcod.console_set_key_color(unit_con, KEY_COLOR)
	libtcod.console_clear(unit_con)
	
	# animation layer console
	anim_con = libtcod.console_new(57, 57)
	libtcod.console_set_default_background(anim_con, KEY_COLOR)
	libtcod.console_set_default_foreground(anim_con, libtcod.grey)
	libtcod.console_set_key_color(anim_con, KEY_COLOR)
	libtcod.console_clear(anim_con)
	
	# top banner scenario info console
	scen_info_con = libtcod.console_new(83, 3)
	libtcod.console_set_default_background(scen_info_con, libtcod.black)
	libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
	libtcod.console_clear(scen_info_con)
	
	# selected PSG info console
	psg_con = libtcod.console_new(24, 21)
	libtcod.console_set_default_background(psg_con, libtcod.black)
	libtcod.console_set_default_foreground(psg_con, libtcod.white)
	libtcod.console_clear(psg_con)
	
	# command menu console
	cmd_con = libtcod.console_new(24, 25)
	libtcod.console_set_default_background(cmd_con, libtcod.black)
	libtcod.console_set_default_foreground(cmd_con, libtcod.white)
	libtcod.console_clear(cmd_con)
	
	# map hex info console
	hex_info_con = libtcod.console_new(24, 7)
	libtcod.console_set_default_background(hex_info_con, libtcod.black)
	libtcod.console_set_default_foreground(hex_info_con, libtcod.white)
	libtcod.console_clear(hex_info_con)
	
	# attack resolution console
	attack_con = libtcod.console_new(26, 57)
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.white)
	libtcod.console_clear(attack_con)

	# load grey tile to indicate tiles that aren't visible to the player
	grey_hex_con = LoadXP('ArmCom2_tile_grey.xp')
	libtcod.console_set_key_color(grey_hex_con, KEY_COLOR)

	# die face image
	dice = LoadXP('dice.xp')
	
	# load terrain type definitions
	terrain_types = LoadTerrainTypes()
	
	# here is where a saved game in-progress would be loaded
	if load_savegame:
		LoadGame()
		# reset pointers to terrain consoles for each map hex
		# (needed because consoles can't be pickled)
		for map_key, map_hex in scenario.hex_map.hexes.iteritems():
			map_hex.SetTerrainType(map_hex.terrain_type.display_name)
		UpdateMapTerrainConsole()
	
	else:
	
		##################################################################################
		#                            Start a new Scenario                                #
		##################################################################################
		
		# create a new campaign day object and hex map
		scenario = Scenario(13, 13)
		GenerateTerrain()
		
		# FUTURE: following will be handled by a Scenario Generator
		# for now, things are set up manually
		scenario.battlefront = 'Western Poland'
		scenario.name = 'Spearhead'
		scenario.description = ('Your forces have broken through enemy lines, ' +
			'and are advancing to capture strategic objectives before the ' +
			'defenders have a chance to react.')
		scenario.objectives = 'Capture & Hold all objectives'
		scenario.year = 1939
		scenario.month = 9
		scenario.hour = 5
		scenario.minute = 0
		scenario.hour_limit = 12
		scenario.minute_limit = 0
		
		# display scenario info: chance to cancel scenario start
		if not ScenarioSummary():
			del scenario
			return
		
		# spawn the player PSGs
		new_psg = SpawnPSG('HQ Panzer Squadron', 'Panzer 35t', 5)
		new_psg.owning_player = 0
		new_psg.facing = 0
		new_psg.skill_lvl = 5
		new_psg.morale_lvl = 5
		new_psg.PlaceAt(5, 10)
		
		new_psg = SpawnPSG('Panzer Squadron', 'Panzer 35t', 5)
		new_psg.owning_player = 0
		new_psg.facing = 0
		new_psg.skill_lvl = 5
		new_psg.morale_lvl = 5
		new_psg.PlaceAt(4, 10)
		
		new_psg = SpawnPSG('Light Panzer Squadron', 'Panzer II A', 5)
		new_psg.owning_player = 0
		new_psg.facing = 0
		new_psg.skill_lvl = 5
		new_psg.morale_lvl = 5
		new_psg.PlaceAt(6, 9)
		
		new_psg = SpawnPSG('Light Panzerspäh Platoon', 'psw_221', 3)
		new_psg.owning_player = 0
		new_psg.facing = 0
		new_psg.skill_lvl = 5
		new_psg.morale_lvl = 5
		new_psg.PlaceAt(7, 9)
		
		new_psg = SpawnPSG('Schützen Platoon', 'german_schutzen', 5)
		new_psg.owning_player = 0
		new_psg.facing = 0
		new_psg.skill_lvl = 4
		new_psg.morale_lvl = 5
		new_psg.PlaceAt(8, 8)
		
		
		# select the first player PSG
		scenario.SelectNextPSG()
		
		# set up our objectives
		scenario.hex_map.AddObjectiveAt(5, 4)
		scenario.hex_map.AddObjectiveAt(6, -2)
		
		# generate enemy OOB and spawn into map
		scenario.GenerateEnemyOOB()
		
		# do initial objective capture
		for map_hex in scenario.objective_hexes:
			map_hex.CheckCapture(no_message=True)
	
		# draw map terrain
		UpdateMapTerrainConsole()
		# calculate initial field of view
		scenario.hex_map.CalcFoV()
		UpdateMapFoVConsole()
		
		# build initial command menu
		scenario.active_cmd_menu = 'movement_root'
		scenario.BuildCmdMenu()
		
		UpdateScreen()
		
		# do initial spot check
		scenario.DoSpotCheck()
		
		
	
	# TODO: End new game set-up
	
	UpdateScenInfoConsole()
	UpdateScreen()
	SaveGame()
	
	##################################################################################
	#     Main Campaign Day Loop
	##################################################################################

	# to trigger when mouse cursor has moved on screen
	mouse_x = -1
	mouse_y = -1
	
	exit_scenario = False
	while not exit_scenario:
		
		if scenario.anim.Update():
			DrawScreenConsoles()
		
		libtcod.console_flush()
	
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			key, mouse)
		
		# emergency loop escape
		if libtcod.console_is_window_closed(): sys.exit()
		
		# check to see if mouse cursor has moved
		if mouse.cx != mouse_x or mouse.cy != mouse_y:
			mouse_x = mouse.cx
			mouse_y = mouse.cy
			UpdateHexInfoConsole()
			DrawScreenConsoles()
		
		##### Mouse Commands #####
		if mouse.lbutton:
			x = mouse.cx - 26
			y = mouse.cy - 3
			if (x,y) in scenario.map_index:
				(hx, hy) = scenario.map_index[(x,y)]
				for psg in scenario.psg_list:
					if psg.owning_player == 1: continue
					if psg.hx == hx and psg.hy == hy:
						scenario.active_psg = psg
						UpdatePSGConsole()
						scenario.BuildCmdMenu()
						DrawScreenConsoles()
						continue
		
		#elif mouse.rbutton:
		
		# open scenario menu screen
		if key.vk == libtcod.KEY_ESCAPE:
			if ScenarioMenu():
				exit_scenario = True
			else:
				DrawScreenConsoles()
			continue
		
		# check for scenario end
		if scenario.winner is not None:
			exit_scenario = True
			continue
		
		##### AI Actions #####
		if scenario.active_player == 1:
			scenario.DoAIPhase()
			scenario.NextPhase()
			UpdateScreen()
			continue
		
		##### Automatic Phase Actions #####
		if scenario.GetCurrentPhase() == 'Close Combat':
			scenario.ResolveCloseCombats()
			scenario.NextPhase()
			UpdateScreen()
			continue
		
		##### Player Keyboard Commands #####
		
		# skip this section if no commands in buffer
		if key is None: continue
		
		##################################################################
		
		# DEBUG command
		if SHOW_TERRAIN_GEN:
			key_char = chr(key.c).lower()
			if key_char == 'g':
				GenerateTerrain()
				scenario.hex_map.CalcFoV()
				UpdateMapFoVConsole()
				UpdateScreen()
				continue
		
		##################################################################
		
		# select previous or next menu option
		if key.vk == libtcod.KEY_UP:
			scenario.cmd_menu.SelectNextOption(reverse=True)
			UpdateScreen()
			continue
			
		elif key.vk == libtcod.KEY_DOWN:
			scenario.cmd_menu.SelectNextOption()
			UpdateScreen()
			continue
		
		# activate selected menu option
		elif key.vk == libtcod.KEY_ENTER:
			option = scenario.cmd_menu.GetSelectedOption()
		
		# see if key is in current menu options
		else:
			option = scenario.cmd_menu.GetOptionByKey()
		
		# no option selected
		if option is None: continue
		
		# select this option, highlight it
		scenario.cmd_menu.selected_option = option
		UpdateScreen()
		libtcod.console_flush()
		
		# selected an inactive menu option
		if option.inactive: continue
		
		##################################################################
		# Root Menu Actions
		##################################################################
		if option.option_id == 'select_unit':
			scenario.SelectNextPSG()
			UpdatePSGConsole()
			scenario.BuildCmdMenu()
			DrawScreenConsoles()
		elif option.option_id == 'next_phase':
			scenario.NextPhase()
			DrawScreenConsoles()
		
		##################################################################
		# Movement Phase Actions
		##################################################################
		elif option.option_id[:5] == 'move_':
			# get the target map hex
			direction = int(option.option_id[5])
			(hx, hy) = GetAdjacentHex(scenario.active_psg.hx,
				scenario.active_psg.hy, direction)
			# attempt the move
			if scenario.active_psg.MoveInto(hx, hy):
				scenario.BuildCmdMenu()
				UpdateScreen()
		elif option.option_id[:7] == 'rotate_':
			direction = int(option.option_id[7])
			scenario.active_psg.PivotToFace(direction)
			scenario.BuildCmdMenu()
			UpdateScreen()
		elif option.option_id[:8] == 'assault_':
			# TODO: get confirmation from player
			direction = int(option.option_id[8])
			(hx, hy) = GetAdjacentHex(scenario.active_psg.hx,
				scenario.active_psg.hy, direction)
			scenario.active_psg.assault_target = (hx, hy)
			scenario.active_psg.moved = True
			scenario.BuildCmdMenu()
			UpdateGUIConsole()
			DrawScreenConsoles()
		
		##################################################################
		# Shooting Phase Actions
		##################################################################
		elif option.option_id == 'next_weapon':
			scenario.active_psg.SelectNextWeapon()
			# clear target list
			scenario.active_psg.target_list = []
			scenario.active_psg.target_psg = None
			UpdatePSGConsole()
			# rebuild command menu for newly selected weapon
			scenario.BuildCmdMenu()
			DrawScreenConsoles()
		elif option.option_id == 'next_target':
			scenario.active_psg.SelectNextTarget()
			scenario.BuildCmdMenu()
			DrawScreenConsoles()
		elif option.option_id[:5] == 'fire_':
			area_fire = False
			if option.option_id[5:] == 'area':
				area_fire = True
			InitAttack(scenario.active_psg, scenario.active_psg.selected_weapon,
				scenario.active_psg.target_psg, area_fire)
			UpdatePSGConsole()
			scenario.BuildCmdMenu()
			DrawScreenConsoles()

	# we're exiting back to the main menu, so delete the scenario object
	del scenario


# try to load game settings from config file
def LoadCFG():
	
	global config
	
	config = ConfigParser.RawConfigParser()
	
	# create a new config file
	if not os.path.exists(DATAPATH + 'armcom2.cfg'):
		
		config.add_section('ArmCom2')
		config.set('ArmCom2', 'large_display_font', 'true')
		config.set('ArmCom2', 'message_pause_time', '700')
		config.set('ArmCom2', 'animation_speed', '30')
		
		# write to disk
		with open(DATAPATH + 'armcom2.cfg', 'wb') as configfile:
			config.write(configfile)
		print 'ArmCom2: No config file found, created a new one'
	
	else:
		# load config file
		config.read(DATAPATH + 'armcom2.cfg')

# save current config to file
def SaveCFG():
	with open(DATAPATH + 'armcom2.cfg', 'wb') as configfile:
		config.write(configfile)



##########################################################################################
#                                       Main Script                                      #
##########################################################################################

global config
global mouse, key, con, darken_con

# try to load game settings from config file
LoadCFG()

# center window on screen
os.putenv('SDL_VIDEO_CENTERED', '1')

# determine font to use based on settings file
if config.getboolean('ArmCom2', 'large_display_font'):
	fontname = 'c64_16x16.png'
else:
	fontname = 'c64_8x8.png'
libtcod.console_set_custom_font(DATAPATH+fontname, libtcod.FONT_LAYOUT_ASCII_INROW,
	0, 0)

libtcod.console_init_root(WINDOW_WIDTH, WINDOW_HEIGHT, NAME + ' - ' + VERSION + SUBVERSION,
	fullscreen = False, renderer = libtcod.RENDERER_GLSL)
libtcod.sys_set_fps(LIMIT_FPS)
libtcod.console_set_keyboard_repeat(0, 0)

# set defaults for screen console
libtcod.console_set_default_background(0, libtcod.black)
libtcod.console_set_default_foreground(0, libtcod.white)
libtcod.console_clear(0)

# main double buffer console
con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(con, libtcod.black)
libtcod.console_set_default_foreground(con, libtcod.white)
libtcod.console_clear(con)

# darken screen console
darken_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(darken_con, libtcod.black)
libtcod.console_set_default_foreground(darken_con, libtcod.black)
libtcod.console_clear(darken_con)

libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER,
	'Loading ...')
libtcod.console_flush()

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()


##########################################################################################
#                                        Main Menu                                       #
##########################################################################################

# generate main menu console
main_menu_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(main_menu_con, libtcod.black)
libtcod.console_set_default_foreground(main_menu_con, libtcod.white)
libtcod.console_clear(main_menu_con)
main_menu_image = LoadXP('ArmCom2_title.xp')
tank_image = LoadXP('unit_pz_II.xp')
libtcod.console_blit(tank_image, 0, 0, 20, 8, main_menu_image, 5, 6)
del tank_image

libtcod.console_blit(main_menu_image, 0, 0, 88, 60, main_menu_con, 0, 0)
libtcod.console_set_default_foreground(main_menu_con, libtcod.black)
libtcod.console_print_ex(main_menu_con, WINDOW_WIDTH-1, 0, libtcod.BKGND_NONE, libtcod.RIGHT,
	VERSION + SUBVERSION)

libtcod.console_set_default_foreground(main_menu_con, libtcod.red)
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-17,
	libtcod.BKGND_NONE, libtcod.CENTER, 'NOTE: This is an incomplete, proof-of-concept version')
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-16,
	libtcod.BKGND_NONE, libtcod.CENTER, 'intended only to demonstrate the core gameplay of the game')

libtcod.console_set_default_foreground(main_menu_con, libtcod.light_grey)
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-4,
	libtcod.BKGND_NONE, libtcod.CENTER, 'Copyright 2016-2017')
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-3,
	libtcod.BKGND_NONE, libtcod.CENTER, 'Free Software under the GNU GPL')
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-2,
	libtcod.BKGND_NONE, libtcod.CENTER, 'www.armouredcommander.com')

libtcod.console_set_default_foreground(main_menu_con, libtcod.white)

# build main menus
menus = []

cmd_menu = CommandMenu('main_menu')
cmd_menu.AddOption('continue_scenario', 'C', 'Continue')
cmd_menu.AddOption('new_scenario', 'N', 'New')
cmd_menu.AddOption('options', 'O', 'Options')
cmd_menu.AddOption('quit', 'Q', 'Quit')
menus.append(cmd_menu)

cmd_menu = CommandMenu('settings_menu')
cmd_menu.AddOption('toggle_font_size', 'F', 'Toggle Font/Window Size',
	desc='Switch between 8px and 16px font size')
cmd_menu.AddOption('select_msg_speed', 'M', 'Select Message Pause Time',
	desc='Change how long messages are displayed before being cleared')
cmd_menu.AddOption('select_ani_speed', 'A', 'Select Animation Speed',
	desc='Change the display speed of in-game animations')
cmd_menu.AddOption('return_to_main', '0', 'Return to Main Menu')
menus.append(cmd_menu)

active_menu = menus[0]

# checked for presence of saved game and disable "continue" option if not present
def CheckSavedGame(menu):
	for menu_option in menu.cmd_list:
		if menu_option.option_id != 'continue_scenario': continue
		if os.path.exists('savegame'):
			menu_option.inactive = False
		else:
			menu_option.inactive = True
		return

CheckSavedGame(active_menu)


global gradient_x

def AnimateScreen():
	
	global gradient_x
	
	# draw gradient
	for x in range(0, 10):
		if x + gradient_x > WINDOW_WIDTH: continue
		for y in range(19, 34):
			char = libtcod.console_get_char(main_menu_con, x + gradient_x, y)
			fg = libtcod.console_get_char_foreground(main_menu_con, x + gradient_x, y)
			if char != 0 and fg != GRADIENT[x]:
				libtcod.console_set_char_foreground(main_menu_con, x + gradient_x,
					y, GRADIENT[x])
	
	# decrease next gradient x location
	gradient_x -= 2
	if gradient_x <= 0:
		gradient_x = WINDOW_WIDTH + 20
	

def UpdateScreen():
	libtcod.console_blit(main_menu_con, 0, 0, 88, 60, con, 0, 0)
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0)
	active_menu.DisplayMe(0, WINDOW_XM-12, 36, 24)
	
	# settings menu active
	if active_menu == menus[1]:
		libtcod.console_set_default_foreground(0, HIGHLIGHT_COLOR)
		text = 'Message Pause Time: '
		msg_time = config.getint('ArmCom2', 'message_pause_time')
		if msg_time == 500:
			text += 'Short'
		elif msg_time == 700:
			text += 'Medium'
		else:
			text += 'Long'
		libtcod.console_print(0, WINDOW_XM-12, 49, text)
		
		text = 'Animation Speed: '
		ani_time = config.getint('ArmCom2', 'animation_speed')
		if ani_time == 16:
			text += 'Fast'
		elif ani_time == 30:
			text += 'Normal'
		else:
			text += 'Slow'
		libtcod.console_print(0, WINDOW_XM-12, 50, text)
		libtcod.console_set_default_foreground(0, libtcod.white)
	
UpdateScreen()

# animation timing
time_click = time.time()
gradient_x = WINDOW_WIDTH + 20



# jump right into the scenario
#exit_game = True
#DoScenario()
exit_game = False

while not exit_game:
	
	# trigger animation
	if time.time() - time_click >= 0.05:
		AnimateScreen()
		UpdateScreen()
		time_click = time.time()
	
	libtcod.console_flush()
	
	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
	
	# exit right away
	if libtcod.console_is_window_closed(): sys.exit()
	
	# skip this section if no commands in buffer
	if key is None: continue
	
	# select previous or next menu option
	if key.vk == libtcod.KEY_UP:
		active_menu.SelectNextOption(reverse=True)
		UpdateScreen()
		continue
		
	elif key.vk == libtcod.KEY_DOWN:
		active_menu.SelectNextOption()
		UpdateScreen()
		continue
	
	# activate selected menu option
	elif key.vk == libtcod.KEY_ENTER:
		option = active_menu.GetSelectedOption()
	
	# see if we pressed a key associated with a menu option
	else:
		option = active_menu.GetOptionByKey()
	
	if option is None: continue
	
	# select this option and highlight it
	active_menu.selected_option = option
	UpdateScreen()
	libtcod.console_flush()
	
	# selected an inactive menu option
	if option.inactive: continue
	
	# main menu
	if option.option_id == 'continue_scenario':
		DoScenario(load_savegame=True)
		active_menu = menus[0]
		CheckSavedGame(active_menu)
		UpdateScreen()
	elif option.option_id == 'new_scenario':
		DoScenario()
		active_menu = menus[0]
		CheckSavedGame(active_menu)
		UpdateScreen()
	elif option.option_id == 'options':
		active_menu = menus[1]
		UpdateScreen()
	elif option.option_id == 'quit':
		exit_game = True
	
	# settings menu
	elif option.option_id == 'toggle_font_size':
		libtcod.console_delete(0)
		if config.getboolean('ArmCom2', 'large_display_font'):
			config.set('ArmCom2', 'large_display_font', 'false')
			fontname = 'c64_8x8.png'
		else:
			config.set('ArmCom2', 'large_display_font', 'true')
			fontname = 'c64_16x16.png'
		libtcod.console_set_custom_font(DATAPATH+fontname,
			libtcod.FONT_LAYOUT_ASCII_INROW, 0, 0)
		libtcod.console_init_root(WINDOW_WIDTH, WINDOW_HEIGHT,
			NAME + ' - ' + VERSION + SUBVERSION, fullscreen = False,
			renderer = libtcod.RENDERER_GLSL)
		SaveCFG()
		UpdateScreen()
	
	elif option.option_id == 'select_msg_speed':
		msg_time = config.getint('ArmCom2', 'message_pause_time')
		if msg_time == 500:
			config.set('ArmCom2', 'message_pause_time', 700)
		elif msg_time == 700:
			config.set('ArmCom2', 'message_pause_time', 900)
		else:
			config.set('ArmCom2', 'message_pause_time', 500)
		SaveCFG()
		UpdateScreen()
	
	elif option.option_id == 'select_ani_speed':
		ani_time = config.getint('ArmCom2', 'animation_speed')
		if ani_time == 16:
			config.set('ArmCom2', 'animation_speed', 30)
		elif ani_time == 30:
			config.set('ArmCom2', 'animation_speed', 46)
		else:
			config.set('ArmCom2', 'animation_speed', 16)
		SaveCFG()
		UpdateScreen()
	
	elif option.option_id == 'return_to_main':
		active_menu = menus[0]
		UpdateScreen()

# END #

