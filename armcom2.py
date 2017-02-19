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
##########################################################################################

# debug constants, should all be set to False in distribution version
NO_AI = False			# AI is disabled, non-player units will only ever wait
AI_REPORTS = True		# AI reports are printed to console
AI_DISPLAY = False		# AI calculations are displayed to the screen
VIEW_ALL = False		# Player can see all hexes on viewport


NAME = 'Armoured Commander II'
VERSION = 'Proof of Concept'				# determines saved game compatability
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
MAX_LOS_DISTANCE = 13					# maximum distance that a Line of Sight can be drawn
SUPPRESSED_PENALTY = -3					# penalty to morale level for being suppressed
ELEVATION_M = 20.0					# each elevation level represents x meters of height
WEAPON_ARC = 31						# 1/2 width of weapon arcs in degrees
MAX_GUARD_DISTANCE = 2					# maximum distance beyond which a PSG that is guarding
							#   a friendly PSG gets worried


# Colour definitions
OPEN_GROUND_COL = libtcod.Color(0, 64, 0)
WATER_COL = libtcod.Color(0, 0, 217)
FOREST_COL = libtcod.Color(0, 140, 0)
FOREST_BG_COL = libtcod.Color(0, 40, 0)
FIELDS_COL = libtcod.Color(102, 102, 0)
RIVER_BG_COL = libtcod.Color(0, 0, 217)			# background color for river edges
DIRT_ROAD_COL = libtcod.Color(50, 40, 25)		# background color for dirt roads

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
	'8' : 'Regular',
	'9' : 'Confident',
	'10' : 'Fearless',
	'11' : 'Fanatic'
}
SKILL_DESC = {
	'7': 'Green',
	'8' : '2nd Line',
	'9' : '1st Line',
	'10' : 'Veteran',
	'11' : 'Elite'
}

PHASE_NAMES = ['Movement', 'Shooting']

MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June',
	'July', 'August', 'September', 'October', 'November', 'December']

DESTHEX = [(0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0)]	# change in hx, hy values for hexes in each direction
PLOT_DIR = [(0,-1), (1,-1), (1,1), (0,1), (-1,1), (-1,-1)]	# position of direction indicator
TURRET_CHAR = [254, 47, 92, 254, 47, 92]			# characters to use for turret display

# infantry fire table values
# K# - PSG loses this number of steps
# M# - PSG must pass a Morale test for each step with # modifier or else step is lost
# S# - suppression test with # modifier
# NA - No effect
#
# 4 FP roughly equal to one rifle platoon w/ 3 inherent MGs
#

# TODO: update this table

