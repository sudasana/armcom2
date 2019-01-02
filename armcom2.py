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

