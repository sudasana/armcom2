# -*- coding: UTF-8 -*-
# Python 2.7.14 x64
# Libtcod 1.6.4 x64
##########################################################################################
#                                                                                        #
#                                Armoured Commander II                                   #
#                                                                                        #
##########################################################################################
#             Project Started February 23, 2016; Restarted July 25, 2016                 #
#                           Restarted again January 11, 2018                             #
##########################################################################################
#
#    Copyright (c) 2016-2018 Gregory Adam Scott (sudasana@gmail.com)
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
import libtcodpy as libtcod				# The Doryen Library
import ConfigParser					# saving and loading settings
from random import choice, shuffle, sample		# for randomness
from math import floor, cos, sin, sqrt			# math
from math import degrees, atan2, ceil			# heading calculations
import xp_loader, gzip					# loading xp image files
import json						# for loading JSON data
import time
from textwrap import wrap				# breaking up strings
import shelve						# saving and loading games

os.environ['PYSDL2_DLL_PATH'] = os.getcwd() + '/lib'.replace('/', os.sep)
import sdl2.sdlmixer as mixer				# sound effects



##########################################################################################
#                                        Constants                                       #
##########################################################################################

# Debug Flags
AI_SPY = False						# write description of AI actions to console
AI_NO_ACTION = False					# no AI actions at all
GODMODE = False						# player cannot be destroyed

NAME = 'Armoured Commander II'				# game name
VERSION = '0.1.0-2018-03-31'				# game version in Semantic Versioning format: http://semver.org/
DATAPATH = 'data/'.replace('/', os.sep)			# path to data files
SOUNDPATH = 'sounds/'.replace('/', os.sep)		# path to sound samples
CAMPAIGNPATH = 'campaigns/'.replace('/', os.sep)	# path to campaign files
LIMIT_FPS = 50						# maximum screen refreshes per second
WINDOW_WIDTH, WINDOW_HEIGHT = 90, 60			# size of game window in character cells
WINDOW_XM, WINDOW_YM = int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/2)	# center of game window


##### Hex geometry definitions #####

# directional and positional constants
DESTHEX = [(0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0)]	# change in hx, hy values for hexes in each direction
CD_DESTHEX = [(1,-1), (1,0), (0,1), (-1,1), (-1,0), (0,-1)]	# same for pointy-top campaign day hexes
PLOT_DIR = [(0,-1), (1,-1), (1,1), (0,1), (-1,1), (-1,-1)]	# position of direction indicator
TURRET_CHAR = [254, 47, 92, 254, 47, 92]			# characters to use for turret display

# coordinates for map viewport hexes, radius 6
VP_HEXES = [
	(0,0), (-1,1), (-1,0), (0,-1), (1,-1), (1,0), (0,1), (-2,2), (-2,1), (-2,0), (-1,-1),
	(0,-2), (1,-2), (2,-2), (2,-1), (2,0), (1,1), (0,2), (-1,2), (-3,3), (-3,2), (-3,1),
	(-3,0), (-2,-1), (-1,-2), (0,-3), (1,-3), (2,-3), (3,-3), (3,-2), (3,-1), (3,0),
	(2,1), (1,2), (0,3), (-1,3), (-2,3), (-4,4), (-4,3), (-4,2), (-4,1), (-4,0), (-3,-1),
	(-2,-2), (-1,-3), (0,-4), (1,-4), (2,-4), (3,-4), (4,-4), (4,-3), (4,-2), (4,-1),
	(4,0), (3,1), (2,2), (1,3), (0,4), (-1,4), (-2,4), (-3,4), (-5,5), (-5,4), (-5,3),
	(-5,2), (-5,1), (-5,0), (-4,-1), (-3,-2), (-2,-3), (-1,-4), (0,-5), (1,-5), (2,-5),
	(3,-5), (4,-5), (5,-5), (5,-4), (5,-3), (5,-2), (5,-1), (5,0), (4,1), (3,2), (2,3),
	(1,4), (0,5), (-1,5), (-2,5), (-3,5), (-4,5), (-6,6), (-6,5), (-6,4), (-6,3),
	(-6,2), (-6,1), (-6,0), (-5,-1), (-4,-2), (-3,-3), (-2,-4), (-1,-5), (0,-6), (1,-6),
	(2,-6), (3,-6), (4,-6), (5,-6), (6,-6), (6,-5), (6,-4), (6,-3), (6,-2), (6,-1),
	(6,0), (5,1), (4,2), (3,3), (2,4), (1,5), (0,6), (-1,6), (-2,6), (-3,6), (-4,6), (-5,6)
]

# pre-calculated hexpairs and second hex step for lines of sight along hexspines
HEXSPINES = {
	0: [(0,-1), (1,-1), (1,-2)],
	1: [(1,-1), (1,0), (2,-1)],
	2: [(1,0), (0,1), (1,1)],
	3: [(0,1), (-1,1), (-1,2)],
	4: [(-1,1), (-1,0), (-2,1)],
	5: [(-1,0), (0,-1), (-1,-1)]
}

# relative locations of edge cells in a given direction for a map hex
HEX_EDGE_CELLS = {
	0: [(-1,-2),(0,-2),(1,-2)],
	1: [(1,-2),(2,-1),(3,0)],
	2: [(3,0),(2,1),(1,2)],
	3: [(1,2),(0,2),(-1,2)],
	4: [(-1,2),(-2,1),(-3,0)],
	5: [(-3,0),(-2,-1),(-1,-2)]
}

# same for campaign day hexes (pointy-topped)
CD_HEX_EDGE_CELLS = {
	0: [(0,-4),(1,-3),(2,-2),(3,-1)],
	1: [(3,-1),(3,0),(3,1)],
	2: [(3,1),(2,2),(1,3),(0,4)],
	3: [(0,4),(-1,3),(-2,2),(-3,1)],
	4: [(-3,1),(-3,0),(-3,-1)],
	5: [(-3,-1),(-2,-2),(-1,-3),(0,-4)]
}

# hexes on campaign day map
CAMPAIGN_DAY_HEXES = [
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

ELEVATION_SHADE = 0.15					# difference in shading for map hexes of
							#   different elevations
FOV_SHADE = 0.5						# alpha level for FoV mask layer
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency
ACTION_KEY_COL = libtcod.Color(51, 153, 255)		# colour for key commands
PORTRAIT_BG_COL = libtcod.Color(217, 108, 0)		# background color for unit portraits
UNKNOWN_UNIT_COL = libtcod.grey				# unknown enemy unit display colour
ENEMY_UNIT_COL = libtcod.light_red			# known "
DIRT_ROAD_COL = libtcod.Color(50, 40, 25)		# background color for dirt roads
RIVER_BG_COL = libtcod.Color(0, 0, 217)			# background color for river edges


# list of possible keyboard layout settings
KEYBOARDS = ['QWERTY', 'AZERTY', 'QWERTZ', 'Dvorak']

# hex terrain types
HEX_TERRAIN_TYPES = [
	'openground', 'forest', 'fields_in_season', 'pond', 'roughground', 'village'
]

# descriptive text for terrain types
HEX_TERRAIN_DESC = {
	'openground' : 'Open Ground', 'forest' : 'Forest', 'fields_in_season' : 'Fields',
	'pond' : 'Pond', 'roughground' : 'Rough Ground', 'village' : 'Village'
}

# maximum length for randomly generated crew names
CREW_NAME_MAX_LENGTH = 20

# list of crew stat names
STAT_NAMES = ['Strength', 'Grit', 'Perception', 'Intelligence']

# list of scenario menus and their highlight colours
MENU_LIST = [
	('Command', 1, libtcod.Color(130, 0, 180)),
	('Crew Action', 2, libtcod.Color(140, 140, 0)),
	('Movement', 3, libtcod.Color(70, 140, 0)),
	('Combat', 4, libtcod.Color(180, 0, 45))
]

# list of campaign day menus and their highlight colours
CD_MENU_LIST = [
	('Support', 1, libtcod.Color(128, 128, 128)),
	('Crew', 2, libtcod.Color(140, 140, 0)),
	('Travel', 3, libtcod.Color(70, 140, 0)),
	('Group', 4, libtcod.Color(180, 0, 45)),
	('Supply', 5, libtcod.Color(128, 100, 64))
]

# list of commands for travel in campaign day
CD_TRAVEL_CMDS = [
	('e',2,-2,228), ('d',2,0,26), ('c',2,2,229), ('z',-2,2,230), ('a',-2,0,27), ('q',-2,-2,231)
]

# load crew action definitions
with open(DATAPATH + 'crew_action_defs.json') as data_file:
	CREW_ACTIONS = json.load(data_file)

# order to display ammo types
AMMO_TYPES = ['HE', 'AP']


#################################
##### Game Engine Constants #####
#################################

# TODO: move to a json file

# base chance of triggering a battle when entering an enemy-held hex on the campaign day map
CD_BATTLE_BASE_CHANCE = 45.0
# effect of each point of strength on chance
CD_BATTLE_STR_MOD = 4.0
# effect of each point of organization <> 5 on chance
CD_BATTLE_ORGANIZATION_MOD = 5.0

# of all enemy units initially spawned in a scenario, portion that are spawned as dummy units
ENEMY_DUMMY_RATIO = 0.25

# critical hit and miss thresholds
CRITICAL_HIT = 3.0
CRITICAL_MISS = 97.0

# base success chances for point fire attacks
# first column is for vehicle targets, second is everything else
PF_BASE_CHANCE = [
	[98.0, 88.0],			# same hex
	[92.0, 72.0],			# 1 hex range
	[89.5, 68.0],			# 2 hex range
	[83.0, 58.0],			# 3 "
	[72.0, 42.0],			# 4 "
	[58.0, 28.0],			# 5 "
	[42.0, 17.0]			# 6 "
]

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
	'75' : 120.0,		# not sure if this and below are accurate, TODO check balance
	'75L' : 160.0,
	'88L' : 200.0
}

# effective FP of an HE hit from different weapon calibres
HE_FP_EFFECT = [
	(75, 8),
	(70, 8),
	(65, 7),
	(60, 7),
	(57, 6),
	(50, 6),
	(45, 5),
	(37, 5),
	(30, 4),
	(25, 3),
	(20, 3)
]

# penetration chance on armour of HE hits
HE_AP_CHANCE = [
	(70, 58.4),
	(50, 41.7),
	(40, 27.8),
	(30, 16.7),
	
]

# maximum range for an MG attack to cause an AP hit on armoured target
MG_AP_RANGE = 2

# base chances of partial effect for area fire attacks: infantry/gun and vehicle targets
INF_FP_BASE_CHANCE = 30.0
VEH_FP_BASE_CHANCE = 20.0

# each additional firepower beyond 1 adds this additional chance
FP_CHANCE_STEP = 5.0
# additional firepower modifier reduced by this much beyond 1
FP_CHANCE_STEP_MOD = 0.95

# multiplier for full effect
FP_FULL_EFFECT = 0.75
# multipler for critical effect
FP_CRIT_EFFECT = 0.1

# base chance of a 1 firepower attack having no effect on a unit
RESOLVE_FP_BASE_CHANCE = 95.0
# each additional firepower beyond 1 subtracts this additional chance
RESOLVE_FP_CHANCE_STEP = 5.0
# additional firepower modifier increased by this much beyond 1
RESOLVE_FP_CHANCE_MOD = 1.05

# list of possible results from fp resolution, in addition to no effect
FP_EFFECT_RESULT_LIST = ['Pin Test', 'Destroyed']

# FUTURE full list:
#FP_EFFECT_RESULT_LIST = ['Pin Test', 'Break Test', 'Reduction', 'Destroyed']

# each point of FP applies this as a negative modifier to a morale check
FP_MORALE_CHECK_MOD = 5.0

# modifier to morale checks for broken units
BROKEN_MORALE_MOD = -40.0

# ranges for morale level descriptions
MORALE_LEVELS = {
	'Reluctant': (51.0, 60.9),
	'Regular': (61.0, 70.9),
	'Confident': (71.0, 80.9),
	'Fearless': (81.0, 90.9),
	'Fanatic': (91.0, 100.0)
}

# list of unit leader positions: they check morale first for the unit
UNIT_LEADER_POSITIONS = [
	'Commander', 'Commander/Gunner', 'NCO'
]

# visible distances for crewmen when buttoned up and exposed
MAX_BU_LOS_DISTANCE = 3
MAX_LOS_DISTANCE = 6

ELEVATION_M = 10.0			# each elevation level represents x meters of height

# percentile LoS modifiers for terrain types
TERRAIN_LOS_MODS = {
	'openground' : 0.0,
	'roughground' : 5.0,
	'forest' : 40.0,
	'village' : 30.0,
	'fields_in_season' : 20.0,
	'pond' : 10.0
}

# effective height in meters of terrain LoS modifiers
TERRAIN_LOS_HEIGHT = {
	'openground' : 0.0,
	'roughground' : 0.0,
	'forest' : 20.0,
	'village' : 12.0,
	'fields_in_season' : 5.0,
	'pond' : 3.0
}

# base chance of getting a bonus move when moving into terrain
TERRAIN_BONUS_CHANCE = {
	'openground' : 80.0,
	'roughground' : 20.0,
	'forest' : 20.0,
	'village' : 10.0,
	'fields_in_season' : 50.0,
	'pond' : 0.0
}
# bonus move chance when moving along a dirt road
DIRT_ROAD_BONUS_CHANCE = 90.0
# multiplier for each extra move already taken
BONUS_CHANCE_MULTIPLIER = 0.4

# maximum total modifer before a LoS is blocked by terrain
MAX_LOS_MOD = 60.0


##########################################################################################
#                                         Classes                                        #
##########################################################################################

# Campaign: stores data about a campaign currently in progress, made up of 1+ campaign days
class Campaign:
	def __init__(self):
		
		# TEMP: following will be set by CampaignSelectionMenu eventually
		
		# current year, month, day, hour, and minute
		# TODO: starting date will be set by campaign type
		self.calendar = {
			'year' : 1939,
			'month' : 9,
			'day' : 1,
			'hour' : 5,
			'minute' : 0
		}
		
		# nation of player forces; corresponds to a key in nation_defs.json
		self.player_nation = 'Germany'
		
		# TEMP: set up player unit
		self.player_unit = Unit('Panzer 38(t) A')
		self.player_unit.owning_player = 0
		self.player_unit.nation = self.player_nation
		self.player_unit.base_morale_level = 'Confident'
		self.player_unit.GenerateNewCrew()
	
	# update screen with info about the currently selected campaign
	def UpdateCampaignSelectionScreen(self, selected_campaign):
		libtcod.console_clear(con)
		DrawFrame(con, 26, 1, 37, 58)
		libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
		ConsolePrintEx(con, 45, 3, libtcod.BKGND_NONE, libtcod.CENTER,
			'Campaign Selection')
		libtcod.console_set_default_background(con, libtcod.dark_blue)
		libtcod.console_rect(con, 27, 5, 35, 3, True, libtcod.BKGND_SET)
		libtcod.console_set_default_background(con, libtcod.black)
		libtcod.console_set_default_foreground(con, libtcod.white)
		ConsolePrintEx(con, 45, 6, libtcod.BKGND_NONE, libtcod.CENTER,
			selected_campaign['name'])
		
		# player nation flag
		if selected_campaign['player_nation'] in session.flags:
			libtcod.console_blit(session.flags[selected_campaign['player_nation']],
				0, 0, 0, 0, con, 30, 10)
		
		# player and enemy forces
		ConsolePrintEx(con, 45, 26, libtcod.BKGND_NONE, libtcod.CENTER,
			'PLAYER FORCE')
		ConsolePrintEx(con, 45, 30, libtcod.BKGND_NONE, libtcod.CENTER,
			'ENEMY FORCES')
		
		libtcod.console_set_default_foreground(con, libtcod.light_grey)
		ConsolePrintEx(con, 45, 27, libtcod.BKGND_NONE, libtcod.CENTER,
			selected_campaign['player_nation'])
		text = ''
		for nation_name in selected_campaign['enemy_nations']:
			if selected_campaign['enemy_nations'].index(nation_name) != 0:
				text += ', '
			text += nation_name
		ConsolePrintEx(con, 45, 31, libtcod.BKGND_NONE, libtcod.CENTER, text)
		
		# TODO: calendar range and total combat days
		
		# TODO: wrapped description text
		
		
		libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
		ConsolePrint(con, 32, 53, EncodeKey('a').upper() + '/' + EncodeKey('d').upper())
		ConsolePrint(con, 32, 55, 'Enter')
		ConsolePrint(con, 32, 56, 'Esc')
		libtcod.console_set_default_foreground(con, libtcod.white)
		ConsolePrint(con, 38, 53, 'Change Campaign')
		ConsolePrint(con, 38, 55, 'Proceed')
		ConsolePrint(con, 38, 56, 'Return to Main Menu')
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	# menu to select campaign
	def CampaignSelectionMenu(self):
		
		# load basic information of campaigns into a list of dictionaries
		BASIC_INFO = [
			'name', 'start_date', 'action_days', 'player_nation',
			'enemy_nations', 'desc'
		]
		
		campaign_list = []
		
		for filename in os.listdir(CAMPAIGNPATH):
			if not filename.endswith('.json'): continue
			with open(CAMPAIGNPATH + filename) as data_file:
				campaign_data = json.load(data_file)
			new_campaign = {}
			for k in BASIC_INFO:
				new_campaign[k] = campaign_data[k]
			campaign_list.append(new_campaign)
			del campaign_data
			print 'DEBUG: added campaign to list: ' + new_campaign['name']
		
		# FUTURE: sort campaigns by start date
		
		# select first campaign by default
		selected_campaign = campaign_list[0]
		
		# draw menu screen for first time
		self.UpdateCampaignSelectionScreen(selected_campaign)
		
		exit_loop = False
		while not exit_loop:
			
			# emergency exit in case of endless loop
			if libtcod.console_is_window_closed(): sys.exit()
			
			libtcod.console_flush()
			
			event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
				key, mouse)
			
			##### Player Keyboard Commands #####
			if session.key_down:
				if event != libtcod.EVENT_KEY_RELEASE:
					continue
				session.key_down = False
			if event != libtcod.EVENT_KEY_PRESS:
				continue
			session.key_down = True
			
			# TEMP? exit
			if key.vk == libtcod.KEY_ESCAPE:
				return False
			
			# proceed with selected campaign
			elif key.vk == libtcod.KEY_ENTER:
				exit_loop = True
			
			key_char = DecodeKey(chr(key.c).lower())
			
			# change selected campaign
			if key_char in ['a', 'd']:
				
				i = campaign_list.index(selected_campaign)
				
				if key_char == 'd':
					if i == len(campaign_list) - 1:
						selected_campaign = campaign_list[0]
					else:
						selected_campaign = campaign_list[i+1]
				else:
					if i == 0:
						selected_campaign = campaign_list[-1]
					else:
						selected_campaign = campaign_list[i-1]
				self.UpdateCampaignSelectionScreen(selected_campaign)
		
		# TODO: set up campaign info here
		
		return True
		
	# advance the current campaign time
	# TODO: how to handle rolling over into new day?
	def AdvanceClock(self, hours, minutes):
		self.calendar['hour'] += hours
		self.calendar['minute'] += minutes
		while self.calendar['minute'] >= 60:
			self.calendar['hour'] += 1
			self.calendar['minute'] -= 60



