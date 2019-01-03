# -*- coding: UTF-8 -*-
# Python 3.6.6 x64
# Libtcod 1.6.4 x64
##########################################################################################
#                                                                                        #
#                                Armoured Commander II                                   #
#                                                                                        #
##########################################################################################
#             Project Started February 23, 2016; Restarted July 25, 2016                 #
#          Restarted again January 11, 2018; Restarted again January 2, 2019             #
##########################################################################################
#
#    Copyright (c) 2016-2019 Gregory Adam Scott (sudasana@gmail.com)
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
#    If not, see <https://www.gnu.org/licenses/>.
#
#    xp_loader.py is covered under a MIT License (MIT) and is Copyright (c) 2015
#    Sean Hagar; see XpLoader_LICENSE.txt for more info.
#
##########################################################################################


##### Libraries #####
import os, sys						# OS-related stuff

if os.name == 'posix':					# if linux - load system libtcodpy
	import libtcodpy_local as libtcod		
else:
	import libtcodpy as libtcod			# The Doryen Library
	os.environ['PYSDL2_DLL_PATH'] = os.getcwd() + '/lib'.replace('/', os.sep)	# set sdl2 dll path
	
from configparser import ConfigParser			# saving and loading configuration settings
from random import choice, shuffle, sample		# for the illusion of randomness
from math import floor, cos, sin, sqrt			# math
from math import degrees, atan2, ceil			# heading calculations
import xp_loader, gzip					# loading xp image files
import json						# for loading JSON data
import time
from textwrap import wrap				# breaking up strings
import shelve						# saving and loading games
import sdl2.sdlmixer as mixer				# sound effects



##########################################################################################
#                                        Constants                                       #
##########################################################################################

NAME = 'Armoured Commander II'				# game name
VERSION = '2019-01-02'			# game version
DATAPATH = 'data/'.replace('/', os.sep)			# path to data files
#SOUNDPATH = 'sounds/'.replace('/', os.sep)		# path to sound samples
#CAMPAIGNPATH = 'campaigns/'.replace('/', os.sep)	# path to campaign files

if os.name == 'posix':					# linux (and OS X?) has to use SDL for some reason
	RENDERER = libtcod.RENDERER_SDL
else:
	RENDERER = libtcod.RENDERER_GLSL

LIMIT_FPS = 50						# maximum screen refreshes per second
WINDOW_WIDTH, WINDOW_HEIGHT = 90, 60			# size of game window in character cells
WINDOW_XM, WINDOW_YM = int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/2)	# center of game window

KEYBOARDS = ['QWERTY', 'AZERTY', 'QWERTZ', 'Dvorak']	# list of possible keyboard layout settings


##### Hex geometry definitions #####

# directional and positional constants
DESTHEX = [(0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0)]	# change in hx, hy values for hexes in each direction
PLOT_DIR = [(0,-1), (1,-1), (1,1), (0,1), (-1,1), (-1,-1)]	# position of direction indicator
TURRET_CHAR = [254, 47, 92, 254, 47, 92]			# characters to use for turret display
HEX_EDGE_CELLS = {						# relative locations of edge cells in a given direction for a map hex
	0: [(-1,-2),(0,-2),(1,-2)],
	1: [(1,-2),(2,-1),(3,0)],
	2: [(3,0),(2,1),(1,2)],
	3: [(1,2),(0,2),(-1,2)],
	4: [(-1,2),(-2,1),(-3,0)],
	5: [(-3,0),(-2,-1),(-1,-2)]
}


##### Colour Definitions #####
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency
ACTION_KEY_COL = libtcod.Color(51, 153, 255)		# colour for key commands
HIGHLIGHT_MENU_COL = libtcod.Color(30, 70, 130)		# background highlight colour for selected menu option
PORTRAIT_BG_COL = libtcod.Color(217, 108, 0)		# background color for unit portraits
UNKNOWN_UNIT_COL = libtcod.grey				# unknown enemy unit display colour
ENEMY_UNIT_COL = libtcod.Color(255, 20, 20)		# known "
ALLIED_UNIT_COL = libtcod.Color(20, 20, 255)		# allied unit display colour
GOLD_COL = libtcod.Color(255, 255, 100)			# golden colour for awards

# list of possible keyboard layout settings
KEYBOARDS = ['QWERTY', 'AZERTY', 'QWERTZ', 'Dvorak']

# text names for months
MONTH_NAMES = [
	'', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
	'September', 'October', 'November', 'December'
]

# text names for scenario phases; final one is for when enemy is active
SCEN_PHASE_NAMES = [
	'Command', 'Spotting', 'Movement', 'Shooting', 'Assault', 'Recovery', 'Enemy Action'
]
# colour associated with phases
SCEN_PHASE_COL = [
	libtcod.yellow, libtcod.purple, libtcod.green, libtcod.red, libtcod.white, libtcod.blue, libtcod.light_red 
]


##########################################################################################
#                                         Classes                                        #
##########################################################################################

# Campaign: stores data about a campaign and calendar currently in progress
class Campaign:
	def __init__(self):
		
		# placeholder for player unit
		self.player_unit = None
		
		# holder for active enemy units
		self.enemy_units = []
		

