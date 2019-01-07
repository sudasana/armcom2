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
ALLIED_UNIT_COL = libtcod.Color(120, 120, 255)		# allied unit display colour
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
	libtcod.yellow, libtcod.purple, libtcod.green, libtcod.red, libtcod.white,
	libtcod.blue, libtcod.light_red 
]

# order to display ammo types
AMMO_TYPES = ['HE', 'AP']

# list of MG-type weapons
MG_WEAPONS = ['Co-ax MG', 'Turret MG', 'Hull MG', 'AA MG']

# text names for months
MONTH_NAMES = [
	'', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
	'September', 'October', 'November', 'December'
]


##########################################################################################
#                                    Engine Constants                                    #
##########################################################################################

# TODO: move these to JSON file

# length of scenario turn in minutes
TURN_LENGTH = 2

# maximum visible distance when buttoned up
MAX_BU_LOS = 1

# base chance to spot unit at distance 0,1,2,3
SPOT_BASE_CHANCE = [50.0, 40.0, 25.0, 5.0]

# each point of Perception increases chance to spot enemy unit by this much
PERCEPTION_SPOTTING_MOD = 3.0

# base chance of moving forward/backward into next hex
BASE_FORWARD_MOVE_CHANCE = 50.0
BASE_REVERSE_MOVE_CHANCE = 20.0

# bonus per unsuccessful move attempt
BASE_MOVE_BONUS = 15.0

# critical hit and miss thresholds
CRITICAL_HIT = 3.0
CRITICAL_MISS = 97.0

# maximum range at which MG attacks have a chance to penetrate armour
MG_AP_RANGE = 1

# base success chances for point fire attacks
# first column is for vehicle targets, second is everything else
PF_BASE_CHANCE = [
	[88.0, 78.0],			# same hex
	[73.0, 68.0],			# 1 hex range
	[62.0, 48.0],			# 2 "
	[48.0, 25.0]			# 3 hex range
]

# modifier for target size if target is known
PF_SIZE_MOD = {
	'Very Small' : -28.0,
	'Small' : -12.0,
	'Large' : 12.0,
	'Very Large' : 28.0
}

# base chances of partial effect for area fire attacks: infantry/gun and vehicle targets
INF_FP_BASE_CHANCE = 30.0
VEH_FP_BASE_CHANCE = 20.0

FP_CHANCE_STEP = 5.0		# each additional firepower beyond 1 adds this additional chance
FP_CHANCE_STEP_MOD = 0.95	# additional firepower modifier reduced by this much beyond 1
FP_FULL_EFFECT = 0.75		# multiplier for full effect
FP_CRIT_EFFECT = 0.1		# multipler for critical effect

# base success chances for armour penetration
AP_BASE_CHANCE = {
	'MG' : 16.7,
	'AT Rifle' : 28.0,
	'20L' : 28.0,
	'37S' : 58.4,
	'37' : 72.0,
	'37L' : 83.0,
	'47S' : 72.0,
	'75S' : 91.7,
	'75' : 120.0,		# not sure if this and below are accurate, FUTURE: check balance
	'75L' : 160.0,
	'88L' : 200.0
}

# effective FP of an HE hit from different weapon calibres
HE_FP_EFFECT = [
	(200, 36),(183, 34),(170, 32),(160, 31),(150, 30),(140, 28),(128, 26),(120, 24),
	(107, 22),(105, 22),(100, 20),(95, 19),(88, 18),(85, 17),(80, 16),(75, 14),
	(70, 12),(65, 10),(60, 8),(57, 7),(50, 6),(45, 5),(37, 4),(30, 2),(25, 2),(20, 1)
]