# Map Hex: a single hex-shaped block of terrain within a scenario
# roughly scaled to 160 m. in width
class MapHex:
	def __init__(self, hx, hy):
		self.hx = hx			# hex coordinates in the map
		self.hy = hy			# 0,0 is centre of map
		self.terrain_type = 'openground'
		self.variant = 0		# FUTURE: variant of visual depiction, no effect on gameplay
		self.elevation = 1		# elevation in steps above baseline
		self.river_edges = []		# list of edges bounded by a river
		self.dirt_roads = []		# list of directions linked by a dirt road
		
		self.unit_stack = []		# stack of units present in this hex
		self.objective = None		# status as an objective; if -1, not controlled
						#   by either player, otherwise 0 or 1
		
		# Pathfinding stuff
		self.parent = None
		self.g = 0
		self.h = 0
		self.f = 0
	
	# set elevation of hex
	# FUTURE: handle cliff edges here?
	def SetElevation(self, elevation):
		self.elevation = elevation
	
	# set terrain type
	def SetTerrainType(self, terrain_type):
		self.terrain_type = terrain_type
	
	# reset pathfinding info for this map hex
	def ClearPathInfo(self):
		self.parent = None
		self.g = 0
		self.h = 0
		self.f = 0
	
	# return total LoS modifier for this terrain hex
	# FUTURE: can also calculate effect of smoke, rain, etc.
	def GetTerrainMod(self):
		return TERRAIN_LOS_MODS[self.terrain_type]
	
	# check to see if this objective hex has been captured
	def CheckCapture(self):
		if self.objective is None: return False
		if len(self.unit_stack) == 0: return False
		
		for unit in self.unit_stack:
			if unit.dummy: continue
			if unit.owning_player != self.objective:
				self.objective = unit.owning_player
				return True



# Campaign Map Hex: a map hex for the campaign day map, each representing a map scenario hexes
# scaled to approx. 2.7 km. wide
class CampaignMapHex:
	def __init__(self, hx, hy):
		self.hx = hx
		self.hy = hy
		self.controlled_by = 1		# which player side currently controls this zone
		
		# real enemy strength and organization, each 1-9
		self.enemy_strength = -9 + libtcod.random_get_int(0, 1, 6) + libtcod.random_get_int(0, 1, 6) + libtcod.random_get_int(0, 1, 6)
		
		if self.enemy_strength < 1:
			self.enemy_strength = 1
		
		self.enemy_organization = 1 + libtcod.random_get_int(0, 0, 4) + libtcod.random_get_int(0, 0, 4)
		
		# calculate encounter chance
		self.encounter_chance = CD_BATTLE_BASE_CHANCE
		self.encounter_chance += (self.enemy_strength * CD_BATTLE_STR_MOD)
		self.encounter_chance += ((self.enemy_organization - 5) * CD_BATTLE_ORGANIZATION_MOD)
		self.encounter_chance = round(self.encounter_chance, 2)
		
		if self.encounter_chance > 97.0:
			self.encounter_chance = 97.0
		
		# create an empty placeholder for a hex map; will be generated if a scenario takes place here
		self.map_hexes = {}
		self.map_radius = 8
		
	# create a hex map for a scenario within this map hex
	def GenerateHexMap(self):
		# generate the hex map in the shape of a pointy-top hex; radius does not include centre hex
		# create centre hex
		self.map_hexes[(0,0)] = MapHex(0,0)
		
		# add rings around centre
		for r in range(1, self.map_radius+1):
			hex_list = GetHexRing(0, 0, r)
			for (hx, hy) in hex_list:
				self.map_hexes[(hx,hy)] = MapHex(hx,hy)
		
		# generate terrain
		self.GenerateTerrain()
	
	# fill the hex map with terrain
	def GenerateTerrain(self):
		
		# get a path from hx1,hy1 to hx2,hy2 suitable for a dirt road and create it
		def GenerateRoad(hx1, hy1, hx2, hy2):
			path = GetHexPath(self.map_hexes, hx1, hy1, hx2, hy2, road_path=True)
			
			# no path was possible
			if len(path) == 0:
				return False
			
			# create the road
			for n in range(len(path)):
				(hx1, hy1) = path[n]
				if n+1 < len(path):
					hx2, hy2 = path[n+1]
					direction = GetDirectionToAdjacent(hx1, hy1, hx2, hy2)
					self.map_hexes[(hx1, hy1)].dirt_roads.append(direction)
					
					direction = GetDirectionToAdjacent(hx2, hy2, hx1, hy1)
					self.map_hexes[(hx2, hy2)].dirt_roads.append(direction)
			
			return True
		
		# create a local list of all hx, hy locations in map
		map_hex_list = []
		for k, map_hex in self.map_hexes.iteritems():
			map_hex_list.append(k)
		
		# record total number of hexes in the map
		hex_num = len(map_hex_list)
		
		# terrain settings
		# FUTURE: will be supplied by battleground settings
		rough_ground_num = int(hex_num / 50)	# rough ground hexes
		
		hill_num = int(hex_num / 70)		# number of hills to generate
		hill_min_size = 4			# minimum width/height of hill area
		hill_max_size = 7			# maximum "
		
		forest_num = int(hex_num / 50)		# number of forest areas to generate
		forest_size = 6				# total maximum height + width of areas
		
		village_max = int(hex_num / 100)	# maximum number of villages to generate
		village_min = int(hex_num / 50)		# minimum "
		
		fields_num = int(hex_num / 50)		# number of tall field areas to generate
		field_min_size = 1			# minimum width/height of field area
		field_max_size = 3			# maximum "
		
		ponds_min = int(hex_num / 400)		# minimum number of ponds to generate
		ponds_max = int(hex_num / 80)		# maximum "
		
		
		##### Rough Ground #####
		for terrain_pass in range(rough_ground_num):
			(hx, hy) = choice(map_hex_list)
			self.map_hexes[(hx, hy)].SetTerrainType('roughground')
		
		##### Elevation / Hills #####
		for terrain_pass in range(hill_num):
			hex_list = []
			
			# determine upper left corner, width, and height of hill area
			(hx_start, hy_start) = choice(map_hex_list)
			hill_width = libtcod.random_get_int(0, hill_min_size, hill_max_size)
			hill_height = libtcod.random_get_int(0, hill_min_size, hill_max_size)
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
				if (hx, hy) in self.map_hexes:
					self.map_hexes[(hx, hy)].SetElevation(2)
		
		##### Forests #####
		if forest_size < 2: forest_size = 2
		
		for terrain_pass in range(forest_num):
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
				if (hx, hy) in self.map_hexes:
					# small chance of gaps in area
					if libtcod.random_get_int(0, 1, 15) == 1:
						continue
					self.map_hexes[(hx, hy)].SetTerrainType('forest')
					
					# set variant too
					self.map_hexes[(hx, hy)].variant = libtcod.random_get_int(0, 0, 1)

		##### Villages #####
		num_villages = libtcod.random_get_int(0, village_min, village_max)
		for terrain_pass in range(num_villages):
			# determine size of village in hexes: 1,1,1,2,3 hexes total
			village_size = libtcod.random_get_int(0, 1, 5) - 2
			if village_size < 1: village_size = 1
			
			# find centre of village
			shuffle(map_hex_list)
			for (hx, hy) in map_hex_list:
				
				if self.map_hexes[(hx, hy)].terrain_type == 'forest':
					continue
				
				# create centre of village
				self.map_hexes[(hx, hy)].SetTerrainType('village')
				
				# handle large villages; if extra hexes fall off map they won't
				#  be added
				# TODO: possible to lose one or more additional hexes if they
				#   are already village hexes
				if village_size > 1:
					for extra_hex in range(village_size-1):
						(hx2, hy2) = GetAdjacentHex(hx, hy, libtcod.random_get_int(0, 0, 5))
						if (hx2, hy2) in map_hex_list:
							self.map_hexes[(hx2, hy2)].SetTerrainType('village')
				break
		
		##### In-Season Fields #####
		for terrain_pass in range(fields_num):
			hex_list = []
			(hx_start, hy_start) = choice(map_hex_list)
			width = libtcod.random_get_int(0, field_min_size, field_max_size)
			height = libtcod.random_get_int(0, field_min_size, field_max_size)
			hx_start -= int(width / 2)
			hy_start -= int(height / 2)
			
			# get a rectangle of hex locations
			hex_rect = GetHexRect(hx_start, hy_start, width, height)
			
			# apply forest locations if they are on map
			for (hx, hy) in hex_rect:
				if (hx, hy) not in map_hex_list:
					continue
					
				# don't overwrite villages
				if self.map_hexes[(hx, hy)].terrain_type == 'village':
					continue
				
				# small chance of overwriting forest
				if self.map_hexes[(hx, hy)].terrain_type == 'forest':
					if libtcod.random_get_int(0, 1, 10) <= 9:
						continue
				
				self.map_hexes[(hx, hy)].SetTerrainType('fields_in_season')

		##### Ponds #####
		num_ponds = libtcod.random_get_int(0, ponds_min, ponds_max)
		shuffle(map_hex_list)
		for terrain_pass in range(num_ponds):
			for (hx, hy) in map_hex_list:
				if self.map_hexes[(hx, hy)].terrain_type != 'openground':
					continue
				if self.map_hexes[(hx, hy)].elevation != 1:
					continue
				self.map_hexes[(hx, hy)].SetTerrainType('pond')
				break
		
		##### Rivers #####
		
		# not yet implemented - need to do pathfinding along hex corners
		#self.map_hexes[(0, 8)].river_edges.append(0)
		
		##### Dirt Road #####
		hx1, hy1 = 0, self.map_radius
		hx2, hy2 = 0, 0 - self.map_radius
		GenerateRoad(hx1, hy1, hx2, hy2)



# Campaign Day: represents one calendar day in a campaign with a 5x7 map of terrain hexes, each of
# which may spawn a Scenario
class CampaignDay:
	def __init__(self):
		
		# campaign day map
		self.map_hexes = {}
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			self.map_hexes[(hx,hy)] = CampaignMapHex(hx, hy)
		
		self.player_unit_location = (-2, 8)		# set player unit group location
		self.map_hexes[(-2, 8)].controlled_by = 0	# set player location to player control
		
		self.active_menu = 3				# number of currently active command menu
		self.travel_direction = None			# selected direction of travel
		
		self.scenario = None				# currently active scenario in progress
		
	
	# initiate a battle encounter scenario and store it in the CD object
	def InitScenario(self, hx, hy):
		self.scenario = Scenario(self.map_hexes[(hx, hy)])
		
	
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
		libtcod.console_clear(cd_map_con)
		
		# draw map hexes to console
		dayhex_openground = LoadXP('dayhex_openground.xp')
		libtcod.console_set_key_color(dayhex_openground, KEY_COLOR)
		
		for k, map_hex in self.map_hexes.iteritems():
			(x,y) = self.PlotCDHex(map_hex.hx, map_hex.hy)
			libtcod.console_blit(dayhex_openground, 0, 0, 0, 0, cd_map_con, x-3, y-4)
	
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
		libtcod.console_set_default_foreground(cd_unit_con, libtcod.red)
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			if self.map_hexes[(hx,hy)].controlled_by == 1:
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
			
			# TEMP - only travel active for now
			if num != 3:
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
				ConsolePrint(cd_command_con, 2, 10, 'Strength: ' + str(map_hex.enemy_strength))
				ConsolePrint(cd_command_con, 2, 11, 'Organization: ' + str(map_hex.enemy_organization))
				libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
				ConsolePrint(cd_command_con, 0, 13, 'Encounter Chance: ' + str(map_hex.encounter_chance) + '%%')
				ConsolePrint(cd_command_con, 0, 14, 'Travel Time: 15 mins.')
		
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			ConsolePrint(cd_command_con, 5, 22, 'Enter')
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			ConsolePrint(cd_command_con, 12, 22, 'Proceed')
	
	
	# generate/update the time and weather console
	# FUTURE: will also be used in scenario display
	def UpdateTimeWeatherDisplay(self):
		libtcod.console_clear(time_weather_con)
		text = str(campaign.calendar['hour']).zfill(2) + ':' + str(campaign.calendar['minute']).zfill(2)
		ConsolePrint(time_weather_con, 14, 1, text)
		ConsolePrintEx(time_weather_con, 16, 2, libtcod.BKGND_NONE, libtcod.CENTER, 'Clear')
		
		
	# draw all campaign day consoles to screen
	def UpdateCDDisplay(self):
		libtcod.console_clear(con)
		libtcod.console_blit(daymap_bkg, 0, 0, 0, 0, con, 0, 0)			# background frame
		libtcod.console_blit(cd_map_con, 0, 0, 0, 0, con, 28, 4)		# terrain map
		libtcod.console_blit(time_weather_con, 0, 0, 0, 0, con, 29, 0)		# time and weather
		libtcod.console_blit(cd_control_con, 0, 0, 0, 0, con, 28, 4, 1.0, 0.0)	# zone control layer
		libtcod.console_blit(cd_unit_con, 0, 0, 0, 0, con, 28, 4, 1.0, 0.0)	# unit group layer
		libtcod.console_blit(cd_player_unit_con, 0, 0, 0, 0, con, 1, 1)		# player unit info
		libtcod.console_blit(cd_command_con, 0, 0, 0, 0, con, 1, 35)		# command menu
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	
	# main campaign day input loop
	def CampaignDayLoop(self):
		
		global daymap_bkg, cd_map_con, cd_unit_con, cd_control_con, cd_command_con
		global cd_player_unit_con
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
		
		
		# generate consoles for the first time
		self.UpdateCDMapCon()
		self.UpdateCDControlCon()
		self.UpdateCDUnitCon()
		self.UpdateTimeWeatherDisplay()
		self.UpdateCDPlayerUnitCon()
		self.UpdateCDCommandCon()
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
				
				self.UpdateCDDisplay()
				libtcod.console_flush()
				
				# we're exiting to main menu, game is already saved
				if session.exiting_to_main_menu:
					session.exiting_to_main_menu = False
					exit_loop = True
					continue
			
			libtcod.console_flush()
			
			# get keyboard and/or mouse event
			event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
				key, mouse)
			
			# check to see if mouse cursor has moved
			if mouse.cx != mouse_x or mouse.cy != mouse_y:
				mouse_x = mouse.cx
				mouse_y = mouse.cy
			
			##### Player Keyboard Commands #####
			
			if session.key_down:
				if event != libtcod.EVENT_KEY_RELEASE:
					continue
				session.key_down = False
			if event != libtcod.EVENT_KEY_PRESS:
				continue
			session.key_down = True
			
			# Determine action based on key pressed
			
			# TEMP exit
			if key.vk == libtcod.KEY_ESCAPE:
				exit_loop = True
			
			# key commands
			key_char = chr(key.c).lower()
			
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
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
					continue
				
				# proceed with travel
				if key.vk == libtcod.KEY_ENTER and self.travel_direction is not None:
					
					# ensure that travel is possible
					(hx, hy) = self.player_unit_location
					(hx, hy) = self.GetAdjacentCDHex(hx, hy, self.travel_direction)
					if (hx, hy) not in self.map_hexes:
						continue
					
					# set new player location
					self.player_unit_location = (hx, hy)
					
					# clear travel direction
					self.travel_direction = None
					
					# advance campaign clock
					campaign.AdvanceClock(0, 15)
					
					# roll for battle encounter if enemy-controlled
					if self.map_hexes[(hx, hy)].controlled_by == 1:
						roll = GetPercentileRoll()
						# TEMP
						roll = 0.0
						if roll <= self.map_hexes[(hx,hy)].encounter_chance:
							ShowNotification('You encounter enemy resistance and a battle ensues!')
							self.InitScenario(hx,hy)
						else:
							ShowNotification('You encounter no enemy resistance and swiftly take control of the area.')
							self.map_hexes[(hx, hy)].controlled_by = 0
							self.UpdateCDControlCon()

					# update rest of consoles
					self.UpdateCDUnitCon()
					self.UpdateTimeWeatherDisplay()
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()


# Session: stores data that is generated for each game session and not stored in the saved game
class Session:
	def __init__(self):
		
		# flag: the last time the keyboard was polled, a key was pressed
		self.key_down = False
		
		# flag to say that we are exiting to main menu
		self.exiting_to_main_menu = False
		
		# load and generate hex console images for scenario map
		self.hex_consoles = {}
		for terrain_type in HEX_TERRAIN_TYPES:
			
			# generate consoles for 4 different terrain heights
			consoles = []
			for elevation in range(4):
				consoles.append(libtcod.console_new(7, 5))
				libtcod.console_blit(LoadXP('hex_' + terrain_type + '.xp'),
					0, 0, 7, 5, consoles[elevation], 0, 0)
				libtcod.console_set_key_color(consoles[elevation], KEY_COLOR)
			
			# apply colour modifier to elevations 0, 2, 3
			for elevation in [0, 2, 3]:
				for y in range(5):
					for x in range(7):
						bg = libtcod.console_get_char_background(consoles[elevation],x,y)
						if bg == KEY_COLOR: continue
						bg = bg * (1.0 + float(elevation-1) * ELEVATION_SHADE)
						libtcod.console_set_char_background(consoles[elevation],x,y,bg)
			
			self.hex_consoles[terrain_type] = consoles
		
		# TODO: load unit portraits
		
		# load national flag images
		self.flags = {}
		with open(DATAPATH + 'nation_defs.json') as data_file:
			nations = json.load(data_file)
		for name, data in nations.iteritems():
			self.flags[name] = LoadXP(data['flag_image'])
		del nations

	# try to initialize SDL2 mixer
	def InitMixer(self):
		mixer.Mix_Init(mixer.MIX_INIT_OGG)
		if mixer.Mix_OpenAudio(48000, mixer.MIX_DEFAULT_FORMAT,	2, 1024) == -1:
			print 'ERROR in Mix_OpenAudio: ' + mixer.Mix_GetError()
			return False
		mixer.Mix_AllocateChannels(16)
		return True
	
	def LoadSounds(self):
		self.sample = {}
		
		SOUND_LIST = [
			'menu_select',
			'37mm_firing_00', '37mm_firing_01', '37mm_firing_02', '37mm_firing_03',
			'37mm_he_explosion_00', '37mm_he_explosion_01',
			'at_rifle_firing',
			'light_tank_moving_00', 'light_tank_moving_01', 'light_tank_moving_02',
			'zb_53_mg_00'
		]
		
		# because the function returns NULL if the file failed to load, Python does not seem
		# to have any way of detecting this and there's no error checking
		for sound_name in SOUND_LIST:
			self.sample[sound_name] = mixer.Mix_LoadWAV(SOUNDPATH + sound_name + '.ogg')
		