# Session: stores data that is generated for each game session and not stored in the saved game
class Session:
	def __init__(self):
		
		# flag: the last time the keyboard was polled, a key was pressed
		self.key_down = False
		
		# sound samples
		self.sample = {}
		
		# store player crew command defintions
		with open(DATAPATH + 'crew_command_defs.json', encoding='utf8') as data_file:
			self.crew_commands = json.load(data_file)
		
		# store nation definition info
		with open(DATAPATH + 'nation_defs.json', encoding='utf8') as data_file:
			self.nations = json.load(data_file)
	
	
	# try to initialize SDL2 mixer
	def InitMixer(self):
		mixer.Mix_Init(mixer.MIX_INIT_OGG)
		if mixer.Mix_OpenAudio(48000, mixer.MIX_DEFAULT_FORMAT,	2, 1024) == -1:
			print('ERROR in Mix_OpenAudio: ' + mixer.Mix_GetError())
			return False
		mixer.Mix_AllocateChannels(16)
		return True
	
	
	def LoadSounds(self):
		
		SOUND_LIST = [
			'menu_select',
			'37mm_firing_00', '37mm_firing_01', '37mm_firing_02', '37mm_firing_03',
			'37mm_he_explosion_00', '37mm_he_explosion_01',
			'vehicle_explosion_00',
			'at_rifle_firing',
			'plane_incoming_00', 'stuka_divebomb_00',
			'armour_save_00', 'armour_save_01',
			'light_tank_moving_00', 'light_tank_moving_01', 'light_tank_moving_02',
			'wheeled_moving_00', 'wheeled_moving_01', 'wheeled_moving_02',
			'zb_53_mg_00',
			'rifle_fire_00', 'rifle_fire_01', 'rifle_fire_02', 'rifle_fire_03'
		]
		
		# because the function returns NULL if the file failed to load, Python does not seem
		# to have any way of detecting this and there's no error checking
		for sound_name in SOUND_LIST:
			filename = SOUNDPATH + sound_name + '.ogg'
			self.sample[sound_name] = mixer.Mix_LoadWAV(filename.encode('ascii'))


# Personnel Class: represents an individual person within a unit 
class Personnel:
	def __init__(self, unit, nation, position):
		self.unit = unit				# pointer to which unit they belong
		self.nation = nation				# nationality of person
		self.current_position = position		# pointer to current position in a unit
		
		self.first_name = ''				# placeholders for first and last name
		self.last_name = ''				#   set by GenerateName()
		self.GenerateName()				# generate random first and last name
		
		self.ce = False					# crewman is exposed in a vehicle
		
		self.cmd_list = []				# list of possible commands
		self.current_cmd = 'Spot'			# currently assigned action for scenario
		self.status = ''				# current status
	
	
	# generate a random first and last name for this person
	def GenerateName(self):
		
		# TEMP: have to normalize extended characters so they can be displayed on screen
		# FUTURE: will have their own glyphs as part of font
		def FixName(text):
			CODE = {
				u'Ś' : 'S', u'Ż' : 'Z', u'Ł' : 'L',
				u'ą' : 'a', u'ć' : 'c', u'ę' : 'e', u'ł' : 'l', u'ń' : 'n', u'ó' : 'o',
				u'ś' : 's', u'ź' : 'z', u'ż' : 'z'
			}
			
			fixed_name = ''
			for i in range(len(text)):
				if text[i] in CODE:
					fixed_name += CODE[text[i]]
				else:
					fixed_name += text[i]
			return fixed_name
		
		first_name = choice(session.nations[self.nation]['first_names'])
		self.first_name = FixName(first_name)
		last_name = choice(session.nations[self.nation]['surnames'])
		self.last_name = FixName(last_name)
	
	
	# return the person's full name
	def GetFullName(self):
		return (self.first_name + ' ' + self.last_name)
	
	
	# (re)build a list of possible commands for this turn
	def BuildCommandList(self):
		self.cmd_list = []
		for (k, d) in session.crew_commands.items():
			if 'position_list' in d:
				if self.current_position.name not in d['position_list']:
					continue
			self.cmd_list.append(k)
	
	# select a new command from command list
	def SelectCommand(self, reverse):
		
		c = 1
		if reverse:
			c = -1
		
		# find current command in list
		i = self.cmd_list.index(self.current_cmd)
		
		# find new command
		if i+c > len(self.cmd_list) - 1:
			i = 0
		elif i+c < 0:
			i = len(self.cmd_list) - 1
		else:
			i += c
		
		self.current_cmd = self.cmd_list[i]
	

# Position class: represents a personnel position within a unit
class Position:
	def __init__(self, position_dict):
		
		self.name = position_dict['name']
		
		self.location = None
		if 'location' in position_dict:
			self.location = position_dict['location']
		
		self.hatch = False
		if 'hatch' in position_dict:
			self.hatch = True
		
		self.hatch_group = None
		if 'hatch_group' in position_dict:
			self.hatch_group = int(position_dict['hatch_group'])
		
		self.open_top = False
		if 'open_top' in position_dict:
			self.open_top = True
		
		self.crew_always_ce = False
		if 'crew_always_exposed' in position_dict:
			self.crew_always_ce = True
		
		self.ce_visible = []
		if 'ce_visible' in position_dict:
			for direction in position_dict['ce_visible']:
				self.ce_visible.append(int(direction))
		
		self.bu_visible = []
		if 'bu_visible' in position_dict:
			for direction in position_dict['bu_visible']:
				self.bu_visible.append(int(direction))
		
		# person currently in this position
		self.crewman = None
		

