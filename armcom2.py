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
#      The author does not condone any of the actions or ideologies depicted herein      #
#                                                                                        #
##########################################################################################


##### Libraries #####
import libtcodpy as libtcod				# The Doryen Library
import ConfigParser					# for saving and loading settings
import time						# for animation timing
from random import choice, shuffle, sample
from textwrap import wrap				# for breaking up strings
from operator import attrgetter				# for list sorting
from math import floor, cos, sin, sqrt			# for math
from math import degrees, atan2, ceil			# for heading calculation

import shelve						# for saving and loading games
#import dbhash, anydbm					# needed for py2exe
import os, sys						# for OS-related stuff
import xp_loader, gzip					# for loading xp image files
import xml.etree.ElementTree as xml			# ElementTree library for xml



##########################################################################################
#                                   Constant Definitions                                 #
#                                   You can rely on them                                 #
##########################################################################################

# debug constants, should all be set to False in distribution version
VIEW_ALL = False			# Player can see all hexes on viewport


NAME = 'Armoured Commander II'
VERSION = 'Alpha 1'					# determines saved game compatability
SUBVERSION = ''						# descriptive, no effect on compatability
DATAPATH = 'data/'.replace('/', os.sep)			# path to data files
LIMIT_FPS = 50						# maximum screen refreshes per second
WINDOW_WIDTH = 83					# width of game window in characters
WINDOW_HEIGHT = 60					# height "
WINDOW_XM = int(WINDOW_WIDTH/2)				# horizontal center of game window
WINDOW_YM = int(WINDOW_HEIGHT/2)			# vertical "
PI = 3.141592653589793					# good enough for the JPL, good enough for us

GRADIENT = [						# gradient animated effect for main menu
	libtcod.Color(51, 51, 51),
	libtcod.Color(64, 64, 64),
	libtcod.Color(128, 128, 128),
	libtcod.Color(192, 192, 192),
	libtcod.Color(255, 255, 255),
	libtcod.Color(192, 192, 192),
	libtcod.Color(128, 128, 128),
	libtcod.Color(64, 64, 64),
	libtcod.Color(51, 51, 51),
	libtcod.Color(51, 51, 51)
]

# Game engine constants, can be tweaked for slightly different results
MAX_LOS_DISTANCE = 13				# maximum distance that a Line of Sight can be drawn
ELEVATION_M = 20.0				# each elevation level represents x meters of height
MP_ALLOWANCE = 12				# how many MP each unit has for each Movement phase

# Colour definitions
OPEN_GROUND_COL = libtcod.Color(0, 64, 0)
WATER_COL = libtcod.Color(0, 0, 217)
FOREST_COL = libtcod.Color(0, 140, 0)
FOREST_BG_COL = libtcod.Color(0, 40, 0)
FIELDS_COL = libtcod.Color(102, 102, 0)
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
SELECTED_HL_COL = libtcod.Color(50, 150, 255)		# selected PSG highlight colour
ENEMY_HL_COL = libtcod.Color(40, 0, 0)
INACTIVE_COL = libtcod.Color(100, 100, 100)		# inactive option color
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency

KEY_HIGHLIGHT_COLOR = libtcod.Color(70, 170, 255)	# highlight for key commands
HIGHLIGHT = (libtcod.COLCTRL_1, libtcod.COLCTRL_STOP)	# constant for highlight pair

# Descriptor definitions
MORALE_DESC = {
	'7' : 'Reluctant',
	'6' : 'Regular',
	'5' : 'Confident',
	'4' : 'Fearless',
	'3' : 'Fanatic'
}
SKILL_DESC = {
	'7': 'Green',
	'6' : '2nd Line',
	'5' : '1st Line',
	'4' : 'Veteran',
	'3' : 'Elite'
}

PHASE_NAMES = ['Movement', 'Shooting']

MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June',
	'July', 'August', 'September', 'October', 'November', 'December']

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