# AI: controller for enemy and player-allied units
class AI:
	def __init__(self, owner):
		self.owner = owner
		self.disposition = None
	
	# print an AI report re: crew actions for this unit to the console, used for debugging
	def DoCrewActionReport(self):
		text = '\nAI SPY: ' + self.owner.unit_id + ' set to disposition: '
		if self.disposition is None:
			text += 'Wait'
		else:
			text += self.disposition
		if self.owner.dummy:
			text += ' (dummy)'
		print text
	
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
			roll -= 20.0
		
		# guns have fewer options for actions
		if self.owner.GetStat('category') == 'Gun':
			if roll >= 70.0:
				self.disposition = None
			else:
				self.disposition = 'Combat'
		
		elif self.owner.GetStat('category') == 'Infantry':
			if roll <= 50.0:
				self.disposition = 'Combat'
			elif roll <= 60.0:
				if self.owner.pinned:
					self.disposition = 'Combat'
				else:
					self.disposition = 'Movement'
			else:
				self.disposition = None
		
		else:
		
			if roll >= 80.0:
				self.disposition = None
			elif roll <= 50.0:
				self.disposition = 'Combat'
			else:
				if self.owner.pinned:
					self.disposition = 'Combat'
				else:
					self.disposition = 'Movement'
		
		# dummy units never attack
		if self.owner.dummy and self.disposition == 'Combat':
			self.disposition = None
		
		# debug override
		if AI_NO_ACTION:
			self.disposition = None
		if AI_SPY:
			self.DoCrewActionReport()
		
		
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
					print text
				
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
				result = self.owner.MoveForward()
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
					print 'AI SPY: ' + self.owner.unit_id + ': no possible targets'
				return
			
			# select our target unit
			unit = None
			
			# if one of these is our acquired target, choose that one
			if self.owner.acquired_target is not None:
				(target, level) = self.owner.acquired_target
				if target in target_list:
					unit = target
			
			if unit is None:
				# select a random target from list
				unit = choice(target_list)
			
			# TEMP - can select first weapon only
			weapon = self.owner.weapon_list[0]
			
			# TEMP - choose AP ammo only
			if weapon.GetStat('type') == 'Gun':
				if 'AP' in weapon.stats['ammo_type_list']:
					weapon.current_ammo = 'AP'
			
			# if weapon is hull mounted, pivot to face target
			if weapon.GetStat('mount') == 'Hull':
				direction = GetDirectionToward(self.owner.hx, self.owner.hy, unit.hx,
					unit.hy)
				if self.owner.facing != direction:
					self.owner.facing = direction
					self.owner.moved = True
					
					if animate:
						UpdateUnitCon()
						UpdateScenarioDisplay()
						libtcod.console_flush()
						Wait(10)
			
			# otherwise, rotate turret if any to face target
			elif self.owner.turret_facing is not None:
				direction = GetDirectionToward(self.owner.hx, self.owner.hy, unit.hx,
					unit.hy)
				if self.owner.turret_facing != direction:
					self.owner.turret_facing = direction
					
					if animate:
						UpdateUnitCon()
						UpdateScenarioDisplay()
						libtcod.console_flush()
						Wait(10)
			
			# try the attack
			result = self.owner.Attack(weapon, unit)
			if not result:
				if AI_SPY:
					print 'AI SPY: ' + self.owner.unit_id + ': could not attack'
					print 'AI SPY: ' + scenario.CheckAttack(self.owner, weapon, unit)
		
		# end activation
		self.owner.DoPostActivation()
	


				
		