# Unit Class: represents a single vehicle or gun, or a squad or small team of infantry
class Unit:
	def __init__(self, unit_id):
		
		self.unit_id = unit_id			# unique ID for unit type
		self.alive = True			# unit is alive
		self.owning_player = 0			# unit is allied to 0:player 1:enemy
		self.nation = None			# nationality of unit and personnel
		
		self.positions_list = []		# list of crew/personnel positions
		self.personnel_list = []		# list of crew/personnel
		self.weapon_list = []			# list of unit weapons
		
		# load unit stats from JSON file
		with open(DATAPATH + 'unit_type_defs.json', encoding='utf8') as data_file:
			unit_types = json.load(data_file)
		if unit_id not in unit_types:
			print('ERROR: Could not find unit id: ' + unit_id)
			self.unit_id = None
			return
		self.stats = unit_types[unit_id].copy()
		
		if 'crew_positions' in self.stats:
			for position_dict in self.stats['crew_positions']:
				self.positions_list.append(Position(position_dict))
		
		# set up initial scenario statuses
		self.ResetMe()
	
	
	# set/reset all scenario statuses
	def ResetMe(self):
		
		self.hx = 0				# location in scenario hex map
		self.hy = 0
		
		# TEMP
		self.spotted = True			# unit has been spotted by opposing side
		self.hull_down = []			# list of directions unit in which Hull Down
		self.moving = False
		self.fired = False
		
		self.facing = None
		self.turret_facing = None
		self.deployed = False
	
	
	# check for the value of a stat, return None if stat not present
	def GetStat(self, stat_name):
		if stat_name not in self.stats:
			return None
		return self.stats[stat_name]
	
	
	# build lists of possible commands for each personnel in this unit
	def BuildCmdLists(self):
		for position in self.positions_list:
			if position.crewman is None: continue
			position.crewman.BuildCommandList()
	
	
	# generate new personnel sufficent to fill all personnel positions
	def GenerateNewPersonnel(self):
		for position in self.positions_list:
			self.personnel_list.append(Personnel(self, self.nation, position))
			position.crewman = self.personnel_list[-1]
	
	
	# move this unit into the given scenario map hex
	def SpawnAt(self, hx, hy):
		self.hx = hx
		self.hy = hy
		for map_hex in scenario.map_hexes:
			if map_hex.hx == hx and map_hex.hy == hy:
				map_hex.unit_stack.append(self)
				return
		
	
	# return the display character to use on the map viewport
	def GetDisplayChar(self):
		# player unit
		if campaign.player_unit == self: return '@'
		
		# unknown enemy unit
		if self.owning_player == 1 and not self.spotted: return '?'
		
		unit_category = self.GetStat('category')
		
		# sniper
		if self.unit_id == 'Sniper': return 248
		
		# infantry
		if unit_category == 'Infantry': return 176
		
		# gun, set according to deployed status / hull facing
		if unit_category == 'Gun':
			if self.facing is None:		# facing not yet set
				return '!'
			if not self.deployed:
				return 124
			elif self.facing in [5, 0, 1]:
				return 232
			elif self.facing in [2, 3, 4]:
				return 233
			else:
				return '!'		# should not happen
		
		# vehicle
		if unit_category == 'Vehicle':
			
			# turretless vehicle
			if self.turret_facing is None:
				return 249
			return 9

		# default
		return '!'
	
	
	# draw this unit to the scenario unit layer console
	def DrawMe(self):
		
		# don't display if not alive any more
		if not self.alive: return
		
		# determine draw location
		(x,y) = scenario.PlotHex(self.hx, self.hy)
		
		# determine foreground color to use
		if self.owning_player == 1:
			if not self.spotted:
				col = UNKNOWN_UNIT_COL
			else:
				col = ENEMY_UNIT_COL
		else:	
			if self == campaign.player_unit:
				col = libtcod.white
			else:
				col = ALLIED_UNIT_COL
		
		# draw main display character
		libtcod.console_put_char_ex(unit_con, x, y, self.GetDisplayChar(),
			col, libtcod.black)
		
		# determine if we need to display a turret / gun depiction
		if self.GetStat('category') == 'Infantry': return
		if self.owning_player == 1 and not self.spotted: return
		if self.GetStat('category') == 'Gun' and not self.deployed: return
		
		# use turret facing if present, otherwise hull facing
		if self.turret_facing is not None:
			facing = self.turret_facing
		else:
			facing = self.facing
		
		# determine location to draw turret/gun character
		x_mod, y_mod = PLOT_DIR[facing]
		char = TURRET_CHAR[facing]
		libtcod.console_put_char_ex(unit_con, x+x_mod, y+y_mod, char, col, libtcod.black)
		
	
	# display info on this unit to a given console starting at x,y
	# if status is False, don't display current status flags
	def DisplayMyInfo(self, console, x, y, status=True):
		
		libtcod.console_set_default_background(console, libtcod.black)
		libtcod.console_set_default_foreground(console, libtcod.lighter_blue)
		
		libtcod.console_print(console, x, y, self.unit_id)
		libtcod.console_set_default_foreground(console, libtcod.light_grey)
		libtcod.console_print(console, x, y+1, self.GetStat('class'))
		
		# draw empty portrait background
		libtcod.console_set_default_background(console, PORTRAIT_BG_COL)
		libtcod.console_rect(console, x, y+2, 25, 8, True, libtcod.BKGND_SET)
		
		# draw portrait if any
		portrait = self.GetStat('portrait')
		if portrait is not None:
			libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, console, x, y+2)
		
		# weapons
		libtcod.console_set_default_foreground(console, libtcod.white)
		libtcod.console_set_default_background(console, libtcod.darkest_red)
		libtcod.console_rect(console, x, y+10, 25, 2, True, libtcod.BKGND_SET)
		
		text1 = ''
		text2 = ''
		for weapon in self.weapon_list:
			if weapon.GetStat('type') == 'Gun':
				if text1 != '': text1 += ', '
				text1 += weapon.stats['name']
			else:
				if text2 != '': text2 += ', '
				text2 += weapon.stats['name']
		libtcod.console_print(console, x, y+10, text1)
		libtcod.console_print(console, x, y+11, text2)
		
		# armour
		armour = self.GetStat('armour')
		if armour is None:
			libtcod.console_print(console, x, y+12, 'Unarmoured')
		else:
			libtcod.console_print(console, x, y+12, 'Armoured')
			libtcod.console_set_default_foreground(console, libtcod.light_grey)
			if self.GetStat('turret'):
				text = 'T'
			else:
				text = 'U'
			text += ' ' + armour['turret_front'] + '/' + armour['turret_side']
			libtcod.console_print(console, x+1, y+13, text)
			text = 'H ' + armour['hull_front'] + '/' + armour['hull_side']
			libtcod.console_print(console, x+1, y+14, text)
		
		# movement
		libtcod.console_set_default_foreground(console, libtcod.light_green)
		libtcod.console_print_ex(console, x+24, y+12, libtcod.BKGND_NONE, libtcod.RIGHT,
			self.GetStat('movement_class'))
		
		# recce and/or off road
		libtcod.console_set_default_foreground(console, libtcod.dark_green)
		text = ''
		if self.GetStat('recce') is not None:
			text += 'Recce'
		if self.GetStat('off_road') is not None:
			if text != '':
				text += ' '
			text += 'ATV'
		libtcod.console_print_ex(console, x+24, y+13, libtcod.BKGND_NONE, libtcod.RIGHT,
			text)
		
		# size class
		libtcod.console_set_default_foreground(console, libtcod.white)
		size_class = self.GetStat('size_class')
		if size_class is not None:
			if size_class != 'Normal':
				libtcod.console_print_ex(console, x+24, y+14, libtcod.BKGND_NONE,
					libtcod.RIGHT, size_class)
			
		# mark place in case we skip unit status display
		ys = 15
		if status:
			
			# Hull Down status if any
			if len(self.hull_down) > 0:
				libtcod.console_set_default_foreground(console, libtcod.sepia)
				libtcod.console_print(console, x+8, ys-1, text)
				char = GetDirectionalArrow(self.hull_down[0])
				libtcod.console_put_char_ex(unit_info_con, x+11, ys-1, char, libtcod.sepia, libtcod.black)
		
			# reset of unit status
			libtcod.console_set_default_foreground(console, libtcod.light_grey)
			libtcod.console_set_default_background(console, libtcod.darkest_blue)
			libtcod.console_rect(console, x, y+ys, 25, 2, True, libtcod.BKGND_SET)
			
			text = ''
			if self.moving:
				text += 'Moving '
			if self.fired:
				text += 'Fired '
			libtcod.console_print(console, x, y+ys+1, text)
			
			ys = 17

		libtcod.console_set_default_background(console, libtcod.black)