# option codes, key codes, and directional arrows to use for rotate/move commands
MOVE_COMMANDS = [
	(5, 'Q', chr(231)),
	(0, 'W', chr(24)),
	(1, 'E', chr(228)),
	(4, 'A', chr(230)),
	(3, 'S', chr(25)),
	(2, 'D', chr(229))
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

# column shifts for differentials in point sterngth vs. armour rating
# TODO: will need to adjust to that they are fair
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

# AI: used to determine actions of non-player-controlled units
class AI:
	def __init__(self, owner):
		self.owner = owner			# the PSG for whom this AI instance is
		
	# randomly choose and execute and action for the current phase
	def DoPhaseAction(self):
		
		# Movement Phase actions
		if scenario.current_phase == 0:
			# TEMP - no move actions
			return
		
		# Shooting Phase actions
		elif scenario.current_phase == 1:
			
			print 'AI Shooting Phase Action for: ' + self.owner.GetName(true_name=True)
			
			af_strength = self.owner.weapon_list[0].stats['area_strength']
			pf_strength = self.owner.weapon_list[0].stats['point_strength']
			max_range = self.owner.weapon_list[0].stats['max_range']
			
			# build list of possible targets
			target_list = []
			for psg in scenario.psg_list:
				# same team!
				if psg.owning_player == self.owner.owning_player: continue
				
				# out of max range
				if GetHexDistance(self.owner.hx, self.owner.hy, psg.hx, psg.hy) > max_range: continue
				
				# don't have the right kind of attack for this target
				if af_strength == 0 and not psg.pf_target: continue
				if pf_strength == 0 and not psg.af_target: continue
				
				# no line of sight
				if (psg.hx, psg.hy) not in GetLoS(self.owner.hx, self.owner.hy, psg.hx, psg.hy): continue
				
				# if we had already aquired this target, choose it automatically
				if self.owner.acquired_target is not None:
					if self.owner.acquired_target == psg:
						print 'AI: Continuing attack on acquired target'
						InitAttack(self.owner, psg, psg.af_target)
						return
				
				target_list.append(psg)
			
			if len(target_list) == 0:
				print 'AI: No possible targets'
				return
			
			text = 'AI: Found ' + str(len(target_list)) + ' possible target'
			if len(target_list) > 1: text += 's'
			print text
			
			# choose a random target!
			psg = choice(target_list)
			
			InitAttack(self.owner, psg, psg.af_target)
		

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
		width = len(self.key_code) + 1 + len(self.option_text)
		if width > 23:
			wrap_w = 23 - (len(self.key_code) + 1)
			self.option_text_lines = wrap(self.option_text, wrap_w)
		else:
			self.option_text_lines = [self.option_text]
		# calculate display height
		self.h = len(self.option_text_lines)


# a list of options for the player
class CommandMenu:
	def __init__(self, menu_id):
		self.menu_id = menu_id			# a unique id for this menu
		self.Clear()
		self.selected_option = None		# currently selected option
	
	# clear any existing menu options
	def Clear(self):
		self.cmd_list = []
	
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
				# player chose an inactive menu item
				if option.inactive: return None
				return option
			if option.key_code == 'Enter' and key.vk == libtcod.KEY_ENTER:
				if option.inactive: return None
				return option
			if option.key_code == 'Tab' and key.vk == libtcod.KEY_TAB:
				if option.inactive: return None
				return option
			if option.key_code == 'Space' and key.vk == libtcod.KEY_SPACE:
				if option.inactive: return None
				return option
			if option.key_code == 'Backspace' and key.vk == libtcod.KEY_BACKSPACE:
				if option.inactive: return None
				return option
			if option.key_code == 'Esc' and key.vk == libtcod.KEY_ESCAPE:
				if option.inactive: return None
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
		

# platoon-sized group class
# represents a platoon, squadron, battery, etc.
class PSG:
	def __init__(self, name, unit_id, num_steps, facing, owning_player, skill_lvl, morale_lvl):
		self.unit_id = unit_id			# unique ID for unit type of this PSG
		self.name = name			# name, eg. 'Tank Squadron'
		self.step_name = ''			# name of individual teams / vehicles w/in this PSG
		self.num_steps = num_steps		# number of unit steps in this PSG
		self.portrait = None			# portrait filename if any
		self.ai = None				# pointer to AI instance
		
		self.hx = 0				# hex location of this PSG, will be set
		self.hy = 0				#   by SpawnAt()
		self.screen_x = 0			# draw location on the screen
		self.screen_y = 0			#   set by DrawMe()
		self.anim_x = 0				# animation location in console
		self.anim_y = 0
		
		self.spotted = False			# PSG has been spotted by an enemy unit
		
		self.facing = facing			# facing direction for guns and vehicles
		self.turret = False			# vehicle has a turret
		
		self.movement_class = ''		# movement class
		self.armour = None			# armour factors if any
		
		self.weapon_list = []			# list of weapons
		self.selected_weapon = None		# currently selected weapon
		
		self.target_list = []			# list of possible targets
		self.target_psg = None			# currently targeted PSG
		
		self.acquired_target = None		# PSG has acquired this unit as target
		self.acquired_by = []			# PSG has been acquired by this unit(s)
		
		self.infantry = False			# PSG type flags
		self.gun = False
		self.vehicle = False
		
		self.af_target = False			# PSG can be targeted by area fire
		self.pf_target = False			# " point fire
		
		self.recce = False			# unit has recce abilities
		
		self.owning_player = owning_player	# player that controls this PSG
		self.display_char = ''			# character to display on map, set below
		
		self.skill_lvl = skill_lvl		# skill and morale levels
		self.morale_lvl = morale_lvl
		
		# action flags
		self.moved = False
		self.fired = False
		self.changed_facing = False
		
		# status flags
		#self.dug_in = False			# only infantry units and guns can dig in
		#self.hull_down = -1			# only vehicles can be hull down, number
							#   is direction
		
		self.pinned = False			# move N/A, attacks less effective
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
		
		if self.vehicle:
			spot_range = 6
		else:
			spot_range = 2
		map_hex = GetHexAt(self.hx, self.hy)
		
		# protective terrain
		if map_hex.terrain_type.af_modifier < 0 or map_hex.terrain_type.pf_modifier < 0:
			spot_range -= 1
		else:
			spot_range += 2
		
		# fired, moved, or pinned: apply worst one
		if self.fired:
			spot_range += 4
		elif self.moved:
			spot_range += 2
		elif self.pinned:
			spot_range -= 1
		
		# skill modifier
		if self.skill_lvl <= 4:
			spot_range -= 1
		
		return spot_range

	# TODO: turn into a proper spawn function
	# try to place this PSG into the target hex, if not possible, place in random adjacent hex
	def SpawnAt(self, hx, hy):
		hex_list = [(hx, hy)]
		adjacent_list = GetAdjacentHexesOnMap(hx, hy)
		shuffle(adjacent_list)
		hex_list.extend(adjacent_list)
		for (hx1, hy1) in hex_list:
			map_hex = GetHexAt(hx1, hy1)
			if map_hex is None: continue
			if map_hex.IsOccupied(): continue
			if map_hex.terrain_type.water: continue
			self.hx = hx1
			self.hy = hy1
			return
		print 'ERROR: unable to spawn PSG into or near ' + str(hx) + ',' + str(hy)

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

	# remove this PSG from the game
	def DestroyMe(self):
		scenario.psg_list.remove(self)
		# clear acquired target records
		self.ClearAcquiredTargets()

	# do any automatic actions for start of current phase
	def ResetForPhase(self):
		
		# clear any targets and selected weapon
		self.target_list = []
		self.target_psg = None
		self.selected_weapon = None
		
		# start of movement phase
		if scenario.current_phase == 0:
			self.mp = self.max_mp
			self.moved = False
			self.changed_facing = False
		elif scenario.current_phase == 1:
			self.fired = False
			self.SelectNextWeapon()

	# TODO: roll for recovery from negative statuses
	def DoRecoveryTests(self):
		if self.pinned:
			if self.MoraleCheck(0):
				self.UnPinMe()

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
				
				# weapon info
				weapon_list = item.find('weapon_list')
				if weapon_list is not None:
					weapons = weapon_list.findall('weapon')
					if weapons is not None:
						for weapon_item in weapons:
							new_weapon = SpawnWeapon(weapon_item)
							self.weapon_list.append(new_weapon)
				
				# infantry stats if any
				if item.find('infantry') is not None:
					self.infantry = True
				
				# vehicle stats if any
				if item.find('vehicle') is not None:
					self.vehicle = True
					if item.find('turret') is not None: self.turret = True
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
				
				# gun stats
				elif item.find('gun') is not None:
					self.gun = True
					self.deployed = True
					self.emplaced = True
					
					if item.find('gun_shield') is not None:
						self.gun_shield = True
					else:
						self.gun_shield = False
				
				return
		
		print 'ERROR: Could not find unit stats for: ' + self.unit_id
	
	# this PSG has been spotted by enemy forces
	
	
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
		if not self.gun and not self.turret: return
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
		if map_hex.IsOccupied(): return False
		if map_hex.terrain_type.water: return False
		return True
	
	# try to move this PSG into the target hex
	# vehicles must be facing this direction to move, or can do a reverse move
	# returns True if the move was successful
	def MoveInto(self, new_hx, new_hy):
		
		# make sure move is allowed
		if not self.CheckMoveInto(new_hx, new_hy):
			return False
		
		# get MP cost of move, return false if not enough
		map_hex1 = GetHexAt(self.hx, self.hy)
		map_hex2 = GetHexAt(new_hx, new_hy)
		mp_cost = GetMPCostToMove(self, map_hex1, map_hex2)
		if mp_cost > self.mp: return False
		
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
			# TODO: play sound
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
		# no result
		if result_row is None:
			text = 'No Effect'
		elif result_row == 0:
			text = 'Morale Check'
		else:
			text = str(result_row) + ' step loss'
			
		libtcod.console_print_ex(attack_con, 13, 50, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		libtcod.console_print_ex(attack_con, 13, 54, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Enter to Continue')
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 3)
		libtcod.console_flush()
		WaitForEnter()
		
		if result_row is None: return
		
		# apply result: step loss
		if result_row >= 1:
			self.num_steps -= result_row
			if self.num_steps < 0: self.num_steps = 0
		
			# check to see if unit has been destroyed completely
			if self.num_steps == 0:
				text = self.GetName() + ' has been destroyed!'
				Message(self.screen_x, self.screen_y, text)
				self.DestroyMe()
				UpdateUnitConsole()
				return
			
			text = self.GetName() + ' has been reduced to ' + str(self.num_steps) + ' step'
			if self.num_steps > 1: text += 's'
			Message(self.screen_x, self.screen_y, text)
		
		# apply morale check
		if self.MoraleCheck(result_row):
			text = self.GetName() + ' passes its morale check.'
			Message(self.screen_x, self.screen_y, text)
		else:
			self.PinMe()
	
	# TODO: perform a morale check for this PSG
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
		
		if roll >= morale_lvl:
			return True
		return False
	
	# pin this unit
	def PinMe(self):
		
		# armoured vehicles never pinned
		if self.vehicle and self.armour is not None:
			return

		self.pinned = True
		text = self.GetName() + ' is pinned.'
		Message(self.screen_x, self.screen_y, text)
	
	# unpin this unit
	def UnPinMe(self):
		self.pinned = False
		text = self.GetName() + ' is no longer pinned.'
		Message(self.screen_x, self.screen_y, text)
	
	# take a skill test, returning True if passed
	def SkillTest(self, modifier):
		skill_lvl = self.skill_lvl - modifier
		d1, d2, roll = Roll2D6()
		if roll <= skill_lvl:
			return True
		return False
	
	
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
	# TODO: set up impassible cliff edges in this and adjacent hexes if required
	def SetElevation(self, new_elevation):
		self.elevation = new_elevation
	
	# set hex terrain
	def SetTerrainType(self, new_terrain_type):
		for terrain_type in terrain_types:
			if terrain_type.display_name == new_terrain_type:
				self.terrain_type = terrain_type
				return
		print 'ERROR: Terrain type not found: ' + new_terrain_type
	
	# returns true if there is a PSG in this hex
	def IsOccupied(self):
		for psg in scenario.psg_list:
			if psg.hx == self.hx and psg.hy == self.hy:
				return True
		return False

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
		# list of edge hexes
		self.edge_hexes = []
		# generate map hexes
		self.hexes = {}
		for hx in range(w):
			hy_start = 0 - hx//2
			hy_end = hy_start + h
			for hy in range(hy_start, hy_end):
				self.hexes[(hx,hy)] = MapHex(hx, hy)
				self.hexes[(hx,hy)].SetTerrainType('Fields')
				self.hexes[(hx,hy)].SetElevation(1)
				# add to list if on edge of map
				if hx == 0 or hx == w-1:
					self.edge_hexes.append((hx, hy))
				elif hy == hy_start or hy == hy_end-1:
					self.edge_hexes.append((hx, hy))
				
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
		
		
		self.active_player = 0			# currently active player (0 or 1)
		self.current_phase = 0			# current action phase
		
		self.psg_list = []			# list of all platoon-sized groups in play
		self.active_psg = None			# currently active PSG
		
		self.player_direction = 3		# direction of player-friendly forces
		self.enemy_direction = 0		# direction of enemy forces
		
		self.winner = None			# number of player that has won the scenario,
							#   None if no winner yet
		self.end_text = ''			# description of how scenario ended
		
		self.cmd_menu = CommandMenu('scenario_menu')		# current command menu for player
		self.active_cmd_menu = None		# currently active command menu
		
		self.messages = []			# list of game messages
		
		# create the hex map
		self.hex_map = HexMap(map_w, map_h)
		self.objective_hexes = []			# list of objective hexes
	
	# do enemy AI actions for this phase
	def DoAIPhase(self):
		
		# build a list of units that can be activated this phase
		activate_list = []
		for psg in self.psg_list:
			if psg.ai is None: continue
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
	
	# finish up current phase, start new phase (and possibly new turn as well)
	def NextPhase(self):
		
		# Movement -> Shooting Phase
		if self.current_phase == 0:
			self.current_phase = 1
			self.active_cmd_menu = 'shooting_root'
		
		# Shooting Phase -> New Active Player and Movement Phase
		elif self.current_phase == 1:
			
			if self.active_player == 0:
				self.active_player = 1
				self.active_psg = None
			else:
				self.AdvanceClock()
				UpdateScenInfoConsole()
				self.active_player = 0
				scenario.SelectNextPSG()
			self.current_phase = 0
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
				
				# calculate spot range for psg2
				spot_range = psg2.GetSpotRange()
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
	
	# check to see if scenario has ended, triggered at start of every new turn
	def CheckForEnd(self):
		
		# no remaining enemy PSGs
		enemy_active = False
		for psg in self.psg_list:
			if psg.owning_player == 1:
				enemy_active = True
				break
		if not enemy_active:
			self.winner = 0
			self.end_text = 'All enemy PSGs were destroyed'
			return
		
		# player captured objective
		for map_hex in self.objective_hexes:
			if map_hex.objective:
				if map_hex.held_by == 0:
					self.winner = 0
					self.end_text = 'Objective was captured'
					return
	
	# display a screen of info about a completed scenario
	def DisplayEndScreen(self):
		# use the buffer console to darken the screen background
		libtcod.console_clear(con)
		libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0, 
			0.0, 0.7)
		libtcod.console_rect(0, 4, 10, 80, 40, True, libtcod.BKGND_SET)
		
		text = 'You have '
		if self.winner == 0:
			text += 'won'
		else:
			text += 'lost'
		text += ' the scenario'
		libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM-4, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM-2, libtcod.BKGND_NONE,
			libtcod.CENTER, self.end_text)
		libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM+2, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Press [Enter] to Return to Main Menu')
		libtcod.console_flush()
		WaitForEnter()
	
	# rebuild a list of commands for the command menu based on current phase and
	#   game state
	def BuildCmdMenu(self):
		
		# clear any existing command menu
		self.cmd_menu.Clear()
		
		# don't display anything if player is not active
		if scenario.active_player != 0:
			UpdateCmdConsole()
			return
		
		# movement phase menu
		if self.active_cmd_menu == 'movement_root':
			
			# run through six possible rotate/move directions and build commands
			for (direction, key_code, char) in MOVE_COMMANDS:
				
				if not scenario.active_psg.infantry:
					if scenario.active_psg.facing != direction:
						cmd = 'rotate_' + str(direction)
						desc = 'Face ' + char
						self.cmd_menu.AddOption(cmd, key_code, desc)
						# FUTURE: disable rotate if not allowed
						continue
				cmd = 'move_' + str(direction)
				desc = 'Move ' + char
				menu_option = self.cmd_menu.AddOption(cmd, key_code, desc)
				
				# disable move command if move not allowed
				if scenario.active_psg.pinned:
					menu_option.inactive = True
					continue
				(hx, hy) = GetAdjacentHex(scenario.active_psg.hx,
					scenario.active_psg.hy, direction)
				if not scenario.active_psg.CheckMoveInto(hx, hy):
					menu_option.inactive = True
			
		# shooting phase menu
		elif self.active_cmd_menu == 'shooting_root':
			if not scenario.active_psg.fired:
				self.cmd_menu.AddOption('next_weapon', 'W', 'Next Weapon')
				self.cmd_menu.AddOption('next_target', 'T', 'Next Target')
				menu_option = self.cmd_menu.AddOption('fire_area', 'A', 'Area Fire')
				
				# Conditions under which Area Fire not Possible:
				if scenario.active_psg.selected_weapon.stats['area_strength'] == 0:
					menu_option.inactive = True
				if scenario.active_psg.target_psg is None:
					menu_option.inactive = True
				else:
					if not scenario.active_psg.target_psg.af_target:
						menu_option.inactive = True
				
				menu_option = self.cmd_menu.AddOption('fire_point', 'P', 'Point Fire')
				
				# Conditions under which Point Fire not Possible:
				if scenario.active_psg.selected_weapon.stats['point_strength'] == 0:
					menu_option.inactive = True
				if scenario.active_psg.target_psg is None:
					menu_option.inactive = True
				else:
					if not scenario.active_psg.target_psg.pf_target:
						menu_option.inactive = True
					# PF attacks have to be on spotted units
					elif not scenario.active_psg.target_psg.spotted:
						menu_option.inactive = True
		
		# all root menus get these commands
		if self.active_cmd_menu in ['movement_root', 'shooting_root']:
			self.cmd_menu.AddOption('select_unit', 'Tab', 'Next Unit')
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