# Scenario: represents a single battle encounter
class Scenario:
	def __init__(self, cd_hex):
		
		# pointer to map hex on campaign day map
		self.cd_hex = cd_hex
		
		# game turn, active player, and phase tracker
		self.game_turn = {
			'active_player' : 0,		# currently active player number
			'goes_first' : 0,		# which player side acts first in each turn
		}
		
		self.active_menu = 2			# currently active player menu; 0:none
		
		self.units = []				# list of units in the scenario
		self.player_unit = None			# pointer to the player unit
		self.active_unit = None			# currently activated unit
		self.activation_list = [		# activation order for player units, enemy units
			[], []
		]
		
		# player 'luck' points
		# FUTURE move into campaign object
		self.player_luck = 2 + libtcod.random_get_int(0, 1, 3)
		
		self.finished = False			# have win/loss conditions been met
		self.winner = -1			# player number of scenario winner, -1 if None
		self.win_desc = ''			# description of win/loss conditions met
		
		self.selected_position = 0		# index of selected crewman in player unit
		self.selected_weapon = None		# currently selected weapon on player unit
		
		self.player_target_list = []		# list of possible enemy targets for player unit
		self.player_target = None		# current target of player unit
		self.player_attack_desc = ''		# text description of attack on player target
		self.player_los_active = False		# display of player's LoS to target is active
		
		###### Hex Map and Map Viewport #####
		self.map_objectives = []		# list of map hex objectives
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
	
	# generate activation order for player units and enemy units
	def GenerateActivationOrder(self):
		
		for unit in self.units:
			if unit == self.player_unit: continue
			self.activation_list[unit.owning_player].append(unit)
		shuffle(self.activation_list[0])
		shuffle(self.activation_list[1])
		
		# add the player unit to the start of the list
		self.activation_list[0].insert(0, self.player_unit)
	
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
			
	# set a given map hex as an objective, and set initial control state
	def SetObjectiveHex(self, hx, hy, owning_player):
		map_hex = self.cd_hex.map_hexes[(hx, hy)]
		map_hex.objective = owning_player
		self.map_objectives.append(map_hex)
	
	# generate enemy units for this scenario
	# assumes that enemy are on defense, already in place in area before player arrives
	# FUTURE: will take list of unit groups for this area from Campaign object
	def SpawnEnemyUnits(self):
		
		# spawn one unit at a time
		# once a tank, armoured car, or gun is spawned, set that as the type for
		# this scenario; any further spawns of this class will be of this type
		
		
		
		# FUTURE - get from campaign object
		enemy_unit_list = [
			('TK-3', 2, 3, 95.0),
			('TKS', 2, 3, 85.0),
			('TKS (20mm)', 1, 2, 40.0),
			('Vickers 6-Ton Mark E', 1, 1, 30.0),
			('7TP', 1, 1, 50.0),
			('wz. 34 (MG)', 1, 2, 75.0),
			('wz. 34 (37mm)', 1, 2, 50.0),
			('37mm wz. 36', 2, 3, 60.0),
			('75mm wz. 02/26', 1, 1, 22.0),
			('75mm wz. 97/25', 1, 1, 13.0),
			('Riflemen', 1, 3, 100.0)
		]
		
		# load unit stats from JSON file
		with open(DATAPATH + 'unit_type_defs.json') as data_file:
			unit_types = json.load(data_file)
		
		# determine how many unit groups will be spawned
		num_unit_groups = libtcod.random_get_int(0, 3, 4)
		
		# generate list of unit groups
		unit_group_list = []
		while len(unit_group_list) < num_unit_groups:
			(unit_id, min_num, max_num, rarity) = choice(enemy_unit_list)
			
			# do rarity test
			roll = GetPercentileRoll()
			if roll > rarity:
				continue
			
			unit_group_list.append((unit_id, min_num, max_num, rarity))
		
		CATEGORY_LIST = ['Gun', 'Infantry', 'Vehicle']
		for category in CATEGORY_LIST:
			for (unit_id, min_num, max_num, rarity) in unit_group_list:
				if unit_id not in unit_types:
					print 'ERROR: Could not find unit id: ' + unit_id
					continue
				
				unit_stats = unit_types[unit_id]
				if unit_stats['category'] != category:
					continue
				
				# determine where to place center point of group
				if category == 'Gun':
					ideal_distance = 1
				elif category == 'Infantry':
					ideal_distance = 3
				else:
					ideal_distance = 12
				
				hx = None
				hy = None
				for tries in range(300):
					close_enough = False
					(hx, hy) = choice(self.cd_hex.map_hexes.keys())
					
					# too close to player
					if GetHexDistance(hx, hy, self.player_unit.hx, self.player_unit.hy) < 5:
						continue
					
					for map_hex in self.map_objectives:
						if GetHexDistance(hx, hy, map_hex.hx, map_hex.hy) <= ideal_distance:
							close_enough = True
							break
					if close_enough:
						break
				
				if hx is None and hy is None:
					print 'ERROR: Could not find a location close enough to an objective to spawn!'
					continue
				
				# spawn each unit within the group close to hx, hy
				unit_num = libtcod.random_get_int(0, min_num, max_num)
				for i in range(unit_num):
					
					# create the unit
					new_unit = Unit(unit_id)
					new_unit.owning_player = 1
					new_unit.ai = AI(new_unit)
					new_unit.nation = 'Poland'
					new_unit.facing = 3
					if 'turret' in new_unit.stats:
						new_unit.turret_facing = 3
					new_unit.base_morale_level = 'Fearless'
					new_unit.GenerateNewCrew()
					# deploy if gun
					if new_unit.GetStat('category') == 'Gun':
						new_unit.deployed = True
					self.units.append(new_unit)
					
					# build a list of hexes within the ideal distance of hx,hy
					hex_list = []
					hex_list.append((hx, hy))
					for r in range(1, ideal_distance+1):
						hex_list.extend(GetHexRing(hx, hy, r))
					
					# find a random location and place the unit there
					for tries in range(300):
						(spawn_hx, spawn_hy) = choice(hex_list)
						
						# too close to player
						if GetHexDistance(spawn_hx, spawn_hy, self.player_unit.hx, self.player_unit.hy) < 5:
							continue
						
						# off map
						if (spawn_hx, spawn_hy) not in self.cd_hex.map_hexes:
							continue
						
						# not passable
						if self.cd_hex.map_hexes[(spawn_hx, spawn_hy)].terrain_type == 'pond':
							continue
						
						new_unit.SpawnAt(spawn_hx, spawn_hy)
						break
		
		unit_list = []
		for unit in self.units:
			if unit.owning_player == 1:
				unit_list.append(unit)
		if len(unit_list) >= 4:
			unit_list = sample(unit_list, int(ceil(len(unit_list) * ENEMY_DUMMY_RATIO)))	
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
			self.win_desc = 'Your tank was destroyed.'
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
		
		all_objectives_captured = True
		for map_hex in self.map_objectives:
			if map_hex.objective == 1:
				all_objectives_captured = False
				break
		if all_objectives_captured:
			self.winner = 0
			self.finished = True
			self.win_desc = 'All objectives in the area were captured.'
			return
		
		# turn half over
		if self.game_turn['active_player'] == self.game_turn['goes_first']:
			
			if self.game_turn['goes_first'] == 0:
				self.game_turn['active_player'] = 1
			else:
				self.game_turn['active_player'] = 0
		else:
			self.game_turn['active_player'] = self.game_turn['goes_first']
		
			# advance campaign clock one minute
			campaign.AdvanceClock(0, 1)

		# check for objective capture
		for map_hex in self.map_objectives:
			if map_hex.CheckCapture():
				text = 'An objective was captured by '
				if map_hex.objective == 0:
					text += 'your forces'
				else:
					text += 'enemy forces'
				self.ShowMessage(text, hx=map_hex.hx, hy=map_hex.hy)
				
	
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
			
			if (unit.hx, unit.hy) not in scenario.player_unit.fov: continue
			self.player_target_list.append(unit)
	
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
	
	# calculate the odds of success of a ranged attack, returns an attack profile
	def CalcAttack(self, attacker, weapon, target):
		
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
		elif weapon_type in ['Co-ax MG', 'Hull MG']:
			profile['type'] = 'Area Fire'
			profile['effective_fp'] = 0		# placeholder for effective fp
		else:
			print 'ERROR: Weapon type not recognized: ' + weapon.stats['name']
			return None
		
		modifier_list = []
		
		# calculate distance to target
		distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
		
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
			# TODO: elif weapon turret rotated
			
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
				modifier_list.append(('Higher Elevation', -20.0))
			
			# unknown target
			if not target.known:
				modifier_list.append(('Unknown Target', -20.0))
			
			# known target
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
				
				# target vehicle moved
				if target.moved and target.GetStat('category') == 'Vehicle':
					modifier_list.append(('Target Moved', -30.0))
				
				# target size
				size_class = target.GetStat('size_class')
				if size_class is not None:
					if size_class == 'Small':
						modifier_list.append(('Small Target', -7.0))
					elif size_class == 'Very Small':
						modifier_list.append(('Very Small Target', -18.0))
		
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
				modifier_list.append(('Higher Elevation', -20.0))
			
			if not target.known:
				modifier_list.append(('Unknown Target', -20.0))
			else:
			
				# target is infantry and moved
				if target.moved and target.GetStat('category') == 'Infantry':
					mod = round(base_chance / 2.0, 2)
					modifier_list.append(('Target Moved', mod))
				
				# target size class
				size_class = target.GetStat('size_class')
				if size_class is not None:
					if size_class == 'Small':
						modifier_list.append(('Small Target', -7.0))
					elif size_class == 'Very Small':
						modifier_list.append(('V. Small Target', -18.0))
		
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
		
		# determine location hit on target
		if libtcod.random_get_int(0, 1, 6) <= 4:
			location = 'Hull'
			turret_facing = False
		else:
			location = 'Turret'
			turret_facing = True
		
		facing = GetFacing(attacker, target, turret_facing=turret_facing)
		hit_location = (location + '_' + facing).lower()
		
		# generate a text description of location hit
		if target.turret_facing is None:
			location = 'Upper Hull'
		profile['location_desc'] = location + ' ' + facing
		
		# calculate base chance of penetration
		if weapon.GetStat('name') == 'AT Rifle':
			base_chance = AP_BASE_CHANCE['AT Rifle']
		elif weapon.GetStat('type') in ['Co-ax MG', 'Hull MG']:
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
					print 'ERROR: No AP base chance found for: ' + gun_rating
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
		armour = target.GetStat('armour')
		if armour is not None:
			target_armour = int(armour[hit_location])
			if target_armour > 0:
				modifier = -7.0
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
	
	# calculate the resolution of FP attacks on a unit
	def CalcFP(self, unit):
		
		profile = {}
		profile['target'] = unit
		profile['type'] = 'FP Resolution'
		profile['effective_fp'] = unit.fp_to_resolve
		
		# calculate base chance of no effect
		base_chance = RESOLVE_FP_BASE_CHANCE
		for i in range(2, unit.fp_to_resolve + 1):
			base_chance -= RESOLVE_FP_CHANCE_STEP * (RESOLVE_FP_CHANCE_MOD ** (i-1)) 
		profile['base_chance'] = round(base_chance, 2)
		
		# TODO: calculate modifiers: eg. morale level
		modifier_list = []
		
		profile['modifier_list'] = modifier_list[:]
		
		# calculate total modifier
		total_modifier = 0.0
		for (desc, mod) in modifier_list:
			total_modifier += mod
		
		# calculate the raw final chance of no effect
		# we'll use this to calculate other result bands
		result_chance = profile['base_chance'] + total_modifier
		
		# record the effective final chance of no effect
		profile['final_chance'] = RestrictChance(result_chance)
		
		# calculate additional result bands
		for result in FP_EFFECT_RESULT_LIST:
			
			if result == 'Destroyed':
				result_chance = 100.0
				profile[result] = 100.0
			else:
				result_chance = round(result_chance + ((100.0 - base_chance) / 4.0), 2)
				profile[result] = RestrictChance(result_chance)
		
		return profile
		
	# display an attack or AP profile to the screen and prompt to proceed
	# does not alter the profile
	def DisplayAttack(self, profile):
		libtcod.console_clear(attack_con)
		
		# display the background outline
		libtcod.console_blit(LoadXP('attack_bkg.xp'), 0, 0, 0, 0, attack_con, 0, 0)
		
		# window title
		libtcod.console_set_default_background(attack_con, libtcod.darker_blue)
		libtcod.console_rect(attack_con, 1, 1, 24, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(attack_con, libtcod.black)
		
		# set flags on whether attacker/target is known to player
		# not used in FP resolution
		attacker_known = True
		target_known = True
		if profile['type'] != 'FP Resolution':
			if profile['attacker'].owning_player == 1 and not profile['attacker'].known:
				attacker_known = False
			if profile['target'].owning_player == 1 and not profile['target'].known:
				target_known = False
		
		if profile['type'] == 'ap':
			text = 'Armour Penetration'
		elif profile['type'] == 'FP Resolution':
			text = 'FP Resolution'
		else:
			text = 'Ranged Attack'
		ConsolePrintEx(attack_con, 13, 1, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		
		# attacker portrait if any
		if profile['type'] in ['Point Fire', 'Area Fire']:
			
			libtcod.console_set_default_background(attack_con, PORTRAIT_BG_COL)
			libtcod.console_rect(attack_con, 1, 2, 24, 8, False, libtcod.BKGND_SET)
		
			# TEMP: in future will store portraits for every active unit type in session object
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
		elif profile['type'] == 'FP Resolution':
			text1 = profile['target'].GetName()
			text2 = 'hit by ' + str(profile['effective_fp']) + ' FP'
			text3 = ''
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
		
		# TEMP: in future will store portraits for every active unit type in session object
		if target_known:
			portrait = profile['target'].GetStat('portrait')
			if portrait is not None:
				libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, attack_con, 1, 13)
		
		# base chance
		text = 'Base Chance '
		if profile['type'] == 'ap':
			text += 'to Penetrate'
		elif profile['type'] in ['FP Resolution', 'Area Fire']:
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
				ConsolePrint(attack_con, 2, y, desc)
				
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
		if profile['type'] == 'FP Resolution':
			
			ConsolePrint(attack_con, 1, 45, 'No Effect: ')
			ConsolePrintEx(attack_con, 24, 45, libtcod.BKGND_NONE,
				libtcod.RIGHT, chr(243) + ' ' + str(profile['final_chance'])) 
			y = 46
			for result in FP_EFFECT_RESULT_LIST:
				ConsolePrint(attack_con, 1, y, result)
				ConsolePrintEx(attack_con, 24, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, chr(243) + ' ' + str(profile[result]))
				y += 1

		elif profile['type'] == 'Area Fire':
			# area fire has partial, full, and critical outcomes possible
			
			# no effect
			libtcod.console_set_default_background(attack_con, libtcod.red)
			libtcod.console_rect(attack_con, 1, 46, 24, 3, False, libtcod.BKGND_SET)
			
			# partial effect
			libtcod.console_set_default_background(attack_con, libtcod.darker_green)
			x = int(ceil(24.0 * profile['final_chance'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			# full effect
			libtcod.console_set_default_background(attack_con, libtcod.green)
			x = int(ceil(24.0 * profile['full_effect'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			# critical effect
			libtcod.console_set_default_background(attack_con, libtcod.blue)
			x = int(ceil(24.0 * profile['critical_effect'] / 100.0))
			libtcod.console_rect(attack_con, 1, 46, x, 3, False, libtcod.BKGND_SET)
			
			text = str(profile['final_chance']) + '%%'
			ConsolePrintEx(attack_con, 13, 47, libtcod.BKGND_NONE,
				libtcod.CENTER, text)
			
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
		ConsolePrint(attack_con, 6, 57, EncodeKey('c').upper())
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		ConsolePrint(attack_con, 12, 57, 'Continue')
		
		# blit the finished console to the screen
		libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
	
	# do a roll, animate the attack console, and display the results
	# returns an altered attack profile
	def DoAttackRoll(self, profile):
		
		# check to see if this weapon maintains Rate of Fire
		def CheckRoF(profile):
			
			# guns must have a Loader active
			if profile['weapon'].GetStat('type') == 'Gun':
				if not profile['attacker'].CheckCrewAction(['Loader'], 'Reload'):
					return False
				
				# guns must also have at least one shell available
				if profile['weapon'].current_ammo is not None:
					if profile['weapon'].ammo_stores[profile['weapon'].current_ammo] == 0:
						return False			
			
			base_chance = float(profile['weapon'].GetStat('rof'))
			roll = GetPercentileRoll()
			
			if roll <= base_chance:
				return True
			return False
			
		# FP resolution uses a different animation
		if profile['type'] == 'FP Resolution':
			for i in range(4):
				roll = GetPercentileRoll()
				ConsolePrintEx(attack_con, 13, 52, libtcod.BKGND_NONE, libtcod.CENTER,
					str(roll))
				libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
				libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
				libtcod.console_flush()
				# don't wait on final roll, this is the real one
				if i != 3:
					Wait(20)
					ConsolePrintEx(attack_con, 13, 52,
						libtcod.BKGND_NONE, libtcod.CENTER, '      ')
		
		else:
			
			# animate roll indicators randomly
			for i in range(3):
				x = libtcod.random_get_int(0, 1, 24)
				libtcod.console_put_char(attack_con, x, 45, 233)
				libtcod.console_put_char(attack_con, x, 49, 232)
				
				libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
				libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
				libtcod.console_flush()
				
				Wait(20)
				
				libtcod.console_put_char(attack_con, x, 45, 0)
				libtcod.console_put_char(attack_con, x, 49, 0)
		
			roll = GetPercentileRoll()
		
		# at this point, if the player tank would be penetrated, they have a chance
		# to survive using luck
		if profile['target'] == self.player_unit and profile['type'] == 'ap':
			if roll <= profile['final_chance']:
				if self.player_luck > 0:
					self.player_luck -= 1
					# generate a random result that would save the player
					minimum = int(profile['final_chance'] * 10.0)
					roll = float(libtcod.random_get_int(0, minimum+1, 1000)) / 10.0
		
		# to-hit or area fire attack, or AP roll
		if profile['type'] != 'FP Resolution':
		
			# display final roll indicators
			x = int(ceil(24.0 * roll / 100.0))
			
			# make sure only critical hits and misses appear in their bands
			if roll > CRITICAL_HIT and x == 1: x = 2
			if roll < CRITICAL_MISS and x == 24: x = 23
			
			libtcod.console_put_char(attack_con, x, 45, 233)
			libtcod.console_put_char(attack_con, x, 49, 232)
		
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
		
		# FP resolution
		elif profile['type'] == 'FP Resolution':
			
			if roll <= profile['final_chance']:
				result_text = 'No Effect'
			else:
				for result in FP_EFFECT_RESULT_LIST:
					if roll <= profile[result]:
						result_text = result
						break
		
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
		
		profile['result'] = result_text
		
		ConsolePrintEx(attack_con, 13, 51, libtcod.BKGND_NONE,
			libtcod.CENTER, result_text)
		
		# display effect FP if it was successful area fire attack
		if profile['type'] == 'Area Fire' and result_text != 'NO EFFECT':
			ConsolePrintEx(attack_con, 13, 52, libtcod.BKGND_NONE,
				libtcod.CENTER, str(profile['effective_fp']) + ' FP')
		
		# check for RoF for gun / MG attacks
		if profile['type'] not in ['ap', 'FP Resolution'] and profile['weapon'].GetStat('rof') is not None:
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
	def CheckAttack(self, attacker, weapon, target):
		
		if weapon.GetStat('type') == 'Gun' and weapon.current_ammo is not None:
			if weapon.ammo_stores[weapon.current_ammo] == 0:
				return 'No ammo of this type remaining'
			if weapon.current_ammo == 'AP' and not target.known:
				return 'Target must be spotted for this attack'
			if weapon.current_ammo == 'AP' and target.GetStat('category') == 'Infantry':
				return 'AP has no effect on infantry'
			if weapon.current_ammo == 'AP' and target.GetStat('category') == 'Gun':
				return 'AP cannot harm guns'
		
		# check range to target
		distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
		if distance > weapon.max_range:
			return 'Beyond maximum weapon range'
		
		# check covered arc
		mount = weapon.GetStat('mount')
		if mount is not None:
			if weapon.GetStat('mount') == 'Turret':
				direction = attacker.turret_facing
			else:
				direction = attacker.facing
			if (target.hx - attacker.hx, target.hy - attacker.hy) not in HEXTANTS[direction]:
				return "Outside of weapon's covered arc"
		
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
		
		# check LoS
		if GetLoS(attacker.hx, attacker.hy, target.hx, target.hy) == -1.0:
			return 'No line of sight to target'
		
		# check that weapon can fire
		if weapon.fired:
			text = 'Weapon already fired'
			if weapon.GetStat('mount') == 'Turret':
				text += '; turret rotation NA'
			return text
		
		# check that proper crew action is set for this attack if required
		position_list = weapon.GetStat('fired_by')
		if position_list is not None:
			weapon_type = weapon.GetStat('type')
			if weapon_type in ['Gun', 'Co-ax MG']:
				action = 'Operate Gun'
			elif weapon_type == 'Hull MG':
				action = 'Operate Hull MG'
			
			if not attacker.CrewActionPossible(position_list, action):
				text = 'No crewman available to: ' + action
				return text

		# attack can proceed
		return ''
	
	# calculate the chance of a unit getting a bonus move after a given move
	# hx, hy is the move destination hex
	def CalcBonusMove(self, unit, hx, hy):
		
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
			chance = chance * 0.5
		
		# movement class modifier
		movement_class = unit.GetStat('movement_class')
		if movement_class is not None:
			if movement_class == 'Fast Tank':
				chance += 15.0
			elif movement_class == 'Infantry':
				chance -= 50.0
			elif movement_class == 'Wheeled':
				if dirt_road:
					chance += 30.0
				else:
					chance -= 30.0
		
		# direct driver modifier
		if unit.CheckCrewAction(['Commander', 'Commander/Gunner'], 'Direct Driver'):
			chance += 15.0
		
		# previous bonus move modifier
		if unit.additional_moves_taken > 0:
			for i in range(unit.additional_moves_taken):
				chance = chance * BONUS_CHANCE_MULTIPLIER
		
		return RestrictChance(chance)
	
	# display a pop-up message overtop the map viewport
	# if hx and hy are not none, highlight this hex on the map viewport
	# if portrait is not None, display a unit portrait above/below the message window
	def ShowMessage(self, message, hx=None, hy=None, portrait=None):
		
		# encode message for display
		message = message.encode('IBM850')
		
		# enable hex highlight if any
		if hx is not None and hy is not None:
			self.highlighted_hex = (hx, hy)
			UpdateUnitCon()
			UpdateScenarioDisplay()
		
		# determine if window needs to be shifted to bottom half of screen
		# so that highlighted hex is not obscured
		switch = False
		if hx is not None and hy is not None:
			for (vp_hx, vp_hy) in VP_HEXES:
				if scenario.map_vp[(vp_hx, vp_hy)] == (hx, hy):
					if vp_hy < int((0 - vp_hx) / 2):
						switch = True
					break
		if switch:
			y_start = 36
		else:
			y_start = 16
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_blit(popup_bkg, 0, 0, 0, 0, 0, 44, y_start)
		y = y_start+1
		lines = wrap(message, 27)
		# max 7 lines tall
		for line in lines[:7]:
			ConsolePrint(0, 45, y, line)
			y += 1
		
		if portrait is not None:
			if switch:
				y = 45
			else:
				y = 8
			libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, 0, 47, y)
		
		libtcod.console_flush()
		
		# FUTURE: get message pause time from settings
		wait_time = 60 + (len(lines) * 60)
		Wait(wait_time)
		
		# clear hex highlight if any
		if hx is not None and hy is not None:
			self.highlighted_hex = None
			UpdateUnitCon()
			UpdateScenarioDisplay()
		else:
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()


# Crew Class: represents a crewman in a vehicle or a single member of a unit's personnel
class Crew:
	def __init__(self, nation, position):
		self.first_name = u''				# name, set by GenerateName()
		self.last_name = u''
		self.nation = nation
		self.GenerateName()				# generate random first and last name
		
		self.current_position = position		# pointer to current position in a unit
		
		self.age = 0					# age of crewman in years
		self.GenerateAge()
		
		self.rank = 0					# rank level
		self.rank_desc = ''				# text name for rank
		self.SetRank()
		
		self.morale = 0.0				# morale level, will be set later on
		self.morale_desc = ''				# text description of morale
		
		self.status = 'Alert'				# current mental/physical status
		
		self.action_list = []				# list of possible special actions
		self.current_action = 'None'			# currently active action
		
		self.fov = set()				# set of visible hexes
		
		self.stats = {}					# dictionary of stat values
		for stat_name in STAT_NAMES:
			self.stats[stat_name] = 0
		
		self.GenerateStats()

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
			
		# get list of possible first and last names
		with open(DATAPATH + 'nation_defs.json') as data_file:
			nations = json.load(data_file)
		
		first_name = choice(nations[self.nation]['first_names'])
		self.first_name = FixName(first_name)
		last_name = choice(nations[self.nation]['surnames'])
		self.last_name = FixName(last_name)
			
	# return the crewman's full name as an encoded string
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
	
	# set rank based on current position
	def SetRank(self):
		if self.current_position.name in ['Commander', 'Commander/Gunner']:
			self.rank = 3
		elif self.current_position.name in ['Gunner', 'Driver']:
			self.rank = 2
		else:
			self.rank = 1
		
		with open(DATAPATH + 'nation_defs.json') as data_file:
			nations = json.load(data_file)
		
		self.rank_desc = nations[self.nation]['rank_names'][str(self.rank)]
	
	# generate a new set of stats for this crewman
	def GenerateStats(self):
		
		for tries in range(300):
			value_list = []
			total = 0
			for i in range(4):
				new_value = libtcod.random_get_int(0, 5, 50) + libtcod.random_get_int(0, 5, 50)
				new_value = int(new_value / 10)
				value_list.append(new_value)
				total += new_value
			
			# check that total stat values fall within a given range
			if 12 <= total <= 32:
				break
		
		# set stat values
		i = 0
		for key in STAT_NAMES:
			self.stats[key] = value_list[i]
			i+=1
	
	# set this crewman's morale level based on base level for unit
	def SetMorale(self, base_level):
		(min_lvl, max_lvl) = MORALE_LEVELS[base_level]
		base_level = (min_lvl + max_lvl) / 2.0
		self.morale = base_level - 5.0 + float(libtcod.random_get_int(0, 0, 5) + libtcod.random_get_int(0, 0, 5))
		
		if self.current_position.name in ['Commander', 'Commander/Gunner']:
			self.morale += 5.0
		
		if self.morale > 100.0:
			self.morale = 100.0
		for k, (min_lvl, max_lvl) in MORALE_LEVELS.iteritems():
			if min_lvl < self.morale < max_lvl:
				self.morale_desc = k
				break
	
	# returns True if this crewman is currently able to choose an action
	def AbleToAct(self):
		if self.status in ['Unconscious', 'Dead']:
			return False
		return True
	
	# set a new action; if True, select next in list, otherwise previous
	def SetAction(self, forward):
		
		# crewman cannot act
		if self.current_action == 'N/A':
			return False
		
		# no other actions possible
		if len(self.action_list) == 1:
			return False
		
		# action was set automatically, cannot change
		if 'selectable' not in CREW_ACTIONS[self.current_action]:
			return False
		
		i = self.action_list.index(self.current_action)
		
		if forward:
			if i == len(self.action_list) - 1:
				self.current_action = self.action_list[0]
			else:
				self.current_action = self.action_list[i+1]
		
		else:
			if i == 0:
				self.current_action = self.action_list[-1]
			else:
				self.current_action = self.action_list[i-1]
		
		return True


# Crew Position class: represents a crew position on a vehicle or gun
class CrewPosition:
	def __init__(self, name, location, hatch, hatch_group, open_visible, closed_visible):
		self.name = name
		self.location = location
		self.crewman = None			# pointer to crewman currently in this position
		
		# hatch existence and status
		self.hatch_open = True
		self.hatch = hatch
		self.hatch_group = None
		if hatch_group is not None:
			self.hatch_group = int(hatch_group)
		
		# visible hextants when hatch is open/closed
		self.open_visible = []
		if open_visible is not None:
			for direction in open_visible:
				self.open_visible.append(int(direction))
		self.closed_visible = []
		if closed_visible is not None:
			for direction in closed_visible:
				self.closed_visible.append(int(direction))
	
	# toggle hatch open/closed status
	def ToggleHatch(self):
		if not self.hatch: return False
		self.hatch_open = not self.hatch_open
		# FUTURE: also toggle hatches in same group
		return True


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
			if self.stats['type'] == 'Co-ax MG':
				self.max_range = 3
			elif self.stats['type'] == 'Hull MG':
				self.max_range = 1
		
		# set up ammo stores if gun with types of ammo
		self.ammo_stores = None
		if self.GetStat('type') == 'Gun' and 'ammo_type_list' in self.stats:
			self.ammo_stores = {}
			
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
		
		# TODO: set up ready rack if any
		
		self.InitScenarioStats()

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
			print 'ERROR: ' + self.stats['name'] + ' is not a gun, cannot generate effective FP'
			return 1
		
		for (calibre, fp) in HE_FP_EFFECT:
			if calibre <= int(self.GetStat('calibre')):
				return fp
		
		print 'ERROR: Could not find effective FP for: ' + self.stats['name']
		return 1
	
	# return the base penetration chance of an HE hit from this gun
	def GetBaseHEPenetrationChance(self):
		if self.GetStat('type') != 'Gun':
			print 'ERROR: ' + self.stats['name'] + ' is not a gun, cannot generate HE AP chance'
			return 0.0
		
		for (calibre, chance) in HE_AP_CHANCE:
			if calibre <= int(self.GetStat('calibre')):
				return chance
		
		print 'ERROR: Could not find HE AP chance for: ' + self.stats['name']
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
		self.ai = None				# AI controller
		self.dummy = False			# unit is a false report, erased upon reveal
		
		# load unit stats from JSON file
		with open(DATAPATH + 'unit_type_defs.json') as data_file:
			unit_types = json.load(data_file)
		if unit_id not in unit_types:
			print 'ERROR: Could not find unit id: ' + unit_id
			self.unit_id = None
			return
		self.stats = unit_types[unit_id].copy()
		self.owning_player = None		# player that controls this unit
		self.nation = None			# nation of unit's crew
		
		self.crew_list = []			# list of pointers to crew/personnel
		self.base_morale_level = ''		# base morale level for personnel
		self.morale_desc = ''			# description of current effective morale level
		self.crew_positions = []		# list of crew positions
		
		if 'crew_positions' in self.stats:
			for position in self.stats['crew_positions']:
				name = position['name']
				
				# infantry units don't have locations as such
				location = None
				if 'location' in position:
					location = position['location']
				
				hatch = False
				if 'hatch' in position:
					hatch = True
				
				hatch_group = None
				if 'hatch_group' in position:
					hatch_group = position['hatch_group']
				
				open_visible = None
				if 'open_visible' in position:
					open_visible = position['open_visible']
				
				closed_visible = None
				if 'closed_visible' in position:
					closed_visible = position['closed_visible']
				
				self.crew_positions.append(CrewPosition(name, location,
					hatch, hatch_group, open_visible, closed_visible))
		
		self.weapon_list = []			# list of weapon systems
		weapon_list = self.stats['weapon_list']
		if weapon_list is not None:
			for weapon in weapon_list:
				
				# create a Weapon object and store in unit's weapon list
				new_weapon = Weapon(weapon)
				self.weapon_list.append(new_weapon)
			
			# clear this stat since we don't need it any more
			self.stats['weapon_list'] = None
		
		self.InitScenarioStats()

	# set up any data that is unique to a scenario
	def InitScenarioStats(self):
		self.alive = True			# unit is not out of action
		self.dummy = False			# unit will disappear when spotted - AI units only
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
		self.misses_turns = 0			# turns outstanding left to be missed
		
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
		
		# mark place in case we skip unit status display
		ys = 15
		if status:
		
			# unit status
			libtcod.console_set_default_foreground(console, libtcod.light_grey)
			libtcod.console_set_default_background(console, libtcod.darkest_blue)
			libtcod.console_rect(player_info_con, x, y+ys, 24, 2, True, libtcod.BKGND_SET)
			
			text = ''
			if self.moved:
				text += 'Moved '
			if self.fired:
				text += 'Fired '
			ConsolePrint(console, x, y+ys+1, text)
			
			ys = 17
		
		# morale level of unit overall
		libtcod.console_set_default_foreground(console, libtcod.white)
		libtcod.console_set_default_background(console, libtcod.darker_cyan)
		libtcod.console_rect(console, x, y+ys, 24, 1, True, libtcod.BKGND_SET)
		ConsolePrint(console, x, y+ys, self.morale_desc)
		
		libtcod.console_set_default_background(console, libtcod.black)

	
	# do automatic actions before an activation
	def DoPreActivation(self):
		
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
		
		# generate list of selectable crew actions
		for position in self.crew_positions:
			
			# no crewman in this position
			if position.crewman is None: continue
			
			action_list = []
			
			# crewman cannot act
			if not position.crewman.AbleToAct():
				position.crewman.current_action = 'N/A'
			else:
				# reset current action unless previous was selected
				if 'selectable' not in CREW_ACTIONS[position.crewman.current_action]:
					position.crewman.current_action = 'None'
				
				for action_name in CREW_ACTIONS:
					
					# skip if not selectable
					if 'selectable' not in CREW_ACTIONS[action_name]:
						continue
					
					# action restricted to a list of positions
					if 'position_list' in CREW_ACTIONS[action_name]:
						if position.name not in CREW_ACTIONS[action_name]['position_list']:
							continue
					action_list.append(action_name)
			
			# copy over the list to the crewman
			position.crewman.action_list = action_list[:]
			
			# if previous action was selected and no longer available, reset
			if 'selectable' in CREW_ACTIONS[position.crewman.current_action]:
				if position.crewman.current_action not in position.crewman.action_list:
					position.crewman.current_action = 'None'
		
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
			
			# clear player target if no longer possible
			if scenario.player_target is not None:
				if scenario.player_target not in scenario.player_target_list:
					scenario.player_target = None
			
			# turn on player LoS display
			scenario.player_los_active = True
			UpdateUnitCon()
		
		# reset flag and weapons
		self.fired = False
		for weapon in self.weapon_list:
			weapon.ResetForNewTurn()
		
		UpdateScenarioDisplay()
	
	# do automatic actions after an activation
	def DoPostActivation(self):
		# if unit moved, lose any acquired targets and lose
		#   any acquired target status
		if self.moved:
			self.ClearAcquiredTargets()
		
		if self.facing is not None:
			if self.facing != self.previous_facing:
				self.moved = True
				
				# lose any of this unit's acquired targets
				self.acquired_target = None
		
		# clear any player LoS
		if self == scenario.player_unit:
			scenario.player_los_active = False
			UpdateUnitCon()
		
		# test for recovery
		self.RecoveryCheck()
		
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
		
		map_hex.unit_stack.remove(self)
		map_hex.unit_stack.insert(0, self)
	
	# check for recovery for the unit and for personnel
	# normally called at end of own turn
	def RecoveryCheck(self):
		
		# check for personnel status recovery first
		for position in self.crew_positions:
			if position.crewman is None: continue
			if position.crewman.status not in ['Stunned', 'Unconscious']: continue
			
			# TODO: roll for recovery from Stunned
			if position.crewman.status == 'Stunned':
				continue
		
		# check for unit recovering from Broken status
		if self.broken:
			if self.MoraleCheck(BROKEN_MORALE_MOD):
				self.broken = False
				text = self.GetName() + ' recovers from being Broken.'
				scenario.ShowMessage(text, self.hx, self.hy)
			return
		
		# check for unit recovering from Pinned status
		if self.pinned:
			if self.MoraleCheck(0):
				self.pinned = False
				text = self.GetName() + ' recovers from being Pinned.'
				scenario.ShowMessage(text, self.hx, self.hy)
	
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
		
		if self == scenario.player_unit:
			text = 'You are now concealed from the enemy'
		else:
			text = 'Lost contact with ' + self.GetName()
		scenario.ShowMessage(text, hx=self.hx, hy=self.hy)
		self.known = False
		UpdateUnitCon()
		UpdateUnitInfoCon()
		UpdateScenarioDisplay()
	
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
			
			visible_hextants = []
			
			# infantry and gun crew can see all around
			if self.GetStat('category') in ['Infantry', 'Gun']:
				visible_hextants = [0,1,2,3,4,5]
				max_distance = MAX_LOS_DISTANCE
			else:
				if not position.hatch:
					visible_hextants = position.closed_visible[:]
					max_distance = MAX_BU_LOS_DISTANCE
				else:
					if position.hatch_open:
						visible_hextants = position.open_visible[:]
						max_distance = MAX_LOS_DISTANCE
					else:
						visible_hextants = position.closed_visible[:]
						max_distance = MAX_BU_LOS_DISTANCE
			
			# restrict visible hextants and max distance if crewman did a
			# special action last turn
			if position.crewman.current_action is not None:
				action = CREW_ACTIONS[position.crewman.current_action]
				if 'fov_hextants' in action:
					visible_hextants = []
					for text in action['fov_hextants']:
						visible_hextants.append(int(text))
				if 'fov_range' in action:
					if int(action['fov_range']) < max_distance:
						max_distance = int(action['fov_range'])
			
			if self.facing is not None:
				# rotate visible hextants based on current turret/hull facing
				if position.location == 'Turret':
					direction = self.turret_facing
				else:
					direction = self.facing
				if direction != 0:
					for i, hextant in enumerate(visible_hextants):
						visible_hextants[i] = ConstrainDir(hextant + direction)
			
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
		#print 'FoV calculation for ' + self.unit_id + ' took ' + str(time_taken) + ' ms.'
	
	# generate a new crew sufficent to man all crew positions
	def GenerateNewCrew(self):
		for position in self.crew_positions:
			new_crew = Crew(self.nation, position)
			new_crew.SetMorale(self.base_morale_level)
			self.crew_list.append(new_crew)
			position.crewman = self.crew_list[-1]
		# set current average morale level description
		total_morale = 0.0
		for crewman in self.crew_list:
			total_morale += crewman.morale
		total_morale = total_morale / len(self.crew_list)
		for k, (min_lvl, max_lvl) in MORALE_LEVELS.iteritems():
			if min_lvl < total_morale < max_lvl:
				self.morale_desc = k
				break
	
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
	
	# attempt to move forward into next map hex
	# returns True if move was a success, false if not
	def MoveForward(self):
		
		# no moves remaining
		if self.move_finished:
			return False
		# already fired
		if self.fired:
			return False
		
		# try to set crewman action
		if not self.SetCrewAction(['Driver'], 'Drive'):
			return False
		
		# determine target hex
		(hx, hy) = GetAdjacentHex(self.hx, self.hy, self.facing)
		
		# target hex is off map
		if (hx, hy) not in scenario.cd_hex.map_hexes:
			return False
		
		map_hex1 = scenario.cd_hex.map_hexes[(self.hx, self.hy)]
		map_hex2 = scenario.cd_hex.map_hexes[(hx, hy)]
		
		# target hex can't be entered
		if map_hex2.terrain_type == 'pond':
			return False
		
		# river on edge and no road link
		if len(map_hex1.river_edges) > 0:
			direction = GetDirectionToAdjacent(self.hx, self.hy, hx, hy)
			if direction in map_hex1.river_edges:
				if direction not in map_hex1.dirt_roads:
					return False
		
		# already occupied by enemy
		for unit in map_hex2.unit_stack:
			if unit.owning_player != self.owning_player:
				return False
		
		# calculate bonus move chance
		chance = scenario.CalcBonusMove(self, hx, hy)
		
		# do movement animation and sound if applicable
		if self.vp_hx is not None and self.vp_hy is not None:
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
		
		self.hx = hx
		self.hy = hy
		
		# add to new map hex unit stack
		map_hex2.unit_stack.append(self)
		
		# recalculate new FoV for unit
		self.CalcFoV()
		
		# set flag
		self.moved = True
		
		# check for bonus move
		roll = GetPercentileRoll()
		if roll <= chance:
			self.additional_moves_taken += 1
		else:
			self.move_finished = True
		
		return True
	
	# pivot the unit facing one hextant
	def Pivot(self, clockwise):
		
		if self.facing is None: return False
		
		# no moves remaining
		if self.move_finished:
			return False
		if self.fired:
			return False
		
		# make sure crewman can drive
		if not self.SetCrewAction(['Driver'], 'Drive'):
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
			elif weapon_type == 'Hull MG':
				action = 'Operate Hull MG'
			self.SetCrewAction(position_list, action)
		
		# set weapon and unit fired flags
		weapon.fired = True
		self.fired = True
		
		# display message if player is the target
		if target == scenario.player_unit:
			text = self.GetName() + ' fires at you!'
			scenario.ShowMessage(text, hx=self.hx, hy=self.hy)
		
		# clear LoS if any
		if self == scenario.player_unit:
			scenario.player_los_active = False
			UpdateUnitCon()
			UpdateScenarioDisplay()
			libtcod.console_flush()
		
		# attack loop, can do multiple shots if maintain RoF
		attack_finished = False
		while not attack_finished: 
		
			# play sound and show animation if both units on viewport
			if self.vp_hx is not None and self.vp_hy is not None and target.vp_hx is not None and target.vp_hy is not None:
				
				# TEMP: uses the root console, future will have an animation console
				
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
						Wait(8)
					
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
				
				elif weapon.GetStat('type') in ['Co-ax MG', 'Hull MG']:
					
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
			
			# display the attack to the screen
			scenario.DisplayAttack(profile)
			
			# pause if we're not doing a RoF attack
			if not profile['weapon'].maintained_rof:
				WaitForContinue()
			
			# do the roll and display results to the screen
			profile = scenario.DoAttackRoll(profile)
			
			# if we maintain RoF, we might choose to attack again here
			end_pause = False
			attack_finished = True
			while not end_pause:
				if libtcod.console_is_window_closed(): sys.exit()
				libtcod.console_flush()
				event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS,
					key, mouse)
				
				if session.key_down:
					if event != libtcod.EVENT_KEY_RELEASE:
						continue
					session.key_down = False
				if event != libtcod.EVENT_KEY_PRESS:
					continue
				session.key_down = True
				
				key_char = DecodeKey(chr(key.c).lower())
				
				if key_char == 'c':
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
				
				if profile['result'] in ['CRITICAL EFFECT', 'FULL EFFECT', 'PARTIAL EFFECT']:
					
					# possible to apply an AP hit if MG within range
					if weapon.GetStat('type') in ['Co-ax MG', 'Hull MG'] and target.GetStat('armour') is not None:
						if GetHexDistance(self.hx, self.hy, target.hx, target.hy) <= MG_AP_RANGE:
							target.ap_hits_to_resolve.append(profile)
					
					target.fp_to_resolve += profile['effective_fp']
					
					# target will automatically be spotted next turn if possible
					if not target.known:
						target.hit_by_fp = 2
			
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
					
						# TODO: apply infantry moved modifier
						
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
		
		# attack is over, re-enable LoS if player unit
		if self == scenario.player_unit:
			scenario.player_los_active = True
			UpdateUnitCon()
			UpdateScenarioDisplay()
			libtcod.console_flush()
			Wait(15)
		
		return True
	
	# resolve all unresolved AP hits and FP on this unit
	# triggered at end of enemy combat phase
	def ResolveHits(self):
		
		# handle FP first
		if self.fp_to_resolve > 0:
			
			# TODO: handle possible crew injury for vehicle units
			if self.GetStat('category') != 'Vehicle':
				profile = scenario.CalcFP(self)
				scenario.DisplayAttack(profile)
				WaitForContinue()
				profile = scenario.DoAttackRoll(profile)
				WaitForContinue()
				
				# handle results
				if profile['result'] == 'Pin Test':
					modifier = self.fp_to_resolve * FP_MORALE_CHECK_MOD
					if not self.MoraleCheck(modifier):
						self.PinMe()
					else:
						text = self.GetName() + ' avoided being Pinned.'
						scenario.ShowMessage(text, self.hx, self.hy)
					
				# TODO: Handle Broken result
				elif profile['result'] == 'Break Test':
					pass
					
				elif profile['result'] == 'Destroyed':
					self.DestroyMe()
					return
					
			self.fp_to_resolve = 0
		
		# handle AP hits
		for profile in self.ap_hits_to_resolve:
			
			# TODO: determine if an AP roll must be made
			if self.GetStat('category') == 'Vehicle':
			
				profile = scenario.CalcAP(profile)
				scenario.DisplayAttack(profile)
				WaitForContinue()
				profile = scenario.DoAttackRoll(profile)
				WaitForContinue()
				if profile['result'] == 'PENETRATED':
					self.DestroyMe()
					return
		
		# clear unresolved hits
		self.ap_hits_to_resolve = []
	
	# do a morale check for this unit, result of FP attack, etc.
	def MoraleCheck(self, modifier):
		
		modifier = float(0 - modifier)
		
		# TODO: apply terrain modifiers
		
		# check against unit leader first
		leader = None
		for crewman in self.crew_list:
			if crewman.current_position.name in UNIT_LEADER_POSITIONS:
				leader = crewman
				break
		
		if leader is not None:
			if leader.AbleToAct():
				effective_morale = leader.morale + modifier
				roll = GetPercentileRoll()
				if roll <= effective_morale:
					return True
		
		# no leader or leader has failed check, check against remaining personnel
		crew_list = []
		for crewman in self.crew_list:
			if crewman.current_position in UNIT_LEADER_POSITIONS:
				continue
			# check for personnel incapacitated
			if not crewman.AbleToAct():
				continue
			crew_list.append(crewman)
		
		passed = 0
		half_crew = int(floor(len(self.crew_list) / 2))
		for crewman in crew_list:
			effective_morale = crewman.morale + modifier
			roll = GetPercentileRoll()
			if roll <= effective_morale:
				passed += 1
		
		if passed >= half_crew:
			return True
		return False
	
	# pin this unit
	def PinMe(self):
		self.pinned = True
		self.acquired_target = None
		UpdateUnitInfoCon()
		UpdateScenarioDisplay()
		text = self.GetName() + ' is now Pinned.'
		scenario.ShowMessage(text, self.hx, self.hy)
		
	# destroy this unit and remove it from the scenario map
	def DestroyMe(self):
		
		# debug flag
		if GODMODE and self == scenario.player_unit:
			print 'DEBUG: Player saved from destruction'
			return
		
		self.alive = False
		scenario.cd_hex.map_hexes[(self.hx, self.hy)].unit_stack.remove(self)
		self.ClearAcquiredTargets()
		UpdateUnitCon()
		UpdateScenarioDisplay()
	
	# roll a spotting check from this unit to another using the given crew position
	def DoSpotCheck(self, target, position):
		
		chance = 100.0
		
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
		
		# crew perception modifier
		chance += (position.crewman.stats['Perception'] - 5) * 5.0
		
		chance = RestrictChance(chance)
		
		# special: automatic spot cases
		if distance <= 2 and los == 0.0:
			chance = 100.0
		
		# target was hit by effective fp last turn
		if target.hit_by_fp > 0:
			chance = 100.0
		
		roll = GetPercentileRoll()
		
		if roll <= chance:
			target.SpotMe()
			# display pop-up message window
			
			if self == scenario.player_unit:
				
				if target.dummy:
					text = (position.crewman.GetFullName() + ' says: ' + 
						"Thought there was something there, but I don't see anything.")
					portrait = None
				else:
					text = position.crewman.GetFullName() + ' says: '
					text += target.GetName() + ' ' + target.GetStat('class')
					text += ' spotted!'
					portrait = target.GetStat('portrait')
				scenario.ShowMessage(text, hx=target.hx, hy=target.hy, portrait=portrait)
			else:
				text = 'You have been spotted!'
				scenario.ShowMessage(text, hx=self.hx, hy=self.hy)
			
	# reveal this unit after being spotted
	def SpotMe(self):
		
		# dummy units are removed instead
		if self.dummy:
			self.DestroyMe()
			return
		
		self.known = True
		UpdateUnitCon()
		UpdateUnitInfoCon()
		UpdateScenarioDisplay()
	
	# returns true if a crewman in any of the given positions is avaible to have an action set
	def CrewActionPossible(self, position_list, action):
		for position in self.crew_positions:
			if position.name in position_list:
				if position.crewman is None: continue
				if position.crewman.current_action == 'N/A': continue
				
				# crewman already on this action
				# TODO: is this ok?
				if position.crewman.current_action == action:
					return True
				
				if position.crewman.current_action == 'None':
					return True
		return False
	
	# returns true if a crewman in any of the given positions is on the given action
	def CheckCrewAction(self, position_list, action):
		for position in self.crew_positions:
			if position.name in position_list:
				if position.crewman is None: continue
				if position.crewman.current_action == action:
					return True
		return False
	
	# check for a crewman in the given position, and try to set their action
	# assumes that the given action is available to every position in the list
	def SetCrewAction(self, position_list, action):
		
		for position in self.crew_positions:
			if position.name in position_list:
				if position.crewman is None: continue
				if position.crewman.current_action == 'N/A': continue
				
				# crewman already on this action
				# TODO: is this ok?
				if position.crewman.current_action == action:
					return True
				
				if position.crewman.current_action != 'None': continue
				
				position.crewman.current_action = action
				UpdateCrewPositionCon()
				return True
				
		return False



##########################################################################################
#                                  General Functions                                     #
##########################################################################################

# TESTING fix for Win10 PyInstaller overflow crash
# wrappers to cast text as a string object before sending to libtcod
def ConsolePrint(console, x, y, text):
	libtcod.console_print(console, x, y, str(text))
def ConsolePrintEx(console, x, y, flag1, flag2, text):
	libtcod.console_print_ex(console, x, y, flag1, flag2, str(text))


# return a random float between 0.0 and 100.0
def GetPercentileRoll():
	return float(libtcod.random_get_int(0, 1, 1000)) / 10.0


# restrict odds to between 3.0 and 97.0
def RestrictChance(chance):
	if chance < 3.0: return 3.0
	if chance > 97.0: return 97.0
	return chance


# load a console image from an .xp file
def LoadXP(filename):
	xp_file = gzip.open(DATAPATH + filename)
	raw_data = xp_file.read()
	xp_file.close()
	xp_data = xp_loader.load_xp_string(raw_data)
	console = libtcod.console_new(xp_data['width'], xp_data['height'])
	xp_loader.load_layer_to_console(console, xp_data['layer_data'][0])
	return console


# returns a path from one hex to another, avoiding impassible and difficult terrain
# based on function from ArmCom 1, which was based on:
# http://stackoverflow.com/questions/4159331/python-speed-up-an-a-star-pathfinding-algorithm
# http://www.policyalmanac.org/games/aStarTutorial.htm
def GetHexPath(hex_list, hx1, hy1, hx2, hy2, unit=None, road_path=False):
	
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
	for k, map_hex in hex_list.iteritems():
		map_hex.ClearPathInfo()
	
	node1 = hex_list[(hx1, hy1)]
	node2 = hex_list[(hx2, hy2)]
	open_list = set()	# contains the nodes that may be traversed by the path
	closed_list = set()	# contains the nodes that will be traversed by the path
	start = node1
	start.h = GetHexDistance(node1.hx, node1.hy, node2.hx, node2.hy)
	start.f = start.g + start.h
	end = node2
	open_list.add(start)		# add the start node to the open list
	
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
			
			# no map hex exists here, skip
			if (hx, hy) not in hex_list: continue
			
			node = hex_list[(hx, hy)]
			
			# ignore nodes on closed list
			if node in closed_list: continue
			
			# ignore impassible nodes
			if node.terrain_type == 'pond': continue
			
			# check that move into this new hex would be possible for unit
			if unit is not None:
				
				# FUTURE: calculate cost of movement for this unit
				cost = 1
			
			# we're creating a path for a road
			elif road_path:
				
				# prefer to use already-existing roads
				if direction in current.dirt_roads:
					cost = -5
				
				# prefer to pass through villages if possible
				if node.terrain_type == 'village':
					cost = -2
				elif node.terrain_type == 'forest':
					cost = 4
				elif node.terrain_type == 'fields_in_season':
					cost = 2
				else:
					cost = 0
				
				if node.elevation != current.elevation:
					cost = cost * 15
				
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


# returns which hexspine hx2, hy2 is along if the two hexes are along a hexspine
# otherwise returns -1
def GetHexSpine(hx1, hy1, hx2, hy2):
	# convert to cube coords
	(x1, y1, z1) = GetCubeCoords(hx1, hy1)
	(x2, y2, z2) = GetCubeCoords(hx2, hy2)
	# calculate change in values for each cube coordinate
	x = x2-x1
	y = y2-y1
	z = z2-z1
	# check cases where change would be along spine
	if x == y and z < 0: return 0
	if y == z and x > 0: return 1
	if x == z and y < 0: return 2
	if x == y and z > 0: return 3
	if y == z and x < 0: return 4
	if x == z and y > 0: return 5
	return -1


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


# return a list of hexes along a line from hex1 to hex2
# adapted from http://www.redblobgames.com/grids/hexagons/implementation.html#line-drawing
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
# FUTURE: find way to improve this function?
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
			# even -> odd column
			direction = 2
		else:
			# odd -> even column
			direction = 1
		(hx, hy) = GetAdjacentHex(hx, hy, direction)
	return hex_list


# plot the center of a given in-game hex on the scenario viewport console
# 0,0 appears in centre of vp console
def PlotHex(hx, hy):
	x = hx*4 + 23
	y = (hy*4) + (hx*2) + 23
	return (x+4,y+3)


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


# check for an unblocked line of sight between two hexes
# returns -1.0 if no LoS, otherwise returns total terrain modifier for the line
def GetLoS(hx1, hy1, hx2, hy2):
	
	# handle the easy cases first
	
	distance = GetHexDistance(hx1, hy1, hx2, hy2)
	
	# too far away
	if distance > MAX_LOS_DISTANCE:
		return -1.0
	
	# same hex
	if hx1 == hx2 and hy1 == hy2:
		return scenario.cd_hex.map_hexes[(hx2, hy2)].GetTerrainMod()
	
	# adjacent hex
	if distance == 1:
		return scenario.cd_hex.map_hexes[(hx2, hy2)].GetTerrainMod()
	
	# store info about the starting and ending hexes for this LoS
	start_elevation = float(scenario.cd_hex.map_hexes[(hx1, hy1)].elevation)
	end_elevation = float(scenario.cd_hex.map_hexes[(hx2, hy2)].elevation)
	# calculate the slope from start to end hex
	los_slope = ((end_elevation - start_elevation) * ELEVATION_M) / (float(distance) * 160.0)
	
	# build a list of hexes along the LoS
	hex_list = []
	
	# lines of sight along hex spines need a special procedure
	mod_list = None
	hex_spine = GetHexSpine(hx1, hy1, hx2, hy2)
	if hex_spine > -1:
		mod_list = HEXSPINES[hex_spine]
		
		# start with first hex
		hx = hx1
		hy = hy1
		
		while hx != hx2 or hy != hy2:
			# break if we've gone off map
			if (hx, hy) not in scenario.cd_hex.map_hexes: break
			
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
	
	# now that we have the list of hexes along the LoS, run through them, and if an
	#   intervening hex elevation blocks the line, we can return -1
	
	# if a terrain feature intersects the line, we add its effect to the total LoS hinderance
	total_mod = 0.0
	
	# we need a few variables to temporarily store information about the first hex of
	#   a hex pair, to compare it with the second of the pair
	hexpair_floor_slope = None
	hexpair_terrain_slope = None
	hexpair_terrain_mod = None
	
	for (hx, hy) in hex_list:
		
		# hex is off map
		if (hx, hy) not in scenario.cd_hex.map_hexes: continue
		
		# hex is beyond the maximum LoS distance (should not happen)
		if GetHexDistance(hx1, hy1, hx, hy) > MAX_LOS_DISTANCE: return -1
		
		map_hex = scenario.cd_hex.map_hexes[(hx, hy)]
		elevation = (float(map_hex.elevation) - start_elevation) * ELEVATION_M
		distance = float(GetHexDistance(hx1, hy1, hx, hy))
		floor_slope = elevation / (distance * 160.0)
		terrain_slope = (elevation + TERRAIN_LOS_HEIGHT[map_hex.terrain_type]) / (distance * 160.0)
		terrain_mod = map_hex.GetTerrainMod()
		
		# if we're on a hexspine, we need to compare some pairs of hexes
		# the lowest floor slope of both hexes is used
		if mod_list is not None:
			index = hex_list.index((hx, hy))
			# hexes 0,3,6... are stored for comparison
			if index % 3 == 0:
				hexpair_floor_slope = floor_slope
				hexpair_terrain_slope = terrain_slope
				hexpair_terrain_mod = terrain_mod
				continue
			# hexes 1,4,7... are compared with stored values from other hex in pair
			elif (index - 1) % 3 == 0:
				if hexpair_floor_slope < floor_slope:
					floor_slope = hexpair_floor_slope
					terrain_slope = hexpair_terrain_slope
					terrain_mod = hexpair_terrain_mod

		# now we compare the floor slope of this hex to that of the LoS, the LoS
		# is blocked if it is higher
		if floor_slope > los_slope:
			return -1
		
		# if the terrain intervenes, then we add its modifier to the total
		if terrain_slope > los_slope:
			total_mod += terrain_mod
			# if total modifier is too high, LoS is blocked
			if total_mod > MAX_LOS_MOD:
				return -1.0

	return total_mod


# wait for a specified amount of miliseconds, refreshing the screen in the meantime
def Wait(wait_time):
	wait_time = wait_time * 0.01
	start_time = time.time()
	while time.time() - start_time < wait_time:
		libtcod.console_flush()


# wait for player to press continue key
# option to allow backspace pressed instead, returns True if so 
def WaitForContinue(allow_cancel=False):
	end_pause = False
	cancel = False
	while not end_pause:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS,
			key, mouse)
		if session.key_down:
			if event != libtcod.EVENT_KEY_RELEASE:
				continue
			session.key_down = False
		if event != libtcod.EVENT_KEY_PRESS:
			continue
		session.key_down = True
		
		if key.vk == libtcod.KEY_BACKSPACE and allow_cancel:
			end_pause = True
			cancel = True
		elif DecodeKey(chr(key.c).lower()) == 'c':
			end_pause = True
	if allow_cancel and cancel:
		return True
	return False


# save the current game in progress
def SaveGame():
	save = shelve.open('savegame', 'n')
	save['campaign'] = campaign
	save['campaign_day'] = campaign_day
	save['version'] = VERSION		# for now the saved version must be identical to the current one
	save.close()


# load a saved game
def LoadGame():
	global campaign, campaign_day
	save = shelve.open('savegame')
	campaign = save['campaign']
	campaign_day = save['campaign_day']
	save.close()


# check the saved game to see if it is compatible with the current game version
def CheckSavedGameVersion():
	save = shelve.open('savegame')
	saved_version = save['version']
	save.close()
	if saved_version == VERSION:
		return True
	return False

# remove a saved game, either because the scenario is over or the player abandoned it
def EraseGame():
	os.remove('savegame')


# try to load game settings from config file
def LoadCFG():
	
	global config
	
	config = ConfigParser.RawConfigParser()
	
	# create a new config file
	if not os.path.exists(DATAPATH + 'armcom2.cfg'):
		print 'No config file found, creating a new one'
		config.add_section('ArmCom2')
		config.set('ArmCom2', 'large_display_font', 'true')
		#config.set('ArmCom2', 'animation_speed', '30')
		config.set('ArmCom2', 'sounds_enabled', 'true')
		config.set('ArmCom2', 'keyboard', '0')
		
		# write to disk
		with open(DATAPATH + 'armcom2.cfg', 'wb') as configfile:
			config.write(configfile)
	else:
		# load config file
		config.read(DATAPATH + 'armcom2.cfg')


# save current config to file
def SaveCFG():
	with open(DATAPATH + 'armcom2.cfg', 'wb') as configfile:
		config.write(configfile)


# generate keyboard encoding and decoding dictionaries
def GenerateKeyboards():
	
	global keyboard_decode, keyboard_encode

	keyboard_decode = {}
	keyboard_encode = {}
	with open(DATAPATH + 'keyboard_mapping.json') as data_file:
		keyboards = json.load(data_file)
	dictionary = keyboards[KEYBOARDS[config.getint('ArmCom2', 'keyboard')]]
	for k, value in dictionary.iteritems():
		keyboard_decode[key] = value
		keyboard_encode[value] = k

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
		print 'ERROR: Sound not found: ' + sound_name
		return
	
	channel = mixer.Mix_PlayChannel(-1, session.sample[sound_name], 0)
	if channel == -1:
		print 'ERROR: could not play sound: ' + sound_name
		print mixer.Mix_GetError()
	return channel


# select and play a sound effect for a given situation
def PlaySoundFor(obj, action):
	
	# sounds disabled
	if not config.getboolean('ArmCom2', 'sounds_enabled'):
		return
	
	if action == 'fire':
		if obj.GetStat('type') == 'Gun':
			
			if obj.GetStat('name') == 'AT Rifle':
				PlaySound('at_rifle_firing')
				return
			
			# TEMP - can add more detail in future
			n = libtcod.random_get_int(0, 0, 3)
			PlaySound('37mm_firing_0' + str(n))
			return
			
		# TEMP - only one MG sound effect for now
		if obj.stats['type'] in ['Co-ax MG', 'Hull MG']:
			PlaySound('zb_53_mg_00')
			return
	 
	elif action == 'he_explosion':
		# TEMP - more detail to come
		n = libtcod.random_get_int(0, 0, 1)
		PlaySound('37mm_he_explosion_0' + str(n))
		return
	
	elif action == 'movement':
		if obj.GetStat('movement_class') == 'Fast Tank':
			n = libtcod.random_get_int(0, 0, 2)
			PlaySound('light_tank_moving_0' + str(n))
			return


##########################################################################################
#                              In-Game Menus and Displays                                #
##########################################################################################

# display the in-game menu to screen, with the given tab active
# TODO: can be called from campaign calendar, campaign day, or scenario interfaces
def ShowGameMenu(active_tab):
	
	# draw the contents of the currently active tab to the menu console
	def DrawMenuCon(active_tab):
		# blit menu background to game menu console
		libtcod.console_blit(game_menu_bkg, 0, 0, 0, 0, game_menu_con, 0, 0)
		
		# fill in active tab info
		
		# Game Menu
		if active_tab == 0:
		
			libtcod.console_set_default_foreground(game_menu_con, ACTION_KEY_COL)
			ConsolePrint(game_menu_con, 25, 22, 'Esc')
			ConsolePrint(game_menu_con, 25, 24, 'Q')
			ConsolePrint(game_menu_con, 25, 25, 'A')
			
			libtcod.console_set_default_foreground(game_menu_con, libtcod.lighter_grey)
			ConsolePrint(game_menu_con, 30, 22, 'Return to Game')
			ConsolePrint(game_menu_con, 30, 24, 'Save and Quit to Main Menu')
			ConsolePrint(game_menu_con, 30, 25, 'Abandon Game')
		
		elif active_tab == 3:
			
			# display list of crew
			DisplayCrew(scenario.player_unit, game_menu_con, 6, 13, True)
			
			# display info on selected crewman
			crewman = scenario.player_unit.crew_positions[scenario.selected_position].crewman
			if crewman is not None:
				DisplayCrewInfo(crewman, game_menu_con, 37, 8)
			
			libtcod.console_set_default_foreground(game_menu_con, ACTION_KEY_COL)
			ConsolePrint(game_menu_con, 6, 40, EncodeKey('w').upper() + '/' + EncodeKey('s').upper())
			
			libtcod.console_set_default_foreground(game_menu_con, libtcod.lighter_grey)
			ConsolePrint(game_menu_con, 11, 40, 'Select Crew')
		
		libtcod.console_blit(game_menu_con, 0, 0, 0, 0, 0, 3, 3)
		libtcod.console_flush()
	
	# create a local copy of the current screen to re-draw when we're done
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
	# darken screen background
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
	
	# generate menu console for the first time and blit to screen
	DrawMenuCon(active_tab)
	
	# get input from player
	exit_menu = False
	result = ''
	while not exit_menu:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS,
			key, mouse)
		if session.key_down:
			if event != libtcod.EVENT_KEY_RELEASE:
				continue
			session.key_down = False
		if event != libtcod.EVENT_KEY_PRESS:
			continue
		session.key_down = True
		
		# Activate Different Menu
		if key.vk == libtcod.KEY_ESCAPE and active_tab != 0:
			active_tab = 0
			DrawMenuCon(active_tab)
			continue
		elif key.vk == libtcod.KEY_F3 and active_tab != 3:
			active_tab = 3
			DrawMenuCon(active_tab)
			continue
		
		key_char = chr(key.c).lower()
		
		# Game Menu
		if active_tab == 0:
			
			if key.vk == libtcod.KEY_ESCAPE:
				exit_menu = True
			
			elif key_char == 'q':
				SaveGame()
				session.exiting_to_main_menu = True
				result = 'exit_game'
				exit_menu = True
			
			elif key_char == 'a':
				text = 'Abandoning will erase the saved game.'
				result = ShowNotification(text, confirm=True)
				if result:
					EraseGame()
					session.exiting_to_main_menu = True
					result = 'exit_game'
					exit_menu = True
				libtcod.console_blit(game_menu_con, 0, 0, 0, 0, 0, 3, 3)
				libtcod.console_flush()
		
		# Crew Menu
		elif active_tab == 3:
			
			key_char = DecodeKey(key_char)
			
			# change selected crewman
			if key_char in ['w', 's']:
				
				if key_char == 'w':
					if scenario.selected_position > 0:
						scenario.selected_position -= 1
					else:
						scenario.selected_position = len(scenario.player_unit.crew_positions) - 1
				
				else:
					if scenario.selected_position == len(scenario.player_unit.crew_positions) - 1:
						scenario.selected_position = 0
					else:
						scenario.selected_position += 1
				UpdateContextCon()
				UpdateCrewPositionCon()
				DrawMenuCon(active_tab)

	libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
	del temp_con
	return result


# display information about a scenario about to start
def DisplayScenInfo():
	
	# create a local copy of the current screen to re-draw when we're done
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
	# darken screen background
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
	
	# load and build scenario info window
	scen_info_con = LoadXP('scen_summary_bkg.xp')
	# TEMP: most of this will be drawn from scenario object in future
	libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
	ConsolePrintEx(scen_info_con, 14, 1, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Western Poland')
	ConsolePrintEx(scen_info_con, 14, 2, libtcod.BKGND_NONE,
		libtcod.CENTER, 'September 1939')
	text = str(campaign.calendar['hour']) + ':' + str(campaign.calendar['minute']).zfill(2)
	ConsolePrintEx(scen_info_con, 14, 3, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	libtcod.console_set_default_foreground(scen_info_con, libtcod.light_grey)
	text = ('You have advanced into an area held by enemy forces. You must capture this area ' +
		'in order to continue your advance.')
	lines = wrap(text, 25)
	y = 7
	for line in lines[:9]:
		ConsolePrint(scen_info_con, 2, y, line)
		y+=1
	
	ConsolePrintEx(scen_info_con, 14, 20, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Light Armour')
	
	ConsolePrint(scen_info_con, 1, 27, '1) Capture all objectives')
	ConsolePrintEx(scen_info_con, 14, 29, libtcod.BKGND_NONE,
		libtcod.CENTER, 'OR')
	ConsolePrint(scen_info_con, 1, 31, '2) Destroy all enemy units')
	
	ConsolePrintEx(scen_info_con, 14, 40, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Light Armour')
	ConsolePrintEx(scen_info_con, 14, 41, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Infantry')
	
	# display to screen
	libtcod.console_blit(scen_info_con, 0, 0, 0, 0, 0, 31, 3)
	
	Wait(15)
	
	# get input from player
	exit_menu = False
	result = ''
	while not exit_menu:
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			key, mouse)
		if libtcod.console_is_window_closed(): sys.exit()
		
		if key is None: continue
		
		# cancel scenario start
		if key.vk == libtcod.KEY_ESCAPE:
			result = False
			exit_menu = True
		
		# confirm and continue
		elif key.vk == libtcod.KEY_ENTER:
			result = True
			exit_menu = True
	
	# replace original screen if canceling
	if not result:
		libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		Wait(15)
	del temp_con
	del scen_info_con
	return result


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


# draw info about a series of crew positions and their crewmen to a console
def DisplayCrew(unit, console, x, y, highlight_selected):
	
	for position in unit.crew_positions:
		
		# highlight selected position and crewman
		if highlight_selected:
			if unit.crew_positions.index(position) == scenario.selected_position:
				libtcod.console_set_default_background(console, libtcod.darker_blue)
				libtcod.console_rect(console, x, y, 24, 4, True, libtcod.BKGND_SET)
				libtcod.console_set_default_background(console, libtcod.black)
		
		libtcod.console_set_default_foreground(console, libtcod.light_blue)
		ConsolePrint(console, x, y, position.name)
		libtcod.console_set_default_foreground(console, libtcod.white)
		ConsolePrintEx(console, x+23, y, libtcod.BKGND_NONE, 
			libtcod.RIGHT, position.location)
		if not position.hatch:
			text = '--'
		else:
			if position.hatch_open:
				text = 'Open'
			else:
				text = 'Shut'
		ConsolePrintEx(console, x+23, y+1, libtcod.BKGND_NONE, 
			libtcod.RIGHT, text)
		
		if position.crewman is None:
			text = 'Empty'
		else:
			text = position.crewman.first_name[0] + '. ' + position.crewman.last_name
		
		# names might have special characters so we encode it before printing it
		ConsolePrint(console, x, y+1, text.encode('IBM850'))
		
		# crewman info if any
		if position.crewman is not None:
			
			# current action
			if position.crewman.current_action is not None:
				libtcod.console_set_default_foreground(console,
					libtcod.dark_yellow)
				ConsolePrint(console, x, y+2,
					position.crewman.current_action)
				
			
			# status
			libtcod.console_set_default_foreground(console, libtcod.grey)
			ConsolePrint(console, x, y+3, position.crewman.status)
			
		libtcod.console_set_default_foreground(console, libtcod.white)
		y += 5


# display info about a crewman to a console
def DisplayCrewInfo(crewman, console, x, y):
	
	# outline and section dividers
	libtcod.console_set_default_foreground(console, libtcod.grey)
	DrawFrame(console, x, y, 31, 41)
	libtcod.console_hline(console, x+1, y+4, 29)
	libtcod.console_hline(console, x+1, y+6, 29)
	libtcod.console_hline(console, x+1, y+8, 29)
	libtcod.console_hline(console, x+1, y+10, 29)
	libtcod.console_hline(console, x+1, y+14, 29)
	libtcod.console_hline(console, x+1, y+23, 29)
	
	# section titles
	libtcod.console_set_default_foreground(console, libtcod.lighter_blue)
	ConsolePrint(console, x+1, y+2, 'Crewman Report')
	ConsolePrint(console, x+1, y+5, 'Name')
	ConsolePrint(console, x+1, y+7, 'Age')
	ConsolePrint(console, x+1, y+9, 'Rank')
	ConsolePrint(console, x+1, y+11, 'Current')
	ConsolePrint(console, x+1, y+12, 'Position')
	ConsolePrint(console, x+1, y+15, 'Assessment')
	
	# info
	libtcod.console_set_default_foreground(console, libtcod.white)
	ConsolePrint(console, x+10, y+5, crewman.GetFullName().encode('IBM850'))
	ConsolePrint(console, x+10, y+7, str(crewman.age))
	ConsolePrint(console, x+10, y+9, crewman.rank_desc)
	ConsolePrint(console, x+10, y+11, scenario.player_unit.unit_id)
	ConsolePrint(console, x+10, y+12, crewman.current_position.name)
	
	# crew stats
	libtcod.console_set_default_background(console, libtcod.darkest_grey)
	background_shade = False
	i = 0
	for stat_name in STAT_NAMES:
		libtcod.console_set_default_foreground(console, libtcod.white)
		ConsolePrint(console, x+8, y+17+i, stat_name)
		libtcod.console_set_default_foreground(console, libtcod.light_grey)
		ConsolePrintEx(console, x+23, y+17+i, libtcod.BKGND_NONE, 
			libtcod.RIGHT, str(crewman.stats[stat_name]))
		if background_shade:
			libtcod.console_rect(console, x+8, y+17+i, 16, 1, False, libtcod.BKGND_SET)
		background_shade = not background_shade
		i+=1
	
	# morale level
	ConsolePrint(console, x+1, y+22, crewman.morale_desc)
	
	libtcod.console_set_default_foreground(console, libtcod.white)
	libtcod.console_set_default_background(console, libtcod.black)
		

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
		event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS,
			key, mouse)
		if session.key_down:
			if event != libtcod.EVENT_KEY_RELEASE:
				continue
			session.key_down = False
		if event != libtcod.EVENT_KEY_PRESS:
			continue
		
		session.key_down = True
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
	for elevation in range(4):
		for (hx, hy) in VP_HEXES:
			(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
			if (map_hx, map_hy) not in scenario.cd_hex.map_hexes:
				continue
			map_hex = scenario.cd_hex.map_hexes[(map_hx, map_hy)]
			
			if map_hex.elevation != elevation: continue
			(x,y) = PlotHex(hx, hy)
			
			libtcod.console_blit(session.hex_consoles[map_hex.terrain_type][map_hex.elevation],
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
	
	# draw roads
	for (hx, hy) in VP_HEXES:
		(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
		if (map_hx, map_hy) not in scenario.cd_hex.map_hexes:
			continue
		map_hex = scenario.cd_hex.map_hexes[(map_hx, map_hy)]
		# no road here
		if len(map_hex.dirt_roads) == 0: continue
		for direction in map_hex.dirt_roads:
			
			# get other VP hex linked by road
			(hx2, hy2) = GetAdjacentHex(hx, hy, ConstrainDir(direction - scenario.player_unit.facing))
			
			# only draw if it is in direction 0-2, unless the other hex is off the VP
			if (hx2, hy2) in VP_HEXES and 3 <= direction <= 5: continue
			
			# paint road
			(x1, y1) = PlotHex(hx, hy)
			(hx2, hy2) = GetAdjacentHex(hx, hy, ConstrainDir(direction - scenario.player_unit.facing))
			(x2, y2) = PlotHex(hx2, hy2)
			line = GetLine(x1, y1, x2, y2)
			for (x, y) in line:
				
				# don't paint over outside of map area
				if libtcod.console_get_char_background(map_vp_con, x, y) == libtcod.black:
					continue
				
				libtcod.console_set_char_background(map_vp_con, x, y,
					DIRT_ROAD_COL, libtcod.BKGND_SET)
				
				# if character is not blank or hex edge, remove it
				if libtcod.console_get_char(map_vp_con, x, y) not in [0, 250]:
					libtcod.console_set_char(map_vp_con, x, y, 0)
			
	# highlight objective hexes
	for (hx, hy) in VP_HEXES:
		(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
		if (map_hx, map_hy) not in scenario.cd_hex.map_hexes: continue
		map_hex = scenario.cd_hex.map_hexes[(map_hx, map_hy)]
		if map_hex.objective is not None:
			(x,y) = PlotHex(hx, hy)
			libtcod.console_blit(hex_objective_neutral, 0, 0, 0, 0,
				map_vp_con, x-3, y-2, 1.0, 0.0)
			

# display units on the unit console
# also displays map hex highlight and LoS if any
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
	
		# check for hex highlight if any
		if scenario.highlighted_hex is not None:
			if scenario.highlighted_hex == (map_hx, map_hy):
				(x,y) = PlotHex(vp_hx, vp_hy)
				libtcod.console_blit(hex_highlight, 0, 0, 0, 0, unit_con, 
					x-3, y-2)
		
	# display LoS if applicable
	if scenario.player_los_active and scenario.player_target is not None:
		line = GetLine(scenario.player_unit.screen_x, scenario.player_unit.screen_y,
			scenario.player_target.screen_x, scenario.player_target.screen_y)
		for (x,y) in line[2:-1]:
			libtcod.console_put_char_ex(unit_con, x, y, 250, libtcod.red,
				libtcod.black)


# display information about the player unit
def UpdatePlayerInfoCon():
	libtcod.console_clear(player_info_con)
	scenario.player_unit.DisplayMyInfo(player_info_con, 0, 0)


# list player unit crew positions and current crewmen if any
def UpdateCrewPositionCon():
	libtcod.console_clear(crew_position_con)
	
	if len(scenario.player_unit.crew_positions) == 0: return
	
	highlight_selected = False
	# crew action menu active
	if scenario.active_menu == 2:
		highlight_selected = True
	
	DisplayCrew(scenario.player_unit, crew_position_con, 0, 1, highlight_selected)


# list current player commands
def UpdateCommandCon():
	libtcod.console_set_default_foreground(command_con, libtcod.white)
	libtcod.console_set_default_background(command_con, libtcod.black)
	libtcod.console_clear(command_con)
	
	# no menu if enemy is active
	if scenario.game_turn['active_player'] == 1:
		return
	
	# draw menu title based on active menu
	x = 0
	for (text, num, col) in MENU_LIST:
		libtcod.console_set_default_background(command_con, col)
		libtcod.console_rect(command_con, x, 0, 2, 1, True, libtcod.BKGND_SET)
		
		# TEMP - no command options yet
		if num == 1:
			libtcod.console_set_default_foreground(command_con, libtcod.dark_grey)
		# menu number
		ConsolePrint(command_con, x, 0, str(num))
		libtcod.console_set_default_foreground(command_con, libtcod.white)
		
		x += 2
		
		# display menu text if active
		if scenario.active_menu == num:
			libtcod.console_rect(command_con, x, 0, len(text)+2, 1, True, libtcod.BKGND_SET)
			ConsolePrint(command_con, x, 0, text)
			x += len(text) + 2
	
	# fill in rest of menu line with final colour
	libtcod.console_rect(command_con, x, 0, 24-x, 1, True, libtcod.BKGND_SET)
	
	libtcod.console_set_default_background(command_con, libtcod.black)
	
	# crew action menu
	if scenario.active_menu == 2:
		
		libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
		
		ConsolePrint(command_con, 2, 2, EncodeKey('w').upper() + '/' + EncodeKey('s').upper())
		ConsolePrint(command_con, 2, 3, EncodeKey('a').upper() + '/' + EncodeKey('d').upper())
		ConsolePrint(command_con, 2, 4, 'H')
		
		libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
		ConsolePrint(command_con, 9, 2, 'Select Crew')
		ConsolePrint(command_con, 9, 3, 'Set Action')
		ConsolePrint(command_con, 9, 4, 'Toggle Hatch')
	
	# movement
	elif scenario.active_menu == 3:
		
		libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
		ConsolePrint(command_con, 2, 2, EncodeKey('w').upper())
		ConsolePrint(command_con, 2, 3, EncodeKey('a').upper() + '/' + EncodeKey('d').upper())
		
		libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
		ConsolePrint(command_con, 9, 2, 'Move Forward')
		ConsolePrint(command_con, 9, 3, 'Pivot Hull')
		
	# combat
	elif scenario.active_menu == 4:
		
		libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
		ConsolePrint(command_con, 2, 2, EncodeKey('w').upper() + '/' + EncodeKey('s').upper())
		ConsolePrint(command_con, 2, 3, EncodeKey('q').upper() + '/' + EncodeKey('e').upper())
		ConsolePrint(command_con, 2, 4, EncodeKey('a').upper() + '/' + EncodeKey('d').upper())
		ConsolePrint(command_con, 2, 5, EncodeKey('z').upper() + '/' + EncodeKey('c').upper())
		ConsolePrint(command_con, 2, 6, 'F')
		
		libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
		ConsolePrint(command_con, 9, 2, 'Select Weapon')
		ConsolePrint(command_con, 9, 3, 'Rotate Turret')
		ConsolePrint(command_con, 9, 4, 'Select Target')
		ConsolePrint(command_con, 9, 5, 'Select Ammo')
		ConsolePrint(command_con, 9, 6, 'Fire')
		
	libtcod.console_set_default_foreground(command_con, ACTION_KEY_COL)
	ConsolePrint(command_con, 2, 10, 'Enter')
	libtcod.console_set_default_foreground(command_con, libtcod.lighter_grey)
	ConsolePrint(command_con, 9, 10, 'End Turn')
	
	
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
	
	# TEMP - don't display hex coordinate in production version?
	ConsolePrint(hex_terrain_con, 0, 1, str(hx) + ',' + str(hy))
	
	# elevation
	text = str(map_hex.elevation * ELEVATION_M) + ' m.'
	ConsolePrintEx(hex_terrain_con, 15, 1, libtcod.BKGND_NONE,
		libtcod.RIGHT, text)
	
	if map_hex.objective is not None:
		libtcod.console_set_default_foreground(hex_terrain_con, libtcod.light_blue)
		ConsolePrint(hex_terrain_con, 0, 2, 'Objective')
		if map_hex.objective == -1:
			return
		if map_hex.objective == 0:
			text = 'Player Held'
		else:
			text = 'Enemy Held'
		libtcod.console_set_default_foreground(hex_terrain_con, libtcod.white)
		ConsolePrint(hex_terrain_con, 0, 3, text)
	
	if len(map_hex.dirt_roads) > 0:
		ConsolePrint(hex_terrain_con, 0, 9, 'Dirt Road')


# draw information based on current turn phase to contextual info console
def UpdateContextCon():
	libtcod.console_clear(context_con)
	libtcod.console_set_default_foreground(context_con, libtcod.white)
	
	# no menu active
	if scenario.active_menu == 0:
		return
	
	# crew actions
	elif scenario.active_menu == 2:
		position = scenario.player_unit.crew_positions[scenario.selected_position]
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
				if y == 9: break
	
	# movement
	elif scenario.active_menu == 3:
		
		libtcod.console_set_default_background(context_con, libtcod.darker_green)
		libtcod.console_rect(context_con, 0, 0, 16, 1, True, libtcod.BKGND_SET)
		ConsolePrint(context_con, 0, 0, 'Movement')
		libtcod.console_set_default_background(context_con, libtcod.black)
		
		libtcod.console_set_default_foreground(context_con, libtcod.light_green)
		if scenario.player_unit.move_finished:
			ConsolePrint(context_con, 0, 2, 'Move finished')
			return
		if scenario.player_unit.fired:
			ConsolePrint(context_con, 0, 2, 'Already Fired')
			return
		
		# display chance of getting a bonus move
		(hx, hy) = GetAdjacentHex(scenario.player_unit.hx, scenario.player_unit.hy,
			scenario.player_unit.facing)
		
		# off map
		if (hx, hy) not in scenario.cd_hex.map_hexes: return
		
		# display destination terrain type
		text = HEX_TERRAIN_DESC[scenario.cd_hex.map_hexes[(hx, hy)].terrain_type]
		ConsolePrint(context_con, 0, 2, text)
		
		libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
		
		# display road status if any
		if scenario.player_unit.facing in scenario.cd_hex.map_hexes[(scenario.player_unit.hx, scenario.player_unit.hy)].dirt_roads:
			ConsolePrint(context_con, 0, 3, 'Dirt Road')
		
		# get bonus move chance
		ConsolePrint(context_con, 0, 4, '+1 move chance:')
		chance = round(scenario.CalcBonusMove(scenario.player_unit, hx, hy), 2)
		ConsolePrint(context_con, 1, 5, str(chance) + '%%')
	
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



# display information about an on-map unit under the mouse cursor, 16x10
def UpdateUnitInfoCon():
	libtcod.console_clear(unit_info_con)
	
	# mouse cursor outside of map area
	if mouse.cx < 32: return
	x = mouse.cx - 31
	y = mouse.cy - 4
	if (x,y) not in scenario.hex_map_index: return
	
	(hx, hy) = scenario.hex_map_index[(x,y)]
	
	unit_stack = scenario.cd_hex.map_hexes[(hx, hy)].unit_stack
	if len(unit_stack) == 0: return
	
	# display unit info
	unit = unit_stack[0]
	
	if unit.owning_player == 1 and not unit.known:
		libtcod.console_set_default_foreground(unit_info_con, UNKNOWN_UNIT_COL)
		ConsolePrint(unit_info_con, 0, 0, 'Possible Enemy')
	else:
		if unit.owning_player == 0:
			col = libtcod.white
		else:
			col = ENEMY_UNIT_COL

		libtcod.console_set_default_foreground(unit_info_con, col)
		lines = wrap(unit.unit_id, 16)
		y = 0
		for line in lines[:2]:
			ConsolePrint(unit_info_con, 0, y, line)
			y+=1
		libtcod.console_set_default_foreground(unit_info_con, libtcod.light_grey)
		ConsolePrint(unit_info_con, 0, 2, unit.GetStat('class'))
		
		libtcod.console_set_default_foreground(unit_info_con, libtcod.white)
		if scenario.player_unit.acquired_target is not None:
			(target, level) = scenario.player_unit.acquired_target 
			if target == unit:
				text = 'Acquired target'
				if level:
					text += '+'
				ConsolePrint(unit_info_con, 0, 4, text)
		
		# active status
		libtcod.console_set_default_foreground(unit_info_con, libtcod.light_red)
		text = ''
		if unit.broken:
			text = 'Broken'
		elif unit.pinned:
			text = 'Pinned'
		ConsolePrint(unit_info_con, 0, 5, text)
	
	# other units in stack if any
	if len(unit_stack) > 1:
		libtcod.console_set_default_foreground(unit_info_con, libtcod.light_grey)
		text = '+' + str(len(unit_stack)-1) + ' other units'
		ConsolePrint(unit_info_con, 0, 8, text)


# update objective info console, 16x10
def UpdateObjectiveInfoCon():
	libtcod.console_clear(objective_con)
	libtcod.console_set_default_foreground(objective_con, libtcod.light_blue)
	ConsolePrintEx(objective_con, 15, 0, libtcod.BKGND_NONE, libtcod.RIGHT, 'Objectives')
	libtcod.console_set_default_foreground(objective_con, libtcod.light_grey)
	
	y = 2
	for map_hex in scenario.map_objectives:
		distance = GetHexDistance(scenario.player_unit.hx, scenario.player_unit.hy,
			map_hex.hx, map_hex.hy) * 160
		if distance > 1000:
			text = str(float(distance) / 1000.0) + ' km.'
		else:
			text = str(distance) + ' m.'
		ConsolePrintEx(objective_con, 13, y, libtcod.BKGND_NONE, libtcod.RIGHT, text)
		
		# capture status
		if map_hex.objective == 0:
			char = 251
		else:
			char = 120
		libtcod.console_put_char(objective_con, 0, y, char)
		
		# directional arrow if required
		if distance > 0:
			direction = GetDirectionToward(scenario.player_unit.hx, scenario.player_unit.hy,
				map_hex.hx, map_hex.hy)
			direction = ConstrainDir(direction + (0 - scenario.player_unit.facing))
			libtcod.console_put_char(objective_con, 15, y, GetDirectionalArrow(direction))
		y += 1
	

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
	
	# TEMP - draw current time and weather conditions directly to console
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
	global attack_con, fov_con, hex_fov, popup_bkg, hex_objective_neutral
	global hex_highlight
	global tile_offmap
	
	# set up consoles
	
	# background outline console for left column
	bkg_console = LoadXP('bkg.xp')
	# black mask for map tiles not visible to player
	hex_fov = LoadXP('hex_fov.xp')
	libtcod.console_set_key_color(hex_fov, libtcod.black)
	# background for scenario message window
	popup_bkg = LoadXP('popup_bkg.xp')
	
	# highlight for objective hexes
	hex_objective_neutral = LoadXP('hex_objective_neutral.xp')
	libtcod.console_set_key_color(hex_objective_neutral, KEY_COLOR)
	
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
	
	# create a global pointer - TEMP
	global scenario
	scenario = campaign_day.scenario
	
	# init scenario if not already; only called when started a new one, not when loading from saved
	if not scenario.init_complete:
		
		# display scenario info, allow player to cancel start
		#if not DisplayScenInfo(): return
		
		# generate hex map if needed
		if scenario.cd_hex.map_hexes == {}:
			scenario.cd_hex.GenerateHexMap()
		
		# generate scenario units
		
		# spawn player tank into scenario
		unit = campaign.player_unit
		
		# spawn into map: 2 hexes up from bottom corner, and set facings
		unit.SpawnAt(0, scenario.cd_hex.map_radius - 2)
		unit.facing = 0
		unit.turret_facing = 0	
		scenario.units.append(unit)
		scenario.player_unit = unit
		unit.CalcFoV()
		
		# set up VP hexes and generate initial VP console
		scenario.CenterVPOnPlayer()
		scenario.SetVPHexes()
		
		# set up map objectives for this scenario
		for i in range(3):
			for tries in range(300):
				(hx, hy) = choice(scenario.cd_hex.map_hexes.keys())
				# already an objective
				if scenario.cd_hex.map_hexes[(hx, hy)].objective is not None:
					continue
				if scenario.cd_hex.map_hexes[(hx, hy)].terrain_type == 'pond':
					continue
				if GetHexDistance(hx, hy, scenario.player_unit.hx, scenario.player_unit.hy) < 5:
					continue
				
				# too close to an existing objective
				too_close = False
				for map_hex in scenario.map_objectives:
					if GetHexDistance(hx, hy, map_hex.hx, map_hex.hy) < 6:
						too_close = True
						break
				if too_close: continue
				
				# too close to map edge
				hex_ring = GetHexRing(hx, hy, 1)
				for (hx2, hy2) in hex_ring:
					if (hx2, hy2) not in scenario.cd_hex.map_hexes:
						too_close = True
						break
				if too_close: continue
				
				scenario.SetObjectiveHex(hx, hy, 1)
				break
		
		# generate and spawn initial enemy units for this scenario
		scenario.SpawnEnemyUnits()
		
		# set activation order
		scenario.GenerateActivationOrder()
		
		# activate player unit
		scenario.active_unit = scenario.player_unit
		scenario.active_unit.DoPreActivation()
		
		scenario.init_complete = True
		
		SaveGame()
	
	# generate consoles for first time
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
			EraseGame()
			# FUTURE: add more descriptive detail here
			text = 'The scenario is over: ' + scenario.win_desc
			ShowNotification(text)
			exit_scenario = True
			continue
		
		# if player is not active, do AI actions
		if scenario.game_turn['active_player'] == 1:
			UpdateCommandCon()
			for unit in scenario.activation_list[1]:
				if not unit.alive: continue
				unit.ai.DoActivation()
			# pause a short time between enemy unit activations
			Wait(5)
			scenario.DoEndOfPlayerTurn()
			
			# activate player
			scenario.active_unit = scenario.player_unit
			scenario.active_unit.DoPreActivation()
			
			UpdatePlayerInfoCon()
			UpdateContextCon()
			UpdateObjectiveInfoCon()
			UpdateCrewPositionCon()
			UpdateCommandCon()
			UpdateScenarioDisplay()
			continue
		
		# get keyboard and/or mouse event
		event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			key, mouse)
		
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
						map_hex.unit_stack.insert(-1, map_hex.unit_stack.pop(0))
					else:
						map_hex.unit_stack.insert(0, map_hex.unit_stack.pop(-1))
					UpdateUnitCon()
					UpdateUnitInfoCon()
					UpdateScenarioDisplay()
			continue
		
		##### Player Keyboard Commands #####
		
		# if a key was previously pressed, wait for it to be released
		if session.key_down:
			if event != libtcod.EVENT_KEY_RELEASE:
				continue
			# key was released
			session.key_down = False
		
		# check for keypress, continue if none
		if event != libtcod.EVENT_KEY_PRESS:
			continue
		
		# set key pressed flag
		session.key_down = True
		
		# Determine action based on key pressed
		
		# enter game menu
		if key.vk in [libtcod.KEY_ESCAPE, libtcod.KEY_F3]:
			if key.vk == libtcod.KEY_ESCAPE:
				menu_tab = 0
			else:
				menu_tab = 3
			result = ShowGameMenu(menu_tab)
			if result == 'exit_game':
				exit_scenario = True
			else:
				# re-draw to clear game menu from screen
				libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
				UpdateScenarioDisplay()
			continue
		
		# end player unit activation
		if key.vk == libtcod.KEY_ENTER:
			scenario.player_unit.DoPostActivation()
			
			# FUTURE: check for allied player units to activate
			
			scenario.DoEndOfPlayerTurn()
			continue

		# key commands
		key_char = chr(key.c).lower()
		
		# switch active menu (same for all keyboard layouts?)
		if key_char in ['2', '3', '4']:
			if scenario.active_menu != int(key_char):
				scenario.active_menu = int(key_char)
				UpdateCommandCon()
				UpdateContextCon()
				UpdateCrewPositionCon()
				UpdateScenarioDisplay()
			continue
		
		# map key to current keyboard layout
		key_char = DecodeKey(key_char)
		
		# crew actions
		if scenario.active_menu == 2:
			
			# change selected crewman
			if key_char in ['w', 's'] or key.vk in [libtcod.KEY_UP, libtcod.KEY_DOWN]:
			
				if key_char == 'w' or key.vk == libtcod.KEY_UP:
					if scenario.selected_position > 0:
						scenario.selected_position -= 1
					else:
						scenario.selected_position = len(scenario.player_unit.crew_positions) - 1
				
				else:
					if scenario.selected_position == len(scenario.player_unit.crew_positions) - 1:
						scenario.selected_position = 0
					else:
						scenario.selected_position += 1
				UpdateContextCon()
				UpdateCrewPositionCon()
				UpdateScenarioDisplay()
			
			# set action for selected crewman
			elif key_char in ['a', 'd'] or key.vk in [libtcod.KEY_LEFT, libtcod.KEY_RIGHT]:
				
				position = scenario.player_unit.crew_positions[scenario.selected_position]
				
				# check for empty position
				if position.crewman is not None:
					if key_char == 'a' or key.vk == libtcod.KEY_LEFT:
						result = position.crewman.SetAction(False)
					else:
						result = position.crewman.SetAction(True)
					if result:
						UpdateContextCon()
						UpdateCrewPositionCon()
						scenario.player_unit.CalcFoV()
						UpdateVPCon()
						UpdateScenarioDisplay()
			
			# toggle hatch for this position
			elif key_char == 'h':
				
				position = scenario.player_unit.crew_positions[scenario.selected_position]
				if position.crewman is not None:
					if position.ToggleHatch():
						UpdateCrewPositionCon()
						scenario.player_unit.CalcFoV()
						UpdateVPCon()
						UpdateScenarioDisplay()
		
		# movement
		elif scenario.active_menu == 3:
		
			# move player unit forward
			if key_char == 'w' or key.vk == libtcod.KEY_UP:
				
				if scenario.player_unit.MoveForward():
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
			elif key_char in ['a', 'd'] or key.vk in [libtcod.KEY_LEFT, libtcod.KEY_RIGHT]:
				
				if key_char == 'a' or key.vk == libtcod.KEY_LEFT:
					result = scenario.player_unit.Pivot(False)
				else:
					result = scenario.player_unit.Pivot(True)
				if result:
					scenario.CenterVPOnPlayer()
					scenario.SetVPHexes()
					UpdateContextCon()
					UpdateVPCon()
					UpdateUnitCon()
					UpdateObjectiveInfoCon()
					UpdateHexTerrainCon()
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
			elif key_char == 'f':
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

print 'Starting ' + NAME + ' version ' + VERSION	# startup message

# try to load game settings from config file, will create a new file if none present
LoadCFG()

os.putenv('SDL_VIDEO_CENTERED', '1')			# center game window on screen

# determine font to use based on settings file
if config.getboolean('ArmCom2', 'large_display_font'):
	fontname = 'c64_16x16.png'
else:
	fontname = 'c64_8x8.png'
# set up custom font for libtcod
libtcod.console_set_custom_font(DATAPATH+fontname, libtcod.FONT_LAYOUT_ASCII_INROW,
	0, 0)

# set up root console
libtcod.console_init_root(WINDOW_WIDTH, WINDOW_HEIGHT, NAME + ' - ' + VERSION,
	fullscreen = False, renderer = libtcod.RENDERER_GLSL)
libtcod.sys_set_fps(LIMIT_FPS)
libtcod.console_set_default_background(0, libtcod.black)
libtcod.console_set_default_foreground(0, libtcod.white)
libtcod.console_clear(0)

# display loading screen
ConsolePrintEx(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER,
	'Loading...')
libtcod.console_flush()

# create new session object
session = Session()

# try to init sound mixer and load sounds if successful
main_theme = None

if config.getboolean('ArmCom2', 'sounds_enabled'):
	if session.InitMixer():
		session.LoadSounds()
		# start main menu theme
		main_theme = mixer.Mix_PlayChannel(-1, mixer.Mix_LoadWAV(SOUNDPATH + 'armcom2_theme.ogg'), -1)
	else:
		config.set('ArmCom2', 'sounds_enabled', 'false')
		print 'Not able to init mixer, sounds disabled'

# generate keyboard mapping dictionaries
GenerateKeyboards()

# set up double buffer console
con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(con, libtcod.black)
libtcod.console_set_default_foreground(con, libtcod.white)
libtcod.console_clear(con)

# darken screen console
darken_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(darken_con, libtcod.black)
libtcod.console_set_default_foreground(darken_con, libtcod.black)
libtcod.console_clear(darken_con)

# game menu console: 84x54
game_menu_bkg = LoadXP('game_menu.xp')
game_menu_con = libtcod.console_new(84, 54)
libtcod.console_set_default_background(game_menu_con, libtcod.black)
libtcod.console_set_default_foreground(game_menu_con, libtcod.white)
libtcod.console_clear(game_menu_con)

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()

# for a unit in 0,0 facing direction 0, the location of map hexes in each sextant, up to range 6
# used for checking field of view for the player, covered arcs for weapons, etc.
HEXTANTS = []
for direction in range(6):
	hex_list = [
		(0,-1),								# range 1
		(1,-2), (0,-2), (-1,-1),					# range 2
		(1,-3), (0,-3), (-1,-2),					# range 3
		(2,-4), (1,-4), (0,-4), (-1,-3), (-2,-2),			# range 4
		(2,-5), (1,-5), (0,-5), (-1,-4), (-2,-3),			# range 5
		(3,-6), (2,-6), (1,-6), (0,-6), (-1,-5), (-2,-4), (-3,-3)	# range 6
	]
	if direction != 0:
		for i, (hx, hy) in enumerate(hex_list):
			hex_list[i] = RotateHex(hx, hy, direction)
	HEXTANTS.append(hex_list)




##########################################################################################
#                                        Main Menu                                       #
##########################################################################################

global main_title, tank_image
global campaign, campaign_day

main_title = LoadXP('main_title.xp')

# list of unit images to display on main menu
TANK_IMAGES = ['unit_7TP.xp', 'unit_TK3.xp', 'unit_TKS.xp', 'unit_TKS_20mm.xp', 'unit_vickers_ejw.xp',
	'unit_pz_38t_a.xp']
tank_image = LoadXP(choice(TANK_IMAGES))

# gradient animated effect for main menu
GRADIENT = [
	libtcod.Color(51, 51, 51), libtcod.Color(64, 64, 64), libtcod.Color(128, 128, 128),
	libtcod.Color(192, 192, 192), libtcod.Color(255, 255, 255), libtcod.Color(192, 192, 192),
	libtcod.Color(128, 128, 128), libtcod.Color(64, 64, 64), libtcod.Color(51, 51, 51),
	libtcod.Color(51, 51, 51)
]

# set up gradient animation timing
time_click = time.time()
gradient_x = WINDOW_WIDTH + 20


# draw the main menu to the main menu console
# if options_menu_active, draw the options menu instead
def UpdateMainMenuCon(options_menu_active):
	
	# display game title
	libtcod.console_blit(main_title, 0, 0, 0, 0, main_menu_con, 0, 0)
	
	# randomly display a tank image to use for this session
	libtcod.console_blit(tank_image, 0, 0, 0, 0, main_menu_con, 7, 6)
	
	# display version number and program info
	libtcod.console_set_default_foreground(main_menu_con, libtcod.red)
	ConsolePrintEx(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-8, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Development Build: Has bugs and incomplete features')
	
	libtcod.console_set_default_foreground(main_menu_con, libtcod.light_grey)
	ConsolePrintEx(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-6, libtcod.BKGND_NONE,
		libtcod.CENTER, VERSION)
	ConsolePrintEx(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-4,
		libtcod.BKGND_NONE, libtcod.CENTER, 'Copyright 2018')
	ConsolePrintEx(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-3,
		libtcod.BKGND_NONE, libtcod.CENTER, 'Free Software under the GNU GPL')
	ConsolePrintEx(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-2,
		libtcod.BKGND_NONE, libtcod.CENTER, 'www.armouredcommander.com')
	
	y = 38
	
	# display menu options
	if options_menu_active:
		OPTIONS = [('F', 'Font Size'), ('S', 'Sound Effects'), ('K', 'Keyboard'), ('Esc', 'Return to Main Menu')]
		for (char, text) in OPTIONS:
			
			# extra spacing
			if char == 'Esc': y += 1
			
			libtcod.console_set_default_foreground(main_menu_con, ACTION_KEY_COL)
			ConsolePrint(main_menu_con, WINDOW_XM-10, y, char)
			
			libtcod.console_set_default_foreground(main_menu_con, libtcod.lighter_grey)
			ConsolePrint(main_menu_con, WINDOW_XM-6, y, text)
			
			# current option settings
			libtcod.console_set_default_foreground(main_menu_con, libtcod.light_blue)
			
			# toggle font size
			if char == 'F':
				if config.getboolean('ArmCom2', 'large_display_font'):
					text = '16x16'
				else:
					text = '8x8'
				ConsolePrint(main_menu_con, WINDOW_XM+8, y, text)
			
			# sound effects
			elif char == 'S':
				if config.getboolean('ArmCom2', 'sounds_enabled'):
					text = 'ON'
				else:
					text = 'OFF'
				ConsolePrint(main_menu_con, WINDOW_XM+8, y, text)
			
			# keyboard settings
			elif char == 'K':
				ConsolePrint(main_menu_con, WINDOW_XM+8, y, KEYBOARDS[config.getint('ArmCom2', 'keyboard')])
			
			y += 1
	else:
		OPTIONS = [('C', 'Continue'), ('N', 'New Campaign'), ('O', 'Options'), ('Q', 'Quit')]
		for (char, text) in OPTIONS:
			# grey-out continue game option if no saved game present
			disabled = False
			if char == 'C' and not os.path.exists('savegame'):
				disabled = True
			
			if disabled:
				libtcod.console_set_default_foreground(main_menu_con, libtcod.dark_grey)
			else:
				libtcod.console_set_default_foreground(main_menu_con, ACTION_KEY_COL)
			ConsolePrint(main_menu_con, WINDOW_XM-5, y, char)
			
			if disabled:
				libtcod.console_set_default_foreground(main_menu_con, libtcod.dark_grey)
			else:
				libtcod.console_set_default_foreground(main_menu_con, libtcod.lighter_grey)
			ConsolePrint(main_menu_con, WINDOW_XM-3, y, text)	
			
			y += 1


# update the animation effect
def AnimateMainMenu():
	
	global gradient_x
	
	for x in range(0, 10):
		if x + gradient_x > WINDOW_WIDTH: continue
		for y in range(19, 34):
			char = libtcod.console_get_char(main_menu_con, x + gradient_x, y)
			fg = libtcod.console_get_char_foreground(main_menu_con, x + gradient_x, y)
			if char != 0 and fg != GRADIENT[x]:
				libtcod.console_set_char_foreground(main_menu_con, x + gradient_x,
					y, GRADIENT[x])
	gradient_x -= 2
	if gradient_x <= 0: gradient_x = WINDOW_WIDTH + 20


# generate main menu console
global main_menu_con
main_menu_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(main_menu_con, libtcod.black)
libtcod.console_set_default_foreground(main_menu_con, libtcod.white)
libtcod.console_clear(main_menu_con)

# use root menu to start
options_menu_active = False

# draw the main menu console for the first time
UpdateMainMenuCon(options_menu_active)
libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)

# Main Menu loop
exit_game = False

while not exit_game:
	
	# emergency exit in case of endless loop
	if libtcod.console_is_window_closed(): sys.exit()
	
	# trigger animation and update screen
	if time.time() - time_click >= 0.08:
		AnimateMainMenu()
		libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)
		time_click = time.time()
	
	libtcod.console_flush()
	
	# get keyboard event
	event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS,
		key, mouse) 
	
	# if a key was previously pressed, wait for it to be released
	if session.key_down:
		if event != libtcod.EVENT_KEY_RELEASE:
			continue
		# key was released
		session.key_down = False
	
	# check for keypress, continue if none
	if event != libtcod.EVENT_KEY_PRESS:
		continue
	
	# set key pressed flag
	session.key_down = True
	
	key_char = chr(key.c).lower()
	
	# root main menu
	if not options_menu_active:
	
		if key_char == 'q':
			exit_game = True
			continue
		
		if key_char == 'o':
			options_menu_active = True
			UpdateMainMenuCon(options_menu_active)
			libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)
		
		# TODO: combine new campaign and continue campaign elif sections
		
		
		elif key_char == 'c':
			if not os.path.exists('savegame'):
				continue
			
			# check that saved game is correct version
			if not CheckSavedGameVersion():
				text = 'Saved game was saved with an older version of the program, cannot continue.'
				result = ShowNotification(text)
				libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)
				continue
			
			# pause main theme if playing
			if main_theme is not None:
				mixer.Mix_Pause(main_theme)
			
			libtcod.console_clear(0)
			ConsolePrintEx(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER,
				'Loading...')
			libtcod.console_flush()
			
			# load the game info and go into the campaign day loop
			LoadGame()
			campaign_day.CampaignDayLoop()
			
			# resume main theme if playing
			if main_theme is not None:
				mixer.Mix_Resume(main_theme)
			
			UpdateMainMenuCon(options_menu_active)
			libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)
		
		# start new campaign
		elif key_char == 'n':
			# check for overwrite of existing saved game
			if os.path.exists('savegame'):
				text = 'Starting a new campaign will PERMANTLY ERASE the existing saved campaign.'
				result = ShowNotification(text, confirm=True)
				# cancel and return to main menu
				if not result:
					libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)
					continue
			if main_theme is not None:
				mixer.Mix_Pause(main_theme)
			
			# create a new campaign object and select a campaign
			campaign = Campaign()
			result = campaign.CampaignSelectionMenu()
			if not result:
				del campaign
				libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)
				if main_theme is not None:
					mixer.Mix_Resume(main_theme)
				continue
			
			# show loading screen - there is a pause while terrain is generated
			libtcod.console_clear(0)
			ConsolePrintEx(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER,
				'Loading...')
			libtcod.console_flush()
			
			# generate a new campaign day object
			campaign_day = CampaignDay()
			
			# go to the campaign day loop
			campaign_day.CampaignDayLoop()
			
			# resume theme music if active
			if main_theme is not None:
				mixer.Mix_Resume(main_theme)
			UpdateMainMenuCon(options_menu_active)
			libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)
	
	# options menu
	else:
		# change an option
		if key_char in ['f', 's', 'k']:
		
			# switch font size
			if key_char == 'f':
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
					NAME + ' - ' + VERSION, fullscreen = False,
					renderer = libtcod.RENDERER_GLSL)
			
			# toggle sound effects on/off
			elif key_char == 's':
				if config.getboolean('ArmCom2', 'sounds_enabled'):
					config.set('ArmCom2', 'sounds_enabled', 'false')
				else:
					config.set('ArmCom2', 'sounds_enabled', 'true')
				
			# switch keyboard layout
			elif key_char == 'k':
				i = config.getint('ArmCom2', 'keyboard')
				if i == len(KEYBOARDS) - 1:
					i = 0
				else:
					i += 1
				config.set('ArmCom2', 'keyboard', i)
				GenerateKeyboards()

			SaveCFG()
			UpdateMainMenuCon(options_menu_active)
			libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)
		
		# exit options menu
		elif key.vk == libtcod.KEY_ESCAPE:
			options_menu_active = False
			UpdateMainMenuCon(options_menu_active)
			libtcod.console_blit(main_menu_con, 0, 0, 0, 0, 0, 0, 0)

# END #