# MapHex: a single hex on the scenario map
class MapHex:
	def __init__(self, hx, hy):
		self.hx = hx
		self.hy = hy
		self.unit_stack = []


# Scenario: represents a single battle encounter
class Scenario:
	def __init__(self):
		
		# generate hex map: single hex surrounded by 4 hex rings. Final ring is not normally
		# part of play and stores units that are coming on or going off of the map proper
		self.map_hexes = []
		self.map_hexes.append(MapHex(0,0))
		for r in range(1, 5):
			for (hx, hy) in GetHexRing(0, 0, r):
				self.map_hexes.append(MapHex(hx,hy))
		
		# turn and phase information
		self.current_turn = 1					# current scenario turn
		self.active_player = 0					# currently active player (0 is human player)
		self.phase = 0						# current phase
		self.advance_phase = False				# flag for input loop to automatically advance to next phase/turn
		
		# index of selected position in player unit
		self.selected_position = 0
	
	
	# advance to next phase/turn and do automatic events
	def AdvanceToNextPhase(self):
		
		# enemy activation finished, player's turn
		if self.active_player == 1:
			self.active_player = 0
			self.phase = 0
		
		# remaining on player turn
		elif self.phase < 5:
			self.phase += 1
		
		# switching to enemy turn
		else:
			self.phase = 6
			self.active_player = 1
		
		# TODO: do automatic actions at start of phase
		
		# automatically advance at end of player spotting phase
		if self.phase == 1:
			self.advance_phase = True
		
		# TEMP: advance at end of enemy activation
		elif self.active_player == 1:
			self.advance_phase = True
		
		self.UpdateCrewInfoCon()
		self.UpdateCmdCon()
		self.UpdateContextCon()
		self.UpdateTimeCon()
		self.UpdateScenarioDisplay()
		libtcod.console_flush()
		
		# pause here if we are advancing to next phase automatically
		#if self.advance_phase:
		#	Wait(50)
	
	
	# update contextual info console
	def UpdateContextCon(self):
		libtcod.console_clear(context_con)
		
		# Command Phase: display info about current crew command
		if self.phase == 0:
			position = campaign.player_unit.positions_list[self.selected_position]
			libtcod.console_set_default_foreground(context_con, SCEN_PHASE_COL[self.phase])
			libtcod.console_print(context_con, 0, 0, position.crewman.current_cmd)
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			lines = wrap(session.crew_commands[position.crewman.current_cmd]['desc'], 18)
			y = 2
			for line in lines:
				libtcod.console_print(context_con, 0, y, line)
				y += 1
		
		# Movement Phase
		elif self.phase == 2:
			# if we're advancing to next phase automatically, don't display anything here
			if self.advance_phase: return
			
			libtcod.console_set_default_foreground(context_con, libtcod.white)
			libtcod.console_print(context_con, 6, 0, 'Bonus')
			libtcod.console_print(context_con, 14, 0, 'Bog')
			
			libtcod.console_print(context_con, 0, 2, 'Fwd')
			libtcod.console_print(context_con, 0, 4, 'Rev')
			libtcod.console_print(context_con, 0, 6, 'Pivot')
			libtcod.console_print(context_con, 0, 8, 'Repo')
			libtcod.console_print(context_con, 0, 10, 'HD')
			
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			
			# TEMP - will have to poll chances from player unit
			
			# forward move
			libtcod.console_print(context_con, 8, 2, '10%%')
			libtcod.console_print(context_con, 14, 2, '12%%')
			
			# reverse move
			libtcod.console_print(context_con, 8, 4, '0%%')
			libtcod.console_print(context_con, 14, 4, '20%%')
			
			# pivot
			libtcod.console_print(context_con, 8, 6, 'N/A')
			libtcod.console_print(context_con, 14, 6, '2%%')
			
			# reposition
			libtcod.console_print(context_con, 8, 8, '-')
			libtcod.console_print(context_con, 14, 8, '2%%')
			
			# hull down
			libtcod.console_print(context_con, 8, 10, '10%%')
			libtcod.console_print(context_con, 14, 10, '2%%')
			
	
	# update time and phase console
	def UpdateTimeCon(self):
		libtcod.console_clear(time_con)
		libtcod.console_set_default_foreground(time_con, SCEN_PHASE_COL[self.phase])
		libtcod.console_print_ex(time_con, 10, 0, libtcod.BKGND_NONE, libtcod.CENTER, 
			SCEN_PHASE_NAMES[self.phase] + ' Phase')
		libtcod.console_set_default_foreground(time_con, libtcod.white)
	
	
	# update player unit info console
	def UpdatePlayerInfoCon(self):
		libtcod.console_clear(player_info_con)
		campaign.player_unit.DisplayMyInfo(player_info_con, 0, 0)
	
	
	# update the player crew info console
	def UpdateCrewInfoCon(self):
		libtcod.console_clear(crew_con)
		
		y = 0
		i = 0
		
		for position in campaign.player_unit.positions_list:
			
			# highlight position if selected and in command phase
			if i == scenario.selected_position and scenario.phase == 0:
				libtcod.console_set_default_background(crew_con, libtcod.darker_blue)
				libtcod.console_rect(crew_con, 0, y, 25, 3, True, libtcod.BKGND_SET)
				libtcod.console_set_default_background(crew_con, libtcod.black)
			
			# display position name and location in vehicle (eg. turret/hull)
			libtcod.console_set_default_foreground(crew_con, libtcod.light_blue)
			libtcod.console_print(crew_con, 0, y, position.name)
			libtcod.console_set_default_foreground(crew_con, libtcod.white)
			libtcod.console_print_ex(crew_con, 0+24, y, libtcod.BKGND_NONE, 
				libtcod.RIGHT, position.location)
			
			# display last name of crewman and buttoned up / exposed status if any
			if position.crewman is None:
				libtcod.console_print(crew_con, 0, y+1, 'Empty')
			else:
				
				# build string of first initial and last name
				text = position.crewman.first_name[0] + '. ' + position.crewman.last_name
				
				# names might have special characters so we encode it before printing it
				libtcod.console_print(crew_con, 0, y+1, text.encode('IBM850'))
			
				if position.crewman.ce:
					text = 'CE'
				else:
					text = 'BU'
				libtcod.console_print_ex(crew_con, 24, y+1, libtcod.BKGND_NONE, libtcod.RIGHT, text)
			
				# display current command
				
				# truncate string if required
				text = position.crewman.current_cmd
				if len(text) + len(position.crewman.status) > 24:
					text = text[:(19 - len(position.crewman.status))] + '...'
				
				libtcod.console_set_default_foreground(crew_con, libtcod.dark_yellow)
				libtcod.console_print(crew_con, 0, y+2, text)
					
				# display current status on same line
				if position.crewman.status == 'Alert':
					libtcod.console_set_default_foreground(crew_con, libtcod.grey)
				elif position.crewman.status == 'Dead':
					libtcod.console_set_default_foreground(crew_con, libtcod.darker_grey)
				elif position.crewman.status == 'Critical':
					libtcod.console_set_default_foreground(crew_con, libtcod.light_red)
				else:
					libtcod.console_set_default_foreground(crew_con, libtcod.red)
				libtcod.console_print_ex(crew_con, 23, y+2, libtcod.BKGND_NONE, libtcod.RIGHT, 
					position.crewman.status)
				
			libtcod.console_set_default_foreground(crew_con, libtcod.white)
			y += 4
			i += 1
	
	
	# update player command console
	def UpdateCmdCon(self):
		libtcod.console_clear(cmd_menu_con)
		
		# player not active
		if scenario.active_player == 1: return
		
		# Any phase in player activation
		libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
		libtcod.console_print(cmd_menu_con, 1, 10, 'Space')
		libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
		libtcod.console_print(cmd_menu_con, 8, 10, 'End Phase')
		
		# Command phase
		if self.phase == 0:
			libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
			libtcod.console_print(cmd_menu_con, 1, 1, 'W/S')
			libtcod.console_print(cmd_menu_con, 1, 2, 'A/D')
			#libtcod.console_print(cmd_menu_con, 1, 3, 'H')
			
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 1, 'Select Crew')
			libtcod.console_print(cmd_menu_con, 8, 2, 'Select Command')
			#libtcod.console_print(cmd_menu_con, 8, 3, 'Toggle Hatch')
		
		# Movement phase
		elif self.phase == 2:
			
			# if we're advancing to next phase automatically, don't display anything here
			if self.advance_phase: return
			
			libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
			libtcod.console_print(cmd_menu_con, 1, 1, 'W/S')
			libtcod.console_print(cmd_menu_con, 1, 2, 'A/D')
			libtcod.console_print(cmd_menu_con, 1, 3, 'R')
			libtcod.console_print(cmd_menu_con, 1, 4, 'H')
			
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 1, 'Forward/Reverse')
			libtcod.console_print(cmd_menu_con, 8, 2, 'Pivot Hull')
			libtcod.console_print(cmd_menu_con, 8, 3, 'Reposition')
			libtcod.console_print(cmd_menu_con, 8, 4, 'Attempt HD')
			
			

	
	# plot the center of a given in-game hex on the scenario hex map console
	# 0,0 appears in centre of console
	def PlotHex(self, hx, hy):
		x = (hx*7) + 26
		y = (hy*6) + (hx*3) + 21
		return (x,y)
	
	
	# update unit layer console
	def UpdateUnitCon(self):
		
		libtcod.console_clear(unit_con)
		for map_hex in self.map_hexes:
			# no units in hex
			if len(map_hex.unit_stack) == 0: continue
			
			# draw top unit in stack
			map_hex.unit_stack[0].DrawMe()
			
			# FUTURE: draw unit's terrain as well
			
			if len(map_hex.unit_stack) == 1: continue
			# FUTURE: draw stack number indicator if any
	
	
	# update hexmap console
	def UpdateHexmapCon(self):
		
		libtcod.console_clear(hexmap_con)
		
		# FUTURE: can use different hex console images for different battlefield types / weather
		scen_hex = LoadXP('scen_hex.xp')
		libtcod.console_set_key_color(scen_hex, KEY_COLOR)
		
		# draw hexes to hex map console
		for map_hex in self.map_hexes:
			if GetHexDistance(0, 0, map_hex.hx, map_hex.hy) > 3: break
			(x,y) = self.PlotHex(map_hex.hx, map_hex.hy)
			libtcod.console_blit(scen_hex, 0, 0, 0, 0, hexmap_con, x-5, y-3)
			
		del scen_hex
	
	
	# update game message console, which displays most recent game message
	def UpdateMsgConsole(self):
		libtcod.console_clear(msg_con)
	
	
	# draw all scenario consoles to the screen
	def UpdateScenarioDisplay(self):
		
		libtcod.console_clear(con)
		
		# left column
		libtcod.console_blit(bkg_console, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(player_info_con, 0, 0, 0, 0, con, 1, 1)
		libtcod.console_blit(crew_con, 0, 0, 0, 0, con, 1, 21)
		libtcod.console_blit(cmd_menu_con, 0, 0, 0, 0, con, 1, 47)
		
		# main map display
		libtcod.console_blit(hexmap_con, 0, 0, 0, 0, con, 32, 9)
		libtcod.console_blit(unit_con, 0, 0, 0, 0, con, 32, 9, 1.0, 0.0)
		
		# consoles around the edge of map
		libtcod.console_blit(context_con, 0, 0, 0, 0, con, 28, 1)
		libtcod.console_blit(time_con, 0, 0, 0, 0, con, 48, 1)
		libtcod.console_blit(scen_info_con, 0, 0, 0, 0, con, 71, 1)
		
		libtcod.console_blit(msg_con, 0, 0, 0, 0, con, 28, 56)
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
	
	
	# main input loop for scenarios
	def DoScenarioLoop(self):
		
		# set up and load scenario consoles
		global bkg_console, crew_con, cmd_menu_con, scen_info_con
		global player_info_con, context_con, time_con, hexmap_con, unit_con, msg_con
		
		# background outline console for left column
		bkg_console = LoadXP('bkg.xp')
		
		# player unit info console
		player_info_con = libtcod.console_new(25, 18)
		libtcod.console_set_default_background(player_info_con, libtcod.black)
		libtcod.console_set_default_foreground(player_info_con, libtcod.white)
		libtcod.console_clear(player_info_con)
		
		# player crew info console
		crew_con = libtcod.console_new(25, 24)
		libtcod.console_set_default_background(crew_con, libtcod.black)
		libtcod.console_set_default_foreground(crew_con, libtcod.white)
		libtcod.console_clear(crew_con)
		
		# player command menu console
		cmd_menu_con = libtcod.console_new(25, 12)
		libtcod.console_set_default_background(cmd_menu_con, libtcod.black)
		libtcod.console_set_default_foreground(cmd_menu_con, libtcod.white)
		libtcod.console_clear(cmd_menu_con)
		
		# contextual info console
		context_con = libtcod.console_new(18, 12)
		libtcod.console_set_default_background(context_con, libtcod.darkest_grey)
		libtcod.console_set_default_foreground(context_con, libtcod.white)
		libtcod.console_clear(context_con)
		
		# time, phase console
		time_con = libtcod.console_new(21, 6)
		libtcod.console_set_default_background(time_con, libtcod.darkest_grey)
		libtcod.console_set_default_foreground(time_con, libtcod.white)
		libtcod.console_clear(time_con)
		
		# scenario conditions info console
		scen_info_con = libtcod.console_new(18, 12)
		libtcod.console_set_default_background(scen_info_con, libtcod.darkest_grey)
		libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
		libtcod.console_clear(scen_info_con)
		
		# unit layer console
		unit_con = libtcod.console_new(53, 43)
		libtcod.console_set_default_background(unit_con, KEY_COLOR)
		libtcod.console_set_default_foreground(unit_con, libtcod.white)
		libtcod.console_set_key_color(unit_con, KEY_COLOR)
		libtcod.console_clear(unit_con)
		
		# hex map console
		hexmap_con = libtcod.console_new(53, 43)
		libtcod.console_set_default_background(hexmap_con, libtcod.black)
		libtcod.console_set_default_foreground(hexmap_con, libtcod.black)
		libtcod.console_clear(hexmap_con)
		
		# game message console
		msg_con = libtcod.console_new(61, 4)
		libtcod.console_set_default_background(msg_con, libtcod.darkest_grey)
		libtcod.console_set_default_foreground(msg_con, libtcod.white)
		libtcod.console_clear(msg_con)
		
		
		# set up player unit
		campaign.player_unit.ResetMe()
		campaign.player_unit.facing = 0
		campaign.player_unit.turret_facing = 0
		campaign.player_unit.SpawnAt(0,0)
		
		# generate an enemy unit
		unit = Unit('7TP')
		unit.owning_player = 1
		unit.facing = 3
		unit.turret_facing = 3
		unit.SpawnAt(0,-2)
		campaign.enemy_units.append(unit)
		
		# set up player unit for first activation
		campaign.player_unit.BuildCmdLists()
		
		# generate consoles and draw scenario screen for first time
		self.UpdateContextCon()
		self.UpdateTimeCon()
		self.UpdatePlayerInfoCon()
		self.UpdateCrewInfoCon()
		self.UpdateCmdCon()
		self.UpdateUnitCon()
		self.UpdateHexmapCon()
		self.UpdateMsgConsole()
		self.UpdateScenarioDisplay()
		
		
		exit_scenario = False
		while not exit_scenario:
			
			# emergency exit in case of endless loop
			if libtcod.console_is_window_closed(): sys.exit()
			
			libtcod.console_flush()
			
			# trigger advance to next phase
			if self.advance_phase:
				self.advance_phase = False
				self.AdvanceToNextPhase()
				continue
			
			# get keyboard and/or mouse event
			keypress = GetInputEvent()
			
			##### Mouse Commands #####
			
			##### Player Keyboard Commands #####
			
			# no keyboard input
			if not keypress: continue
			
			# key commands
			key_char = chr(key.c).lower()
			
			# TEMP - exit game
			if key_char == 'q':
				exit_scenario = True
				continue
			
			# player not active
			if scenario.active_player == 1: continue
			
			# Any Phase
			
			# advance to next phase
			if key.vk == libtcod.KEY_SPACE:
				self.advance_phase = True
				continue
			
			
			# Command Phase only
			if scenario.phase == 0:
				
				# change selected crew position
				if key_char in ['w', 's']:
					
					if key_char == 'w':
						scenario.selected_position -= 1
						if scenario.selected_position < 0:
							scenario.selected_position = len(campaign.player_unit.positions_list) - 1
					
					else:
						scenario.selected_position += 1
						if scenario.selected_position == len(campaign.player_unit.positions_list):
							scenario.selected_position = 0
				
					self.UpdateContextCon()
					self.UpdateCrewInfoCon()
					self.UpdateScenarioDisplay()
					continue
				
				# change current command for selected crewman
				elif key_char in ['a', 'd']:
					
					# no crewman in selected position
					crewman = campaign.player_unit.positions_list[scenario.selected_position].crewman
					if crewman is None:
						continue
					
					if key_char == 'a':
						crewman.SelectCommand(True)
					else:
						crewman.SelectCommand(False)
					
					self.UpdateContextCon()
					self.UpdateCrewInfoCon()
					self.UpdateScenarioDisplay()
					continue
			


##########################################################################################
#                                  General Functions                                     #
##########################################################################################	

# get keyboard and/or mouse event; returns False if no new key press
def GetInputEvent():
	event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
		key, mouse)
	if session.key_down:
		if event != libtcod.EVENT_KEY_RELEASE:
			return False
		session.key_down = False
	if event != libtcod.EVENT_KEY_PRESS:
		return False
	session.key_down = True
	return True