# calculate an area or point fire attack
def CalcAttack(attacker, weapon, target, area_fire):
	# create a new attack object
	attack_obj = Attack(attacker, weapon, target)
	
	# determine if this is an area or point fire attack
	if area_fire:
		attack_obj.area_fire = True
	else:
		attack_obj.point_fire = True
	
	# determine distance to target
	distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
	
	# determine base attack stregth or steps firing
	if area_fire:
		attack_strength = weapon.stats['area_strength']
		if attacker.infantry:
			if distance == 1:
				attack_strength += int(ceil(attacker.num_steps / 2))
		else:
			attack_strength = attack_strength * attacker.num_steps
		
		if attacker.pinned:
			attack_strength = int(ceil(attack_strength / 2))
		
		if not target.spotted:
			attack_strength = int(ceil(attack_strength / 2))
		
	else:
		attack_strength = attacker.num_steps
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
	if area_fire:
		if distance <= 1:
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
	else:
		max_range = weapon.stats['max_range']
		multipler = 0.5	
		if weapon.stats['long_range'] == 'L':
			multipler = 0.75
		elif weapon.stats['long_range'] == 'LL':
			multipler = 1.0
		normal_range = int(ceil(float(max_range) * multipler))
		close_range = int(ceil(float(normal_range) * 0.5))
		
		if distance <= close_range:
			attack_obj.column_modifiers.append(('Close Range', 5))
		elif distance <= normal_range:
			attack_obj.column_modifiers.append(('Normal Range', 3))
	
	# pinned PF attack
	if not area_fire:
		if attacker.pinned:
			attack_obj.column_modifiers.append(('Attacker Pinned', -2))	
	
	# attacker moved or changed facing
	if attacker.moved:
		attack_obj.column_modifiers.append(('Attacker Moved', -3))
	elif attacker.changed_facing:
		attack_obj.column_modifiers.append(('Attacker Pivoted', -1))
	
	# acquired target
	if attacker.acquired_target is not None:
		if attacker.acquired_target == target:
			attack_obj.column_modifiers.append(('Acquired Target', 1))
	
	# Target Terrain Modifier
	map_hex = GetHexAt(target.hx, target.hy)
	af_modifier = map_hex.terrain_type.af_modifier
	pf_modifier = map_hex.terrain_type.pf_modifier
	if area_fire:
		if af_modifier != 0:
			attack_obj.column_modifiers.append((map_hex.terrain_type.display_name, af_modifier))
	else:
		if pf_modifier != 0:
			attack_obj.column_modifiers.append((map_hex.terrain_type.display_name, pf_modifier))
	
	# infantry movement in no cover
	if target.infantry and target.moved and pf_modifier == 0:
		attack_obj.column_modifiers.append(('Target Moved, No Protective Cover', 2))
	
	if target.vehicle and target.moved:
		attack_obj.column_modifiers.append(('Target Vehicle Moved', -2))
	
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
	# TODO: if column is less than 0, no chance of effect?
	if column < 0:
		column = 0
	elif column > MAX_FIRE_TABLE_COLUMN - 1:
		column = MAX_FIRE_TABLE_COLUMN - 1
		
	final_column = FIRE_TABLE[column]
	attack_obj.final_column = final_column
	
	# build list of possible final outcomes
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
	stats['name'] = item.find('name').text
	if item.find('area_strength') is None:
		stats['area_strength'] = 0
	else:
		stats['area_strength'] = int(item.find('area_strength').text)
	if item.find('point_strength') is None:
		stats['point_strength'] = 0
	else:
		stats['point_strength'] = int(item.find('point_strength').text)
	if item.find('max_range') is None:
		# guns by default have max range of 1 mile
		stats['max_range'] = 10
	else:
		stats['max_range'] = int(item.find('max_range').text)
	if item.find('long_range') is None:
		stats['long_range'] = ''
	else:
		stats['long_range'] = item.find('long_range').text
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


