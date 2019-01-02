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
	
from configparser import ConfigParser			# saving and loading settings
from random import choice, shuffle, sample		# for randomness
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
<<<<<<< HEAD
VERSION = '2019-01-02'			# game version
=======
VERSION = 'Alpha 1.0.0-2018-09-27'			# game version
>>>>>>> 6fb365a465b82191e802d0b528c9965c0c8558f0
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
CD_DESTHEX = [(1,-1), (1,0), (0,1), (-1,1), (-1,0), (0,-1)]	# same for pointy-top campaign day hexes
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
CD_HEX_EDGE_CELLS = {						# relative locations of edge cells in a given direction for campaign day hexes (pointy-topped)
	0: [(0,-4),(1,-3),(2,-2),(3,-1)],
	1: [(3,-1),(3,0),(3,1)],
	2: [(3,1),(2,2),(1,3),(0,4)],
	3: [(0,4),(-1,3),(-2,2),(-3,1)],
	4: [(-3,1),(-3,0),(-3,-1)],
	5: [(-3,-1),(-2,-2),(-1,-3),(0,-4)]
}
CAMPAIGN_DAY_HEXES = [						# hexes on campaign day map
	(0,0),(1,0),(2,0),(3,0),(4,0),
	(0,1),(1,1),(2,1),(3,1),
	(-1,2),(0,2),(1,2),(2,2),(3,2),
	(-1,3),(0,3),(1,3),(2,3),
	(-2,4),(-1,4),(0,4),(1,4),(2,4),
	(-2,5),(-1,5),(0,5),(1,5),
	(-3,6),(-2,6),(-1,6),(0,6),(1,6),
	(-3,7),(-2,7),(-1,7),(0,7),
	(-4,8),(-3,8),(-2,8),(-1,8),(0,8)
]


##### Colour Definitions #####
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency
ACTION_KEY_COL = libtcod.Color(51, 153, 255)		# colour for key commands
HIGHLIGHT_MENU_COL = libtcod.Color(30, 70, 130)		# background highlight colour for selected menu option
PORTRAIT_BG_COL = libtcod.Color(217, 108, 0)		# background color for unit portraits
UNKNOWN_UNIT_COL = libtcod.grey				# unknown enemy unit display colour
ENEMY_UNIT_COL = libtcod.light_red			# known "
GOLD_COL = libtcod.Color(255, 255, 100)			# golden colour for awards
<<<<<<< HEAD
CREW_NAME_MAX_LENGTH = 18				# maximum length for crew first or last names
=======

# list of possible keyboard layout settings
KEYBOARDS = ['QWERTY', 'AZERTY', 'QWERTZ', 'Dvorak']

# hex terrain types
HEX_TERRAIN_TYPES = [
	'openground', 'forest', 'fields_in_season', 'pond', 'roughground', 'village'
]

# list of all inner cells in a hex console image
HEX_CONSOLE_LOCATIONS = [
	(2,1),(3,1),(4,1),(1,2),(2,2),(3,2),(4,2),(5,2),(2,3),(3,3),(4,3)
]

# descriptive text for terrain types
HEX_TERRAIN_DESC = {
	'openground' : 'Open Ground', 'forest' : 'Forest', 'fields_in_season' : 'Fields',
	'pond' : 'Pond', 'roughground' : 'Rough Ground', 'village' : 'Village'
}

# maximum length for crew first or last names
CREW_NAME_MAX_LENGTH = 18
>>>>>>> 6fb365a465b82191e802d0b528c9965c0c8558f0

# list of campaign day menus and their highlight colours
CD_MENU_LIST = [
	('Support', 1, libtcod.Color(128, 128, 128)),
	('Crew', 2, libtcod.Color(140, 140, 0)),
	('Travel', 3, libtcod.Color(70, 140, 0)),
	('Group', 4, libtcod.Color(180, 0, 45)),
	('Supply', 5, libtcod.Color(128, 100, 64))
]

# directional arrows for directions on the campaign day map
CD_DIR_ARROW = [228,26,229,230,27,231]

# list of commands for travel in campaign day
CD_TRAVEL_CMDS = [
	('e',2,-2,228), ('d',2,0,26), ('c',2,2,229), ('z',-2,2,230), ('a',-2,0,27), ('q',-2,-2,231)
]

# text names for months
MONTH_NAMES = [
	'', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
	'September', 'October', 'November', 'December'
]


##########################################################################################
#                                         Classes                                        #
##########################################################################################

# Session: stores data that is generated for each game session and not stored in the saved game
class Session:
	def __init__(self):
		
		# flag: the last time the keyboard was polled, a key was pressed
		self.key_down = False
		
		# sound samples
		self.sample = {}
	
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


# Crew Position class: represents a crew position on a vehicle or gun
class CrewPosition:
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
		
		# crewman currently in this position
		self.crewman = None


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
		
		# save maximum range as an int
		self.max_range = 6
		if 'max_range' in self.stats:
			self.max_range = int(self.stats['max_range'])
			del self.stats['max_range']
		else:
			if self.stats['type'] in ['Turret MG', 'Co-ax MG', 'AA MG']:
				self.max_range = 3
			elif self.stats['type'] == 'Hull MG':
				self.max_range = 1
		
		# set up ammo stores if gun with types of ammo
		self.ammo_stores = None
		if self.GetStat('type') == 'Gun' and 'ammo_type_list' in self.stats:
			self.ammo_stores = {}
			self.LoadGunAmmo()

		# TODO: set up ready rack if any
		
		self.InitScenarioStats()

	# load this gun full of ammo
	def LoadGunAmmo(self):
		# set up empty categories first
		for ammo_type in self.stats['ammo_type_list']:
			self.ammo_stores[ammo_type] = 0
		
		# now determine loadout
		max_ammo = int(self.stats['max_ammo'])
		
		# only one type, fill it up
		if len(self.stats['ammo_type_list']) == 1:
			ammo_type = self.stats['ammo_type_list'][0]
			self.ammo_stores[ammo_type] = max_ammo
		
		# HE and AP: 70% and 30%
		else:
			if self.stats['ammo_type_list'] == ['HE', 'AP']:
				self.ammo_stores['HE'] = int(max_ammo * 0.7)
				self.ammo_stores['AP'] = max_ammo - self.ammo_stores['HE']
		

	# set up any data that is unique to a scenario
	def InitScenarioStats(self):
		self.fired = False
		self.maintained_rof = False			# can fire again even if fired == True
		self.current_ammo = None
		
		# Guns must have current_ammo set or else attacks won't work properly
		if self.GetStat('type') == 'Gun':
			self.current_ammo = self.stats['ammo_type_list'][0]
	
	# switch active ammo type for this weapon
	def SelectAmmoType(self, forward):
		
		if self.GetStat('type') != 'Gun':
			return False
		if self.current_ammo is None:
			return False
		if 'ammo_type_list' not in self.stats:
			return False
		
		i = self.stats['ammo_type_list'].index(self.current_ammo)
		
		if forward:
			if i == len(self.stats['ammo_type_list']) - 1:
				i = 0
			else:
				i += 1
		else:
			if i == 0:
				i = len(self.stats['ammo_type_list']) - 1
			else:
				i = 0
		self.current_ammo = self.stats['ammo_type_list'][i]
		
		return True
	
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
	
	# reset gun for start of new turn
	def ResetForNewTurn(self):
		self.fired = False
	
	# check for the value of a stat, return None if stat not present
	def GetStat(self, stat_name):
		if stat_name not in self.stats:
			return None
		return self.stats[stat_name]


# Unit Class: represents a single vehicle or gun, or a squad or small team of infantry
class Unit:
	def __init__(self, unit_id):
		
		self.unit_id = unit_id			# unique ID for unit type
		self.alive = True			# unit is alive
		
		# load unit stats from JSON file
		#with open(DATAPATH + 'unit_type_defs.json', encoding='utf8') as data_file:
		#	unit_types = json.load(data_file)
		#if unit_id not in unit_types:
		#	print('ERROR: Could not find unit id: ' + unit_id)
		#	self.unit_id = None
		#	return
		#self.stats = unit_types[unit_id].copy()

		
# Map Hex: one zone of terrain on the scenario map
class MapHex:
	def __init__(self, hx, hy):
		self.hx = hx						# hex coordinates in the map
		self.hy = hy						# 0,0 is centre of map


# Scenario: represents a single battle encounter
class Scenario:
	def __init__(self):
		
		# generate hex map: single hex surrounded by 4 hex rings. Final ring is not normally
		# part of play and stores units that are coming on or going off of the map proper
		self.map_hexes = []
		self.map_hexes.append((0,0))
		for r in range(1, 5):
			for (hx, hy) in GetHexRing(0, 0, r):
				self.map_hexes.append((hx,hy))
	
	# plot the center of a given in-game hex on the scenario hex map console
	# 0,0 appears in centre of console
	def PlotHex(self, hx, hy):
		x = (hx*7) + 26
		y = (hy*6) + (hx*3) + 21
		return (x,y)
	
	# update hexmap console
	def UpdateHexmapCon(self):
		
		libtcod.console_clear(hexmap_con)
		
		# FUTURE: can use different hex console images for different battlefield types / weather
		scen_hex = LoadXP('scen_hex.xp')
		libtcod.console_set_key_color(scen_hex, KEY_COLOR)
		
		# draw hexes to hex map console
		for (hx, hy) in self.map_hexes:
			if GetHexDistance(0, 0, hx, hy) > 3: break
			(x,y) = self.PlotHex(hx, hy)
			libtcod.console_blit(scen_hex, 0, 0, 0, 0, hexmap_con, x-5, y-3)
			
		del scen_hex
		
	
	# draw all scenario consoles to the screen
	def UpdateScenarioDisplay(self):
		
		libtcod.console_clear(con)
		
		libtcod.console_blit(bkg_console, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(hexmap_con, 0, 0, 0, 0, con, 32, 9)
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
	
	
	# main input loop for scenarios
	def DoScenarioLoop(self):
		
		# set up and load scenario consoles
		global bkg_console
		global hexmap_con
		
		# background outline console for left column
		bkg_console = LoadXP('bkg.xp')
		
		# hex map console
		hexmap_con = libtcod.console_new(53, 43)
		libtcod.console_set_default_background(hexmap_con, libtcod.black)
		libtcod.console_set_default_foreground(hexmap_con, libtcod.black)
		libtcod.console_clear(hexmap_con)
		
		
		# generate consoles and draw scenario screen for first time
		self.UpdateHexmapCon()
		self.UpdateScenarioDisplay()
		
		
		exit_scenario = False
		while not exit_scenario:
			
			# emergency exit in case of endless loop
			if libtcod.console_is_window_closed(): sys.exit()
			
			libtcod.console_flush()
			
			# get keyboard and/or mouse event
			keypress = GetInputEvent()
			
			##### Mouse Commands #####
			
			##### Player Keyboard Commands #####
			
			# no keyboard input
			if not keypress: continue
			
			# key commands
			key_char = chr(key.c).lower()
			#key_char = DecodeKey(key_char)
			
			if key_char == 'q':
				exit_scenario = True
				continue
		
		



# Zone Hex: a position on the campaign day map, each representing an area where a combat encounter
#   can possibly take place.
class ZoneHex:
	def __init__(self, hx, hy):
		self.hx = hx
		self.hy = hy
		
		self.coordinate = (chr(hy+65) + str(5 + int(hx - (hy - hy&1) / 2)))
		
		self.terrain_type = ''		# placeholder for terrain type in this zone
		self.console_seed = libtcod.random_get_int(0, 1, 128)	# seed for console image generation
		
		self.dirt_roads = []		# directions linked by a dirt road
		self.stone_roads = []		# " stone road
		
		self.controlled_by = 1		# which player side currently controls this zone
		self.known_to_player = False	# player knows enemy strength and organization in this zone
		
		# real enemy strength and organization, each 1-3
		roll = libtcod.random_get_int(0, 1, 6)
		if roll <= 3:
			self.enemy_strength = 1
		elif roll < 6:
			self.enemy_strength = 2
		else:
			self.enemy_strength = 3
		
		roll = libtcod.random_get_int(0, 1, 6)
		if roll == 1:
			self.enemy_organization = 1
		elif roll <= 4:
			self.enemy_organization = 2
		else:
			self.enemy_organization = 3
	
	# generate a random terrain type for this hex
	# FUTURE: can pull data from the campaign day to determine possible terrain types
	def GenerateTerrainType(self):
		
		roll = GetPercentileRoll()
		
		# TEMP: settings are for Poland/September campaign
		if roll <= 40.0:
			self.terrain_type = 'Flat'
		elif roll <= 50.0:
			self.terrain_type = 'Forest'
		elif roll <= 65.0:
			self.terrain_type = 'Hills'
		elif roll <= 75.0:
			self.terrain_type = 'Fields'
		elif roll <= 80.0:
			self.terrain_type = 'Marsh'
		elif roll <= 90.0:
			self.terrain_type = 'Villages'
		else:
			self.terrain_type = 'Flat'


# Campaign Day: represents one calendar day in a campaign with a 5x7 map of terrain hexes, each of
# which may spawn a Scenario
class CampaignDay:
	def __init__(self):
		
		# set up air and artillery support for the day
		self.air_support_level = 0.0
		self.air_support_step = 0.0
		if 'air_support_level' in campaign.today:
			self.air_support_level = float(campaign.today['air_support_level'])
			self.air_support_step = float(campaign.today['air_support_step'])
		
		self.arty_support_level = 0.0
		self.arty_support_step = 0.0
		if 'arty_support_level' in campaign.today:
			self.arty_support_level = float(campaign.today['arty_support_level'])
			self.arty_support_step = float(campaign.today['arty_support_step'])
		
		# current chance of random scenario event being triggered
		self.random_event_chance = SCENARIO_RANDOM_EVENT_CHANCE
		
		# list of messages: each is a tuple of time and text
		self.messages = []
		
		# victory point rewards for this campaign day
		self.capture_zone_vp = 2
		self.unit_destruction_vp = {
			'Infantry': 1,
			'Gun' : 2,
			'Vehicle': 4 
		}
		
		# records for end-of-day summary
		self.records = {
			'Map Areas Captured' : 0,
			'Gun Hits' : 0,
			'Vehicles Destroyed' : 0,
			'Guns Destroyed' : 0,
			'Infantry Destroyed' : 0
		}
		
		# generate campaign day map
		self.map_hexes = {}
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			self.map_hexes[(hx,hy)] = ZoneHex(hx, hy)
		
			# set zone terrain type too
			self.map_hexes[(hx,hy)].GenerateTerrainType()
		
		# dictionary of screen display locations on the display console and their corresponding map hex
		self.zone_map_index = {}
		
		# generate dirt roads on campaign day map
		self.GenerateRoads()
		
		self.player_unit_location = (-2, 8)		# set player unit group location
		self.map_hexes[(-2, 8)].controlled_by = 0	# set player location to player control
		
		self.active_menu = 3				# number of currently active command menu
		self.travel_direction = None			# selected direction of travel
		
		self.abandoned_tank = False			# set to true if player abandoned their tank that day
		
		self.scenario = None				# currently active scenario in progress
	
	# reduce air support level due to a successful request
	def ReduceAirSupLevel(self):
		self.air_support_level -= self.air_support_step
		if self.air_support_level < 0.0:
			self.air_support_level = 0.0
	
	# reduce artillery support level due to a successful request
	def ReduceArtSupLevel(self):
		self.arty_support_level -= self.arty_support_step
		if self.arty_support_level < 0.0:
			self.arty_support_level = 0.0
	
	# increase air or arty support level due to random event, etc.
	# don't increase if there was none to start
	def IncreaseSupLevel(self, air_sup):
		if air_sup:
			if self.air_support_step == 0.0: return
			self.air_support_level += self.air_support_step
			text = 'Air'
		else:
			if self.arty_support_step == 0.0: return
			self.arty_support_level += arty_support_step
			text = 'Artillery'
		text += ' support level increased.'
		Message(text)
		
	# add a message with the current timestamp to the journal
	def AddMessage(self, text):
		self.messages.append((str(campaign.calendar['hour']).zfill(2) + ':' + str(campaign.calendar['minute']).zfill(2), text))
	
	# generate roads linking zones; only dirt roads for now
	def GenerateRoads(self):
		
		# generate one road from the bottom to the top of the map
		hx = choice([-4,-3,-2,-1,0])
		for hy in range(8, -1, -1):
			direction = choice([5,0])
			(hx2,hy2) = self.GetAdjacentCDHex(hx, hy, direction)
			if (hx2,hy2) not in self.map_hexes:
				if direction == 0:
					direction = 5
				else:
					direction = 0
				(hx2,hy2) = self.GetAdjacentCDHex(hx, hy, direction)
			self.map_hexes[(hx,hy)].dirt_roads.append(direction)
			# avoid looking for final hex off-map
			if (hx2,hy2) in self.map_hexes:
				self.map_hexes[(hx2,hy2)].dirt_roads.append(ConstrainDir(direction + 3))
			hx = hx2
		
		# 1-2 branch roads
		target_hy_list = sample(range(0, 9), libtcod.random_get_int(0, 1, 3))
		for target_hy in target_hy_list:
			for (hx, hy) in CAMPAIGN_DAY_HEXES:
				if hy != target_hy: continue
				if len(self.map_hexes[(hx,hy)].dirt_roads) == 0: continue
				
				direction = choice([1,4])
				# make sure can take at least one step in this direction
				if self.GetAdjacentCDHex(hx, hy, direction) not in self.map_hexes:
					if direction == 1:
						direction = 4
					else:
						direction = 1
				
				# create road
				while (hx,hy) in self.map_hexes:
					self.map_hexes[(hx,hy)].dirt_roads.append(direction)
					(hx,hy) = self.GetAdjacentCDHex(hx, hy, direction)
					if (hx,hy) in self.map_hexes:
						self.map_hexes[(hx,hy)].dirt_roads.append(ConstrainDir(direction + 3))
			
	
	# resupply the player unit and other units in the player's unit group
	def ResupplyPlayer(self):
		campaign.AdvanceClock(0, 30)
		ShowNotification('You contact HQ for resupply, which arrives 30 minutes later.')
		for weapon in campaign.player_unit.weapon_list:
			if weapon.ammo_stores is not None:
				weapon.LoadGunAmmo()
				text = weapon.stats['name'] + ' gun has been fully restocked with ammo.'
				ShowNotification(text)
		# resupply allies too
		for unit in campaign.player_unit_group:
			for weapon in unit.weapon_list:
				if weapon.ammo_stores is not None:
					weapon.LoadGunAmmo()
	
	
	# initiate a battle encounter scenario and store it in the CD object
	def InitScenario(self, hx, hy, source_direction):
		self.scenario = Scenario(self.map_hexes[(hx, hy)], source_direction)
		
	
	# plot the centre of a day map hex location onto the map console
	# top left of hex 0,0 will appear at cell 2,2
	def PlotCDHex(self, hx, hy):
		x = (hx*6) + (hy*3)
		y = (hy*5)
		return (x+5,y+6)
	
	# returns the hx, hy location of the adjacent hex in direction
	def GetAdjacentCDHex(self, hx1, hy1, direction):
		(hx_m, hy_m) = CD_DESTHEX[direction]
		return (hx1+hx_m, hy1+hy_m)
	
	
	# generate/update the campaign day map console
	def UpdateCDMapCon(self):
		
		CHAR_LOCATIONS = [
				(3,1), (2,2), (3,2), (4,2), (1,3), (2,3), (3,3), (4,3), (5,3),
				(1,4), (2,4), (4,4), (5,4), (1,5), (2,5), (3,5), (4,5), (5,5),
				(2,6), (3,6), (4,6), (3,7)
		]
		
		def GetRandomLocation(gen):
			return CHAR_LOCATIONS[libtcod.random_get_int(generator, 0, 21)]
		
		libtcod.console_clear(cd_map_con)
		self.zone_map_index = {}
		
		# draw map hexes to console
		
		# load base zone image
		dayhex_openground = LoadXP('dayhex_openground.xp')
		temp_con = libtcod.console_new(7, 9)
		libtcod.console_set_key_color(temp_con, KEY_COLOR)
		bg_col = libtcod.Color(0,64,0)
		
		for (hx, hy), zone_hex in self.map_hexes.items():
			
			# generate console image for this zone's terrain type
			libtcod.console_blit(dayhex_openground, 0, 0, 0, 0, temp_con, 0, 0)
			
			generator = libtcod.random_new_from_seed(zone_hex.console_seed)
			
			if zone_hex.terrain_type == 'Forest':
				
				for (x,y) in CHAR_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 10) <= 4: continue
					col = libtcod.Color(0,libtcod.random_get_int(generator, 100, 170),0)
					libtcod.console_put_char_ex(temp_con, x, y, 6, col, bg_col)
				
			elif zone_hex.terrain_type == 'Hills':
				
				col = libtcod.Color(70,libtcod.random_get_int(generator, 110, 150),0)
				x = libtcod.random_get_int(generator, 2, 3)
				libtcod.console_put_char_ex(temp_con, x, 2, 236, col, bg_col)
				libtcod.console_put_char_ex(temp_con, x+1, 2, 237, col, bg_col)
				
				if libtcod.random_get_int(generator, 0, 1) == 0:
					x = 1
				else:
					x = 4
				libtcod.console_put_char_ex(temp_con, x, 4, 236, col, bg_col)
				libtcod.console_put_char_ex(temp_con, x+1, 4, 237, col, bg_col)
				
				x = libtcod.random_get_int(generator, 2, 3)
				libtcod.console_put_char_ex(temp_con, x, 6, 236, col, bg_col)
				libtcod.console_put_char_ex(temp_con, x+1, 6, 237, col, bg_col)
				
			elif zone_hex.terrain_type == 'Fields':
				
				for (x,y) in CHAR_LOCATIONS:
					c = libtcod.random_get_int(generator, 120, 190)
					libtcod.console_put_char_ex(temp_con, x, y, 176,
						libtcod.Color(c,c,0), bg_col)
				
			elif zone_hex.terrain_type == 'Marsh':
				
				elements = libtcod.random_get_int(generator, 7, 13)
				while elements > 0:
					(x,y) = GetRandomLocation(generator)
					if libtcod.console_get_char(temp_con, x, y) == 176: continue
					libtcod.console_put_char_ex(temp_con, x, y, 176,
						libtcod.Color(45,0,180), bg_col)
					elements -= 1
				
			elif zone_hex.terrain_type == 'Villages':
				
				elements = libtcod.random_get_int(generator, 5, 9)
				while elements > 0:
					(x,y) = GetRandomLocation(generator)
					if libtcod.console_get_char(temp_con, x, y) == 249: continue
					libtcod.console_put_char_ex(temp_con, x, y, 249,
						libtcod.Color(77,77,77), bg_col)
					elements -= 1
			
			# draw the final image to the map console
			(x,y) = self.PlotCDHex(hx, hy)
			libtcod.console_blit(temp_con, 0, 0, 0, 0, cd_map_con, x-3, y-4)
			
			# record screen locations of hex
			# strictly speaking this only needs to be done once ever, but in
			# the future it might be possible to scroll the campaign day map
			# so we'd need to update this anyway
			self.zone_map_index[(x, y-3)] = (hx, hy)
			for x1 in range(x-1, x+2):
				self.zone_map_index[(x1, y-2)] = (hx, hy)
				self.zone_map_index[(x1, y+2)] = (hx, hy)
			for x1 in range(x-2, x+3):
				self.zone_map_index[(x1, y-1)] = (hx, hy)
				self.zone_map_index[(x1, y)] = (hx, hy)
				self.zone_map_index[(x1, y+1)] = (hx, hy)
			self.zone_map_index[(x, y+3)] = (hx, hy)
			
		del temp_con, dayhex_openground
		
		# draw dirt roads overtop
		for (hx, hy), map_hex in self.map_hexes.items():
			if len(map_hex.dirt_roads) == 0: continue
			for direction in map_hex.dirt_roads:
				# only draw if in direction 0-2
				if direction > 2: continue
				# get the other zone linked by road
				(hx2, hy2) = self.GetAdjacentCDHex(hx, hy, direction)
				if (hx2, hy2) not in self.map_hexes: continue
				
				# paint road
				(x1, y1) = self.PlotCDHex(hx, hy)
				(x2, y2) = self.PlotCDHex(hx2, hy2)
				line = GetLine(x1, y1, x2, y2)
				for (x, y) in line:
				
					# don't paint over outside of map area
					if libtcod.console_get_char_background(cd_map_con, x, y) == libtcod.black:
						continue
					
					libtcod.console_set_char_background(cd_map_con, x, y,
						DIRT_ROAD_COL, libtcod.BKGND_SET)
					
					# if character is not blank or hex edge, remove it
					if libtcod.console_get_char(cd_map_con, x, y) not in [0, 249, 250]:
						libtcod.console_set_char(cd_map_con, x, y, 0)
				
		# draw hex row guides
		for i in range(0, 9):
			libtcod.console_put_char_ex(cd_map_con, 0, 6+(i*5), chr(i+65),
				libtcod.light_green, libtcod.black)
		
		# draw hex column guides
		for i in range(0, 5):
			libtcod.console_put_char_ex(cd_map_con, 7+(i*6), 50, chr(i+49),
				libtcod.light_green, libtcod.black)
		for i in range(5, 9):
			libtcod.console_put_char_ex(cd_map_con, 32, 39-((i-5)*10), chr(i+49),
				libtcod.light_green, libtcod.black)
	
	
	# generate/update the campaign day unit layer console
	def UpdateCDUnitCon(self):
		libtcod.console_clear(cd_unit_con)
		libtcod.console_set_default_foreground(cd_unit_con, libtcod.white)
		
		# draw enemy strength and organization levels
		# only display if adjacent to player
		libtcod.console_set_default_foreground(cd_unit_con, libtcod.red)
		(player_hx, player_hy) = self.player_unit_location
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			if self.map_hexes[(hx,hy)].controlled_by == 0: continue
			if not self.map_hexes[(hx,hy)].known_to_player: continue
			if GetHexDistance(player_hx, player_hy, hx, hy) > 1: continue
			text = str(self.map_hexes[(hx,hy)].enemy_strength)
			text += ' '
			text += str(self.map_hexes[(hx,hy)].enemy_organization)
			(x,y) = self.PlotCDHex(hx, hy)
			ConsolePrint(cd_unit_con, x-1, y, text)
		
		# draw player unit group
		(hx, hy) = self.player_unit_location
		(x,y) = self.PlotCDHex(hx, hy)
		libtcod.console_put_char_ex(cd_unit_con, x, y, '@', libtcod.white, libtcod.black)
	
	
	# generate/update the zone control console, showing the battlefront between two sides
	def UpdateCDControlCon(self):
		libtcod.console_clear(cd_control_con)
		
		# run through every hex, if it's under player control, see if there an adjacent
		# enemy-controlled hex and if so, draw a border there
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			if self.map_hexes[(hx,hy)].controlled_by != 0: continue
			
			for direction in range(6):
				(hx_m, hy_m) = CD_DESTHEX[direction]
				hx2 = hx+hx_m
				hy2 = hy+hy_m
				
				# hex is off map
				if (hx2, hy2) not in self.map_hexes: continue
				# hex is friendly controlled
				if self.map_hexes[(hx2,hy2)].controlled_by == 0: continue
				
				# draw a border
				(x,y) = self.PlotCDHex(hx, hy)
				for (xm,ym) in CD_HEX_EDGE_CELLS[direction]:
					libtcod.console_put_char_ex(cd_control_con, x+xm,
						y+ym, chr(249), libtcod.red, libtcod.black)
	
	
	# generate/update the GUI console
	def UpdateCDGUICon(self):
		libtcod.console_clear(cd_gui_con)
		
		# movement menu, direction currently selected
		if self.active_menu == 3 and self.travel_direction is not None:
			
			# draw directional line
			(hx, hy) = self.player_unit_location
			(x1,y1) = self.PlotCDHex(hx, hy)
			(hx, hy) = self.GetAdjacentCDHex(hx, hy, self.travel_direction)
			if (hx, hy) in self.map_hexes:
				(x2,y2) = self.PlotCDHex(hx, hy)
				line = GetLine(x1,y1,x2,y2)
				for (x,y) in line[1:-1]:
					libtcod.console_put_char_ex(cd_gui_con, x, y, 250, libtcod.green,
						libtcod.black)
				(x,y) = line[-1]
				libtcod.console_put_char_ex(cd_gui_con, x, y, CD_DIR_ARROW[self.travel_direction],
					libtcod.green, libtcod.black)
	
	
	# generate/update the player unit console
	def UpdateCDPlayerUnitCon(self):
		libtcod.console_clear(cd_player_unit_con)
		campaign.player_unit.DisplayMyInfo(cd_player_unit_con, 0, 0, status=False)
	
	
	# generate/update the command menu console
	def UpdateCDCommandCon(self):
		libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
		libtcod.console_clear(cd_command_con)
		
		x = 0
		for (text, num, col) in CD_MENU_LIST:
			libtcod.console_set_default_background(cd_command_con, col)
			libtcod.console_rect(cd_command_con, x, 0, 2, 1, True, libtcod.BKGND_SET)
			
			# only travel and supply menus active for now
			if num not in [3, 5]:
				libtcod.console_set_default_foreground(cd_command_con, libtcod.dark_grey)
			# menu number
			ConsolePrint(cd_command_con, x, 0, str(num))
			libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			
			x += 2
			
			# display menu text if active
			if self.active_menu == num:
				libtcod.console_rect(cd_command_con, x, 0, len(text)+2, 1,
					True, libtcod.BKGND_SET)
				ConsolePrint(cd_command_con, x, 0, text)
				x += len(text) + 2
		
		# fill in rest of menu line with final colour
		libtcod.console_rect(cd_command_con, x, 0, 24-x, 1, True, libtcod.BKGND_SET)
		libtcod.console_set_default_background(cd_command_con, libtcod.black)
		
		# travel menu
		if self.active_menu == 3:
			
			libtcod.console_put_char(cd_command_con, 11, 4, '@')
			
			for direction in range(6):
				libtcod.console_set_default_foreground(cd_command_con, libtcod.dark_green)
				
				if self.travel_direction is not None:
					if self.travel_direction == direction:
						libtcod.console_set_default_foreground(cd_command_con, libtcod.blue)
				
				(k, x, y, char) = CD_TRAVEL_CMDS[direction]
				libtcod.console_put_char(cd_command_con, 11+x, 4+y, EncodeKey(k).upper())
				if direction <= 2:
					x+=1
				else:
					x-=1
				libtcod.console_put_char(cd_command_con, 11+x, 4+y, chr(char))
			
			if self.travel_direction is None:
				libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
				ConsolePrintEx(cd_command_con, 12, 22, libtcod.BKGND_NONE, libtcod.CENTER,
					'Select Direction')
				return
							
			# check to see whether travel in this direction is not possible
			(hx, hy) = self.player_unit_location
			(hx, hy) = self.GetAdjacentCDHex(hx, hy, self.travel_direction)
			if (hx, hy) not in self.map_hexes: return
				
			# display enemy strength/organization if any and chance of encounter
			map_hex = self.map_hexes[(hx,hy)]
			if map_hex.controlled_by == 1:
				
				libtcod.console_set_default_foreground(cd_command_con, libtcod.red)
				ConsolePrint(cd_command_con, 1, 9, 'Enemy Controlled')
				
				if not map_hex.known_to_player:
					libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
					ConsolePrint(cd_command_con, 0, 13, 'Recon: 15 mins.')
					libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
					ConsolePrint(cd_command_con, 5, 21, 'R')
					libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
					ConsolePrint(cd_command_con, 12, 21, 'Recon')
				else:
					ConsolePrint(cd_command_con, 2, 10, 'Strength: ' + str(map_hex.enemy_strength))
					ConsolePrint(cd_command_con, 2, 11, 'Organization: ' + str(map_hex.enemy_organization))
					libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			
			libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			text = 'Travel Time: '
			if self.travel_direction in map_hex.dirt_roads:
				text += '15'
			else:
				text += '30'
			text += ' mins.'
			ConsolePrint(cd_command_con, 0, 14, text)
		
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			ConsolePrint(cd_command_con, 5, 22, 'Enter')
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			ConsolePrint(cd_command_con, 12, 22, 'Proceed')
		
		# resupply menu
		elif self.active_menu == 5:
			
			ConsolePrintEx(cd_command_con, 12, 10, libtcod.BKGND_NONE, libtcod.CENTER,
				'Request resupply:')
			ConsolePrintEx(cd_command_con, 12, 11, libtcod.BKGND_NONE, libtcod.CENTER,
				'30 mins.')
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			ConsolePrint(cd_command_con, 8, 22, 'R')
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			ConsolePrint(cd_command_con, 10, 22, 'Resupply')
	
	
	# generate/update the time and weather console 33x4
	# FUTURE: will also be used in scenario display
	def UpdateTimeWeatherDisplay(self):
		libtcod.console_clear(time_weather_con)
		
		# time remaining in combat day
		libtcod.console_set_default_background(time_weather_con, libtcod.darker_yellow)
		libtcod.console_rect(time_weather_con, 1, 1, 31, 1, True, libtcod.BKGND_SET)
		
		hours = campaign.calendar['hour'] - campaign.start_of_day['hour']
		minutes = campaign.calendar['minute'] - campaign.start_of_day['minute']
		if minutes < 0:
			hours -= 1
			minutes += 60
		minutes += (hours * 60)
		x = int(31.0 * float(minutes) / float(campaign.day_length))
		libtcod.console_set_default_background(time_weather_con, libtcod.dark_yellow)
		libtcod.console_rect(time_weather_con, 1, 1, x, 1, True, libtcod.BKGND_SET)
		
		libtcod.console_set_default_background(time_weather_con, libtcod.black)
		text = str(campaign.calendar['hour']).zfill(2) + ':' + str(campaign.calendar['minute']).zfill(2)
		ConsolePrint(time_weather_con, 14, 1, text)
		ConsolePrintEx(time_weather_con, 16, 2, libtcod.BKGND_NONE, libtcod.CENTER, 'Clear')
	
	
	# generate/update the campaign info console
	def UpdateCDCampaignCon(self):
		libtcod.console_clear(cd_campaign_con)
		
		# current VP total
		libtcod.console_set_default_foreground(cd_campaign_con, ACTION_KEY_COL)
		ConsolePrint(cd_campaign_con, 0, 0, 'Campaign Info')
		libtcod.console_set_default_foreground(cd_campaign_con, libtcod.white)
		ConsolePrint(cd_campaign_con, 1, 2, 'VP: ' + str(campaign.player_vp))
	
	
	# generate/update the zone info console
	def UpdateCDZoneInfoCon(self):
		libtcod.console_clear(cd_zone_info_con)
		
		libtcod.console_set_default_foreground(cd_zone_info_con, ACTION_KEY_COL)
		ConsolePrint(cd_zone_info_con, 0, 0, 'Zone Info')
		
		# mouse cursor outside of map area
		if mouse.cx < 31 or mouse.cx > 59:
			return
		x = mouse.cx - 28
		y = mouse.cy - 4
		
		# no zone here
		if (x,y) not in self.zone_map_index: return
		
		(hx, hy) = self.zone_map_index[(x,y)]
		zone_hex = self.map_hexes[(hx, hy)]
		
		# display hex zone coordinates
		libtcod.console_set_default_foreground(cd_zone_info_con, libtcod.light_green)
		ConsolePrint(cd_zone_info_con, 11, 0, zone_hex.coordinate)
		
		# terrain
		libtcod.console_set_default_foreground(cd_zone_info_con, libtcod.light_grey)
		ConsolePrint(cd_zone_info_con, 0, 1, zone_hex.terrain_type)
		
		# control
		if zone_hex.controlled_by == 0:
			ConsolePrint(cd_zone_info_con, 0, 2, 'Friendly controlled')
		else:
			ConsolePrint(cd_zone_info_con, 0, 2, 'Enemy controlled')
			if zone_hex.known_to_player:
				ConsolePrint(cd_zone_info_con, 0, 3, 'Strength: ' + 
					str(zone_hex.enemy_strength))
				ConsolePrint(cd_zone_info_con, 0, 4, 'Organization: ' + 
					str(zone_hex.enemy_organization))
		
		# roads
		if len(zone_hex.dirt_roads) > 0:
			ConsolePrint(cd_zone_info_con, 0, 8, 'Dirt roads')
	
	
	# draw all campaign day consoles to screen
	def UpdateCDDisplay(self):
		libtcod.console_clear(con)
		
		libtcod.console_blit(daymap_bkg, 0, 0, 0, 0, con, 0, 0)			# background frame
		libtcod.console_blit(cd_map_con, 0, 0, 0, 0, con, 28, 4)		# terrain map
		libtcod.console_blit(cd_control_con, 0, 0, 0, 0, con, 28, 4, 1.0, 0.0)	# zone control layer
		libtcod.console_blit(cd_unit_con, 0, 0, 0, 0, con, 28, 4, 1.0, 0.0)	# unit group layer
		libtcod.console_blit(cd_gui_con, 0, 0, 0, 0, con, 28, 4, 1.0, 0.0)	# GUI layer
		
		libtcod.console_blit(time_weather_con, 0, 0, 0, 0, con, 29, 0)		# time and weather
		
		libtcod.console_blit(cd_player_unit_con, 0, 0, 0, 0, con, 1, 1)		# player unit info
		libtcod.console_blit(cd_command_con, 0, 0, 0, 0, con, 1, 35)		# command menu
		libtcod.console_blit(cd_campaign_con, 0, 0, 0, 0, con, 66, 1)		# campaign info
		libtcod.console_blit(cd_zone_info_con, 0, 0, 0, 0, con, 66, 50)		# zone info
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	# main campaign day input loop
	def CampaignDayLoop(self):
		
		global daymap_bkg, cd_map_con, cd_unit_con, cd_control_con, cd_command_con
		global cd_player_unit_con, cd_campaign_con, cd_gui_con, cd_zone_info_con
		global time_weather_con
		
		# create consoles
		
		# campaign day map background
		daymap_bkg = LoadXP('daymap_bkg.xp')
		
		# campaign day map console 35x53
		cd_map_con = libtcod.console_new(35, 53)
		libtcod.console_set_default_background(cd_map_con, libtcod.black)
		libtcod.console_set_default_foreground(cd_map_con, libtcod.white)
		libtcod.console_clear(cd_map_con)
		
		# campaign day unit group console 35x53
		cd_unit_con = libtcod.console_new(35, 53)
		libtcod.console_set_default_background(cd_unit_con, KEY_COLOR)
		libtcod.console_set_default_foreground(cd_unit_con, libtcod.white)
		libtcod.console_clear(cd_unit_con)
		
		# campaign day hex zone control console 35x53
		cd_control_con = libtcod.console_new(35, 53)
		libtcod.console_set_default_background(cd_control_con, KEY_COLOR)
		libtcod.console_set_default_foreground(cd_control_con, libtcod.red)
		libtcod.console_clear(cd_control_con)
		
		# campaign day GUI console
		cd_gui_con = libtcod.console_new(35, 53)
		libtcod.console_set_default_background(cd_gui_con, KEY_COLOR)
		libtcod.console_set_default_foreground(cd_gui_con, libtcod.red)
		libtcod.console_clear(cd_gui_con)
		
		# time and weather console
		time_weather_con = libtcod.console_new(33, 4)
		libtcod.console_set_default_background(time_weather_con, libtcod.black)
		libtcod.console_set_default_foreground(time_weather_con, libtcod.white)
		libtcod.console_clear(time_weather_con)
		
		# player unit console 24x16
		cd_player_unit_con = libtcod.console_new(24, 16)
		libtcod.console_set_default_background(cd_player_unit_con, libtcod.black)
		libtcod.console_set_default_foreground(cd_player_unit_con, libtcod.white)
		libtcod.console_clear(cd_player_unit_con)
		
		# command menu console 24x24
		cd_command_con = libtcod.console_new(24, 24)
		libtcod.console_set_default_background(cd_command_con, libtcod.black)
		libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
		libtcod.console_clear(cd_command_con)
		
		# campaign info console 23x16
		cd_campaign_con = libtcod.console_new(23, 16)
		libtcod.console_set_default_background(cd_campaign_con, libtcod.black)
		libtcod.console_set_default_foreground(cd_campaign_con, libtcod.white)
		libtcod.console_clear(cd_campaign_con)
		
		# zone info console 23x9
		cd_zone_info_con = libtcod.console_new(23, 9)
		libtcod.console_set_default_background(cd_zone_info_con, libtcod.black)
		libtcod.console_set_default_foreground(cd_zone_info_con, libtcod.white)
		libtcod.console_clear(cd_zone_info_con)
		
		
		# generate consoles for the first time
		self.UpdateCDMapCon()
		self.UpdateCDControlCon()
		self.UpdateCDUnitCon()
		self.UpdateCDGUICon()
		self.UpdateTimeWeatherDisplay()
		self.UpdateCDPlayerUnitCon()
		self.UpdateCDCommandCon()
		self.UpdateCDCampaignCon()
		self.UpdateCDZoneInfoCon()
		self.UpdateCDDisplay()
		
		# record mouse cursor position to check when it has moved
		mouse_x = -1
		mouse_y = -1
		
		SaveGame()
		
		exit_loop = False
		while not exit_loop:
			
			# emergency exit in case of endless loop
			if libtcod.console_is_window_closed(): sys.exit()
			
			# if we've initiated a scenario or are resuming a saved game with a scenario
			# running, go to the scenario loop now
			if self.scenario is not None:
				
				DoScenario()
				
				# we're exiting to main menu, game is already saved
				if session.exiting_to_main_menu:
					session.exiting_to_main_menu = False
					exit_loop = True
					continue
				
				self.UpdateCDDisplay()
				libtcod.console_flush()
				
				# handle result of a completed scenario
				
				# player was destroyed
				if self.scenario.winner == 1:
					EraseGame()
					DisplayCampaignDaySummary()
					session.exiting_to_main_menu = False
					exit_loop = True
					continue
				
				# player won
				elif self.scenario.winner == 0:
					ShowNotification('You have defeated all enemy resistance and now control this area.')
					campaign_day.AddMessage('We captured the enemy-controlled area.')
					self.map_hexes[self.player_unit_location].controlled_by = 0
					self.records['Map Areas Captured'] += 1
					self.UpdateTimeWeatherDisplay()
					self.UpdateCDControlCon()
					self.UpdateCDUnitCon()
					self.UpdateCDZoneInfoCon()
					
					# award vp to player
					campaign.AwardVP(self.capture_zone_vp)
					self.UpdateCDCampaignCon()
					
					self.UpdateCDDisplay()
					
					# delete completed scenario
					self.scenario = None
					
					# check for end of day
					# FUTURE: must be way to do this once in the loop
					if campaign.EndOfDay():
						ShowNotification('Your combat day has ended.') 
						campaign_day.AddMessage('The combat day ends')
						EraseGame()
						DisplayCampaignDaySummary()
						session.exiting_to_main_menu = False
						exit_loop = True
						continue
					
					SaveGame()
					
			libtcod.console_flush()
			
			# get keyboard and/or mouse event
			keypress = GetInputEvent()
			
			# check to see if mouse cursor has moved
			if mouse.cx != mouse_x or mouse.cy != mouse_y:
				mouse_x = mouse.cx
				mouse_y = mouse.cy
				self.UpdateCDZoneInfoCon()
				self.UpdateCDDisplay()
			
			##### Player Keyboard Commands #####
			if not keypress: continue
			
			# Determine action based on key pressed
			
			# enter game menu
			if key.vk in [libtcod.KEY_ESCAPE, libtcod.KEY_F1, libtcod.KEY_F2, libtcod.KEY_F3]:
				
				result = ShowGameMenu()
				
				if result == 'exit_game':
					SaveGame()
					exit_loop = True
				
				continue
			
			# key commands
			key_char = chr(key.c).lower()
			
			# switch active menu
			if key_char in ['3', '5']:
				if self.active_menu != int(key_char):
					self.active_menu = int(key_char)
					self.UpdateCDGUICon()
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
				continue
			
			# map key to current keyboard layout
			key_char = DecodeKey(key_char)
			
			# travel menu active
			if self.active_menu == 3:
				
				# set travel direction
				DIRECTION_KEYS = ['e', 'd', 'c', 'z', 'a', 'q'] 
				if key_char in DIRECTION_KEYS:
					direction = DIRECTION_KEYS.index(key_char)
					if self.travel_direction is None:
						self.travel_direction = direction
					else:
						# cancel direction
						if self.travel_direction == direction:
							self.travel_direction = None
						else:
							self.travel_direction = direction
					self.UpdateCDGUICon()
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
					continue
				
				# recon or proceed with travel
				elif key_char == 'r' or key.vk == libtcod.KEY_ENTER:
					
					# no direction set
					if self.travel_direction is None: continue
					
					# ensure that travel/recon is possible
					(hx, hy) = self.player_unit_location
					map_hex1 = self.map_hexes[(hx,hy)]
					(hx, hy) = self.GetAdjacentCDHex(hx, hy, self.travel_direction)
					if (hx, hy) not in self.map_hexes:
						continue
					map_hex2 = self.map_hexes[(hx,hy)]
					
					# recon
					if key_char == 'r':
						if map_hex2.known_to_player: continue
						map_hex2.known_to_player = True
						campaign.AdvanceClock(0, 15)
						text = 'Estimated enemy strength in zone: ' + str(map_hex2.enemy_strength)
						text += '; estimated organization: ' + str(map_hex2.enemy_organization) + '.'
						ShowNotification(text)
						self.UpdateTimeWeatherDisplay()
						self.UpdateCDUnitCon()
						self.UpdateCDCommandCon()
						self.UpdateCDZoneInfoCon()
						self.UpdateCDDisplay()
						
					# proceed with travel
					else:
					
						# advance clock
						if self.travel_direction in map_hex1.dirt_roads:
							mins = 15
						else:
							mins = 30
						campaign.AdvanceClock(0, mins)
						
						# set new player location and clear travel direction
						# save direction from which player entered zone
						self.player_unit_location = (hx, hy)
						source_direction = ConstrainDir(self.travel_direction + 3)
						self.travel_direction = None
						self.UpdateCDGUICon()
						
						# trigger battle encounter if enemy-controlled
						ShowNotification('You enter the enemy-held zone.')
						campaign_day.AddMessage('We moved into an enemy-held area.')
						self.InitScenario(hx, hy, source_direction)
							
						self.UpdateTimeWeatherDisplay()
						self.UpdateCDControlCon()
						self.UpdateCDUnitCon()
						self.UpdateCDCommandCon()
						self.UpdateCDZoneInfoCon()
						self.UpdateCDDisplay()
						
					SaveGame()
			
			# supply menu active
			elif self.active_menu == 5:
				
				# request resupply
				if key_char == 'r':
					self.ResupplyPlayer()
					self.UpdateTimeWeatherDisplay()
					self.UpdateCDDisplay()
					SaveGame()
			
			# check for end of day
			if campaign.EndOfDay():
				text = 'Your combat day has ended.'
				ShowNotification(text)
				EraseGame()
				DisplayCampaignDaySummary()
				session.exiting_to_main_menu = False
				exit_loop = True
				continue