# clear all keyboard events
def FlushKeyboardEvents():
	exit = False
	while not exit:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
		if event != libtcod.EVENT_KEY_PRESS: exit = True
	session.key_down = False


# wait for a specified amount of miliseconds, refreshing the screen in the meantime
def Wait(wait_time):
	wait_time = wait_time * 0.01
	start_time = time.time()
	while time.time() - start_time < wait_time:
		FlushKeyboardEvents()


# load a console image from an .xp file
def LoadXP(filename):
	xp_file = gzip.open(DATAPATH + filename)
	raw_data = xp_file.read()
	xp_file.close()
	xp_data = xp_loader.load_xp_string(raw_data)
	console = libtcod.console_new(xp_data['width'], xp_data['height'])
	xp_loader.load_layer_to_console(console, xp_data['layer_data'][0])
	return console


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


# constrain a direction to a value 0-5
def ConstrainDir(direction):
	while direction < 0:
		direction += 6
	while direction > 5:
		direction -= 6
	return direction


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
	return ''


# returns a ring of hexes around a center point for a given radius
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


# returns the compass bearing from x1, y1 to x2, y2
def GetBearing(x1, y1, x2, y2):
	return int((degrees(atan2((y2 - y1), (x2 - x1))) + 90.0) % 360)


# returns a bearing from 0-359 degrees
def RectifyBearing(h):
	while h < 0: h += 360
	while h > 359: h -= 360
	return h