# returns the hex object at the given hex coordinate
def GetHexAt(hx, hy):
	if (hx, hy) in scenario.hex_map.hexes:
		return scenario.hex_map.hexes[(hx, hy)]
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
# if skip_occupied > -1, skip hexes that already have an enemy PSG in them
def GetAdjacentHexesOnMap(hx, hy, skip_occupied=-1):
	hex_list = []
	for d in range(6):
		(hx_mod, hy_mod) = DESTHEX[d]
		hx2 = hx+hx_mod
		hy2 = hy+hy_mod
		# hex is on the game map
		if (hx2, hy2) in scenario.hex_map.hexes:
			if skip_occupied > -1:
				if GetHexAt(hx2, hy2).IsOccupied():
					continue
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


# calculate the MP required to move into the target hex
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
	
	elif psg.movement_class == 'Tank':
		if road:
			cost = 4
		elif map_hex2.terrain_type.difficult:
			cost = 6
		else:
			cost = 4
	
	elif psg.movement_class == 'Fast Tank':
		if road:
			cost = 3
		elif map_hex2.terrain_type.difficult:
			cost = 6
		else:
			cost = 3

	return cost
	


# returns a path from one hex to another, avoiding impassible and difficult terrain
# based on function from ArmCom 1, which was based on:
# http://stackoverflow.com/questions/4159331/python-speed-up-an-a-star-pathfinding-algorithm
# http://www.policyalmanac.org/games/aStarTutorial.htm
def GetHexPath(hx1, hy1, hx2, hy2, movement_class=None):
	
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
				pass
			
			# TEMP
			if node.terrain_type.very_difficult:
				cost = 6
			elif node.terrain_type.difficult:
				cost = 2
			else:
				cost = 1
			
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
	print 'GetHexPath() Error: No path possible'
	return []
	