# Campaign: stores data about a campaign and calendar currently in progress
class Campaign:
	def __init__(self):
		
		pass




		
<<<<<<< HEAD





=======
		# return a random x,y location within a hex console image
		def GetRandomLocation(gen):
			return HEX_CONSOLE_LOCATIONS[libtcod.random_get_int(generator, 0, 10)]
		
		self.hex_consoles = {}
		
		for k, map_hex in scenario.cd_hex.map_hexes.items():
			
			# generate basic hex console image
			# FUTURE: can change colours used here based on environment/weather
			console = libtcod.console_new(7, 5)
			libtcod.console_set_default_background(console, KEY_COLOR)
			libtcod.console_clear(console)
			
			libtcod.console_set_default_foreground(console, HEX_BORDER_COL)
			
			# draw hex border
			for x in [2,3,4]:
				libtcod.console_put_char_ex(console, x, 0, 250,
					HEX_BORDER_COL, OG_BG_COL)
				libtcod.console_put_char_ex(console, x, 4, 250,
					HEX_BORDER_COL, OG_BG_COL)
			for x in [1,5]:
				libtcod.console_put_char_ex(console, x, 1, 250,
					HEX_BORDER_COL, OG_BG_COL)
				libtcod.console_put_char_ex(console, x, 3, 250,
					HEX_BORDER_COL, OG_BG_COL)
			libtcod.console_put_char_ex(console, 0, 2, 250, HEX_BORDER_COL,
				OG_BG_COL)
			libtcod.console_put_char_ex(console, 6, 2, 250, HEX_BORDER_COL,
				OG_BG_COL)
			
			# draw hex interior
			if map_hex.terrain_type == 'pond':
				libtcod.console_set_default_background(console, RIVER_BG_COL)
			else:
				libtcod.console_set_default_background(console, OG_BG_COL)
			libtcod.console_rect(console, 2, 1, 3, 1, True, libtcod.BKGND_SET)
			libtcod.console_rect(console, 1, 2, 5, 1, True, libtcod.BKGND_SET)
			libtcod.console_rect(console, 2, 3, 3, 1, True, libtcod.BKGND_SET)
			
			# add random greebles
			generator = libtcod.random_new_from_seed(map_hex.console_seed)
			
			# open ground
			if map_hex.terrain_type == 'openground':
				if libtcod.random_get_int(generator, 1, 10) == 1:
					(x,y) = GetRandomLocation(generator)
					libtcod.console_put_char_ex(console, x, y, 247,
						HEX_BORDER_COL, OG_BG_COL)
			
			# rough ground
			elif map_hex.terrain_type == 'roughground':
				elements = libtcod.random_get_int(generator, 2, 5)
				while elements > 0:
					(x,y) = GetRandomLocation(generator)
					# skip if a greeble is already there
					if libtcod.console_get_char(console, x, y) != 32:
						continue
					(char, col) = [(249, libtcod.grey), (247, libtcod.sepia)][libtcod.random_get_int(generator, 0, 1)]
					libtcod.console_put_char_ex(console, x, y, char,
						col, OG_BG_COL)
					elements -= 1
			
			# forest
			elif map_hex.terrain_type == 'forest':
				for (x,y) in HEX_CONSOLE_LOCATIONS:
					roll = libtcod.random_get_int(generator, 1, 10)
					if roll == 1:
						char = 32
					elif roll < 9:
						char = 6
					else:
						char = 5
					if libtcod.random_get_int(generator, 1, 8) < 8:
						col = libtcod.Color(0,libtcod.random_get_int(generator, 100, 170),0)
					else:
						col = libtcod.dark_sepia
					libtcod.console_put_char_ex(console, x, y, char, col, OG_BG_COL)
			
			# fields in season
			elif map_hex.terrain_type == 'fields_in_season':
				for (x,y) in HEX_CONSOLE_LOCATIONS:
					c = libtcod.random_get_int(generator, 120, 190)
					libtcod.console_put_char_ex(console, x, y, 177, libtcod.Color(c,c,0), OG_BG_COL)
			
			# pond
			elif map_hex.terrain_type == 'pond':
				elements = libtcod.random_get_int(generator, 3, 6)
				while elements > 0:
					(x,y) = GetRandomLocation(generator)
					if libtcod.console_get_char(console, x, y) != 32:
						continue
					libtcod.console_put_char_ex(console, x, y, 247,
						libtcod.Color(45,0,180), RIVER_BG_COL)
					elements -= 1
			
			# village
			elif map_hex.terrain_type == 'village':
				for (x,y) in HEX_CONSOLE_LOCATIONS:
					roll = libtcod.random_get_int(generator, 1, 10)
					
					# blank
					if roll < 5:
						continue
					# small hut
					if roll < 7:
						char = 250
						fc = libtcod.sepia
						bc = OG_BG_COL
					# haystack
					elif roll < 9:
						char = 4
						fc = libtcod.sepia
						bc = OG_BG_COL
					# building 1
					elif roll == 9:
						char = 249
						fc = libtcod.grey
						bc = libtcod.dark_sepia
					# building 2
					else:
						char = 206
						fc = libtcod.dark_sepia
						bc = libtcod.darkest_grey
					libtcod.console_put_char_ex(console, x, y, char, fc, bc)
			
			libtcod.random_delete(generator)

			libtcod.console_set_key_color(console, KEY_COLOR)
			
			# apply elevation shading
			if map_hex.elevation != 0:
				for y in range(5):
					for x in range(7):
						bg = libtcod.console_get_char_background(console,x,y)
						if bg == KEY_COLOR: continue
						bg = bg * (1.0 + float(map_hex.elevation) * ELEVATION_SHADE)
						libtcod.console_set_char_background(console,x,y,bg)
			
			# save to dictionary
			self.hex_consoles[(map_hex.hx, map_hex.hy)] = console

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
		

# AI: controller for enemy and player-allied units
class AI:
	def __init__(self, owner):
		self.owner = owner
		self.group_leader = None		# if set, unit will mirror actions of this lead unit
		self.disposition = None
	
	# print an AI report re: personnel actions for this unit to the console, used for debugging
	def DoAIActionReport(self):
		text = '\nAI SPY: ' + self.owner.unit_id + ' set to disposition: '
		if self.disposition is None:
			text += 'Wait'
		else:
			text += self.disposition
		if self.owner.dummy:
			text += ' (dummy)'
		print(text)
	
	# do activation for this unit
	def DoActivation(self):
		
		if not self.owner.alive: return
		
		# set as active unit and move to top of hex stack
		scenario.active_unit = self.owner
		self.owner.MoveToTopOfStack()
		UpdateUnitCon()
		UpdateScenarioDisplay()
		libtcod.console_flush()
		
		self.owner.DoPreActivation()
		
		# Step 1: Determine unit disposition for this activation
		
		roll = GetPercentileRoll()
			
		# much more likely to attack if already have an acquired target
		if self.owner.acquired_target is not None:
			roll -= 15.0
		
		# sniper units have separate list of actions
		if self.owner.unit_id == 'Sniper':
			if roll >= 90.0:
				self.disposition = None
			else:
				self.disposition = 'Combat'
		
		# guns have few options for actions
		elif self.owner.GetStat('category') == 'Gun':
			if roll >= 80.0:
				self.disposition = None
			else:
				self.disposition = 'Combat'
		
		elif self.owner.GetStat('category') == 'Infantry':
			if roll <= 65.0:
				self.disposition = 'Combat'
			elif roll <= 80.0:
				if self.owner.pinned:
					self.disposition = 'Combat'
				else:
					self.disposition = 'Movement'
			else:
				self.disposition = None
		
		else:
		
			if roll >= 85.0:
				self.disposition = None
			elif roll <= 55.0:
				self.disposition = 'Combat'
			else:
				if self.owner.pinned:
					self.disposition = 'Combat'
				else:
					self.disposition = 'Movement'
		
		# check for group leader
		if self.group_leader is not None:
			
			# TEMP - player allied unit: combat only
			if self.owner.owning_player == 0:
				self.disposition = 'Combat'
		
		# dummy units never attack
		if self.owner.dummy and self.disposition == 'Combat':
			self.disposition = None
		
		# broken units cannot act
		if self.owner.broken:
			self.disposition = None
		
		# debug override
		if AI_NO_ACTION:
			self.disposition = None
		if AI_SPY:
			self.DoAIActionReport()
		
		
		# Step 2: Determine action to take
		if self.disposition == 'Movement':
			move_done = False
			while not move_done:
				
				animate = False
				dist = GetHexDistance(self.owner.hx, self.owner.hy, scenario.player_unit.hx,
					scenario.player_unit.hy)
				if dist <= 7:
					animate = True
				
				# pick a random direction for move
				dir_list = [0,1,2,3,4,5]
				shuffle(dir_list)
				for direction in dir_list:
					(hx, hy) = GetAdjacentHex(self.owner.hx, self.owner.hy, direction)
					if (hx, hy) not in scenario.cd_hex.map_hexes: continue
					if scenario.cd_hex.map_hexes[(hx, hy)].terrain_type == 'pond':
						continue
					break
				
				if AI_SPY:
					text = ('AI SPY: ' + self.owner.unit_id + ' is moving to ' +
						str(hx) + ',' + str(hy))
					print(text)
				
				# pivot to face new direction if not already
				if self.owner.facing != direction:
					
					change = direction - self.owner.facing
					self.owner.facing = direction
					
					# rotate turret if any
					if self.owner.turret_facing is not None:
						self.owner.turret_facing = self.owner.facing
					
					if animate and self.owner.GetStat('category') != 'Infantry':
						UpdateUnitCon()
						UpdateScenarioDisplay()
						libtcod.console_flush()
						Wait(10)
				
				# do the move
				result = self.owner.MoveForward(False)
				if animate:
					UpdateUnitCon()
					UpdateUnitInfoCon()
					UpdateScenarioDisplay()
					libtcod.console_flush()
					Wait(10)
				
				# if move was not possible, end phase action
				if result == False:
					move_done = True
				# if no more moves, end phase action
				if self.owner.move_finished:
					move_done = True
		
		elif self.disposition == 'Combat':
			if AI_SPY:
				print('\nAI SPY: Starting a combat action for ' + self.owner.unit_id)
			
			animate = False
			dist = GetHexDistance(self.owner.hx, self.owner.hy, scenario.player_unit.hx,
				scenario.player_unit.hy)
			if dist <= 7:
				animate = True
			
			# see if there are any potential targets
			target_list = []
			for unit in scenario.units:
				if not unit.alive: continue
				if unit.owning_player == self.owner.owning_player: continue
				if GetHexDistance(self.owner.hx, self.owner.hy, unit.hx,
					unit.hy) > 6: continue
				if (unit.hx, unit.hy) not in self.owner.fov: continue
				if not unit.known: continue
				target_list.append(unit)
			
			if len(target_list) == 0:
				if AI_SPY:
					print('AI SPY: ' + self.owner.unit_id + ': no possible targets')
				self.owner.DoPostActivation()
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
				if AI_SPY:
					print('AI SPY: ' + self.owner.unit_id + ': no possible attacks on targets')
				self.owner.DoPostActivation()
				return	
						
			# score each attack
			scored_list = []
			for (weapon, target, ammo_type) in attack_list:
				
				# skip small arms attacks on targets that have no chance of effect
				if not target.VulnerableToSAFireFrom(self.owner):
					if weapon.GetStat('type') != 'Gun' and weapon.GetStat('type') not in MG_WEAPONS:
						continue
				
				# determine if a pivot or turret rotation would be required
				pivot_req = None
				turret_rotate_req = None
				
				mount = weapon.GetStat('mount')
				if mount is not None:
					if mount == 'Turret' and self.owner.turret_facing is not None:
						if (target.hx - self.owner.hx, target.hy - self.owner.hy) not in HEXTANTS[self.owner.turret_facing]:
							turret_rotate_req = True
					else:
						if (target.hx - self.owner.hx, target.hy - self.owner.hy) not in HEXTANTS[self.owner.facing]:
							pivot_req = True
				
				# can't pivot if already moved
				if pivot_req:
					if self.owner.move_finished:
						continue
					if self.owner.fired:
						continue
					if self.owner.GetStat('category') == 'Vehicle':
						position = self.owner.PersonnelActionPossible(['Driver', 'Co-Driver'], 'Drive')
						if not position:
							continue
				
				# set ammo type if required
				if ammo_type != '':
					weapon.current_ammo = ammo_type
				
				# calculate odds of attack
				profile = scenario.CalcAttack(self.owner, weapon, target, pivot=pivot_req, turret_rotate=turret_rotate_req)
				
				if profile is None: continue
				
				score = profile['final_chance']
				
				# skip attacks with low chance of success
				if score <= 3.0:
					continue
				
				# improve chance of AP attacks on armoured targets
				if target.GetStat('armour') is not None and ammo_type == 'AP':
					score += 25.0
				
				# FUTURE: modify score by chance of armour penetration if AP
				
				# add to list
				scored_list.append((score, weapon, target, ammo_type))
				
						
			# no possible attacks
			if len(scored_list) == 0:
				if AI_SPY:
					print('AI SPY: ' + self.owner.unit_id + ': no possible scored attacks on targets')
				self.owner.DoPostActivation()
				return
			
			# sort list by score then select best attack
			scored_list.sort(key=lambda x:x[0], reverse=True)
			(score, weapon, target, ammo_type) = scored_list[0]
			
			if AI_SPY:
				print('AI SPY: Best attack with score of ' + str(score) + ': ' + 
					weapon.stats['name'] + '(' + ammo_type + ') against ' + 
					target.unit_id)
			
			# do the attack
			if ammo_type != '':
				weapon.current_ammo = ammo_type
			
			# pivot or rotate turret if needed
			direction = GetDirectionToward(self.owner.hx, self.owner.hy, target.hx,
				target.hy)
			mount = weapon.GetStat('mount')
			if mount is not None:
				changed_facing = False
				if mount == 'Turret' and self.owner.turret_facing is not None:
					if (target.hx - self.owner.hx, target.hy - self.owner.hy) not in HEXTANTS[self.owner.turret_facing]:
						self.owner.turret_facing = direction
						changed_facing = True
						
				else:
					if (target.hx - self.owner.hx, target.hy - self.owner.hy) not in HEXTANTS[self.owner.facing]:
						self.owner.facing = direction
						changed_facing = True
				
				if animate and changed_facing:
					UpdateUnitCon()
					UpdateScenarioDisplay()
					libtcod.console_flush()
					Wait(10)
			
			# do the attack
			result = self.owner.Attack(weapon, target)
			
			if not result:
				if AI_SPY:
					print('AI SPY: ' + self.owner.unit_id + ': could not attack')
					print('AI SPY: ' + scenario.CheckAttack(self.owner, weapon, unit))
		
			if AI_SPY:
				print('AI SPY: Ending combat action for ' + self.owner.unit_id)
		
		# end activation
		self.owner.DoPostActivation()