#               0    1     2     3     4     5     6     7     8     9     10    11    12    13    14    15
IFT_TABLE = {
	'1' : ['K1', 'K1', 'K1', 'M0', 'S1', 'S0', 'S0', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA'],
	'2' : ['K2', 'K1', 'K1', 'M0', 'S1', 'S1', 'S1', 'S0', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA'],
	'3' : ['K2', 'K1', 'K1', 'M0', 'S1', 'S1', 'S1', 'S0', 'S0', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA'],
	'4' : ['K2', 'K1', 'K1', 'M1', 'M0', 'S1', 'S1', 'S1', 'S1', 'S0', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA'],
	'5' : ['K2', 'K1', 'K1', 'M1', 'M0', 'S1', 'S1', 'S0', 'S1', 'S0', 'S0', 'NA', 'NA', 'NA', 'NA', 'NA'],
	'6' : ['K3', 'K2', 'K1', 'K1', 'M1', 'M0', 'S2', 'S1', 'S0', 'S1', 'S0', 'NA', 'NA', 'NA', 'NA', 'NA'],
	'7' : ['K3', 'K2', 'K1', 'K1', 'M1', 'M0', 'S2', 'S1', 'S0', 'S1', 'S0', 'S0', 'NA', 'NA', 'NA', 'NA'],
	'8' : ['K3', 'K2', 'K1', 'K1', 'M1', 'M1', 'M0', 'S2', 'S2', 'S1', 'S1', 'S1', 'S0', 'NA', 'NA', 'NA'],
	'9' : ['K3', 'K2', 'K1', 'K1', 'M1', 'M1', 'M0', 'S2', 'S2', 'S1', 'S1', 'S1', 'S0', 'S0', 'NA', 'NA'],
	'10' : ['K3', 'K2', 'K1', 'K1', 'M2', 'M1', 'M0', 'S3', 'S2', 'S2', 'S1', 'S1', 'S1', 'S0', 'NA', 'NA'],
	'12' : ['K4', 'K3', 'K2', 'K1', 'K1', 'M2', 'M1', 'M0', 'S3', 'S3', 'S2', 'S2', 'S2', 'S1', 'S0', 'NA'],
	'16' : ['K4', 'K3', 'K2', 'K1', 'K1', 'M3', 'M2', 'M1', 'M0', 'S4', 'S3', 'S2', 'S2', 'S2', 'S2', 'S1'],
	'20' : ['K5', 'K4', 'K3', 'K2', 'K1', 'M3', 'M2', 'M1', 'M0', 'S4', 'S3', 'S2', 'S2', 'S2', 'S2', 'S1']
}


##########################################################################################
#                                         Classes                                        #
##########################################################################################

# terrain type: determines effect of different types of map hex terrain
class TerrainType:
	def __init__(self):
		self.console = []
		self.display_name = ''
		self.los_height = 0
		self.base_image = ''
		self.modifier_matrix = []
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
	
	# return the modifier for the given psg if it were in this terrain
	def GetModifier(self, psg):
		if psg.infantry:
			if psg.moved:
				return int(self.modifier_matrix[0])
			elif psg.dug_in:
				return int(self.modifier_matrix[1])
			return int(self.modifier_matrix[2])
		elif psg.gun:
			if psg.moved:
				return int(self.modifier_matrix[3])
			elif psg.dug_in:
				return int(self.modifier_matrix[4])
			return int(self.modifier_matrix[5])
		elif psg.vehicle:
			if not psg.recce:
				if psg.moved:
					return int(self.modifier_matrix[6])
				else:
					return int(self.modifier_matrix[7])
			else:
				if psg.moved:
					return int(self.modifier_matrix[8])
				else:
					return int(self.modifier_matrix[9])
		print 'ERROR: unable to calculate terrain modifier'
		return 0


# Attack class, used for attack objects holding scores to use in an attack
# generated by CalcTH or CalcIFT
class Attack:
	def __init__(self, attacker, weapon, target):
		self.attacker = attacker
		self.weapon = weapon
		self.target = target
		self.ift_attack = False
		self.th_attack = False
		self.base_fp = 0
		self.final_fp = 0
		self.fp_mods = []
		self.column = 0
		self.drm = []
		self.total_mod = 0
		self.base_th = 0
		self.roll_req = 0


##########################################################################################
#                                        AI Class                                        #
##########################################################################################

# AI class, assigned to all PSGs including player PSG
class AI:
	def __init__(self, owner):
		self.owner = owner		# pointer to owning PSG object


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
			# background dots
			libtcod.console_set_default_foreground(console, libtcod.darker_grey)
			for x1 in range(x, x+w, 3):
				libtcod.console_put_char(console, x1, y+n, '-')
			
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
				libtcod.console_print_ex(console, x+w-1, y+n, libtcod.BKGND_NONE,
					libtcod.RIGHT, line)
				n+=1
			
			n += 1
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
						libtcod.console_print(console,
							x, y+max_n+2+n,	line)
						n += 1
				
				break
						
			n += menu_option.h + 1
		libtcod.console_set_default_foreground(console, original_fg)
		


# platoon-sized group class
# represents a platoon, squadron, battery, etc.
class PSG:
	def __init__(self, name, unit_id, num_steps, facing, turret_facing, owning_player, skill_lvl, morale_lvl):
		self.unit_id = unit_id			# unique ID for unit type of this PSG
		self.name = name			# name, eg. 'Tank Squadron'
		self.step_name = ''			# name of individual teams / vehicles w/in this PSG
		self.num_steps = num_steps		# number of unit steps in this PSG
		self.portrait = None			# portrait filename if any
		self.ai = AI(self)			# AI object
		
		self.hx = 0				# hex location of this PSG, will be set
		self.hy = 0				#   by SpawnAt()
		self.screen_x = 0			# draw location on the screen
		self.screen_y = 0			#   set by DrawMe()
		self.anim_offset_x = 0			# offset used for movement animation
		self.anim_offset_y = 0
		
		self.facing = facing			# facing direction, for vehicles this
							#   is their hull facing
		self.turret_facing = turret_facing	# turret facing if any
		
		self.movement_class = ''		# movement class
		self.armour = None			# armour ratings if any
		
		self.weapon_list = []			# list of weapons
		self.selected_weapon = None		# currently selected weapon
		
		self.target_list = []			# list of possible targets
		self.target_psg = None			# currently targeted PSG
		
		self.acquired_target = None		# PSG has acquired this unit as target
		self.acquired_target_lvl = 0		# level of acquired (-1, or -2)
		self.acquired_by = []			# PSG has been acquired by this unit(s)
		
		self.infantry = False			# PSG type flags
		self.gun = False
		self.vehicle = False
		
		self.recce = False			# unit has recce abilities
		
		self.owning_player = owning_player	# player that controls this PSG
		self.display_char = ''			# character to display on map, set below
		
		self.skill_lvl = skill_lvl		# skill and morale levels
		self.morale_lvl = morale_lvl
		
		# action flags
		self.moved = False
		self.fired = False
		self.changed_facing = False
		self.changed_turret_facing = False
		
		# status flags
		self.dug_in = False			# only infantry units and guns can dig in
		self.hull_down = -1			# only vehicles can be hull down, number
							#   is direction
		
		self.hidden = True			# PSG is not visible to enemy side
		self.pinned = False			# move N/A, attacks less effective
		self.bogged = False			# move N/A
		self.suppressed = False			# move/fire N/A, penalty to morale
		self.melee = False			# held in melee
		
		self.max_tu = 36			# TU allowance per turn
		self.tu = 36				# remaining TU - can be negative, deficit
							#   is removed at start of next turn
		
		self.max_mp = 6				# maximum Movement Points per turn
		self.mp = 6				# current mp
		
		# load stats from data file
		self.LoadStats()
		
		# set initial display character
		self.display_char = self.GetDisplayChar()
		
		# select first weapon by default
		if len(self.weapon_list) > 0:
			self.selected_weapon = self.weapon_list[0]

	# return description of PSG
	# if using real name, transcode it to handle any special characters in it
	# if true_name, return the real identity of this PSG no matter what
	def GetName(self, true_name=False):
		if not true_name:
			if self.owning_player == 1 and self.hidden:
				return 'Possible Enemy PSG'
		return self.name.decode('utf8').encode('IBM850')

	# return the name of a single step within this PSG
	def GetStepName(self):
		return self.step_name.decode('utf8').encode('IBM850')

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
				if psg.hidden: continue
				# check range
				normal_range = self.selected_weapon.stats['normal_range']
				if GetHexDistance(self.hx, self.hy, psg.hx, psg.hy) > normal_range:
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
		self.acquired_target_lvl = 0
		self.acquired_by = []
		for psg in scenario.psg_list:
			if self in psg.acquired_by:
				psg.acquired_by.remove(self)
			if psg.acquired_target == self:
				psg.acquired_target = None
				psg.acquired_target_lvl = 0

	# remove this PSG from the game
	def DestroyMe(self):
		scenario.psg_list.remove(self)
		# clear acquired target records
		self.ClearAcquiredTargets()

	# do any automatic actions for start of current phase
	def ResetForPhase(self):
		# start of movement phase
		if scenario.current_phase == 0:
			self.moved = False
			self.changed_facing = False
			self.changed_turret_facing = False
		elif scenario.current_phase == 1:
			self.fired = False

	# roll for recovery from negative statuses
	def DoRecoveryTests(self):
		if self.pinned or self.suppressed:
			morale_lvl = self.morale_lvl
			
			if self.suppressed:
				morale_lvl += SUPPRESSED_PENALTY
			terrain_mod = GetHexAt(self.hx, self.hy).terrain_type.GetModifier(self)
			if terrain_mod > 0:
				morale_lvl += terrain_mod
			
			if morale_lvl < 2:
				morale_lvl = 2
			elif morale_lvl > 11:
				morale_lvl = 11
			
			# do the roll
			d1, d2, roll = Roll2D6()
			if roll <= morale_lvl:
				if self.pinned:
					text = self.GetName() + ' recovers from being Pinned.'
					Message(self.screen_x, self.screen_y, text)
					self.pinned = False
				else:
					text = self.GetName() + ' recovers from being Suppressed.'
					Message(self.screen_x, self.screen_y, text)
					self.suppressed = False

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
					ord_weapons = weapon_list.findall('ord_weapon')
					if ord_weapons is not None:
						for weapon_item in ord_weapons:
							new_weapon = SpawnORDWeapon(weapon_item)
							self.weapon_list.append(new_weapon)
					ift_weapons = weapon_list.findall('ift_weapon')
					if ift_weapons is not None:
						for weapon_item in ift_weapons:
							new_weapon = SpawnIFTWeapon(weapon_item)
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
					self.armour = {}
					armour_ratings = item.find('armour')
					turret_ratings = armour_ratings.find('turret')
					self.armour['turret_front'] = int(turret_ratings.find('front').text)
					self.armour['turret_side'] = int(turret_ratings.find('side').text)
					hull_ratings = armour_ratings.find('hull')
					self.armour['hull_front'] = int(hull_ratings.find('front').text)
					self.armour['hull_side'] = int(hull_ratings.find('side').text)
				
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
	
	# remove one or more steps from this PSG, also check for PSG removal
	def RemoveSteps(self, step_num, skip_msg=False):
		
		if step_num == 0: return
		
		for i in range(step_num):
			
			if self.num_steps > 1:
				if not skip_msg:
					text = 'A ' + self.step_name + ' was destroyed!'
					Message(self.screen_x, self.screen_y, text)
				self.num_steps -= 1
				continue
			
			self.num_steps = 0
			text = self.GetName() + ' has been destroyed!'
			Message(self.screen_x, self.screen_y, text)
			self.DestroyMe()
			UpdateUnitConsole()
			return
		
		text = self.GetName() + ' is Pinned.'
		Message(self.screen_x, self.screen_y, text)
		self.pinned = True
		
	# this PSG has been revealed by enemy forces
	def RevealMe(self):
		self.hidden = False

		# update unit console to display
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		
		# TEMP - no message
		return
		
		# show message
		if self.owning_player == 0:
			text = 'Your '
		else:
			text = 'Enemy '
		text += self.GetName() + ' has been spotted!'
		Message(self.screen_x, self.screen_y, text)
	
	# regain Hidden status for this PSG
	def HideMe(self):
		#if self.owning_player == 0:
		#	text = self.GetName() + ' is now Hidden'
		#else:
		#	text = 'Lost contact with ' + self.GetName()
		#Message(self.screen_x, self.screen_y, text)
		self.hidden = True
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
	
	# get display character to be used on hex map
	def GetDisplayChar(self):
		
		# enemy Hidden PSG
		if self.owning_player == 1 and self.hidden:
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
			# turreted vehicle
			if self.turret_facing is not None:
				
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
		(x,y) = PlotHex(self.hx, self.hy)
		# record draw position on screen
		self.screen_x = x + 26
		self.screen_y = y + 3
		
		self.display_char = self.GetDisplayChar()
		
		# determine foreground color to use
		if self.owning_player == 1:
			if self.hidden:
				col = libtcod.dark_red
			else:
				col = libtcod.red
		else:	
			if self.hidden:
				col = libtcod.light_grey
			else:
				col = libtcod.white
		libtcod.console_put_char_ex(unit_con, x+self.anim_offset_x,
			y+self.anim_offset_y, self.display_char, col,
			libtcod.black)
		
		# determine if we need to display a turret
		display_turret = True
		
		if not self.vehicle and not self.gun:
			display_turret = False
		elif self.owning_player == 1 and self.hidden:
			display_turret = False
		elif not self.gun and self.turret_facing is None:
			display_turret = False
		
		if not display_turret: return
		
		# guns use their hull facing
		if self.gun:
			facing = self.facing
		else:
			facing = self.turret_facing
		
		# determine location to draw turret character
		x_mod, y_mod = PLOT_DIR[facing]
		char = TURRET_CHAR[facing]
		libtcod.console_put_char_ex(unit_con, x+x_mod+self.anim_offset_x,
			y+y_mod+self.anim_offset_y, char, col, libtcod.black)
	
	# pivot the hull of this PSG so it faces the given direction
	# TEMP? turret if any is rotated to face this direction too
	def PivotToFace(self, direction):
		if self.facing is None: return
		self.facing = direction
		self.changed_facing = True
		if self.turret_facing is not None:
			self.turret_facing = direction
		
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
		
		# TODO: spend the mp
		
		
		# see if a hull pivot is required
		if self.movement_class != 'Infantry':
			if self.facing is not None:
				direction = GetDirectionToAdjacent(self.hx, self.hy,
					new_hx, new_hy)
				self.PivotToFace(direction)
			
		# record movement vector
		hx_diff = new_hx - self.hx
		hy_diff = new_hy - self.hy
		self.last_move = (hx_diff, hy_diff)
		
		# display movement animation if not player psg
		# TEMP: disabled
		#if self is not scenario.player_psg:
		#	DisplayMoveAnimation(self, new_hx, new_hy)
		
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
			scenario.DoHiddenCheck()
		
		UpdateUnitConsole()
		
		return True
		
	# resolve an IFT attack against this PSG
	def ResolveIFTAttack(self, attack_obj):
		
		# display dice roll animation if player is involved
		if attack_obj.attacker == scenario.player_psg or attack_obj.target == scenario.player_psg:
		
			# roll dice and display results on attack console
			pause_time = config.getint('ArmCom2', 'animation_speed') * 10
			for i in range(3):
				d1, d2, roll = Roll2D6()
				DrawDie(attack_con, 12, 42, d1)
				DrawDie(attack_con, 17, 42, d2)
				libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
				libtcod.console_flush()
				# TODO: play sound
				Wait(pause_time)
				
			# display roll result on attack console
			# TODO: highlight result too
			libtcod.console_rect(attack_con, 1, 8, 48, 1, False, libtcod.BKGND_SET)
			libtcod.console_print_ex(attack_con, 15, 48, libtcod.BKGND_NONE,
				libtcod.CENTER, 'Roll: ' + str(roll))
			
			libtcod.console_print_ex(attack_con, 15, 57, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Enter to Continue')
			
			libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
			libtcod.console_flush()
			WaitForEnter()
		
		else:
			d1, d2, roll = Roll2D6()
		
		# apply modifiers to roll, limit modified roll to 0-15
		mod_roll = roll + attack_obj.total_mod
		if mod_roll < 0:
			mod_roll = 0
		elif mod_roll > 15:
			mod_roll = 15
		
		# get result
		result = attack_obj.column[mod_roll]
		
		# no effect
		if result == 'NA':
			text = 'No effect.'
			Message(self.screen_x, self.screen_y, text)
			return
		
		# PSG is revealed if hidden
		if self.hidden:
			self.RevealMe()
		
		# one or more steps removed
		if result[0] == 'K':
			kill_num = int(result[1])
			if kill_num > self.num_steps: kill_num = self.num_steps
			self.RemoveSteps(kill_num)
		
		# each step must morale test or be destroyed
		elif result[0] == 'M':
			self.MoraleTest(int(result[1]))
		
		# suppression test
		elif result[0] == 'S':
			self.SupressionTest(int(result[1]))
	
	# resolve a to-hit attack against this PSG
	def ResolveToHitAttack(self, attack_obj):
		
		# display dice roll animation if player is involved
		if attack_obj.attacker == scenario.player_psg or self == scenario.player_psg:
			
			# roll dice and display results on attack console
			pause_time = config.getint('ArmCom2', 'animation_speed') * 10
			for i in range(3):
				d1, d2, roll = Roll2D6()
				DrawDie(attack_con, 12, 42, d1)
				DrawDie(attack_con, 17, 42, d2)
				libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
				libtcod.console_flush()
				# TODO: play sound
				Wait(pause_time)
				
			# display roll result on attack console
			# TODO: highlight result too
			libtcod.console_rect(attack_con, 1, 8, 48, 1, False, libtcod.BKGND_SET)
			libtcod.console_print_ex(attack_con, 15, 48, libtcod.BKGND_NONE,
				libtcod.CENTER, 'Roll: ' + str(roll))
			
			libtcod.console_print_ex(attack_con, 15, 57, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Enter to Continue')
			
			libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
			libtcod.console_flush()
			WaitForEnter()
		
		else:
			d1, d2, roll = Roll2D6()
		
		# apply modifiers to roll, limit modified roll to 2-12
		mod_roll = roll + attack_obj.total_mod
		if mod_roll < 2:
			mod_roll = 2
		elif mod_roll > 12:
			mod_roll = 12
		
		# determine number of hits from final modified roll
		gun_roll = libtcod.random_get_int(0, 1, attack_obj.attacker.num_steps)
		if mod_roll <= int(floor(attack_obj.roll_req / 2)):
			total_hits = gun_roll * 2
		elif mod_roll <= attack_obj.roll_req:
			total_hits = gun_roll
		elif mod_roll < (attack_obj.roll_req * 2):
			total_hits = int(floor(gun_roll / 2))
		else:
			total_hits = 0
		if total_hits > attack_obj.attacker.num_steps:
			total_hits = attack_obj.attacker.num_steps
		
		# resolve hits if any
		if total_hits > 0:
			
			text = str(total_hits) + ' hit'
			if total_hits > 1: text += 's'
			Message(self.screen_x, self.screen_y, text)
			
			# TEMP: shells magically transform based on target type
			
			# AP attack
			if self.vehicle:
				for h in range(total_hits):
					self.ResolveAPHit(attack_obj)
					# add extra pause to distinguish 2+ messages
					Wait(config.getint('ArmCom2', 'message_pause_time'))
					# possible that PSG was destroyed; don't try to resolve
					#   further hits
					if self not in scenario.psg_list:
						break
			
			# HE attack
			else:
				
				# calculate the IFT attack of HE hit(s)
				hit_object = CalcIFT(attack_obj.attacker,
					attack_obj.weapon, attack_obj.target,
					hit_result=True, multiple_hits=total_hits)
				
				# display hit result IFT and resolve it
				if attack_obj.attacker == scenario.player_psg or self == scenario.player_psg:
					DisplayIFTRoll(hit_object, hit_result=True)
					WaitForEnter()
				self.ResolveIFTAttack(hit_object)
		
		else:
			Message(self.screen_x, self.screen_y, 'No hits')
	
	# take a supression test for this PSG
	def SupressionTest(self, modifier):
		
		# already supressed, one step takes a morale test instead
		if self.suppressed:
			text = self.GetName() + ' is already suppressed, one step takes a morale test.'
			Message(self.screen_x, self.screen_y, text)
			self.MoraleTest(modifier, total_to_test=1)
			return
		
		morale_lvl = self.morale_lvl - modifier
		if morale_lvl < 2:
			morale_lvl = 2
		elif morale_lvl > 11:
			morale_lvl = 11
		
		d1, d2, roll = Roll2D6()
		
		if roll > morale_lvl:
			text = self.GetName() + ' is suppressed!'
			Message(self.screen_x, self.screen_y, text)
			self.suppressed = True
		else:
			text = self.GetName() + ' passes its suppression test and is pinned instead.'
			Message(self.screen_x, self.screen_y, text)	
			self.pinned = True
	
	# take a morale test for each step, if they failed then they flee and are destroyed
	#   if total_to_test > 0, only test for maximum this many steps
	def MoraleTest(self, modifier, total_to_test=0):
		morale_lvl = self.morale_lvl - modifier
		if self.suppressed:
			morale_lvl += SUPPRESSED_PENALTY
			
		if morale_lvl < 2:
			morale_lvl = 2
		elif morale_lvl > 11:
			morale_lvl = 11
		
		steps_lost = 0
		
		if total_to_test == 0:
			total_to_test = self.num_steps
		for i in range(total_to_test):
			d1, d2, roll = Roll2D6()
			if roll > morale_lvl:
				steps_lost += 1
		
		if steps_lost == 0:
			text = self.GetName() + ' passed all its Morale Tests.'
		else:
			text = self.GetName() + ' lost ' + str(steps_lost) + ' step'
			if steps_lost > 1:
				text += 's'
			text += ' to failed morale and is Pinned!'
		Message(self.screen_x, self.screen_y, text)
		self.RemoveSteps(steps_lost, skip_msg=True)
		self.pinned = True
	
	# take a skill test, returning True if passed
	def SkillTest(self, modifier):
		skill_lvl = self.skill_lvl - modifier
		d1, d2, roll = Roll2D6()
		if roll <= skill_lvl:
			return True
		return False
	
	# resolve an AP hit against this PSG
	def ResolveAPHit(self, attack_obj):
		
		# determine hit location
		hit_location = GetHitLocation(False, GetFacing(attack_obj.attacker, self, False))
		if hit_location == 'Miss':
			Message(self.screen_x, self.screen_y, 'Target is Hull Down and was ' +
				'not hit.')
			return True
		turret = False
		if hit_location == 'Turret': turret = True
		
		# determine facing of hit location toward attacker
		facing = GetFacing(attack_obj.attacker, self, turret)
		
		(base_tk, roll_req, drm, total_mod) = CalcTK(attack_obj.attacker,
			attack_obj.weapon, self, facing, hit_location)
		
		# display to-kill info if attacker or target is player PSG
		if attack_obj.attacker == scenario.player_psg or self == scenario.player_psg:
			DisplayTKRoll(attack_obj.attacker, attack_obj.weapon, self, base_tk,
				roll_req, drm, total_mod)
		
		# not possible to penetrate
		if base_tk == -1 and roll_req == -1:
			Message(self.screen_x, self.screen_y, 'Not possible to damage ' +
				'target at this range.')
			return True
		
		# do to-kill roll
		d1, d2, roll = Roll2D6()
		
		if roll <= roll_req:
			# PSG is revealed if hidden
			if self.hidden:
				self.RevealMe()
			
			if hit_location == 'Track':
				text = ('A ' + self.step_name + ' has been immobilized ' +
					'and is out of action!')
			else:
				text = ('One ' + self.step_name + ' was hit in the ' + 
					hit_location + ' and was destroyed!')
			Message(self.screen_x, self.screen_y, text)
			self.RemoveSteps(1, skip_msg=True)
		else:
			Message(self.screen_x, self.screen_y, 'No effect.')
		

# Ordinance Weapon class: represents a larger HE or AP-firing gun
class OrdinanceWeapon:
	def __init__(self, stats):
		self.ift_weapon = False
		self.ord_weapon = True
		self.stats = stats
		self.reloading_tu = 0		# tu remaining before reloaded
	
	# return a descriptive name for this weapon
	def GetName(self):
		return str(self.stats['calibre']) + self.stats['long_range'] + ' Gun'


# IFT Weapon class: for MGs and small arms
class IFTWeapon:
	def __init__(self, stats):
		self.ift_weapon = True
		self.ord_weapon = False
		self.stats = stats
	
	# return a descriptive name for this weapon
	def GetName(self):
		return self.stats['name']
		

# a single terrain hex on the game map
# must have elevation and terrain type set before use
class MapHex:
	def __init__(self, hx, hy):
		self.hx = hx
		self.hy = hy
		self.elevation = None
		self.terrain_type = None
		
		self.objective = None			# type of objective if any
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
	
	# set this hex as an objective
	def SetObjective(self, objective_type):
		self.objective = objective_type
		scenario.objective_hexes.append(self)
	
	# capture this hex by whatever player has a PSG in it
	def CaptureMe(self):
		if self.objective is None: return False		# not an objective hex
		if len(self.contained_psgs) == 0: return False	# no PSG in hex
		psg = self.contained_psgs[0]
		if self.held_by == psg.owning_player: return False	# already captured
		self.held_by = psg.owning_player
		return True


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
				self.hexes[(hx,hy)].SetTerrainType('Open Ground')
				self.hexes[(hx,hy)].SetElevation(1)
				# add to list if on edge of map
				if hx == 0 or hx == w-1:
					self.edge_hexes.append((hx, hy))
				elif hy == hy_start or hy == hy_end-1:
					self.edge_hexes.append((hx, hy))
				
		self.vp_matrix = {}			# map viewport matrix
	
	# calculate field of view for human player
	def CalcFoV(self):
		
		# set all hexes to not visible to start
		for (hx, hy) in scenario.hex_map.hexes:
			map_hex = GetHexAt(hx, hy)
			map_hex.vis_to_player = False
		
		# debug mode
		if VIEW_ALL:
			for (hx, hy) in scenario.hex_map.hexes:
				map_hex = GetHexAt(hx, hy)
				map_hex.vis_to_player = True
			return
		
		# set all hex locations of player units to visible
		for psg in scenario.psg_list:
			if psg.owning_player == 1: continue
			GetHexAt(psg.hx, psg.hy).vis_to_player = True
		
		# run through each player unit and raycast to each remaining not visible hex
		for psg in scenario.psg_list:
			if psg.owning_player == 1: continue
			for (hx, hy) in scenario.hex_map.edge_hexes:
				map_hex = GetHexAt(hx, hy)
				visible_hexes = GetLoS(psg.hx, psg.hy, hx, hy)
				for (hx1, hy1) in visible_hexes:
					scenario.hex_map.hexes[(hx1, hy1)].vis_to_player = True

	# set a given hex on the campaign day map to a terrain type
	def SetHexTerrainType(self, hx, hy, terrain_type):
		self.hexes[(hx,hy)].terrain_type = terrain_type


# holds information about a scenario in progress
# on creation, also set the map size
class Scenario:
	def __init__(self, map_w, map_h):
		
		self.map_index = {}			# dictionary of console locations that
							#   correspond to map hexes
		
		self.year = 0				# current calendar year
		self.month = 0				# current calendar month
		self.name = ''				# scenario name
		
		self.active_player = 0			# currently active player (0 or 1)
		self.current_turn = 0			# current scenario turn
		self.max_turns = 0			# maximum turns before scenario end
		self.current_phase = 0			# current action phase
		
		self.psg_list = []			# list of all platoon-sized groups in play
		self.active_psg = None			# currently active PSG
		
		
		
		
		self.player_direction = 3		# direction of player-friendly forces
		self.enemy_direction = 0		# direction of enemy forces
		
		self.winner = None			# number of player that has won the scenario,
							#   None if no winner yet
		self.end_text = ''			# description of how scenario ended
		
		
		self.player_psg = None			# pointer to player-controlled PSG
		
		self.cmd_menu = CommandMenu('scenario_menu')		# current command menu for player
		self.active_cmd_menu = None		# currently active command menu
		
		self.messages = []			# list of game messages
		
		# create the hex map
		self.hex_map = HexMap(map_w, map_h)
		self.objective_hexes = []			# list of objective hexes
	
	# finish up current phase, start new phase (and possibly new turn as well)
	def NextPhase(self):
		
		# Movement -> Shooting Phase
		if self.current_phase == 0:
			self.current_phase = 1
			self.active_cmd_menu = 'shooting_root'
		
		# Shooting Phase -> New Active Player and Movement Phase
		elif self.current_phase == 1:
			
			# TEMP: skip enemy turn
			self.active_player = 1
			
			if self.active_player == 0:
				self.active_player = 1
			else:
				self.current_turn += 1
				UpdateScenInfoConsole()
				self.active_player = 0
			self.current_phase = 0
			self.active_cmd_menu = 'movement_root'
		
		# do automatic actions for active player's units for this phase
		for psg in self.psg_list:
			if psg.owning_player == self.active_player:
				psg.ResetForPhase()
		
		UpdatePSGConsole()
		self.BuildCmdMenu()
	
	# check to see if any enemy PSGs are newly visible or nto visible as a result of FoV changes
	def DoHiddenCheck(self):
		for psg in self.psg_list:
			if psg.owning_player == 0: continue
			map_hex = GetHexAt(psg.hx, psg.hy)
			if psg.hidden:
				if map_hex.vis_to_player:
					psg.RevealMe()
			else:
				if not map_hex.vis_to_player:
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
		DrawFrame(0, 4, 10, 80, 40)
		
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
	
	# given a PSG and a weapon system, return a list of hexes that could be targeted
	#   by the PSG-weapon combo
	def GetTargetHexes(self, psg, weapon):
		
		hex_list = []
		for (hx, hy) in GetHexRing(psg.hx, psg.hy, weapon.stats['normal_range']):
			los_list = GetLoS(psg.hx, psg.hy, hx, hy)
			for (hx1, hy1) in los_list:
				if (hx1, hy1) not in hex_list:
					hex_list.append((hx1, hy1))
		
		if not psg.infantry:
			# only keep hexes that are within the weapon arc
			(x1, y1) = PlotIdealHex(psg.hx, psg.hy)
			for (hx, hy) in reversed(hex_list):
				(x2, y2) = PlotIdealHex(hx, hy)
				bearing = RectifyHeading(GetBearing(x1, y1, x2, y2) -
					(psg.facing * 60))
				
				if bearing <= 180:
					if bearing > WEAPON_ARC:
						hex_list.remove((hx, hy))
				else:
					if bearing + WEAPON_ARC < 360:
						hex_list.remove((hx, hy))
		
		return hex_list
	
	# rebuild a list of commands for the command menu based on current phase and
	#   game state
	def BuildCmdMenu(self):
		
		# clear any existing command menu
		self.cmd_menu.Clear()
		
		# don't display anything if player is not active
		# TEMP - no AI right now so disabled
		#if scenario.active_player != 0:
		#	UpdateCmdConsole()
		#	return
		
		# all root menus get these commands
		if self.active_cmd_menu in ['movement_root', 'shooting_root']:
			self.cmd_menu.AddOption('select_unit', 'Tab', 'Select Next Unit')
			self.cmd_menu.AddOption('next_phase', 'Space', 'Next Phase')
		
		# movement phase menu
		if self.active_cmd_menu == 'movement_root':
			self.cmd_menu.AddOption('move_5', 'Q', 'Up and Left')
			self.cmd_menu.AddOption('move_0', 'W', 'Up')
			self.cmd_menu.AddOption('move_1', 'E', 'Up and Right')
			self.cmd_menu.AddOption('move_2', 'D', 'Down and Right')
			self.cmd_menu.AddOption('move_3', 'S', 'Down')
			self.cmd_menu.AddOption('move_4', 'A', 'Down and Left')
		
		# shooting phase menu
		elif self.active_cmd_menu == 'shooting_root':
			if not scenario.active_psg.fired:
				self.cmd_menu.AddOption('next_weapon', 'W', 'Select Next Weapon')
				self.cmd_menu.AddOption('next_target', 'T', 'Select Next Target')
				self.cmd_menu.AddOption('fire_target', 'F', 'Fire at Target')
		
		
		
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
		temp = item.find('modifier_matrix').text
		new_type.modifier_matrix = temp.split(',')
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


# draw an armcom2-style frame
def DrawFrame(console, x, y, w, h):
	libtcod.console_hline(console, x+1, y, w-1)
	libtcod.console_hline(console, x+1, y+h, w-1)
	libtcod.console_vline(console, x, y+1, h-1)
	libtcod.console_vline(console, x+w, y+1, h-1)
	libtcod.console_put_char(console, x, y, 249)
	libtcod.console_put_char(console, x+w, y, 249)
	libtcod.console_put_char(console, x, y+h, 249)
	libtcod.console_put_char(console, x+w, y+h, 249)


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
	
	
# calculate a score for a given attack, determining how effective it is likely to be
def ScoreAttack(attacker, weapon, target):
	# no LoS
	
	# check to see what the to-hit roll required would be
	attack_obj = CalcAttack(attacker, weapon, target)
	
	if attack_obj.th_attack:
		score = attack_obj.roll_req
	else:
		mod_roll = 7 + attack_obj.total_mod
		if mod_roll < 0:
			mod_roll = 0
		elif mod_roll > 15:
			mod_roll = 15
		result = attack_obj.column[mod_roll]
		if result == 'NA':
			score = 4
		elif result[0] == 'K':
			score = 9
		elif result[0] == 'P':
			score = 8
		elif result[0] == 'S':
			score = 7
	
	# not in front hull facing, a pivot would be required
	if GetFacing(target, attacker, False) != 'Front':
		score -= 2
	
	return score


# handle a given attack, either from ScoreAttack or InitAttack
# determine what kind of roll to use, and return if attack would have no effect
def CalcAttack(attacker, weapon, target):
	ift_roll = True
	if 'ift_class' in weapon.stats:
		if weapon.stats['ift_class'] == 'MG' and target.vehicle:
			ift_roll = False
	elif not weapon.ift_weapon:
		ift_roll = False
	
	if ift_roll:
		return CalcIFT(attacker, weapon, target)
	
	return CalcTH(attacker, weapon, target)


# determine hit location on vehicles
def GetHitLocation(hull_down, hull_facing):
	result = libtcod.random_get_int(0, 1, 10)
	if hull_down:
		if result <= 5:
			return 'Turret'
		else:
			return 'Miss'
	else:
		if result <= 4:
			return 'Turret'
		elif result <= 9 or hull_facing in ['Front', 'Rear']:
			return 'Hull'
		else:
			return 'Track'


# calculates base to-hit number, drm, and final roll required for an ordinance to-hit attack
# returns an attack object
def CalcTH(attacker, weapon, target):
	
	attack_obj = Attack(attacker, weapon, target)
	attack_obj.th_attack = True
	
	# determine range of attack
	rng = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy) * 4
	
	##### Determine base to-hit score required #####
	
	# infantry target
	if not target.vehicle:
		if rng <= 4:
			attack_obj.base_th = 10
		elif rng <= 12:
			attack_obj.base_th = 9
		elif rng <= 16:
			attack_obj.base_th = 8
		elif rng <= 24:
			attack_obj.base_th = 7
		elif rng <= 36:
			attack_obj.base_th = 6
		elif rng <= 40:
			attack_obj.base_th = 5
		elif rng <= 48:
			attack_obj.base_th = 2
		elif rng <= 52:
			attack_obj.base_th = 1
		else:
			attack_obj.base_th = 0
	else:
		if rng <= 4:
			attack_obj.base_th = 8
		elif rng <= 12:
			attack_obj.base_th = 7
		elif rng <= 16:
			attack_obj.base_th = 6
		elif rng <= 24:
			attack_obj.base_th = 5
		elif rng <= 28:
			attack_obj.base_th = 4
		elif rng <= 36:
			attack_obj.base_th = 3
		elif rng <= 40:
			attack_obj.base_th = 2
		elif rng <= 48:
			attack_obj.base_th = 1
		elif rng <= 52:
			attack_obj.base_th = 0
		else:
			attack_obj.base_th = -1

	# to-hit score modifiers
	# long-range guns
	if 'long_range' in weapon.stats:
		if weapon.stats['long_range'] == 'L':
			if rng > 12:
				attack_obj.base_th += 1
		elif weapon.stats['long_range'] == 'LL':
			if 13 <= rng <= 24:
				attack_obj.base_th += 1
			elif rng >= 25:
				attack_obj.base_th += 2

	##### Dice Roll Modifiers #####
	
	# elevation difference
	map_hex1 = GetHexAt(attacker.hx, attacker.hy)
	map_hex2 = GetHexAt(target.hx, target.hy)
	if map_hex1.elevation > map_hex2.elevation:
		attack_obj.drm.append(('Height Advantage', -1))
	
	# target hex terrain modifier
	terrain_mod = map_hex2.terrain_type.GetModifier(target)
	if terrain_mod != 0:
		attack_obj.drm.append(('Terrain Modifier', terrain_mod))
	
	if attacker.moved:
		attack_obj.drm.append(('Attacker Moved', 2))
	elif attacker.changed_facing:
		attack_obj.drm.append(('Attacker Changed Facing', 2))
	
	if attacker.pinned:
		attack_obj.drm.append(('Attacker is Pinned', 2))
	
	if target.hidden:
		attack_obj.drm.append(('Target is Hidden', 2))
	
	if target.vehicle:
		if target.size_class == 'Small':
			attack_obj.drm.append(('Small Target', 1))
	
	if attacker.acquired_target is not None:
		if attacker.acquired_target == target:
			attack_obj.drm.append(('Acquired Target', attacker.acquired_target_lvl))
	
	##### Final Numbers #####
	attack_obj.total_mod = 0
	for (text, mod) in attack_obj.drm:
		attack_obj.total_mod += mod
	attack_obj.roll_req = attack_obj.base_th - attack_obj.total_mod
	
	return attack_obj


# return an armour value modified to be x steps higher/lower
# modified slightly from ArmCom1
def GetArmourStep(base_armour, modifier):
	ARMOUR_VALUES = [0,1,2,3,4,6,8,11,14,18,26]
	index = ARMOUR_VALUES.index(base_armour)
	new_index = index + modifier
	if new_index < 0:
		return ARMOUR_VALUES[0]
	elif new_index > 10:
		return ARMOUR_VALUES[10]
	return ARMOUR_VALUES[new_index]


# calculate base to-kill number, drm, and final roll required for a kill on a vehicle
def CalcTK(attacker, weapon, target, facing, hit_location):
	
	# get armour modifier, or set unarmoured target location flag
	unarmoured = False
	if hit_location in ['Hull', 'Track']:
		if facing in ['Rear', 'Side']:
			if 'hull_side' in target.armour.keys():
				armour_text = 'Hull ' + facing
				armour_mod = target.armour['hull_side']
			else:
				unarmoured = True
		else:
			if 'hull_front' in target.armour.keys():
				armour_text = 'Hull Front'
				armour_mod = target.armour['hull_front']
			else:
				unarmoured = True
	
	# turret hit
	else:
		if facing in ['Rear', 'Side']:
			if 'turret_side' in target.armour.keys():
				armour_text = 'Turret ' + facing
				armour_mod = target.armour['turret_side']
			else:
				unarmoured = True
		else:
			if 'turret_front' in target.armour.keys():
				armour_text = 'Turret Front'
				armour_mod = target.armour['turret_front']
			else:
				unarmoured = True
	
	# track and rear hits are -1 armour step
	if hit_location == 'Track':
		armour_text = 'Track'
		armour_mod = GetArmourStep(armour_mod, -1)
	elif facing == 'Rear':
		armour_mod = GetArmourStep(armour_mod, -1)
	
	# TEMP - assumes AP
	
	# determine range of attack
	rng = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
	
	drm = []
	
	# determine base TK number
	# hit location is unarmoured
	if unarmoured:
		# TODO: MGs, ATRs, etc.
		c = weapon.stats['calibre']
		if c <= 28:
			base_tk = 7
		elif c <= 57:
			base_tk = 8
		elif c <= 77:
			base_tk = 9
		elif c <= 95:
			base_tk = 10
		else:
			base_tk = 11
		drm.append((armour_text + ' Unarmoured', 0))
		
	else:
		
		# calculate base TK number
		if 'ift_class' in weapon.stats:
			if weapon.stats['ift_class'] == 'MG':
				base_tk = 3
			else:
				print 'ERROR: unrecognized IFT weapon'
				base_tk = 0
		else:
			gun_rating = str(weapon.stats['calibre']) + weapon.stats['long_range']
			if gun_rating in ['20L']:
				base_tk = 6
			elif gun_rating in ['37']:
				base_tk = 8
			elif gun_rating in ['37L']:
				base_tk = 9
	
			# calibre range modifer
			c = weapon.stats['calibre']
			
			text = 'Range'
			
			if c <= 25:
				if rng == 0:
					drm.append((text, 2))
				elif rng <= 1:
					drm.append((text, 1))
				elif rng < 5:
					pass
				elif rng <= 6:
					drm.append((text, -1))
				elif rng == 7:
					drm.append((text, -2))
				elif rng <= 9:
					drm.append((text, -3))
				elif rng == 10:
					drm.append((text, -4))
				elif rng <= 12:
					drm.append((text, -5))
				else:
					# not possible
					return (-1, -1, [])
			elif c <= 57:
				if rng == 0:
					drm.append((text, 1))
				elif rng <= 4:
					pass
				elif rng <= 6:
					drm.append((text, -1))
				elif rng <= 9:
					drm.append((text, -2))
				elif rng == 10:
					drm.append((text, -3))
				elif rng <= 13:
					drm.append((text, -4))
				elif rng <= 15:
					drm.append((text, -5))
				else:
					# not possible
					return (-1, -1, [])
			else:
				if rng == 0:
					drm.append((text, 1))
				elif rng <= 4:
					pass
				elif rng <= 7:
					drm.append((text, -1))
				elif rng <= 10:
					drm.append((text, -2))
				elif rng <= 13:
					drm.append((text, -3))
				elif rng <= 16:
					drm.append((text, -4))
				elif rng <= 19:
					drm.append((text, -5))
				else:
					# not possible
					return (-1, -1, [])
		
		# hit location armour
		drm.append((armour_text + ' Armour', -armour_mod))
	
	# calculate roll required
	total_mod = 0
	for (text, mod) in drm:
		total_mod += mod
	roll_req = base_tk + total_mod
	
	return (base_tk, roll_req, drm, total_mod)


# calculates an IFT attack or IFT damage from a hit result
# returns an Attack object
def CalcIFT(attacker, weapon, target, hit_result=False, multiple_hits=1):
	
	attack_obj = Attack(attacker, weapon, target)
	attack_obj.ift_attack = True
	
	# calculate base fp: work with it as float for now
	if weapon.ord_weapon:
		c = weapon.stats['calibre']
		if c <= 20:
			attack_obj.base_fp = 1.0
		elif c <= 30:
			attack_obj.base_fp = 2.0
		elif c <= 37:
			attack_obj.base_fp = 4.0
	else:
		attack_obj.base_fp = float(weapon.stats['fp'])	
	
	# calcuate effective fp
	attack_obj.final_fp = attack_obj.base_fp
	
	attack_obj.base_fp = int(attack_obj.base_fp)
	
	# IFT attack fp modifiers
	if not hit_result:
		
		# step number modifiers for IFT attacks
		if attacker.vehicle:
			attack_obj.final_fp = attack_obj.final_fp * float(attacker.num_steps)
			attack_obj.fp_mods.append((str(attacker.num_steps) + ' steps attacking',
				'x' + str(attacker.num_steps)))
		elif attacker.infantry:
			if attacker.num_steps == 2:
				attack_obj.final_fp = attack_obj.final_fp / 2.0
				attack_obj.fp_mods.append(('Infantry at 2 steps', '/2'))
			elif attacker.num_steps == 1:
				attack_obj.final_fp = attack_obj.final_fp / 3.0
				attack_obj.fp_mods.append(('Infantry at 1 step', '/3'))
		
		if attacker.moved:
			attack_obj.final_fp = attack_obj.final_fp / 2.0
			attack_obj.fp_mods.append(('Attacker Moved', '/2'))
		elif attacker.changed_facing:
			attack_obj.final_fp = attack_obj.final_fp / 2.0
			attack_obj.fp_mods.append(('Attacker Changed Facing', '/2'))
		
		if attacker.pinned:
			attack_obj.final_fp = attack_obj.final_fp / 2.0
			attack_obj.fp_mods.append(('Attacker is Pinned', '/2'))
		
		dist = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
		# close range attack
		if dist == 1:
			attack_obj.final_fp = attack_obj.final_fp * 2.0
			attack_obj.fp_mods.append(('Close Range', 'x2'))
		# point blank range attack
		elif dist == 0:
			attack_obj.final_fp = attack_obj.final_fp * 3.0
			attack_obj.fp_mods.append(('Point Blank Range', 'x3'))
	
	# TODO: hit result fp modifiers
	else:
		if multiple_hits > 1:
			attack_obj.final_fp = attack_obj.final_fp * float(multiple_hits)
			attack_obj.fp_mods.append(('Multiple Hits', 'x'+str(multiple_hits)))
	
	# round down final fp, convert to int, collapse odd values, and get column to use
	attack_obj.final_fp = int(floor(attack_obj.final_fp))
	while str(attack_obj.final_fp) not in IFT_TABLE.keys():
		attack_obj.final_fp -= 1
	attack_obj.column = IFT_TABLE[str(attack_obj.final_fp)]
	
	##### Dice Roll Modifiers #####
	
	# IFT attack DRM
	if not hit_result:
		
		# elevation difference
		map_hex1 = GetHexAt(attacker.hx, attacker.hy)
		map_hex2 = GetHexAt(target.hx, target.hy)
		if map_hex1.elevation > map_hex2.elevation:
			attack_obj.drm.append(('Height Advantage', -1))
		
		# target hex terrain modifier
		terrain_mod = map_hex2.terrain_type.GetModifier(target)
		if terrain_mod != 0:
			attack_obj.drm.append(('Terrain Modifier', terrain_mod))
		
		# target PSG is hidden
		if target.hidden:
			attack_obj.drm.append(('Target is Hidden', 2))
		
	# hit result DRM
	else:
		if target.gun:
			if target.emplaced:
				attack_obj.drm.append(('Target is Emplaced', 2))
	
	##### Final Numbers #####
	attack_obj.total_mod = 0
	for (text, mod) in attack_obj.drm:
		attack_obj.total_mod += mod
	
	return attack_obj
	

# spawns an ordinance weapon and loads its stats from a given XML item
def SpawnORDWeapon(item):
	stats = {}
	stats['name'] = item.find('name').text
	stats['calibre'] = int(item.find('calibre').text)
	if item.find('long_range') is None:
		stats['long_range'] = ''
	else:
		stats['long_range'] = item.find('long_range').text
	stats['fire_tu'] = int(item.find('fire_tu').text)
	# all guns have a maximum normal range of 1 mile
	stats['normal_range'] = 10
	stats['reload_tu_min'] = int(item.find('reload_tu_min').text)
	stats['reload_tu_max'] = int(item.find('reload_tu_max').text)
	return OrdinanceWeapon(stats)


# spawns an IFT weapon and loads its data from a given XML item
def SpawnIFTWeapon(item):
	stats = {}
	stats['name'] = item.find('name').text
	stats['ift_class'] = item.find('ift_class').text
	stats['fp'] = int(item.find('fp').text)
	stats['fire_tu'] = int(item.find('fire_tu').text)
	stats['normal_range'] = int(item.find('normal_range').text)
	return IFTWeapon(stats)


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
	
	# linked by road
	road = False
	direction = GetDirectionToAdjacent(map_hex1.hx, map_hex1.hy, map_hex2.hx, map_hex2.hy)
	if direction in map_hex1.dirt_road_links: road = True
	
	if psg.movement_class == 'Infantry':
		if road:
			cost = 4
		else:
			cost = 6
	
	elif psg.movement_class == 'Wheeled':
		if road:
			cost = 2
		elif map_hex2.terrain_type.difficult:
			cost = 6
		else:
			cost = 3
	
	elif psg.movement_class == 'Tank':
		if road:
			cost = 3
		elif map_hex2.terrain_type.difficult:
			cost = 6
		else:
			cost = 3
	
	elif psg.movement_class == 'Fast Tank':
		if road:
			cost = 2
		elif map_hex2.terrain_type.difficult:
			cost = 6
		else:
			cost = 2

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
# TODO: keep updating animations while waiting
def WaitForEnter():
	end_pause = False
	while not end_pause:
		# get input from user
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		
		# exit right away
		if libtcod.console_is_window_closed():
			sys.exit()
		
		elif key.vk == libtcod.KEY_ENTER: 
			end_pause = True
		
		# refresh the screen
		libtcod.console_flush()
	
	# wait for enter to be released
	while libtcod.console_is_key_pressed(libtcod.KEY_ENTER):
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		libtcod.console_flush()


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
	xdist = (x2 - x1)
	ydist = (y2 - y1)
	angle = degrees(atan2(ydist, xdist))
	return int((angle + 90.0) % 360)


# assuming an observer in hx1, hy1 looking at hx2, hy2, returns a list of visible hexes
# along this line of sight
# used in HexMap.CalcFoV()
def GetLoS(hx1, hy1, hx2, hy2):
	
	visible_hexes = []
	
	visible_hexes.append((hx1, hy1))
	
	# same hex
	if hx1 == hx2 and hy1 == hy2:
		return visible_hexes
	
	distance = GetHexDistance(hx1, hy1, hx2, hy2)
	
	# adjacent hex
	if distance == 1:
		visible_hexes.append((hx2, hy2))
		return visible_hexes
	
	observer_elevation = float(GetHexAt(hx1, hy1).elevation)
	los_slope = None
	
	# start with first hex
	hx = hx1
	hy = hy1
	
	while hx != hx2 or hy != hy2:
		
		# TEMP: emergency escape
		if libtcod.console_is_window_closed():
			sys.exit()
		
		# get the next hex or hex pair in the line toward the endpoint
		(x1, y1) = PlotHex(hx, hy)
		(x2, y2) = PlotHex(hx2, hy2)
		bearing = GetBearing(x1, y1, x2, y2)
		hex_list = []
		
		if bearing == 30:
			hex_list.append(GetAdjacentHex(hx, hy, 0))
			hex_list.append(GetAdjacentHex(hx, hy, 1))
		elif bearing == 90:
			hex_list.append(GetAdjacentHex(hx, hy, 1))
			hex_list.append(GetAdjacentHex(hx, hy, 2))
		elif bearing == 150:
			hex_list.append(GetAdjacentHex(hx, hy, 2))
			hex_list.append(GetAdjacentHex(hx, hy, 3))
		elif bearing == 210:
			hex_list.append(GetAdjacentHex(hx, hy, 3))
			hex_list.append(GetAdjacentHex(hx, hy, 4))
		elif bearing == 270:
			hex_list.append(GetAdjacentHex(hx, hy, 4))
			hex_list.append(GetAdjacentHex(hx, hy, 5))
		elif bearing == 330:
			hex_list.append(GetAdjacentHex(hx, hy, 5))
			hex_list.append(GetAdjacentHex(hx, hy, 0))
		else:
			if bearing > 330 or bearing < 30:
				hex_list.append(GetAdjacentHex(hx, hy, 0))
			elif bearing < 90:
				hex_list.append(GetAdjacentHex(hx, hy, 1))
			elif bearing > 270:
				hex_list.append(GetAdjacentHex(hx, hy, 5))
			elif bearing < 150:
				hex_list.append(GetAdjacentHex(hx, hy, 2))
			elif bearing > 210:
				hex_list.append(GetAdjacentHex(hx, hy, 4))
			else:
				hex_list.append(GetAdjacentHex(hx, hy, 3))
		
		# check that we haven't gone beyond the max LoS distance
		(hx3, hy3) = hex_list[0]
		if GetHexDistance(hx1, hy1, hx3, hy3) > MAX_LOS_DISTANCE:
			return visible_hexes
		
		# check either the next hex or the next hex pair
		lowest_elevation = None
		for (hx, hy) in hex_list:
			
			# hex is off the map
			if (hx, hy) not in scenario.hex_map.hexes:
				continue
			
			distance = float(GetHexDistance(hx1, hy1, hx, hy)) * 160.0
			map_hex = scenario.hex_map.hexes[(hx, hy)]
			elevation = float(map_hex.elevation) - observer_elevation
			elevation = elevation * ELEVATION_M
			elevation += float(map_hex.terrain_type.los_height)
			
			# if no lowest elevation recorded yet, record it
			if lowest_elevation is None:
				lowest_elevation = elevation
			
			# otherwise, if lower than previously recorded, replace it
			else:
				if elevation < lowest_elevation:
					lowest_elevation = elevation
			
			# calculate slope from observer to this hex
			slope = elevation / distance
			
			# if adjacent hex, automatically visible
			if los_slope is None:
				visible_hexes.append((hx, hy))
				
				# we have reached end of LoS check
				if hx == hx2 and hy == hy2:
					return visible_hexes
				
				# set new LoS slope
				los_slope = slope
			
			else:
				# check if this hex is visible based on previous LoS slope
				if slope >= los_slope:
					
					visible_hexes.append((hx, hy))
					
					# we have reached end of LoS check
					if hx == hx2 and hy == hy2:
						return visible_hexes
			
		# if we ended up with no lowest_elevation, hex or both hexes are off map,
		#   so break ray
		if lowest_elevation is None:
			return visible_hexes
		
		# calculate slope to lower of hex pair
		slope = lowest_elevation / distance
		
		# if slope larger than previous los_slope, set new los_slope
		if slope > los_slope:
			los_slope = slope

	return visible_hexes


# return the maximum range in hexes between these two PSGs for the first to spot the second
def GetSpottingDistance(spotter, target):
	
	# determine base distance
	
	if spotter.infantry:
		distance = 2
	elif spotter.gun:
		distance = 3
	elif spotter.vehicle:
		distance = 5
	
	# apply target modifiers
	map_hex = GetHexAt(target.hx, target.hy)
	if map_hex.terrain_type.GetModifier(target) > 0: distance -= 1
	if target.fired: distance += 3
	if target.moved: distance += 1
	if target.dug_in: distance -= 1
	if target.suppressed: distance -= 1
	if target.pinned: distance -= 1
	
	# spotter modifiers
	if spotter.recce: distance += 2
	if spotter.dug_in: distance += 1
	if spotter.moved: distance -= 1
	if spotter.suppressed: distance -= 3
	if spotter.pinned: distance -= 1
	
	return distance
	

# get the relative facing of a target PSG from the pov of an attacker PSG
def GetFacing(attacker, target, turret):
	
	# first assume that target unit is facing direction 0 and get bearing
	(x1, y1) = PlotHex(target.hx, target.hy)
	(x2, y2) = PlotHex(attacker.hx, attacker.hy)
	bearing = GetBearing(x1, y1, x2, y2)
	
	# rotate for target PSG or unit's facing
	facing = target.facing
	if turret and target.turret_facing is not None:
		facing = target.turret_facing
		
	bearing = RectifyHeading(bearing - (facing * 60))
	
	if bearing >= 300 or bearing <= 60:
		return 'Front'
	elif 120 <= bearing <= 240:
		return 'Rear'
	return 'Side'


# initiate an attack by one PSG on another
def InitAttack(attacker, target):
	
	# TEMP: make sure there's a weapon and a target
	if target is None: return
	if attacker.selected_weapon is None: return
	
	# set fired flag and clear the selected target
	attacker.fired = True
	attacker.target_psg = None
	
	# determine weapon used in attack
	weapon = attacker.selected_weapon
	
	# send information to CalcAttack, which will return an Attack object with the
	# calculated stats to use for the attack
	attack_obj = CalcAttack(attacker, weapon, target)
	
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
			Wait(50)

	# display attack console for this attack
	if attack_obj.ift_attack:
		DisplayIFTRoll(attack_obj)
	else:
		DisplayToHitRoll(attack_obj)
	WaitForEnter()
	
	# clear any LoS from screen
	DrawScreenConsoles()
	
	# Perform Attack
	
	# IFT attack: roll once for entire PSG
	# TODO: different animations for MGs and small arms
	if attack_obj.ift_attack:
	#	IFTAttackAnimation(attack_obj)
		target.ResolveIFTAttack(attack_obj)
	
	# to-hit attack
	else:
	#	OrdAttackAnimation(attack_obj)
		target.ResolveToHitAttack(attack_obj)
	
	# handle acquired target flags
	
	# attacker had already acquired target
	if attacker.acquired_target == target:
		if attacker.acquired_target_lvl == -1:
			attacker.acquired_target_lvl = -2
	# newly acquired target
	else:
		attacker.acquired_target = target
		attacker.acquired_target_lvl = -1
		target.acquired_by.append(attacker)


# display the stats for an IFT roll on the screen
def DisplayIFTRoll(attack_obj, hit_result=False):
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.white)
	libtcod.console_clear(attack_con)
	temp = LoadXP('ArmCom2_attack_bkg.xp')
	libtcod.console_blit(temp, 0, 0, 30, 60, attack_con, 0, 0)
	del temp
	
	# title
	if hit_result:
		text1 = 'Resolving attack by'
		text2 = attack_obj.weapon.GetName() + ' on'
	else:
		text1 = attack_obj.attacker.GetName()
		text2 = 'firing ' + attack_obj.weapon.GetName() + ' at'
	libtcod.console_print_ex(attack_con, 15, 1, libtcod.BKGND_NONE,
		libtcod.CENTER, text1)
	libtcod.console_print_ex(attack_con, 15, 3, libtcod.BKGND_NONE,
		libtcod.CENTER, text2)
	libtcod.console_print_ex(attack_con, 15, 5, libtcod.BKGND_NONE,
		libtcod.CENTER, attack_obj.target.GetName())
	
	# base fp
	libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR)
	libtcod.console_rect(attack_con, 1, 8, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 8, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Firepower')
	
	libtcod.console_print_ex(attack_con, 15, 10, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Base FP: ' + str(attack_obj.base_fp))
	
	# list fp modifiers (max 3)
	y = 12
	for (text1, text2) in attack_obj.fp_mods:
		libtcod.console_print(attack_con, 4, y, text1)
		libtcod.console_print_ex(attack_con, 25, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text2)
		y += 1

	libtcod.console_print_ex(attack_con, 15, 16, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Final FP: ' + str(attack_obj.final_fp))
	
	# DRM list
	libtcod.console_rect(attack_con, 1, 19, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 19, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Roll Modifiers')
	
	y = 21
	for (text, mod) in attack_obj.drm:
		libtcod.console_print(attack_con, 2, y, text)
		mod_text = str(mod)
		if mod > 0: mod_text = '+' + mod_text
		libtcod.console_print_ex(attack_con, 27, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, mod_text)
		y += 1
	
	text = str(attack_obj.total_mod)
	if attack_obj.total_mod > 0: text = '+' + text
	libtcod.console_print_ex(attack_con, 15, 31, libtcod.BKGND_NONE, libtcod.CENTER,
		'Total Modifier: ' + text)
	
	# display list of possible results
	libtcod.console_rect(attack_con, 1, 34, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 34, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Possible Results')
	
	libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR2)
	libtcod.console_rect(attack_con, 1, 36, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print(attack_con, 3, 36, '2 3 4 5 6 7 8 9 10 11 12')
	
	for test_roll in range(2, 13):
		mod_roll = test_roll + attack_obj.total_mod
		if mod_roll < 0:
			mod_roll = 0
		elif mod_roll > 15:
			mod_roll = 15
		result = attack_obj.column[mod_roll]
		x = -1 + (test_roll * 2)
		if test_roll >= 10:
			x += test_roll-9
		libtcod.console_print(attack_con, x, 37, result[0])
		libtcod.console_print(attack_con, x, 38, result[1])
	
	libtcod.console_print_ex(attack_con, 15, 57, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Enter to Continue')
	
	# display console on screen
	libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
	libtcod.console_flush()


# display the stats for an to-hit roll on the screen
def DisplayToHitRoll(attack_obj):
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.white)
	libtcod.console_clear(attack_con)
	temp = LoadXP('ArmCom2_attack_bkg.xp')
	libtcod.console_blit(temp, 0, 0, 30, 60, attack_con, 0, 0)
	del temp
	
	# title
	libtcod.console_print_ex(attack_con, 15, 1, libtcod.BKGND_NONE,
		libtcod.CENTER, attack_obj.attacker.step_name)
	libtcod.console_print_ex(attack_con, 15, 3, libtcod.BKGND_NONE,
		libtcod.CENTER, 'firing ' + attack_obj.weapon.GetName() + ' at')
	libtcod.console_print_ex(attack_con, 15, 5, libtcod.BKGND_NONE,
		libtcod.CENTER, attack_obj.target.GetName())
	
	# base to hit
	libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR)
	libtcod.console_rect(attack_con, 1, 8, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 8, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Base To-Hit: ' + chr(243) + str(attack_obj.base_th))
	
	# DRM list
	libtcod.console_rect(attack_con, 1, 19, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 19, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Roll Modifiers')
	
	y = 21
	for (text, mod) in attack_obj.drm:
		libtcod.console_print(attack_con, 2, y, text)
		mod_text = str(mod)
		if mod > 0: mod_text = '+' + mod_text
		libtcod.console_print_ex(attack_con, 27, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, mod_text)
		y += 1
	
	text = str(attack_obj.total_mod)
	if attack_obj.total_mod > 0: text = '+' + text
	libtcod.console_print_ex(attack_con, 15, 47, libtcod.BKGND_NONE, libtcod.CENTER,
		'Total DRM: ' + text)
	
	# TODO: possible number of hits
	# final to-hit roll required
	#libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR2)
	#libtcod.console_rect(attack_con, 1, 51, 28, 1, False, libtcod.BKGND_SET)
	#libtcod.console_print_ex(attack_con, 15, 51, libtcod.BKGND_NONE, libtcod.CENTER,
	#	'Final To-Hit: ' + chr(243) + str(attack_obj.roll_req))
	
	libtcod.console_print_ex(attack_con, 15, 57, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Enter to Continue')
	
	# display console on screen
	libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
	libtcod.console_flush()
	
	
# display the stats for a to-kill roll on the screen
def DisplayTKRoll(attacker, weapon, target, base_tk, roll_req, drm, total_mod):
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.white)
	libtcod.console_clear(attack_con)
	temp = LoadXP('ArmCom2_attack_bkg.xp')
	libtcod.console_blit(temp, 0, 0, 30, 60, attack_con, 0, 0)
	del temp
	
	# title
	libtcod.console_print_ex(attack_con, 15, 1, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Resolving hit by')
	libtcod.console_print_ex(attack_con, 15, 3, libtcod.BKGND_NONE,
		libtcod.CENTER, weapon.GetName() + ' on')
	libtcod.console_print_ex(attack_con, 15, 5, libtcod.BKGND_NONE,
		libtcod.CENTER, target.GetName())
	
	# base tk
	libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR)
	libtcod.console_rect(attack_con, 1, 8, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 8, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Base To-Kill: ' + chr(243) + str(base_tk))
	
	# DRM list
	libtcod.console_rect(attack_con, 1, 19, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 19, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Roll Modifiers')
	
	y = 21
	for (text, mod) in drm:
		libtcod.console_print(attack_con, 2, y, text)
		mod_text = str(mod)
		if mod > 0: mod_text = '+' + mod_text
		libtcod.console_print_ex(attack_con, 27, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, mod_text)
		y += 1
	
	text = str(total_mod)
	if total_mod > 0: text = '+' + text
	libtcod.console_print_ex(attack_con, 15, 47, libtcod.BKGND_NONE, libtcod.CENTER,
		'Total DRM: ' + text)
	
	# final to-hit roll required
	libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR2)
	libtcod.console_rect(attack_con, 1, 51, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 51, libtcod.BKGND_NONE, libtcod.CENTER,
		'Final To-Kill: ' + chr(243) + str(roll_req))
	
	libtcod.console_print_ex(attack_con, 15, 57, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Enter to Continue')
	
	
	# display console on screen
	libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
	libtcod.console_flush()
	
	WaitForEnter()


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
		if HasAdjacent(map_hex, 'Forest'):
			forest_chance = 30
		else:
			forest_chance = 5
		
		# if there's already an adjacent field, higher chance of there being one
		if HasAdjacent(map_hex, 'Field'):
			field_chance = 10
		else:
			field_chance = 5
		
		if HasAdjacent(map_hex, 'Village'):
			village_chance = 0
		else:
			village_chance = 2
		
		roll = libtcod.random_get_int(0, 1, 100)
		
		if roll <= pond_chance:
			map_hex.SetTerrainType('Pond')
			continue
		
		roll -= pond_chance
		
		if roll <= forest_chance:
			map_hex.SetTerrainType('Forest')
			continue
		
		roll -= forest_chance
			
		if roll <= field_chance:
			map_hex.SetTerrainType('Field')
			continue
		
		roll -= field_chance
		
		if roll <= village_chance:
			map_hex.SetTerrainType('Village')
	
	# TEMP - no road
	return
	
	# add a road running from the bottom to the top of the map
	path = GetHexPath(6, 84, 6, -3)
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

# show a PSG moving from its current location to hx, hy
def DisplayMoveAnimation(psg, new_hx, new_hy):
	
	# calculate path for animation
	(x1,y1) = PlotHex(psg.hx, psg.hy)
	(x2,y2) = PlotHex(new_hx, new_hy)
	x3 = x2-x1
	y3 = y2-y1
	line = GetLine(0, 0, x3, y3)
	
	pause_time = config.getint('ArmCom2', 'animation_speed') * 6
	
	for (x_mod, y_mod) in line:
		psg.anim_offset_x = x_mod
		psg.anim_offset_y = y_mod
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		Wait(pause_time)

	# reset animation offsets
	psg.anim_offset_x = 0
	psg.anim_offset_y = 0 


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
		UpdateMapGUIConsole()
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
		UpdateMapGUIConsole()
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
	
	# TEMP: handle messages that would appear off-map
	if x < 30:
		x = 30
	elif x > WINDOW_WIDTH - 8:
		x = WINDOW_WIDTH - 8
	if y < 3:
		y = 3
	elif y > WINDOW_HEIGHT - 8:
		y = WINDOW_HEIGHT - 8
	
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0)
	lines = wrap(text, 16)
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
		
	#start_time = time.time()
	
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
	
	# TEMP
	return
	
	
	# TEMP: draw roads and rivers overtop
	for (hx, hy) in VP_HEXES:
		if (hx, hy) not in scenario.hex_map.vp_matrix: continue
		map_hex = scenario.hex_map.vp_matrix[(hx,hy)]
		
		# river edges		
		#if map_hex.river_edges:
	
		#	(x,y) = PlotHex(hx, hy)
			
		#	for map_hex2 in map_hex.river_edges:
		#		direction = GetDirectionToAdjacent(map_hex.hx, map_hex.hy, map_hex2.hx, map_hex2.hy)
				# modify for vp rotation
		#		direction = CombineDirs(direction, scenario.player_psg.facing)
		#		for (rx,ry) in GetEdgeTiles(x, y, direction):
		#			libtcod.console_set_char_background(map_terrain_con, rx, ry, RIVER_BG_COL, flag=libtcod.BKGND_SET)
		
		# dirt roads
		if len(map_hex.dirt_road_links) > 0:
			
			# set colour to use for roads
			if not map_hex.vis_to_player:
				col = libtcod.black
			else:
				col = DIRT_ROAD_COL
			
			for direction in map_hex.dirt_road_links:
				# modify for vp rotation
				direction = CombineDirs(direction, scenario.player_psg.facing)
				
				# paint road
				(x1, y1) = PlotHex(hx, hy)
				(x2, y2) = GetEdgeTiles(x1, y1, direction)[1]
				
				line = GetLine(x1, y1, x2, y2)
				for (x, y) in line:
					libtcod.console_set_char_background(map_terrain_con, x, y, col, libtcod.BKGND_SET)
					
					# if character is not blank or hex edge, remove it
					if libtcod.console_get_char(map_terrain_con, x, y) not in [0, 250]:
						libtcod.console_set_char(map_terrain_con, x, y, 0)

	# highlight any objective hexes
	for (vp_hx, vp_hy), map_hex in scenario.hex_map.vp_matrix.iteritems():
		if map_hex.objective is not None:
			(x,y) = PlotHex(vp_hx, vp_hy)
			temp = LoadXP('ArmCom2_objective_highlight.xp')
			libtcod.console_set_key_color(temp, KEY_COLOR)
			libtcod.console_blit(temp, 0, 0, 7, 5, map_terrain_con, x-3, y-2, 1.0, 0.0)
			del temp
	
	#print 'UpdateMapTerrainConsole() Finished: Took ' + str(time.time() - start_time) + ' seconds'


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
def UpdateMapGUIConsole():
	libtcod.console_clear(map_gui_con)
		

# run through active PSGs and draw them to the unit console
def UpdateUnitConsole():
	libtcod.console_clear(unit_con)
	for psg in scenario.psg_list:
		# don't draw hidden enemy units
		if psg.owning_player == 1 and psg.hidden: continue
		psg.DrawMe()


# updates the selected PSG info console
def UpdatePSGConsole():
	libtcod.console_clear(psg_con)
	
	# create a local pointer to the currently active PSG
	psg = scenario.active_psg
	
	# PSG name
	libtcod.console_print(psg_con, 0, 0, psg.GetName())
	
	# unit type
	libtcod.console_set_default_foreground(psg_con, HIGHLIGHT_COLOR)
	libtcod.console_print(psg_con, 0, 1, psg.GetStepName())
	libtcod.console_set_default_foreground(psg_con, libtcod.white)
	
	# vehicle portrait
	libtcod.console_set_default_background(psg_con, PORTRAIT_BG_COL)
	libtcod.console_rect(psg_con, 0, 2, 24, 8, False, libtcod.BKGND_SET)
	libtcod.console_set_default_background(psg_con, libtcod.black)
	
	# TODO: re-do portraits so that width is now 24
	if psg.portrait is not None:
		temp = LoadXP(psg.portrait)
		if temp is not None:
			x = 14 - int(libtcod.console_get_width(temp) / 2)
			libtcod.console_blit(temp, 0, 0, 24, 8, psg_con, x, 2)
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
	y = 12
	libtcod.console_set_default_background(psg_con, HIGHLIGHT_BG_COLOR)
	
	for weapon in psg.weapon_list:
		libtcod.console_set_default_background(psg_con, WEAPON_LIST_COLOR)
		# highlight selected weapon if in shooting phase
		if scenario.current_phase == 1 and psg.selected_weapon is not None:
			if weapon == psg.selected_weapon:
				libtcod.console_set_default_background(psg_con, SELECTED_WEAPON_COLOR)
		libtcod.console_rect(psg_con, 0, y, 24, 1, False, libtcod.BKGND_SET)
		if weapon.ord_weapon:
			text = str(weapon.stats['calibre']) + 'mm ' + weapon.stats['long_range']
			libtcod.console_print(psg_con, 0, y, text)
		else:
			libtcod.console_print(psg_con, 0, y, weapon.stats['name'])
			text = str(weapon.stats['fp']) + '-' + str(weapon.stats['normal_range'])
			libtcod.console_print_ex(psg_con, 23, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
		y += 1
	
	# armour ratings if any
	if psg.armour:
		text = ('Turret ' + str(psg.armour['turret_front']) + '/' +
			str(psg.armour['turret_side']))
		libtcod.console_print(psg_con, 0, 16, text)
		text = ('Hull   ' + str(psg.armour['hull_front']) + '/' +
			str(psg.armour['hull_side']))
		libtcod.console_print(psg_con, 0, 17, text)
	
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
		libtcod.console_print(psg_con, 0, 19, 'Pivoted Hull')
	elif psg.changed_turret_facing:
		libtcod.console_print(psg_con, 0, 19, 'Rotated Turret')
	elif psg.dug_in:
		libtcod.console_print(psg_con, 0, 19, 'Dug-in')
	elif psg.hull_down > -1:
		text = 'HD '
		# TODO: add directional character
		libtcod.console_print(psg_con, 0, 19, text)
	
	# fired last turn
	if psg.fired:
		libtcod.console_print_ex(psg_con, 23, 19, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'Fired')

	
	# status flags
	#libtcod.console_set_default_foreground(psg_con, libtcod.light_red)
	#libtcod.console_set_default_background(psg_con, libtcod.darkest_red)
	#libtcod.console_rect(psg_con, 0, y, 24, 1, False, libtcod.BKGND_SET)
	
	#if psg.suppressed:
	#	libtcod.console_print(psg_con, 0, y, 'Suppressed')
	#elif psg.pinned:
	#	libtcod.console_print(psg_con, 0, y, 'Pinned')
	
	
	# TODO: current terrain type
	
	# TODO: vehicle crew?
	#libtcod.console_set_default_background(psg_con, libtcod.dark_grey)
	#libtcod.console_set_default_foreground(psg_con, libtcod.light_grey)
	#libtcod.console_rect(psg_con, 0, 15, 28, 1, False, libtcod.BKGND_SET)
	#libtcod.console_print(psg_con, 0, 15, 'Crew')
	
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
	
	# scenario date
	text = MONTH_NAMES[scenario.month] + ', ' + str(scenario.year)
	libtcod.console_print_ex(scen_info_con, 42, 0, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	
	# scenario name
	libtcod.console_set_default_foreground(scen_info_con, libtcod.light_blue)
	libtcod.console_print_ex(scen_info_con, 42, 1, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.name)
	libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
	
	# current turn and maximum turns
	text = 'Turn ' + str(scenario.current_turn) + '/' + str(scenario.max_turns)
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


# draw PSG info to the PSG info console based on current mouse location
# DEFUNCT: merge into UpdateHexInfoConsole() below
def UpdatePSGInfoConsole():
	
	# TEMP
	psg_info_con = libtcod.console_new(57, 57)
	
	
	libtcod.console_clear(psg_info_con)
	
	psg = None
	
	# PSG name (max 2 lines)
	# hidden enemy PSG
	if psg.owning_player == 1 and psg.hidden:
		libtcod.console_print(psg_info_con, 0, 0, 'Possible Enemy')
		libtcod.console_set_default_background(psg_info_con, libtcod.black)
		return
	
	lines = wrap(psg.GetName(), 21, subsequent_indent = ' ')
	n = 0
	for line in lines[:2]:
		libtcod.console_print(psg_info_con, 0, 0+n, line)
		n += 1
	
	# number of steps in PSG and name of squads/vehicles
	text = str(psg.num_steps) + ' ' + psg.GetStepName()
	libtcod.console_print(psg_info_con, 0, 2, text)
	
	# hull and turret facing if any
	text = ''
	if psg.vehicle or psg.gun:
		direction = CombineDirs(psg.facing, scenario.player_psg.facing)
		char = GetDirectionalArrow(direction)
		if psg.gun:
			text += 'Gun '
		else:
			text += 'Hull '
		text += char + ' '
		if psg.turret_facing is not None:
			direction = CombineDirs(psg.turret_facing, scenario.player_psg.facing)
			char = GetDirectionalArrow(direction)
			text += 'Turret ' + char
	
	libtcod.console_print(psg_info_con, 0, 4, text)
	
	# unit abilities and status
	if psg.recce:
		libtcod.console_print(psg_info_con, 0, 5, 'Recce')
	
	text = ''
	if psg.pinned:
		text = 'Pinned'
	elif psg.suppressed:
		text = 'Suppressed'
	
	if psg.hidden:
		if len(text) > 0: text += ' '
		text += 'Hidden'
	
	libtcod.console_print_ex(psg_info_con, 20, 5, libtcod.BKGND_NONE,
		libtcod.RIGHT, text)
	
	libtcod.console_set_default_background(psg_info_con, libtcod.black)


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
		if map_hex.objective is not None:
			libtcod.console_print_ex(hex_info_con, 23, 0, libtcod.BKGND_NONE,
				libtcod.RIGHT, 'Objective')

		# hex terrain type
		libtcod.console_print(hex_info_con, 0, 1, map_hex.terrain_type.display_name)

		# road status
		if len(map_hex.dirt_road_links) > 0:
			libtcod.console_print(hex_info_con, 0, 2, 'Dirt Road')
	

# layer the display consoles onto the screen
def DrawScreenConsoles():
	libtcod.console_clear(con)
	
	# map viewport layers
	libtcod.console_blit(bkg_console, 0, 0, 0, 0, con, 0, 3)		# grey outline
	libtcod.console_blit(map_terrain_con, 0, 0, 0, 0, con, 26, 3)		# map terrain
	libtcod.console_blit(map_fov_con, 0, 0, 0, 0, con, 26, 3, 0.7, 0.7)	# map FoV overlay
	libtcod.console_blit(unit_con, 0, 0, 0, 0, con, 26, 3, 1.0, 0.0)	# map unit layer
	#libtcod.console_blit(map_gui_con, 0, 0, 0, 0, con, 26, 0, 0.0, 1.0)	# map GUI layer

	# highlight selected PSG if any
	if scenario.active_psg is not None:
		libtcod.console_set_char_background(con, scenario.active_psg.screen_x,
			scenario.active_psg.screen_y, SELECTED_HL_COL, flag=libtcod.BKGND_SET)
	
		# highlight targeted PSG if any
		psg = scenario.active_psg.target_psg
		if psg is not None:
			libtcod.console_set_char_background(con, psg.screen_x, psg.screen_y,
				TARGET_HL_COL, flag=libtcod.BKGND_SET)
			# TODO: draw LoS line too
			line = GetLine(scenario.active_psg.screen_x, scenario.active_psg.screen_y,
				psg.screen_x, psg.screen_y)
			for (x, y) in line[2:-1]:
				libtcod.console_set_char(con, x, y, 250)
				libtcod.console_set_char_foreground(con, x, y, libtcod.red)
	
	# left column consoles
	libtcod.console_blit(psg_con, 0, 0, 0, 0, con, 1, 4)
	libtcod.console_blit(cmd_con, 0, 0, 0, 0, con, 1, 26)
	libtcod.console_blit(hex_info_con, 0, 0, 0, 0, con, 1, 52)
	
	# scenario info
	libtcod.console_blit(scen_info_con, 0, 0, 0, 0, con, 0, 0)
	
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)


# display the in-game menu
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
		UpdateMapGUIConsole()
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
	
	# attack resolution console (TEMP)
	attack_con = libtcod.console_new(30, 60)
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.light_grey)
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
		
		scenario.year = 1939
		scenario.month = 9
		scenario.name = 'Spearhead'
		scenario.max_turns = 8
		scenario.current_turn = 1		# TEMP
		
		# spawn the player PSGs
		new_psg = PSG('HQ Panzer Squadron', 'Panzer 35t', 5, 0, 0, 0, 9, 9)
		scenario.player_psg = new_psg
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(5, 10)
		
		new_psg = PSG('Light Panzer Squadron', 'Panzer II A', 5, 0, 0, 0, 9, 9)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(6, 9)
		
		new_psg = PSG('Light Panzerspäh Platoon', 'sd_kfz_221', 3, 0, 0, 0, 9, 9)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(7, 9)
		
		new_psg = PSG('Schützen Platoon', 'german_schutzen', 5, 0, 0, 0, 10, 9)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(8, 9)
		
		
		# select the first player PSG
		scenario.SelectNextPSG()
		
		# set up our objective
		#map_hex = GetHexAt(6, 48)
		# make sure it can be entered
		#if map_hex.terrain_type.display_name == 'Pond':
		#	map_hex = GetHexAt(6, 47)
		#map_hex.SetObjective('Capture')
		
		# set up enemy PSGs
		new_psg = PSG('HQ Tank Squadron', '7TP jw', 3, 3, 3, 1, 10, 10)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(5, 4)
		
		new_psg = PSG('AT Gun Section', '37mm wz. 36', 2, 3, 3, 1, 10, 10)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(6, 5)
		
	
		# draw map terrain
		UpdateMapTerrainConsole()
		# calculate initial field of view
		scenario.hex_map.CalcFoV()
		UpdateMapFoVConsole()
		
		# build initial command menu
		scenario.active_cmd_menu = 'movement_root'
		scenario.BuildCmdMenu()
		
		UpdateScreen()
		
		# do initial hidden/reveal check
		scenario.DoHiddenCheck()
		
		# do initial enemy spawn
		#scenario.SpawnEnemyUnits()
		
	
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
			
				
			
			##### Keyboard Commands #####
			
			# skip this section if no commands in buffer
			if key is None: continue
			
			# open scenario menu screen
			if key.vk == libtcod.KEY_ESCAPE:
				if ScenarioMenu():
					exit_scenario = True
				else:
					DrawScreenConsoles()
				continue
			
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
			Wait(100)
			
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
					UpdateScreen()
			
			##################################################################
			# Shooting Phase Actions
			##################################################################
			elif option.option_id == 'next_weapon':
				scenario.active_psg.SelectNextWeapon()
				# clear target list and select a new target
				scenario.active_psg.target_list = []
				scenario.active_psg.SelectNextTarget()
				UpdatePSGConsole()
				DrawScreenConsoles()
			elif option.option_id == 'next_target':
				scenario.active_psg.SelectNextTarget()
				DrawScreenConsoles()
			
			elif option.option_id == 'fire_target':
				InitAttack(scenario.active_psg, scenario.active_psg.target_psg)
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
menu_option = cmd_menu.AddOption('continue_scenario', 'C', 'Continue', desc='Continue a ' +
	'scenario in progress')
if not os.path.exists('savegame'): menu_option.inactive = True
cmd_menu.AddOption('new_scenario', 'N', 'New', desc='Start a new scenario, erasing any ' +
	'scenario already in progress')
cmd_menu.AddOption('options', 'O', 'Options', desc='View display and game options')
cmd_menu.AddOption('quit', 'Q', 'Quit', desc='Quit to desktop')
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