# returns the viewport hex corresponding to this map hex, None if not in viewport
def GetVPHex(hx, hy):
	for (vp_hx, vp_hy), map_hex in scenario.hex_map.vp_matrix.iteritems():
		if hx == map_hex.hx and hy == map_hex.hy:
			return (vp_hx, vp_hy)
	return None


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
def PlotLine(x1, y1, l, a):
	a = RectifyHeading(a-90)
	x2 = int(x1 + (l * cos(a*PI/180.0)))
	y2 = int(y1 + (l * sin(a*PI/180.0))) 
	return (x2, y2)


# wait for a specified amount of miliseconds, refreshing the screen in the meantime
def Wait(wait_time):
	# added this to avoid the spinning wheel of death in Windows
	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
	libtcod.sys_sleep_milli(wait_time)
	# TEMP?
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
		
		# TEMP - emergency exit from game
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
			
			# TEMP: emergency escape in case of stuck loop
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
	lowest_elevation = None
	hexpair = None
	hexpair_elevation = 0
	for (hx, hy) in hex_list:
		
		if (hx, hy) not in scenario.hex_map.hexes:
			continue
		if GetHexDistance(hx1, hy1, hx, hy) > MAX_LOS_DISTANCE:
			continue
		
		map_hex = scenario.hex_map.hexes[(hx, hy)]
		elevation = float(map_hex.elevation) - observer_elevation
		elevation = (elevation * ELEVATION_M) + float(map_hex.terrain_type.los_height)
		
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

		# if no lowest elevation recorded yet, record it
		if lowest_elevation is None:
			lowest_elevation = elevation
		
		# otherwise, if lower than previously recorded, replace it
		else:
			if elevation < lowest_elevation:
				lowest_elevation = elevation
		
		# calculate slope from observer to this hex
		slope = elevation / float(GetHexDistance(hx1, hy1, hx, hy)) * 160.0
		
		# if adjacent hex, automatically visible
		if los_slope is None:
			visible_hexes.append((hx, hy))
			los_slope = slope
		
		else:
			# check if this hex is visible based on previous LoS slope
			if slope >= los_slope:
				visible_hexes.append((hx, hy))
				# if hexspine, check for also making first part of a hexpair
				# visible as well
				if hexpair is not None:
					visible_hexes.append(hexpair)
					hexpair = None
		
			# if slope larger than previous los_slope, set new los_slope
			if slope > los_slope:
				los_slope = slope

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
def InitAttack(attacker, target, area_fire):
	
	# make sure there's a weapon and a target
	if target is None: return
	if attacker.selected_weapon is None: return

	# send information to CalcAttack, which will return an Attack object with the
	#   calculated stats to use for the attack
	attack_obj = CalcAttack(attacker, attacker.selected_weapon, target, area_fire)
	
	# if player wasn't attacker, display LoS from attacker to target
	if attacker.owning_player == 1:
		line = GetLine(attacker.screen_x, attacker.screen_y, target.screen_x,
			target.screen_y)
		for (x,y) in line[2:-1]:
			libtcod.console_set_char(con, x, y, 250)
			libtcod.console_set_char_foreground(con, x, y, libtcod.red)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
			Wait(15)
	
	# display attack console for this attack
	DisplayAttack(attack_obj)
	
	cancel_attack = WaitForEnter(allow_cancel=True)
	
	# player has chance to cancel attack at this point
	if attacker.owning_player == 0 and cancel_attack:
		return
	
	# clear any LoS drawn above from screen
	DrawScreenConsoles()
	
	
	# TODO: display attack animation
	
	
	# set fired flag and clear the selected target
	attacker.fired = True
	attacker.target_psg = None
	
	# determine if a facing change is needed
	if not attacker.infantry:
		bearing = GetRelativeBearing(attacker, target)
		if 30 < bearing < 330:
			direction = GetDirectionToward(attacker.hx, attacker.hy, target.hx,
				target.hy)
			attacker.PivotToFace(direction)
			UpdateUnitConsole()
			DrawScreenConsoles()
			libtcod.console_flush()
	
	# resolve attack
	target.ResolveAttack(attack_obj)
	
	# clear attacker's selected weapon
	attacker.selected_weapon = None
	
	# handle newly acquired target
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
	
	if attack_obj.area_fire:
		text = 'Area'
	else:
		text = 'Point'
	text += ' fire attack by'
	libtcod.console_print_ex(attack_con, 13, 3, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	text = attack_obj.attacker.GetName()
	libtcod.console_print_ex(attack_con, 13, 4, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
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
	
	if attack_obj.attacker.owning_player == 0:
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
	
	# create a river
	# TEMP not yet implemented
	def CreateRiver(start_hx, start_hy, direction):
		pass
	
	# returns true if an adjacent map hex has alrady been set to this terrain type
	def HasAdjacent(map_hex, terrain_type):
		hex_list = GetAdjacentHexesOnMap(map_hex.hx, map_hex.hy)
		for (hx, hy) in hex_list:
			if scenario.hex_map.hexes[(hx, hy)].terrain_type == terrain_type:
				return True
		return False
	
	# create a list of map hexes and shuffle their order
	hex_list = []
	for key, map_hex in scenario.hex_map.hexes.items():
		hex_list.append(map_hex)
	shuffle(hex_list)
	
	# do first elevation pass
	for map_hex in hex_list:
		roll = libtcod.random_get_int(0, 1, 100)
		if roll <= 5:
			map_hex.SetElevation(0)
		elif roll <= 80:
			continue
		elif roll <= 95:
			map_hex.SetElevation(2)
		else:
			map_hex.SetElevation(3)
	
	# do second pass: elevation smoothing
	for map_hex in hex_list:
		if map_hex.elevation == 2:
			has_adjacent_hill = False
			adjacent_list = GetAdjacentHexesOnMap(map_hex.hx, map_hex.hy)
			for (hx, hy) in adjacent_list:
				adjacent_hex = GetHexAt(hx, hy)
				if adjacent_hex.elevation >= 2:
					has_adjacent_hill = True
					break
			if not has_adjacent_hill:
				map_hex.SetElevation(1)

	# do terrain type pass
	for map_hex in hex_list:
		
		# if there's already an adjcacent pond, don't create another one
		if HasAdjacent(map_hex, 'Pond'):
			pond_chance = 0
		else:
			pond_chance = 5
		
		# if there's already an adjacent forest, higher chance of there being one
		if HasAdjacent(map_hex, 'Sparse Forest'):
			forest_chance = 30
		else:
			forest_chance = 5
		
		# if there's already an adjacent field, higher chance of there being one
		if HasAdjacent(map_hex, 'In-Season Fields'):
			field_chance = 10
		else:
			field_chance = 5
		
		if HasAdjacent(map_hex, 'Village, Wood Buildings'):
			village_chance = 0
		else:
			village_chance = 2
		
		roll = libtcod.random_get_int(0, 1, 100)
		
		if roll <= pond_chance:
			map_hex.SetTerrainType('Pond')
			continue
		
		roll -= pond_chance
		
		if roll <= forest_chance:
			map_hex.SetTerrainType('Sparse Forest')
			continue
		
		roll -= forest_chance
			
		if roll <= field_chance:
			map_hex.SetTerrainType('In-Season Fields')
			continue
		
		roll -= field_chance
		
		if roll <= village_chance:
			map_hex.SetTerrainType('Village, Wood Buildings')
	
	# add a road running from the bottom to the top of the map
	path = GetHexPath(5, 10, 8, -4)
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



##########################################################################################
#                                 Scenario Animations                                    #
##########################################################################################

# show an ordinance attack firing animation
def OrdAttackAnimation(attack_obj):
	
	# redraw screen consoles to clear any old GUI display
	DrawScreenConsoles()
	if attack_obj.attacker == scenario.player_psg or attack_obj.target == scenario.player_psg:
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
	libtcod.console_flush()
	
	# use draw locations, but we'll be drawing to the GUI console so
	#   modify by -30, -1
	x1, y1 = attack_obj.attacker.screen_x-30, attack_obj.attacker.screen_y-1
	x2, y2 = attack_obj.target.screen_x-30, attack_obj.target.screen_y-1
	
	# projectile animation
	line = GetLine(x1, y1, x2, y2, los=True)
	
	pause_time = config.getint('ArmCom2', 'animation_speed')
	pause_time2 = int(pause_time / 2)
	
	for (x, y) in line:
		UpdateGUIConsole()
		libtcod.console_put_char_ex(map_gui_con, x, y, 250,
			libtcod.white, libtcod.black)
		DrawScreenConsoles()
		if attack_obj.attacker == scenario.player_psg or attack_obj.target == scenario.player_psg:
			libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
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
		if attack_obj.attacker == scenario.player_psg or attack_obj.target == scenario.player_psg:
			libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
		libtcod.console_flush()
		Wait(pause_time2)
		
	libtcod.console_clear(map_gui_con)
	DrawScreenConsoles()
	libtcod.console_flush()


# show a small arms / MG firing animation
def IFTAttackAnimation(attack_obj):
	
	# redraw screen consoles to clear any old GUI display
	DrawScreenConsoles()
	if attack_obj.attacker == scenario.player_psg or attack_obj.target == scenario.player_psg:
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
	libtcod.console_flush()
	
	# use draw locations, but we'll be drawing to the GUI console so
	#   modify by -30, -1
	x1, y1 = attack_obj.attacker.screen_x-30, attack_obj.attacker.screen_y-1
	x2, y2 = attack_obj.target.screen_x-30, attack_obj.target.screen_y-1
	
	line = GetLine(x1, y1, x2, y2, los=True)
	
	# TODO: different animation depending on weapon class (MG / SA)
	
	pause_time = config.getint('ArmCom2', 'animation_speed')
	
	for i in range(20):
		(x,y) = choice(line[:-1])
		libtcod.console_clear(map_gui_con)
		libtcod.console_put_char_ex(map_gui_con, x, y, 250,
			libtcod.red, libtcod.black)
		DrawScreenConsoles()
		if attack_obj.attacker == scenario.player_psg or attack_obj.target == scenario.player_psg:
			libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
		libtcod.console_flush()
		Wait(pause_time)
	
	libtcod.console_clear(map_gui_con)
	DrawScreenConsoles()
	if attack_obj.attacker == scenario.player_psg or attack_obj.target == scenario.player_psg:
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
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
	
	# TEMP: draw roads and rivers overtop
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
		if scenario.current_phase == 1 and psg.selected_weapon is not None:
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
	if scenario.current_phase == 0:
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
	#elif psg.dug_in:
	#	libtcod.console_print(psg_con, 0, 19, 'Dug-in')
	#elif psg.hull_down > -1:
	#	text = 'HD '
		# TODO: add directional character
	#	libtcod.console_print(psg_con, 0, 19, text)
	
	# fired last turn
	if psg.fired:
		libtcod.console_print_ex(psg_con, 23, 19, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'Fired')

	
	# negative status flags
	libtcod.console_set_default_foreground(psg_con, libtcod.light_red)
	libtcod.console_set_default_background(psg_con, libtcod.darkest_red)
	libtcod.console_rect(psg_con, 0, 20, 24, 1, False, libtcod.BKGND_SET)
	if psg.pinned:
		libtcod.console_print(psg_con, 0, 20, 'Pinned')
	
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
	text = PHASE_NAMES[scenario.current_phase]
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

				# number of steps in PSG and name of squads/vehicles
				text = str(psg.num_steps) + ' ' + psg.GetStepName()
				libtcod.console_print(hex_info_con, 0, 3+n, text)
				
				if psg.pinned:
					libtcod.console_print(hex_info_con, 0, 6, 'Pinned')
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
	if scenario.active_psg is not None:
		libtcod.console_set_char_background(con, scenario.active_psg.screen_x,
			scenario.active_psg.screen_y, SELECTED_HL_COL, flag=libtcod.BKGND_SET)
	
		# highlight targeted PSG if any
		psg = scenario.active_psg.target_psg
		if psg is not None:
			libtcod.console_set_char_background(con, psg.screen_x, psg.screen_y,
				TARGET_HL_COL, flag=libtcod.BKGND_SET)
			
			# TEMP - show LoS hexes
			los_line = GetLoS(scenario.active_psg.hx, scenario.active_psg.hy,
				psg.hx, psg.hy)
			
			for (hx, hy) in los_line:
				(x,y) = PlotHex(hx, hy)
				x += 26
				y += 3
				libtcod.console_set_char(con, x, y, 250)
				libtcod.console_set_char_foreground(con, x, y, libtcod.red)
			
			# draw LoS line
			#line = GetLine(scenario.active_psg.screen_x, scenario.active_psg.screen_y,
			#	psg.screen_x, psg.screen_y)
			#for (x, y) in line[2:-1]:
			#	libtcod.console_set_char(con, x, y, 250)
			#	libtcod.console_set_char_foreground(con, x, y, libtcod.red)
	
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
	libtcod.console_print_ex(temp, 13, 1, libtcod.BKGND_NONE, libtcod.CENTER,
		'Scenario')
	libtcod.console_set_default_foreground(temp, HIGHLIGHT_COLOR)
	libtcod.console_print_ex(temp, 13, 2, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.name)
	libtcod.console_set_default_foreground(temp, libtcod.white)
	
	# scenario description
	lines = wrap(scenario.description, 25)
	n = 0
	for line in lines:
		libtcod.console_print(temp, 1, 5+n, line)
		n += 1
	
	# battlefront, date, and start time
	libtcod.console_print_ex(temp, 13, 20, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.battlefront)
	text = MONTH_NAMES[scenario.month] + ' ' + str(scenario.year)
	libtcod.console_print_ex(temp, 13, 21, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	text = str(scenario.hour) + ':' + str(scenario.minute).zfill(2)
	libtcod.console_print_ex(temp, 13, 22, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	
	# forces on both sides
	# TODO: this info should be part of scenario object as well
	libtcod.console_set_default_foreground(temp, HIGHLIGHT_COLOR)
	libtcod.console_print(temp, 1, 25, 'Your Forces')
	libtcod.console_print(temp, 1, 31, 'Expected Resistance')
	libtcod.console_set_default_foreground(temp, libtcod.white)
	libtcod.console_print(temp, 2, 26, 'German Heer')
	libtcod.console_print(temp, 2, 27, 'Armoured Battlegroup')
	libtcod.console_print(temp, 2, 32, 'Polish Army')
	libtcod.console_print(temp, 2, 33, 'Armoured and Infantry')
	
	# objectives
	libtcod.console_set_default_foreground(temp, HIGHLIGHT_COLOR)
	libtcod.console_print(temp, 1, 38, 'Objectives')
	libtcod.console_set_default_foreground(temp, libtcod.white)
	text = (scenario.objectives + ' by ' + str(scenario.hour_limit) + ':' +
		str(scenario.minute_limit).zfill(2))
	lines = wrap(text, 25)
	n = 0
	for line in lines:
		libtcod.console_print(temp, 1, 40+n, line)
		n += 1
	
	# list of menu commands
	libtcod.console_set_default_foreground(temp, HIGHLIGHT_COLOR)
	libtcod.console_print(temp, 1, 52, 'ESC')
	libtcod.console_print(temp, 15, 52, 'Enter')
	libtcod.console_set_default_foreground(temp, libtcod.white)
	libtcod.console_print(temp, 5, 52, 'Cancel')
	libtcod.console_print(temp, 21, 52, 'Start')
	
	libtcod.console_blit(temp, 0, 0, 0, 0, 0, 27, 3)
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
		libtcod.console_blit(scen_menu_con, 0, 0, 0, 0, 0, 5, 3)
		cmd_menu.DisplayMe(0, WINDOW_XM-12, 24, 25)
	
	# use the buffer console to darken the screen background
	libtcod.console_clear(con)
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0, 
		0.0, 0.7)
	
	# build menu of basic options
	cmd_menu = CommandMenu('scenario_menu')
	cmd_menu.AddOption('save_and_quit', 'Q', 'Save and Quit', desc='Save the scenario ' +
		'in progress and quit to the Main Menu')
	cmd_menu.AddOption('return', 'Esc', 'Return to Scenario', desc='Return and continue ' +
		'playing the scenario in progress')
	
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
		Wait(100)
		
		if option.option_id == 'save_and_quit':
			SaveGame()
			return True
		elif option.option_id == 'return':
			return False
		


def DoScenario(load_savegame=False):
	
	global scenario
	global terrain_types
	# screen consoles
	global scen_menu_con, bkg_console, map_terrain_con, map_fov_con, map_gui_con
	global unit_con, psg_con, cmd_con, attack_con, scen_info_con
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
		scenario.hour_limit = 10
		scenario.minute_limit = 0
		
		# display scenario info: chance to cancel start
		if not ScenarioSummary():
			del scenario
			return
		
		# spawn the player PSGs
		new_psg = PSG('HQ Panzer Squadron', 'Panzer 35t', 5, 0, 0, 5, 5)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(5, 10)
		
		new_psg = PSG('Light Panzer Squadron', 'Panzer II A', 5, 0, 0, 5, 5)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(6, 9)
		
		new_psg = PSG('Light Panzerspäh Platoon', 'sd_kfz_221', 3, 0, 0, 5, 5)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(7, 9)
		
		new_psg = PSG('Schützen Platoon', 'german_schutzen', 5, 0, 0, 4, 5)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(8, 9)
		
		
		# select the first player PSG
		scenario.SelectNextPSG()
		
		# set up our objectives
		scenario.hex_map.AddObjectiveAt(5, 3)
		scenario.hex_map.AddObjectiveAt(6, -2)
		
		# set up enemy PSGs
		new_psg = PSG('HQ Tank Squadron', '7TP jw', 3, 3, 1, 4, 4)
		new_psg.ai = AI(new_psg)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(2, 4)
		
		new_psg = PSG('AT Gun Section', '37mm wz. 36', 2, 3, 1, 4, 4)
		new_psg.ai = AI(new_psg)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(8, 0)
		
		new_psg = PSG('Piechoty Platoon', 'polish_piechoty', 5, 3, 1, 4, 4)
		new_psg.ai = AI(new_psg)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(6, -2)
		
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
	
	
	##################################################################################
	#     Main Campaign Day Loop
	##################################################################################

	# to trigger when mouse cursor has moved on screen
	mouse_x = -1
	mouse_y = -1
	
	exit_scenario = False
	while not exit_scenario:
		
		libtcod.console_flush()
		
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			key, mouse)
		
		# TEMP: emergency exit
		if libtcod.console_is_window_closed(): sys.exit()
		
		UpdateScreen()
		
		# save the game in progress at this point
		SaveGame()
		
		while not exit_scenario:
			
			libtcod.console_flush()
		
			libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
				key, mouse)
			
			# TEMP: emergency escape
			if libtcod.console_is_window_closed(): sys.exit()
			
			# check to see if mouse cursor has moved
			if mouse.cx != mouse_x or mouse.cy != mouse_y:
				mouse_x = mouse.cx
				mouse_y = mouse.cy
				UpdateHexInfoConsole()
				DrawScreenConsoles()
			
			##### Mouse Commands #####
			#if mouse.rbutton:
				
			
			#elif mouse.lbutton:
			
			# open scenario menu screen
			if key.vk == libtcod.KEY_ESCAPE:
				if ScenarioMenu():
					exit_scenario = True
				else:
					DrawScreenConsoles()
				continue
			
			
			##### AI Actions #####
			if scenario.active_player == 1:
				scenario.DoAIPhase()
				scenario.NextPhase()
				UpdateScreen()
				continue
			
			
			##### Player Keyboard Commands #####
			
			# skip this section if no commands in buffer
			if key is None: continue
			
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
			#Wait(100)
			
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
				InitAttack(scenario.active_psg, scenario.active_psg.target_psg, area_fire)
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
global mouse, key, con

# try to load game settings from config file
LoadCFG()

# set up basic stuff
os.putenv('SDL_VIDEO_CENTERED', '1')		# center window on screen

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

libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER,
	'Loading ...')