# Scenario: represents a single battle encounter
class Scenario:
	def __init__(self, cd_hex, source_direction):
		
		# pointer to map hex on campaign day map
		self.cd_hex = cd_hex
		
		# direction from which player entered
		self.source_direction = source_direction
		
		# game turn, active player, and phase tracker
		self.game_turn = {
			'active_player' : 0,		# currently active player number
			'goes_first' : 0,		# which player side acts first in each turn
		}
		
		#self.active_menu = 2			# currently active player menu; 0:none
		self.airsup_menu_active = False		# Air Support sub-menu active
		self.artsup_menu_active = False		# Artillery "
		
		self.units = []				# list of units in the scenario
		self.player_unit = None			# pointer to the player unit
		self.active_unit = None			# currently activated unit
		self.activation_list = [		# activation order for player units, enemy units
			[], []
		]
		
		self.objective_timer = [0, None]	# remaining minutes needed for each player to
							# control objective and gain control of zone
							# if None, not possible
		
		self.objective_timer[0] = self.cd_hex.enemy_organization * OBJECTIVE_CAPTURE_MULTIPLIER
		
		self.finished = False			# have win/loss conditions been met
		self.winner = -1			# player number of scenario winner, -1 if None
		self.win_desc = ''			# description of win/loss conditions met
		
		self.selected_weapon = None		# currently selected weapon on player unit
		
		self.player_target_list = []		# list of possible enemy targets for player unit
		self.player_target = None		# current target of player unit
		self.player_attack_desc = ''		# text description of attack on player target
		
		self.player_target_hex_list = []	# list of possible target hexes for air support, etc.
		self.player_target_hex = None		# pointer to an entire hex being targeted (air support, etc.)
		
		self.player_airsup_failed = False	# flag for a failed air sup request
		self.player_airsup_success = False	# " successful #
		
		self.player_artsup_failed = False	# flag for a failed artillery sup request
		self.player_artsup_success = False	# " successful #
		self.player_artsup_los = 0.0		# LoS modifier for spotting
		
		###### Hex Map and Map Viewport #####
		self.highlighted_hex = None		# currently highlighted map hex
		
		self.map_vp = {}			# dictionary of map viewport hexes and
							#   their corresponding map hexes
		self.vp_hx = 0				# location and facing of center of
		self.vp_hy = 0				#   viewport on map
		self.vp_facing = 0
		
		# dictionary of screen display locations on the VP and their corresponding map hex
		self.hex_map_index = {}
		
		# flag for when scenario has been set up by DoScenario()
		self.init_complete = False
	
	# roll to see if a random event takes place, triggered before start of player activation
	def RandomEventRoll(self):
		
		roll = GetPercentileRoll()
		
		# no event this turn, increase chance
		if roll > campaign_day.random_event_chance:
			campaign_day.random_event_chance += SCENARIO_RANDOM_EVENT_STEP
			return
		
		# roll for type of random event; if event is NA, nothing happens
		roll = GetPercentileRoll()
		
		# debug flag
		if ALWAYS_SNIPER: roll = 30.0
		
		if roll <= 10.0:
			# increase air support level if any
			self.IncreaseSupLevel(True)
		elif roll <= 20.0:
			# increase artillery support if any
			self.IncreaseSupLevel(False)
		elif roll <= 30.0:
			# spawn enemy sniper if one not already in play
			self.SpawnSniper(1)
		else:
			# TEMP: otherwise, no event
			pass
		
		# event triggered, reset event chance
		campaign_day.random_event_chance = SCENARIO_RANDOM_EVENT_CHANCE
		
	# spawn a sniper unit into the game on player_num's side
	# will not spawn if another sniper is already active
	def SpawnSniper(self, player_num):
		
		# check for already existing sniper
		for unit in self.units:
			if unit.unit_id != 'Sniper': continue
			if unit.owning_player != player_num: continue
			return
		
		# determine spawn location
		hex_list = []
		for distance in range(1, 4):
			hex_list.extend(GetHexRing(self.player_unit.hx, self.player_unit.hy, distance))
		shuffle(hex_list)
		
		good_location = False
		for (hx, hy) in hex_list:
			
			# hex is off map
			if (hx, hy) not in self.cd_hex.map_hexes: continue
			
			map_hex = self.cd_hex.map_hexes[(hx, hy)]
			
			# not passable
			if map_hex.terrain_type == 'pond':
				continue
			
			# not enough terrain
			if map_hex.GetTerrainMod() == 0.0:
				continue
			
			good_location = True
			break
		
		if not good_location:
			return
		
		new_unit = Unit('Sniper')
		new_unit.InitScenarioStats()
		new_unit.owning_player = player_num
		new_unit.ai = AI(new_unit)
		new_unit.nation = campaign.stats['enemy_nations'][0]
		new_unit.GenerateNewPersonnel()
		self.units.append(new_unit)
		new_unit.SpawnAt(hx, hy)
		self.activation_list[player_num].append(new_unit)
		
		UpdateUnitCon()
		UpdateUnitInfoCon()
		UpdateScenarioDisplay()
	
	# generate activation order for player units and enemy units
	def GenerateActivationOrder(self):
		for unit in self.units:
			if unit == self.player_unit: continue
			self.activation_list[unit.owning_player].append(unit)
		shuffle(self.activation_list[0])
		shuffle(self.activation_list[1])
	
	# set up map viewport hexes based on viewport center position and facing
	def SetVPHexes(self):
		for (hx, hy) in VP_HEXES:
			map_hx = hx + self.vp_hx
			map_hy = hy + self.vp_hy
			# rotate based on viewport facing
			(hx, hy) = RotateHex(hx, hy, ConstrainDir(0 - self.vp_facing))
			self.map_vp[(hx, hy)] = (map_hx, map_hy)
	
	# center the map viewport on the player unit and rotate so that player unit is facing up
	def CenterVPOnPlayer(self):
		self.vp_hx = self.player_unit.hx
		self.vp_hy = self.player_unit.hy
		self.vp_facing = self.player_unit.facing
	
	# generate enemy units for this scenario
	# TEMP: assumes that enemy are on defense, already in place in area before player arrives
	def SpawnEnemyUnits(self):
		
		# roll for initial number of enemy units to be spawned
		roll = GetPercentileRoll()
		# apply effect of enemy strength in zone
		if self.cd_hex.enemy_strength > 1:
			roll += CD_ENEMY_STRENGTH_EFFECT * (self.cd_hex.enemy_strength - 1)
		if roll > 100.0: roll = 100.0
		
		for enemy_unit_num in range(len(ENEMY_NUMBER_ODDS)):
			if roll <= ENEMY_NUMBER_ODDS[enemy_unit_num]:
				break
			roll -= ENEMY_NUMBER_ODDS[enemy_unit_num]
		
		# add dummy units
		enemy_unit_num += ENEMY_DUMMY_UNITS
		
		# load unit stats for reference from JSON file
		with open(DATAPATH + 'unit_type_defs.json', encoding='utf8') as data_file:
			unit_types = json.load(data_file)
		
		# create a local pointer to current calendar day class odds
		class_odds = campaign.today['enemy_unit_class_odds']
		
		# TODO:
		# once a tank, armoured car, or gun is spawned, set that as the type for
		# this scenario; any further spawns of this class will be of this type
		tank_type = None
		ac_type = None
		gun_type = None
		
		enemy_unit_list = []
		while len(enemy_unit_list) < enemy_unit_num:
			
			# choose a random unit class, rolling against its ubiquity factor
			unit_class = None
			while unit_class is None:
				k, value = choice(list(class_odds.items()))
				if GetPercentileRoll() <= float(value):
					unit_class = k
			
			# TODO: if class unit type has already been set, use that one instead
			
			# choose a random unit type
			type_list = []
			for unit_id in campaign.stats['enemy_unit_list']:
				# unrecognized unit id
				if unit_id not in unit_types: continue
				# not the right class
				if unit_types[unit_id]['class'] != unit_class: continue
				type_list.append(unit_id)
			
			# no units of the correct class found
			if len(type_list) == 0: continue
			
			selected_unit_id = None
			while selected_unit_id is None:
				unit_id = choice(type_list)
				# no ubiquity rating, select automatically
				if 'ubiquity' not in unit_types[unit_id]:
					selected_unit_id = unit_id
					continue
				
				# roll for ubiquity rating
				if GetPercentileRoll() <= float(unit_types[unit_id]['ubiquity']):
					selected_unit_id = unit_id
					continue
			
			# add the final selected unit id
			enemy_unit_list.append(selected_unit_id)
			
			# TODO: set class type if not set already
		
		# spawn each unit in the list in order of these categories
		for category in ['Gun', 'Infantry', 'Vehicle']:
			for unit_id in enemy_unit_list:
				if unit_types[unit_id]['category'] != category: continue
				
				hx = None
				hy = None
				
				# if infantry or gun, use terrain scores to select spawn location
				if category in ['Gun', 'Infantry']:
					
					scored_list = []
					for (map_hx, map_hy), map_hex in self.cd_hex.map_hexes.items():
						scored_list.append((map_hex.scores['total_score'], map_hx, map_hy))
					scored_list = sorted(scored_list, key=lambda x:x[0], reverse=True)
					
					# check locations from best score to worst
					for (score, map_hx, map_hy) in scored_list:
						
						# too close to player
						if GetHexDistance(map_hx, map_hy, self.player_unit.hx, self.player_unit.hy) < ENEMY_SPAWN_MIN_DISTANCE:
							continue
						
						# not passable
						if self.cd_hex.map_hexes[(map_hx, map_hy)].terrain_type == 'pond':
							continue
						
						# stack too large
						if len(self.cd_hex.map_hexes[(map_hx, map_hy)].unit_stack) > 1:
							continue
						
						# good location
						hx = map_hx
						hy = map_hy
						
						break
				
				# if vehicle, use an ideal distance to objective instead
				else:
				
					ideal_distance = 6
				
					for tries in range(300):
						close_enough = False
						
						(hx, hy) = choice(list(self.cd_hex.map_hexes.keys()))
						
						# too close to player
						if GetHexDistance(hx, hy, self.player_unit.hx, self.player_unit.hy) < ENEMY_SPAWN_MIN_DISTANCE:
							continue
						
						# not passable
						if self.cd_hex.map_hexes[(hx, hy)].terrain_type == 'pond':
							continue
						
						# close enough to objective
						if GetHexDistance(hx, hy, 0, 0) <= ideal_distance:
							close_enough = True
							break
						
						if close_enough:
							break
				
				if hx is None and hy is None:
					print('ERROR: Could not find a good location to spawn ' + unit_id)
					continue
				
				# create the unit
				new_unit = Unit(unit_id)
				new_unit.InitScenarioStats()
				new_unit.owning_player = 1
				new_unit.ai = AI(new_unit)
				
				# TEMP
				new_unit.nation = campaign.stats['enemy_nations'][0]
				
				# set facing toward player
				direction = GetDirectionToward(new_unit.hx, new_unit.hy,
					self.player_unit.hx, self.player_unit.hy)
				new_unit.facing = direction
				# unit has rotatable turret
				if 'turret' in new_unit.stats:
					new_unit.turret_facing = direction
				
				new_unit.GenerateNewPersonnel()
				
				# deploy immediately if gun
				if new_unit.GetStat('category') == 'Gun':
					new_unit.deployed = True
				self.units.append(new_unit)
				new_unit.SpawnAt(hx, hy)
				
				# check for hull down status
				new_unit.CheckHullDownGain()
					
		# create dummy units
		unit_list = []
		for unit in self.units:
			if unit.owning_player == 1:
				unit_list.append(unit)
		unit_list = sample(unit_list, ENEMY_DUMMY_UNITS)	
		for unit in unit_list:
			unit.dummy = True

	# do automatic events at the end of a player turn
	def DoEndOfPlayerTurn(self):
		
		# resolve hits on enemy units
		for unit in self.units:
			if unit.owning_player == self.game_turn['active_player']:
				continue
			if not unit.alive:
				continue
			unit.ResolveHits()
		
		# check for win/loss conditions
		if not self.player_unit.alive:
			self.winner = 1
			self.finished = True
			self.win_desc = 'Your tank was destroyed. Final VP: ' + str(campaign.player_vp)
			return
		
		all_enemies_dead = True
		for unit in self.units:
			if unit.owning_player == 1 and unit.alive:
				all_enemies_dead = False
				break
		if all_enemies_dead:
			self.winner = 0
			self.finished = True
			self.win_desc = 'All enemy units in the area were destroyed.'
			return
		
		# check for objective hold
		for player in [0, 1]:
			# player can't win by holding objective
			if scenario.objective_timer[player] is None: continue
			# no units in objective
			map_hex = scenario.cd_hex.map_hexes[(0,0)]
			if len(map_hex.unit_stack) == 0: continue
			# not the right player's unit
			if map_hex.unit_stack[0].owning_player != player: continue
			# player's unit is holding the objective, decrement the timer
			scenario.objective_timer[player] -= 1
		
		# check for objective timer completion
		for player in [0, 1]:
			# player can't win by holding objective
			if scenario.objective_timer[player] is None: continue
			# timer has run out
			if scenario.objective_timer[player] <= 0:
				self.winner = player
				self.finished = True
				if player == 0:
					text = 'You'
				else:
					text = 'The enemy'
				text += ' held the objective and all opposing forces were forced to fall back'
				self.win_desc = text
				return
		
		# turn half over
		if self.game_turn['active_player'] == self.game_turn['goes_first']:
			
			if self.game_turn['goes_first'] == 0:
				self.game_turn['active_player'] = 1
			else:
				self.game_turn['active_player'] = 0
		# end of turn
		else:
			self.game_turn['active_player'] = self.game_turn['goes_first']
		
		# advance campaign clock
		campaign.AdvanceClock(0, 1)
	
	# select the next or previous weapon on the player unit, looping around the list
	def SelectNextWeapon(self, forward):
		
		# no weapons to select
		if len(self.player_unit.weapon_list) == 0: return False
		
		# no weapon selected yet
		if self.selected_weapon is None:
			self.selected_weapon = self.player_unit.weapon_list[0]
			return True
		
		i = self.player_unit.weapon_list.index(self.selected_weapon)
		
		if forward:
			i+=1
		else:
			i-=1
		
		if i < 0:
			self.selected_weapon = self.player_unit.weapon_list[-1]
		elif i > len(self.player_unit.weapon_list) - 1:
			self.selected_weapon = self.player_unit.weapon_list[0]
		else:
			self.selected_weapon = self.player_unit.weapon_list[i]
		return True
	
	# rebuild the list of all enemy units that could be targeted by the player unit
	def RebuildPlayerTargetList(self):
		self.player_target_list = []
		
		for unit in self.units:
			if not unit.alive: continue
			if unit.owning_player == 0: continue
			
			# target must be on VP
			if unit.vp_hx is None or unit.vp_hy is None:
				continue
			
			if (unit.hx, unit.hy) not in self.player_unit.fov: continue
			self.player_target_list.append(unit)
		
		# clear player target if no longer possible
		if self.player_target is not None:
			if self.player_target not in self.player_target_list:
				self.player_target = None
	
	# select the next enemy target for the player unit, looping around the list
	def SelectNextTarget(self, forward):
		
		# no targets possible
		if len(self.player_target_list) == 0: return False
		
		if self.player_target is None:
			self.player_target = self.player_target_list[0]
		else:
			i = self.player_target_list.index(self.player_target)
			
			if forward:
				i+=1
			else:
				i-=1
			
			if i < 0:
				self.player_target = self.player_target_list[-1]
			elif i > len(self.player_target_list) - 1:
				self.player_target = self.player_target_list[0]
			else:
				self.player_target = self.player_target_list[i]
	
		# TODO: see if target is valid?
		self.player_attack_desc = self.CheckAttack(self.player_unit,
			self.selected_weapon, self.player_target)
		
		# move target to top of stack
		self.player_target.MoveToTopOfStack()
		
		return True
	
	# rebuild the list of possible hex targets for player unit air/arty support attack
	def RebuildTargetHexList(self):
		self.player_target_hex_list = []
		for unit in self.units:
			if not unit.alive: continue
			if unit.owning_player == 0: continue
			if unit.vp_hx is None or unit.vp_hy is None: continue
			if (unit.hx, unit.hy) in self.player_target_hex_list: continue
			if (unit.hx, unit.hy) not in scenario.player_unit.fov: continue
			self.player_target_hex_list.append((unit.hx, unit.hy))
		
		# reset selected hex if no longer possible
		#if self.player_target_hex is not None:
		#	if self.player_target_hex not in self.player_target_hex_list:
		#		self.player_target_hex = None
	
	# change selected target hex
	def SelectNextTargetHex(self, reverse):
		
		# no target hexes possible
		if len(self.player_target_hex_list) == 0: return
		
		# no hex selected yet
		if self.player_target_hex is None:
			if reverse:
				self.player_target_hex = self.player_target_hex_list[-1]
			else:
				self.player_target_hex = self.player_target_hex_list[0]
			return
		
		# select next/previous hex and loop around if required
		i = self.player_target_hex_list.index(self.player_target_hex)
		if reverse:
			i-=1
		else:
			i+=1
		if i < 0:
			self.player_target_hex = self.player_target_hex_list[-1]
		elif i > len(self.player_target_hex_list) - 1:
			self.player_target_hex = self.player_target_hex_list[0]
		else:
			self.player_target_hex = self.player_target_hex_list[i]
	
	# request an air support attack against the target hex location
	def RequestAirSup(self):
		# no hex selected
		if self.player_target_hex is None: return False
		# already failed this turn
		if self.player_airsup_failed: return False
		
		# try to set crew action
		if not self.player_unit.SetPersonnelAction(['Commander', 'Commander/Gunner'], 'Request Support'):
			return False
		
		# do support roll
		roll = GetPercentileRoll()
		
		# debug flag
		if PLAYER_ALWAYS_HITS: roll = 10.0
		
		if roll > campaign_day.air_support_level:
			self.player_airsup_failed = True
			text = 'Unable to respond to air support request.'
			Message(text, no_log=True)
			return True
		
		# reduce support level by one step
		campaign_day.ReduceAirSupLevel()
		
		# set scenario flag for next player unit activation
		self.player_airsup_success = True
		
		# display and record message
		text = 'Air support request was successful, air support is now inbound.'
		Message(text)
		
		return True
	
	# do an air support attack against the selected hex target
	def DoAirSupportAttack(self):
		
		# roll for number of planes
		roll = libtcod.random_get_int(0, 1, 6)
		if roll <= 2:
			num_planes = 1
		elif roll <= 5:
			num_planes = 2
		else:
			num_planes = 3
		
		# determine type of plane
		plane_id = choice(campaign.stats['player_air_support'])
		
		# display message
		text = str(num_planes) + ' ' + plane_id + ' arrive'
		if num_planes == 1: text += 's'
		text += ' for an attack run'
		Message(text, no_log=True)
		
		# find target hex on viewport
		for (vp_hx, vp_hy) in VP_HEXES:
			if self.map_vp[(vp_hx, vp_hy)] == self.player_target_hex:
				break
		(x2,y2) = PlotHex(vp_hx, vp_hy)
		
		# record target hex coordinates then clear it from the scenario object hex
		(hx, hy) = self.player_target_hex
		self.player_target_hex = None
		UpdateUnitCon()
		UpdateScenarioDisplay()
		
		# translate from vp console into screen coordinates
		x2 += 30
		y2 += 4
		
		# determine attack direction and starting position
		x = x2
		if y2 <= 26:
			y1 = y2 + 20
			if y1 > 53: y1 = 53
			y2 += 1
			direction = -1
		else:
			y1 = y2 - 20
			if y1 < 5: y1 = 5
			y2 -= 3
			direction = 1
		
		# create and draw plane console
		temp_con = libtcod.console_new(3, 3)
		libtcod.console_set_default_background(temp_con, libtcod.black)
		libtcod.console_set_default_foreground(temp_con, libtcod.light_grey)
		libtcod.console_clear(temp_con)
		
		libtcod.console_put_char(temp_con, 0, 1, chr(196))
		libtcod.console_put_char(temp_con, 1, 1, chr(197))
		libtcod.console_put_char(temp_con, 2, 1, chr(196))
		if direction == -1:
			libtcod.console_put_char(temp_con, 1, 2, chr(193))
		else:
			libtcod.console_put_char(temp_con, 1, 0, chr(194))
		
		PlaySoundFor(None, 'plane_incoming')
		
		# animate plane movement toward target hex
		for y in range(y1, y2, direction):
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, x, y, 1.0, 0.0)
			libtcod.console_flush()
			Wait(8)
		
		PlaySoundFor(None, 'stuka_divebomb')
		
		# bomb animation here
		for i in range(24):
			col = choice([libtcod.red, libtcod.yellow, libtcod.black])
			libtcod.console_set_default_foreground(0, col)
			libtcod.console_put_char(0, x2+1, y2-1, 42)
			libtcod.console_flush()
			Wait(4)
		libtcod.console_set_default_foreground(0, libtcod.white)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		
		# wait for sound effect to finish
		if config['ArmCom2'].getboolean('sounds_enabled'):
			Wait(140)
		
		# do attack
		self.DoAirAttack(hx, hy, num_planes, plane_id)
		
		Wait(30)
		
		# clear plane from screen and delete console
		UpdateScenarioDisplay()
		libtcod.console_flush()
		del temp_con
	
	
	# do an air attack on the target hex
	def DoAirAttack(self, hx, hy, num_planes, plane_id):
		
		# get target map hex
		map_hex = self.cd_hex.map_hexes[(hx, hy)]
		
		# no target possible
		if len(map_hex.unit_stack) == 0:
			text = 'No possible targets, calling off attack run'
			Message(text, hx=hx, hy=hy, no_log=True)
			return
		
		# create plane units
		unit_list = []
		for i in range(num_planes):
			unit_list.append(Unit(plane_id))
		
		# determine calibre for bomb attack
		for weapon in unit_list[0].weapon_list:
			if weapon.stats['name'] == 'Bombs':
				bomb_calibre = int(weapon.stats['calibre'])
				break
		
		# determine effective fp
		for (calibre, effective_fp) in HE_FP_EFFECT:
			if calibre <= bomb_calibre:
				break
		
		# get target hex terrain modifier
		terrain_mod = map_hex.GetTerrainMod()
		
		results = False
		
		# do one attack per plane
		for unit in unit_list:
			
			# no more targets possible
			if len(map_hex.unit_stack) == 0:
				break
			
			# select a random target within the hex
			target = choice(map_hex.unit_stack)
			
			# calculate basic to-hit score required
			if not target.known:
				chance = PF_BASE_CHANCE[0][1]
			else:
				if target.GetStat('category') == 'Vehicle':
					chance = PF_BASE_CHANCE[0][0]
				else:
					chance = PF_BASE_CHANCE[0][1]
			
			# apply terrain modifier for target hex
			chance -= terrain_mod
			
			# air burst modifier
			if map_hex.terrain_type == 'forest' and target.GetStat('category') != 'Vehicle':
				chance += 20.0
			
			# target size
			size_class = target.GetStat('size_class')
			if size_class is not None:
				if size_class != 'Normal':
					chance += PF_SIZE_MOD[size_class]
			
			chance = RestrictChance(chance)
			
			# do attack roll
			roll = GetPercentileRoll()
			
			# no hit
			if roll > chance:
				continue
			
			# hit
			results = True
			
			# infantry or gun target
			if target.GetStat('category') in ['Infantry', 'Gun']:
				
				# critical hit modifier
				if roll <= 3.0:
					target.fp_to_resolve += (effective_fp * 2)
				else:
					target.fp_to_resolve += effective_fp
				
				if not target.known:
					target.hit_by_fp = 2
				
				text = target.GetName() + ' was hit by air attack'
				Message(text, hx=target.hx, hy=target.hy)
			
			# vehicle hit
			elif target.GetStat('category') == 'Vehicle':
				
				# determine location hit - use side locations and modify later
				# for aerial attack
				if GetPercentileRoll() <= 50.0:
					hit_location = 'hull_side'
				else:
					hit_location = 'turret_side'
				
				# determine base penetration chance
				for (calibre, chance) in HE_AP_CHANCE:
					if calibre <= bomb_calibre:
						break
				
				# TODO: direct hit vs. near miss
				
				# target armour modifier
				armour = target.GetStat('armour')
				if armour is not None:
					if armour[hit_location] != '-':
						target_armour = int(armour[hit_location])
						if target_armour >= 0:
						
							modifier = -9.0
							for i in range(target_armour - 1):
								modifier = modifier * 1.8
							
							chance += modifier
							
							# apply critical hit modifier if any
							if roll <= 3.0:
								modifier = round(abs(modifier) * 0.8, 2)
								chance += modifier
				
				# calculate final chance
				chance = RestrictChance(chance)
				
				# do AP roll
				roll = GetPercentileRoll()
				
				# no penetration
				if roll > chance:
					text = target.GetName() + ' was unaffected by air attack'
					Message(text, hx=target.hx, hy=target.hy)
					continue
				
				# penetrated
				target.DestroyMe()
				text = target.GetName() + ' was destroyed by air attack'
				Message(text, hx=target.hx, hy=target.hy)
		
		if not results:
			Message('Attack run had no effect')
		
		# clear selected target
		self.player_target_hex = None
	
	
	# request an artillery support attack against the target hex location
	def RequestArtySup(self):
		# no hex selected
		if self.player_target_hex is None: return False
		# already failed this turn
		if self.player_artsup_failed: return False
		
		# try to set crew action
		if not self.player_unit.SetPersonnelAction(['Commander', 'Commander/Gunner'], 'Request Support'):
			return False
		
		# do support roll
		roll = GetPercentileRoll()
		
		# debug flag
		if PLAYER_ALWAYS_HITS: roll = 10.0
		
		if roll > campaign_day.arty_support_level:
			self.player_artsup_failed = True
			text = 'Unable to respond to artillery support request.'
			Message(text, no_log=True)
			return True
		
		# reduce support level by one step
		campaign_day.ReduceArtSupLevel()
		
		# set scenario flag for next player unit activation
		self.player_artsup_success = True
		
		# record LoS modifier from player
		(hx2, hy2) = self.player_target_hex
		self.player_artsup_los = GetLoS(self.player_unit.hx, self.player_unit.hy,
			hx2, hy2)
		
		# display and record message
		text = 'Artillery support request was successful, spotting rounds inbound.'
		Message(text, no_log=True)
		
		return True
	
	
	# attempt an artillery attack against the selected hex target
	def DoArtSupportAttack(self):
		
		# find target hex on viewport
		for (vp_hx, vp_hy) in VP_HEXES:
			if self.map_vp[(vp_hx, vp_hy)] == self.player_target_hex:
				break
		
		# bonus for spotting round falling in player FoV
		fov_bonus = False
		
		# fire spotting rounds
		for i in range(3):
			(target_vp_hx, target_vp_hy) = (vp_hx, vp_hy)
			chance = ARTY_BASE_SPOT_CHANCE - self.player_artsup_los
			chance = RestrictChance(chance)
			if fov_bonus: chance += 15.0
			roll = GetPercentileRoll()
			
			# did not hit target, pick a random adjacent vp hex on vp
			if roll > chance:
				for i in range(300):
					direction = libtcod.random_get_int(0, 0, 5)
					(target_vp_hx, target_vp_hy) = GetAdjacentHex(target_vp_hx, target_vp_hy, direction)
					if (target_vp_hx, target_vp_hy) in VP_HEXES: break
			
			# plot screen location of hit hex and randomize animation location within hex
			(x,y) = PlotHex(target_vp_hx, target_vp_hy)
			x2 = x + 30 + libtcod.random_get_int(0, 0, 2)
			y2 = y + 3 + libtcod.random_get_int(0, 0, 2)
			
			# play sound
			PlaySoundFor(None, 'he_explosion')
			
			# show spotting round animation
			for i in range(24):
				col = choice([libtcod.red, libtcod.yellow, libtcod.black])
				libtcod.console_set_default_foreground(0, col)
				libtcod.console_put_char(0, x2, y2, 42)
				libtcod.console_flush()
				Wait(4)
			libtcod.console_set_default_foreground(0, libtcod.white)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			
			# break if hit
			if (target_vp_hx, target_vp_hy) == (vp_hx, vp_hy):
				break
			
			# check for FoV bonus
			fov_bonus = False
			if self.map_vp[(target_vp_hx, target_vp_hy)] in self.player_unit.fov:
				fov_bonus = True
				
		# was not able to range in
		if (target_vp_hx, target_vp_hy) != (vp_hx, vp_hy):
			text = 'Artillery not able to range in, will attempt again.'
			Message(text, no_log=True)
			return
		
		# set flag so that it doesn't try to range in again next turn
		self.player_artsup_success = False
		
		# spawn gun unit and determine effective FP
		unit_id = choice(campaign.stats['player_arty_support'])
		gun_unit = Unit(unit_id)
		gun_calibre = int(gun_unit.weapon_list[0].GetStat('calibre'))
		
		# determine effective fp and base AP chance for gun
		for (calibre, effective_fp) in HE_FP_EFFECT:
			if calibre <= gun_calibre:
				break
		for (calibre, ap_chance) in HE_AP_CHANCE:
			if calibre <= gun_calibre:
				break
		
		text = 'Artillery ranged in, ' + unit_id + ' battery firing for effect.'
		Message(text, no_log=True)
		
		# do attack animation
		(x,y) = PlotHex(vp_hx, vp_hy)
		for i in range(6):
			x2 = x + 30 + libtcod.random_get_int(0, 0, 2)
			y2 = y + 3 + libtcod.random_get_int(0, 0, 2)
			PlaySoundFor(None, 'he_explosion')
			
			# show spotting round animation
			for i in range(12):
				col = choice([libtcod.red, libtcod.yellow, libtcod.black])
				libtcod.console_set_default_foreground(0, col)
				libtcod.console_put_char(0, x2, y2, 42)
				libtcod.console_flush()
				Wait(2)
			libtcod.console_set_default_foreground(0, libtcod.white)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
		
		# get units in target map hex and shuffle a local copy of the list
		map_hex = self.cd_hex.map_hexes[self.player_target_hex]
		unit_list = map_hex.unit_stack[:]
		shuffle(unit_list)
		
		results = False
		for target in unit_list:
			
			# calculate base effect chance
			if target.GetStat('category') == 'Vehicle':
				chance = VEH_FP_BASE_CHANCE
			else:
				chance = INF_FP_BASE_CHANCE
			for i in range(2, effective_fp + 1):
				chance += FP_CHANCE_STEP * (FP_CHANCE_STEP_MOD ** (i-1)) 
			
			# target is infantry and moved in open
			terrain_mod = map_hex.GetTerrainMod()
			if terrain_mod == 0.0 and target.moved and target.GetStat('category') == 'Infantry':
				chance += (chance / 2.0)
			
			# air burst modifier
			if map_hex.terrain_type == 'forest' and target.GetStat('category') != 'Vehicle':
				chance += (chance / 2.0)
			
			chance = round(chance, 2)
			roll = GetPercentileRoll()
			
			# no effect
			if roll > chance:
				continue
			
			results = True
			
			# infantry or gun target
			if target.GetStat('category') in ['Infantry', 'Gun']:
			
				# critical hit modifier
				if roll <= 3.0:
					target.fp_to_resolve += (effective_fp * 2)
				else:
					target.fp_to_resolve += effective_fp
				
				if not target.known:
					target.hit_by_fp = 2
				
				text = target.GetName() + ' was hit by artillery attack'
				Message(text, hx=target.hx, hy=target.hy)
			
			# vehicle hit
			elif target.GetStat('category') == 'Vehicle':
				
				# determine location hit - use side locations and modify later
				# for aerial attack
				if GetPercentileRoll() <= 50.0:
					hit_location = 'hull_side'
				else:
					hit_location = 'turret_side'
				
				# TODO: direct hit vs. near miss
				
				# start with base AP chance
				chance = ap_chance
				
				# apply target armour modifier
				armour = target.GetStat('armour')
				if armour is not None:
					if armour[hit_location] != '-':
						target_armour = int(armour[hit_location])
						if target_armour >= 0:
						
							modifier = -9.0
							for i in range(target_armour - 1):
								modifier = modifier * 1.8
							
							chance += modifier
							
							# apply critical hit modifier if any
							if roll <= 3.0:
								modifier = round(abs(modifier) * 0.8, 2)
								chance += modifier
				
				# calculate final chance of AP
				chance = RestrictChance(chance)
				
				# do AP roll
				roll = GetPercentileRoll()
				
				# no penetration
				if roll > chance:
					text = target.GetName() + ' was hit by artillery attack but is unharmed.'
					Message(text, hx=target.hx, hy=target.hy)
					if not target.known:
						target.hit_by_fp = 2
					continue
				
				# penetrated
				target.DestroyMe()
				text = target.GetName() + ' was destroyed by artillery attack'
				Message(text, hx=target.hx, hy=target.hy)
			
		if not results:
			(hx, hy) = self.player_target_hex
			text = 'Artillery attack had no effect'
			Message(text, hx=hx, hy=hy)
		
		# clear selected target
		self.player_target_hex = None
		
	
	# calculate the odds of success of a ranged attack, returns an attack profile
	# if pivot or turret_rotate are set to True or False, will override
	# any actual attacker status
	def CalcAttack(self, attacker, weapon, target, pivot=None, turret_rotate=None):
		
		profile = {}
		profile['attacker'] = attacker
		profile['weapon'] = weapon
		profile['ammo_type'] = weapon.current_ammo
		profile['target'] = target
		profile['result'] = ''		# placeholder for text rescription of result
		
		# determine attack type: point or area; AP results are handled by CalcAP()
		
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
		# [maximum displayable modifier description length is 17 characters]
		
		modifier_list = []
		
		# point fire attacks (eg. large guns)
		if profile['type'] == 'Point Fire':
			
			# calculate base success chance
			
			# can fire HE at unknown targets
			if not target.known:
				# use infantry chance as base chance
				profile['base_chance'] = PF_BASE_CHANCE[distance][1]
			else:
				if target.GetStat('category') == 'Vehicle':
					profile['base_chance'] = PF_BASE_CHANCE[distance][0]
				else:
					profile['base_chance'] = PF_BASE_CHANCE[distance][1]
		
			# calculate modifiers and build list of descriptions
			
			# description max length is 19 chars
			
			# attacker moved
			if attacker.moved:
				modifier_list.append(('Attacker Moved', -60.0))
			
			# attacker pivoted
			elif attacker.facing != attacker.previous_facing:
				modifier_list.append(('Attacker Pivoted', -40.0))

			# weapon turret rotated
			elif weapon.GetStat('mount') == 'Turret' and attacker.turret_facing is not None:
				if attacker.turret_facing != attacker.previous_turret_facing:
					modifier_list.append(('Turret Rotated', -20.0))
			
			# attacker pinned
			if attacker.pinned:
				modifier_list.append(('Attacker Pinned', -60.0))
			
			# LoS modifier
			los = GetLoS(attacker.hx, attacker.hy, target.hx, target.hy)
			if los > 0.0:
				modifier_list.append(('Terrain', 0.0 - los))
			
			# elevation
			elevation1 = self.cd_hex.map_hexes[(attacker.hx, attacker.hy)].elevation
			elevation2 = self.cd_hex.map_hexes[(target.hx, target.hy)].elevation
			if elevation2 > elevation1:
				# within one elevation step
				if elevation2 - elevation1 == 1:
					modifier_list.append(('Height Advantage', -10.0))
				# two or more elevation steps
				else:
					modifier_list.append(('Height Advantage', -20.0))
			
			# unknown target
			if not target.known:
				modifier_list.append(('Unknown Target', -10.0))
			
			# known target
			else:
			
				# acquired target
				if not attacker.moved and attacker.facing == attacker.previous_facing and attacker.acquired_target is not None:
					(ac_target, level) = attacker.acquired_target
					if ac_target == target:
						if not level:
							mod = 10.0
						else:
							mod = 20.0
						modifier_list.append(('Acquired Target', mod))
				
				# target vehicle moved
				if target.moved and target.GetStat('category') == 'Vehicle':
					modifier_list.append(('Target Moved', -30.0))
				
				# target size
				size_class = target.GetStat('size_class')
				if size_class is not None:
					if size_class != 'Normal':
						text = size_class + ' Target'
						mod = PF_SIZE_MOD[size_class]
						modifier_list.append((text, mod))
			
			# long / short-barreled gun
			long_range = weapon.GetStat('long_range')
			if long_range is not None and distance >= 3:
				if long_range == 'S':
					modifier_list.append(('Short Gun', -12.0))
				elif long_range == 'L':
					modifier_list.append(('Long Gun', 12.0))
		
		# area fire
		elif profile['type'] == 'Area Fire':
			
			# calculate base FP
			fp = int(weapon.GetStat('fp'))
			
			# close range multiplier
			if distance == 1:
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
			
			# attacker moved
			if attacker.moved:
				mod = round(base_chance / 2.0, 2)
				modifier_list.append(('Attacker Moved', 0.0 - mod))
			
			# attacker pivoted
			elif attacker.facing != attacker.previous_facing:
				mod = round(base_chance / 3.0, 2)
				modifier_list.append(('Attacker Pivoted', 0.0 - mod))

			# weapon turret rotated
			elif weapon.GetStat('mount') == 'Turret' and attacker.turret_facing is not None:
				if attacker.turret_facing != attacker.previous_turret_facing:
					mod = round(base_chance / 4.0, 2)
					modifier_list.append(('Turret Rotated', 0.0 - mod))
			
			# attacker pinned
			if attacker.pinned:
				mod = round(base_chance / 2.0, 2)
				modifier_list.append(('Attacker Pinned', 0.0 - mod))
			
			# close range
			if distance == 1:
				modifier_list.append(('Close Range', base_chance))
			
			# LoS modifier
			los = GetLoS(attacker.hx, attacker.hy, target.hx, target.hy)
			if los > 0.0:
				modifier_list.append(('Terrain', 0.0 - los))
			
			# elevation
			elevation1 = self.cd_hex.map_hexes[(attacker.hx, attacker.hy)].elevation
			elevation2 = self.cd_hex.map_hexes[(target.hx, target.hy)].elevation
			if elevation2 > elevation1:
				# within one elevation step
				if elevation2 - elevation1 == 1:
					modifier_list.append(('Height Advantage', -10.0))
				# two or more elevation steps
				else:
					modifier_list.append(('Height Advantage', -20.0))
			
			if not target.known:
				modifier_list.append(('Unknown Target', -10.0))
			else:
			
				# target is infantry and moved in open
				terrain_mod = self.cd_hex.map_hexes[(target.hx, target.hy)].GetTerrainMod()
				if terrain_mod == 0.0 and target.moved and target.GetStat('category') == 'Infantry':
					mod = round(base_chance / 2.0, 2)
					modifier_list.append(('Exposed Infantry', mod))
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
				
		# Commander directing fire
		position = attacker.CheckPersonnelAction(['Commander'], 'Direct Fire')
		if position is not False:
			mod = 10.0 + (float(position.crewman.traits['Knowledge']) * DIRECT_FIRE_MOD)
			#print('DEBUG: Modified to-hit based on commander Knowledge of ' + str(position.crewman.traits['Knowledge']))
			modifier_list.append(('Fire Direction', mod))
		
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
	
	# calculate an armour penetration attempt
	# also determines location hit on target
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
			if distance <= 1:
				if calibre <= 57:
					modifier_list.append(('Close Range', 7.0))
			elif distance == 5:
				modifier_list.append(('Medium Range', -7.0))
			elif distance == 6:
				if calibre < 65:
					modifier_list.append(('Long Range', -18.0))
				else:
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
		if profile['attacker'] != self.player_unit and profile['target'] != self.player_unit:
			return
		
		libtcod.console_clear(attack_con)
		
		# display the background outline
		libtcod.console_blit(LoadXP('attack_bkg.xp'), 0, 0, 0, 0, attack_con, 0, 0)
		
		# window title
		libtcod.console_set_default_background(attack_con, libtcod.darker_blue)
		libtcod.console_rect(attack_con, 1, 1, 24, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(attack_con, libtcod.black)
		
		# set flags on whether attacker/target is known to player
		
		attacker_known = True
		if profile['attacker'].owning_player == 1 and not profile['attacker'].known:
			attacker_known = False
		target_known = True
		if profile['target'].owning_player == 1 and not profile['target'].known:
			target_known = False
		
		if profile['type'] == 'ap':
			text = 'Armour Penetration'
		else:
			text = 'Ranged Attack'
		ConsolePrintEx(attack_con, 13, 1, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		
		# attacker portrait if any
		if profile['type'] in ['Point Fire', 'Area Fire']:
			
			libtcod.console_set_default_background(attack_con, PORTRAIT_BG_COL)
			libtcod.console_rect(attack_con, 1, 2, 24, 8, False, libtcod.BKGND_SET)
		
			# FUTURE: store portraits for every active unit type in session object
			if attacker_known:
				portrait = profile['attacker'].GetStat('portrait')
				if portrait is not None:
					libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, attack_con, 1, 2)
		
		# attack description
		if profile['type'] == 'ap':
			text1 = profile['target'].GetName()
			if attacker_known:
				text2 = 'hit by ' + profile['weapon'].GetStat('name')
			else:
				text2 = 'hit'
			if profile['ammo_type'] is not None:
				text2 += ' (' + profile['ammo_type'] + ')'
			text3 = 'in ' + profile['location_desc']
		else:
			text1 = profile['attacker'].GetName()
			if attacker_known:
				text2 = 'firing ' + profile['weapon'].GetStat('name') + ' at'
			else:
				text2 = 'firing at'
			text3 = profile['target'].GetName()
			
		ConsolePrintEx(attack_con, 13, 10, libtcod.BKGND_NONE,
			libtcod.CENTER, text1)
		ConsolePrintEx(attack_con, 13, 11, libtcod.BKGND_NONE,
			libtcod.CENTER, text2)
		ConsolePrintEx(attack_con, 13, 12, libtcod.BKGND_NONE,
			libtcod.CENTER, text3)
		
		# target portrait if any
		libtcod.console_set_default_background(attack_con, PORTRAIT_BG_COL)
		libtcod.console_rect(attack_con, 1, 13, 24, 8, False, libtcod.BKGND_SET)
		
		# FUTURE: store portraits for every active unit type in session object
		if target_known:
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
		ConsolePrintEx(attack_con, 13, 23, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		text = str(profile['base_chance']) + '%%'
		ConsolePrintEx(attack_con, 13, 24, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		
		# modifiers
		libtcod.console_set_default_background(attack_con, libtcod.darker_blue)
		libtcod.console_rect(attack_con, 1, 27, 24, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(attack_con, libtcod.black)
		ConsolePrintEx(attack_con, 13, 27, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Modifiers')
		
		y = 29
		if len(profile['modifier_list']) == 0:
			ConsolePrintEx(attack_con, 13, y, libtcod.BKGND_NONE,
				libtcod.CENTER, 'None')
		else:
			for (desc, mod) in profile['modifier_list']:
				# max displayable length is 17 chars
				ConsolePrint(attack_con, 2, y, desc[:17])
				
				if mod > 0.0:
					col = libtcod.green
					text = '+'
				else:
					col = libtcod.red
					text = ''
				
				text += str(mod)
				
				libtcod.console_set_default_foreground(attack_con, col)
				ConsolePrintEx(attack_con, 24, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, text)
				libtcod.console_set_default_foreground(attack_con, libtcod.white)
				
				y += 1
		
		# display final chance
		libtcod.console_set_default_background(attack_con, libtcod.darker_blue)
		libtcod.console_rect(attack_con, 1, 43, 24, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(attack_con, libtcod.black)
		ConsolePrintEx(attack_con, 13, 43, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Final Chance')
		
		# display chance graph
		if profile['type'] == 'Area Fire':
			# area fire has partial, full, and critical outcomes possible
			
			# no effect
			libtcod.console_set_default_background(attack_con, libtcod.red)
			libtcod.console_rect(attack_con, 1, 46, 24, 3, False, libtcod.BKGND_SET)
			
			# partial effect
			libtcod.console_set_default_background(attack_con, libtcod.darker_green)
			x = int(ceil(24.0 * profile['final_chance'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			if profile['final_chance'] > profile['full_effect']:
				ConsolePrintEx(attack_con, 23, 46, libtcod.BKGND_NONE,
					libtcod.RIGHT, 'PART')
				text = str(profile['final_chance']) + '%%'
				ConsolePrintEx(attack_con, 23, 47, libtcod.BKGND_NONE,
					libtcod.RIGHT, text)
			
			# full effect
			libtcod.console_set_default_background(attack_con, libtcod.green)
			x = int(ceil(24.0 * profile['full_effect'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			if profile['full_effect'] > profile['critical_effect']:
				ConsolePrintEx(attack_con, 13, 46, libtcod.BKGND_NONE,
					libtcod.CENTER, 'FULL')
				text = str(profile['full_effect']) + '%%'
				ConsolePrintEx(attack_con, 13, 47, libtcod.BKGND_NONE,
					libtcod.CENTER, text)
			
			# critical effect
			libtcod.console_set_default_background(attack_con, libtcod.blue)
			x = int(ceil(24.0 * profile['critical_effect'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			ConsolePrint(attack_con, 2, 46, 'CRIT')
			text = str(profile['critical_effect']) + '%%'
			ConsolePrint(attack_con, 2, 47, text)
			
		else:
			
			# miss
			libtcod.console_set_default_background(attack_con, libtcod.red)
			libtcod.console_rect(attack_con, 1, 46, 24, 3, False, libtcod.BKGND_SET)
			
			# hit
			x = int(ceil(24.0 * profile['final_chance'] / 100.0))
			libtcod.console_set_default_background(attack_con, libtcod.green)
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			# critical hit band
			libtcod.console_set_default_foreground(attack_con, libtcod.blue)
			for y in range(46, 49):
				libtcod.console_put_char(attack_con, 1, y, 221)
			
			# critical miss band
			libtcod.console_set_default_foreground(attack_con, libtcod.dark_grey)
			for y in range(46, 49):
				libtcod.console_put_char(attack_con, 24, y, 222)
		
			libtcod.console_set_default_foreground(attack_con, libtcod.white)
			libtcod.console_set_default_background(attack_con, libtcod.black)
		
			text = str(profile['final_chance']) + '%%'
			ConsolePrintEx(attack_con, 13, 47, libtcod.BKGND_NONE,
				libtcod.CENTER, text)
		
		# display prompts
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		ConsolePrint(attack_con, 6, 57, 'Tab')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		ConsolePrint(attack_con, 12, 57, 'Continue')
		
		# blit the finished console to the screen
		libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
	
	# do a roll, animate the attack console, and display the results
	# returns an modified attack profile
	def DoAttackRoll(self, profile):
		
		# check to see if this weapon maintains Rate of Fire
		def CheckRoF(profile):
			
			# guns must have a Loader active
			if profile['weapon'].GetStat('type') == 'Gun':
				if not profile['attacker'].CheckPersonnelAction(['Loader'], 'Reload'):
					return False
				
				# guns must also have at least one shell of the current type available
				if profile['weapon'].current_ammo is not None:
					if profile['weapon'].ammo_stores[profile['weapon'].current_ammo] == 0:
						return False			
			
			base_chance = float(profile['weapon'].GetStat('rof'))
			roll = GetPercentileRoll()
			
			if roll <= base_chance:
				return True
			return False
		
		# don't animate percentage rolls if player is not involved
		if profile['attacker'] != self.player_unit and profile['target'] != self.player_unit:
			roll = GetPercentileRoll()
		else:
			for i in range(6):
				roll = GetPercentileRoll()
				
				# check for debug flag
				if profile['attacker'] == self.player_unit and PLAYER_ALWAYS_HITS:
					roll = 2.0
				
				# clear any previous text
				ConsolePrintEx(attack_con, 13, 49, libtcod.BKGND_NONE,
					libtcod.CENTER, '      ')
				
				text = str(roll) + '%%'
				ConsolePrintEx(attack_con, 13, 49, libtcod.BKGND_NONE,
					libtcod.CENTER, text)
				libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
				libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
				libtcod.console_flush()
				Wait(15)
		
		# record the final roll in the attack profile
		profile['roll'] = roll
			
		# determine location hit on target (not always used)
		location_roll = GetPercentileRoll()
		# apply modifier if target is higher elevation
		elevation1 = self.cd_hex.map_hexes[(profile['attacker'].hx, profile['attacker'].hy)].elevation
		elevation2 = self.cd_hex.map_hexes[(profile['target'].hx, profile['target'].hy)].elevation
		if elevation1 < elevation2:
			location_roll -= 10.0
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
		# FUTURE: AI will check for RoF too
		if profile['attacker'] != self.player_unit and profile['target'] != self.player_unit:
			return profile
		
		ConsolePrintEx(attack_con, 13, 51, libtcod.BKGND_NONE,
			libtcod.CENTER, result_text)
		
		# display effective FP if it was successful area fire attack
		if profile['type'] == 'Area Fire' and result_text != 'NO EFFECT':
			ConsolePrintEx(attack_con, 13, 52, libtcod.BKGND_NONE,
				libtcod.CENTER, str(profile['effective_fp']) + ' FP')
		
		# check for RoF for gun / MG attacks
		if profile['type'] != 'ap' and profile['weapon'].GetStat('rof') is not None:
			# TEMP: player only for now
			if profile['attacker'] == scenario.player_unit:
				profile['weapon'].maintained_rof = CheckRoF(profile) 
				if profile['weapon'].maintained_rof:
					ConsolePrintEx(attack_con, 13, 53, libtcod.BKGND_NONE,
						libtcod.CENTER, 'Maintained Rate of Fire')
					libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
					ConsolePrint(attack_con, 6, 56, 'F')
					libtcod.console_set_default_foreground(attack_con, libtcod.white)
					ConsolePrint(attack_con, 12, 56, 'Fire Again')
			
		# blit the finished console to the screen
		libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		
		return profile
	
	# given a combination of an attacker, weapon, and target, see if this would be a
	# valid attack; if not, return a text description of why not
	# if ignore_facing is true, we don't check whether weapon is facing correct direction
	def CheckAttack(self, attacker, weapon, target, ignore_facing=False):
		
		if weapon.GetStat('type') == 'Gun' and weapon.current_ammo is not None:
			if weapon.ammo_stores[weapon.current_ammo] == 0:
				return 'No ammo of this type remaining'
			if weapon.current_ammo == 'AP' and not target.known:
				return 'Target must be spotted for this attack'
			if weapon.current_ammo == 'AP' and target.GetStat('category') == 'Infantry':
				return 'AP has no effect on infantry'
			if weapon.current_ammo == 'AP' and target.GetStat('category') == 'Gun':
				return 'AP cannot harm guns'
		
		# don't allow firing if another weapon in this group has already fired
		firing_group = weapon.GetStat('firing_group')
		if firing_group is not None:
			for weapon2 in attacker.weapon_list:
				if weapon2 == weapon: continue
				firing_group2 = weapon2.GetStat('firing_group')
				if firing_group2 is None: continue
				if firing_group2 != firing_group: continue
				if not weapon2.fired: continue
				return "Another weapon on this mount has fired"
		
		# check that proper crew action is set for this attack if required
		position_list = weapon.GetStat('fired_by')
		if position_list is not None:
			weapon_type = weapon.GetStat('type')
			if weapon_type in ['Gun', 'Co-ax MG']:
				action = 'Operate Gun'
			elif weapon_type == 'AA MG':
				action = 'Operate AA MG'
			elif weapon_type == 'Hull MG':
				action = 'Operate Hull MG'
			elif weapon_type == 'Turret MG':
				action = 'Operate Turret MG'
			
			position = attacker.PersonnelActionPossible(position_list, action)
			if not position:
				text = 'No crewman available to: ' + action
				return text
			
			# check that firer doesn't have to be CE to fire
			if weapon.GetStat('ce_to_fire') is not None:
				if not position.crewman.ce:
					return 'Crewman must be exposed to fire'
		
		# check LoS
		if GetLoS(attacker.hx, attacker.hy, target.hx, target.hy) == -1.0:
			return 'No line of sight to target'
		
		# check that weapon can fire
		if weapon.fired:
			text = 'Weapon already fired'
			if weapon.GetStat('mount') == 'Turret':
				text += '; turret rotation NA'
			return text
		
		# check for hull-mounted weapons being blocked
		mount = weapon.GetStat('mount')
		if mount is not None:
			if mount == 'Hull' and len(attacker.hull_down) > 0:
				direction = GetDirectionToward(attacker.hx, attacker.hy,
					target.hx, target.hy)
				if direction in attacker.hull_down:
					return 'Weapon blocked by Hull Down status'

		# check range to target
		distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
		if distance > weapon.max_range:
			return 'Beyond maximum weapon range'
		
		if ignore_facing:
			return ''
		
		# check covered arc
		if mount is not None:
			if mount == 'Turret' and attacker.turret_facing is not None:
				direction = attacker.turret_facing
			else:
				direction = attacker.facing
			if (target.hx - attacker.hx, target.hy - attacker.hy) not in HEXTANTS[direction]:
				return "Outside of weapon's covered arc"

		# attack can proceed
		return ''
	
	# calculate the chance of a unit getting a bonus move after a given move
	# hx, hy is the move destination hex
	def CalcBonusMove(self, unit, hx, hy, reverse=False):
		
		# need a reverse driver to get chance of bonus
		if reverse:
			if unit.GetStat('reverse_driver') is None:
				return 0.0
			crewman = unit.GetPersonnelByPosition('Co-Driver')
			if crewman is None:
				return 0.0
			if not crewman.AbleToAct():
				return 0.0
		
		# none for ponds
		if self.cd_hex.map_hexes[(hx, hy)].terrain_type == 'pond':
			return 0.0
		
		# none for river crossings
		if len(self.cd_hex.map_hexes[(unit.hx, unit.hy)].river_edges) > 0:
			direction = GetDirectionToAdjacent(unit.hx, unit.hy, hx, hy)
			if direction in self.cd_hex.map_hexes[(unit.hx, unit.hy)].river_edges:
				return 0.0
		
		# check for dirt road link
		direction = GetDirectionToAdjacent(unit.hx, unit.hy, hx, hy)
		dirt_road = False
		if direction in self.cd_hex.map_hexes[(unit.hx, unit.hy)].dirt_roads:
			chance = DIRT_ROAD_BONUS_CHANCE
			dirt_road = True
		else:
			chance = TERRAIN_BONUS_CHANCE[self.cd_hex.map_hexes[(hx, hy)].terrain_type]
		
		# elevation change modifier
		if self.cd_hex.map_hexes[(hx, hy)].elevation > self.cd_hex.map_hexes[(unit.hx, unit.hy)].elevation:
			chance = chance * 0.75
		
		# movement class modifier
		movement_class = unit.GetStat('movement_class')
		if movement_class is not None:
			if movement_class == 'Fast Tank':
				chance += 15.0
			elif movement_class == 'Slow Tank':
				chance -= 60.0
			elif movement_class == 'Infantry':
				chance -= 50.0
			elif movement_class == 'Wheeled':
				if dirt_road:
					chance += 30.0
				else:
					chance -= 30.0
			elif movement_class == 'Fast Wheeled':
				if dirt_road:
					chance += 50.0
				else:
					if unit.GetStat('off_road') is None:
						chance -= 30.0
		
		# direct driver modifier
		position = unit.CheckPersonnelAction(['Commander', 'Commander/Gunner'], 'Direct Driver')
		if position is not False:
			mod = 15.0 + (float(position.crewman.traits['Knowledge']) * DIRECT_DRIVER_MOD)
			#print('DEBUG: Modified to-hit based on commander Knowledge of ' + str(position.crewman.traits['Knowledge']))
			chance += mod
		
		# previous bonus move modifier
		if unit.additional_moves_taken > 0:
			for i in range(unit.additional_moves_taken):
				chance = chance * BONUS_CHANCE_MULTIPLIER
		
		# reverse driver bonus less likely
		if reverse:
			chance = chance * 0.5
		
		# round off and constrain final chance
		return RestrictChance(chance)
	
	# display a pop-up window with info on a unit
	def ShowUnitInfoWindow(self, unit):
		
		# create a local copy of the current screen to re-draw when we're done
		temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
		libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
		# darken screen background
		libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
		
		# create window and draw fram
		window_con = libtcod.console_new(26, 26)
		libtcod.console_set_default_background(window_con, libtcod.black)
		libtcod.console_set_default_foreground(window_con, libtcod.white)
		DrawFrame(window_con, 0, 0, 26, 26)
		
		# draw unit info and command instructions
		unit.DisplayMyInfo(window_con, 1, 1)
		libtcod.console_set_default_foreground(window_con, ACTION_KEY_COL)
		ConsolePrint(window_con, 7, 24, 'ESC')
		libtcod.console_set_default_foreground(window_con, libtcod.lighter_grey)
		ConsolePrint(window_con, 12, 24, 'Return')
		
		# blit window to screen and then delete
		libtcod.console_blit(window_con, 0, 0, 0, 0, 0, WINDOW_XM-13, WINDOW_YM-13)
		del window_con
		
		# wait for player to exit view
		exit = False
		while not exit:
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			
			# get keyboard and/or mouse event
			if not GetInputEvent(): continue
			
			if key.vk == libtcod.KEY_ESCAPE:
				exit = True
		
		# re-draw original view
		libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
		del temp_con
		

# Personnel Class: represents an individual member of a unit 
class Personnel:
	def __init__(self, unit, nation, position):
		self.unit = unit				# pointer to which unit they belong
		self.nation = nation
		self.current_position = position		# pointer to current position in a unit
		
		self.first_name = ''				# placeholders for first and last name
		self.last_name = ''				#   set by GenerateName()
		self.GenerateName()				# generate random first and last name
		
		self.age = 0					# age of crewman in years
		self.GenerateAge()
		
		self.traits = {					# default values for modification
			'Perception' : 5,
			'Grit' : 5,
			'Knowledge' : 5
		}
		self.GenerateTraits()
		
		self.injuries = {				# injury levels for different body parts
			'Head' : 0,
			'Torso' : 0,
			'Left Arm' : 0,
			'Right Arm' : 0,
			'Left Leg' : 0,
			'Right Leg' : 0
		}
		
		self.status = 'Alert'				# current mental/physical status
		
		self.rank = 0					# rank level
		self.rank_desc = ''				# text name for rank
		self.SetRank()
		
		self.action_list = []				# list of possible actions
		self.current_action = 'None'			# currently active action
		self.action_bonus_used = False
		
		self.ce = True					# Crew Exposed / Buttoned Up
		self.CheckCE()					# check to see if no hatch, must be BU
		
		self.fov = set()				# set of visible hexes

	# generate a random first and last name for this crewman
	# TEMP: have to normalize extended characters so they can be displayed on screen
	def GenerateName(self):
		
		# normalize extended characters
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
			
	# return the crewman's full name
	def GetFullName(self):
		return (self.first_name + ' ' + self.last_name)
	
	# generate a random age for this crewman
	# FUTURE: can take into account current year of war
	def GenerateAge(self):
		self.age = 22
		roll = libtcod.random_get_int(0, 1, 6)
		if roll == 1:
			self.age -= 2
		elif roll == 2:
			self.age -= 1
		elif roll == 5:
			self.age += 1
		elif roll == 6:
			self.age += 2
		
		if self.current_position.name in ['Commander', 'Commander/Gunner']:
			roll = libtcod.random_get_int(0, 1, 6)
			if roll <= 4:
				self.age += 3
			else:
				self.age += 4
	
	# randomly modify trait values
	def GenerateTraits(self):		
		for i in range(5):
			key = choice(list(self.traits))
			self.traits[key] += 1 
			key = choice(list(self.traits))
			self.traits[key] -= 1
		
		for key in self.traits:
			if self.traits[key] < 3:
				self.traits[key] = 3
			elif self.traits[key] > 7:
				self.traits[key] = 7
	
	# set rank based on current position
	def SetRank(self):
		if self.current_position.name in ['Commander', 'Commander/Gunner']:
			self.rank = 3
		elif self.current_position.name in ['Gunner', 'Driver', 'Co-Driver']:
			self.rank = 2
		else:
			self.rank = 1
		
		self.rank_desc = session.nations[self.nation]['rank_names'][str(self.rank)]
	
	# set crewman's status, updating action if required
	def SetStatus(self, new_status):
		
		# status not possible!
		if new_status not in CREW_STATUS_LIST:
			return
		
		self.status = new_status
		
		# show player message if part of player crew
		if self.unit == campaign.player_unit:
			Message(self.GetFullName() + ' is now ' + self.status)
	
	# returns True if this crewman is currently able to choose an action
	def AbleToAct(self):
		if self.status in ['Stunned', 'Critical', 'Dead']:
			return False
		return True
	
	# build a list of possible actions for this crewman
	def BuildActionList(self):
		
		self.action_list = []
		self.current_action = 'None'
		
		# no actions possible
		if not self.AbleToAct():
			return
		
		if self.current_position.name == 'Driver':
			
			self.action_list.append(('W', 'Move Forward'))
			self.action_list.append(('S', 'Move Backward'))
			self.action_list.append(('A', 'Pivot Port'))
			self.action_list.append(('D', 'Pivot Stb'))
			self.action_list.append(('H', 'Go Hull Down'))
		
		# all crew positions
		self.action_list.append(('E', 'Toggle Hatch'))
		
	# check current CE/BU status and fix if required
	def CheckCE(self):
		if not self.current_position.hatch:
			self.ce = False
		elif self.current_position.crew_always_ce:
			self.ce = True
	
	# toggle crew exposed / button up status
	def ToggleCE(self):
		
		# can't act
		if not self.AbleToAct():
			return False
		
		# can't go CE
		if not self.ce and not self.current_position.hatch:
			return False
		
		# always CE
		if self.ce and self.current_position.crew_always_ce:
			return False
		
		self.ce = not self.ce
		return True
	
	# test for and apply injury as a result of being exposed to firepower
	# TODO: sniper hit modifiers
	def DoInjuryTest(self, fp, sniper_hit=False):
		
		# crew is not exposed, no chance of injury
		if not self.ce: return ''
		
		# roll for injury
		
		# TEMP - rough chance only, in FUTURE will be modified by fp
		chance = 40.0
		roll = GetPercentileRoll()
		if roll > chance:
			return ''
		
		# roll for location of injury
		roll = GetPercentileRoll()
		for location in BODY_LOCATIONS:
			chance = INJURY_CHANCES[location]
			if roll <= chance:
				break
			roll -= chance
		
		text = self.GetFullName()
		
		# roll for severity of injury
		# TEMP: rough roll only, will be modified by fp
		
		roll = GetPercentileRoll()
		
		# debug flag
		if INJURY_IS_DEATH: roll = 100.0
		
		if roll <= 80.0:
			# light injury
			if self.injuries[location] == 0:
				self.injuries[location] = 1
				text += ' was lightly injured in the ' + location + '.'
			
			# light -> severe injury
			elif self.injuries[location] == 1:
				self.injuries[location] = 2
				text += ' was again injured in the ' + location + ' and now has a severe injury.'
		
			# no further effect if already severe injury
			else:
				text = ''
		
		elif roll <= 97.0:
		
			# severe injury, or light -> severe injury
			# no further effect if already severely injured
			if self.injuries[location] == 2:
				text = ''
			else:
				self.injuries[location] = 2
				text += ' was severely injured in the ' + location + '.'
		
		else:
			
			# death
			self.status = 'Dead'
			self.ce = False
			text += ' has died.'
		
		# return text description of effect
		return text
	
	# check for a status change based on being subject to fp
	def CheckStatusChange(self, fp):
		
		if not self.ce: return ''
		
		# if already critical or dead, no further change possible
		if self.status in ['Critical', 'Dead']: return ''
		
		# determine injury modifier
		injury_mod = 0
		
		for key in BODY_LOCATIONS:
			if self.injuries[key] == 0:
				continue
			if key == 'Head':
				mod = 4
			elif key == 'Torso':
				mod = 2
			else:
				mod = 1
			if self.injuries[key] == 2:
				mod = mod * 2
			injury_mod += mod
		
		# if at stunned status but no injuries, no further change possible
		if self.status == 'Stunned' and injury_mod == 0:
			return ''
		
		# TODO: test against grit and apply injury modifier
		chance = float(self.traits['Grit'] * 10)
		chance -= float(injury_mod * 5)
		chance = RestrictChance(chance)
		
		#print('DEBUG: Testing status change for ' + self.GetFullName() + ', chance is: ' + str(chance))
		
		# roll passed, no change
		if GetPercentileRoll() <= chance:
			return ''
		
		# roll failed, status gets worse
		if self.status == 'Critical':
			self.status = 'Dead'
			# automatically goes BU if not already
			self.ce = False
			return self.GetFullName() + ' has died.'
		
		if self.status == 'Stunned':
			self.status = 'Critical'
			self.ce = False
			return self.GetFullName() + "'s status has worsened and is now critical."
		
		if self.status == 'Shaken':
			self.status = 'Stunned'
			self.ce = False
			return self.GetFullName() + ' is now Stunned.'
		
		self.status = 'Shaken'
		return self.GetFullName() + ' is now Shaken.'
	
	# check for recovery from negative statuses, called at start of unit activation
	def RecoveryCheck(self):
		if self.status not in ['Shaken', 'Stunned', 'Critical']:
			return ''
		
		chance = float(self.traits['Grit'] * 3)
		
		if self.status == 'Shaken':
			chance += (chance * 0.5)
		elif self.status == 'Critical':
			chance -= (chance * 0.5)
		chance = RestrictChance(chance)
		
		#print('DEBUG: Testing status recovery for ' + self.GetFullName() + ', chance is: ' + str(chance))
		
		roll = GetPercentileRoll()
		
		# roll failed, no improvement
		if roll > chance:
			
			# check for critical worsening to Death
			if self.status == 'Critical':
				if roll >= 95.0:
					self.status = 'Dead'
					return self.GetFullName() + ' has died.'
			return ''
		
		# roll passed, improve one level
		if self.status == 'Critical':
			self.status = 'Stunned'
		elif self.status == 'Stunned':
			self.status = 'Shaken'
		else:
			self.status = 'Alert'
		
		return self.GetFullName() + "'s status improves and is now " + self.status


# Crew Position class: represents a crew position on a vehicle or gun
class CrewPosition:
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
		
		# crewman currently in this position
		self.crewman = None


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
		
		# save maximum range as an int
		self.max_range = 6
		if 'max_range' in self.stats:
			self.max_range = int(self.stats['max_range'])
			del self.stats['max_range']
		else:
			if self.stats['type'] in ['Turret MG', 'Co-ax MG', 'AA MG']:
				self.max_range = 3
			elif self.stats['type'] == 'Hull MG':
				self.max_range = 1
		
		# set up ammo stores if gun with types of ammo
		self.ammo_stores = None
		if self.GetStat('type') == 'Gun' and 'ammo_type_list' in self.stats:
			self.ammo_stores = {}
			self.LoadGunAmmo()

		# TODO: set up ready rack if any
		
		self.InitScenarioStats()

	# load this gun full of ammo
	def LoadGunAmmo(self):
		# set up empty categories first
		for ammo_type in self.stats['ammo_type_list']:
			self.ammo_stores[ammo_type] = 0
		
		# now determine loadout
		max_ammo = int(self.stats['max_ammo'])
		
		# only one type, fill it up
		if len(self.stats['ammo_type_list']) == 1:
			ammo_type = self.stats['ammo_type_list'][0]
			self.ammo_stores[ammo_type] = max_ammo
		
		# HE and AP: 70% and 30%
		else:
			if self.stats['ammo_type_list'] == ['HE', 'AP']:
				self.ammo_stores['HE'] = int(max_ammo * 0.7)
				self.ammo_stores['AP'] = max_ammo - self.ammo_stores['HE']
		

	# set up any data that is unique to a scenario
	def InitScenarioStats(self):
		self.fired = False
		self.maintained_rof = False			# can fire again even if fired == True
		self.current_ammo = None
		
		# Guns must have current_ammo set or else attacks won't work properly
		if self.GetStat('type') == 'Gun':
			self.current_ammo = self.stats['ammo_type_list'][0]
	
	# switch active ammo type for this weapon
	def SelectAmmoType(self, forward):
		
		if self.GetStat('type') != 'Gun':
			return False
		if self.current_ammo is None:
			return False
		if 'ammo_type_list' not in self.stats:
			return False
		
		i = self.stats['ammo_type_list'].index(self.current_ammo)
		
		if forward:
			if i == len(self.stats['ammo_type_list']) - 1:
				i = 0
			else:
				i += 1
		else:
			if i == 0:
				i = len(self.stats['ammo_type_list']) - 1
			else:
				i = 0
		self.current_ammo = self.stats['ammo_type_list'][i]
		
		return True
	
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
	
	# reset gun for start of new turn
	def ResetForNewTurn(self):
		self.fired = False
	
	# check for the value of a stat, return None if stat not present
	def GetStat(self, stat_name):
		if stat_name not in self.stats:
			return None
		return self.stats[stat_name]
		


# Unit Class: represents a single vehicle or gun, or a squad or small team of infantry
class Unit:
	def __init__(self, unit_id):
		
		self.unit_id = unit_id			# unique ID for unit type
		self.alive = True			# unit is alive
		self.ai = None				# AI controller
		self.dummy = False			# unit is a false report, erased upon reveal
		
		# load unit stats from JSON file
		with open(DATAPATH + 'unit_type_defs.json', encoding='utf8') as data_file:
			unit_types = json.load(data_file)
		if unit_id not in unit_types:
			print('ERROR: Could not find unit id: ' + unit_id)
			self.unit_id = None
			return
		self.stats = unit_types[unit_id].copy()
		self.owning_player = None		# player that controls this unit
		self.nation = None			# nation of unit's crew
		
		self.crew_list = []			# list of pointers to crew/personnel
		
		self.crew_positions = []		# list of crew positions
		if 'crew_positions' in self.stats:
			for position_dict in self.stats['crew_positions']:
				self.crew_positions.append(CrewPosition(position_dict))
		
		self.weapon_list = []			# list of weapon systems
		weapon_list = self.stats['weapon_list']
		if weapon_list is not None:
			for weapon_dict in weapon_list:
				self.weapon_list.append(Weapon(weapon_dict))
			
			# clear this stat since we don't need it any more
			self.stats['weapon_list'] = None

	# set up any data that is unique to a scenario
	def InitScenarioStats(self):
		self.known = False			# unit is known to the opposing side
		self.identified = False			# FUTURE: unit type has been identifed
		
		self.fp_to_resolve = 0			# fp from attacks to be resolved at end of phase
		self.ap_hits_to_resolve = []		# list of unresolved AP hits
		
		self.hit_by_fp = 0			# used to tag unknown units hit by fp;
							# impacts spotting checks next turn
		
		self.hx = 0				# hex location in the scenario map
		self.hy = 0
		self.facing = None			# facing direction
		self.previous_facing = None		# hull facing before current action
		self.turret_facing = None		# facing of main turret on unit
		self.previous_turret_facing = None	# turret facing before current action
		self.hull_down = []			# list of directions in HD status
		self.dug_in = False			# unit is dug-in (infantry and guns only)
		
		self.acquired_target = None		# tuple: unit has acquired this unit to this level (1/2)
		
		self.screen_x = 0			# draw location on the screen
		self.screen_y = 0			#   set by DrawMe()
							# TODO: at present is relative to unit_con, not screen
		self.vp_hx = None			# location in viewport if any
		self.vp_hy = None			# "
		self.anim_x = 0				# animation location in console
		self.anim_y = 0
		
		# action flags
		self.used_up_moves = False		# if true, unit has no move actions remaining this turn
		self.moved = False			# unit moved or pivoted in its previous movement phase
		self.move_finished = False		# unit has no additional moves left this turn
		self.additional_moves_taken = 0		# how many bonus moves this unit has had this turn
		self.fired = False			# unit fired 1+ weapons this turn
		
		# status flags
		self.pinned = False
		self.broken = False
		#self.immobilized = False
		self.deployed = False
		
		# field of view
		self.fov = set()			# set of visible hexes for this unit
	
	# have crewmen recover and replaced after end of scenario
	def InitPostScenario(self):
		
		# clear all negative crew statuses
		# this is TEMP, in FUTURE crew will have to roll to recover
		for position in self.crew_positions:
			if position.crewman is None: continue
			if position.crewman.status in ['Alert', 'Dead']: continue
			if self == campaign.player_unit:
				text = position.crewman.GetFullName() + ' recovers from being ' + position.crewman.status
				Message(text)
			position.crewman.status = 'Alert'
		
		# replace any dead crew
		for position in self.crew_positions:
			if position.crewman.status != 'Dead': continue
			self.crew_list.remove(position.crewman)
			self.crew_list.append(Personnel(self, self.nation, position))
			position.crewman = self.crew_list[-1]
			if self == campaign.player_unit:
				text = position.crewman.GetFullName() + ' joins your crew in the ' + position.name + ' position.'
				Message(text)
			
	# return the value of a stat
	def GetStat(self, stat_name):
		if stat_name in self.stats:
			return self.stats[stat_name]
		return None
	
	# display info on this unit to a given console starting at x,y
	# if status is False, don't display status flags (used in campaign day display)
	def DisplayMyInfo(self, console, x, y, status=True):
		
		libtcod.console_set_default_background(console, libtcod.black)
		libtcod.console_set_default_foreground(console, libtcod.lighter_blue)
		
		ConsolePrint(console, x, y, self.unit_id)
		libtcod.console_set_default_foreground(console, libtcod.light_grey)
		ConsolePrint(console, x, y+1, self.GetStat('class'))
		
		portrait = self.GetStat('portrait')
		if portrait is not None:
			libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, console, x, y+2)
		
		# weapons
		libtcod.console_set_default_foreground(console, libtcod.white)
		libtcod.console_set_default_background(console, libtcod.darkest_red)
		libtcod.console_rect(console, x, y+10, 24, 2, True, libtcod.BKGND_SET)
		
		text1 = ''
		text2 = ''
		for weapon in self.weapon_list:
			if weapon.GetStat('type') == 'Gun':
				if text1 != '': text1 += ', '
				text1 += weapon.stats['name']
			else:
				if text2 != '': text2 += ', '
				text2 += weapon.stats['name']
		ConsolePrint(console, x, y+10, text1)
		ConsolePrint(console, x, y+11, text2)
		
		# armour
		armour = self.GetStat('armour')
		if armour is None:
			ConsolePrint(console, x, y+12, 'Unarmoured')
		else:
			ConsolePrint(console, x, y+12, 'Armoured')
			libtcod.console_set_default_foreground(console, libtcod.light_grey)
			if self.GetStat('turret'):
				text = 'T'
			else:
				text = 'U'
			text += ' ' + armour['turret_front'] + '/' + armour['turret_side']
			ConsolePrint(console, x+1, y+13, text)
			text = 'H ' + armour['hull_front'] + '/' + armour['hull_side']
			ConsolePrint(console, x+1, y+14, text)
		
		# movement
		libtcod.console_set_default_foreground(console, libtcod.light_green)
		ConsolePrintEx(console, x+23, y+12, libtcod.BKGND_NONE, libtcod.RIGHT,
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
		ConsolePrintEx(console, x+23, y+13, libtcod.BKGND_NONE, libtcod.RIGHT,
			text)
		
		# size class
		libtcod.console_set_default_foreground(console, libtcod.white)
		size_class = self.GetStat('size_class')
		if size_class is not None:
			if size_class != 'Normal':
				ConsolePrintEx(console, x+23, y+14, libtcod.BKGND_NONE,
					libtcod.RIGHT, size_class)
			
		# mark place in case we skip unit status display
		ys = 15
		if status:
			
			# Hull Down status if any
			if len(self.hull_down) > 0:
				libtcod.console_set_default_foreground(console, libtcod.sepia)
				ConsolePrint(console, x+8, ys-1, text)
				char = GetDirectionalArrow(ConstrainDir(self.hull_down[0] - scenario.vp_facing))
				libtcod.console_put_char_ex(unit_info_con, x+11, ys-1, char, libtcod.sepia, libtcod.black)
		
			# unit status
			libtcod.console_set_default_foreground(console, libtcod.light_grey)
			libtcod.console_set_default_background(console, libtcod.darkest_blue)
			libtcod.console_rect(console, x, y+ys, 24, 2, True, libtcod.BKGND_SET)
			
			text = ''
			if self.moved:
				text += 'Moved '
			if self.fired:
				text += 'Fired '
			ConsolePrint(console, x, y+ys+1, text)
			
			ys = 17

		libtcod.console_set_default_background(console, libtcod.black)
	
	# return the chance of gaining HD status
	def GetHullDownChance(self):
		if self.GetStat('category') != 'Vehicle': return 0.0
		if self.fired: return 0.0
		if self.moved: return 0.0
		if self.additional_moves_taken > 0: return 0.0
		
		driver_present = False
		for position in self.crew_positions:
			if position.name not in ['Driver', 'Co-Driver']: continue
			if position.crewman is None: continue
			if not position.crewman.AbleToAct(): continue
			driver_present = True
			break
		
		if not driver_present: return 0.0
		
		# use terrain modifier of current location as base chance
		chance = scenario.cd_hex.map_hexes[(self.hx, self.hy)].GetTerrainMod()
		
		# if open ground, only a very small unmodified base chance
		if chance == 0.0:
			chance = 3.0
		else:
			# apply size modifier
			size_class = self.GetStat('size_class')
			if size_class is not None:
				if size_class == 'Small':
					chance += 6.0
				elif size_class == 'Very Small':
					chance += 12.0
		
		# bonus if commander is on Direct Driver action
		if self.CheckPersonnelAction(['Commander', 'Commander/Gunner'], 'Direct Driver'):
			chance += 15.0
		
		# bonus if railroad in hex
		if len(scenario.cd_hex.map_hexes[(self.hx, self.hy)].railroads) > 0:
			chance += 15.0
		
		return RestrictChance(chance)

	# roll for HD status gain
	# if direction is provided, any HD status will be centered on that direction
	# returns True if successful
	def CheckHullDownGain(self, direction=None):
		chance = self.GetHullDownChance()
		if chance == 0.0: return False
		
		position = self.CheckPersonnelAction(['Commander', 'Commander/Gunner'], 'Direct Driver')
		if position:
			position.crewman.action_bonus_used = True
		
		roll = GetPercentileRoll()
		if roll > chance: return False
		if direction is None:
			direction = choice(range(6))
		self.SetHullDown(direction)
		return True

	# gain/update hull down status centered on given direction
	def SetHullDown(self, direction):
		self.hull_down = [direction]
		self.hull_down.append(ConstrainDir(direction + 1))
		self.hull_down.append(ConstrainDir(direction - 1))
	
	# do automatic actions before an activation
	def DoPreActivation(self):
		
		# check for air support attack trigger
		if self == scenario.player_unit and scenario.player_airsup_success:
			scenario.player_airsup_success = False
			scenario.DoAirSupportAttack()
		
		# check for artillery support attack trigger
		if self == scenario.player_unit and scenario.player_artsup_success:
			scenario.DoArtSupportAttack()
		
		# do spot checks for unknown or unidentified enemy units
		# dummy units can't spot
		if not self.dummy:
		
			# create a local list of crew positions in a random order
			position_list = sample(self.crew_positions, len(self.crew_positions))
			
			for position in position_list:
				if position.crewman is None: continue
				if position.crewman.current_action != 'Spot': continue
				
				spot_list = []
				for unit2 in scenario.units:
					if unit2.owning_player == self.owning_player:
						continue
					if not unit2.alive:
						continue
					if unit2.known:
						continue
					if GetHexDistance(self.hx, self.hy, unit2.hx, unit2.hy) > MAX_LOS_DISTANCE:
						continue
					
					if (unit2.hx, unit2.hy) in position.crewman.fov:
						spot_list.append(unit2)
				
				if len(spot_list) > 0:
					self.DoSpotCheck(choice(spot_list), position)
		
		# test for personnel status change and unit recovery
		self.UnitRecoveryCheck()
		
		# generate list of selectable crew actions
		for position in self.crew_positions:
			
			# no crewman in this position
			if position.crewman is None: continue
			
			position.crewman.BuildActionList()
			
			# reset bonus flag
			position.crewman.action_bonus_used = False
		
		# decrement FP hit counter if any
		if self.hit_by_fp > 0:
			self.hit_by_fp -= 1
		
		# check for regaining concealment
		self.ConcealmentCheck()
		
		# recalculate FoV
		# TODO: still needed?
		self.CalcFoV()
		if self == scenario.player_unit:
			UpdateVPCon()
			UpdateUnitCon()
		
		# Movement: reset flags
		self.moved = False
		self.move_finished = False
		self.additional_moves_taken = 0
		self.previous_facing = self.facing
		self.previous_turret_facing = self.turret_facing
		
		# Combat
		
		# if player unit, set up weapon and targets
		if self == scenario.player_unit:
			# if no player weapon selected, try to select the first one in the list
			if scenario.selected_weapon is None:
				if len(self.weapon_list) > 0:
					scenario.selected_weapon = self.weapon_list[0]
				
			# rebuild list of potential targets
			scenario.RebuildPlayerTargetList()
			
			# reset any failed support request flag, rebuild list of possible support attack hexes
			scenario.player_airsup_failed = False
			scenario.player_artsup_failed = False
			scenario.RebuildTargetHexList()
			
			# update unit console to show player LoS display
			UpdateUnitCon()
		
		# reset flag and weapons
		self.fired = False
		for weapon in self.weapon_list:
			weapon.ResetForNewTurn()
		
		SaveGame()
		UpdateScenarioDisplay()
	
	# do automatic actions after an activation
	def DoPostActivation(self):
		
		if self.facing is not None:
			if self.facing != self.previous_facing:
				self.moved = True
				
				# lose any of this unit's acquired targets
				self.acquired_target = None
		
		# have any free crewmen spot
		for position in self.crew_positions:
			if position.crewman is None: continue
			if not position.crewman.AbleToAct(): continue
			if position.crewman.current_action == 'None':
				position.crewman.current_action = 'Spot'
		if self == scenario.player_unit:
			UpdateCrewPositionCon()
		
		UpdateScenarioDisplay()
		libtcod.console_flush()
	
	# get a descriptive name of this unit
	def GetName(self):
		if self.owning_player == 1 and not self.known:
			return 'Unknown Unit'
		return self.unit_id
	
	# place this unit into the scenario map at hx, hy
	def SpawnAt(self, hx, hy):
		self.hx = hx
		self.hy = hy
		scenario.cd_hex.map_hexes[(hx, hy)].unit_stack.append(self)
	
	# move to the top of its current hex stack
	def MoveToTopOfStack(self):
		map_hex = scenario.cd_hex.map_hexes[(self.hx, self.hy)]
		
		# only unit in stack
		if len(map_hex.unit_stack) == 1:
			return
		
		# not actually in stack
		if self not in map_hex.unit_stack:
			return
		
		map_hex.unit_stack.remove(self)
		map_hex.unit_stack.insert(0, self)
	
	# check for personnel status change, unit recovery
	def UnitRecoveryCheck(self):
		
		# check for personnel status recovery first
		for position in self.crew_positions:
			if position.crewman is None: continue
			text = position.crewman.RecoveryCheck()
			if text != '' and self == scenario.player_unit:
				Message(text, hx=self.hx, hy=self.hy)
		
		# check for unit recovering from Broken status
		if self.broken:
			if self.MoraleCheck(BROKEN_MORALE_MOD):
				self.broken = False
				text = self.GetName() + ' recovers from being Broken.'
				Message(text, hx=self.hx, hy=self.hy)
			return
		
		# check for unit recovering from Pinned status
		if self.pinned:
			if self.MoraleCheck(0):
				self.pinned = False
				text = self.GetName() + ' recovers from being Pinned.'
				Message(text, hx=self.hx, hy=self.hy)
	
	# check to see if this unit can regain unknown status
	def ConcealmentCheck(self):
		
		# already unknown
		if not self.known: return
		
		for unit in scenario.units:
			if unit.owning_player == self.owning_player: continue
			if not unit.alive: continue
			
			# if in the FoV of an active enemy unit, can't regain unknown status
			if (self.hx, self.hy) in unit.fov:
				return
		
		# if we get here, unit is not in enemy FoV
		
		# no message if outside of VP
		dist = GetHexDistance(self.hx, self.hy, scenario.player_unit.hx,
			scenario.player_unit.hy)
		if dist > 6:
			self.unknown = True
			return
		
		# no message if allied unit
		if self.owning_player == 0 and self != scenario.player_unit:
			self.known = False
			return
		
		if self == scenario.player_unit:
			text = 'You are now concealed from the enemy'
		else:
			text = 'Lost contact with ' + self.GetName()
		Message(text, hx=self.hx, hy=self.hy, no_log=True)
		self.known = False
		UpdateUnitCon()
		UpdateUnitInfoCon()
		UpdateScenarioDisplay()
	
	# return the crewman currently in the given position
	def GetPersonnelByPosition(self, position_name):
		for position in self.crew_positions:
			if position.crewman is None: continue
			if position.name == position_name:
				return position.crewman
		return None
	
	# calculate which hexes are visible to this unit
	def CalcFoV(self):
		
		# clear set of visible hexes
		self.fov = set()
		
		# can always see own hex
		self.fov.add((self.hx, self.hy))
		
		# start field of view calculations
		#start_time = time.time()
		
		# go through crew and calculate FoV for each, adding each hex to
		# unit FoV set
		for position in self.crew_positions:
			if position.crewman is None: continue
			
			position.crewman.fov = set()
			position.crewman.fov.add((self.hx, self.hy))
			
			# to start, all visible ehxtants assume that unit is facing
			# direction 0, all hextants will be rotated to match crewman's
			# actual facing as final step
			visible_hextants = []
			
			# infantry and gun crew can see all around
			if self.GetStat('category') in ['Infantry', 'Gun']:
				visible_hextants = [0,1,2,3,4,5]
				max_distance = MAX_LOS_DISTANCE
			else:
				if not position.hatch:
					visible_hextants = position.bu_visible[:]
					max_distance = MAX_BU_LOS_DISTANCE
				else:
					if position.crewman.ce:
						visible_hextants = position.ce_visible[:]
						max_distance = MAX_LOS_DISTANCE
					else:
						visible_hextants = position.bu_visible[:]
						max_distance = MAX_BU_LOS_DISTANCE
			
			# restrict visible hextants and max distance if crewman did a
			# special action last turn
			if position.crewman.current_action is not None:
				action = CREW_ACTIONS[position.crewman.current_action]
				
				# possible visible hextants are limited by current action
				if 'fov_hextants' in action:
					limited_hextants = []
					for text in action['fov_hextants']:
						limited_hextants.append(int(text))
					for hextant in reversed(visible_hextants):
						if hextant not in limited_hextants:
							visible_hextants.remove(hextant)
						
				# maximum range limited by current action
				if 'fov_range' in action:
					if int(action['fov_range']) < max_distance:
						max_distance = int(action['fov_range'])
			
			# rotate visible hextants based on current turret/hull facing
			if self.facing is not None:
				# position is in a rotatable turret
				if position.location == 'Turret' and self.turret_facing is not None:
					direction = self.turret_facing
				else:
					direction = self.facing
				if direction != 0:
					for i, hextant in enumerate(visible_hextants):
						visible_hextants[i] = ConstrainDir(hextant + direction)
			
			# restrict vision if hull crewman and vehicle is HD
			if len(self.hull_down) > 0 and position.location == 'Hull':
				for hextant in reversed(visible_hextants):
					if hextant in self.hull_down:
						visible_hextants.remove(hextant)
			
			# go through hexes in each hextant and check LoS if within spotting distance
			for hextant in visible_hextants:
				for (hxm, hym) in HEXTANTS[hextant]:
					
					# check that it's within range
					if GetHexDistance(0, 0, hxm, hym) > max_distance:
						continue
					
					hx = self.hx + hxm
					hy = self.hy + hym
					
					# check that it's on the map
					if (hx, hy) not in scenario.cd_hex.map_hexes:
						continue
					
					# check for LoS to hex
					if GetLoS(self.hx, self.hy, hx, hy) != -1.0:
						position.crewman.fov.add((hx, hy))
			
			# add this crewman's visisble hexes to that of unit
			self.fov = self.fov | position.crewman.fov
		
		#end_time = time.time()
		#time_taken = round((end_time - start_time) * 1000, 3) 
		#print('FoV calculation for ' + self.unit_id + ' took ' + str(time_taken) + ' ms.')
	
	# generate a new crew sufficent to man all crew positions
	def GenerateNewPersonnel(self):
		for position in self.crew_positions:
			self.crew_list.append(Personnel(self, self.nation, position))
			position.crewman = self.crew_list[-1]
	
	# draw this unit to the given viewport hex on the unit console
	def DrawMe(self, vp_hx, vp_hy):
		
		# don't display if not alive any more
		if not self.alive: return
		
		# record location in viewport
		self.vp_hx = vp_hx
		self.vp_hy = vp_hy
		
		# use animation position if any, otherwise calculate draw position
		if self.anim_x !=0 and self.anim_y != 0:
			x, y = self.anim_x, self.anim_y
		else:
			(x,y) = PlotHex(vp_hx, vp_hy)
		
		# determine foreground color to use
		if self.owning_player == 1:
			if not self.known:
				col = UNKNOWN_UNIT_COL
			else:
				col = ENEMY_UNIT_COL
		else:	
			if not self.known:
				col = libtcod.grey
			else:
				col = libtcod.white
		
		libtcod.console_put_char_ex(unit_con, x, y, self.GetDisplayChar(),
			col, libtcod.black)
		
		# record draw position on unit console
		self.screen_x = x
		self.screen_y = y
		
		# determine if we need to display a turret / gun depiction
		if self.GetStat('category') == 'Infantry': return
		if self.owning_player == 1 and not self.known: return
		if self.GetStat('category') == 'Gun' and not self.deployed: return
		
		# use turret facing if present, otherwise hull facing
		if self.turret_facing is not None:
			facing = self.turret_facing
		else:
			facing = self.facing
		
		# determine location to draw turret/gun character
		direction = ConstrainDir(facing - scenario.vp_facing)
		x_mod, y_mod = PLOT_DIR[direction]
		char = TURRET_CHAR[direction]
		libtcod.console_put_char_ex(unit_con, x+x_mod, y+y_mod, char, col, libtcod.black)
		
		
	# return the display character to use on the map viewport
	def GetDisplayChar(self):
		# player unit
		if scenario.player_unit == self: return '@'
		
		# unknown enemy unit
		if self.owning_player == 1 and not self.known: return '?'
		
		unit_category = self.GetStat('category')
		
		# sniper
		if self.unit_id == 'Sniper': return 248
		
		# infantry
		if unit_category == 'Infantry': return 176
		
		# gun, set according to deployed status / hull facing
		if unit_category == 'Gun':
			if self.facing is None:		# facing not yet set
				return '!'
			direction = ConstrainDir(self.facing - scenario.player_unit.facing)
			if not self.deployed:
				return 124
			elif direction in [5, 0, 1]:
				return 232
			elif direction in [2, 3, 4]:
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
	
	# attempt to move unit in hull facing direction into next map hex
	# returns True if move was a success, false if not
	def MoveForward(self, reverse):
		
		# no moves remaining
		if self.move_finished:
			return False
		# already fired
		if self.fired:
			return False
		
		# try to set crewman action
		action_set = False
		if reverse and self.GetStat('reverse_driver') is not None:
			if self.SetPersonnelAction(['Co-Driver', 'Driver'], 'Drive'):
				action_set = True
		else:
			if self.SetPersonnelAction(['Driver'], 'Drive'):
				action_set = True
		
		# unable to set required crew action
		if not action_set:
			return False
		
		# determine target hex
		if reverse:
			(hx, hy) = GetAdjacentHex(self.hx, self.hy, ConstrainDir(self.facing + 3))
		else:
			(hx, hy) = GetAdjacentHex(self.hx, self.hy, self.facing)
		
		# target hex is off map
		if (hx, hy) not in scenario.cd_hex.map_hexes:
			return False
		
		map_hex1 = scenario.cd_hex.map_hexes[(self.hx, self.hy)]
		map_hex2 = scenario.cd_hex.map_hexes[(hx, hy)]
		direction = GetDirectionToAdjacent(self.hx, self.hy, hx, hy)
		
		# target hex can't be entered
		if map_hex2.terrain_type == 'pond':
			return False
		
		# river on edge and no road link
		if len(map_hex1.river_edges) > 0:
			if direction in map_hex1.river_edges:
				if direction not in map_hex1.dirt_roads:
					return False
		
		# already occupied by enemy
		for unit in map_hex2.unit_stack:
			if unit.owning_player != self.owning_player:
				return False
		
		# calculate bonus move chance
		chance = scenario.CalcBonusMove(self, hx, hy, reverse=reverse)
		
		# set bonus used flag if applicable
		if chance != 0.0:
			position = self.CheckPersonnelAction(['Commander', 'Commander/Gunner'], 'Direct Driver')
			if position:
				position.crewman.action_bonus_used = True
		
		# do the move and clear any acquired targets
		self.MoveInto(hx, hy)
		self.ClearAcquiredTargets()
		
		# move any unit group members as well
		# note - does not check if it's possible for them to move
		for unit in scenario.units:
			if not unit.alive: continue
			if unit.owning_player != self.owning_player: continue
			if unit.ai is None: continue
			if unit.ai.group_leader is None: continue
			if unit.ai.group_leader != self: continue
			if unit.facing is not None:
				unit.facing = direction
			if unit.turret_facing is not None:
				unit.turret_facing = direction
			unit.MoveInto(hx, hy, effects=False)
			unit.ClearAcquiredTargets()
		
		# check for bonus move
		roll = GetPercentileRoll()
		if roll <= chance:
			self.additional_moves_taken += 1
		else:
			self.move_finished = True
		
		# recalculate target hex list if player
		if self == scenario.player_unit:
			scenario.RebuildTargetHexList()
		
		return True
	
	# moves the unit into hx, hy
	# does not check whether move is possible but does set proper flags
	# if effects is true, animation and sound effects may be triggered
	def MoveInto(self, hx, hy, effects=True):
		
		map_hex1 = scenario.cd_hex.map_hexes[(self.hx, self.hy)]
		map_hex2 = scenario.cd_hex.map_hexes[(hx, hy)]
		
		# do movement animation and sound if applicable
		if effects and self.vp_hx is not None and self.vp_hy is not None:
			x1, y1 = self.screen_x, self.screen_y
			direction = GetDirectionToAdjacent(self.hx, self.hy, hx, hy)
			direction = ConstrainDir(direction - scenario.player_unit.facing)
			(new_vp_hx, new_vp_hy) = GetAdjacentHex(self.vp_hx, self.vp_hy, direction)
			(x2,y2) = PlotHex(new_vp_hx, new_vp_hy)
			line = GetLine(x1,y1,x2,y2)
			
			if not(self.owning_player == 1 and not self.known):
				PlaySoundFor(self, 'movement')
			
			for (x,y) in line[1:-1]:
				self.anim_x = x
				self.anim_y = y
				UpdateUnitCon()
				UpdateScenarioDisplay()
				libtcod.console_flush()
				Wait(8)
			self.anim_x = 0
			self.anim_y = 0
		
		# remove unit from old map hex unit stack
		map_hex1.unit_stack.remove(self)
		
		# lose any HD status
		self.hull_down = []
		
		# move to new location and add to new map hex unit stack
		self.hx = hx
		self.hy = hy
		map_hex2.unit_stack.append(self)
		
		# recalculate new FoV for unit
		self.CalcFoV()
		
		# set flag
		self.moved = True
		
		# check for random HD status gain
		self.CheckHullDownGain()
			
	# pivot the unit facing one hextant
	def Pivot(self, clockwise):
		
		if self.facing is None: return False
		
		# no moves remaining
		if self.move_finished:
			return False
		if self.fired:
			return False
		
		# make sure a crewman can drive
		if not self.SetPersonnelAction(['Driver', 'Co-Driver'], 'Drive'):
			return False
		
		if clockwise:
			change = 1
		else:
			change = -1
	
		self.facing = ConstrainDir(self.facing + change)
		
		# move turret if any along with hull
		if self.turret_facing is not None:
			self.turret_facing = ConstrainDir(self.turret_facing + change)
		
		# recalculate FoV for unit
		self.CalcFoV()
		
		return True
	
	# rotate the turret facing one hextant
	# only used by player unit for now, AI units have their own procedure in the AI object
	def RotateTurret(self, clockwise):
		
		if self.turret_facing is None:
			return False
		
		# if turret weapon fired, don't allow turret rotation
		for weapon in self.weapon_list:
			if weapon.fired:
				if weapon.GetStat('mount') == 'Turret':
					return False
		
		# TODO: make sure there is a crewman in the turret who can act to rotate the turret
		
		if clockwise:
			change = 1
		else:
			change = -1
		
		self.turret_facing = ConstrainDir(self.turret_facing + change)
		
		# recalculate FoV for unit
		self.CalcFoV()
		
		return True
	
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
	
	# start an attack with the given weapon on the given target
	def Attack(self, weapon, target):
		
		# check to see that correct data has been supplied
		if weapon is None or target is None:
			return False
		
		# make sure attack is possible
		if scenario.CheckAttack(self, weapon, target) != '':
			return False
		
		# set crew action
		position_list = weapon.GetStat('fired_by')
		if position_list is not None:
			weapon_type = weapon.GetStat('type')
			if weapon_type in ['Gun', 'Co-ax MG']:
				action = 'Operate Gun'
			elif weapon_type == 'AA MG':
				action = 'Operate AA MG'
			elif weapon_type == 'Hull MG':
				action = 'Operate Hull MG'
			elif weapon_type == 'Turret MG':
				action = 'Operate Turret MG'
			self.SetPersonnelAction(position_list, action)
		
		# set weapon and unit fired flags
		weapon.fired = True
		self.fired = True
		
		# display message if player is the target
		if target == scenario.player_unit:
			text = self.GetName() + ' fires at you!'
			Message(text, hx=self.hx, hy=self.hy)
		
		# hide player LoS
		if self == scenario.player_unit:
			session.hide_player_los = True
			UpdateUnitCon()
			UpdateScenarioDisplay()
			libtcod.console_flush()
		
		# attack loop, can do multiple shots if maintain RoF
		attack_finished = False
		while not attack_finished: 
			
			##### Attack Animation and Sound Effects #####
		
			# play sound and show animation if both units on viewport
			if self.vp_hx is not None and self.vp_hy is not None and target.vp_hx is not None and target.vp_hy is not None:
				
				# uses the root console, FUTURE: will have an animation console
				
				# Gun animation
				if weapon.GetStat('type') == 'Gun':
			
					x1, y1 = self.screen_x, self.screen_y
					x2, y2 = target.screen_x, target.screen_y
					line = GetLine(x1,y1,x2,y2)
					
					PlaySoundFor(weapon, 'fire')
					
					for (x,y) in line[2:-1]:
						libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
						libtcod.console_put_char(0, x+31, y+4, 250)
						libtcod.console_flush()
						Wait(6)
					
					libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
					libtcod.console_flush()
					
					# add explosion effect if HE ammo
					if weapon.current_ammo == 'HE':
						
						PlaySoundFor(weapon, 'he_explosion')
						
						for i in range(6):
							col = choice([libtcod.red, libtcod.yellow, libtcod.black])
							libtcod.console_set_default_foreground(0, col)
							libtcod.console_put_char(0, x2+31, y2+4, 42)
							libtcod.console_flush()
							Wait(4)
						libtcod.console_set_default_foreground(0, libtcod.white)
						libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
						libtcod.console_flush()
				
				elif weapon.GetStat('type') == 'Small Arms' or weapon.GetStat('type') in MG_WEAPONS:
					
					x1, y1 = self.screen_x, self.screen_y
					x2, y2 = target.screen_x, target.screen_y
					line = GetLine(x1,y1,x2,y2)
					
					PlaySoundFor(weapon, 'fire')
					
					libtcod.console_set_default_foreground(0, libtcod.yellow)
					for i in range(30):
						(x,y) = choice(line[2:-1])
						libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
						libtcod.console_put_char(0, x+31, y+4, 250)
						Wait(3)
					libtcod.console_set_default_foreground(0, libtcod.white)
					
					libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
					libtcod.console_flush()
			
			
			# expend a shell if gun
			if weapon.GetStat('type') == 'Gun' and weapon.current_ammo is not None:
				weapon.ammo_stores[weapon.current_ammo] -= 1
			
			# calculate an attack profile
			profile = scenario.CalcAttack(self, weapon, target)
			
			# something went wrong!
			if profile is None: return False
			
			# set bonus used flag if applicable
			if profile['type'] in ['Point Fire', 'Area Fire']:
				position = self.CheckPersonnelAction(['Commander'], 'Direct Fire')
				if position:
					position.crewman.action_bonus_used = True
			
			# display the attack to the screen
			scenario.DisplayAttack(profile)
			
			# pause if player is involved and we didn't maintain RoF
			if self == scenario.player_unit or target == scenario.player_unit:
				if not weapon.maintained_rof:
					WaitForContinue()
			
			# do the roll and display results to the screen
			profile = scenario.DoAttackRoll(profile)
			
			# if we maintain RoF, we might choose to attack again here
			attack_finished = True
			if self == scenario.player_unit or target == scenario.player_unit:
				end_pause = False
				while not end_pause:
					if libtcod.console_is_window_closed(): sys.exit()
					libtcod.console_flush()
					if not GetInputEvent(): continue
					
					key_char = DecodeKey(chr(key.c).lower())
					
					if key.vk == libtcod.KEY_TAB:
						end_pause = True
					
					if self == scenario.player_unit:
						if key_char == 'f' and weapon.maintained_rof:
							attack_finished = False
							end_pause = True
			
			
			# add acquired target if firing gun
			if weapon.GetStat('type') == 'Gun':
				self.AddAcquiredTarget(target)
			
			# apply results of this attack if any
			if profile['type'] == 'Area Fire':
				
				# sniper attacks are resolved right away
				if self.unit_id == 'Sniper':
					if profile['result'] == 'NO EFFECT': return
					
					# resolve sniper attack now
					
					# select target
					position_list = []
					for position in target.crew_positions:
						if position.crewman is None: continue
						if position.crewman.status in ['Critical', 'Dead']: continue
						# vehicle target: crewman must be exposed
						if target.GetStat('category') == 'Vehicle':
							if not position.crewman.ce: continue
						position_list.append(position)
					
					# no valid targets
					if len(position_list) == 0:
						return
					
					position = choice(position_list)
					result = position.crewman.DoInjuryTest(2, sniper_hit=True)
					
					# target was injured and is in player unit
					if result != '' and self == campaign.player_unit:
						Message(result)
					
					if target.GetStat('category') != 'Vehicle':
						target.PinMe()
						
					return
				
				if profile['result'] in ['CRITICAL EFFECT', 'FULL EFFECT', 'PARTIAL EFFECT']:
					
					target.fp_to_resolve += profile['effective_fp']
					
					# target will automatically be spotted next turn if possible
					if not target.known:
						target.hit_by_fp = 2
				
				# possible it was converted into an AP MG hit
				elif profile['result'] in ['HIT', 'CRITICAL HIT']:	
					target.ap_hits_to_resolve.append(profile)
			
			# ap attack hit
			elif profile['result'] in ['CRITICAL HIT', 'HIT']:
				
				# infantry or gun target
				if target.GetStat('category') in ['Infantry', 'Gun']:
					
					# if HE hit, apply effective FP
					if profile['ammo_type'] == 'HE':
						
						effective_fp = profile['weapon'].GetEffectiveFP()
						
						# apply critical hit multiplier
						if profile['result'] == 'CRITICAL HIT':
							effective_fp = effective_fp * 2 
					
						target.fp_to_resolve += effective_fp
						
						if not target.known:
							target.hit_by_fp = 2
					
					# TEMP: AP hits have no effect on Guns
				
				# vehicle hit
				else:
					
					# record AP hit to be resolved if target was a vehicle
					# also handles AP rolls for HE hits
					if target.GetStat('category') == 'Vehicle':
						target.ap_hits_to_resolve.append(profile)
				
				# add to record if player
				if self == scenario.player_unit:
					campaign_day.records['Gun Hits'] += 1
		
		# reset weapon RoF - needed?
		weapon.maintained_rof = False
		
		# re-enable player LoS
		if self == scenario.player_unit:
			session.hide_player_los = False
			UpdateUnitCon()
			UpdateScenarioDisplay()
			libtcod.console_flush()
		
		return True
	
	# resolve all unresolved AP hits and FP on this unit
	# triggered at end of enemy combat phase
	def ResolveHits(self):
		
		# handle FP first
		self.ResolveFP()
		if not self.alive: return
		
		# handle AP hits
		for profile in self.ap_hits_to_resolve:
			
			# TODO: determine if an AP roll must be made
			if self.GetStat('category') == 'Vehicle':
			
				profile = scenario.CalcAP(profile)
				scenario.DisplayAttack(profile)
				
				if profile['attacker'] == scenario.player_unit or self == scenario.player_unit:
					WaitForContinue()
				
				# do the attack roll; modifies the attack profile
				profile = scenario.DoAttackRoll(profile)
				
				if profile['result'] == 'NO PENETRATION':
					PlaySoundFor(self, 'armour_save')
				
				if profile['attacker'] == scenario.player_unit or self == scenario.player_unit:
					WaitForContinue()
				
				if profile['result'] == 'PENETRATED':
					
					# TODO: roll for penetration result here, use the
					# final 'roll' difference vs. 'final_chance' as modifier
					
					self.DestroyMe()
					
					# display message
					if self == scenario.player_unit:
						text = 'You were'
					else:
						text = self.GetName() + ' was'
					text += ' destroyed by '
					if profile['attacker'] == scenario.player_unit:
						text += 'you.'
					else:
						text += profile['attacker'].GetName() + '.'
					Message(text, hx=self.hx, hy=self.hy)
					
					return
				
				# if HE shell, apply fp to crew and check for injury
				if profile['ammo_type'] == 'HE':
					self.CheckForCrewInjury(int(profile['weapon'].GetEffectiveFP()))
		
		# clear unresolved hits
		self.ap_hits_to_resolve = []
	
	# resolve FP on this unit if any
	def ResolveFP(self):
		if self.fp_to_resolve == 0: return
		
		if self.GetStat('category') == 'Vehicle':
			self.CheckForCrewInjury(self.fp_to_resolve)		
			self.fp_to_resolve = 0
			return
		
		# calculate base chance of no effect
		base_chance = RESOLVE_FP_BASE_CHANCE
		for i in range(2, self.fp_to_resolve + 1):
			base_chance -= RESOLVE_FP_CHANCE_STEP * (RESOLVE_FP_CHANCE_MOD ** (i-1)) 
		
		# TODO: calculate modifiers
		
		# round and restrict final chances
		broken_chance = RestrictChance(base_chance * 1.2)
		base_chance = RestrictChance(base_chance)
		
		# display pop-up message if unit is known and on VP
		if (self.owning_player == 0 or (self.owning_player == 1 and self.known)) and self.vp_hx is not None:
			text = 'Resolving ' + str(self.fp_to_resolve) + ' firepower on ' + self.GetName()
			Message(text, hx=self.hx, hy=self.hy)
		
		# roll for effect
		roll = GetPercentileRoll()
		
		if roll <= base_chance:
			# no effect, but do pin test (handles message itself)
			self.PinTest(self.fp_to_resolve)
		
		elif roll <= broken_chance:
			text = self.GetName() + ' was Broken.'
			Message(text, hx=self.hx, hy=self.hy)
			self.BreakMe()
		else:
			text = self.GetName() + ' was destroyed.'
			Message(text, hx=self.hx, hy=self.hy)
			self.DestroyMe()
		
		self.fp_to_resolve = 0
	
	# check for crew injury from receiving fp
	def CheckForCrewInjury(self, fp):
		for position in self.crew_positions:
			if position.crewman is None: continue
			text = position.crewman.DoInjuryTest(fp)
			
			# display message if result and personnel is part of player unit
			if text != '' and self == scenario.player_unit:
				Message(text, hx=self.hx, hy=self.hy)
				
			# check for possible personnel status change
			text = position.crewman.CheckStatusChange(self.fp_to_resolve)
			if text != '' and self == scenario.player_unit:
				# update crew position console to show new status
				UpdateCrewPositionCon()
				Message(text, hx=self.hx, hy=self.hy)
	
	# do a morale check for this unit to recover from Broken or Pinned status
	def MoraleCheck(self, modifier):
		
		chance = MORALE_CHECK_BASE_CHANCE + modifier
		
		# TODO: apply terrain modifiers
		
		# TODO: check for leader skill
		
		chance = RestrictChance(chance)
		
		roll = GetPercentileRoll()
		if roll <= chance:
			return True
		return False
		
	# do a pin test on this unit
	def PinTest(self, fp):
		chance = float(fp) * 10.0
		chance -= scenario.cd_hex.map_hexes[(self.hx, self.hy)].GetTerrainMod()
		chance = RestrictChance(chance)
		roll = GetPercentileRoll()
		if roll > chance:
			self.PinMe()
	
	# pin this unit
	def PinMe(self):
		self.pinned = True
		self.acquired_target = None
		UpdateUnitInfoCon()
		UpdateScenarioDisplay()
		text = self.GetName() + ' is now Pinned.'
		Message(text, hx=self.hx, hy=self.hy)
	
	# break this unit
	def BreakMe(self):
		self.broken = True
		self.acquired_target = None
		UpdateUnitInfoCon()
		UpdateScenarioDisplay()
	
	# destroy this unit and remove it from the scenario map
	def DestroyMe(self):
		
		# debug flag active
		if GODMODE and self == scenario.player_unit:
			Message('GODMODE: You were saved from destruction', hx=self.hx, hy=self.hy)
			self.ap_hits_to_resolve = []
			return
		
		if not self.dummy and self.GetStat('category') == 'Vehicle':
			PlaySoundFor(self, 'vehicle_explosion')
		
		self.alive = False
		
		scenario.cd_hex.map_hexes[(self.hx, self.hy)].unit_stack.remove(self)
		self.ClearAcquiredTargets()
		
		# clear if this unit was player target
		if scenario.player_target == self:
			scenario.player_target = None
		
		# remove player ally from campaign list
		if self != scenario.player_unit and self.owning_player == 0:
			if self in campaign.player_unit_group:
				campaign.player_unit_group.remove(self)
		
		# set campaign unit flag
		if self == scenario.player_unit:
			campaign.player_unit.alive = False
		
		# award VP to player for unit destruction
		elif self.owning_player == 1:
			campaign.AwardVP(campaign_day.unit_destruction_vp[self.GetStat('category')])
			
			# add to day records
			category = self.GetStat('category')
			if category == 'Vehicle':
				campaign_day.records['Vehicles Destroyed'] += 1
			elif category == 'Gun':
				campaign_day.records['Guns Destroyed'] += 1
			elif category == 'Infantry':
				campaign_day.records['Infantry Destroyed'] += 1
		
		UpdateUnitCon()
		UpdateScenarioDisplay()
	
	# returns true if this unit would be vulnerable to small arms fire from the given attacker
	def VulnerableToSAFireFrom(self, attacker):
		
		# infantry and guns always vulnerable
		if self.GetStat('category') in ['Infantry', 'Gun']: return True
		
		# unarmoured vehicles are always vulnerable
		armour = self.GetStat('armour')
		if armour is None: return True
		
		# check possible turret hit
		turret_facing = False
		if self.turret_facing is not None:
			turret_facing = True
		facing = GetFacing(attacker, self, turret_facing=turret_facing).lower()
		if armour['turret_' + facing] == '-': return True
		
		# check possible hull hit
		facing = GetFacing(attacker, self, turret_facing=False).lower()
		if armour['hull_' + facing] == '-': return True
		
		# check for any exposed crew
		for position in self.crew_positions:
			if position.crewman is None: continue
			if position.crewman.ce: return True
		
		return False
	
	# roll a spotting check from this unit to another using the given crew position
	def DoSpotCheck(self, target, position):
		
		chance = SPOT_BASE_CHANCE
		
		# distance modifier
		distance = GetHexDistance(self.hx, self.hy, target.hx, target.hy)
		
		for i in range(distance):
			chance = chance * 0.9
		
		# terrain
		los = GetLoS(self.hx, self.hy, target.hx, target.hy)
		if los > 0.0:
			chance -= los
		
		# target size
		size_class = target.GetStat('size_class')
		if size_class is not None:
			if size_class == 'Small':
				chance -= 7.0
			elif size_class == 'Very Small':
				chance -= 18.0
		
		# spotter moved / target moved
		if self.moved:
			chance = chance * 0.75
		elif target.moved:
			chance = chance * 1.5
		
		# target fired
		if target.fired:
			chance = chance * 2.0
		
		# infantry are not as good at spotting from their lower position
		if self.GetStat('category') == 'Infantry':
			chance = chance * 0.5
		
		# snipers are hard to spot
		if target.unit_id == 'Sniper':
			chance = chance * 0.25
		
		# perception modifier
		chance += float(position.crewman.traits['Perception']) * PERCEPTION_SPOTTING_MOD
		
		chance = RestrictChance(chance)
		
		# special: automatic spot cases
		if distance <= 1 and los == 0.0:
			chance = 100.0
		
		# target was hit by effective fp last turn
		if target.hit_by_fp > 0:
			chance = 100.0
		
		roll = GetPercentileRoll()
		
		if roll <= chance:
			target.SpotMe()
			
			# display pop-up message window
			if self.owning_player == 0:
				
				# need different message if it's an allied unit doing the spotting
				if self == scenario.player_unit:
					text = position.crewman.GetFullName() + ' says: '
				else:
					text = 'Radio message: '
				
				if target.dummy:
					text += 'False report: No enemy unit actually in area.'
					portrait = None
				else:
					text += target.GetName() + ' ' + target.GetStat('class')
					text += ' spotted!'
					portrait = target.GetStat('portrait')
				
				Message(text, hx=target.hx, hy=target.hy, portrait=portrait)
			
			elif target == scenario.player_unit:
				Message('You have been spotted!', hx=target.hx, hy=target.hy)
			
	# reveal this unit after being spotted
	def SpotMe(self):
		
		# dummy units are removed instead
		if self.dummy:
			self.DestroyMe()
			return
>>>>>>> 6fb365a465b82191e802d0b528c9965c0c8558f0
		






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
		if event != libtcod.EVENT_KEY_PRESS:
			exit = True
	session.key_down = False
	

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


# wait for a specified amount of miliseconds, refreshing the screen in the meantime
def Wait(wait_time):
	wait_time = wait_time * 0.01
	start_time = time.time()
	while time.time() - start_time < wait_time:
		FlushKeyboardEvents()


# save the current game in progress
#def SaveGame():
#	save = shelve.open('savegame', 'n')
#	save['campaign'] = campaign
#	save['campaign_day'] = campaign_day
#	save['version'] = VERSION		# for now the saved version must be identical to the current one
#	save.close()


# load a saved game
#def LoadGame():
#	global campaign, campaign_day
#	save = shelve.open('savegame')
#	campaign = save['campaign']
#	campaign_day = save['campaign_day']
#	save.close()


# remove a saved game
def EraseGame():
	os.remove('savegame.dat')
	os.remove('savegame.dir')
	os.remove('savegame.bak')
	

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


# save current config to file
def SaveCFG():
	with open(DATAPATH + 'armcom2.cfg', 'w') as configfile:
		config.write(configfile)


# generate keyboard encoding and decoding dictionaries
def GenerateKeyboards():
	
	global keyboard_decode, keyboard_encode

	keyboard_decode = {}
	keyboard_encode = {}
	with open(DATAPATH + 'keyboard_mapping.json', encoding='utf8') as data_file:
		keyboards = json.load(data_file)
	dictionary = keyboards[KEYBOARDS[config['ArmCom2'].getint('keyboard')]]
	for key, value in dictionary.items():
		keyboard_decode[key] = value
		keyboard_encode[value] = key


# turn an inputted key into a standard key input
def DecodeKey(key_char):
	if key_char in keyboard_decode:
		return keyboard_decode[key_char].encode('IBM850')
	return key_char


# turn a standard key into the one for the current keyboard layout
def EncodeKey(key_char):
	if key_char in keyboard_encode:
		return keyboard_encode[key_char].encode('IBM850')
	return key_char


##########################################################################################
#                                   Sounds and Music                                     #
##########################################################################################

# play a given sample, returns the channel it is playing on
def PlaySound(sound_name):
	
	if sound_name not in session.sample:
		print('ERROR: Sound not found: ' + sound_name)
		return
	
	channel = mixer.Mix_PlayChannel(-1, session.sample[sound_name], 0)
	if channel == -1:
		print('ERROR: could not play sound: ' + sound_name)
		print(mixer.Mix_GetError())
	return channel


# select and play a sound effect for a given situation
def PlaySoundFor(obj, action):
	
	# sounds disabled
	if not config['ArmCom2'].getboolean('sounds_enabled'):
		return
	
	if action == 'menu_select':
		PlaySound('menu_select')
		return
	
	elif action == 'fire':
		if obj.GetStat('type') == 'Gun':
			
			if obj.GetStat('name') == 'AT Rifle':
				PlaySound('at_rifle_firing')
				return
			
			n = libtcod.random_get_int(0, 0, 3)
			PlaySound('37mm_firing_0' + str(n))
			return
			
		if obj.stats['type'] in MG_WEAPONS:
			PlaySound('zb_53_mg_00')
			return
		
		if obj.GetStat('name') == 'Rifles':
			n = libtcod.random_get_int(0, 0, 3)
			PlaySound('rifle_fire_0' + str(n))
			return
	 
	elif action == 'he_explosion':
		n = libtcod.random_get_int(0, 0, 1)
		PlaySound('37mm_he_explosion_0' + str(n))
		return
	
	elif action == 'armour_save':
		n = libtcod.random_get_int(0, 0, 1)
		PlaySound('armour_save_0' + str(n))
		return
	
	elif action == 'movement':
		if obj.GetStat('movement_class') in ['Wheeled', 'Fast Wheeled']:
			n = libtcod.random_get_int(0, 0, 2)
			PlaySound('wheeled_moving_0' + str(n))
			return
		
		if obj.GetStat('class') in ['Tankette', 'Light Tank', 'Medium Tank']:
			n = libtcod.random_get_int(0, 0, 2)
			PlaySound('light_tank_moving_0' + str(n))
			return
	
	elif action == 'vehicle_explosion':
		PlaySound('vehicle_explosion_00')
		return
	
	elif action == 'plane_incoming':
		PlaySound('plane_incoming_00')
		return
	
	elif action == 'stuka_divebomb':
		PlaySound('stuka_divebomb_00')
		return


##########################################################################################
#                              In-Game Menus and Displays                                #
##########################################################################################

# display a list of game options and current settings
def DisplayGameOptions(console, x, y, skip_esc=False):
	for (char, text) in [('F', 'Font Size'), ('S', 'Sound Effects'), ('K', 'Keyboard'), ('Esc', 'Return to Main Menu')]:
		
		if char == 'Esc' and skip_esc: continue
		
		# extra spacing
		if char == 'Esc': y += 1
		
		libtcod.console_set_default_foreground(console, ACTION_KEY_COL)
		ConsolePrint(console, x, y, char)
		
		libtcod.console_set_default_foreground(console, libtcod.lighter_grey)
		ConsolePrint(console, x+4, y, text)
		
		# current option settings
		libtcod.console_set_default_foreground(console, libtcod.light_blue)
		
		# toggle font size
		if char == 'F':
			if config['ArmCom2'].getboolean('large_display_font'):
				text = '16x16'
			else:
				text = '8x8'
			ConsolePrint(console, x+18, y, text)
		
		# sound effects
		elif char == 'S':
			if config['ArmCom2'].getboolean('sounds_enabled'):
				text = 'ON'
			else:
				text = 'OFF'
			ConsolePrint(console, x+18, y, text)
		
		# keyboard settings
		elif char == 'K':
			ConsolePrint(console, x+18, y, KEYBOARDS[config['ArmCom2'].getint('keyboard')])
		
		y += 1


# take a keyboard input and change game settings
def ChangeGameSettings(key_char):
	
	if key_char not in ['f', 's', 'k']:
		return
	
	# switch font size
	if key_char == 'f':
		libtcod.console_delete(0)
		if config.getboolean('ArmCom2', 'large_display_font'):
			config['ArmCom2']['large_display_font'] = 'false'
			fontname = 'c64_8x8.png'
		else:
			config['ArmCom2']['large_display_font'] = 'true'
			fontname = 'c64_16x16.png'
		libtcod.console_set_custom_font(DATAPATH+fontname,
			libtcod.FONT_LAYOUT_ASCII_INROW, 0, 0)
		libtcod.console_init_root(WINDOW_WIDTH, WINDOW_HEIGHT,
			NAME + ' - ' + VERSION, fullscreen = False,
			renderer = RENDERER)
	
	# toggle sound effects on/off
	elif key_char == 's':
		if config['ArmCom2'].getboolean('sounds_enabled'):
			config['ArmCom2']['sounds_enabled'] = 'false'
		else:
			config['ArmCom2']['sounds_enabled'] = 'true'
			# init mixer and load sound samples if required
			if len(session.sample) == 0:
				session.InitMixer()
				session.LoadSounds()
		
	# switch keyboard layout
	elif key_char == 'k':
		i = config['ArmCom2'].getint('keyboard')
		if i == len(KEYBOARDS) - 1:
			i = 0
		else:
			i += 1
		config['ArmCom2']['keyboard'] = i
		GenerateKeyboards()
	
	SaveCFG()
	return True


##########################################################################################
#                              Console Drawing Functions                                 #
##########################################################################################
<<<<<<< HEAD
=======

# draw an ArmCom2-style frame to the given console
def DrawFrame(console, x, y, w, h):
	libtcod.console_put_char(console, x, y, 249)
	libtcod.console_put_char(console, x+w-1, y, 249)
	libtcod.console_put_char(console, x, y+h-1, 249)
	libtcod.console_put_char(console, x+w-1, y+h-1, 249)
	for x1 in range(x+1, x+w-1):
		libtcod.console_put_char(console, x1, y, 196)
		libtcod.console_put_char(console, x1, y+h-1, 196)
	for y1 in range(y+1, y+h-1):
		libtcod.console_put_char(console, x, y1, 179)
		libtcod.console_put_char(console, x+w-1, y1, 179)


# draw info about a series of crew positions and their crewmen to a console
def DisplayCrew(unit, console, x, y, highlight_selected, skip_action=False):
	
	n = 0
	
	for position in unit.crew_positions:
		
		n += 1
		
		# highlight selected position and crewman
		if highlight_selected:
			if n-1 == campaign.selected_position:
				libtcod.console_set_default_background(console, libtcod.darker_blue)
				libtcod.console_rect(console, x, y, 24, 3, True, libtcod.BKGND_SET)
				libtcod.console_set_default_background(console, libtcod.black)
		
		# display ordinal number of position, location in vehicle, and name of position
		libtcod.console_set_default_foreground(console, ACTION_KEY_COL)
		ConsolePrint(console, x, y, str(n))
		
		libtcod.console_set_default_foreground(console, libtcod.light_blue)
		ConsolePrint(console, x, y+1, position.name)
		
		libtcod.console_set_default_foreground(console, libtcod.white)
		ConsolePrintEx(console, x+23, y, libtcod.BKGND_NONE, libtcod.RIGHT,
			position.location)
		
		# if crewman is present in position, display his info
		if position.crewman is None:
			ConsolePrint(console, x+2, y, 'Empty')
		else:
		
			# names might have special characters so we encode it before printing it
			ConsolePrint(console, x+2, y, position.crewman.last_name.encode('IBM850'))
		
			if position.crewman.ce:
				text = 'CE'
			else:
				text = 'BU'
			ConsolePrintEx(console, x+23, y+1, libtcod.BKGND_NONE, libtcod.RIGHT, text)
		
			# display current action if any
			if not skip_action:
				# truncate string if required
				text = position.crewman.current_action
				if len(text) + len(position.crewman.status) > 23:
					text = text[:(19 - len(position.crewman.status))] + '...'
				
				libtcod.console_set_default_foreground(console, libtcod.dark_yellow)
				ConsolePrint(console, x, y+2, text)
				
			# display current status on same line
			if position.crewman.status == 'Alert':
				libtcod.console_set_default_foreground(console, libtcod.grey)
			elif position.crewman.status == 'Dead':
				libtcod.console_set_default_foreground(console, libtcod.darker_grey)
			elif position.crewman.status == 'Critical':
				libtcod.console_set_default_foreground(console, libtcod.light_red)
			else:
				libtcod.console_set_default_foreground(console, libtcod.red)
			ConsolePrintEx(console, x+23, y+2, libtcod.BKGND_NONE, libtcod.RIGHT, 
				position.crewman.status)
			
		libtcod.console_set_default_foreground(console, libtcod.white)
		y += 4
>>>>>>> 6fb365a465b82191e802d0b528c9965c0c8558f0

# draw an ArmCom2-style frame to the given console
def DrawFrame(console, x, y, w, h):
	libtcod.console_put_char(console, x, y, 249)
	libtcod.console_put_char(console, x+w-1, y, 249)
	libtcod.console_put_char(console, x, y+h-1, 249)
	libtcod.console_put_char(console, x+w-1, y+h-1, 249)
	for x1 in range(x+1, x+w-1):
		libtcod.console_put_char(console, x1, y, 196)
		libtcod.console_put_char(console, x1, y+h-1, 196)
	for y1 in range(y+1, y+h-1):
		libtcod.console_put_char(console, x, y1, 179)
		libtcod.console_put_char(console, x+w-1, y1, 179)


# display a pop-up message on the root console
# can be used for yes/no confirmation
def ShowNotification(text, confirm=False):
	
	# determine window x, height, and y position
	x = WINDOW_XM - 30
	lines = wrap(text, 56)
	h = len(lines) + 6
	y = WINDOW_YM - int(h/2)
	
	# create a local copy of the current screen to re-draw when we're done
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
	# darken background 
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.5)
	
	# draw a black rect and an outline
	libtcod.console_rect(0, x, y, 60, h, True, libtcod.BKGND_SET)
	DrawFrame(0, x, y, 60, h)
	
	# display message
	ly = y+2
	for line in lines:
		ConsolePrint(0, x+2, ly, line)
		ly += 1
	
	# if asking for confirmation, display yes/no choices, otherwise display a simple messages
	if confirm:
		text = 'Proceed? Y/N'
	else:
		text = 'Enter to Continue'
	
	ConsolePrintEx(0, WINDOW_XM, y+h-2, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	
	# show to screen
	libtcod.console_flush()
	
	exit_menu = False
	while not exit_menu:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		
		if not GetInputEvent(): continue
		key_char = chr(key.c).lower()
		
		if confirm:
			
			if key_char == 'y':
				# restore original screen before returning
				libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
				del temp_con
				return True
			elif key_char == 'n':
				libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
				del temp_con
				return False
		else:
			if key.vk == libtcod.KEY_ENTER:
				exit_menu = True
	
	libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
	del temp_con
	

<<<<<<< HEAD
=======
# draw the map viewport console
# each hex is 5x5 cells, but edges overlap with adjacent hexes
def UpdateVPCon():

	libtcod.console_set_default_background(map_vp_con, libtcod.black)
	libtcod.console_clear(map_vp_con)
	libtcod.console_clear(fov_con)
	scenario.hex_map_index = {}
	
	# draw off-map hexes first
	for (hx, hy), (map_hx, map_hy) in scenario.map_vp.items():
		if (map_hx, map_hy) not in scenario.cd_hex.map_hexes:
			(x,y) = PlotHex(hx, hy)
			libtcod.console_blit(tile_offmap, 0, 0, 0, 0, map_vp_con, x-3, y-2)
			
	# draw on-map hexes starting with lowest elevation
	for elevation in range(MAX_ELEVATION+1):
		for (hx, hy) in VP_HEXES:
			(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
			if (map_hx, map_hy) not in scenario.cd_hex.map_hexes:
				continue
			map_hex = scenario.cd_hex.map_hexes[(map_hx, map_hy)]
			
			if map_hex.elevation != elevation: continue
			(x,y) = PlotHex(hx, hy)
			
			libtcod.console_blit(session.hex_consoles[(map_hx, map_hy)],
				0, 0, 0, 0, map_vp_con, x-3, y-2)
			
			# if this hex is visible, unmask it in the FoV mask
			if (map_hx, map_hy) in scenario.player_unit.fov:
				libtcod.console_blit(hex_fov, 0, 0, 0, 0, fov_con, x-3, y-2)
				
			# record map hexes of screen locations
			for x1 in range(x-1, x+2):
				scenario.hex_map_index[(x1,y-1)] = (map_hx, map_hy)
				scenario.hex_map_index[(x1,y+1)] = (map_hx, map_hy)
			for x1 in range(x-2, x+3):
				scenario.hex_map_index[(x1,y)] = (map_hx, map_hy)
	
	# draw river edges
	for (hx, hy) in VP_HEXES:
		(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
		if (map_hx, map_hy) not in scenario.cd_hex.map_hexes:
			continue
		map_hex = scenario.cd_hex.map_hexes[(map_hx, map_hy)]
		
		if len(map_hex.river_edges) == 0: continue
		
		(x,y) = PlotHex(hx, hy)
		for direction in map_hex.river_edges:
			for (xm, ym) in HEX_EDGE_CELLS[ConstrainDir(direction - scenario.player_unit.facing)]:
				libtcod.console_set_char_background(map_vp_con, x+xm, 
					y+ym, RIVER_BG_COL)
	
	# draw roads and railroads
	for (hx, hy) in VP_HEXES:
		(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
		if (map_hx, map_hy) not in scenario.cd_hex.map_hexes:
			continue
		map_hex = scenario.cd_hex.map_hexes[(map_hx, map_hy)]
		# no road here
		if len(map_hex.dirt_roads) >= 0:
			for direction in map_hex.dirt_roads:
				
				# get other VP hex linked by road
				(hx2, hy2) = GetAdjacentHex(hx, hy, ConstrainDir(direction - scenario.player_unit.facing))
				
				# only draw if it is in direction 0-2, unless the other hex is off the VP
				if (hx2, hy2) in VP_HEXES and 3 <= direction <= 5: continue
				
				# paint road
				(x1, y1) = PlotHex(hx, hy)
				#(hx2, hy2) = GetAdjacentHex(hx, hy, ConstrainDir(direction - scenario.player_unit.facing))
				(x2, y2) = PlotHex(hx2, hy2)
				for (x, y) in GetLine(x1, y1, x2, y2):
					
					# don't paint over outside of map area
					if libtcod.console_get_char_background(map_vp_con, x, y) == libtcod.black:
						continue
					
					libtcod.console_set_char_background(map_vp_con, x, y,
						DIRT_ROAD_COL, libtcod.BKGND_SET)
					
					# if character is not blank or hex edge, remove it
					if libtcod.console_get_char(map_vp_con, x, y) not in [0, 250]:
						libtcod.console_set_char(map_vp_con, x, y, 0)
		
		if len(map_hex.railroads) > 0:
			libtcod.console_set_default_foreground(map_vp_con, libtcod.dark_grey)
			for direction in map_hex.railroads:
				(hx2, hy2) = GetAdjacentHex(hx, hy, ConstrainDir(direction - scenario.player_unit.facing))
				if (hx2, hy2) in VP_HEXES and 3 <= direction <= 5: continue
				(x1, y1) = PlotHex(hx, hy)
				(x2, y2) = PlotHex(hx2, hy2)
				for (x, y) in GetLine(x1, y1, x2, y2):
					if libtcod.console_get_char_background(map_vp_con, x, y) == libtcod.black:
						continue
					ConsolePrint(map_vp_con, x, y, '#')
			libtcod.console_set_default_foreground(map_vp_con, libtcod.white)	

	# highlight objective
	for (hx, hy) in VP_HEXES:
		if scenario.map_vp[(hx, hy)] != (0,0): continue
		(x,y) = PlotHex(hx, hy)
		libtcod.console_blit(hex_objective, 0, 0, 0, 0, map_vp_con, x-3, y-2, 1.0, 0.0)
		break
	
	# show hex scores if flag enabled
	if not SHOW_HEX_SCORES: return
	
	for (hx, hy) in VP_HEXES:
		(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
		if (map_hx, map_hy) not in scenario.cd_hex.map_hexes:
			continue
		map_hex = scenario.cd_hex.map_hexes[(map_hx, map_hy)]
		(x,y) = PlotHex(hx, hy)
		ConsolePrint(map_vp_con, x-1, y+1, str(map_hex.scores['total_score']))



# display units on the unit console
# also displays map hex highlight, targeted hex, and LoS if any
def UpdateUnitCon():
	libtcod.console_set_default_foreground(unit_con, libtcod.white)
	libtcod.console_set_default_background(unit_con, KEY_COLOR)
	libtcod.console_clear(unit_con)
	
	# clear unit vp_hx and vp_hy
	for unit in scenario.units:
		unit.vp_hx = None
		unit.vp_hy = None
	
	# run through each viewport hex
	for (vp_hx, vp_hy) in VP_HEXES:
		# determine which map hex this viewport hex displays
		(map_hx, map_hy) = scenario.map_vp[(vp_hx, vp_hy)]
		# hex is off-map
		if (map_hx, map_hy) not in scenario.cd_hex.map_hexes: continue
		# get the map hex
		map_hex = scenario.cd_hex.map_hexes[(map_hx, map_hy)]
		
		# any units in the stack
		if len(map_hex.unit_stack) != 0:
			# display the top unit in the stack
			unit = map_hex.unit_stack[0]
			unit.DrawMe(vp_hx, vp_hy)
		
			# draw stack unit number indicator if this unit is not animating
			if unit.anim_x == 0 and unit.anim_y == 0 and len(map_hex.unit_stack) > 1:
				text = str(len(map_hex.unit_stack))
				if map_hex.unit_stack[0].turret_facing is not None:
					facing = map_hex.unit_stack[0].turret_facing
				else:
					facing = map_hex.unit_stack[0].facing
				facing = ConstrainDir(facing - scenario.vp_facing)
				if facing in [5,0,1]:
					y_mod = 1
				else:
					y_mod = -1
				x = map_hex.unit_stack[0].screen_x
				y = map_hex.unit_stack[0].screen_y + y_mod
				libtcod.console_set_default_foreground(unit_con, libtcod.grey)
				libtcod.console_set_default_background(unit_con, libtcod.black)
				ConsolePrintEx(unit_con, x, y, libtcod.BKGND_SET, libtcod.CENTER, text)
			
			# record vp and screen location of other units in the stack
			if len(map_hex.unit_stack) > 1:
				for unit in map_hex.unit_stack[1:]:
					unit.vp_hx = vp_hx
					unit.vp_hy = vp_hy
					(unit.screen_x, unit.screen_y) = PlotHex(vp_hx, vp_hy)
	
		# check for hex highlight
		if scenario.highlighted_hex is not None:
			if scenario.highlighted_hex == (map_hx, map_hy):
				(x,y) = PlotHex(vp_hx, vp_hy)
				libtcod.console_blit(hex_highlight, 0, 0, 0, 0, unit_con, x-3, y-2)
		
		# check for target hex display
		if scenario.player_target_hex is not None:
			if scenario.player_target_hex == (map_hx, map_hy):
				(x,y) = PlotHex(vp_hx, vp_hy)
				libtcod.console_put_char_ex(unit_con, x-1, y-1, 169, libtcod.red, libtcod.black)
				libtcod.console_put_char_ex(unit_con, x+1, y-1, 170, libtcod.red, libtcod.black)
				libtcod.console_put_char_ex(unit_con, x-1, y+1, 28, libtcod.red, libtcod.black)
				libtcod.console_put_char_ex(unit_con, x+1, y+1, 29, libtcod.red, libtcod.black)
		
	# display LoS if applicable
	if scenario.active_unit != scenario.player_unit: return
	if scenario.player_target is None: return
	if session.hide_player_los: return
	line = GetLine(scenario.player_unit.screen_x, scenario.player_unit.screen_y,
		scenario.player_target.screen_x, scenario.player_target.screen_y)
	for (x,y) in line[2:-1]:
		libtcod.console_put_char_ex(unit_con, x, y, 250, libtcod.red,
			libtcod.black)


# display information about the player unit
def UpdatePlayerInfoCon():
	libtcod.console_clear(player_info_con)
	scenario.player_unit.DisplayMyInfo(player_info_con, 0, 0)


# update crew position console 24x26
# display player unit crew positions and current crewmen if any
def UpdateCrewPositionCon():
	libtcod.console_clear(crew_position_con)
	
	# no crew positions in this unit
	if len(scenario.player_unit.crew_positions) == 0: return
	
	DisplayCrew(scenario.player_unit, crew_position_con, 0, 1, True)


# list current player commands
def UpdateCommandCon():
	libtcod.console_set_default_foreground(command_con, libtcod.white)
	libtcod.console_set_default_background(command_con, libtcod.black)
	libtcod.console_clear(command_con)
	
	# no menu if enemy is active
	if scenario.game_turn['active_player'] == 1:
		return
	
	# menu title
	libtcod.console_set_default_background(command_con, libtcod.dark_blue)
	libtcod.console_rect(command_con, 0, 0, 24, 1, True, libtcod.BKGND_SET)
	libtcod.console_set_default_background(command_con, libtcod.black)
	ConsolePrint(command_con, 0, 0, 'Crewman Actions')
	
	crewman = campaign.player_unit.crew_positions[campaign.selected_position].crewman
	if crewman is not None:
		
		y = 2
		
		# no actions possible
		if len(crewman.action_list) == 0:
			libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
			ConsolePrint(command_con, 1, y, 'None Available')
		else:
			for (command_key, text) in crewman.action_list:
				libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
				ConsolePrint(command_con, 1, y, command_key)
				libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
				ConsolePrint(command_con, 3, y, text)
				y += 1
	
	libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
	ConsolePrint(command_con, 1, 10, 'Enter')
	libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
	ConsolePrint(command_con, 7, 10, 'End Turn')
	
	return
	
	
	# command menu
	if scenario.active_menu == 1:
		
		# air or artillery support sub-menu active
		if scenario.airsup_menu_active or scenario.artsup_menu_active:
		
			libtcod.console_set_default_foreground(command_con, libtcod.white)
			if scenario.airsup_menu_active:
				ConsolePrint(command_con, 1, 2, 'Air Support')
			else:
				ConsolePrint(command_con, 1, 2, 'Artillery Support')
			
			# if artillery support in progress, only option is to cancel
			if scenario.player_artsup_success:
				libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
				ConsolePrint(command_con, 1, 4, 'C')
				libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
				ConsolePrint(command_con, 5, 4, 'Cancel Attack')
			
			# if air support in progress, no other options
			elif scenario.player_airsup_success:
				pass
			
			else:
				libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
				ConsolePrint(command_con, 1, 4, 'R')
				ConsolePrint(command_con, 1, 5, EncodeKey('a').upper() + '/' + EncodeKey('d').upper())
				libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
				ConsolePrint(command_con, 5, 4, 'Request Attack')
				ConsolePrint(command_con, 5, 5, 'Select Target Hex')
				
			libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
			ConsolePrint(command_con, 1, 8, 'Q')
			libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
			ConsolePrint(command_con, 7, 8, 'Exit sub-menu')
		
		# root command menu
		else:
		
			libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
			ConsolePrint(command_con, 1, 2, 'A')
			ConsolePrint(command_con, 1, 3, 'R')
			ConsolePrint(command_con, 1, 7, 'X')
			
			libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
			ConsolePrint(command_con, 5, 2, 'Air Support')
			ConsolePrint(command_con, 5, 3, 'Artillery Support')
			ConsolePrint(command_con, 5, 7, 'Abandon Tank')
			
	# crew action menu
	elif scenario.active_menu == 2:
		
		libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
		ConsolePrint(command_con, 1, 2, EncodeKey('w').upper() + '/' + EncodeKey('s').upper())
		ConsolePrint(command_con, 1, 3, EncodeKey('a').upper() + '/' + EncodeKey('d').upper())
		ConsolePrint(command_con, 1, 4, 'E')
		
		libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
		ConsolePrint(command_con, 5, 2, 'Select Crew')
		ConsolePrint(command_con, 5, 3, 'Set Action')
		ConsolePrint(command_con, 5, 4, 'Exposed/Button Up')
	
	# movement
	elif scenario.active_menu == 3:
		
		libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
		ConsolePrint(command_con, 1, 2, EncodeKey('w').upper() + '/' + EncodeKey('s').upper())
		ConsolePrint(command_con, 1, 3, EncodeKey('a').upper() + '/' + EncodeKey('d').upper())
		ConsolePrint(command_con, 1, 4, 'H')
		
		libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
		ConsolePrint(command_con, 6, 2, 'Forward/Backward')
		ConsolePrint(command_con, 6, 3, 'Pivot Hull')
		ConsolePrint(command_con, 6, 4, 'Attempt Hull Down')
		
	# combat
	elif scenario.active_menu == 4:
		
		libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
		ConsolePrint(command_con, 1, 2, EncodeKey('w').upper() + '/' + EncodeKey('s').upper())
		ConsolePrint(command_con, 1, 3, EncodeKey('q').upper() + '/' + EncodeKey('e').upper())
		ConsolePrint(command_con, 1, 4, EncodeKey('a').upper() + '/' + EncodeKey('d').upper())
		ConsolePrint(command_con, 1, 5, EncodeKey('z').upper() + '/' + EncodeKey('c').upper())
		ConsolePrint(command_con, 1, 6, 'F')
		
		libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
		ConsolePrint(command_con, 6, 2, 'Select Weapon')
		ConsolePrint(command_con, 6, 3, 'Rotate Turret')
		ConsolePrint(command_con, 6, 4, 'Select Target')
		ConsolePrint(command_con, 6, 5, 'Select Ammo')
		ConsolePrint(command_con, 6, 6, 'Fire')
		
	
	
	
# draw information about the hex currently under the mouse cursor to the hex terrain info
# console, 16x10
def UpdateHexTerrainCon():
	libtcod.console_clear(hex_terrain_con)
	
	# mouse cursor outside of map area
	if mouse.cx < 32: return
	x = mouse.cx - 31
	y = mouse.cy - 4
	
	if (x,y) not in scenario.hex_map_index:
		# possible hex edge info
		col = libtcod.console_get_char_background(map_vp_con, x, y)
		if col == RIVER_BG_COL:
			ConsolePrint(hex_terrain_con, 0, 0, 'River')
		return
	
	libtcod.console_set_default_foreground(hex_terrain_con, libtcod.white)
	
	(hx, hy) = scenario.hex_map_index[(x,y)]
	map_hex = scenario.cd_hex.map_hexes[(hx, hy)]
	text = HEX_TERRAIN_DESC[map_hex.terrain_type]
	ConsolePrint(hex_terrain_con, 0, 0, text)
	
	# FUTURE: display hex coordinate in production version?
	ConsolePrint(hex_terrain_con, 0, 1, str(hx) + ',' + str(hy))
	
	# elevation
	text = str(map_hex.elevation * ELEVATION_M) + ' m.'
	ConsolePrintEx(hex_terrain_con, 15, 1, libtcod.BKGND_NONE,
		libtcod.RIGHT, text)
	
	if hx == 0 and hy == 0:
		ConsolePrint(hex_terrain_con, 0, 3, 'Objective')
	
	if len(map_hex.dirt_roads) > 0:
		ConsolePrint(hex_terrain_con, 0, 8, 'Dirt Road')
	if len(map_hex.railroads) > 0:
		ConsolePrint(hex_terrain_con, 0, 9, 'Railroad')


# draw information based on current turn phase to contextual info console
def UpdateContextCon():
	libtcod.console_clear(context_con)
	libtcod.console_set_default_foreground(context_con, libtcod.white)
	
	# enemy player active
	if scenario.game_turn['active_player'] == 1:
		return
	
	crewman = campaign.player_unit.crew_positions[campaign.selected_position].crewman
	
	# no player crewman in selected position
	if crewman is None: return
	
	libtcod.console_set_default_background(context_con, libtcod.darker_blue)
	libtcod.console_rect(context_con, 0, 0, 16, 1, True, libtcod.BKGND_SET)
	ConsolePrint(context_con, 0, 0, crewman.current_position.name)
	libtcod.console_set_default_background(context_con, libtcod.black)
	
	# Driver position active
	if crewman.current_position.name == 'Driver':
		
		# display movement status
		libtcod.console_set_default_foreground(context_con, libtcod.light_green)
		if scenario.player_unit.move_finished:
			ConsolePrint(context_con, 0, 2, 'Move finished')
			return
		if scenario.player_unit.fired:
			ConsolePrint(context_con, 0, 2, 'Already Fired')
			return
		
		# display HD chance if any in current terrain
		chance = scenario.player_unit.GetHullDownChance()
		if chance > 0.0:
			ConsolePrint(context_con, 0, 2, 'HD Chance: ' + str(chance) + '%%')
		
		# see if there's a hex in front of us
		(hx, hy) = GetAdjacentHex(scenario.player_unit.hx, scenario.player_unit.hy,
			scenario.player_unit.facing)
		if (hx, hy) not in scenario.cd_hex.map_hexes: return
		
		libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
		ConsolePrint(context_con, 0, 4, 'Terrain ahead:')
		
		# display destination terrain type
		text = HEX_TERRAIN_DESC[scenario.cd_hex.map_hexes[(hx, hy)].terrain_type]
		ConsolePrint(context_con, 1, 5, text)
		
		# display road status if any
		if scenario.player_unit.facing in scenario.cd_hex.map_hexes[(scenario.player_unit.hx, scenario.player_unit.hy)].dirt_roads:
			ConsolePrint(context_con, 1, 6, 'Dirt Road')
		
		# display chance of getting a bonus move
		chance = round(scenario.CalcBonusMove(scenario.player_unit, hx, hy), 2)
		ConsolePrint(context_con, 0, 7, '+1 move: ' + str(chance) + '%%')
		
		
		
		
	
	# TEMP
	return
	
	# no menu active
	if scenario.active_menu == 0:
		return
	
	# command menu
	elif scenario.active_menu == 1:
		libtcod.console_set_default_background(context_con, libtcod.Color(130, 0, 180))
		libtcod.console_rect(context_con, 0, 0, 16, 1, True, libtcod.BKGND_SET)
		libtcod.console_set_default_background(context_con, libtcod.black)
		
		if scenario.airsup_menu_active:
			ConsolePrint(context_con, 0, 0, 'Air Support')
			
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			ConsolePrint(context_con, 0, 2, 'Level: ' + str(campaign_day.air_support_level))
			
			if scenario.player_airsup_failed:
				ConsolePrint(context_con, 0, 4, 'Request failed')
			elif scenario.player_airsup_success:
				ConsolePrint(context_con, 0, 4, 'Support inbound')
			
		else:
			
			ConsolePrint(context_con, 0, 0, 'Command')
			
			
	# crew actions
	elif scenario.active_menu == 2:
		position = scenario.player_unit.crew_positions[campaign.selected_position]
		action = position.crewman.current_action
		
		libtcod.console_set_default_background(context_con, libtcod.darker_yellow)
		libtcod.console_rect(context_con, 0, 0, 16, 1, True, libtcod.BKGND_SET)
		ConsolePrint(context_con, 0, 0, 'Crew Action')
		libtcod.console_set_default_background(context_con, libtcod.black)
		
		
		# TODO: is this even possible any more??
		if action is None:
			ConsolePrint(context_con, 0, 2, 'No action')
			ConsolePrint(context_con, 0, 3, 'assigned')
		else:
			libtcod.console_set_default_foreground(context_con,
				libtcod.dark_yellow)
			ConsolePrint(context_con, 0, 2, action)
			libtcod.console_set_default_foreground(context_con,
				libtcod.light_grey)
			
			lines = wrap(CREW_ACTIONS[action]['desc'], 16)
			y = 3
			for line in lines:
				ConsolePrint(context_con, 0, y, line)
				y += 1
				if y == 8: break
			
			if position.crewman.action_bonus_used:
				ConsolePrint(context_con, 0, 9, 'Bonus used')
	
	# movement
	elif scenario.active_menu == 3:
		
		pass
	
	# combat
	elif scenario.active_menu == 4:
		if scenario.selected_weapon is None: return
		
		weapon = scenario.selected_weapon
		
		libtcod.console_set_default_background(context_con, libtcod.darkest_red)
		libtcod.console_rect(context_con, 0, 0, 16, 1, True, libtcod.BKGND_SET)
		ConsolePrint(context_con, 0, 0, weapon.stats['name'])
		libtcod.console_set_default_background(context_con, libtcod.black)
		
		if weapon.GetStat('mount') is not None:
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			ConsolePrint(context_con, 0, 1, weapon.stats['mount'])
		
		# if gun, display current ammo stats
		if weapon.GetStat('type') == 'Gun':
			
			# current active ammo type
			if weapon.current_ammo is not None:
				ConsolePrintEx(context_con, 14, 0, libtcod.BKGND_NONE,
					libtcod.RIGHT, weapon.current_ammo)
			
			# general stores
			y = 2
			for ammo_type in AMMO_TYPES:
				if ammo_type in weapon.ammo_stores:
					libtcod.console_set_default_foreground(context_con, libtcod.white)
					ConsolePrint(context_con, 0, y, ammo_type)
					libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
					ConsolePrintEx(context_con, 7, y, libtcod.BKGND_NONE,
						libtcod.RIGHT, str(weapon.ammo_stores[ammo_type]))
					y += 1
			y += 1
			ConsolePrint(context_con, 0, y, 'Max')
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			ConsolePrintEx(context_con, 7, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, weapon.stats['max_ammo'])
			
			# TODO: display contents of ready rack if any
			
		if scenario.player_target is None: return
		
		# check if this attack could proceed
		scenario.player_attack_desc = scenario.CheckAttack(scenario.player_unit,
			weapon, scenario.player_target)
		if scenario.player_attack_desc == '': return
		
		libtcod.console_set_default_foreground(context_con, libtcod.red)
		lines = wrap(scenario.player_attack_desc, 16)
		y = 7
		for line in lines[:3]:
			ConsolePrint(context_con, 0, y, line)
			y += 1
		libtcod.console_set_default_foreground(context_con, libtcod.light_grey)

>>>>>>> 6fb365a465b82191e802d0b528c9965c0c8558f0



	
	
# draw all layers of scenario display to screen
def UpdateScenarioDisplay():
	libtcod.console_clear(con)
	libtcod.console_blit(bkg_console, 0, 0, 0, 0, con, 0, 0)		# grey outline
	libtcod.console_blit(player_info_con, 0, 0, 0, 0, con, 1, 1)		# player unit info
	libtcod.console_blit(crew_position_con, 0, 0, 0, 0, con, 1, 20)		# crew position info
	libtcod.console_blit(command_con, 0, 0, 0, 0, con, 1, 47)		# player commands
	
	# map viewport layers
	libtcod.console_blit(map_vp_con, 0, 0, 0, 0, con, 31, 4)		# map viewport
	libtcod.console_blit(fov_con, 0, 0, 0, 0, con, 31, 4, FOV_SHADE, FOV_SHADE)	# player FoV layer
	libtcod.console_blit(unit_con, 0, 0, 0, 0, con, 31, 4, 1.0, 0.0)	# unit layer
	
	# informational consoles surrounding the map viewport
	libtcod.console_blit(context_con, 0, 0, 0, 0, con, 27, 1)		# contextual info
	libtcod.console_blit(unit_info_con, 0, 0, 0, 0, con, 27, 50)		# unit info
	libtcod.console_blit(objective_con, 0, 0, 0, 0, con, 74, 1)		# target info
	libtcod.console_blit(hex_terrain_con, 0, 0, 0, 0, con, 74, 50)		# hex terrain info
	
	# draw current time and weather conditions directly to console
	# FUTURE: use time_weather_con generated by campaign day
	text = str(campaign.calendar['hour']).zfill(2) + ':' + str(campaign.calendar['minute']).zfill(2)
	ConsolePrint(con, 56, 1, text)
	ConsolePrintEx(con, 58, 2, libtcod.BKGND_NONE, libtcod.CENTER, 'Clear')
	
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)



##########################################################################################
#                                 Main Scenario Loop                                     #
##########################################################################################

def DoScenario():
	
	global bkg_console, map_vp_con, unit_con, player_info_con, hex_terrain_con
	global crew_position_con, command_con, context_con, unit_info_con, objective_con
	global attack_con, fov_con, hex_fov, hex_objective
	global hex_highlight
	global tile_offmap
	
	# set up consoles
	
	# background outline console for left column
	bkg_console = LoadXP('bkg.xp')
	# black mask for map tiles not visible to player
	hex_fov = LoadXP('hex_fov.xp')
	libtcod.console_set_key_color(hex_fov, libtcod.black)
	
	# highlight for objective hexes
	hex_objective = LoadXP('hex_objective.xp')
	libtcod.console_set_key_color(hex_objective, KEY_COLOR)
	
	# highlight for in-game messages
	hex_highlight = LoadXP('hex_highlight.xp')
	libtcod.console_set_key_color(hex_highlight, KEY_COLOR)
	
	# map viewport console
	map_vp_con = libtcod.console_new(55, 53)
	libtcod.console_set_default_background(map_vp_con, libtcod.black)
	libtcod.console_set_default_foreground(map_vp_con, libtcod.white)
	libtcod.console_clear(map_vp_con)
	
	# indicator for off-map tiles on viewport
	tile_offmap = LoadXP('tile_offmap.xp')
	libtcod.console_set_key_color(tile_offmap, KEY_COLOR)
	
	# unit layer console
	unit_con = libtcod.console_new(55, 53)
	libtcod.console_set_default_background(unit_con, KEY_COLOR)
	libtcod.console_set_default_foreground(unit_con, libtcod.white)
	libtcod.console_set_key_color(unit_con, KEY_COLOR)
	libtcod.console_clear(unit_con)
	
	# player Field of View mask console
	fov_con = libtcod.console_new(55, 53)
	libtcod.console_set_default_background(fov_con, libtcod.black)
	libtcod.console_set_default_foreground(fov_con, libtcod.black)
	libtcod.console_set_key_color(fov_con, KEY_COLOR)
	libtcod.console_clear(fov_con)
	
	# player info console
	player_info_con = libtcod.console_new(24, 18)
	libtcod.console_set_default_background(player_info_con, libtcod.black)
	libtcod.console_set_default_foreground(player_info_con, libtcod.white)
	libtcod.console_clear(player_info_con)
	
	# crew position console
	crew_position_con = libtcod.console_new(24, 26)
	libtcod.console_set_default_background(crew_position_con, libtcod.black)
	libtcod.console_set_default_foreground(crew_position_con, libtcod.white)
	libtcod.console_clear(crew_position_con)
	
	# player command console
	command_con = libtcod.console_new(24, 12)
	libtcod.console_set_default_background(command_con, libtcod.black)
	libtcod.console_set_default_foreground(command_con, libtcod.white)
	libtcod.console_clear(command_con)
	
	# hex terrain info console
	hex_terrain_con = libtcod.console_new(16, 10)
	libtcod.console_set_default_background(hex_terrain_con, libtcod.black)
	libtcod.console_set_default_foreground(hex_terrain_con, libtcod.white)
	libtcod.console_clear(hex_terrain_con)
	
	# unit info console
	unit_info_con = libtcod.console_new(16, 10)
	libtcod.console_set_default_background(unit_info_con, libtcod.black)
	libtcod.console_set_default_foreground(unit_info_con, libtcod.white)
	libtcod.console_clear(unit_info_con)
	
	# contextual info console
	context_con = libtcod.console_new(16, 10)
	libtcod.console_set_default_background(context_con, libtcod.black)
	libtcod.console_set_default_foreground(context_con, libtcod.white)
	libtcod.console_clear(context_con)
	
	# objective info console
	objective_con = libtcod.console_new(16, 10)
	libtcod.console_set_default_background(objective_con, libtcod.black)
	libtcod.console_set_default_foreground(objective_con, libtcod.white)
	libtcod.console_clear(objective_con)
	
	# attack display console
	attack_con = libtcod.console_new(26, 60)
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.white)
	libtcod.console_clear(attack_con)
	
	# create a global pointer
	global scenario
	scenario = campaign_day.scenario
	
	# init scenario if not already; only called when started a new one, not when loading from saved
	if not scenario.init_complete:
		
		# generate hex map if needed
		if scenario.cd_hex.map_hexes == {}:
			scenario.cd_hex.GenerateHexMap()
		
		# generate scenario units
		
		# spawn player tank into scenario
		scenario.player_unit = campaign.player_unit
		
		(hx, hy) = scenario.cd_hex.entry_hexes[scenario.source_direction]
		
		campaign.player_unit.InitScenarioStats()
		scenario.units.append(campaign.player_unit)
		campaign.player_unit.SpawnAt(hx, hy)
		
		# set facing toward center of map
		direction = GetDirectionToward(hx, hy, 0, 0)
		campaign.player_unit.facing = direction
		if 'turret' in campaign.player_unit.stats:
			campaign.player_unit.turret_facing = direction
		
		campaign.player_unit.CheckHullDownGain()
		campaign.player_unit.CalcFoV()
		
		# spawn rest of player group
		for unit in campaign.player_unit_group:
			unit.InitScenarioStats()
			unit.facing = 0
			unit.turret_facing = 0
			scenario.units.append(unit)
			unit.SpawnAt(hx, hy)
			unit.CheckHullDownGain()
			unit.CalcFoV()
		
		# set up VP hexes and generate initial VP console
		scenario.CenterVPOnPlayer()
		scenario.SetVPHexes()
		
		# generate and spawn initial enemy units for this scenario
		scenario.SpawnEnemyUnits()
		
		# set activation order
		scenario.GenerateActivationOrder()
	
	# do this for both new and loaded scenarios
	session.GenerateHexConsoles()
	UpdateVPCon()
	UpdateUnitCon()
	UpdatePlayerInfoCon()
	UpdateCrewPositionCon()
	UpdateCommandCon()
	UpdateContextCon()
	UpdateUnitInfoCon()
	UpdateObjectiveInfoCon()
	UpdateScenarioDisplay()
	libtcod.console_flush()
	
		
	# only do if starting a new scenario
	if not scenario.init_complete:
		
		# activate player unit
		scenario.active_unit = scenario.player_unit
		scenario.active_unit.DoPreActivation()
		
		scenario.init_complete = True
		
		SaveGame()
	
	# record mouse cursor position to check when it has moved
	mouse_x = -1
	mouse_y = -1
	
	exit_scenario = False
	while not exit_scenario:
		
		# emergency exit in case of endless loop
		if libtcod.console_is_window_closed(): sys.exit()
		
		libtcod.console_flush()
		
		# check if scenario end conditions have been met
		if scenario.finished:
			text = 'The scenario is over: ' + scenario.win_desc
			ShowNotification(text)
			exit_scenario = True
			
			# have each unit in the player unit group recover
			for unit in campaign.player_unit_group:
				if unit.alive:
					unit.InitPostScenario()
			continue
		
		# if player is not active, do AI actions
		if scenario.game_turn['active_player'] == 1:
			UpdateCommandCon()
			UpdateUnitCon()
			for unit in scenario.activation_list[1]:
				if not unit.alive: continue
				unit.ai.DoActivation()
				# pause a short time between enemy unit activations
				Wait(5)
			scenario.DoEndOfPlayerTurn()
			
			# clear keyboard events
			FlushKeyboardEvents()
			
			# check for random event
			scenario.RandomEventRoll()
			
			# activate player again
			scenario.active_unit = scenario.player_unit
			scenario.active_unit.MoveToTopOfStack()
			UpdateUnitCon()
			UpdateScenarioDisplay()
			libtcod.console_flush()
			scenario.active_unit.DoPreActivation()
			
			UpdatePlayerInfoCon()
			UpdateContextCon()
			UpdateObjectiveInfoCon()
			UpdateCrewPositionCon()
			UpdateCommandCon()
			UpdateUnitCon()
			UpdateScenarioDisplay()
			continue
		
		# get keyboard and/or mouse event
		keypress = GetInputEvent()
		
		# check to see if mouse cursor has moved
		if mouse.cx != mouse_x or mouse.cy != mouse_y:
			mouse_x = mouse.cx
			mouse_y = mouse.cy
			UpdateHexTerrainCon()
			UpdateUnitInfoCon()
			UpdateScenarioDisplay()
		
		# check to see if mouse wheel has moved
		if mouse.wheel_up or mouse.wheel_down:
			
			# see if cursor is over a hex with 2+ units in it
			x = mouse.cx - 31
			y = mouse.cy - 4
			if (x,y) in scenario.hex_map_index:
				(hx, hy) = scenario.hex_map_index[(x,y)]
				map_hex = scenario.cd_hex.map_hexes[(hx, hy)]
				if len(map_hex.unit_stack) > 1:
					if mouse.wheel_up:
						map_hex.unit_stack[:] = map_hex.unit_stack[1:] + [map_hex.unit_stack[0]]
					else:
						map_hex.unit_stack.insert(0, map_hex.unit_stack.pop(-1))
					UpdateUnitCon()
					UpdateUnitInfoCon()
					UpdateScenarioDisplay()
			continue
		
		# mouse button clicked
		if mouse.rbutton_pressed:
			x = mouse.cx - 31
			y = mouse.cy - 4
			if (x,y) in scenario.hex_map_index:
				(hx, hy) = scenario.hex_map_index[(x,y)]
				map_hex = scenario.cd_hex.map_hexes[(hx, hy)]
				if len(map_hex.unit_stack) > 0:
					unit = map_hex.unit_stack[0]
					if not (unit.owning_player == 1 and not unit.known):
						# display info on top unit in stack
						scenario.ShowUnitInfoWindow(unit)
					continue
		
		
		##### Player Keyboard Commands #####
		if not keypress: continue
		
		# Determine action based on key pressed
		
		# enter game menu
		if key.vk in [libtcod.KEY_ESCAPE, libtcod.KEY_F1, libtcod.KEY_F2, libtcod.KEY_F3]:
			
			result = ShowGameMenu()
			
			if result == 'exit_game':
				exit_scenario = True
			else:
				# re-draw to clear game menu from screen
				UpdateScenarioDisplay()
			continue
		
		# end player unit activation
		if key.vk == libtcod.KEY_ENTER:
			scenario.player_unit.DoPostActivation()
			
			# activate allied player units
			for unit in scenario.activation_list[0]:
				if not unit.alive: continue
				unit.ai.DoActivation()
			
			scenario.DoEndOfPlayerTurn()
			continue

		# key commands
		key_char = chr(key.c).lower()
		
		# activate a different crew position
		if key_char in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
			n = int(key_char)
			if n == 0: n = 10
			if scenario.player_unit.crew_positions == n-1: continue
			if len(scenario.player_unit.crew_positions) >= n:
				campaign.selected_position = n - 1
				UpdateCommandCon()
				UpdateContextCon()
				UpdateCrewPositionCon()
				UpdateScenarioDisplay()
			continue
		
		# map key to current keyboard layout and capitalize
		key_char = DecodeKey(key_char).upper()
		
		# check to see if command is in possible crew actions
		crewman = campaign.player_unit.crew_positions[campaign.selected_position].crewman
		if crewman is None: continue
		
		# find the selected action in the list of crew actions
		for (command_key, action) in crewman.action_list:
			if key_char == command_key:
				
				# Driver Actions
				
				# move player unit forward / backward
				if action in ['Move Forward', 'Move Backward']:
				
					reverse = False
					if action == 'Move Backward':
						reverse = True
					
					if scenario.player_unit.MoveForward(reverse):
						scenario.RebuildPlayerTargetList()
						UpdatePlayerInfoCon()
						UpdateContextCon()
						UpdateCrewPositionCon()
						scenario.CenterVPOnPlayer()
						scenario.SetVPHexes()
						UpdateVPCon()
						UpdateUnitCon()
						UpdateObjectiveInfoCon()
						UpdateHexTerrainCon()
						UpdateScenarioDisplay()
						libtcod.console_flush()
						SaveGame()
				
				# pivot hull facing
				elif action in ['Pivot Port', 'Pivot Stb']:
				
					if action == 'Pivot Port':
						result = scenario.player_unit.Pivot(False)
					else:
						result = scenario.player_unit.Pivot(True)
					if result:
						scenario.RebuildPlayerTargetList()
						scenario.CenterVPOnPlayer()
						scenario.SetVPHexes()
						UpdatePlayerInfoCon()
						UpdateContextCon()
						UpdateVPCon()
						UpdateUnitCon()
						UpdateObjectiveInfoCon()
						UpdateHexTerrainCon()
						UpdateScenarioDisplay()
				
				# attempt Hull Down
				elif action == 'Go Hull Down':
					
					# not possible
					if scenario.player_unit.GetHullDownChance() == 0.0: continue
					
					# attempt HD
					result = scenario.player_unit.CheckHullDownGain(direction=scenario.player_unit.facing)
					scenario.player_unit.moved = True
					scenario.player_unit.move_finished = True
					
					# was attempt successful
					if result:
						text = 'You move into a Hull Down position.'
					else:
						text = 'You were unable to move into a Hull Down position.'
					Message(text, hx=scenario.player_unit.hx, hy=scenario.player_unit.hy, no_log=True)
					UpdatePlayerInfoCon()
					UpdateContextCon()
					UpdateVPCon()
					UpdateUnitInfoCon()
					UpdateScenarioDisplay()	
		
		
		# TEMP
		continue
		
		
		# command actions
		if scenario.active_menu == 1:
			
			# air or artillery support sub-menu
			if scenario.airsup_menu_active or scenario.artsup_menu_active:
				
				# if artillery support in progress, only option is to cancel
				if scenario.player_artsup_success:
					
					# cancel request
					if chr(key.c).lower() == 'c':
						scenario.player_artsup_success = False
						scenario.player_artsup_failed = True
						UpdateCommandCon()
						UpdateUnitCon()
						UpdateScenarioDisplay()
						text = 'Artillery support request cancelled.'
						Message(text, no_log=True)
						continue
				
				# if air support inbound, don't allow these options
				elif not scenario.player_airsup_success:
				
					# select target hex
					if key_char in ['a', 'd'] or key.vk in [libtcod.KEY_LEFT, libtcod.KEY_RIGHT]:
						reverse = False
						if key_char == 'a' or key.vk == libtcod.KEY_LEFT:
							reverse = True
						scenario.SelectNextTargetHex(reverse)
						UpdateUnitCon()
						UpdateScenarioDisplay()
					
					# request support
					if chr(key.c).lower() == 'r':
						
						if scenario.airsup_menu_active:
							result = scenario.RequestAirSup()
						else:
							result = scenario.RequestArtySup()
						
						if result:
							UpdateCommandCon()
							UpdateContextCon()
							UpdateScenarioDisplay()
				
				# close sub-menu
				if chr(key.c).lower() == 'q':
					if scenario.airsup_menu_active:
						scenario.airsup_menu_active = False
					else:
						scenario.artsup_menu_active = False
					UpdateCommandCon()
					UpdateContextCon()
					UpdateScenarioDisplay()
			
			# root command menu
			else:
				# open air support sub-menu
				if chr(key.c).lower() == 'a':
					if campaign_day.air_support_level > 0.0:
						scenario.airsup_menu_active = True
						UpdateCommandCon()
						UpdateContextCon()
						UpdateScenarioDisplay()
				
				# open artillery support sub-menu
				elif chr(key.c).lower() == 'r':
					if campaign_day.arty_support_level > 0.0:
						scenario.artsup_menu_active = True
						UpdateCommandCon()
						UpdateContextCon()
						UpdateScenarioDisplay()
				
				# abandon tank
				elif chr(key.c).lower() == 'x':
					result = ShowNotification('Abandon your tank and end the combat day?', confirm=True)
					
					# cancel command
					if not result:
						libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
						continue
					
					campaign_day.scenario.winner = 1
					campaign_day.abandoned_tank = True
					
					ShowNotification('You abandon your tank and return to friendly lines.')
					exit_scenario = True
			
		# crew actions
		elif scenario.active_menu == 2:
			
			# change selected crewman
			if key_char in ['w', 's'] or key.vk in [libtcod.KEY_UP, libtcod.KEY_DOWN]:
			
				if key_char == 'w' or key.vk == libtcod.KEY_UP:
					if campaign.selected_position > 0:
						campaign.selected_position -= 1
					else:
						campaign.selected_position = len(campaign.player_unit.crew_positions) - 1
				
				else:
					if campaign.selected_position == len(campaign.player_unit.crew_positions) - 1:
						campaign.selected_position = 0
					else:
						campaign.selected_position += 1
				UpdateContextCon()
				UpdateCrewPositionCon()
				UpdateScenarioDisplay()
			
			# toggle BU/CE for this crewman
			elif chr(key.c).lower() == 'e':
				
				position = scenario.player_unit.crew_positions[campaign.selected_position]
				if position.crewman is not None:
					if position.crewman.ToggleCE():
						UpdateCrewPositionCon()
						scenario.player_unit.CalcFoV()
						UpdateVPCon()
						UpdateScenarioDisplay()
		
		# combat
		elif scenario.active_menu == 4:
			
			# select weapon
			if key_char in ['w', 's'] or key.vk in [libtcod.KEY_UP, libtcod.KEY_DOWN]:
				if key_char == 'w' or key.vk == libtcod.KEY_UP:
					result = scenario.SelectNextWeapon(False)
				else:
					result = scenario.SelectNextWeapon(True)
				if result:
					UpdateContextCon()
					UpdateScenarioDisplay()
			
			# rotate turret facing
			elif key_char in ['q', 'e']:
				if key_char == 'q':
					result = scenario.player_unit.RotateTurret(False)
				else:
					result = scenario.player_unit.RotateTurret(True)
				if result:
					scenario.RebuildPlayerTargetList()
					UpdateUnitCon()
					UpdateContextCon()
					UpdateVPCon()
					UpdateScenarioDisplay()
			
			# select target
			elif key_char in ['a', 'd'] or key.vk in [libtcod.KEY_LEFT, libtcod.KEY_RIGHT]:
				if key_char == 'a' or key.vk == libtcod.KEY_LEFT:
					result = scenario.SelectNextTarget(False)
				else:
					result = scenario.SelectNextTarget(True)
				if result:
					UpdateContextCon()
					UpdateUnitCon()
					UpdateScenarioDisplay()
			
			# select ammo type
			elif key_char in ['z', 'c'] or key.vk in [libtcod.KEY_PAGEUP, libtcod.KEY_PAGEDOWN]:
				if key_char == 'z' or key.vk == libtcod.KEY_PAGEUP:
					result = scenario.selected_weapon.SelectAmmoType(False)
				else:
					result = scenario.selected_weapon.SelectAmmoType(True)
				if result:
					UpdateContextCon()
					UpdateScenarioDisplay()
			
			# fire the active weapon at the selected target
			elif chr(key.c).lower() == 'f':
				result = scenario.player_unit.Attack(scenario.selected_weapon,
					scenario.player_target)
				if result:
					UpdateContextCon()
					UpdatePlayerInfoCon()
					UpdateCrewPositionCon()
					UpdateVPCon()
					UpdateUnitCon()
					UpdateScenarioDisplay()
					SaveGame()



##########################################################################################
#                                      Main Script                                       #
##########################################################################################

global keyboard_decode, keyboard_encode
global session, scenario

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

# generate keyboard mapping dictionaries
GenerateKeyboards()

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

# create a new scenario
scenario = Scenario()

# run the scenario
scenario.DoScenarioLoop()


print(NAME + ' version ' + VERSION + ' shutting down')			# shutdown message
# END #