# get the bearing from unit1 to unit2, rotated for unit1's facing
def GetRelativeBearing(unit1, unit2):
	(x1, y1) = PlotHex(unit1.hx, unit1.hy)
	(x2, y2) = PlotHex(unit2.hx, unit2.hy)
	bearing = GetBearing(x1, y1, x2, y2)
	return RectifyBearing(bearing - (unit1.facing * 60))


# get the relative facing of one unit from the point of view of another unit
# unit1 is the observer, unit2 is being observed
def GetFacing(attacker, target, turret_facing=False):
	bearing = GetRelativeBearing(target, attacker)
	if turret_facing and target.turret_facing is not None:
		turret_diff = target.turret_facing - target.facing
		bearing = RectifyBearing(bearing - (turret_diff * 60))
	if bearing >= 300 or bearing <= 60:
		return 'Front'
	return 'Side'
	

# try to load game settings from config file
def LoadCFG():
	
	global config
	
	config = ConfigParser()
	
	# create a new config file
	if not os.path.exists(DATAPATH + 'armcom2.cfg'):
		
		config['ArmCom2'] = {
			'large_display_font' : 'true',
			'sounds_enabled' : 'true',
			'keyboard' : '0'
		}
		
		# write to disk
		with open(DATAPATH + 'armcom2.cfg', 'w') as configfile:
			config.write(configfile)
	else:
		# load config file
		config.read(DATAPATH + 'armcom2.cfg')