libtcod.console_flush()

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()

# set up colour control for highlighting command keys
libtcod.console_set_color_control(libtcod.COLCTRL_1, KEY_HIGHLIGHT_COLOR, libtcod.black)



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
libtcod.console_print_ex(main_menu_con, WINDOW_WIDTH-1, 0, libtcod.BKGND_NONE, libtcod.RIGHT, VERSION + SUBVERSION)
libtcod.console_set_default_foreground(main_menu_con, libtcod.light_grey)
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-4,
	libtcod.BKGND_NONE, libtcod.CENTER, 'Copyright 2016-2017' )
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-3,
	libtcod.BKGND_NONE, libtcod.CENTER, 'Free Software under the GNU GPL')
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-2,
	libtcod.BKGND_NONE, libtcod.CENTER, 'www.armouredcommander.com')

libtcod.console_set_default_foreground(main_menu_con, libtcod.white)

# build main menus
menus = []

cmd_menu = CommandMenu('main_menu')
menu_option = cmd_menu.AddOption('continue_scenario', 'C', 'Continue')
if not os.path.exists('savegame'): menu_option.inactive = True
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
	active_menu.DisplayMe(0, WINDOW_XM-10, 36, 18)
	
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



# TEMP - jump right into the scenario
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
	Wait(100)
	
	# main menu
	if option.option_id == 'continue_scenario':
		DoScenario(load_savegame=True)
		active_menu = menus[0]
		UpdateScreen()
	elif option.option_id == 'new_scenario':
		DoScenario()
		active_menu = menus[0]
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