# penetration chance on armour of HE hits
HE_AP_CHANCE = [
	(150, 110.0),
	(120, 100.0),
	(100, 91.7),
	(80, 72.2),
	(70, 58.4),
	(50, 41.7),
	(40, 27.8),
	(30, 16.7),
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



# Campaign Day: represents one calendar day in a campaign with a 5x7 map of terrain hexes, each of
# which may spawn a Scenario
class CampaignDay:
	def __init__(self):
		
		# current year, month, day, hour, and minute
		self.calendar = {
			'year' : 1939,
			'month' : 9,
			'day' : 1,
			'hour' : 4,
			'minute' : 45
		}
	
	# advance the current campaign time
	# FUTURE: handle rolling over into a new day: might happen eg. in days that start at dusk
	def AdvanceClock(self, hours, minutes):
		self.calendar['hour'] += hours
		self.calendar['minute'] += minutes
		while self.calendar['minute'] >= 60:
			self.calendar['hour'] += 1
			self.calendar['minute'] -= 60
		
		

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
		
		# background for attack console
		self.attack_bkg = LoadXP('attack_bkg.xp')
		
		# game menu background console
		self.game_menu_bkg = LoadXP('game_menu.xp')
		
		# field of view highlight on scenario hex map
		self.scen_hex_fov = LoadXP('scen_hex_fov.xp')
		libtcod.console_set_key_color(self.scen_hex_fov, KEY_COLOR)
	
	
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
		
		self.stats = {					# default values for modification
			'Perception' : 3,
			'Grit' : 3,
			'Knowledge' : 3,
			'Morale' : 3
		}
		self.SetStats()
		
		self.ce = False					# crewman is exposed in a vehicle
		self.SetCEStatus()				# set CE status
		
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
	
	
	# randomly modify initial stat values
	def SetStats(self):		
		for i in range(5):
			key = choice(list(self.stats))
			self.stats[key] += 1 
			key = choice(list(self.stats))
			self.stats[key] -= 1
		
		for key in self.stats:
			if self.stats[key] < 1:
				self.stats[key] = 1
			elif self.stats[key] > 5:
				self.stats[key] = 5
	
	
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
	
	
	# attempt to toggle current hatch status
	def ToggleHatch(self):
		
		# no hatch in position
		if not self.current_position.hatch: return False
		if self.current_position.open_top: return False
		if self.current_position.crew_always_ce: return False
		
		self.current_position.hatch_open = not self.current_position.hatch_open
		
		# FUTURE: change other hatches in this group if any
		
		# set CE status based on new hatch status
		self.SetCEStatus()
		
		return True
	
	
	# set crewman BU/CE status based on position status
	def SetCEStatus(self):
		
		if not self.current_position.hatch:
			self.ce = False
			return
		
		if self.current_position.open_top or self.current_position.crew_always_ce:
			self.ce = True
			return
		
		if self.current_position.hatch_open:
			self.ce = True
		else:
			self.ce = False
	

# Position class: represents a personnel position within a unit
class Position:
	def __init__(self, unit, position_dict):
		
		self.unit = unit
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
		
		# current hatch open/closed status
		self.hatch_open = False
		
		# list of map hexes visible to this position
		self.visible_hexes = []
	
	
	# update the list of hexes currently visible from this position
	def UpdateVisibleHexes(self):
		
		self.visible_hexes = []
		
		if self.crewman is None: return
		
		# can always spot in own hex
		self.visible_hexes.append((self.unit.hx, self.unit.hy))
		
		# current crew command does not allow spotting
		if session.crew_commands[self.crewman.current_cmd]['spotting_allowed'] == 'FALSE':
			return
		
		if self.hatch_open:
			direction_list = self.ce_visible
		else:
			direction_list = self.bu_visible
		
		for direction in direction_list:
			hextant_hex_list = GetCoveredHexes(self.unit.hx, self.unit.hy, direction)
			for (hx, hy) in hextant_hex_list:
				# hex is off map
				if (hx, hy) not in scenario.hex_dict: continue
				# already in list
				if (hx, hy) in self.visible_hexes: continue
				# too far away for BU crew
				if not self.hatch_open:
					if GetHexDistance(self.unit.hx, self.unit.hy, hx, hy) > MAX_BU_LOS:
						continue
				self.visible_hexes.append((hx, hy))



# Weapon Class: represents a weapon mounted on or carried by a unit
class Weapon:
	def __init__(self, stats):
		self.stats = stats
		
		# some weapons need a descriptive name generated
		if 'name' not in self.stats:
			if self.GetStat('type') == 'Gun':
				text = self.GetStat('calibre') + 'mm'
				if self.GetStat('long_range') is not None:
					text += '(' + self.GetStat('long_range') + ')'
				self.stats['name'] = text
			else:
				self.stats['name'] = self.GetStat('type')
		
		# save maximum range as an local int
		self.max_range = 3
		if 'max_range' in self.stats:
			self.max_range = int(self.stats['max_range'])
			del self.stats['max_range']
		else:
			if self.stats['type'] in ['Turret MG', 'Co-ax MG']:
				self.max_range = 2
			elif self.stats['type'] in ['Hull MG', 'AA MG']:
				self.max_range = 1
		
		self.ammo_type = None
		
		# if weapon is a gun, set up ammo stores
		self.ammo_stores = None
		if self.GetStat('type') == 'Gun' and 'ammo_type_list' in self.stats:
			self.ammo_stores = {}
			self.LoadGunAmmo()
		
		self.ResetMe()
	
	
	# load this gun full of ammo
	def LoadGunAmmo(self):
		
		if not self.GetStat('type') == 'Gun': return
		
		# set up empty categories first
		for ammo_type in self.stats['ammo_type_list']:
			self.ammo_stores[ammo_type] = 0
		
		# now determine loadout
		max_ammo = int(self.stats['max_ammo'])
		
		# only one type, fill it up
		if len(self.stats['ammo_type_list']) == 1:
			ammo_type = self.stats['ammo_type_list'][0]
			self.ammo_stores[ammo_type] = max_ammo
			self.ammo_type = ammo_type
		
		# HE and AP: 70% and 30%
		else:
			if self.stats['ammo_type_list'] == ['HE', 'AP']:
				self.ammo_stores['HE'] = int(max_ammo * 0.7)
				self.ammo_stores['AP'] = max_ammo - self.ammo_stores['HE']
				self.ammo_type = 'AP'
	
	
	# set/reset all scenario statuses
	def ResetMe(self):
		self.fired = False
	
	
	# cycle to use next available ammo type
	def CycleAmmo(self):
		
		# no other types possible
		if len(self.stats['ammo_type_list']) == 1:
			return False
		
		i = self.stats['ammo_type_list'].index(self.ammo_type)
		if i == len(self.stats['ammo_type_list']) - 1:
			i = 0
		else:
			i += 1
		
		self.ammo_type = self.stats['ammo_type_list'][i]
		
		return True
			
	
	# check for the value of a stat, return None if stat not present
	def GetStat(self, stat_name):
		if stat_name not in self.stats:
			return None
		return self.stats[stat_name]
	
	
	# return the effective FP of an HE hit from this gun
	def GetEffectiveFP(self):
		if self.GetStat('type') != 'Gun':
			print('ERROR: ' + self.stats['name'] + ' is not a gun, cannot generate effective FP')
			return 1
		
		for (calibre, fp) in HE_FP_EFFECT:
			if calibre <= int(self.GetStat('calibre')):
				return fp
		
		print('ERROR: Could not find effective FP for: ' + self.stats['name'])
		return 1
	
	
	# return the base penetration chance of an HE hit from this gun
	def GetBaseHEPenetrationChance(self):
		if self.GetStat('type') != 'Gun':
			print('ERROR: ' + self.stats['name'] + ' is not a gun, cannot generate HE AP chance')
			return 0.0
		
		for (calibre, chance) in HE_AP_CHANCE:
			if calibre <= int(self.GetStat('calibre')):
				return chance
		
		print('ERROR: Could not find HE AP chance for: ' + self.stats['name'])
		return 0.0



# AI: controller for enemy and player-allied units
class AI:
	def __init__(self, owner):
		self.owner = owner			# pointer to owning Unit
		self.disposition = None			# records type of action for this activation

	# do activation for this unit
	def DoActivation(self):
		
		# no action if it's not alive
		if not self.owner.alive: return
		
		print('AI DEBUG: ' + self.owner.unit_id + ' now acting')
		
		roll = GetPercentileRoll()
		
		# Step 1: roll for unit action
		if self.owner.GetStat('category') == 'Infantry':
			if roll <= 75.0:
				self.disposition = 'Combat'
			elif roll <= 90.0:
				if self.owner.pinned:
					self.disposition = 'Combat'
				else:
					self.disposition = 'Movement'
			else:
				self.disposition = None
		
		elif self.owner.GetStat('category') == 'Gun':
			
			if not self.owner.deployed:
				self.disposition = None
			else:
				if roll >= 80.0:
					self.disposition = None
				else:
					self.disposition = 'Combat'
		
		else:
			if roll <= 65.0:
				self.disposition = 'Combat'
			elif roll <= 85.0:
				self.disposition = 'Movement'
			else:
				self.disposition = None
					
		
		current_range = GetHexDistance(0, 0, self.owner.hx, self.owner.hy)
		
		# no combat if unit is off-map
		if current_range > 3:
			if self.disposition == 'Combat':
				self.disposition = None
		
		# Step 2: Determine action to take
		if self.disposition == 'Movement':
			
			# build a list of adjacent hexes
			hex_list = GetHexRing(self.owner.hx, self.owner.hy, 1)
			
			for (hx, hy) in reversed(hex_list):
				
				# don't move into player's hex
				if hx == 0 and hy == 0:
					hex_list.remove((hx, hy))
					continue
				
				# destination is on map, check if 1+ enemy units present
				if (hx, hy) in scenario.hex_dict:
					for unit in scenario.hex_dict[(hx,hy)].unit_stack:
						if unit.owning_player != self.owner.owning_player:
							hex_list.remove((hx, hy))
							continue
				
				# if range would change, chance that this hex gets thrown out
				if GetHexDistance(0, 0, hx, hy) != current_range:
					if GetPercentileRoll() <= 60.0:
						hex_list.remove((hx, hy))
						continue
			
			# no possible moves
			if len(hex_list) == 0:
				return
			
			(hx, hy) = choice(hex_list)
			
			# if destination is off-map, remove from game
			if (hx, hy) not in scenario.hex_dict:
				self.owner.RemoveFromPlay()
				return
			
			scenario.Message(self.owner.GetName() + ' moves')
			
			# turn to face destination
			if self.owner.facing is not None:
				direction = GetDirectionToAdjacent(self.owner.hx, self.owner.hy, hx, hy)
				self.owner.facing = direction
				if self.owner.turret_facing is not None:
					self.owner.turret_facing = direction
			
			# move into new hex
			scenario.hex_dict[(self.owner.hx, self.owner.hy)].unit_stack.remove(self.owner)
			self.owner.hx = hx
			self.owner.hy = hy
			scenario.hex_dict[(hx, hy)].unit_stack.append(self.owner)
			
			self.owner.moving = True
			self.owner.ClearAcquiredTargets()
			
			scenario.UpdateUnitCon()
			scenario.UpdateScenarioDisplay()
			libtcod.console_flush()
		
		elif self.disposition == 'Combat':
			
			# only a small chance that they will attack player, higher if they were
			# fired upon by player and/or have acquired player as target
			
			# determine target
			target_list = []
			
			for unit in scenario.units:
				if unit.owning_player == 1: continue
				if GetHexDistance(0, 0, unit.hx, unit.hy) > 3: continue
				target_list.append(unit)
			
			# no possible targets
			if len(target_list) == 0:
				print ('AI DEBUG: No possible targets for ' + self.owner.unit_id)
				return
			
			# score possible weapon-target combinations
			attack_list = []
			
			for target in target_list:
				for weapon in self.owner.weapon_list:
					
					# gun weapons need to check multiple ammo type combinations
					if weapon.GetStat('type') == 'Gun':
						ammo_list = weapon.stats['ammo_type_list']
						for ammo_type in ammo_list:
							
							weapon.current_ammo = ammo_type
							result = scenario.CheckAttack(self.owner, weapon, target, ignore_facing=True)
							# attack not possible
							if result != '':
								continue
							attack_list.append((weapon, target, ammo_type))
						continue
					
					result = scenario.CheckAttack(self.owner, weapon, target, ignore_facing=True)
					if result != '':
						continue
					attack_list.append((weapon, target, ''))
			
			# no possible attacks
			if len(attack_list) == 0:
				print ('AI DEBUG: No possible attacks for ' + self.owner.unit_id)
				return
			
			# TODO: score possible weapon-target combinations
			
			# TEMP
			print ('AI DEBUG: ' + str(len(attack_list)) + ' possible attacks for ' + self.owner.unit_id)
			
			# TEMP - choose random attack
			(weapon, target, ammo_type) = choice(attack_list)
			
			# re-roll if player target
			if target == campaign.player_unit:
				(weapon, target, ammo_type) = choice(attack_list)
			
			if ammo_type != '':
				weapon.current_ammo = ammo_type
			
			scenario.Message(self.owner.GetName() + ' fires at ' + target.GetName())
			
			result = self.owner.Attack(weapon, target)
			
			
			



# Unit Class: represents a single vehicle or gun, or a squad or small team of infantry
class Unit:
	def __init__(self, unit_id):
		
		self.unit_id = unit_id			# unique ID for unit type
		self.alive = True			# unit is alive
		self.owning_player = 0			# unit is allied to 0:player 1:enemy
		self.nation = None			# nationality of unit and personnel
		self.ai = None				# AI controller if any
		
		self.squad = None			# list of units in player squad
		
		self.positions_list = []		# list of crew/personnel positions
		self.personnel_list = []		# list of crew/personnel
		
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
				self.positions_list.append(Position(self, position_dict))
		
		# set up weapons
		self.weapon_list = []			# list of unit weapons
		weapon_list = self.stats['weapon_list']
		if weapon_list is not None:
			for weapon_dict in weapon_list:
				self.weapon_list.append(Weapon(weapon_dict))
			
			# clear this stat since we don't need it any more
			self.stats['weapon_list'] = None
		
		# set up initial scenario statuses
		self.ResetMe()
	
	
	# set/reset all scenario statuses
	def ResetMe(self):
		
		self.hx = 0				# location in scenario hex map
		self.hy = 0
		self.dest_hex = None			# destination hex for move
		
		self.spotted = False			# unit has been spotted by opposing side
		
		self.hull_down = []			# list of directions unit in which Hull Down
		self.moving = False
		self.fired = False
		self.hit_by_fp = False			# was hit by an effective fp attack
		
		self.facing = None
		self.previous_facing = None
		self.turret_facing = None
		self.previous_turret_facing = None
		
		self.pinned = False
		self.deployed = False
		
		self.acquired_target = None		# tuple: unit has acquired this unit to this level (1/2)
		
		self.forward_move_chance = 0.0		# set by CalculateMoveChances()
		self.reverse_move_chance = 0.0
		
		self.forward_move_bonus = 0.0
		self.reverse_move_bonus = 0.0
		
		self.fp_to_resolve = 0			# fp from attacks to be resolved
		self.ap_hits_to_resolve = []		# list of unresolved AP hits
	
	
	# reset this unit for new turn
	def ResetForNewTurn(self):
		
		self.moving = False
		self.previous_facing = self.facing
		self.previous_turret_facing = self.turret_facing
		
		self.fired = False
		for weapon in self.weapon_list:
			weapon.ResetMe()
		
		# select first player weapon if none selected so far
		if self == campaign.player_unit:
			if scenario.selected_weapon is None:
				scenario.selected_weapon = self.weapon_list[0]
		
		# update visible hexes for crew positions
		for position in self.positions_list:
			position.UpdateVisibleHexes()
		
	
	# check for the value of a stat, return None if stat not present
	def GetStat(self, stat_name):
		if stat_name not in self.stats:
			return None
		return self.stats[stat_name]
	
	
	# get a descriptive name of this unit
	def GetName(self):
		if self.owning_player == 1 and not self.spotted:
			return 'Unspotted Unit'
		return self.unit_id
	
	
	# return the person in the given position
	def GetPersonnelByPosition(self, position_name):
		for position in self.positions_list:
			if position.crewman is None: continue
			if position.name == position_name:
				return position.crewman
		return None
	
	
	# clear any acquired target from this unit, and clear it from any enemy unit
	def ClearAcquiredTargets(self):
		self.acquired_target = None
		for unit in scenario.units:
			if unit.owning_player == self.owning_player: continue
			if unit.acquired_target is None: continue
			(target, level) = unit.acquired_target
			if target == self:
				unit.acquired_target = None
	
	
	# set a newly acquired target, or add a level
	def AddAcquiredTarget(self, target):
		
		# no previous acquired target
		if self.acquired_target is None:
			self.acquired_target = (target, False)
			return
		
		(old_target, level) = self.acquired_target
		
		# had an old target but now have a new one
		if old_target != target:
			self.acquired_target = (target, False)
			return
		
		# possible to add one level
		if not level:
			self.acquired_target = (target, True)
			return
		
		# otherwise, already acquired target to 2 levels, no further effect
	
	
	# calcualte chances of a successful forward/reverse move action
	def CalculateMoveChances(self):
		
		# set values to base values
		self.forward_move_chance = BASE_FORWARD_MOVE_CHANCE
		self.reverse_move_chance = BASE_REVERSE_MOVE_CHANCE
		
		# add bonuses from previous moves
		self.forward_move_chance += self.forward_move_bonus
		self.reverse_move_chance += self.reverse_move_bonus
		
	
	# build lists of possible commands for each personnel in this unit
	def BuildCmdLists(self):
		for position in self.positions_list:
			if position.crewman is None: continue
			position.crewman.BuildCommandList()
	
	
	# do a round of spotting from this unit
	def DoSpotChecks(self):
		
		# unit out of play range
		if GetHexDistance(0, 0, self.hx, self.hy) > 3:
			return
		
		# create a local list of crew positions in a random order
		position_list = sample(self.positions_list, len(self.positions_list))
		
		for position in position_list:
			
			# no crewman in position
			if position.crewman is None: continue
			
			# build list of units it's possible to spot
			
			spot_list = []
			for unit in scenario.units:
				if unit.owning_player == self.owning_player:
					continue
				if not unit.alive:
					continue
				if unit.spotted:
					continue
				if (unit.hx, unit.hy) not in position.visible_hexes:
					continue
				
				spot_list.append(unit)
			
			# no units possible to spot from this position
			if len(spot_list) == 0:
				continue
			
			# roll once for each unit
			for unit in spot_list:
			
				distance = GetHexDistance(self.hx, self.hy, unit.hx, unit.hy)
				
				chance = SPOT_BASE_CHANCE[distance]
				
				# target size
				size_class = unit.GetStat('size_class')
				if size_class is not None:
					if size_class == 'Small':
						chance -= 7.0
					elif size_class == 'Very Small':
						chance -= 18.0
					elif size_class == 'Large':
						chance += 7.0
					elif size_class == 'Very Large':
						chance += 18.0
				
				# target moving
				if unit.moving:
					chance = chance * 1.5
				
				# target fired
				if unit.fired:
					chance = chance * 2.0
				
				# infantry are not as good at spotting from their lower position
				if self.GetStat('category') == 'Infantry':
					chance = chance * 0.5
				
				# snipers are hard to spot
				if unit.unit_id == 'Sniper':
					chance = chance * 0.25
				
				# perception modifier
				chance += float(position.crewman.stats['Perception']) * PERCEPTION_SPOTTING_MOD
				
				chance = RestrictChance(chance)
				
				# special: target was hit by effective fp last turn
				if unit.hit_by_fp > 0:
					chance = 100.0
				
				roll = GetPercentileRoll()
				
				print('DEBUG: rolling to spot ' + unit.unit_id + ', chance is ' + str(chance) +
					', roll was ' + str(roll))
				
				if roll <= chance:
					
					unit.SpotMe()
					scenario.UpdateUnitCon()
					scenario.UpdateScenarioDisplay()
					
					# display message
					if self.owning_player == 0:
						text = unit.GetName() + ' ' + unit.GetStat('class')
						text += ' spotted!'
						scenario.Message(text)
					elif unit == campaign.player_unit:
						scenario.Message('You have been spotted!')
	
	
	# reveal this unit after being spotted
	def SpotMe(self):
		self.spotted = True
		
	
	
	# generate new personnel sufficent to fill all personnel positions
	def GenerateNewPersonnel(self):
		self.personnel_list = []
		for position in self.positions_list:
			self.personnel_list.append(Personnel(self, self.nation, position))
			position.crewman = self.personnel_list[-1]
	
	
	# move this unit into the given scenario map hex
	def SpawnAt(self, hx, hy):
		self.hx = hx
		self.hy = hy
		scenario.units.append(self)
		for map_hex in scenario.map_hexes:
			if map_hex.hx == hx and map_hex.hy == hy:
				map_hex.unit_stack.append(self)
				return
	
	
	# move this unit to the top of its current hex stack
	def MoveToTopOfStack(self):
		map_hex = scenario.hex_dict[(self.hx, self.hy)]
		
		# only unit in stack
		if len(map_hex.unit_stack) == 1:
			return
		
		# not actually in stack
		if self not in map_hex.unit_stack:
			return
		
		map_hex.unit_stack.remove(self)
		map_hex.unit_stack.insert(0, self)
	
	
	# remove this unit from the scenario
	def RemoveFromPlay(self):
		# remove from hex stack
		scenario.hex_dict[(self.hx, self.hy)].unit_stack.remove(self)
		# remove from scenario unit list
		scenario.units.remove(self)
		print ('DEBUG: removed a ' + self.unit_id + ' from play')
	
	
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
	
	
	# initiate an attack from this unit with the specified weapon against the specified target
	def Attack(self, weapon, target):
		
		# make sure correct information has been supplied
		if weapon is None or target is None:
			return False
		
		# make sure attack is possible
		if scenario.CheckAttack(self, weapon, target) != '':
			return False
		
		# calculate attack profile
		profile = scenario.CalcAttack(self, weapon, target)
		
		# attack not possible
		if profile is None: return False
		
		# display attack profile on screen if player involved
		if self == campaign.player_unit or target == campaign.player_unit:
			scenario.DisplayAttack(profile)
		
			# allow player to cancel attack
			if WaitForContinue(allow_cancel=True):
				return True
		
		# TODO: attack animation
				
		# set weapon and unit fired flags
		weapon.fired = True
		self.fired = True
		
		# do the roll, display results to the screen, and modify the attack profile
		profile = scenario.DoAttackRoll(profile)
		
		# wait for the player if they are involved
		if self == campaign.player_unit or target == campaign.player_unit:
			WaitForContinue()
		
		# add one level of acquired target if firing gun
		if weapon.GetStat('type') == 'Gun':
			self.AddAcquiredTarget(target)
		
		# apply results of this attack if any
		
		# area fire attack
		if profile['type'] == 'Area Fire':
				
			if profile['result'] in ['CRITICAL EFFECT', 'FULL EFFECT', 'PARTIAL EFFECT']:
				
				target.fp_to_resolve += profile['effective_fp']
				
				# target will automatically be spotted next turn if possible
				if not target.spotted:
					target.hit_by_fp = True
			
			# possible it was converted into an AP MG hit
			elif profile['result'] in ['HIT', 'CRITICAL HIT']:	
				target.ap_hits_to_resolve.append(profile)
		
		# ap attack hit
		elif profile['result'] in ['CRITICAL HIT', 'HIT']:
			
			# armoured target
			if target.GetStat('armour') is not None:
				target.ap_hits_to_resolve.append(profile)
		
		# TEMP attack is finished
		return True
	
	
	# resolve all unresolved FP and AP hits on this unit
	def ResolveHits(self):
		
		# no hits to resolve! doing fine!
		if self.fp_to_resolve == 0 and len(self.ap_hits_to_resolve) == 0: return
		
		# move to top of hex stack
		self.MoveToTopOfStack()
		scenario.UpdateUnitCon()
		
		# FUTURE: handle FP first
		#self.ResolveFP()
		self.fp_to_resolve == 0
		if not self.alive: return
		
		# handle AP hits
		for profile in self.ap_hits_to_resolve:
			
			# unit is armoured
			if self.GetStat('armour') is not None:
				
				profile = scenario.CalcAP(profile)
				scenario.DisplayAttack(profile)
				
				# wait if player is involved
				if profile['attacker'] == campaign.player_unit or self == campaign.player_unit:
					WaitForContinue()
				
				# do the attack roll; modifies the attack profile
				profile = scenario.DoAttackRoll(profile)
				
				# wait if player is involved
				if profile['attacker'] == campaign.player_unit or self == campaign.player_unit:
					WaitForContinue()
				
				# apply result if any
				if profile['result'] == 'PENETRATED':
					
					# TODO: roll for penetration result here, use the
					# final 'roll' difference vs. 'final_chance' as modifier
					
					self.DestroyMe()
					
					# display message
					if self == campaign.player_unit:
						text = 'You were'
					else:
						text = self.GetName() + ' was'
					text += ' destroyed by '
					if profile['attacker'] == campaign.player_unit:
						text += 'you.'
					else:
						text += profile['attacker'].GetName() + '.'
					scenario.Message(text)
					
					return
		
		# clear unresolved hits
		self.ap_hits_to_resolve = []
	
	
	# destroy this unit and remove it from the game
	def DestroyMe(self):
		
		# TEMP: catch player destruction
		if self == campaign.player_unit:
			Wait(50)
			sys.exit()
		
		# set flag
		self.alive = False
		
		# remove from hex stack
		map_hex = scenario.hex_dict[(self.hx, self.hy)]
		if self in map_hex.unit_stack:
			map_hex.unit_stack.remove(self)
			
		# remove from scenario unit list
		if self in scenario.units:
			scenario.units.remove(self)
		
		# remove from active target and target list
		if scenario.selected_target == self:
			scenario.selected_target = None
		if self in scenario.target_list:
			scenario.target_list.remove(self)
		
		scenario.UpdateUnitCon()
		scenario.UpdateScenarioDisplay()


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
		# also store pointers to hexes in a dictionary for quick access
		self.map_hexes = []
		self.hex_dict = {}
		for r in range(0, 5):
			for (hx, hy) in GetHexRing(0, 0, r):
				self.map_hexes.append(MapHex(hx,hy))
				self.hex_dict[(hx,hy)] = self.map_hexes[-1]
		
		# dictionary of console cells covered by map hexes
		self.hex_map_index = {}
		
		
		self.units = []						# list of units in play
		
		# turn and phase information
		self.current_turn = 1					# current scenario turn
		self.active_player = 0					# currently active player (0 is human player)
		self.phase = 0						# current phase
		self.advance_phase = False				# flag for input loop to automatically advance to next phase/turn
		
		self.player_pivot = 0					# keeps track of player unit pivoting
		
		self.selected_weapon = None				# player's currently selected weapon
		self.selected_target = None				# player's current selected target
		self.target_list = []					# list of possible player targets
		
		self.selected_position = 0				# index of selected position in player unit
		
		self.message_log = []					# log of scenario messages
	
	
	# add a game message to the log and display it in the message console
	def Message(self, text):
		# add timestamp
		#text = (str(campaign_day.calendar['hour']).zfill(2) + ':' +
		#	str(campaign_day.calendar['minute']).zfill(2) + ' ' + text)
		self.message_log.append(text)
		self.UpdateMsgConsole()
	
	
	# given a combination of an attacker, weapon, and target, see if this would be a
	# valid attack; if not, return a text description of why not
	# if ignore_facing is true, we don't check whether weapon is facing correct direction
	def CheckAttack(self, attacker, weapon, target, ignore_facing=False):
		
		# check that proper crew command has been set
		
		# check that weapon hasn't already fired
		if weapon.fired:
			return 'Weapon has already fired this turn'
		
		# check that current ammo is available and this ammo would affect the target
		
		# check firing group restrictions
		
		# check that target is in range
		if GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy) > weapon.max_range:
			return 'Target beyond maximum weapon range'
		
		# check that target is in covered arc
		
		# check for hull-mounted weapons blocked by HD status
		
		
		
		# attack can proceed
		return ''
	
	
	# generate a profile for a given attack
	# if pivot or turret_rotate are set to True or False, will override actual attacker status
	def CalcAttack(self, attacker, weapon, target, pivot=None, turret_rotate=None):
		
		profile = {}
		profile['attacker'] = attacker
		profile['weapon'] = weapon
		profile['ammo_type'] = weapon.ammo_type
		profile['target'] = target
		profile['result'] = ''		# placeholder for text rescription of result
		
		
		# determine attack type
		weapon_type = weapon.GetStat('type')
		if weapon_type == 'Gun':
			profile['type'] = 'Point Fire'
		elif weapon_type == 'Small Arms' or weapon_type in MG_WEAPONS:
			profile['type'] = 'Area Fire'
			profile['effective_fp'] = 0		# placeholder for effective fp
		else:
			print('ERROR: Weapon type not recognized: ' + weapon.stats['name'])
			return None
		
		# calculate distance to target
		distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
		
		# list of modifiers
		# [maximum displayable modifier description length is 18 characters]
		
		modifier_list = []
		
		# point fire attacks (eg. large guns)
		if profile['type'] == 'Point Fire':
			
			# calculate base success chance
			
			# possible to fire HE at unspotted targets
			if not target.spotted:
				# use infantry chance as base chance
				profile['base_chance'] = PF_BASE_CHANCE[distance][1]
			else:
				if target.GetStat('category') == 'Vehicle':
					profile['base_chance'] = PF_BASE_CHANCE[distance][0]
				else:
					profile['base_chance'] = PF_BASE_CHANCE[distance][1]
		
			# calculate modifiers and build list of descriptions
			
			# description max length is 19 chars
			
			# attacker is moving
			if attacker.moving:
				modifier_list.append(('Attacker Moving', -60.0))
			
			# attacker pivoted
			elif attacker.facing != attacker.previous_facing:
				modifier_list.append(('Attacker Pivoted', -40.0))

			# player attacker pivoted
			elif attacker == campaign.player_unit and self.player_pivot != 0:
				modifier_list.append(('Attacker Pivoted', -40.0))

			# weapon has turret rotated
			elif weapon.GetStat('mount') == 'Turret':
				if attacker.turret_facing != attacker.previous_turret_facing:
					modifier_list.append(('Turret Rotated', -20.0))
			
			# attacker pinned
			if attacker.pinned:
				modifier_list.append(('Attacker Pinned', -60.0))
			
			# unspotted target
			if not target.spotted:
				modifier_list.append(('Unspotted Target', -25.0))
			
			# spotted target
			else:
			
				# acquired target
				if attacker.acquired_target is not None:
					(ac_target, level) = attacker.acquired_target
					if ac_target == target:
						if not level:
							mod = 10.0
						else:
							mod = 20.0
						modifier_list.append(('Acquired Target', mod))
				
				# target vehicle moving
				if target.moving and target.GetStat('category') == 'Vehicle':
					modifier_list.append(('Target Moving', -30.0))
				
				# target size
				size_class = target.GetStat('size_class')
				if size_class is not None:
					if size_class != 'Normal':
						text = size_class + ' Target'
						mod = PF_SIZE_MOD[size_class]
						modifier_list.append((text, mod))
			
			# long / short-barreled gun
			long_range = weapon.GetStat('long_range')
			if long_range is not None:
				if long_range == 'S' and distance > 1:
					modifier_list.append(('Short Gun', -12.0))
				
				elif long_range == 'L' and distance > 1:
					modifier_list.append(('Long Gun', 12.0))
				
				elif long_range == 'LL':
					if distance == 1:
						modifier_list.append(('Long Gun', 12.0))
					elif distance >= 2:
						modifier_list.append(('Long Gun', 24.0))
			
			# smaller-calibre gun at longer range
			if weapon_type == 'Gun':
				calibre_mod = 0
				calibre = int(weapon.stats['calibre'])
				
				if calibre <= 40 and distance >= 2:
					calibre_mod -= 1	
				
				if calibre <= 57:
					if distance == 2:
						calibre_mod -= 1
					elif distance == 3:
						calibre_mod -= 2
				if calibre_mod < 0:
					modifier_list.append(('Small Calibre', (8.0 * calibre_mod)))
		
		# area fire
		elif profile['type'] == 'Area Fire':
			
			# calculate base FP
			fp = int(weapon.GetStat('fp'))
			
			# point blank range multiplier
			if distance == 0:
				fp = fp * 2
			
			profile['base_fp'] = fp
			
			# calculate base effect chance
			if target.GetStat('category') == 'Vehicle':
				base_chance = VEH_FP_BASE_CHANCE
			else:
				base_chance = INF_FP_BASE_CHANCE
			for i in range(2, fp + 1):
				base_chance += FP_CHANCE_STEP * (FP_CHANCE_STEP_MOD ** (i-1)) 
			profile['base_chance'] = round(base_chance, 2)
			
			# store the rounded base chance so we can use it later for modifiers
			base_chance = profile['base_chance']
			
			# calculate modifiers
			
			# attacker moving
			if attacker.moving:
				mod = round(base_chance / 2.0, 2)
				modifier_list.append(('Attacker Moving', 0.0 - mod))
			
			# attacker pivoted
			elif attacker.facing != attacker.previous_facing:
				mod = round(base_chance / 3.0, 2)
				modifier_list.append(('Attacker Pivoted', 0.0 - mod))

			# player attacker pivoted
			elif attacker == campaign.player_unit and self.player_pivot != 0:
				mod = round(base_chance / 3.0, 2)
				modifier_list.append(('Attacker Pivoted', 0.0 - mod))

			# weapon turret rotated
			elif weapon.GetStat('mount') == 'Turret':
				if attacker.turret_facing != attacker.previous_turret_facing:
					mod = round(base_chance / 4.0, 2)
					modifier_list.append(('Turret Rotated', 0.0 - mod))
			
			# attacker pinned
			if attacker.pinned:
				mod = round(base_chance / 2.0, 2)
				modifier_list.append(('Attacker Pinned', 0.0 - mod))
			
			if not target.spotted:
				modifier_list.append(('Unspotted Target', -25.0))
			else:
			
				# target is infantry and moving
				if target.moving and target.GetStat('category') == 'Infantry':
					mod = round(base_chance / 2.0, 2)
					modifier_list.append(('Infantry Moving', mod))
				else:
					if target.GetStat('class') == 'Team':
						modifier_list.append(('Small Team', -20.0))
				
				# target size
				size_class = target.GetStat('size_class')
				if size_class is not None:
					if size_class != 'Normal':
						text = size_class + ' Target'
						mod = PF_SIZE_MOD[size_class]
						modifier_list.append((text, mod))
				
		# FUTURE: Commander directing fire
		
		# save the list of modifiers
		profile['modifier_list'] = modifier_list[:]
		
		# calculate total modifier
		total_modifier = 0.0
		for (desc, mod) in modifier_list:
			total_modifier += mod
		
		# calculate final chance of success
		profile['final_chance'] = RestrictChance(profile['base_chance'] + total_modifier)
		
		# calculate additional outcomes for Area Fire
		if profile['type'] == 'Area Fire':
			profile['full_effect'] = RestrictChance((profile['base_chance'] + 
				total_modifier) * FP_FULL_EFFECT)
			profile['critical_effect'] = RestrictChance((profile['base_chance'] + 
				total_modifier) * FP_CRIT_EFFECT)
		
		return profile
	
	
	# takes an attack profile and generates a profile for an armour penetration attempt
	def CalcAP(self, profile):
		
		profile['type'] = 'ap'
		modifier_list = []
		
		# create local pointers for convenience
		attacker = profile['attacker']
		weapon = profile['weapon']
		target = profile['target']
		
		# get location hit on target
		location = profile['location']
		# hull hit or target does not have rotatable turret
		if location == 'Hull' or target.turret_facing is None:
			turret_facing = False
		else:
			turret_facing = True
		
		facing = GetFacing(attacker, target, turret_facing=turret_facing)
		hit_location = (location + '_' + facing).lower()
		
		# generate a text description of location hit
		if location == 'Turret' and target.turret_facing is None:
			location = 'Upper Hull'
		profile['location_desc'] = location + ' ' + facing
		
		# calculate base chance of penetration
		if weapon.GetStat('name') == 'AT Rifle':
			base_chance = AP_BASE_CHANCE['AT Rifle']
		elif weapon.GetStat('type') in MG_WEAPONS:
			base_chance = AP_BASE_CHANCE['MG']
		else:
			gun_rating = weapon.GetStat('calibre')
			
			# HE hits have a much lower base chance
			if profile['ammo_type'] == 'HE':
				base_chance = weapon.GetBaseHEPenetrationChance()
			else:
				if weapon.GetStat('long_range') is not None:
					gun_rating += weapon.GetStat('long_range')
				if gun_rating not in AP_BASE_CHANCE:
					print('ERROR: No AP base chance found for: ' + gun_rating)
					return None
				base_chance = AP_BASE_CHANCE[gun_rating]
		
		profile['base_chance'] = base_chance
		
		# calculate modifiers
		
		# calibre/range modifier - not applicable to HE and MG attacks
		if profile['ammo_type'] == 'AP' and weapon.GetStat('calibre') is not None:
			calibre = int(weapon.GetStat('calibre'))
			distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
			
			if calibre <= 25:
				if distance == 0:
					modifier_list.append(('Close Range', 18.0))
				elif distance == 2:
					modifier_list.append(('Medium Range', -7.0))
				else:
					modifier_list.append(('Long Range', -18.0))
			elif calibre <= 57:
				if distance == 0:
					modifier_list.append(('Close Range', 7.0))
				elif distance == 2:
					modifier_list.append(('Medium Range', -7.0))
				else:
					modifier_list.append(('Long Range', -12.0))
			else:
				if distance == 0:
					modifier_list.append(('Close Range', 7.0))
				elif 2 <= distance <= 3:
					modifier_list.append(('Long Range', -7.0))
		
		# target armour modifier
		# TODO: move into GetArmourModifier function for target
		#       use in DoAirAttack as well
		armour = target.GetStat('armour')
		if armour is not None:
			
			# location is armoured
			if armour[hit_location] != '-':
				target_armour = int(armour[hit_location])
				if target_armour >= 0:
					modifier = -9.0
					for i in range(target_armour - 1):
						modifier = modifier * 1.8
					
					modifier_list.append(('Target Armour', modifier))
					
					# apply critical hit modifier if any
					if profile['result'] == 'CRITICAL HIT':
						modifier = round(abs(modifier) * 0.8, 2)
						modifier_list.append(('Critical Hit', modifier))
				
		
		# save the list of modifiers
		profile['modifier_list'] = modifier_list[:]
		
		# calculate total modifer
		total_modifier = 0.0
		for (desc, mod) in modifier_list:
			total_modifier += mod
		
		# calculate final chance of success
		profile['final_chance'] = RestrictChance(profile['base_chance'] + total_modifier)
		
		return profile
	
	
	# display an attack or AP profile to the screen and prompt to proceed
	# does not alter the profile
	def DisplayAttack(self, profile):
		
		# don't display if player is not involved
		#if profile['attacker'] != self.player_unit and profile['target'] != self.player_unit:
		#	return
		
		libtcod.console_clear(attack_con)
		
		# display the background outline
		libtcod.console_blit(session.attack_bkg, 0, 0, 0, 0, attack_con, 0, 0)
		
		# window title
		libtcod.console_set_default_background(attack_con, libtcod.darker_blue)
		libtcod.console_rect(attack_con, 1, 1, 25, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(attack_con, libtcod.black)
		
		# set flags on whether attacker/target is spotted
		
		attacker_spotted = True
		if profile['attacker'].owning_player == 1 and not profile['attacker'].spotted:
			attacker_spotted = False
		target_spotted = True
		if profile['target'].owning_player == 1 and not profile['target'].spotted:
			target_spotted = False
		
		if profile['type'] == 'ap':
			text = 'Armour Penetration'
		else:
			text = 'Ranged Attack'
		libtcod.console_print_ex(attack_con, 13, 1, libtcod.BKGND_NONE, libtcod.CENTER, text)
		
		# attacker portrait if any
		if profile['type'] in ['Point Fire', 'Area Fire']:
			
			libtcod.console_set_default_background(attack_con, PORTRAIT_BG_COL)
			libtcod.console_rect(attack_con, 1, 2, 25, 8, False, libtcod.BKGND_SET)
		
			# FUTURE: store portraits for every active unit type in session object
			if attacker_spotted:
				portrait = profile['attacker'].GetStat('portrait')
				if portrait is not None:
					libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, attack_con, 1, 2)
		
		# attack description
		if profile['type'] == 'ap':
			text1 = profile['target'].GetName()
			if attacker_spotted:
				text2 = 'hit by ' + profile['weapon'].GetStat('name')
			else:
				text2 = 'hit'
			if profile['ammo_type'] is not None:
				text2 += ' (' + profile['ammo_type'] + ')'
			text3 = 'in ' + profile['location_desc']
		else:
			text1 = profile['attacker'].GetName()
			if attacker_spotted:
				text2 = 'firing ' + profile['weapon'].GetStat('name')
				if profile['weapon'].ammo_type is not None:
					text2 += ' ' + profile['weapon'].ammo_type
				text2 += ' at'
			else:
				text2 = 'firing at'
			text3 = profile['target'].GetName()
			
		libtcod.console_print_ex(attack_con, 13, 10, libtcod.BKGND_NONE, libtcod.CENTER, text1)
		libtcod.console_print_ex(attack_con, 13, 11, libtcod.BKGND_NONE, libtcod.CENTER, text2)
		libtcod.console_print_ex(attack_con, 13, 12, libtcod.BKGND_NONE, libtcod.CENTER, text3)
		
		# display target portrait if any
		libtcod.console_set_default_background(attack_con, PORTRAIT_BG_COL)
		libtcod.console_rect(attack_con, 1, 13, 25, 8, False, libtcod.BKGND_SET)
		
		# FUTURE: store portraits for every active unit type in session object
		if target_spotted:
			portrait = profile['target'].GetStat('portrait')
			if portrait is not None:
				libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, attack_con, 1, 13)
		
		# base chance
		text = 'Base Chance '
		if profile['type'] == 'ap':
			text += 'to Penetrate'
		elif profile['type'] == 'Area Fire':
			text += 'of Effect'
		else:
			text += 'to Hit'
		libtcod.console_print_ex(attack_con, 13, 23, libtcod.BKGND_NONE, libtcod.CENTER, text)
		text = str(profile['base_chance']) + '%%'
		libtcod.console_print_ex(attack_con, 13, 24, libtcod.BKGND_NONE, libtcod.CENTER, text)
		
		# list of modifiers
		libtcod.console_set_default_background(attack_con, libtcod.darker_blue)
		libtcod.console_rect(attack_con, 1, 27, 25, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(attack_con, libtcod.black)
		libtcod.console_print_ex(attack_con, 13, 27, libtcod.BKGND_NONE, libtcod.CENTER,
			'Modifiers')
		
		y = 29
		if len(profile['modifier_list']) == 0:
			libtcod.console_print_ex(attack_con, 13, y, libtcod.BKGND_NONE, libtcod.CENTER,
				'None')
		else:
			for (desc, mod) in profile['modifier_list']:
				# max displayable length is 17 chars
				libtcod.console_print(attack_con, 2, y, desc[:17])
				
				if mod > 0.0:
					col = libtcod.green
					text = '+'
				else:
					col = libtcod.red
					text = ''
				
				text += str(mod)
				
				libtcod.console_set_default_foreground(attack_con, col)
				libtcod.console_print_ex(attack_con, 24, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, text)
				libtcod.console_set_default_foreground(attack_con, libtcod.white)
				
				y += 1
		
		# display final chance
		libtcod.console_set_default_background(attack_con, libtcod.darker_blue)
		libtcod.console_rect(attack_con, 1, 43, 25, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(attack_con, libtcod.black)
		libtcod.console_print_ex(attack_con, 14, 43, libtcod.BKGND_NONE, libtcod.CENTER,
			'Final Chance')
		
		# display chance graph
		if profile['type'] == 'Area Fire':
			# area fire has partial, full, and critical outcomes possible
			
			# no effect
			libtcod.console_set_default_background(attack_con, libtcod.red)
			libtcod.console_rect(attack_con, 1, 46, 25, 3, False, libtcod.BKGND_SET)
			
			# partial effect
			libtcod.console_set_default_background(attack_con, libtcod.darker_green)
			x = int(ceil(25.0 * profile['final_chance'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			if profile['final_chance'] > profile['full_effect']:
				libtcod.console_print_ex(attack_con, 24, 46, libtcod.BKGND_NONE,
					libtcod.RIGHT, 'PART')
				text = str(profile['final_chance']) + '%%'
				libtcod.console_print_ex(attack_con, 24, 47, libtcod.BKGND_NONE,
					libtcod.RIGHT, text)
			
			# full effect
			libtcod.console_set_default_background(attack_con, libtcod.green)
			x = int(ceil(25.0 * profile['full_effect'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			if profile['full_effect'] > profile['critical_effect']:
				libtcod.console_print_ex(attack_con, 13, 46, libtcod.BKGND_NONE,
					libtcod.CENTER, 'FULL')
				text = str(profile['full_effect']) + '%%'
				libtcod.console_print_ex(attack_con, 13, 47, libtcod.BKGND_NONE,
					libtcod.CENTER, text)
			
			# critical effect
			libtcod.console_set_default_background(attack_con, libtcod.blue)
			x = int(ceil(25.0 * profile['critical_effect'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			libtcod.console_print(attack_con, 2, 46, 'CRIT')
			text = str(profile['critical_effect']) + '%%'
			libtcod.console_print(attack_con, 2, 47, text)
			
		else:
			
			# miss
			libtcod.console_set_default_background(attack_con, libtcod.red)
			libtcod.console_rect(attack_con, 1, 46, 25, 3, False, libtcod.BKGND_SET)
			
			# hit
			x = int(ceil(25.0 * profile['final_chance'] / 100.0))
			libtcod.console_set_default_background(attack_con, libtcod.green)
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			# critical hit band
			libtcod.console_set_default_foreground(attack_con, libtcod.blue)
			for y in range(46, 49):
				libtcod.console_put_char(attack_con, 1, y, 221)
			
			# critical miss band
			libtcod.console_set_default_foreground(attack_con, libtcod.dark_grey)
			for y in range(46, 49):
				libtcod.console_put_char(attack_con, 25, y, 222)
		
			libtcod.console_set_default_foreground(attack_con, libtcod.white)
			libtcod.console_set_default_background(attack_con, libtcod.black)
		
			text = str(profile['final_chance']) + '%%'
			libtcod.console_print_ex(attack_con, 13, 47, libtcod.BKGND_NONE,
				libtcod.CENTER, text)
		
		# display prompts
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		libtcod.console_print(attack_con, 6, 56, 'Bksp')
		libtcod.console_print(attack_con, 6, 57, 'Tab')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		libtcod.console_print(attack_con, 12, 56, 'Cancel')
		libtcod.console_print(attack_con, 12, 57, 'Continue')
		
		# blit the finished console to the screen
		libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
	
	
	# do a roll, animate the attack console, and display the results
	# returns an modified attack profile
	def DoAttackRoll(self, profile):
		
		# clear prompts from attack console
		libtcod.console_print(attack_con, 6, 56, '                  ')
		libtcod.console_print(attack_con, 6, 57, '                  ')
		
		# don't animate percentage rolls if player is not involved
		if profile['attacker'] != campaign.player_unit and profile['target'] != campaign.player_unit:
			roll = GetPercentileRoll()
		else:
			for i in range(6):
				roll = GetPercentileRoll()
				
				# clear any previous text
				libtcod.console_print_ex(attack_con, 13, 49, libtcod.BKGND_NONE,
					libtcod.CENTER, '      ')
				
				text = str(roll) + '%%'
				libtcod.console_print_ex(attack_con, 13, 49, libtcod.BKGND_NONE,
					libtcod.CENTER, text)
				libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
				libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
				libtcod.console_flush()
				Wait(15)
		
		# record the final roll in the attack profile
		profile['roll'] = roll
			
		# determine location hit on target (not always used)
		location_roll = GetPercentileRoll()
		if location_roll <= 75.0:
			profile['location'] = 'Hull'
		else:
			profile['location'] = 'Turret'
		
		# armour penetration roll
		if profile['type'] == 'ap':
			
			if roll >= CRITICAL_MISS:
				result_text = 'NO PENETRATION'
			elif roll <= CRITICAL_HIT:
				result_text = 'PENETRATED'
			elif roll <= profile['final_chance']:
				result_text = 'PENETRATED'
			else:
				result_text = 'NO PENETRATION'
		
		# area fire attack
		elif profile['type'] == 'Area Fire':
			
			if roll <= profile['critical_effect']:
				result_text = 'CRITICAL EFFECT'
				profile['effective_fp'] = profile['base_fp'] * 2
			elif roll <= profile['full_effect']:
				result_text = 'FULL EFFECT'
				profile['effective_fp'] = profile['base_fp']
			elif roll <= profile['final_chance']:
				result_text = 'PARTIAL EFFECT'
				profile['effective_fp'] = int(floor(profile['base_fp'] / 2))
			else:
				result_text = 'NO EFFECT'
			
			# might be converted into an AP MG hit
			if result_text in ['FULL EFFECT', 'CRITICAL EFFECT']:
				if profile['weapon'].GetStat('type') in MG_WEAPONS and profile['target'].GetStat('armour') is not None:
					distance = GetHexDistance(profile['attacker'].hx,
						profile['attacker'].hy, profile['target'].hx,
						profile['target'].hy)
					if distance <= MG_AP_RANGE:
						if result_text == 'FULL EFFECT':
							result_text = 'HIT'
						else:
							result_text = 'CRITICAL HIT'

		# point fire attack
		else:
			
			if roll >= CRITICAL_MISS:
				result_text = 'MISS'
			elif roll <= CRITICAL_HIT:
				result_text = 'CRITICAL HIT'
			elif roll <= profile['final_chance']:
				result_text = 'HIT'
			else:
				result_text = 'MISS'
		
		# if point fire hit or AP MG hit, may be saved by HD status
		if result_text in ['HIT', 'CRITICAL HIT'] and len(profile['target'].hull_down) > 0:
			
			if profile['location'] == 'Hull':
				direction = GetDirectionToward(profile['target'].hx,
					profile['target'].hy, profile['attacker'].hx,
					profile['attacker'].hy)
				if direction in profile['target'].hull_down:
					result_text = 'MISS - HULL DOWN'
		
		profile['result'] = result_text
		
		# if player is not involved, we can return here
		if profile['attacker'] != campaign.player_unit and profile['target'] != campaign.player_unit:
			return profile
		
		libtcod.console_print_ex(attack_con, 13, 51, libtcod.BKGND_NONE,
			libtcod.CENTER, result_text)
		
		# display effective FP if it was successful area fire attack
		if profile['type'] == 'Area Fire' and result_text != 'NO EFFECT':
			libtcod.console_print_ex(attack_con, 13, 52, libtcod.BKGND_NONE,
				libtcod.CENTER, str(profile['effective_fp']) + ' FP')
		
		# FUTURE: check for RoF for gun / MG attacks
		#if profile['type'] != 'ap' and profile['weapon'].GetStat('rof') is not None:
			# TEMP: player only for now
		#	if profile['attacker'] == scenario.player_unit:
		#		profile['weapon'].maintained_rof = CheckRoF(profile) 
		#		if profile['weapon'].maintained_rof:
		#			libtcod.console_print_ex(attack_con, 13, 53, libtcod.BKGND_NONE,
		#				libtcod.CENTER, 'Maintained Rate of Fire')
		#			libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		#			libtcod.console_print(attack_con, 6, 56, 'F')
		#			libtcod.console_set_default_foreground(attack_con, libtcod.white)
		#			libtcod.console_print(attack_con, 12, 56, 'Fire Again')
		
		# display prompt
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		libtcod.console_print(attack_con, 6, 57, 'Tab')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		libtcod.console_print(attack_con, 12, 57, 'Continue')
		
		# blit the finished console to the screen
		libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		
		return profile
	
	
	# selecte a different weapon on the player unit
	def SelectWeapon(self, forward):
		
		if self.selected_weapon is None:
			self.selected_weapon = campaign.player_unit.weapon_list[0]
			return
		
		if forward:
			m = 1
		else:
			m = -1
		
		i = campaign.player_unit.weapon_list.index(self.selected_weapon)
		i += m
		
		if i < 0:
			self.selected_weapon = campaign.player_unit.weapon_list[-1]
		elif i > len(campaign.player_unit.weapon_list) - 1:
			self.selected_weapon = campaign.player_unit.weapon_list[0]
		else:
			self.selected_weapon = campaign.player_unit.weapon_list[i]
	
	
	# (re)build a sorted list of possible player targets
	def BuildTargetList(self):
		
		self.target_list = []
		
		for unit in self.units:
			# allied unit
			if unit.owning_player == 0: continue
			# beyond active part of map
			if GetHexDistance(0, 0, unit.hx, unit.hy) > 3: continue
			self.target_list.append(unit)
		
		# old target no longer on list
		if self.selected_target not in self.target_list:
			self.selected_target = None
	
	
	# cycle selected player target
	def CycleTarget(self, forward):
		
		# no targets to select from
		if len(self.target_list) == 0: return
		
		# no target selected yet
		if self.selected_target is None:
			self.selected_target = self.target_list[0]
			return
		
		if forward:
			m = 1
		else:
			m = -1
		
		i = self.target_list.index(self.selected_target)
		i += m
		
		if i < 0:
			self.selected_target = self.target_list[-1]
		elif i > len(self.target_list) - 1:
			self.selected_target = self.target_list[0]
		else:
			self.selected_target = self.target_list[i]
	
	
	# execute a player move forward/backward, repositioning units on the hex map as needed
	def MovePlayer(self, forward):
		
		# FUTURE: do sound effect
		
		# do move success roll
		if forward:
			chance = campaign.player_unit.forward_move_chance
		else:
			chance = campaign.player_unit.reverse_move_chance
		roll = GetPercentileRoll()
		
		# move was not successful
		if roll > chance:
			
			# clear any alternative bonus and apply bonus for future moves
			if forward:
				campaign.player_unit.reverse_move_bonus = 0.0
				campaign.player_unit.forward_move_bonus += BASE_MOVE_BONUS
			else:
				campaign.player_unit.forward_move_bonus = 0.0
				campaign.player_unit.reverse_move_bonus += BASE_MOVE_BONUS
			
			campaign.player_unit.moving = True
			
			# show message to player
			text = 'You move but not far enough to enter a new map hex'
			scenario.Message(text)
			
			# end movement phase
			self.advance_phase = True
			
			return
			
		# show message to player
		text = 'You move far enough to enter a new map hex'
		scenario.Message(text)
		
		# move was successful, clear all bonuses
		campaign.player_unit.forward_move_bonus = 0.0
		campaign.player_unit.reverse_move_bonus = 0.0
		
		campaign.player_unit.moving = True
		campaign.player_unit.ClearAcquiredTargets()
		
		# calculate new hex positions for each unit in play
		if forward:
			direction = 3
		else:
			direction = 0
		
		# run through list in reverse so we can remove units that move off board
		for unit in reversed(self.units):
			
			if unit == campaign.player_unit: continue
			
			(new_hx, new_hy) = GetAdjacentHex(unit.hx, unit.hy, direction)
			
			# special case: remove any units that would move off map
			if GetHexDistance(0, 0, new_hx, new_hy) > 4:
				unit.RemoveFromPlay()
				continue
				
			# special case: jump over player hex 0,0
			if new_hx == 0 and new_hy == 0:
				(new_hx, new_hy) = GetAdjacentHex(0, 0, direction)
			
			# set destination hex
			unit.dest_hex = (new_hx, new_hy)
		
		# TODO: animate movement
		
		# set new hex location for each unit and move into new hex stack
		for unit in self.units:
			if unit == campaign.player_unit: continue
			scenario.hex_dict[(unit.hx, unit.hy)].unit_stack.remove(unit)
			(unit.hx, unit.hy) = unit.dest_hex
			scenario.hex_dict[(unit.hx, unit.hy)].unit_stack.append(unit)
			# clear destination hex
			unit.dest_hex = None
		
		self.UpdateUnitCon()
		
		# end movement phase
		self.advance_phase = True
	
	
	# pivot the hull of the player unit
	def PivotPlayer(self, clockwise):
		
		if clockwise:
			r = 5
			f = -1
		else:
			r = 1
			f = 1
		
		# calculate new hex positions of units
		for unit in self.units:
			if unit == campaign.player_unit: continue
			
			(new_hx, new_hy) = RotateHex(unit.hx, unit.hy, r)
			# set destination hex
			unit.dest_hex = (new_hx, new_hy)
		
		# TODO: animate movement
		
		# set new hex location for each unit and move into new hex stack
		for unit in self.units:
			if unit == campaign.player_unit: continue
			scenario.hex_dict[(unit.hx, unit.hy)].unit_stack.remove(unit)
			(unit.hx, unit.hy) = unit.dest_hex
			scenario.hex_dict[(unit.hx, unit.hy)].unit_stack.append(unit)
			# clear destination hex
			unit.dest_hex = None
			
			# pivot unit facings if any
			if unit.facing is not None:
				unit.facing = ConstrainDir(unit.facing + f)
			if unit.turret_facing is not None:
				unit.turret_facing = ConstrainDir(unit.turret_facing + f)
		
		self.UpdateUnitCon()
		
		# record player pivot
		self.player_pivot = ConstrainDir(self.player_pivot + f)
	
	
	# rotate turret of player unit
	def RotatePlayerTurret(self, clockwise):
		
		if campaign.player_unit.turret_facing is None: return
		
		if clockwise:
			f = 1
		else:
			f = -1
		campaign.player_unit.turret_facing = ConstrainDir(campaign.player_unit.turret_facing + f)
		self.UpdateUnitCon()
		
	
	# advance to next phase/turn and do automatic events
	def AdvanceToNextPhase(self):
		
		# do end of phase actions for player
		
		# end of movement phase
		if self.phase == 2:
			
			# player pivoted during movement phase
			if self.player_pivot != 0:
				campaign.player_unit.acquired_target = None
		
		# end of shooting phase
		elif self.phase == 3:
			
			# clear GUI console and refresh screen
			libtcod.console_clear(gui_con)
			self.UpdateScenarioDisplay()
			libtcod.console_flush()
			
			# resolve hits on enemy units
			for unit in self.units:
				if not unit.alive: continue
				if unit.owning_player == self.active_player: continue
				unit.ResolveHits()
				
		# enemy activation finished, player's turn
		if self.active_player == 1:
			
			# advance clock
			campaign_day.AdvanceClock(0, TURN_LENGTH)
			
			self.active_player = 0
			self.phase = 0
			campaign.player_unit.ResetForNewTurn()
			campaign.player_unit.MoveToTopOfStack()
			self.UpdateUnitCon()
		
		# remaining on player turn
		elif self.phase < 5:
			self.phase += 1
		
		# switching to enemy turn
		else:
			self.phase = 6
			self.active_player = 1
		
		# do automatic actions at start of phase
		
		# command phase: rebuild lists of commands
		if self.phase == 0:
			campaign.player_unit.BuildCmdLists()
		
		# spotting phase: do spotting then automatically advance
		elif self.phase == 1:
			campaign.player_unit.DoSpotChecks()
			self.advance_phase = True
		
		# movement phase: 
		elif self.phase == 2:
			
			self.player_pivot = 0
			
			# skip phase if driver not on move command
			crewman = campaign.player_unit.GetPersonnelByPosition('Driver')
			
			# no driver in position
			if crewman is None:
				self.advance_phase = True
			else:
				# driver not on Drive command
				if crewman.current_cmd != 'Drive':
					self.advance_phase = True
			
			# if we're doing the phase, calculate move chances for player unit
			if not self.advance_phase:
				campaign.player_unit.CalculateMoveChances()
		
		# shooting phase
		elif self.phase == 3:
			self.BuildTargetList()
			self.UpdateGuiCon()
		
		# assault phase
		elif self.phase == 4:
			
			# TEMP - advance automatically past this phase
			self.advance_phase = True
		
		# recovery phase
		elif self.phase == 5:
			
			# TEMP - advance automatically past this phase
			self.advance_phase = True
		
		# enemy activation
		elif self.active_player == 1:
			
			# run through list in reverse since we might remove units from play
			for unit in reversed(self.units):
				if unit.owning_player == 0: continue
				unit.ai.DoActivation()
			
			self.advance_phase = True
		
		self.UpdateCrewInfoCon()
		self.UpdateCmdCon()
		self.UpdateContextCon()
		self.UpdateGuiCon()
		self.UpdateTimeCon()
		self.UpdateScenarioDisplay()
		libtcod.console_flush()
		
		# pause here if we are advancing to next phase automatically
		#if self.advance_phase:
		#	Wait(50)
	
	
	# update contextual info console
	# 18x12
	def UpdateContextCon(self):
		libtcod.console_clear(context_con)
		
		# if we're advancing to next phase automatically, don't display anything here
		if self.advance_phase: return
		
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
			
			libtcod.console_set_default_foreground(context_con, libtcod.white)
			libtcod.console_print(context_con, 6, 0, 'Success')
			#libtcod.console_print(context_con, 14, 0, 'Bog')
			
			libtcod.console_print(context_con, 0, 2, 'Fwd')
			libtcod.console_print(context_con, 0, 4, 'Rev')
			libtcod.console_print(context_con, 0, 6, 'Pivot')
			#libtcod.console_print(context_con, 0, 8, 'Repo')
			#libtcod.console_print(context_con, 0, 10, 'HD')
			
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			
			# TEMP - will have to poll chances from player unit
			
			# forward move
			text = str(campaign.player_unit.forward_move_chance) + '%%'
			libtcod.console_print_ex(context_con, 11, 2, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			#libtcod.console_print_ex(context_con, 16, 2, libtcod.BKGND_NONE,
			#	libtcod.RIGHT, '10%%')
			
			# reverse move
			text = str(campaign.player_unit.reverse_move_chance) + '%%'
			libtcod.console_print_ex(context_con, 11, 4, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			#libtcod.console_print_ex(context_con, 16, 4, libtcod.BKGND_NONE,
			#	libtcod.RIGHT, '20%%')
			
			# pivot
			libtcod.console_print_ex(context_con, 11, 6, libtcod.BKGND_NONE,
				libtcod.RIGHT, '100%%')
			#libtcod.console_print_ex(context_con, 16, 6, libtcod.BKGND_NONE,
			#	libtcod.RIGHT, '1.5%%')
			
			# reposition
			#libtcod.console_print_ex(context_con, 10, 8, libtcod.BKGND_NONE,
			#	libtcod.RIGHT, '75%%')
			#libtcod.console_print_ex(context_con, 16, 8, libtcod.BKGND_NONE,
			#	libtcod.RIGHT, '4%%')
			
			# hull down
			#libtcod.console_print_ex(context_con, 10, 10, libtcod.BKGND_NONE,
			#	libtcod.RIGHT, '70%%')
			#libtcod.console_print_ex(context_con, 16, 10, libtcod.BKGND_NONE,
			#	libtcod.RIGHT, '2%%')
		
		# Shooting Phase
		elif self.phase == 3:
			
			weapon = self.selected_weapon
			if weapon is None:
				return
			
			libtcod.console_set_default_foreground(context_con, libtcod.white)
			libtcod.console_set_default_background(context_con, libtcod.darkest_red)
			libtcod.console_rect(context_con, 0, 0, 18, 1, True, libtcod.BKGND_SET)
			libtcod.console_print(context_con, 0, 0, weapon.stats['name'])
			libtcod.console_set_default_background(context_con, libtcod.darkest_grey)
			
			if weapon.GetStat('mount') is not None:
				libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
				libtcod.console_print_ex(context_con, 17, 0, libtcod.BKGND_NONE,
					libtcod.RIGHT, weapon.stats['mount'])
			
			# if weapon is a gun, display ammo info
			if weapon.GetStat('type') == 'Gun':
				
				# general stores
				y = 3
				for ammo_type in AMMO_TYPES:
					if ammo_type in weapon.ammo_stores:
						
						# highlight if this ammo type currently active
						if weapon.ammo_type is not None:
							if weapon.ammo_type == ammo_type:
								libtcod.console_set_default_background(context_con, libtcod.darker_blue)
								libtcod.console_rect(context_con, 0, y, 18, 1, True, libtcod.BKGND_SET)
								libtcod.console_set_default_background(context_con, libtcod.darkest_grey)
						
						libtcod.console_set_default_foreground(context_con, libtcod.white)
						libtcod.console_print(context_con, 0, y, ammo_type)
						libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
						libtcod.console_print_ex(context_con, 7, y, libtcod.BKGND_NONE,
							libtcod.RIGHT, str(weapon.ammo_stores[ammo_type]))
						y += 1
				y += 1
				libtcod.console_print(context_con, 0, y, 'Max')
				libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
				libtcod.console_print_ex(context_con, 7, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, weapon.stats['max_ammo'])
				
				# TODO: highlight currenly selected ammo type
				#if weapon.ammo_type is not None:
			
			if weapon.fired:
				libtcod.console_set_default_foreground(context_con, libtcod.red)
				libtcod.console_print(context_con, 0, 11, 'Fired')
			
	
	# update time and phase console
	def UpdateTimeCon(self):
		libtcod.console_clear(time_con)
		
		text = (MONTH_NAMES[campaign_day.calendar['month']] + ' ' + str(campaign_day.calendar['day']) +
			', ' + str(campaign_day.calendar['year']))
		libtcod.console_print_ex(time_con, 10, 0, libtcod.BKGND_NONE, libtcod.CENTER, text)
		
		text = str(campaign_day.calendar['hour']).zfill(2) + ':' + str(campaign_day.calendar['minute']).zfill(2)
		libtcod.console_print_ex(time_con, 10, 1, libtcod.BKGND_NONE, libtcod.CENTER, text)
		
		# current scenario phase
		libtcod.console_set_default_foreground(time_con, SCEN_PHASE_COL[self.phase])
		libtcod.console_print_ex(time_con, 10, 3, libtcod.BKGND_NONE, libtcod.CENTER, 
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
		# advancing to next phase automatically
		if self.advance_phase: return
		
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
			libtcod.console_print(cmd_menu_con, 1, 3, 'H')
			
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 1, 'Select Crew')
			libtcod.console_print(cmd_menu_con, 8, 2, 'Select Command')
			libtcod.console_print(cmd_menu_con, 8, 3, 'Open/Shut Hatch')
		
		# Movement phase
		elif self.phase == 2:
			libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
			libtcod.console_print(cmd_menu_con, 1, 1, 'W/S')
			libtcod.console_print(cmd_menu_con, 1, 2, 'A/D')
			#libtcod.console_print(cmd_menu_con, 1, 3, 'R')
			#libtcod.console_print(cmd_menu_con, 1, 4, 'H')
			
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 1, 'Forward/Reverse')
			libtcod.console_print(cmd_menu_con, 8, 2, 'Pivot Hull')
			#libtcod.console_print(cmd_menu_con, 8, 3, 'Reposition')
			#libtcod.console_print(cmd_menu_con, 8, 4, 'Attempt HD')
		
		# Shooting phase
		elif self.phase == 3:
			libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
			libtcod.console_print(cmd_menu_con, 1, 1, 'W/S')
			libtcod.console_print(cmd_menu_con, 1, 2, 'A/D')
			libtcod.console_print(cmd_menu_con, 1, 3, 'Q/E')
			libtcod.console_print(cmd_menu_con, 1, 4, 'C')
			libtcod.console_print(cmd_menu_con, 1, 5, 'F')
			
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 1, 'Select Weapon')
			libtcod.console_print(cmd_menu_con, 8, 2, 'Select Target')
			libtcod.console_print(cmd_menu_con, 8, 3, 'Rotate Turret')
			libtcod.console_print(cmd_menu_con, 8, 4, 'Cycle Ammo Type')
			libtcod.console_print(cmd_menu_con, 8, 5, 'Fire at Target')

	
	# plot the center of a given in-game hex on the scenario hex map console
	# 0,0 appears in centre of console
	def PlotHex(self, hx, hy):
		x = (hx*7) + 26
		y = (hy*6) + (hx*3) + 21
		return (x,y)
	
	
	# update hexmap console
	def UpdateHexmapCon(self):
		
		libtcod.console_clear(hexmap_con)
		
		# clear dictionary of console cells covered by hexes
		self.hex_map_index = {}
		
		# FUTURE: can use different hex console images for different battlefield types / weather
		scen_hex = LoadXP('scen_hex.xp')
		libtcod.console_set_key_color(scen_hex, KEY_COLOR)
		
		# draw hexes to hex map console
		for map_hex in self.map_hexes:
			if GetHexDistance(0, 0, map_hex.hx, map_hex.hy) > 3: break
			(x,y) = self.PlotHex(map_hex.hx, map_hex.hy)
			libtcod.console_blit(scen_hex, 0, 0, 0, 0, hexmap_con, x-5, y-3)
			
			# record console positions to dictionary
			for x1 in range(x-2, x+3):
				self.hex_map_index[(x1, y-2)] = map_hex
				self.hex_map_index[(x1, y+2)] = map_hex
			for x1 in range(x-3, x+4):
				self.hex_map_index[(x1, y-1)] = map_hex
				self.hex_map_index[(x1, y+1)] = map_hex
			for x1 in range(x-4, x+5):
				self.hex_map_index[(x1, y)] = map_hex
			
		del scen_hex
	
	
	# update unit layer console
	def UpdateUnitCon(self):
		
		libtcod.console_clear(unit_con)
		for map_hex in self.map_hexes:
			
			# too far away
			if GetHexDistance(0, 0, map_hex.hx, map_hex.hy) > 3: continue
			
			# no units in hex
			if len(map_hex.unit_stack) == 0: continue
			
			# draw top unit in stack
			map_hex.unit_stack[0].DrawMe()
			
			# FUTURE: draw unit's terrain as well
			
			# draw stack number indicator if any
			if len(map_hex.unit_stack) == 1: continue
			if map_hex.unit_stack[0].turret_facing is not None:
				facing = map_hex.unit_stack[0].turret_facing
			else:
				facing = 3
			if facing in [5,0,1]:
				y_mod = 1
			else:
				y_mod = -1
			(x,y) = scenario.PlotHex(map_hex.unit_stack[0].hx, map_hex.unit_stack[0].hy)
			text = str(len(map_hex.unit_stack))
			libtcod.console_set_default_foreground(unit_con, libtcod.grey)
			libtcod.console_set_default_background(unit_con, libtcod.black)
			libtcod.console_print_ex(unit_con, x, y+y_mod, libtcod.BKGND_SET, libtcod.CENTER,
				text)
		
	
	# update GUI console
	def UpdateGuiCon(self):
		
		libtcod.console_clear(gui_con)
		
		# display field of view if in command phase
		if self.phase == 0:
			
			position = campaign.player_unit.positions_list[scenario.selected_position]
			for (hx, hy) in position.visible_hexes:
				(x,y) = scenario.PlotHex(hx, hy)
				libtcod.console_blit(session.scen_hex_fov, 0, 0, 0, 0, gui_con,
					x-5, y-3)
		
		
		# display LoS if in shooting phase
		elif self.phase == 3 and self.selected_target is not None:
			(x1,y1) = self.PlotHex(0,0)
			(x2,y2) = self.PlotHex(self.selected_target.hx, self.selected_target.hy)
			
			libtcod.console_put_char_ex(gui_con, x2-1, y2-1, 218, libtcod.red, libtcod.black)
			libtcod.console_put_char_ex(gui_con, x2+1, y2-1, 191, libtcod.red, libtcod.black)
			libtcod.console_put_char_ex(gui_con, x2-1, y2+1, 192, libtcod.red, libtcod.black)
			libtcod.console_put_char_ex(gui_con, x2+1, y2+1, 217, libtcod.red, libtcod.black)
			
			# TEMP - no LoS
			return
			
			line = GetLine(x1, y1, x2, y2)
			for (x, y) in line[2:-1]:
				libtcod.console_put_char_ex(gui_con, x, y, 250,
					libtcod.red, libtcod.black)
		
	
	# update game message console, which displays most recent game message
	# 61x3
	def UpdateMsgConsole(self):
		libtcod.console_clear(msg_con)
		
		# no message to display
		if len(self.message_log) == 0: return
		
		lines = wrap(self.message_log[-1], 61)
		y = 0
		for line in lines[0:2]:
			libtcod.console_print(msg_con, 0, y, line)
			y += 1
	
	
	# update the unit info console, which displays basic information about a unit under
	# the mouse cursor
	# 18x8
	def UpdateUnitInfoCon(self):
		libtcod.console_clear(unit_info_con)
		
		# mouse cursor outside of map area
		if mouse.cx < 32: return
		
		# check that cursor is on a map hex
		x = mouse.cx - 32
		y = mouse.cy - 9
		if (x,y) not in self.hex_map_index: return
		
		map_hex = self.hex_map_index[(x,y)]
	
		# no units in hex
		if len(map_hex.unit_stack) == 0: return
		
		# display unit info
		unit = map_hex.unit_stack[0]
		
		if unit.owning_player == 1 and not unit.spotted:
			libtcod.console_set_default_foreground(unit_info_con, UNKNOWN_UNIT_COL)
			libtcod.console_print(unit_info_con, 0, 0, 'Possible Enemy')
		else:
			if unit == campaign.player_unit:
				col = libtcod.light_blue
			elif unit.owning_player == 0:
				col = ALLIED_UNIT_COL
			else:
				col = ENEMY_UNIT_COL
	
			libtcod.console_set_default_foreground(unit_info_con, col)
			libtcod.console_print(unit_info_con, 0, 0, unit.unit_id)
			
			libtcod.console_set_default_foreground(unit_info_con, libtcod.light_grey)
			libtcod.console_print(unit_info_con, 0, 1,
				session.nations[unit.nation]['adjective'])
			libtcod.console_print(unit_info_con, 0, 2, unit.GetStat('class'))
			
			# moving/fired status
			if unit.moving:
				libtcod.console_print(unit_info_con, 0, 3, 'Moving')
			if unit.fired:
				libtcod.console_print(unit_info_con, 7, 3, 'Fired')
			
			# acquired target
			libtcod.console_set_default_foreground(unit_info_con, libtcod.white)
			if campaign.player_unit.acquired_target is not None:
				(target, level) = campaign.player_unit.acquired_target
				if target == unit:
					text = 'AC'
					if level:
						text += '2'
					libtcod.console_print(unit_info_con, 0, 4, text)
			
			libtcod.console_set_default_foreground(unit_info_con, ENEMY_UNIT_COL)
			if unit.acquired_target is not None:
				(target, level) = unit.acquired_target
				if target == campaign.player_unit:
					text = 'AC'
					if level:
						text += '2'
					libtcod.console_print(unit_info_con, 4, 4, text)
			
			# facing if any
			if unit.facing is not None and unit.GetStat('category') != 'Infantry':
				libtcod.console_put_char_ex(unit_info_con, 0, 6, 'H',
					libtcod.light_grey, libtcod.darkest_grey)
				libtcod.console_put_char_ex(unit_info_con, 1, 6,
					GetDirectionalArrow(unit.facing), libtcod.light_grey,
					libtcod.darkest_grey)
			
			# HD status if any
			if len(unit.hull_down) > 0:
				libtcod.console_set_default_foreground(unit_info_con, libtcod.sepia)
				libtcod.console_print(unit_info_con, 3, 6, 'HD')
				libtcod.console_put_char_ex(unit_info_con, 5, 6,
					GetDirectionalArrow(unit.hull_down[0]), libtcod.sepia,
					libtcod.darkest_grey)
			
			# FUTURE: cover if any
			libtcod.console_set_default_foreground(unit_info_con, libtcod.dark_green)
			libtcod.console_print(unit_info_con, 0, 7, 'Open Ground')
		
		
	
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
		libtcod.console_blit(gui_con, 0, 0, 0, 0, con, 32, 9, 1.0, 0.0)
		
		# consoles around the edge of map
		libtcod.console_blit(context_con, 0, 0, 0, 0, con, 28, 1)
		libtcod.console_blit(time_con, 0, 0, 0, 0, con, 48, 1)
		libtcod.console_blit(scen_info_con, 0, 0, 0, 0, con, 71, 1)
		libtcod.console_blit(unit_info_con, 0, 0, 0, 0, con, 28, 48)
		
		libtcod.console_blit(msg_con, 0, 0, 0, 0, con, 28, 57)
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
	
	
	# main input loop for scenarios
	def DoScenarioLoop(self):
		
		# set up and load scenario consoles
		global bkg_console, crew_con, cmd_menu_con, scen_info_con
		global player_info_con, context_con, time_con, hexmap_con, unit_con, gui_con
		global msg_con, attack_con, unit_info_con
		
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
		
		# unit info console
		unit_info_con = libtcod.console_new(18, 8)
		libtcod.console_set_default_background(unit_info_con, libtcod.darkest_grey)
		libtcod.console_set_default_foreground(unit_info_con, libtcod.white)
		libtcod.console_clear(unit_info_con)
		
		# hex map console
		hexmap_con = libtcod.console_new(53, 43)
		libtcod.console_set_default_background(hexmap_con, libtcod.black)
		libtcod.console_set_default_foreground(hexmap_con, libtcod.black)
		libtcod.console_clear(hexmap_con)
		
		# unit layer console
		unit_con = libtcod.console_new(53, 43)
		libtcod.console_set_default_background(unit_con, KEY_COLOR)
		libtcod.console_set_default_foreground(unit_con, libtcod.white)
		libtcod.console_set_key_color(unit_con, KEY_COLOR)
		libtcod.console_clear(unit_con)
		
		# gui console - used for displaying target recticles, line of sight, etc.
		gui_con = libtcod.console_new(53, 43)
		libtcod.console_set_default_background(gui_con, KEY_COLOR)
		libtcod.console_set_default_foreground(gui_con, libtcod.white)
		libtcod.console_set_key_color(gui_con, KEY_COLOR)
		libtcod.console_clear(gui_con)
		
		# game message console
		msg_con = libtcod.console_new(61, 2)
		libtcod.console_set_default_background(msg_con, libtcod.black)
		libtcod.console_set_default_foreground(msg_con, libtcod.white)
		libtcod.console_clear(msg_con)
		
		# attack display console
		attack_con = libtcod.console_new(27, 60)
		libtcod.console_set_default_background(attack_con, libtcod.black)
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		libtcod.console_clear(attack_con)
		
		
		# set up player unit
		campaign.player_unit.facing = 0
		campaign.player_unit.turret_facing = 0
		campaign.player_unit.squad = []
		campaign.player_unit.SpawnAt(0,0)
		
		# set up player squad
		for i in range(4):
			unit = Unit(campaign.player_unit.unit_id)
			unit.nation = campaign.player_unit.nation
			unit.GenerateNewPersonnel()
			unit.facing = 0
			unit.turret_facing = 0
			unit.SpawnAt(0,0)
			campaign.player_unit.squad.append(unit)
		
		# generate enemy units
		unit = Unit('7TP')
		unit.owning_player = 1
		unit.nation = 'Poland'
		unit.ai = AI(unit)
		unit.GenerateNewPersonnel()
		unit.facing = 3
		unit.turret_facing = 3
		unit.SpawnAt(0, -3)
		campaign.enemy_units.append(unit)
		
		unit = Unit('37mm wz. 36')
		unit.owning_player = 1
		unit.nation = 'Poland'
		unit.ai = AI(unit)
		unit.GenerateNewPersonnel()
		unit.facing = 3
		unit.deployed = True
		unit.SpawnAt(1, -2)
		campaign.enemy_units.append(unit)
		
		unit = Unit('Riflemen')
		unit.owning_player = 1
		unit.nation = 'Poland'
		unit.ai = AI(unit)
		unit.GenerateNewPersonnel()
		unit.SpawnAt(2, 1)
		campaign.enemy_units.append(unit)
		
		# set up player unit for first activation
		campaign.player_unit.BuildCmdLists()
		campaign.player_unit.ResetForNewTurn()
		
		scenario.Message('Welcome to Armoured Commander II!')
		
		# generate consoles and draw scenario screen for first time
		self.UpdateContextCon()
		self.UpdateTimeCon()
		self.UpdatePlayerInfoCon()
		self.UpdateCrewInfoCon()
		self.UpdateCmdCon()
		self.UpdateUnitCon()
		self.UpdateGuiCon()
		self.UpdateHexmapCon()
		self.UpdateMsgConsole()
		self.UpdateScenarioDisplay()
		
		# record mouse cursor position to check when it has moved
		mouse_x = -1
		mouse_y = -1
		
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
			
			# check to see if mouse cursor has moved
			if mouse.cx != mouse_x or mouse.cy != mouse_y:
				mouse_x = mouse.cx
				mouse_y = mouse.cy
				self.UpdateUnitInfoCon()
				self.UpdateScenarioDisplay()
			
			# check to see if mouse wheel has moved
			if mouse.wheel_up or mouse.wheel_down:
				
				# see if cursor is over a hex with 2+ units in it
				x = mouse.cx - 32
				y = mouse.cy - 9
				if (x,y) in self.hex_map_index:
					map_hex = self.hex_map_index[(x,y)]
					if len(map_hex.unit_stack) > 1:
						if mouse.wheel_up:
							map_hex.unit_stack[:] = map_hex.unit_stack[1:] + [map_hex.unit_stack[0]]
						else:
							map_hex.unit_stack.insert(0, map_hex.unit_stack.pop(-1))
						self.UpdateUnitCon()
						self.UpdateUnitInfoCon()
						self.UpdateScenarioDisplay()
						continue
			
			##### Player Keyboard Commands #####
			
			# no keyboard input
			if not keypress: continue
			
			# game menu
			if key.vk == libtcod.KEY_ESCAPE:
				ShowGameMenu()
				continue
			
			# key commands
			key_char = chr(key.c).lower()
			
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
					self.UpdateGuiCon()
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
					
					campaign.player_unit.positions_list[scenario.selected_position].UpdateVisibleHexes()
					
					self.UpdateContextCon()
					self.UpdateCrewInfoCon()
					self.UpdateGuiCon()
					self.UpdateScenarioDisplay()
					continue
				
				# toggle hatch for selected crewman
				elif key_char == 'h':
					
					# no crewman in selected position
					crewman = campaign.player_unit.positions_list[scenario.selected_position].crewman
					if crewman is None:
						continue
					
					if crewman.ToggleHatch():
						campaign.player_unit.positions_list[scenario.selected_position].UpdateVisibleHexes()
						self.UpdateCrewInfoCon()
						self.UpdateGuiCon()
						self.UpdateScenarioDisplay()
						continue
			
			# Movement phase only
			elif scenario.phase == 2:
				
				# move forward/backward
				if key_char in ['w', 's']:
					self.MovePlayer(key_char == 'w')
					self.UpdateContextCon()
					self.UpdateScenarioDisplay()
					continue
				
				# pivot hull
				elif key_char in ['a', 'd']:
					self.PivotPlayer(key_char == 'd')
					self.UpdateContextCon()
					self.UpdateScenarioDisplay()
					continue
				
			# Shooting phase
			elif scenario.phase == 3:
				
				# select player weapon
				if key_char in ['w', 's']:
					self.SelectWeapon(key_char == 's')
					self.UpdateGuiCon()
					self.UpdateContextCon()
					self.UpdateScenarioDisplay()
					continue
				
				# cycle player target
				elif key_char in ['a', 'd']:
					self.CycleTarget(key_char == 'd')
					self.UpdateGuiCon()
					self.UpdateContextCon()
					self.UpdateScenarioDisplay()
					continue
				
				# rotate turret
				elif key_char in ['q', 'e']:
					self.RotatePlayerTurret(key_char == 'e')
					self.UpdateContextCon()
					self.UpdateScenarioDisplay()
					continue
				
				# cycle ammo type
				elif key_char == 'c':
					result = scenario.selected_weapon.CycleAmmo()
					if result:
						self.UpdateContextCon()
						self.UpdateScenarioDisplay()
					continue
				
				# player fires active weapon at selected target
				elif key_char == 'f':
					result = campaign.player_unit.Attack(scenario.selected_weapon,
						scenario.selected_target)
					if result:
						self.UpdateUnitInfoCon()
						self.UpdateContextCon()
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


# wait for player to press continue key
# option to allow backspace pressed instead, returns True if so 
def WaitForContinue(allow_cancel=False):
	end_pause = False
	cancel = False
	while not end_pause:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		
		# get keyboard and/or mouse event
		if not GetInputEvent(): continue
		
		if key.vk == libtcod.KEY_BACKSPACE and allow_cancel:
			end_pause = True
			cancel = True
		elif key.vk == libtcod.KEY_TAB:
			end_pause = True
	if allow_cancel and cancel:
		return True
	return False


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
	direction = ConstrainDir(direction)
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
	if radius == 0: return [(hx, hy)]
	hex_list = []
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


# return a list of hexes covered by the given hextant in direction d from hx, hy
# max range is 3
def GetCoveredHexes(hx, hy, d):
	hex_list = []
	hex_list.append((hx, hy))
	for i in range(2):
		(hx, hy) = GetAdjacentHex(hx, hy, d)
	hex_list.append((hx, hy))
	hex_list += GetHexRing(hx, hy, 1)
	return hex_list


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
	(x1, y1) = scenario.PlotHex(unit1.hx, unit1.hy)
	(x2, y2) = scenario.PlotHex(unit2.hx, unit2.hy)
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


# return a random float between 0.0 and 100.0
def GetPercentileRoll():
	return float(libtcod.random_get_int(0, 0, 1000)) / 10.0


# round and restrict odds to between 3.0 and 97.0
def RestrictChance(chance):
	chance = round(chance, 1)
	if chance < 3.0: return 3.0
	if chance > 97.0: return 97.0
	return chance


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


# display the in-game menu
def ShowGameMenu():
	
	# draw the contents of the currently active tab to the menu console
	def DrawMenuCon(active_tab):
		# blit menu background to game menu console
		libtcod.console_blit(session.game_menu_bkg, 0, 0, 0, 0, game_menu_con, 0, 0)
		
		# highlight active tab title
		x1 = 2 + (active_tab * 11)
		for x in range(x1, x1+9):
			libtcod.console_set_char_foreground(game_menu_con, x, 1, ACTION_KEY_COL)
			libtcod.console_set_char_foreground(game_menu_con, x, 2, libtcod.white)
		
		# erase part of line so it appears that tab is in foreground
		x1 = 1 + (active_tab * 11)
		for x in range(x1, x1+10):
			libtcod.console_put_char(game_menu_con, x, 3, chr(0))
		
		# fill in active tab info
		
		# Root Game Menu
		if active_tab == 0:
			
			libtcod.console_set_default_foreground(game_menu_con, libtcod.white)
			libtcod.console_print_ex(game_menu_con, 42, 8, libtcod.BKGND_NONE,
				libtcod.CENTER, NAME)
			libtcod.console_print_ex(game_menu_con, 42, 9, libtcod.BKGND_NONE,
				libtcod.CENTER, 'Version: ' + VERSION)
			
			
			libtcod.console_set_default_foreground(game_menu_con, ACTION_KEY_COL)
			libtcod.console_print(game_menu_con, 36, 22, 'Q')
			libtcod.console_set_default_foreground(game_menu_con, libtcod.lighter_grey)
			libtcod.console_print(game_menu_con, 40, 22, 'Quit Game')
		
		libtcod.console_blit(game_menu_con, 0, 0, 0, 0, 0, 3, 3)
		libtcod.console_flush()
		
	
	# create a local copy of the current screen to re-draw when we're done
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
	# darken screen background
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
	
	# always start on root menu
	active_tab = 0
	
	# generate menu console for the first time and blit to screen
	DrawMenuCon(active_tab)
	
	# get input from player
	exit_menu = False
	result = ''
	while not exit_menu:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		
		# get keyboard and/or mouse event
		if not GetInputEvent(): continue
		
		# close menu
		if key.vk == libtcod.KEY_ESCAPE:
			exit_menu = True
			continue
		
		key_char = chr(key.c).lower()
		
		# Root Game Menu
		
		if active_tab == 0:
			if key_char == 'q':
				# TEMP - exit right away
				sys.exit()
	
	libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
	del temp_con
	return result


##########################################################################################
#                                      Main Script                                       #
##########################################################################################

global campaign, campaign_day, scenario, session 

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
libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER,
	'Loading...')
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
game_menu_con = libtcod.console_new(84, 54)
libtcod.console_set_default_background(game_menu_con, libtcod.black)
libtcod.console_set_default_foreground(game_menu_con, libtcod.white)
libtcod.console_clear(game_menu_con)

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()


# TEMP testing

# create a new campaign, campaign day and player unit
campaign = Campaign()
campaign_day = CampaignDay()
campaign.player_unit = Unit('Panzer 35(t)')
campaign.player_unit.nation = 'Germany'
campaign.player_unit.GenerateNewPersonnel()

# create a new scenario
scenario = Scenario()

# run the scenario
scenario.DoScenarioLoop()


print(NAME + ' shutting down')			# shutdown message
# END #