##########################################################################################
#                                      Main Script                                       #
##########################################################################################

global campaign, scenario, session 

print('Starting ' + NAME + ' version ' + VERSION)	# startup message

# try to load game settings from config file, will create a new file if none present
LoadCFG()

os.putenv('SDL_VIDEO_CENTERED', '1')			# center game window on screen

# determine font to use based on settings file
if config['ArmCom2'].getboolean('large_display_font'):
	fontname = 'c64_16x16.png'
else:
	fontname = 'c64_8x8.png'

# set up custom font and root console
libtcod.console_set_custom_font(DATAPATH+fontname, libtcod.FONT_LAYOUT_ASCII_INROW,
        0, 0)
libtcod.console_init_root(WINDOW_WIDTH, WINDOW_HEIGHT, NAME + ' - ' + VERSION,
	fullscreen = False, renderer = RENDERER)

libtcod.sys_set_fps(LIMIT_FPS)
libtcod.console_set_default_background(0, libtcod.black)
libtcod.console_set_default_foreground(0, libtcod.white)
libtcod.console_clear(0)

# display loading screen
libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER, 'Loading...')
libtcod.console_flush()

# create new session object
session = Session()

# try to init sound mixer and load sounds if successful
main_theme = None

if config['ArmCom2'].getboolean('sounds_enabled'):
	if session.InitMixer():
		session.LoadSounds()
		# load and play main menu theme
		main_theme = mixer.Mix_LoadMUS((SOUNDPATH + 'armcom2_theme.ogg').encode('ascii'))
		mixer.Mix_PlayMusic(main_theme, -1)
	else:
		config['ArmCom2']['sounds_enabled'] = 'false'
		print('Not able to init mixer, sounds disabled')

# create double buffer console
con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(con, libtcod.black)
libtcod.console_set_default_foreground(con, libtcod.white)
libtcod.console_clear(con)

# create darken screen console
darken_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(darken_con, libtcod.black)
libtcod.console_set_default_foreground(darken_con, libtcod.black)
libtcod.console_clear(darken_con)

# create game menu console: 84x54
game_menu_bkg = LoadXP('game_menu.xp')
game_menu_con = libtcod.console_new(84, 54)
libtcod.console_set_default_background(game_menu_con, libtcod.black)
libtcod.console_set_default_foreground(game_menu_con, libtcod.white)
libtcod.console_clear(game_menu_con)

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()


# TEMP testing

# create a new campaign and player unit
campaign = Campaign()
campaign.player_unit = Unit('Panzer 35(t)')
campaign.player_unit.nation = 'Germany'
campaign.player_unit.GenerateNewPersonnel()


# create a new scenario
scenario = Scenario()

# run the scenario
scenario.DoScenarioLoop()


print(NAME + ' shutting down')			# shutdown message
# END #

