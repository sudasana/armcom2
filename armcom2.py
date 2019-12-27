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

if sys.platform == 'darwin':				# OSX
	import tcod as libtcod
elif os.name == 'posix':				# linux
	import libtcodpy_local as libtcod
else:							# windows
	import libtcodpy as libtcod
	os.environ['PYSDL2_DLL_PATH'] = os.getcwd() + '/lib'.replace('/', os.sep)	# set sdl2 dll path

from configparser import ConfigParser			# saving and loading configuration settings
from random import choice, shuffle, sample		# for the illusion of randomness
from math import floor, cos, sin, sqrt, degrees, atan2, ceil	# math and heading calculations
import xp_loader, gzip					# loading xp image files
import json						# for loading JSON data
import time
from datetime import datetime				# for timestamping logs
from textwrap import wrap				# breaking up strings
import shelve						# saving and loading games
import sdl2.sdlmixer as mixer				# sound effects
from calendar import monthrange				# for date calculations


##########################################################################################
#                                        Constants                                       #
##########################################################################################

DEBUG = False						# debug flag - set to False in all distribution versions
NAME = 'Armoured Commander II'				# game name
VERSION = '0.10.0 RC 1'					# game version
DATAPATH = 'data/'.replace('/', os.sep)			# path to data files
SOUNDPATH = 'sounds/'.replace('/', os.sep)		# path to sound samples
CAMPAIGNPATH = 'campaigns/'.replace('/', os.sep)	# path to campaign files

if sys.platform == 'darwin':
	RENDERER = libtcod.RENDERER_SDL2
elif os.name == 'posix':				# linux (and OS X?) has to use SDL for some reason
	RENDERER = libtcod.RENDERER_SDL
else:
	RENDERER = libtcod.RENDERER_GLSL

LIMIT_FPS = 50						# maximum screen refreshes per second
ANIM_UPDATE_TIMER = 0.15				# number of seconds between animation frame checks
WINDOW_WIDTH, WINDOW_HEIGHT = 90, 60			# size of game window in character cells
WINDOW_XM, WINDOW_YM = int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/2)	# center of game window
KEYBOARDS = ['QWERTY', 'AZERTY', 'QWERTZ', 'Dvorak', 'Custom']	# list of possible keyboard layout settings
MAX_TANK_NAME_LENGTH = 20				# maximum length of tank names
MAX_NICKNAME_LENGTH = 10				# " for crew nicknames

##### Hex geometry definitions #####

# directional and positional constants
DESTHEX = [(0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0)]	# change in hx, hy values for hexes in each direction
CD_DESTHEX = [(1,-1), (1,0), (0,1), (-1,1), (-1,0), (0,-1)]	# same for pointy-top
PLOT_DIR = [(0,-1), (1,-1), (1,1), (0,1), (-1,1), (-1,-1)]	# position of direction indicator
TURRET_CHAR = [254, 47, 92, 254, 47, 92]			# characters to use for turret display

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

# smaller hex outline for objective hex highlighting
CD_HEX_OBJECTIVE_CELLS = [
	(0,-3), (1,-2), (2,-1), (2,0), (2,1), (1,2), (0,3), (-1,2), (-2,1),
	(-2,0), (-2,-1), (-1,-2)
]

# list of hexes on campaign day map
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
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency
ACTION_KEY_COL = libtcod.Color(51, 153, 255)		# colour for key commands
HIGHLIGHT_MENU_COL = libtcod.Color(30, 70, 130)		# background highlight colour for selected menu option
TITLE_COL = libtcod.Color(102, 178, 255)		# menu titles
PORTRAIT_BG_COL = libtcod.Color(217, 108, 0)		# background color for unit portraits
UNKNOWN_UNIT_COL = libtcod.grey				# unknown enemy unit display colour
ENEMY_UNIT_COL = libtcod.Color(255, 20, 20)		# known "
ALLIED_UNIT_COL = libtcod.Color(120, 120, 255)		# allied unit display colour
GOLD_COL = libtcod.Color(255, 255, 100)			# golden colour for awards
DIRT_ROAD_COL = libtcod.Color(80, 50, 20)		# dirt roads on campaign day map
RIVER_COL = libtcod.Color(0, 0, 140)			# rivers "
BRIDGE_COL = libtcod.Color(40, 20, 10)			# bridges/fords "

# text names for months
MONTH_NAMES = [
	'', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
	'October', 'November', 'December'
]

# order of turn phases
PHASE_COMMAND = 0
PHASE_SPOTTING = 1
PHASE_CREW_ACTION = 2
PHASE_MOVEMENT = 3
PHASE_SHOOTING = 4
PHASE_CC = 5
PHASE_ALLIED_ACTION = 6
PHASE_ENEMY_ACTION = 7

# text names for scenario turn phases
SCEN_PHASE_NAMES = [
	'Command', 'Spotting', 'Crew Action', 'Movement', 'Shooting', 'Close Combat', 'Allied Action',
	'Enemy Action'
]

# colour associated with phases
SCEN_PHASE_COL = [
	libtcod.yellow, libtcod.purple, libtcod.light_blue, libtcod.green, libtcod.red, libtcod.white,
	ALLIED_UNIT_COL, ENEMY_UNIT_COL 
]

# list of campaign calendar menus and their highlight colours
CC_MENU_LIST = [
	('Proceed', 1, libtcod.Color(70, 140, 0)),
	('Crew and Tank', 2, libtcod.Color(140, 140, 0))
#	('Group', 3, libtcod.Color(180, 0, 45))
]

# list of campaign day menus and their highlight colours
CD_MENU_LIST = [
	('Support', 1, libtcod.Color(128, 128, 128)),
	('Crew', 2, libtcod.Color(140, 140, 0)),
	('Travel', 3, libtcod.Color(70, 140, 0)),
	('Group', 4, libtcod.Color(180, 0, 45)),
	('Main Gun', 5, libtcod.Color(128, 100, 64))
]

# directional arrows for directions on the campaign day map
CD_DIR_ARROW = [228,26,229,230,27,231]

# list of commands for travel in campaign day
CD_TRAVEL_CMDS = [
	('e',2,-2,228), ('d',2,0,26), ('c',2,2,229), ('z',-2,2,230), ('a',-2,0,27), ('q',-2,-2,231)
]

# order to display ammo types
AMMO_TYPES = ['HE', 'AP']

# list of MG-type weapons
MG_WEAPONS = ['Co-ax MG', 'Turret MG', 'Hull MG', 'AA MG', 'HMG']

# types of records to store for each combat day and for entire campaign
# also order in which they are displayed
RECORD_LIST = [
	'Battles Fought', 'Map Areas Captured', 'Map Areas Defended', 'Gun Hits', 'Vehicles Destroyed',
	'Guns Destroyed', 'Infantry Destroyed'
]

# text descriptions for different types of Campaign Day missions
MISSION_DESC = {
	'Advance' : 'Enemy resistance is scattered and we are pushing forward. Advance into enemy territory, destroy any resistance, and capture territory.',
	'Battle' : 'Your group has been posted to the front line where there is heavy resistance. Break through the enemy defenses, destroy enemy units, and capture territory.',
	'Counterattack' : 'After being on the defensive, your battlegroup has been ordered to attack the enemy advance.',
	'Fighting Withdrawl' : 'The enemy is mounting a strong attack against our lines. Help to defend territory and withdraw into friendly territory if necessary.'
}

##########################################################################################
#                                Game Engine Definitions                                 #
##########################################################################################

# FUTURE: move these to a JSON file?

# chance of a direct hit during air or artillery attacks
DIRECT_HIT_CHANCE = 8.0

# base crew experience point and level system
BASE_EXP_REQUIRED = 10.0
EXP_EXPONENT = 1.1

# region definitions: set by campaigns, determine terrain odds on the campaign day map,
# types and odds of weather conditions at different times during the calendar year
REGIONS = {
	'Northeastern Europe' : {
		
		# campaign day map terrain type odds
		'cd_terrain_odds' : {
			'Flat' : 50.0,
			'Forest' : 10.0,
			'Hills' : 15.0,
			'Fields' : 10.0,
			'Marsh' : 5.0,
			'Villages' : 10.0
		},
		
		# odds of 1 dirt road bring present on the map
		'dirt_road_odds' : 50.0,
		
		# odds of 1+ rivers being spawned (with crossing points)
		'river_odds' : 50.0,
		
		# seasons, end dates, and weather odds for each season
		'season_weather_odds' : {
			
			'Winter' : {
				'end_date' : '03.31',
				'ground_conditions' : {
					'Dry' : 20.0, 'Wet' : 0.0, 'Muddy' : 5.0,
					'Snow' : 60.0, 'Deep Snow' : 15.0
				},
				
				# if ground cover is rolled as 'Dry', chance that snow could later fall
				'freezing' : 80.0,
				
				'cloud_cover' : {
					'Clear' : 40.0, 'Scattered' : 20.0,
					'Heavy' : 20.0, 'Overcast' : 20.0
				},
				
				# if precipitation is rolled and cloud cover is clear, cloud cover will be set to scattered+
				'precipitation' : {
					'None' : 35.0, 'Mist' : 10.0,
					'Rain' : 10.0, 'Heavy Rain' : 5.0,
					'Light Snow' : 10.0, 'Snow' : 20.0,
					'Blizzard' : 10.0
				}
				
			},
			'Spring' : {
				'end_date' : '06.14',
				'ground_conditions' : {
					'Dry' : 50.0, 'Wet' : 20.0, 'Muddy' : 25.0,
					'Snow' : 5.0, 'Deep Snow' : 0.0
				},
				'freezing' : 10.0,
				'cloud_cover' : {
					'Clear' : 50.0, 'Scattered' : 15.0,
					'Heavy' : 20.0, 'Overcast' : 15.0
				},
				'precipitation' : {
					'None' : 30.0, 'Mist' : 10.0,
					'Rain' : 30.0, 'Heavy Rain' : 20.0,
					'Light Snow' : 10.0, 'Snow' : 0.0,
					'Blizzard' : 0.0
				}
				
			},
			'Summer' : {
				'end_date' : '09.31',
				'ground_conditions' : {
					'Dry' : 75.0, 'Wet' : 10.0, 'Muddy' : 15.0,
					'Snow' : 0.0, 'Deep Snow' : 0.0
				},
				'freezing' : 0.0,
				'cloud_cover' : {
					'Clear' : 50.0, 'Scattered' : 15.0,
					'Heavy' : 20.0, 'Overcast' : 15.0
				},
				'precipitation' : {
					'None' : 60.0, 'Mist' : 10.0,
					'Rain' : 20.0, 'Heavy Rain' : 10.0,
					'Light Snow' : 0.0, 'Snow' : 0.0,
					'Blizzard' : 0.0
				}	
			},
			'Autumn' : {
				'end_date' : '12.01',
				'ground_conditions' : {
					'Dry' : 65.0, 'Wet' : 10.0, 'Muddy' : 15.0,
					'Snow' : 10.0, 'Deep Snow' : 0.0
				},
				'freezing' : 15.0,
				'cloud_cover' : {
					'Clear' : 50.0, 'Scattered' : 15.0,
					'Heavy' : 20.0, 'Overcast' : 15.0
				},
				'precipitation' : {
					'None' : 50.0, 'Mist' : 10.0,
					'Rain' : 20.0, 'Heavy Rain' : 10.0,
					'Light Snow' : 10.0, 'Snow' : 0.0,
					'Blizzard' : 0.0
				}
				
			}
		}
		
	},
	
	'Northwestern Europe' : {

		'cd_terrain_odds' : {
			'Flat' : 40.0,
			'Forest' : 20.0,
			'Hills' : 10.0,
			'Fields' : 15.0,
			'Marsh' : 5.0,
			'Villages' : 10.0
		},
		
		'dirt_road_odds' : 80.0,
		'river_odds' : 20.0,

		'season_weather_odds' : {
			
			'Winter' : {
				'end_date' : '03.31',
				'ground_conditions' : {
					'Dry' : 25.0, 'Wet' : 0.0, 'Muddy' : 5.0,
					'Snow' : 60.0, 'Deep Snow' : 10.0
				},
				'freezing' : 60.0,
				'cloud_cover' : {
					'Clear' : 40.0, 'Scattered' : 20.0,
					'Heavy' : 20.0, 'Overcast' : 20.0
				},
				
				'precipitation' : {
					'None' : 35.0, 'Mist' : 10.0,
					'Rain' : 10.0, 'Heavy Rain' : 5.0,
					'Light Snow' : 15.0, 'Snow' : 20.0,
					'Blizzard' : 5.0
				}
				
			},
			'Spring' : {
				'end_date' : '06.14',
				'ground_conditions' : {
					'Dry' : 50.0, 'Wet' : 20.0, 'Muddy' : 25.0,
					'Snow' : 5.0, 'Deep Snow' : 0.0
				},
				'freezing' : 5.0,
				'cloud_cover' : {
					'Clear' : 50.0, 'Scattered' : 15.0,
					'Heavy' : 20.0, 'Overcast' : 15.0
				},
				'precipitation' : {
					'None' : 30.0, 'Mist' : 10.0,
					'Rain' : 30.0, 'Heavy Rain' : 20.0,
					'Light Snow' : 10.0, 'Snow' : 0.0,
					'Blizzard' : 0.0
				}
				
			},
			'Summer' : {
				'end_date' : '09.31',
				'ground_conditions' : {
					'Dry' : 75.0, 'Wet' : 10.0, 'Muddy' : 15.0,
					'Snow' : 0.0, 'Deep Snow' : 0.0
				},
				'freezing' : 0.0,
				'cloud_cover' : {
					'Clear' : 50.0, 'Scattered' : 15.0,
					'Heavy' : 20.0, 'Overcast' : 15.0
				},
				'precipitation' : {
					'None' : 60.0, 'Mist' : 10.0,
					'Rain' : 20.0, 'Heavy Rain' : 10.0,
					'Light Snow' : 0.0, 'Snow' : 0.0,
					'Blizzard' : 0.0
				}
				
			},
			'Autumn' : {
				'end_date' : '12.01',
				'ground_conditions' : {
					'Dry' : 65.0, 'Wet' : 10.0, 'Muddy' : 15.0,
					'Snow' : 10.0, 'Deep Snow' : 0.0
				},
				'freezing' : 10.0,
				'cloud_cover' : {
					'Clear' : 50.0, 'Scattered' : 15.0,
					'Heavy' : 20.0, 'Overcast' : 15.0
				},
				'precipitation' : {
					'None' : 50.0, 'Mist' : 10.0,
					'Rain' : 20.0, 'Heavy Rain' : 10.0,
					'Light Snow' : 10.0, 'Snow' : 0.0,
					'Blizzard' : 0.0
				}
				
			}
		}
		
	}
}

# base chance of a ground conditions change during weather update
GROUND_CONDITION_CHANGE_CHANCE = 3.0
# modifier for heavy rain/snow
HEAVY_PRECEP_MOD = 5.0

# list of crew stats
CREW_STATS = ['Perception', 'Morale', 'Grit', 'Knowledge']

# list of positions that player character can be (Commander, etc.)
PLAYER_POSITIONS = ['Commander', 'Commander/Gunner']

# list of possible new positions for a crew that is transferring to a different type of tank
# listed in order of preference
POSITION_TRANSFER_LIST = {
	"Commander" : ["Commander", "Commander/Gunner"],
	"Commander/Gunner" : ["Commander/Gunner", "Commander"],
	"Gunner" : ["Gunner", "Gunner/Loader"],
	"Gunner/Loader" : ["Gunner/Loader", "Gunner"],
	"Loader" : ["Loader", "Gunner/Loader"],
	"Driver" : ["Driver"],
	"Assistant Driver" : ["Assistant Driver", "Radio Operator"],
	"Radio Operator" : ["Radio Operator", "Assistant Driver"]
}

# length of scenario turn in minutes
TURN_LENGTH = 2

# maximum visible distance when buttoned up
MAX_BU_LOS = 1

# base chance to spot unit at distance 0,1,2,3
SPOT_BASE_CHANCE = [95.0, 85.0, 70.0, 50.0]

# each point of Perception increases chance to spot enemy unit by this much
PERCEPTION_SPOTTING_MOD = 5.0

# base chance of moving forward/backward into next hex
BASE_FORWARD_MOVE_CHANCE = 50.0
BASE_REVERSE_MOVE_CHANCE = 20.0

# bonus per unsuccessful move attempt
BASE_MOVE_BONUS = 15.0

# base critical hit and miss thresholds
CRITICAL_HIT = 3.0
CRITICAL_MISS = 97.0

# maximum range at which MG attacks have a chance to penetrate armour
MG_AP_RANGE = 1

# base success chances for point fire attacks
# first column is for vehicle targets, second is everything else
PF_BASE_CHANCE = [
	[98.0, 88.0],			# same hex
	[83.0, 78.0],			# 1 hex range
	[72.0, 58.0],			# 2 "
	[58.0, 35.0]			# 3 hex range
]

# acquired target bonus for level 1 and level 2 for point fire
AC_BONUS = [
	[8.0, 15.0],	# distance 0
	[10.0, 25.0],	# distance 1
	[10.0, 25.0],	# distance 2
	[20.0, 35.0]	# distance 3
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


RESOLVE_FP_BASE_CHANCE = 5.0	# base chance of a 1 firepower attack destroying a unit
RESOLVE_FP_CHANCE_STEP = 5.0	# each additional firepower beyond 1 adds this additional chance
RESOLVE_FP_CHANCE_MOD = 1.05	# additional firepower modifier increased by this much beyond 1

MORALE_CHECK_BASE_CHANCE = 70.0	# base chance of passing a morale check


# base success chances for armour penetration
AP_BASE_CHANCE = {
	'MG' : 16.7,
	'AT Rifle' : 28.0,
	'20L' : 28.0,
	'37S' : 58.4,
	'37' : 72.0,
	'37L' : 83.0,
	'47S' : 72.0,
	'45L' : 91.7,
	'50L' : 120.0,
	'75S' : 91.7,
	'75' : 120.0,		# not sure if this and below are accurate, FUTURE: check balance
	'75L' : 160.0,
	'76S' : 83.0,
	'76L' : 160.0,
	'76LL' : 300.0,
	'88L' : 200.0,
	'88LL' : 380.0,
	'105' : 420.0
}

# effective FP of an HE hit from different weapon calibres
HE_FP_EFFECT = [
	(200, 36),(183, 34),(170, 32),(160, 31),(150, 30),(140, 28),(128, 26),(120, 24),
	(107, 22),(105, 22),(100, 20),(95, 19),(88, 18),(85, 17),(80, 16),(75, 14),
	(70, 12),(65, 10),(60, 8),(57, 7),(50, 6),(45, 5),(37, 4),(30, 2),(25, 2),(20, 1)
]

# penetration chance on armour of HE hits
HE_AP_CHANCE = [
	(150, 110.0),(120, 100.0),(100, 91.7),(80, 72.2),(70, 58.4),(50, 41.7),(40, 27.8),(30, 16.7)
]

# odds of unarmoured vehicle destruction when resolving FP
VEH_FP_TK = [
	(36, 110.0),(30, 100.0),(24, 97.0),(20, 92.0),(16, 83.0),(12, 72.0),(8, 58.0),(6, 42.0),
	(4, 28.0),(2, 17.0),(1, 8.0)
]

# amount within an AFV armour save that will result in Stun tests for crew/unit
AP_STUN_MARGIN = 10.0

# for each campaign day hex terrain type, odds that a unit on the scenario map will be in
# a given type of terrain in its scenario hex
SCENARIO_TERRAIN_ODDS = {
	'Flat' : {
		'Open Ground' : 60.0,
		'Broken Ground' : 20.0,
		'Brush' : 10.0,
		'Woods' : 5.0,
		'Wooden Buildings' : 5.0
	},
	'Forest' : {
		'Open Ground' : 10.0,
		'Broken Ground' : 15.0,
		'Brush' : 25.0,
		'Woods' : 45.0,
		'Wooden Buildings' : 5.0
	},
	'Hills' : {
		'Open Ground' : 15.0,
		'Broken Ground' : 10.0,
		'Brush' : 5.0,
		'Woods' : 5.0,
		'Hills' : 50.0,
		'Wooden Buildings' : 5.0
	},
	'Fields' : {
		'Open Ground' : 20.0,
		'Broken Ground' : 5.0,
		'Brush' : 5.0,
		'Woods' : 5.0,
		'Fields' : 50.0,
		'Wooden Buildings' : 5.0
	},
	'Marsh' : {
		'Open Ground' : 10.0,
		'Broken Ground' : 5.0,
		'Brush' : 5.0,
		'Woods' : 5.0,
		'Marsh' : 60.0,
		'Wooden Buildings' : 5.0
	},
	'Villages' : {
		'Open Ground' : 10.0,
		'Broken Ground' : 10.0,
		'Brush' : 10.0,
		'Woods' : 5.0,
		'Fields' : 15.0,
		'Wooden Buildings' : 50.0
	}
}

# modifiers and effects for different types of terrain on the scenario layer
SCENARIO_TERRAIN_EFFECTS = {
	'Open Ground' : {
		'HD Chance' : 5.0
	},
	'Broken Ground' : {
		'TEM' : {
			'Infantry' : -15.0,
			'Deployed Gun' : -15.0
		},
		'HD Chance' : 10.0,
		'Movement Mod' : -5.0,
		'Bog Mod' : 1.0
	},
	'Brush': {
		'TEM' : {
			'All' : -15.0
		},
		'HD Chance' : 10.0,
		'Movement Mod' : -15.0,
		'Bog Mod' : 2.0,
		'Air Burst' : 10.0,
		'Burnable' : True
	},
	'Woods': {
		'TEM' : {
			'All' : -25.0
		},
		'HD Chance' : 20.0,
		'Movement Mod' : -30.0,
		'Bog Mod' : 5.0,
		'Double Bog Check' : True,		# player must test to bog before moving out of this terrain type
		'Air Burst' : 20.0,
		'Burnable' : True
	},
	'Fields': {
		'TEM' : {
			'All' : -10.0
		},
		'HD Chance' : 5.0,
		'Burnable' : True
	},
	'Hills': {
		'TEM' : {
			'All' : -20.0
		},
		'HD Chance' : 40.0,
		'Hidden Mod' : 30.0
	},
	'Wooden Buildings': {
		'TEM' : {
			'Infantry' : -30.0,
			'Deployed Gun' : -30.0
		},
		'HD Chance' : 30.0,
		'Hidden Mod' : 20.0,
		'Burnable' : True
	},
	'Marsh': {
		'TEM' : {
			'All' : -10.0
		},
		'HD Chance' : 15.0,
		'Movement Mod' : -30.0,
		'Bog Mod' : 10.0,
		'Double Bog Check' : True
	}
}

# relative locations to draw greebles for terrain on scenario map
GREEBLE_LOCATIONS = [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]

# modifier for base HD chance
HD_SIZE_MOD = {
	'Very Small' : 12.0, 'Small' : 6.0, 'Normal' : 0.0, 'Large' : -6.0, 'Very Large' : -12.0
}

# base chance of a sniper attack being effective
BASE_SNIPER_TK_CHANCE = 45.0

# base chance of a random event in a scenario
BASE_RANDOM_EVENT_CHANCE = 5.0
# base chance of a random event in a campaign day
BASE_CD_RANDOM_EVENT_CHANCE = 3.0

# base number of minutes between weather update checks
BASE_WEATHER_UPDATE_CLOCK = 30



##########################################################################################
#                                         Classes                                        #
##########################################################################################

# Campaign: stores data about a campaign and calendar currently in progress
class Campaign:
	def __init__(self):
		
		# load skills from JSON file - they won't change over the course of a campaign
		with open(DATAPATH + 'skill_defs.json', encoding='utf8') as data_file:
			self.skills = json.load(data_file)
		
		self.logs = {}			# dictionary of campaign logs for each combat day
		self.player_unit = None		# placeholder for player unit
		self.player_squad_max = 0	# maximum units in player squad
		self.player_squad_num = 0	# current units in player squad
		self.player_vp = 0		# total player victory points
		self.stats = {}			# local copy of campaign stats
		self.combat_calendar = []	# list of combat days, created by GenerateCalendar
		self.today = None		# pointer to current day in calendar
		self.current_week = None	# " week
		self.enemy_class_odds = {}	# placeholder for enemy unit spawn odds, set by campaign days
		self.active_calendar_menu = 1	# currently active menu in the campaign calendar interface
		self.ended = False		# campaign has ended due to player serious injury or death
		self.player_oob = False		# player was seriously injured or killed
		
		self.decoration = ''		# decoration awarded to player at end of campaign
		
		# records for end-of-campaign summary
		self.records = {}
		for text in RECORD_LIST:
			self.records[text] = 0
	
	
	# end the campaign
	def DoEnd(self):
		self.AwardDecorations()
		self.DisplayCampaignSummary()
		ExportLog()
		EraseGame()
	
	
	# randomly generate a list of combat days for this campaign
	def GenerateCombatCalendar(self):
		
		# roll separately for each week of campaign
		for week in self.stats['calendar_weeks']:
			
			# if refitting week, only add the first day to the calendar
			if 'refitting' in week:
				self.combat_calendar.append(week['start_date'])
				continue
			
			# build list of possible dates this week: add the first date, then the following 6
			possible_days = []
			possible_days.append(week['start_date'])
			day_text = possible_days[0]
			for i in range(6):
				(year, month, day) = day_text.split('.')
				
				# last day of month
				if int(day) == monthrange(int(year), int(month))[1]:
					
					# last day of year
					if int(month) == 12:
						year = str(int(year) + 1)
						month = '01'
						day = '01'
					else:
						month = str(int(month) + 1)
						day = '01'
				
				else:
					day = str(int(day) + 1)
				
				day_text = year + '.' + month.zfill(2) + '.' + day.zfill(2)
				
				# check that day is not past end of campaign
				if day_text > self.stats['end_date']:
					break
				
				possible_days.append(day_text)
			
			# for each possible day, roll to see if it's added to the combat calendar
			chance = float(week['combat_chance'])
			for day_text in possible_days:
				# if day is past end of calendar week, stop
				if 'end_date' in week:
					if day_text > week['end_date']:
						continue
				
				if GetPercentileRoll() <= chance:
					self.combat_calendar.append(day_text)
		
		#print('DEBUG: Added ' + str(len(self.combat_calendar)) + ' days to combat calendar')
		#for day_text in self.combat_calendar:
		#	print(day_text)
	
	
	# copy over day's records to a new entry in the campaign record log
	def LogDayRecords(self):
		self.logs[self.today] = campaign_day.records.copy()
	
	
	# award VP to the player, also adds exp to active crew
	def AwardVP(self, vp_to_add):
		self.player_vp += vp_to_add
		
		for position in self.player_unit.positions_list:
			if position.crewman is None: continue
			if position.crewman.status not in ['Dead', 'Unconscious']:
				position.crewman.AwardExp(vp_to_add)
	
	
	# menu to select a campaign
	def CampaignSelectionMenu(self):
		
		# update screen with info about the currently selected campaign
		def UpdateCampaignSelectionScreen(selected_campaign):
			libtcod.console_clear(con)
			DrawFrame(con, 26, 1, 37, 58)
			libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
			libtcod.console_print_ex(con, 45, 3, libtcod.BKGND_NONE, libtcod.CENTER,
				'Campaign Selection')
			libtcod.console_set_default_background(con, libtcod.darkest_grey)
			libtcod.console_rect(con, 27, 5, 35, 4, True, libtcod.BKGND_SET)
			libtcod.console_set_default_background(con, libtcod.black)
			libtcod.console_set_default_foreground(con, PORTRAIT_BG_COL)
			lines = wrap(selected_campaign['name'], 33)
			y = 6
			for line in lines:
				libtcod.console_print_ex(con, 45, y, libtcod.BKGND_NONE, libtcod.CENTER, line)
				y += 1
			
			# player nation flag
			if selected_campaign['player_nation'] in session.flags:
				libtcod.console_blit(session.flags[selected_campaign['player_nation']],
					0, 0, 0, 0, con, 30, 10)
			
			# player and enemy forces
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print_ex(con, 45, 26, libtcod.BKGND_NONE, libtcod.CENTER,
				'PLAYER FORCE')
			libtcod.console_print_ex(con, 45, 30, libtcod.BKGND_NONE, libtcod.CENTER,
				'ENEMY FORCES')
			
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			libtcod.console_print_ex(con, 45, 27, libtcod.BKGND_NONE, libtcod.CENTER,
				selected_campaign['player_nation'])
			text = ''
			for nation_name in selected_campaign['enemy_nations']:
				if selected_campaign['enemy_nations'].index(nation_name) != 0:
					text += ', '
				text += nation_name
			libtcod.console_print_ex(con, 45, 31, libtcod.BKGND_NONE, libtcod.CENTER, text)
			
			# calendar range and total combat days
			libtcod.console_set_default_foreground(con, libtcod.white)
			text = GetDateText(selected_campaign['start_date']) + ' to'
			libtcod.console_print_ex(con, 45, 33, libtcod.BKGND_NONE, libtcod.CENTER, text)
			text = GetDateText(selected_campaign['end_date'])
			libtcod.console_print_ex(con, 45, 34, libtcod.BKGND_NONE, libtcod.CENTER, text)
			
			# wrapped description text
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			y = 39
			lines = wrap(selected_campaign['desc'], 33)
			for line in lines[:10]:
				libtcod.console_print(con, 28, y, line)
				y+=1
				
			libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
			libtcod.console_print(con, 32, 53, EnKey('a').upper() + '/' + EnKey('d').upper())
			libtcod.console_print(con, 32, 54, 'R')
			libtcod.console_print(con, 32, 55, 'Enter')
			libtcod.console_print(con, 32, 56, 'Esc')
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print(con, 38, 53, 'Select Campaign')
			libtcod.console_print(con, 38, 54, 'Select Random')
			libtcod.console_print(con, 38, 55, 'Proceed')
			libtcod.console_print(con, 38, 56, 'Return to Main Menu')
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		
		# load basic information of campaigns into a list of dictionaries
		BASIC_INFO = [
			'name', 'start_date', 'end_date', 'player_nation',
			'enemy_nations', 'desc'
		]
		
		campaign_list = []
		
		for filename in os.listdir(CAMPAIGNPATH):
			if not filename.endswith('.json'): continue
			with open(CAMPAIGNPATH + filename, encoding='utf8') as data_file:
				campaign_data = json.load(data_file)
			new_campaign = {}
			new_campaign['filename'] = filename
			for k in BASIC_INFO:
				new_campaign[k] = campaign_data[k]
			campaign_list.append(new_campaign)
			del campaign_data
		
		# sort campaigns by start date
		campaign_list = sorted(campaign_list, key = lambda x : (x['start_date']))
		
		# select first campaign by default
		selected_campaign = campaign_list[0]
		
		# draw menu screen for first time
		UpdateCampaignSelectionScreen(selected_campaign)
		
		exit_menu = False
		while not exit_menu:
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			if not GetInputEvent(): continue
			
			# exit without starting a new campaign if escape is pressed
			if key.vk == libtcod.KEY_ESCAPE:
				return False
			
			# proceed with selected campaign
			elif key.vk == libtcod.KEY_ENTER:
				exit_menu = True
			
			key_char = DeKey(chr(key.c).lower())
			
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
				UpdateCampaignSelectionScreen(selected_campaign)
			
			# select a random campaign (not keymapped)
			elif chr(key.c).lower() == 'r':
				selected_campaign = choice(campaign_list)
				exit_menu = True
				
		
		# create a local copy of selected campaign stats
		with open(CAMPAIGNPATH + selected_campaign['filename'], encoding='utf8') as data_file:
			self.stats = json.load(data_file)
		
		# generate list of combat days
		self.GenerateCombatCalendar()
		
		# set current date and week
		self.today = self.combat_calendar[0]
		self.current_week = self.stats['calendar_weeks'][0]
		
		return True
		
		
	# menu to select player tank
	# also allows input/generation of tank name, and return both
	# can be used when replacing a tank mid-campaign as well
	def TankSelectionMenu(self):
		
		def UpdateTankSelectionScreen(selected_unit, player_tank_name):
			libtcod.console_clear(con)
			DrawFrame(con, 26, 1, 37, 58)
			
			libtcod.console_set_default_background(con, libtcod.darker_blue)
			libtcod.console_rect(con, 27, 2, 35, 3, False, libtcod.BKGND_SET)
			libtcod.console_set_default_background(con, libtcod.black)
			
			libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
			libtcod.console_print_ex(con, 45, 3, libtcod.BKGND_NONE, libtcod.CENTER,
				'Player Unit Selection')
			libtcod.console_set_default_foreground(con, libtcod.white)
			
			libtcod.console_print_ex(con, 45, 6, libtcod.BKGND_NONE, libtcod.CENTER,
				'Select a tank type to command')
			
			DrawFrame(con, 32, 10, 27, 18)
			selected_unit.DisplayMyInfo(con, 33, 11, status=False)
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print(con, 33, 26, 'Crew: ' + str(len(selected_unit.GetStat('crew_positions'))))
			
			libtcod.console_print(con, 33, 13, player_tank_name)
			
			text = ''
			for t in selected_unit.GetStat('description'):
				text += t
			
			lines = wrap(text, 33)
			y = 32
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			for line in lines[:20]:
				libtcod.console_print(con, 28, y, line)
				y+=1
			
			libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
			libtcod.console_print(con, 32, 53, EnKey('a').upper() + '/' + EnKey('d').upper())
			libtcod.console_print(con, 32, 54, 'N')
			libtcod.console_print(con, 32, 55, 'Enter')
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print(con, 38, 53, 'Select Unit Type')
			libtcod.console_print(con, 38, 54, 'Set/Generate Tank Name')
			libtcod.console_print(con, 38, 55, 'Proceed')
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		
		# generate tempoary list of units, one per possible unit type
		unit_list = []
		with open(DATAPATH + 'unit_type_defs.json', encoding='utf8') as data_file:
			unit_types = json.load(data_file)
		
		for unit_id in self.stats['player_unit_list']:
			
			# check that unit is available at current point in calendar
			if unit_id not in unit_types: continue
			if 'rarity' in unit_types[unit_id]:
				for date, chance in unit_types[unit_id]['rarity'].items():
					# not yet available at this time
					if date > campaign.today:
						continue
					# earliest rarity date is on or after current date, proceed
					break
			
			new_unit = Unit(unit_id)
			unit_list.append(new_unit)
		
		# select first tank by default
		selected_unit = unit_list[0]
		
		# placeholder for tank name if any
		player_tank_name = ''
		
		# draw menu screen for first time
		UpdateTankSelectionScreen(selected_unit, player_tank_name)
		
		exit_loop = False
		while not exit_loop:
			
			# emergency exit in case of endless loop
			if libtcod.console_is_window_closed(): sys.exit()
			
			libtcod.console_flush()
			if not GetInputEvent(): continue
			
			# proceed with selected tank
			if key.vk == libtcod.KEY_ENTER:
				exit_loop = True
			
			# unmapped keys
			key_char = chr(key.c).lower()
			
			# change/generate player tank name
			if key_char == 'n':				
				player_tank_name = ShowTextInputMenu('Enter a name for your tank', player_tank_name, MAX_TANK_NAME_LENGTH, [])
				UpdateTankSelectionScreen(selected_unit, player_tank_name)
			
			# mapped keys
			key_char = DeKey(chr(key.c).lower())
			
			# change selected tank
			if key_char in ['a', 'd']:
				
				i = unit_list.index(selected_unit)
				
				if key_char == 'd':
					if i == len(unit_list) - 1:
						selected_unit = unit_list[0]
					else:
						selected_unit = unit_list[i+1]
				else:
					if i == 0:
						selected_unit = unit_list[-1]
					else:
						selected_unit = unit_list[i-1]
				UpdateTankSelectionScreen(selected_unit, player_tank_name)
			
		return (selected_unit.unit_id, player_tank_name)
	
	
	# allow player to choose a new tank after losing one or during a refit period
	def ReplacePlayerTank(self):
		
		exit_menu = False
		while not exit_menu:
			
			# allow player to choose a new tank model
			(unit_id, tank_name) = campaign.TankSelectionMenu()
			
			# determine crew transfer procedure
			
			# build a list of the required position names for the new tank type
			open_position_list = []
			with open(DATAPATH + 'unit_type_defs.json', encoding='utf8') as data_file:
				unit_types = json.load(data_file)
				for position in unit_types[unit_id]['crew_positions']:
					open_position_list.append(position['name'])
			
			# run through every position in current tank, try to place crew into a position in the new one
			# if any crew cannot be fit into new position, put them into a list
			transfer_dict = {}
			discard_list = []
			for position in campaign.player_unit.positions_list:
				if position.crewman is None: continue
				
				# try to find an open position in the new unit that fits
				open_spot = False
				for new_position in POSITION_TRANSFER_LIST[position.name]:
					
					if new_position in open_position_list:
						open_spot = True
						open_position_list.pop(open_position_list.index(new_position))
						transfer_dict[position.name] = new_position
						print('DEBUG: found a transfer match: ' + position.name + ' -> ' + new_position)
						break
				
				if not open_spot:
					discard_list.append(position.name)
					print('DEBUG: must discard crewman in ' + position.name + ' position')
			
			# display this info to player and allow them to cancel and choose a different tank model
			if len(discard_list) > 0:
				text = 'Crewmen in the following positions will leave your tank and be reassigned: '
				for position_name in discard_list:
					text += position_name + ' '
			else:
				text = 'All current crew can be assigned to this new tank.'
			
			if ShowNotification(text, confirm=True):
				exit_menu = True
			
		new_unit = Unit(unit_id)
		new_unit.unit_name = tank_name
		new_unit.nation = campaign.stats['player_nation']
		
		# use transfer_dict to transfer crew over to new tank
		for position_name, new_position in transfer_dict.items():
			
			# find a crewman currently in this position
			crewman = None
			for position in campaign.player_unit.positions_list:
				if position_name != position.name: continue
				if position.crewman is None: continue
				crewman = position.crewman
				break
			
			# no crewman in that position to move
			if crewman is None: continue
			
			# target position should exist, and should be empty
			for position in new_unit.positions_list:
				if position.name == new_position:
					position.crewman = crewman
					print('DEBUG: moved ' + position_name + ' to ' + new_position)
					break
			
			
		
		# generate new crewmen if required
		for position in new_unit.positions_list:
			if position.crewman is None:
				position.crewman = Personnel(new_unit, new_unit.nation, position)
				print('DEBUG: generated new crewman for ' + position.name)
		
		new_unit.ClearGunAmmo()
		self.player_unit = new_unit

	
	# display an animated screen for the start of a new combat day
	def ShowStartOfDay(self):
		
		libtcod.console_clear(con)
		
		for y in range(WINDOW_HEIGHT):
			col = libtcod.Color(int(255 * (y / WINDOW_HEIGHT)), int(170 * (y / WINDOW_HEIGHT)), 0)
			libtcod.console_set_default_background(con, col)
			libtcod.console_rect(con, 0, y, WINDOW_WIDTH, 1, True, libtcod.BKGND_SET)
		libtcod.console_set_default_background(con, libtcod.black)
		libtcod.console_rect(con, 30, 20, 30, 10, True, libtcod.BKGND_SET)
		libtcod.console_set_default_foreground(con, libtcod.light_grey)
		DrawFrame(con, 30, 20, 30, 10)
		libtcod.console_set_default_foreground(con, libtcod.white)
		libtcod.console_print_ex(con, WINDOW_XM, 22, libtcod.BKGND_NONE, libtcod.CENTER,
			GetDateText(self.today))
		
		if 'refitting' in self.current_week:
			libtcod.console_print_ex(con, WINDOW_XM, 24, libtcod.BKGND_NONE, libtcod.CENTER,
				'Refitting')
		else:
			libtcod.console_print_ex(con, WINDOW_XM, 23, libtcod.BKGND_NONE, libtcod.CENTER,
				self.current_week['day_start'])
			libtcod.console_print_ex(con, WINDOW_XM, 25, libtcod.BKGND_NONE, libtcod.CENTER,
				self.current_week['week_description'])
		
		# fade in from black
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		for i in range(100, 0, -5):
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, (i * 0.01))
			libtcod.console_flush()
			Wait(5, ignore_animations=True)
		Wait(95, ignore_animations=True)
	
	
	# do automatic actions that end a campaign day: resolve wounds and check for crewman level up
	def ShowEndOfDay(self):
		
		# create background console
		libtcod.console_clear(con)
		
		# starfield
		for i in range(18):
			x = libtcod.random_get_int(0, 0, WINDOW_WIDTH)
			y = libtcod.random_get_int(0, 0, 18)
			libtcod.console_put_char_ex(con, x, y, 250, libtcod.white, libtcod.black)
		
		# gradient
		for y in range(19, WINDOW_HEIGHT):
			col = libtcod.Color(int(180 * (y / WINDOW_HEIGHT)), 0, 0)
			libtcod.console_set_default_background(con, col)
			libtcod.console_rect(con, 0, y, WINDOW_WIDTH, 1, True, libtcod.BKGND_SET)
		
		# window
		libtcod.console_set_default_background(con, libtcod.black)
		libtcod.console_rect(con, 15, 12, 60, 40, True, libtcod.BKGND_SET)
		libtcod.console_set_default_foreground(con, libtcod.light_grey)
		DrawFrame(con, 15, 12, 60, 40)
		
		libtcod.console_set_default_background(con, libtcod.darker_blue)
		libtcod.console_rect(con, 39, 13, 12, 3, True, libtcod.BKGND_SET)
		libtcod.console_set_default_background(con, libtcod.black)
		libtcod.console_set_default_foreground(con, libtcod.lighter_blue)
		libtcod.console_print_ex(con, WINDOW_XM, 14, libtcod.BKGND_NONE, libtcod.CENTER,
				'End of Day')
		
		# crew advances and wound recovery
		libtcod.console_set_default_foreground(con, libtcod.red)
		libtcod.console_print(con, 43, 18, 'Wound')
		libtcod.console_set_default_foreground(con, libtcod.light_blue)
		libtcod.console_print(con, 55, 18, 'Level Up')
		
		y = 20
		for position in campaign.player_unit.positions_list:
			if position.crewman is None: continue
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print(con, 19, y, position.name)
			position.crewman.DisplayName(con, 19, y+1, first_initial=True)
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			for x in range(19, 68):
				libtcod.console_put_char(con, x, y+2, '.')
			y += 5
		
		libtcod.console_set_default_foreground(con, libtcod.light_grey)
		for y1 in range(19, y-3):
			libtcod.console_put_char(con, 40, y1, '.')
			libtcod.console_put_char(con, 52, y1, '.')
		
		libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
		libtcod.console_print(con, 38, 49, 'Enter')
		libtcod.console_set_default_foreground(con, libtcod.light_grey)
		libtcod.console_print(con, 45, 49, 'Continue')
		
		
		# fade in from black
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		for i in range(100, 0, -5):
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, (i * 0.01))
			Wait(5, ignore_animations=True)
		
		# roll and display crew wounds and advances
		y = 20
		for position in campaign.player_unit.positions_list:
			if position.crewman is None: continue
			
			if position.crewman.wound == '':
				libtcod.console_set_default_foreground(con, libtcod.light_grey)
				libtcod.console_print(con, 43, y+1, 'None')
			elif position.crewman.wound == 'Critical':
				position.crewman.wound = 'Serious'
				libtcod.console_set_default_foreground(con, libtcod.dark_red)
				libtcod.console_print(con, 43, y+1, position.crewman.wound)
			else:
				# roll for wound recovery
				roll = GetPercentileRoll()
				
				if roll <= position.crewman.stats['Grit'] * 8.0:
					position.crewman.wound = ''
					libtcod.console_set_default_foreground(con, libtcod.dark_blue)
					libtcod.console_print(con, 43, y+1, 'Recovered')
				else:
					libtcod.console_set_default_foreground(con, libtcod.dark_red)
					libtcod.console_print(con, 43, y+1, position.crewman.wound)
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			Wait(30, ignore_animations=True)
			
			# check for level up
			levels_up = 0
			for level in range(position.crewman.level+1, 31):
				if position.crewman.exp >= GetExpRequiredFor(level):
					levels_up += 1
				else:
					break
			
			if levels_up == 0:
				libtcod.console_set_default_foreground(con, libtcod.light_grey)
				libtcod.console_print(con, 55, y+1, 'None')
			else:
				position.crewman.level += levels_up
				position.crewman.adv += levels_up
				libtcod.console_set_default_foreground(con, libtcod.white)
				libtcod.console_print(con, 55, y+1, '+' + str(levels_up))
			
			# crewmen recover too
			position.crewman.status = ''
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			Wait(30, ignore_animations=True)
			y += 5
		
		# repair tank if required
		if campaign.player_unit.immobilized:
			campaign.player_unit.immobilized = False
		
		exit_menu = False
		while not exit_menu:
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			if not GetInputEvent(): continue
			
			if key.vk == libtcod.KEY_ENTER:
				exit_menu = True

	
	
	# calculate decorations to be awarded at the end of a campaign
	def AwardDecorations(self):
		
		# no decorations set
		if 'decorations_list' not in self.stats:
			return
		
		# generate an ordered list of required VP scores and decoration names for this campaign
		deco_list = []
		
		for key, value in self.stats['decorations_list'].items():
			deco_list.append((int(key), value))
		deco_list.sort(key = lambda x: x[0], reverse=True)
		
		# see if player has enough VP for a decoration
		for (vp_req, decoration) in deco_list:
			if self.player_vp >= vp_req:
				self.decoration = decoration
				return
	
	
	# display a summary of a completed campaign
	def DisplayCampaignSummary(self):
		
		# clear screen
		libtcod.console_clear(con)
		
		# build info window
		temp_con = libtcod.console_new(29, 54)
		libtcod.console_set_default_background(temp_con, libtcod.black)
		libtcod.console_set_default_foreground(temp_con, libtcod.light_grey)
		libtcod.console_clear(temp_con)
		DrawFrame(temp_con, 0, 0, 29, 54)
		
		# campaign and calendar day info
		libtcod.console_set_default_foreground(temp_con, TITLE_COL)
		libtcod.console_print_ex(temp_con, 14, 1, libtcod.BKGND_NONE, libtcod.CENTER,
			'Your Campaign is Finished')
		
		libtcod.console_set_default_foreground(temp_con, PORTRAIT_BG_COL)
		y = 3
		for line in wrap(self.stats['name'], 27):
			libtcod.console_print_ex(temp_con, 14, y, libtcod.BKGND_NONE, libtcod.CENTER,
				line)
			y += 1
		
		# FUTURE: display start and end dates of player's campaign
		
		# FUTURE: display outcome for player character
		
		# display decoration if any
		if self.decoration != '':
			libtcod.console_set_default_foreground(temp_con, libtcod.yellow)
			libtcod.console_print_ex(temp_con, 14, 6, libtcod.BKGND_NONE, libtcod.CENTER,
				self.decoration)
		
		# total VP
		libtcod.console_set_default_foreground(temp_con, libtcod.white)
		libtcod.console_print_ex(temp_con, 14, 11, libtcod.BKGND_NONE, libtcod.CENTER,
			'Total VP Earned:')
		libtcod.console_print_ex(temp_con, 14, 13, libtcod.BKGND_NONE, libtcod.CENTER,
			str(self.player_vp))
		
		# campaign stats
		y = 17
		for text in RECORD_LIST:
			libtcod.console_print(temp_con, 2, y, text + ':')
			libtcod.console_print_ex(temp_con, 26, y, libtcod.BKGND_NONE, libtcod.RIGHT,
				str(self.records[text]))
			y += 1
			if y == 49:
				break
			
		libtcod.console_set_default_foreground(temp_con, ACTION_KEY_COL)
		libtcod.console_print(temp_con, 7, 51, 'Enter')
		libtcod.console_set_default_foreground(temp_con, libtcod.light_grey)
		libtcod.console_print(temp_con, 14, 51, 'Continue')
		
		# display console to screen
		libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 31, 3)
		
		# get input from player
		exit_menu = False
		while not exit_menu:
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			if not GetInputEvent(): continue
			
			# end menu
			if key.vk in [libtcod.KEY_ESCAPE, libtcod.KEY_ENTER]:
				exit_menu = True
	
	
	#######################################
	#     Campaign Calendar Interface     #
	#######################################
	
	# update the day outline console, 24x22
	def UpdateDayOutlineCon(self):
		libtcod.console_clear(day_outline)
		
		libtcod.console_set_default_foreground(day_outline, PORTRAIT_BG_COL)
		lines = wrap(campaign.stats['name'], 20)
		y = 1
		for line in lines[:2]:
			libtcod.console_print_ex(day_outline, 12, y, libtcod.BKGND_NONE,
				libtcod.CENTER, line)
			y += 1
		
		libtcod.console_set_default_foreground(day_outline, libtcod.light_grey)
		libtcod.console_print_ex(day_outline, 11, 4, libtcod.BKGND_NONE, libtcod.CENTER,
			GetDateText(campaign.today))
		
		lines = wrap(campaign.current_week['week_description'], 20)
		y = 6
		for line in lines:
			libtcod.console_print_ex(day_outline, 12, y, libtcod.BKGND_NONE,
				libtcod.CENTER, line)
			y += 1
			if y == 17: break
		
		libtcod.console_set_default_foreground(day_outline, libtcod.light_grey)
		libtcod.console_print(day_outline, 1, 19, 'Start of Day:')
		libtcod.console_print(day_outline, 3, 20, 'End of Day:')
		
		libtcod.console_set_default_foreground(day_outline, libtcod.white)
		libtcod.console_print_ex(day_outline, 19, 19, libtcod.BKGND_NONE, libtcod.RIGHT,
			campaign.current_week['day_start'])
		libtcod.console_print_ex(day_outline, 19, 20, libtcod.BKGND_NONE, libtcod.RIGHT,
			campaign.current_week['day_end'])
	
	
	# update the command menu for the campaign calendar interface, 24x21
	def UpdateCalendarCmdCon(self):
		libtcod.console_clear(calendar_cmd_con)
		
		libtcod.console_set_default_foreground(calendar_cmd_con, TITLE_COL)
		libtcod.console_print(calendar_cmd_con, 6, 0, 'Command Menu')
		libtcod.console_set_default_foreground(calendar_cmd_con, libtcod.light_grey)
		libtcod.console_print(calendar_cmd_con, 0, 19, 'Use highlighted keys')
		libtcod.console_print(calendar_cmd_con, 0, 20, 'to navigate interface')
		
		x = 0
		for (text, num, col) in CC_MENU_LIST:
			libtcod.console_set_default_background(calendar_cmd_con, col)
			libtcod.console_rect(calendar_cmd_con, x, 1, 2, 1, True, libtcod.BKGND_SET)
			
			# display menu activation key, use darker bg colour for visibility
			col2 = col * libtcod.light_grey
			libtcod.console_put_char_ex(calendar_cmd_con, x, 1, str(num), ACTION_KEY_COL, col2)
			x += 2
			
			# display menu text if active
			if self.active_calendar_menu == num:
				libtcod.console_rect(calendar_cmd_con, x, 1, len(text)+2, 1,
					True, libtcod.BKGND_SET)
				libtcod.console_set_default_foreground(calendar_cmd_con, libtcod.white)
				libtcod.console_print(calendar_cmd_con, x, 1, text)
				x += len(text) + 2
		
		# fill in rest of menu line with final colour
		libtcod.console_rect(calendar_cmd_con, x, 1, 25-x, 1, True, libtcod.BKGND_SET)
		libtcod.console_set_default_background(calendar_cmd_con, libtcod.black)
		
		# proceed - start day or continue to next day, summary of expected day
		if self.active_calendar_menu == 1:
			
			libtcod.console_set_default_foreground(calendar_cmd_con, ACTION_KEY_COL)
			if DEBUG:
				libtcod.console_print(calendar_cmd_con, 4, 9, 'S')
			libtcod.console_print(calendar_cmd_con, 4, 10, 'Enter')
			
			libtcod.console_set_default_foreground(calendar_cmd_con, libtcod.light_grey)
			if DEBUG:
				libtcod.console_print(calendar_cmd_con, 11, 9, 'Skip Day')
			
			# day has not yet started
			if not campaign_day.started:
				libtcod.console_print(calendar_cmd_con, 11, 10, 'Start Day')
			
			# day has finished
			else:
				libtcod.console_print(calendar_cmd_con, 11, 10, 'Next Day')
		
		# crew and tank menu
		elif self.active_calendar_menu == 2:
			
			libtcod.console_set_default_foreground(calendar_cmd_con, ACTION_KEY_COL)
			libtcod.console_print(calendar_cmd_con, 1, 4, EnKey('w').upper() + '/' + EnKey('s').upper())
			libtcod.console_print(calendar_cmd_con, 1, 5, EnKey('f').upper())
			libtcod.console_print(calendar_cmd_con, 1, 6, 'N')
			
			libtcod.console_set_default_foreground(calendar_cmd_con, libtcod.light_grey)
			libtcod.console_print(calendar_cmd_con, 5, 4, 'Select Position')
			libtcod.console_print(calendar_cmd_con, 5, 5, 'Crewman Menu')
			libtcod.console_print(calendar_cmd_con, 5, 6, 'Crewman Nickname')
			
			if campaign.player_unit.unit_name == '':
				libtcod.console_set_default_foreground(calendar_cmd_con, ACTION_KEY_COL)
				libtcod.console_print(calendar_cmd_con, 1, 7, 'T')
				libtcod.console_set_default_foreground(calendar_cmd_con, libtcod.light_grey)
				libtcod.console_print(calendar_cmd_con, 5, 7, 'Tank Name')
		
		# tank
		elif self.active_calendar_menu == 3:
			pass
		
		# group - not yet implemented
		elif self.active_calendar_menu == 4:
			pass
	
	
	# update the main calendar display panel
	def UpdateCCMainPanel(self, selected_position):
		libtcod.console_clear(calendar_main_panel)
		
		# proceed menu - show summary of expected day
		if self.active_calendar_menu == 1:
			
			# day has finished
			if campaign_day.ended:
				return
			
			x = 15
			y = 1
			
			# display outline
			libtcod.console_set_default_foreground(calendar_main_panel, libtcod.white)
			
			# mission type and description
			libtcod.console_print_ex(calendar_main_panel, x+15, y, libtcod.BKGND_NONE,
				libtcod.CENTER,	"Today's Mission")
			libtcod.console_set_default_foreground(calendar_main_panel, libtcod.light_blue)
			libtcod.console_print_ex(calendar_main_panel, x+15, y+2, libtcod.BKGND_NONE,
				libtcod.CENTER,	campaign_day.mission)
			
			libtcod.console_set_default_foreground(calendar_main_panel, libtcod.light_grey)
			lines = wrap(MISSION_DESC[campaign_day.mission], 30)
			y1 = y+4
			for line in lines:
				libtcod.console_print(calendar_main_panel, x, y1, line)
				y1+=1
				if y1 == y+13: break
			
			# player support
			libtcod.console_set_default_foreground(calendar_main_panel, libtcod.white)
			libtcod.console_print(calendar_main_panel, x, y+15, 'Air Support:')
			libtcod.console_print(calendar_main_panel, x, y+16, 'Artillery Support:')
			
			libtcod.console_set_default_foreground(calendar_main_panel, libtcod.light_grey)
			if 'air_support_level' not in campaign.current_week:
				text = 'None'
			else:
				text = str(campaign.current_week['air_support_level'])
			libtcod.console_print(calendar_main_panel, x+19, y+15, text)
			if 'arty_support_level' not in campaign.current_week:
				text = 'None'
			else:
				text = str(campaign.current_week['arty_support_level'])
			libtcod.console_print(calendar_main_panel, x+19, y+16, text)
			
			# expected enemy forces
			libtcod.console_set_default_foreground(calendar_main_panel, libtcod.white)
			libtcod.console_print_ex(calendar_main_panel, x+10, y+19, libtcod.BKGND_NONE,
				libtcod.CENTER,	'Expected Enemy Forces')
			libtcod.console_set_default_foreground(calendar_main_panel, libtcod.light_grey)
			
			text = session.nations[campaign.current_week['enemy_nation']]['adjective']
			text += ' infantry, guns, and AFVs'
			lines = wrap(text, 30)
			y1 = y+21
			for line in lines:
				libtcod.console_print(calendar_main_panel, x, y1, line)
				y1+=1
				if y1 == y+24: break
		
		# crew and tank menu
		elif self.active_calendar_menu == 2:
			
			# show list of crewmen
			libtcod.console_set_default_foreground(calendar_main_panel, TITLE_COL)
			libtcod.console_print(calendar_main_panel, 3, 5, 'Tank Positions and Crewmen')
			libtcod.console_print(calendar_main_panel, 41, 5, 'Player Tank')
			
			DisplayCrew(campaign.player_unit, calendar_main_panel, 4, 8, selected_position)
			
			# show info on player tank if still alive
			if campaign.player_unit.alive:
				campaign.player_unit.DisplayMyInfo(calendar_main_panel, 34, 8, status=False)
				
				# description of tank
				text = ''
				for t in campaign.player_unit.GetStat('description'):
					text += t
				lines = wrap(text, 27)
				y = 24
				libtcod.console_set_default_foreground(calendar_main_panel, libtcod.light_grey)
				for line in lines[:20]:
					libtcod.console_print(calendar_main_panel, 33, y, line)
					y+=1
			
			else:
				libtcod.console_print(calendar_main_panel, 41, 8, 'None')
	
	
	# update the display of the campaign calendar interface
	def UpdateCCDisplay(self):
		
		libtcod.console_blit(calendar_bkg, 0, 0, 0, 0, con, 0, 0)		# background frame
		libtcod.console_blit(day_outline, 0, 0, 0, 0, con, 1, 15)		# summary of current day
		libtcod.console_blit(calendar_cmd_con, 0, 0, 0, 0, con, 1, 38)		# command menu
		libtcod.console_blit(calendar_main_panel, 0, 0, 0, 0, con, 26, 15)	# main panel
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		
	
	# main campaign calendar loop
	def DoCampaignCalendarLoop(self):
		
		def ProceedToNextDay():
			# set today to next day in calendar, and update enemy unit odds data
			self.today = self.combat_calendar[day_index+1]
			
			# check for start of new week
			week_index = campaign.stats['calendar_weeks'].index(campaign.current_week)
			if week_index < len(campaign.stats['calendar_weeks']) - 1:
				week_index += 1
				if self.today >= campaign.stats['calendar_weeks'][week_index]['start_date']:
					campaign.current_week = campaign.stats['calendar_weeks'][week_index]
					
					# check for modified class spawn odds
					if 'enemy_class_odds_modifier' in campaign.current_week:
						for k, v in campaign.current_week['enemy_class_odds_modifier'].items():
							if k in campaign.stats['enemy_unit_class_odds']:
								campaign.stats['enemy_unit_class_odds'][k] = v
		
		
		# consoles for campaign calendar interface
		global calendar_bkg, day_outline, calendar_cmd_con, calendar_main_panel
		global campaign_day
		
		# selected crew position
		selected_position = 0
		
		# create consoles
		calendar_bkg = LoadXP('calendar_bkg.xp')
		day_outline = NewConsole(24, 22, libtcod.black, libtcod.white)
		calendar_cmd_con = NewConsole(24, 21, libtcod.black, libtcod.white)
		calendar_main_panel = NewConsole(63, 44, libtcod.black, libtcod.white)
		
		# generate consoles for the first time
		self.UpdateDayOutlineCon()
		self.UpdateCalendarCmdCon()
		self.UpdateCCMainPanel(selected_position)
		
		if not (campaign_day.started and not campaign_day.ended):
			self.UpdateCCDisplay()
		
		SaveGame()
		
		exit_loop = False
		while not exit_loop:
			
			# if we've initiated a campaign day or are resuming a saved game with a
			# campaign day running, go into the campaign day loop now
			if campaign_day.started and not campaign_day.ended:
							
				campaign_day.DoCampaignDayLoop()
				
				# player was taken out
				if campaign.ended:
					self.LogDayRecords()
					self.DoEnd()
					exit_loop = True
					continue
				
				if session.exiting:
					exit_loop = True
					continue
				
				# redraw the screen
				self.UpdateDayOutlineCon()
				self.UpdateCalendarCmdCon()
				self.UpdateCCMainPanel(selected_position)
				self.UpdateCCDisplay()
				
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			keypress = GetInputEvent()	
			if not keypress: continue
			
			# game menu
			if key.vk == libtcod.KEY_ESCAPE:
				ShowGameMenu()
				if session.exiting:
					exit_loop = True
					continue
			
			# debug menu
			elif key.vk == libtcod.KEY_F2:
				if not DEBUG: continue
				ShowDebugMenu()
				continue
			
			# mapped key commands
			key_char = DeKey(chr(key.c).lower())
			
			# switch active menu
			if key_char in ['1', '2', '3']:
				if self.active_calendar_menu != int(key_char):
					self.active_calendar_menu = int(key_char)
					self.UpdateCalendarCmdCon()
					self.UpdateCCMainPanel(selected_position)
					self.UpdateCCDisplay()
				continue
			
			# proceed menu active
			if self.active_calendar_menu == 1:
				
				# debug - skip day
				if chr(key.c).lower() == 's':
					campaign_day.started = True
					campaign_day.ended = True
					self.UpdateCalendarCmdCon()
					self.UpdateCCMainPanel(selected_position)
					self.UpdateCCDisplay()
					continue
				
				# start or proceed to next day
				if key.vk == libtcod.KEY_ENTER:
				
					# start new day
					if not campaign_day.ended:
						campaign_day.AmmoReloadMenu()	# allow player to load ammo
						campaign_day.started = True
						continue			# continue in loop to go into campaign day layer
				
					# proceed to next day or end campaign
					else:
						
						# do end-of-day stuff
						self.ShowEndOfDay()
						
						# add day records to campaign log
						self.LogDayRecords()
						
						# check for end of campaign as a result of reaching end of calendar
						day_index = campaign.combat_calendar.index(campaign.today)
						if day_index == len(campaign.combat_calendar) - 1:
							self.DoEnd()
							exit_loop = True
							continue
						
						ProceedToNextDay()
						
						# if player tank was destroyed, allow player to choose a new one
						if not self.player_unit.alive:
							self.ReplacePlayerTank()
						
						# create a new campaign day
						campaign_day = CampaignDay()
						campaign_day.GenerateRoads()
						campaign_day.GenerateRivers()
						
						# show new day starting animation
						self.ShowStartOfDay()	
						
						# handle refitting weeks here
						if 'refitting' in campaign.current_week:
							
							# allow player to change tanks
							if ShowNotification('Your battlegroup has been recalled for refitting. Do you want to request a new tank?', confirm=True):
								self.ReplacePlayerTank()
							
							# proceed to next combat day
							ProceedToNextDay()
							campaign_day = CampaignDay()
							campaign_day.GenerateRoads()
							campaign_day.GenerateRivers()
							self.ShowStartOfDay()
						
						# redraw the screen
						self.UpdateDayOutlineCon()
						self.UpdateCalendarCmdCon()
						self.UpdateCCMainPanel(selected_position)
						self.UpdateCCDisplay()
						continue
					
			
			# crew menu active
			elif self.active_calendar_menu == 2:
				
				# select different crew position
				if key_char in ['w', 's']:
					if key_char == 'w':
						selected_position -= 1
						if selected_position < 0:
							selected_position = len(campaign.player_unit.positions_list) - 1
				
					else:
						selected_position += 1
						if selected_position == len(campaign.player_unit.positions_list):
							selected_position = 0
				
					self.UpdateCCMainPanel(selected_position)
					self.UpdateCCDisplay()
					continue
				
				# open crewman menu
				elif key_char == 'f':
					crewman = campaign.player_unit.positions_list[selected_position].crewman
					if crewman is None: continue
					crewman.ShowCrewmanMenu()
					self.UpdateCCDisplay()
					continue
				
				# set nickname (not keymapped)
				elif chr(key.c).lower() == 'n':
					crewman = campaign.player_unit.positions_list[selected_position].crewman
					if crewman is None: continue
					if crewman.nickname != '': continue
					new_nickname = ShowTextInputMenu('Enter a nickname; cannot be changed once set!',
						'', MAX_NICKNAME_LENGTH, [])
					if new_nickname != '':
						crewman.nickname = new_nickname
					self.UpdateCCMainPanel(selected_position)
					self.UpdateCCDisplay()
					continue
				
				# set tank nickname (not keymapped)
				elif chr(key.c).lower() == 't':
					if campaign.player_unit.unit_name != '': continue
					player_tank_name = ShowTextInputMenu('Enter a name for your tank', '', MAX_TANK_NAME_LENGTH, [])
					if player_tank_name != '':
						campaign.player_unit.unit_name = player_tank_name
					self.UpdateCCMainPanel(selected_position)
					self.UpdateCCDisplay()
					continue


# Campaign Day: represents one calendar day in a campaign with a 5x7 map of terrain hexes, each of
# which may spawn a Scenario
class CampaignDay:
	def __init__(self):
		
		# campaign day records
		self.records = {}
		for text in RECORD_LIST:
			self.records[text] = 0
		
		self.started = False				# day is in progress
		self.ended = False				# day has been completed
		self.mission = ''
		self.GenerateMission()				# roll for type of mission today
		
		self.travel_time_spent = False
		
		# current weather conditions, will be set by GenerateWeather
		self.weather = {
			'Cloud Cover' : '',
			'Precipitation' : '',
			'Fog' : 0,
			'Ground' : '',
			'Freezing' : False
		}
		self.weather_update_clock = 0		# number of minutes until next weather update
		self.GenerateWeather()
		
		self.fate_points = libtcod.random_get_int(0, 1, 2)	# fate points protecting the player
		
		# set max number of units in player squad
		player_unit_class = campaign.player_unit.GetStat('class')
		if player_unit_class == 'Tankette':
			campaign.player_squad_max = 4
		elif player_unit_class == 'Light Tank':
			campaign.player_squad_max = 3
		elif player_unit_class == 'Medium Tank':
			campaign.player_squad_max = 2
		elif player_unit_class == 'Heavy Tank':
			campaign.player_squad_max = 1
		campaign.player_squad_num = campaign.player_squad_max
		
		# current hour, and minute: set initial time from campaign info
		self.day_clock = {}
		time_str = campaign.current_week['day_start'].split(':')
		self.day_clock['hour'] = int(time_str[0])
		self.day_clock['minute'] = int(time_str[1])
		
		# end of day
		self.end_of_day = {}
		time_str = campaign.current_week['day_end'].split(':')
		self.end_of_day['hour'] = int(time_str[0])
		self.end_of_day['minute'] = int(time_str[1])
		
		# combat day length in minutes
		hours = self.end_of_day['hour'] - self.day_clock['hour']
		minutes = self.end_of_day['minute'] - self.day_clock['minute']
		if minutes < 0:
			hours -= 1
			minutes += 60
		self.day_length = minutes + (hours * 60)
		
		# current odds of a random event being triggered
		self.random_event_chance = BASE_CD_RANDOM_EVENT_CHANCE
		
		# generate campaign day map
		self.map_hexes = {}
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			self.map_hexes[(hx,hy)] = CDMapHex(hx, hy, self.mission)
			# set zone terrain type
			self.map_hexes[(hx,hy)].GenerateTerrainType()
		
		# set up initial zone control based on day mission
		if self.mission == 'Fighting Withdrawl':
			for (hx, hy) in CAMPAIGN_DAY_HEXES:
				self.map_hexes[(hx, hy)].controlled_by = 0
		elif self.mission == 'Counterattack':
			for (hx, hy) in CAMPAIGN_DAY_HEXES:
				self.map_hexes[(hx, hy)].controlled_by = 0
			hy = 0
			hx1 = 0 - floor(hy / 2)
			for hx in range(hx1, hx1 + 5):
				if (hx, hy) not in self.map_hexes: continue
				self.map_hexes[(hx, hy)].controlled_by = 1
		elif self.mission == 'Battle':
			for (hx, hy) in CAMPAIGN_DAY_HEXES:
				self.map_hexes[(hx, hy)].controlled_by = 1
			for hy in range(6, 9):
				hx1 = 0 - floor(hy / 2)
				for hx in range(hx1, hx1 + 5):
					if (hx, hy) not in self.map_hexes: continue
					self.map_hexes[(hx, hy)].controlled_by = 0
		
		# set up objectives
		self.GenerateObjectives()
		
		# dictionary of screen display locations on the display console
		self.cd_map_index = {}
		
		# set up initial player location
		if self.mission == 'Fighting Withdrawl':
			self.player_unit_location = (2, 0)	# top center of map
		elif self.mission == 'Battle':
			self.player_unit_location = (-1, 6)	# lower center of map
		elif self.mission == 'Counterattack':
			self.player_unit_location = (2, 1)	# second row of map
		else:
			self.player_unit_location = (-2, 8)	# bottom center of map
		
		self.active_menu = 3				# number of currently active command menu
		self.selected_position = 0			# selected crew position in crew command menu tab
		self.selected_direction = None			# select direction for support, travel, etc.
		self.abandoned_tank = False			# set to true if player abandoned their tank that day
		self.scenario = None				# currently active scenario in progress
		
		self.air_support_level = 0.0
		if 'air_support_level' in campaign.current_week:
			self.air_support_level = campaign.current_week['air_support_level']
		
		self.arty_support_level = 0.0
		if 'arty_support_level' in campaign.current_week:
			self.arty_support_level = campaign.current_week['arty_support_level']
		
		self.advancing_fire = False			# player is using advancing fire when moving
		self.air_support_request = False		# " requesting air support upon move
		self.arty_support_request = False		# " arty "
		
		self.encounter_mod = 0.0			# increases every time player caputures an area without resistance
		
		# set player location to player control
		self.map_hexes[self.player_unit_location].controlled_by = 0
		
		# animation object; keeps track of active animations on the animation console
		self.animation = {
			'rain_active' : False,
			'rain_drops' : [],
			'snow_active' : False,
			'snowflakes' : []
		}
	
	
	# generate new objectives for this campaign day map
	def GenerateObjectives(self):
		
		hex_list = []
		
		# clear any existing objectives and create a local list of hex zones
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			self.map_hexes[(hx,hy)].objective = None
			hex_list.append((hx, hy))
		shuffle(hex_list)
		
		# create new objectives based on day mission
		if self.mission == 'Battle':
			
			objective_dict = {
				'objective_type' : 'Capture',
				'vp_reward' : 4,
				'time_limit' : None
				}
			
			for i in range(2):
				for (hx, hy) in hex_list:
					if self.map_hexes[(hx,hy)].controlled_by == 0: continue
				self.map_hexes[(hx, hy)].SetObjective(objective_dict)
		
		elif self.mission in ['Advance']:
			objective_dict = {
				'objective_type' : 'Capture',
				'vp_reward' : 2,
				'time_limit' : None
				}
			for i in range(2):
				for (hx, hy) in hex_list:
					if self.map_hexes[(hx,hy)].controlled_by == 0: continue
				self.map_hexes[(hx, hy)].SetObjective(objective_dict)
		
	
	# check for shift of campaign day map:
	# shift displayed map up or down, triggered by player reaching other end of map
	def CheckForCDMapShift(self):
		
		(player_hx, player_hy) = self.player_unit_location
		
		if self.mission in ['Fighting Withdrawl', 'Counterattack']:
			if player_hy != 8: return
		else:
			if player_hy != 0: return
		
		ShowMessage('You enter a new map region.')
		
		# determine direction to shift map based on current player location
		
		if player_hy == 8:
			shift_down = False
		elif player_hy == 0:
			shift_down = True
		else:
			return
		
		if shift_down:
			new_hy = 8
			hx_mod = -4
		else:
			new_hy = 0
			hx_mod = +4
		
		# copy terrain for current player row to new row
		for hx in range(player_hx-4, player_hx+5):
			if (hx, player_hy) not in CAMPAIGN_DAY_HEXES: continue
			self.map_hexes[(hx+hx_mod, new_hy)] = self.map_hexes[(hx, player_hy)]
			self.map_hexes[(hx+hx_mod, new_hy)].hx = hx+hx_mod
			self.map_hexes[(hx+hx_mod, new_hy)].hy = new_hy
			self.map_hexes[(hx+hx_mod, new_hy)].Reset()
		
		self.player_unit_location = (player_hx+hx_mod, new_hy)
		
		# generate new terrain for remainder of map
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			if hy == new_hy: continue
			self.map_hexes[(hx,hy)] = CDMapHex(hx, hy, self.mission)
			self.map_hexes[(hx,hy)].GenerateTerrainType()
	
		# set up zone control
		if self.mission == 'Fighting Withdrawl':
			for (hx, hy) in CAMPAIGN_DAY_HEXES:
				self.map_hexes[(hx, hy)].controlled_by = 0
		else:
			for (hx, hy) in CAMPAIGN_DAY_HEXES:
				self.map_hexes[(hx, hy)].controlled_by = 1
			self.map_hexes[self.player_unit_location].controlled_by = 0
		
		# generate new map objectives
		self.GenerateObjectives()
		
		# update consoles
		self.UpdateCDMapCon()
		self.UpdateCDGUICon()
		self.UpdateCDPlayerUnitCon()
		
		SaveGame()
		
		
	# roll for type of mission for today
	def GenerateMission(self):
		
		roll = GetPercentileRoll()
		
		for k, v in campaign.current_week['mission_odds'].items():
			if roll <= float(v):
				self.mission = k
				return
			roll -= float(v)
		
		print('ERROR: unable to set a mission for today, choosing default')
		for k, v in self.current_week['mission_odds'].items():
			self.mission = k
			return
		
	
	# calculate required tarvel time in minutes from one zone to another
	def CalculateTravelTime(self, hx1, hy1, hx2, hy2):
		
		# check for river block
		direction = self.GetDirectionToAdjacentCD(hx1, hy1, hx2, hy2)
		if direction in self.map_hexes[(hx1,hy1)].rivers:
			if direction not in self.map_hexes[(hx1,hy1)].bridges:
				return -1
		direction2 = self.GetDirectionToAdjacentCD(hx2, hy2, hx1, hy1)
		if direction2 in self.map_hexes[(hx2,hy2)].rivers:
			if direction2 not in self.map_hexes[(hx2,hy2)].bridges:
				return -1
		
		# check for road link
		
		if direction in self.map_hexes[(hx1,hy1)].dirt_roads:
			mins = 30
		else:
			if self.map_hexes[(hx2,hy2)].terrain_type == 'Forest':
				mins = 60
			else:
				mins = 45
		
		# check ground conditions
		if self.weather['Ground'] == 'Deep Snow':
			mins += 25
		elif self.weather['Ground'] in ['Muddy', 'Snow']:
			mins += 15
		elif self.weather['Precipitation'] != 'None':
			mins += 10
		
		# check for active support request flag(s) when moving into enemy zone
		if self.map_hexes[(hx2,hy2)].controlled_by == 1:
			if self.arty_support_request:
				mins += 15
			if self.air_support_request:
				mins += 10
		
		return mins
		
	
	# increments one of the combat day records, also increments campaign record
	def AddRecord(self, name, i):
		self.records[name] += i
		campaign.records[name] += i
	
	
	# generate a new random set of initial weather conditions, should only be called when day is created
	def GenerateWeather(self):
		
		# determine current calendar season
		weather_odds_dict = REGIONS[campaign.stats['region']]['season_weather_odds']
		date = campaign.today[campaign.today.find('.') + 1:]
		
		for season, value in weather_odds_dict.items():
			if date <= value['end_date']:
				break
		else:
			# catch cases where date is late in the calendar year
			season = 'Winter'
		
		weather_odds = weather_odds_dict[season]
		
		# roll for ground cover first
		roll = GetPercentileRoll()
		for result, chance in weather_odds['ground_conditions'].items():
			if roll <= chance:
				break
			roll -= chance
		
		self.weather['Ground'] = result
		
		if result in ['Snow', 'Deep Snow']:
			self.weather['Freezing'] = True
		# even if ground conditions are dry, chance that snow might fall later
		elif result == 'Dry':
			if GetPercentileRoll() <= weather_odds['freezing']:
				self.weather['Freezing'] = True

		# roll for cloud cover
		roll = GetPercentileRoll()
		for result, chance in weather_odds['cloud_cover'].items():
			if roll <= chance:
				break
			roll -= chance
		self.weather['Cloud Cover'] = result
		
		# roll for precipitation
		roll = GetPercentileRoll()
		for result, chance in weather_odds['precipitation'].items():
			
			# only allow snow if weather is cold
			if not self.weather['Freezing'] and result in ['Light Snow', 'Snow', 'Blizzard']:
				roll -= chance
				continue
			
			# only allow rain if weather is warm
			if self.weather['Freezing'] and result in ['Rain', 'Heavy Rain']:
				roll -= chance
				continue
			
			if roll <= chance:
				self.weather['Precipitation'] = result
				break
			roll -= chance
		else:
			self.weather['Precipitation'] = 'None'
		
		
		# if precipitation has been rolled, fix clear cloud cover
		if self.weather['Precipitation'] != 'None' and self.weather['Cloud Cover'] == 'Clear':
			self.weather['Cloud Cover'] = choice(['Scattered', 'Heavy', 'Overcast'])
		
		# FUTURE fog level: 0-3
		
		# set first weather update countdown
		self.weather_update_clock = BASE_WEATHER_UPDATE_CLOCK + (libtcod.random_get_int(0, 1, 16))
	
	
	# update weather conditions, possibly changing them
	def UpdateWeather(self):
		
		# reset update clock
		self.weather_update_clock = BASE_WEATHER_UPDATE_CLOCK + (libtcod.random_get_int(0, 1, 16))
		
		# check for ground condition update
		roll = GetPercentileRoll()
		
		# muddy ground drying out
		if self.weather['Ground'] == 'Muddy':
			if self.weather['Precipitation'] == 'None':
				if roll <= GROUND_CONDITION_CHANGE_CHANCE:
					self.weather['Ground'] = 'Wet'
					ShowMessage('The muddy ground has dried out a little.')
		
		# wet ground drying out
		elif self.weather['Ground'] == 'Wet':
			if self.weather['Precipitation'] == 'None':
				if roll <= GROUND_CONDITION_CHANGE_CHANCE:
					self.weather['Ground'] = 'Dry'
					ShowMessage('The ground has completely dried out.')
			
			elif self.weather['Precipitation'] in ['Rain', 'Heavy Rain']:
				
				if self.weather['Precipitation'] == 'Heavy Rain':
					roll -= HEAVY_PRECEP_MOD
				if roll <= GROUND_CONDITION_CHANGE_CHANCE:
					self.weather['Ground'] = 'Muddy'
					ShowMessage('The ground has become muddy.')
		
		# snowy ground deepening
		elif self.weather['Ground'] == 'Snow':
			if self.weather['Precipitation'] in ['Snow', 'Blizzard']:
				if self.weather['Precipitation'] == 'Blizzard':
					roll -= HEAVY_PRECEP_MOD
				if roll <= GROUND_CONDITION_CHANGE_CHANCE:
					self.weather['Ground'] = 'Deep Snow'
					ShowMessage('The snow has accumilated and is now deep.')
		
		# dry ground - can get wet or snowy
		else:
			
			if self.weather['Precipitation'] in ['Rain', 'Heavy Rain']:
				if self.weather['Precipitation'] == 'Heavy Rain':
					roll -= HEAVY_PRECEP_MOD
				if roll <= GROUND_CONDITION_CHANGE_CHANCE:
					self.weather['Ground'] = 'Wet'
					ShowMessage('The ground has become wet.')
			
			elif self.weather['Precipitation'] in ['Snow', 'Blizzard']:
				if self.weather['Precipitation'] == 'Blizzard':
					roll -= HEAVY_PRECEP_MOD
				if roll <= GROUND_CONDITION_CHANGE_CHANCE:
					self.weather['Ground'] = 'Snow'
					ShowMessage('The ground is now covered in snow.')
					
					# update map consoles to reflect new ground cover
					campaign_day.UpdateCDMapCon()
					if scenario is not None:
						scenario.UpdateHexmapCon()
		
		
		# roll to see weather change takes place
		if GetPercentileRoll() > 15.0: return
		
		# roll for possible type of weather change
		roll = GetPercentileRoll()
			
		# change in precipitation level
		if roll <= 70.0:
			
			# no change possible
			if self.weather['Cloud Cover'] == 'Clear':
				return
			
			roll = GetPercentileRoll()
			
			if self.weather['Precipitation'] == 'None':
				
				if self.weather['Freezing']:
					if roll <= 80.0:
						self.weather['Precipitation'] = 'Light Snow'
						ShowMessage('Light snow begins to fall.')
					else:
						self.weather['Precipitation'] = 'Snow'
						ShowMessage('Snow begins to fall.')
				else:
				
					if roll <= 50.0:
						self.weather['Precipitation'] = 'Mist'
						ShowMessage('A light mist begins to fall.')
					elif roll <= 85.0:
						self.weather['Precipitation'] = 'Rain'
						ShowMessage('Rain begins to fall.')
					else:
						self.weather['Precipitation'] = 'Heavy Rain'
						ShowMessage('A heavy downpour suddenly begins to fall.')
			
			elif self.weather['Precipitation'] == 'Mist':
				if roll <= 40.0:
					self.weather['Precipitation'] = 'None'
					ShowMessage('The light mist has cleared up.')
				elif roll <= 80.0:
					self.weather['Precipitation'] = 'Rain'
					ShowMessage('The light mist thickens into a steady rain.')
				else:
					self.weather['Precipitation'] = 'Heavy Rain'
					ShowMessage('The light mist suddenly turns into a heavy downpour.')
			
			elif self.weather['Precipitation'] == 'Rain':
				if roll <= 30.0:
					self.weather['Precipitation'] = 'None'
					ShowMessage('The rain has cleared up.')
				elif roll <= 80.0:
					self.weather['Precipitation'] = 'Mist'
					ShowMessage('The rain turns into a light mist.')
				else:
					self.weather['Precipitation'] = 'Heavy Rain'
					ShowMessage('The rain gets heavier.')
			
			elif self.weather['Precipitation'] == 'Heavy Rain':
				if roll <= 35.0:
					self.weather['Precipitation'] = 'Mist'
					ShowMessage('The rain turns into a light mist.')
				else:
					self.weather['Precipitation'] = 'Rain'
					ShowMessage('The rain lightens a little.')

			elif self.weather['Precipitation'] == 'Light Snow':
				if roll <= 30.0:
					self.weather['Precipitation'] = 'None'
					ShowMessage('The snow stops falling.')
				elif roll <= 80.0:
					self.weather['Precipitation'] = 'Snow'
					ShowMessage('The snow gets a little heavier.')
				else:
					self.weather['Precipitation'] = 'Blizzard'
					ShowMessage('The snow starts falling very heavily.')
			
			elif self.weather['Precipitation'] == 'Snow':
				if roll <= 20.0:
					self.weather['Precipitation'] = 'None'
					ShowMessage('The snow stops falling.')
				elif roll <= 80.0:
					self.weather['Precipitation'] = 'Light Snow'
					ShowMessage('The snow gets a little lighter.')
				else:
					self.weather['Precipitation'] = 'Blizzard'
					ShowMessage('The snow starts falling very heavily.')
			
			elif self.weather['Precipitation'] == 'Blizzard':
				if roll <= 20.0:
					self.weather['Precipitation'] = 'Light Snow'
					ShowMessage('The snow gets quite a bit lighter.')
				else:
					self.weather['Precipitation'] = 'Snow'
					ShowMessage('The snow gets a bit lighter.')
			
			# update animations
			self.InitAnimations()
			if scenario is not None:
				scenario.InitAnimations()
		
		# FUTURE: change in fog level
		#elif roll <= 75.0:
		#	return False
		
		# change in cloud level
		else:
			
			roll = GetPercentileRoll()
			
			if self.weather['Cloud Cover'] == 'Clear':
				if roll <= 85.0:
					self.weather['Cloud Cover'] = 'Scattered'
					ShowMessage('Scattered clouds begin to form.')
				else:
					self.weather['Cloud Cover'] = 'Heavy'
					ShowMessage('A heavy cloud front rolls in.')
			
			elif self.weather['Cloud Cover'] == 'Scattered':
				if roll <= 75.0:
					self.weather['Cloud Cover'] = 'Clear'
					ShowMessage('The clouds part and the sky is clear.')
				elif roll <= 90.0:
					self.weather['Cloud Cover'] = 'Heavy'
					ShowMessage('The cloud cover gets thicker.')
				else:
					self.weather['Cloud Cover'] = 'Overcast'
					ShowMessage('A storm front has rolled in.')
			
			elif self.weather['Cloud Cover'] == 'Heavy':
				if roll <= 85.0:
					self.weather['Cloud Cover'] = 'Scattered'
					ShowMessage('The clouds begin to thin out.')
				else:
					self.weather['Cloud Cover'] = 'Overcast'
					ShowMessage('The cloud cover thickens.')
			
			# overcast
			else:
				self.weather['Cloud Cover'] = 'Heavy'
				ShowMessage('The cloud cover begins to thin out but remains heavy.')

			# stop any precipitation if clouds have cleared up
			if self.weather['Cloud Cover'] == 'Clear' and self.weather['Precipitation'] != 'None':
				self.weather['Precipitation'] = 'None'
				
				# stop animation
				self.InitAnimations()
				if scenario is not None:
					scenario.InitAnimations()

	
	# advance the current campaign day time, check for end of day, and also weather conditions update
	def AdvanceClock(self, hours, minutes, skip_checks=False):
		self.day_clock['hour'] += hours
		self.day_clock['minute'] += minutes
		while self.day_clock['minute'] >= 60:
			self.day_clock['hour'] += 1
			self.day_clock['minute'] -= 60
		
		if skip_checks: return
		
		self.CheckForEndOfDay()
		
		# check for weather update
		self.weather_update_clock -= hours * 60
		self.weather_update_clock -= minutes
		if self.weather_update_clock <= 0:
			# check for weather conditions change, update relevant consoles
			self.UpdateWeather()
			self.UpdateCDCommandCon()
			DisplayWeatherInfo(cd_weather_con)
			if scenario is not None:
				if scenario.init_complete:
					scenario.UpdateScenarioInfoCon()
		
	
	# sets flag if we've met or exceeded the set length of the combat day
	def CheckForEndOfDay(self):
		if self.day_clock['hour'] > self.end_of_day['hour']:
			self.ended = True
		if self.day_clock['hour'] == self.end_of_day['hour']:
			if self.day_clock['minute'] >= self.end_of_day['minute']:
				self.ended = True
	
	
	# roll for trigger of random Campaign Day event
	def CheckForRandomEvent(self):
		
		# don't trigger an event if day has already ended
		if self.ended: return
		
		# don't trigger if a scenario just started
		if scenario is not None: return
		
		roll = GetPercentileRoll()
		
		if DEBUG:
			if session.debug['Always CD Random Event']:
				roll = 1.0
		
		# no event this time, increase chance for next time
		if roll > self.random_event_chance:
			self.random_event_chance += 2.0
			return
		
		# reset random event chance
		self.random_event_chance = BASE_CD_RANDOM_EVENT_CHANCE
		
		# roll for type of event
		roll = GetPercentileRoll()
		
		# enemy strength increases
		if roll <= 15.0:
			hex_list = []
			for (hx, hy) in self.map_hexes:
				if self.map_hexes[(hx,hy)].controlled_by == 0: continue
				hex_list.append((hx, hy))
			
			if len(hex_list) == 0:
				return
			
			(hx, hy) = choice(hex_list)
			map_hex = self.map_hexes[(hx,hy)]
			
			map_hex.enemy_strength += libtcod.random_get_int(0, 1, 3)
			if map_hex.enemy_strength > 10:
				map_hex.enemy_strength = 10
			
			# don't show anything if zone not known to player
			if not map_hex.known_to_player: return
			
			ShowMessage('We have reports of an increase of enemy strength in a zone!')
			# FUTURE: highlight hex momentarily
		
		# reveal enemy strength
		elif roll <= 35.0:
			
			hex_list = []
			for (hx, hy) in self.map_hexes:
				if self.map_hexes[(hx,hy)].controlled_by == 0: continue
				if self.map_hexes[(hx,hy)].known_to_player: continue
				hex_list.append((hx, hy))
			
			if len(hex_list) == 0:
				return
			
			(hx, hy) = choice(hex_list)
			self.map_hexes[(hx,hy)].known_to_player = True
			
			ShowMessage('We have received information about expected enemy strength in an area.')
			# FUTURE: highlight hex momentarily
		
		# free resupply
		elif roll <= 40.0:
			ShowMessage('You happen to encounter a supply truck, and can restock your gun ammo.')
			self.AmmoReloadMenu()
		
		# loss of recon knowledge and possible change in strength
		elif roll <= 70.0:
			
			hex_list = []
			for (hx, hy) in self.map_hexes:
				if self.map_hexes[(hx,hy)].controlled_by == 0: continue
				if not self.map_hexes[(hx,hy)].known_to_player: continue
				hex_list.append((hx, hy))
			
			if len(hex_list) == 0:
				return
			
			ShowMessage('Enemy movement reported in a map zone, estimated strength no longer certain.')
			
			(hx, hy) = choice(hex_list)
			map_hex = self.map_hexes[(hx,hy)]
			
			map_hex.known_to_player = False
			map_hex.enemy_strength -= 3
			map_hex.enemy_strength += libtcod.random_get_int(0, 0, 6)
			
			if map_hex.enemy_strength < 1:
				map_hex.enemy_strength = 1
			if map_hex.enemy_strength > 10:
				map_hex.enemy_strength = 10
		
		# increase current support level
		elif roll <= 75.0:
			
			text = 'Additional '
			
			if 'air_support_level' in campaign.current_week:
				text += 'air'
				self.air_support_level += (10.0 * float(libtcod.random_get_int(0, 1, 3)))
				# make sure does not go beyond initial level
				if self.air_support_level > campaign.current_week['air_support_level']:
					self.air_support_level = campaign.current_week['air_support_level']
			elif 'arty_support_level' in campaign.current_week:
				text += 'artillery'
				self.arty_support_level += (10.0 * float(libtcod.random_get_int(0, 1, 3)))
				if self.arty_support_level > campaign.current_week['arty_support_level']:
					self.arty_support_level = campaign.current_week['arty_support_level']
			else:
				return
			
			text += ' support has made available to you from Command.'
			ShowMessage(text)
		
		# no other random events for now
		else:
			pass
		
		# random event finished, update consoles and screen
		self.UpdateCDUnitCon()
		self.UpdateCDControlCon()
		self.UpdateCDGUICon()
		self.UpdateCDCommandCon()
		self.UpdateCDHexInfoCon()
		self.UpdateCDDisplay()
	
	
	# check for zone capture/loss
	# if zone_just_captured is True, then the player's own zone won't be selected as one that
	# the enemy captures
	def CheckForZoneCapture(self, zone_just_captured=False):
		
		global scenario
		
		# don't trigger an event if day has already ended
		if self.ended: return
		
		# set odds of each possible occurance based on current day mission
		
		enemy_max_capture = 1
		
		if campaign_day.mission == 'Advance':
			friendly_capture_odds = 45.0
			enemy_capture_odds = 5.0
		elif campaign_day.mission == 'Battle':
			friendly_capture_odds = 20.0
			enemy_capture_odds = 20.0
			enemy_max_capture = 2
		elif campaign_day.mission == 'Fighting Withdrawl':
			friendly_capture_odds = 3.0
			enemy_capture_odds = 85.0
			enemy_max_capture = 4
		elif campaign_day.mission == 'Counterattack':
			friendly_capture_odds = 5.0
			enemy_capture_odds = 80.0
			enemy_max_capture = 2
		# no other missions for now
		else:
			return
		
		roll = GetPercentileRoll()
		
		# friendly forces capture an enemy zone
		if roll <= friendly_capture_odds:
			
			# find a possible zone to capture
			hex_list = []
			for (hx, hy) in self.map_hexes:
				map_hex = self.map_hexes[(hx,hy)]
				if map_hex.controlled_by == 0: continue
				
				# automatically a candidate if in bottom hex row
				if hy == 8:
					hex_list.append((hx,hy))
					continue
				
				# make sure there is at least one adjacent friendly hex
				for direction in range(5):
					(hx2, hy2) = self.GetAdjacentCDHex(hx, hy, direction)
					if (hx2, hy2) not in self.map_hexes: continue
					if self.map_hexes[(hx2,hy2)].controlled_by == 0:
						hex_list.append((hx,hy))
						break
			
			# 1+ possible hexes to capture
			if len(hex_list) > 0:
				ShowMessage('Allied forces have captured an enemy-held zone!') 
				(hx, hy) = choice(hex_list)
				self.map_hexes[(hx,hy)].CaptureMe(0, no_vp=True)
		
		
		roll = GetPercentileRoll()
		
		(player_hx, player_hy) = self.player_unit_location
		
		# friendly zone lost - may be multiple
		if roll <= enemy_capture_odds:
			
			hex_list = []
			for (hx, hy) in self.map_hexes:
				map_hex = self.map_hexes[(hx,hy)]
				if map_hex.controlled_by == 1: continue
				
				# don't capture player's zone if they just took it
				if zone_just_captured:
					if hx == player_hx and hy == player_hy:
						continue
				
				# automatically a candidate if in top hex row
				if hy == 0:
					hex_list.append((hx,hy))
					continue
				
				# make sure there is at least one adjacent enemy hex
				for direction in range(5):
					(hx2, hy2) = self.GetAdjacentCDHex(hx, hy, direction)
					if (hx2, hy2) not in self.map_hexes: continue
					if self.map_hexes[(hx2,hy2)].controlled_by == 1:
						hex_list.append((hx,hy))
						break
			
			# 1+ possible hexes to capture
			if len(hex_list) > 0:
				
				capture_num = libtcod.random_get_int(0, 1, enemy_max_capture)
				if capture_num > len(hex_list):
					capture_list = hex_list.copy()
				else:
					capture_list = sample(hex_list, capture_num)
				
				# in FW mission, more likely that player zone is attacked
				#if campaign_day.mission == 'Fighting Withdrawl':
				#	if (hx, hy) != self.player_unit_location:
				#		(hx, hy) = choice(hex_list)
				
				for (hx, hy) in capture_list:
					self.map_hexes[(hx,hy)].CaptureMe(1)
				
				# player zone was captured
				if self.player_unit_location in capture_list:
					# player is present, trigger a scenario
					ShowMessage('Enemy forces attack your area!')
					map_hex = self.map_hexes[self.player_unit_location]
					scenario = Scenario(map_hex)
					self.scenario = scenario
					self.AddRecord('Battles Fought', 1)
				else:
					# player zone not captured
					if len(capture_list) > 1:
						ShowMessage('Enemy forces have captured allied-held zones!')
					else:
						ShowMessage('Enemy forces have captured an allied-held zone!')
	
		# update consoles and screen
		self.UpdateCDUnitCon()
		self.UpdateCDControlCon()
		self.UpdateCDGUICon()
		self.UpdateCDCommandCon()
		self.UpdateCDHexInfoCon()
		self.UpdateCDDisplay()
	
	
	# menu for restocking ammo for main guns on the player tank
	def AmmoReloadMenu(self):
		
		weapon = None
		ammo_num = 0
		rr_num = 0
		add_num = 1
		use_rr = False
		
		# update the menu console and draw to screen
		def UpdateMenuCon():
			
			libtcod.console_clear(con)
			
			# window title
			libtcod.console_set_default_background(con, libtcod.dark_blue)
			libtcod.console_rect(con, 0, 2, WINDOW_WIDTH, 5, True, libtcod.BKGND_SET)
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print_ex(con, WINDOW_XM, 4, libtcod.BKGND_NONE,
				libtcod.CENTER, 'Ammo Load')
			
			# player unit portrait
			x = 33
			y = 9
			libtcod.console_set_default_background(con, PORTRAIT_BG_COL)
			libtcod.console_rect(con, x, y, 25, 8, True, libtcod.BKGND_SET)
			portrait = campaign.player_unit.GetStat('portrait')
			if portrait is not None:
				libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, con, x, y)
			libtcod.console_set_default_foreground(con, libtcod.white)
			if campaign.player_unit.unit_name != '':
				libtcod.console_print(con, x, y, self.player_unit.unit_name)
			libtcod.console_set_default_background(con, libtcod.black)
			
			# command menu
			x = 58
			y = 35
			libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
			libtcod.console_print(con, x, y, EnKey('q').upper())
			libtcod.console_print(con, x, y+1, EnKey('e').upper())
			libtcod.console_print(con, x, y+2, EnKey('r').upper())
			
			libtcod.console_print(con, x, y+4, EnKey('d').upper())
			libtcod.console_print(con, x, y+5, EnKey('a').upper())
			
			libtcod.console_print(con, x, y+7, EnKey('z').upper())
			
			libtcod.console_print(con, x, y+9, EnKey('x').upper())
			
			libtcod.console_print(con, x, y+11, 'Enter')
			
			
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print(con, x+2, y, 'Cycle Selected Gun')
			libtcod.console_print(con, x+2, y+1, 'Cycle Selected Ammo Type')
			libtcod.console_print(con, x+2, y+2, 'Toggle Ready Rack')
			
			libtcod.console_print(con, x+2, y+4, 'Load ' + str(add_num))
			libtcod.console_print(con, x+2, y+5, 'Unload ' + str(add_num))
			
			libtcod.console_print(con, x+2, y+7, 'Toggle 1/10')
			
			libtcod.console_print(con, x+2, y+9, 'Default Load')
			
			libtcod.console_print(con, x+6, y+11, 'Accept and Continue')
			
			
			# possible but not likely
			if weapon is None:
				libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
				return
			
			libtcod.console_print_ex(con, WINDOW_XM, 18, libtcod.BKGND_NONE,
				libtcod.CENTER, weapon.GetStat('name'))
			
			# description of ammo types available to current gun
			x = 3
			y = 22
			
			libtcod.console_set_default_foreground(con, libtcod.light_blue)
			libtcod.console_print(con, x, y, 'Available Ammo Types')
			y += 3
			
			for ammo_type in weapon.stats['ammo_type_list']:
				
				libtcod.console_set_default_foreground(con, libtcod.white)
				
				if ammo_type == 'HE':
					libtcod.console_print(con, x, y, 'High Explosive (HE)')
					libtcod.console_set_default_foreground(con, libtcod.light_grey)
					libtcod.console_print(con, x, y+2, 'Used against guns,')
					libtcod.console_print(con, x, y+3, 'infantry, and unarmoured')
					libtcod.console_print(con, x, y+4, 'vehicles.')
					
					y += 7
				
				elif ammo_type == 'AP':
					libtcod.console_print(con, x, y, 'Armour Penetrating (AP)')
					libtcod.console_set_default_foreground(con, libtcod.light_grey)
					libtcod.console_print(con, x, y+2, 'Used against armoured')
					libtcod.console_print(con, x, y+3, 'targets.')
					
					y += 6
			
			# visual depicition of main stores and ready rack
			x = 33
			y = 25
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print(con, x, y, 'Stores')
			libtcod.console_print(con, x+10, y, 'Ready Rack')
			
			# highlight active stores
			libtcod.console_set_default_background(con, libtcod.darker_yellow)
			if not use_rr:
				xh = x
				w = 9
			else:
				xh = x+10
				w = 10
			libtcod.console_rect(con, xh, y, w, 1, False, libtcod.BKGND_SET)
			libtcod.console_set_default_background(con, libtcod.black)
			
			y += 2
			
			ammo_count = weapon.ammo_stores.copy()
			rr_count = weapon.ready_rack.copy()
			
			# main stores
			libtcod.console_set_default_foreground(con, libtcod.darker_grey)
			xm = 0
			ym = 0
			total = 0
			for ammo_type in AMMO_TYPES:
				if ammo_type in ammo_count:
					for i in range(ammo_count[ammo_type]):
						
						# determine colour to use
						if ammo_type == 'HE':
							col = libtcod.grey
						elif ammo_type == 'AP':
							col = libtcod.yellow
						
						libtcod.console_put_char_ex(con, x+xm, y+ym, 7, col, libtcod.black)
						
						if xm == 8:
							xm = 0
							ym += 1
						else:
							xm += 1
						
						total += 1
			
			# fill out empty slots up to max ammo
			if total < int(weapon.stats['max_ammo']):
				for i in range(int(weapon.stats['max_ammo']) - total):
					libtcod.console_put_char(con, x+xm, y+ym, 9)
					if xm == 8:
						xm = 0
						ym += 1
					else:
						xm += 1
			
			# ready rack
			x += 10
			libtcod.console_set_default_foreground(con, libtcod.darker_grey)
			xm = 0
			ym = 0
			total = 0
			for ammo_type in AMMO_TYPES:
				if ammo_type in rr_count:
					for i in range(rr_count[ammo_type]):
						
						# determine colour to use
						if ammo_type == 'HE':
							col = libtcod.grey
						elif ammo_type == 'AP':
							col = libtcod.yellow
						
						libtcod.console_put_char_ex(con, x+xm, y+ym, 7, col, libtcod.black)
						
						if xm == 8:
							xm = 0
							ym += 1
						else:
							xm += 1
						
						total += 1
			
			# fill out empty slots up to max ammo
			if total < weapon.rr_size:
				for i in range(weapon.rr_size - total):
					libtcod.console_put_char(con, x+xm, y+ym, 9)
					if xm == 8:
						xm = 0
						ym += 1
					else:
						xm += 1
			
			
			# show current numerical values for each ammo type
			# also which type is currently selected
			x = 58
			y = 25
			
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print_ex(con, x+11, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, 'RR')
			y += 1
			for ammo_type in AMMO_TYPES:
				if ammo_type in weapon.ammo_stores:
					
					if selected_ammo_type == ammo_type:
						libtcod.console_set_default_background(con, libtcod.dark_blue)
						libtcod.console_rect(con, x, y, 12, 1, True, libtcod.BKGND_SET)
						libtcod.console_set_default_background(con, libtcod.black)
					
					if ammo_type == 'HE':
						col = libtcod.grey
					elif ammo_type == 'AP':
						col = libtcod.yellow
					libtcod.console_put_char_ex(con, x, y, 7, col, libtcod.black)
					
					libtcod.console_set_default_foreground(con, libtcod.white)
					libtcod.console_print(con, x+2, y, ammo_type)
					libtcod.console_set_default_foreground(con, libtcod.light_grey)
					libtcod.console_print_ex(con, x+8, y, libtcod.BKGND_NONE,
						libtcod.RIGHT, str(weapon.ammo_stores[ammo_type]))
					libtcod.console_print_ex(con, x+11, y, libtcod.BKGND_NONE,
						libtcod.RIGHT, str(weapon.ready_rack[ammo_type]))
					
					
					
					y += 1
			y += 1
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_print(con, x+2, y, 'Max')
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			libtcod.console_print_ex(con, x+8, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, weapon.stats['max_ammo'])
			libtcod.console_print_ex(con, x+11, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, str(weapon.rr_size))
			
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			
			# FUTURE: visual depicition of extra ammo
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			
			
		# select first weapon by default, and first ammo type
		weapon = campaign.player_unit.weapon_list[0]
		selected_ammo_type = weapon.stats['ammo_type_list'][0]
		
		# record initial loaded number of ammo
		ammo_num = 0
		for ammo_type in AMMO_TYPES:
			if ammo_type in weapon.ammo_stores:
				ammo_num += weapon.ammo_stores[ammo_type]
		rr_num = 0
		for ammo_type in AMMO_TYPES:
			if ammo_type in weapon.ready_rack:
				rr_num += weapon.ready_rack[ammo_type]
		
		
		# draw screen for first time
		UpdateMenuCon()
		
		# menu input loop
		exit_menu = False
		while not exit_menu:
			
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			keypress = GetInputEvent()
			if not keypress: continue
			
			if key.vk == libtcod.KEY_ENTER:
				exit_menu = True
				continue
			
			# mapped key commands
			key_char = DeKey(chr(key.c).lower())
			
			# cycle selected ammo type
			if key_char == 'e':
				i = weapon.stats['ammo_type_list'].index(selected_ammo_type)
				
				if i == len(weapon.stats['ammo_type_list']) - 1:
					i = 0
				else:
					i += 1
					
				selected_ammo_type = weapon.stats['ammo_type_list'][i]
				UpdateMenuCon()
				continue
			
			# toggle load/unload ready rack
			elif key_char == 'r':
				use_rr = not use_rr
				UpdateMenuCon()
				continue
			
			# load one shell of selected type
			elif key_char == 'd':
				
				# make sure there is enough room before loading
				if use_rr:
					if rr_num + add_num > weapon.rr_size:
						continue
					weapon.ready_rack[selected_ammo_type] += add_num
					rr_num += add_num
				else:
					if ammo_num + add_num > int(weapon.stats['max_ammo']):
						continue
					weapon.ammo_stores[selected_ammo_type] += add_num
					ammo_num += add_num
				
				if add_num == 1:
					PlaySoundFor(None, 'move_1_shell')
				else:
					PlaySoundFor(None, 'move_10_shell')
				UpdateMenuCon()
				continue
			
			# unload one shell of selected type
			elif key_char == 'a':
				
				# make sure shell(s) are available
				if use_rr:
					if weapon.ready_rack[selected_ammo_type] - add_num < 0:
						continue
					weapon.ready_rack[selected_ammo_type] -= add_num
					rr_num -= add_num
				else:
				
					if weapon.ammo_stores[selected_ammo_type] - add_num < 0:
						continue
					weapon.ammo_stores[selected_ammo_type] -= add_num
					ammo_num -= add_num
				
				if add_num == 1:
					PlaySoundFor(None, 'move_1_shell')
				else:
					PlaySoundFor(None, 'move_10_shell')
				UpdateMenuCon()
				continue
			
			# toggle adding/removing 1/10
			elif key_char == 'z':
				
				if add_num == 1:
					add_num = 10
				else:
					add_num = 1
				UpdateMenuCon()
				continue
			
			# replace current load with default
			elif key_char == 'x':
				
				# clear current load
				for ammo_type in AMMO_TYPES:
					if ammo_type in weapon.ammo_stores:
						weapon.ammo_stores[ammo_type] = 0
					if ammo_type in weapon.ready_rack:
						weapon.ready_rack[ammo_type] = 0
				
				# replace with default load
				
				# HE only
				if 'HE' in weapon.ammo_stores and 'AP' not in weapon.ammo_stores:
					weapon.ammo_stores['HE'] = int(weapon.stats['max_ammo'])
					weapon.ready_rack['HE'] = weapon.rr_size
					
				# AP only
				elif 'AP' in weapon.ammo_stores and 'HE' not in weapon.ammo_stores:
					weapon.ammo_stores['AP'] = int(weapon.stats['max_ammo'])
					weapon.ready_rack['AP'] = weapon.rr_size
		
				# HE and AP
				else:
					weapon.ammo_stores['HE'] = int(float(weapon.stats['max_ammo']) * 0.75)
					weapon.ready_rack['HE'] = int(float(weapon.rr_size * 0.75))
					weapon.ammo_stores['AP'] = int(weapon.stats['max_ammo']) - weapon.ammo_stores['HE']
					weapon.ready_rack['AP'] = weapon.rr_size - weapon.ready_rack['HE']
				
				PlaySoundFor(None, 'move_10_shell')
				UpdateMenuCon()
				continue
				
	
	# check to see whether we need to replace crew after a scenario
	# at present this is only used for player unit, but in future could be used for AI units as well
	def DoCrewCheck(self, unit):
		
		# don't bother for dead tanks
		if not unit.alive: return
		
		# skip if player died
		if campaign.ended: return
		
		# Stunned, Unconscious, and Critical crew automatically recover
		# FUTURE: Do a final recovery roll for Critical crew
		replacement_needed = False
		player_seriously_injured = False
		for position in unit.positions_list:
			if position.crewman is None: continue
			if position.crewman.status != '':
				if position.crewman.status == 'Dead':
					replacement_needed = True
					continue
				if position.crewman.wound in ['Serious', 'Critical']:
					if position.name in PLAYER_POSITIONS:
						player_seriously_injured = True
					replacement_needed = True
					continue
				position.crewman.status = ''
		
		# return if no replacements needed
		if not replacement_needed: return
		
		# return if player has serious wound
		if player_seriously_injured:
			ShowMessage('You have been seriously injured and are taken off the front lines. Your campaign is over.')
			self.ended = True
			campaign.ended = True
			campaign.player_oob = True
			return
		
		# spend time if campaign day has not yet ended
		if unit == campaign.player_unit and not campaign_day.ended:
			self.AdvanceClock(0, 30)
			ShowMessage('You await a transport to recover bodies and provide new crew, which takes 30 mins.')
			
		for position in unit.positions_list:
			if position.crewman is None: continue
			if position.crewman.status == 'Dead' or position.crewman.wound in ['Serious', 'Critical']:
				# FUTURE: preserve original order when replacing crewmen
				unit.personnel_list.remove(position.crewman)
				unit.personnel_list.append(Personnel(unit, unit.nation, position))
				position.crewman = unit.personnel_list[-1]
				if unit == campaign.player_unit:
					text = 'A new crewman joins your crew in the ' + position.name + ' position.'
					ShowMessage(text)
	
	# generate roads linking zones; only dirt roads for now
	def GenerateRoads(self):
		
		# for DEBUG - clear any existing roads
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			self.map_hexes[(hx,hy)].dirt_roads = []
		
		# see if a road is generated on this map
		if 'dirt_road_odds' not in REGIONS[campaign.stats['region']]:
			return
		if GetPercentileRoll() > float(REGIONS[campaign.stats['region']]['river_odds']):
			return
		
		# choose a random edge hex
		edge_list = []
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			for d in range(6):
				if self.GetAdjacentCDHex(hx, hy, d) not in CAMPAIGN_DAY_HEXES:
					edge_list.append((hx, hy))
					break
		(hx1, hy1) = choice(edge_list)
		
		# find the hex on opposite edge of map
		hx2 = hx1 * -1
		if hy1 > 4:
			hy2 = hy1 - ((hy1 - 4) * 2)
		elif hy1 == 4:
			hy2 = 4
		else:
			hy2 = hy1 + ((4 - hy1) * 2)
		
		# plot the road
		hx, hy = hx1, hy1
		while hx != hx2 or hy != hy2:
			path_choices = []
			distance = GetHexDistance(hx, hy, hx2, hy2)
			for d in range(6):
				
				# already a road link here
				if d in self.map_hexes[(hx,hy)].dirt_roads:
					continue
				(hx_p, hy_p) = self.GetAdjacentCDHex(hx, hy, d)
				
				# target hex not on map
				if (hx_p, hy_p) not in CAMPAIGN_DAY_HEXES:
					continue
				
				# further away or same distance from target hex
				if GetHexDistance(hx_p, hy_p, hx2, hy2) >= distance:
					continue
				
				path_choices.append(d)
			
			# no path choices remaining
			if len(path_choices) == 0:
				break
			
			# choose one and make a link to it
			d = choice(path_choices)
			self.map_hexes[(hx,hy)].dirt_roads.append(d)
			(hx_p,hy_p) = self.GetAdjacentCDHex(hx, hy, d)
			self.map_hexes[(hx_p,hy_p)].dirt_roads.append(ConstrainDir(d + 3))
			
			# move current hex to the one just linked
			hx, hy = hx_p, hy_p
		
		# link all settled hexes to a road branch
		
		# build a list of all settled hexes
		hex_list = []
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			if self.map_hexes[(hx,hy)].terrain_type in ['Villages']:
				
				# already on road
				if len(self.map_hexes[(hx,hy)].dirt_roads) > 0: continue
				
				hex_list.append((hx, hy))
		
		if len(hex_list) > 0:
			shuffle(hex_list)
			for (hx1, hy1) in hex_list:
				
				# find the nearest CD map hex with at least one road link
				link_list = []
				for (hx2, hy2) in CAMPAIGN_DAY_HEXES:
					# same hex
					if hx2 == hx1 and hy2 == hy1: continue
					
					# no roads there
					if len(self.map_hexes[(hx2,hy2)].dirt_roads) == 0: continue
					
					# get the distance to the possible link
					d = GetHexDistance(hx1, hy1, hx2, hy2)
					
					link_list.append((d,hx2,hy2))
				
				# no possible links!
				if len(link_list) == 0:
					continue
				
				# sort the list by distance and get the nearest one
				link_list.sort(key = lambda x: x[0])
				(d,hx2,hy2) = link_list[0]
				
				# generate a road to link the two
				line = GetHexLine(hx1, hy1, hx2, hy2)
				for i in range(len(line)-1):
					(hx, hy) = line[i]
					(hx_p, hy_p) = line[i+1]
					
					# make sure that both hexes are on map, and break if either is not
					if (hx, hy) not in self.map_hexes or (hx_p,hy_p) not in self.map_hexes:
						break
					
					# create the road links
					d = self.GetDirectionToAdjacentCD(hx, hy, hx_p, hy_p)
					self.map_hexes[(hx,hy)].dirt_roads.append(d)
					self.map_hexes[(hx_p,hy_p)].dirt_roads.append(ConstrainDir(d+3))
	
	
	# generate rivers and bridges along hex zone edges
	def GenerateRivers(self):
		
		# roll for how many rivers are on map (max 2)
		if 'river_odds' not in REGIONS[campaign.stats['region']]:
			return
		
		# clear any existing rivers and bridges
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			self.map_hexes[(hx,hy)].rivers = []
			self.map_hexes[(hx,hy)].bridges = []
		
		rivers = 0
		odds = float(REGIONS[campaign.stats['region']]['river_odds'])
		
		if GetPercentileRoll() <= odds:
			rivers += 1
			if GetPercentileRoll() <= odds:
				rivers += 1
		
		if rivers == 0: return
		
		# create the rivers
		
		# try loop to make sure that map is still traversable
		for tries in range(300):
			
			for i in range(rivers):
				
				libtcod.console_flush()
				
				# build a list of map edge hexes
				edge_list = []
				for (hx, hy) in CAMPAIGN_DAY_HEXES:
					for d in range(6):
						if self.GetAdjacentCDHex(hx, hy, d) not in CAMPAIGN_DAY_HEXES:
							edge_list.append((hx, hy))
							break
				
				# determine starting and ending hex 
				(hx1, hy1) = choice(edge_list)
				shuffle(edge_list)
				for (hx2, hy2) in edge_list:
					if GetHexDistance(hx1, hy1, hx2, hy2) < 5: continue
					break
				
				#print('DEBUG: Adding river from ' + str(hx1) + ',' + str(hy1) + ' to ' + str(hx2) + ',' + str(hy2))
				
				# run through the hex line
				hex_line = GetHexLine(hx1, hy1, hx2, hy2)
				for index in range(len(hex_line)):
				
					(hx, hy) = hex_line[index]
					
					if (hx, hy) not in CAMPAIGN_DAY_HEXES: continue
					
					# chance that river will end in map
					if GetPercentileRoll() <= 2.0:
						break
					
					# each hex needs 1+ hexsides to become rivers
					
					# determine direction to previous hex
					if hx == hx1 and hy == hy1:
						
						# for first hex, we need to use off-board hex as previous location
						for direction1 in range(6):
							if self.GetAdjacentCDHex(hx, hy, direction1) not in CAMPAIGN_DAY_HEXES:
								break
					
					else:
						# otherwise use direction toward previous hex
						(hx_n, hy_n) = hex_line[index-1]
						direction1 = self.GetDirectionToAdjacentCD(hx, hy, hx_n, hy_n)
					
					# determine direction to next hex
					if hx == hx2 and hy == hy2:
						# for final hex, we need to use off-board hex as next location
						for direction2 in range(6):
							if self.GetAdjacentCDHex(hx, hy, direction2) not in CAMPAIGN_DAY_HEXES:
								break
					else:
						# otherwise use direction toward next hex
						(hx_n, hy_n) = hex_line[index+1]
						direction2 = self.GetDirectionToAdjacentCD(hx, hy, hx_n, hy_n)
					
					# determine shortest rotation path (clockwise or counter clockwise)
					path1 = []
					for i in range(6):
						path1.append(ConstrainDir(direction1 + i))
						if ConstrainDir(direction1 + i) == direction2: break
						
					path2 = []
					for i in range(6):
						path2.append(ConstrainDir(direction1 - i))
						if ConstrainDir(direction1 - i) == direction2: break
						
					if len(path1) < len(path2):
						path = path1
					else:
						path = path2
					
					for direction in path[1:]:
						# may have already been added by first river
						if direction in self.map_hexes[(hx,hy)].rivers: continue
						self.map_hexes[(hx,hy)].rivers.append(direction)
					
			# create bridges in the rivers
			for (hx, hy) in CAMPAIGN_DAY_HEXES:
				if len(self.map_hexes[(hx,hy)].rivers) == 0: continue
			
				for direction in self.map_hexes[(hx,hy)].rivers:
					# road already here
					if direction in self.map_hexes[(hx,hy)].dirt_roads:
						if direction not in self.map_hexes[(hx,hy)].bridges:
							self.map_hexes[(hx,hy)].bridges.append(direction)
						continue
					
					# randomly add a bridge/ford here
					if GetPercentileRoll() <= 10.0:
						if direction not in self.map_hexes[(hx,hy)].bridges:
							self.map_hexes[(hx,hy)].bridges.append(direction)
		
			# do path checking
			path_good = False
			(hx1, hy1) = self.player_unit_location
			if self.mission == 'Fighting Withdrawl':
				hx2_max = 1
				hy2 = 8
			else:
				hx2_max = 5
				hy2 = 0
			for hx2 in range(hx2_max - 5, hx2_max):
				if len(GetHexPath(hx1, hy1, hx2, hy2)) != 0:
					path_good = True
					break
			
			# if path is good: break rather than trying again
			if path_good:
				break
			
			# clear any created rivers and bridges before trying again
			for (hx, hy) in CAMPAIGN_DAY_HEXES:
				self.map_hexes[(hx,hy)].rivers = []
				self.map_hexes[(hx,hy)].bridges = []
		
		
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
	
	
	# returns the direction toward an adjacent hex
	def GetDirectionToAdjacentCD(self, hx1, hy1, hx2, hy2):
		hx_mod = hx2 - hx1
		hy_mod = hy2 - hy1
		if (hx_mod, hy_mod) in CD_DESTHEX:
			return CD_DESTHEX.index((hx_mod, hy_mod))
			# hex is not adjacent
			return -1
	
	
	# display a summary of a completed campaign day
	def DisplayCampaignDaySummary(self):
	
		# create a local copy of the current screen to re-draw when we're done
		temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
		libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
		
		# darken screen background
		libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
		
		# build info window
		temp_con = libtcod.console_new(29, 54)
		libtcod.console_set_default_background(temp_con, libtcod.black)
		libtcod.console_set_default_foreground(temp_con, libtcod.light_grey)
		libtcod.console_clear(temp_con)
		DrawFrame(temp_con, 0, 0, 29, 54)
		
		# campaign and calendar day info
		libtcod.console_set_default_foreground(temp_con, PORTRAIT_BG_COL)
		lines = wrap(campaign.stats['name'], 27)
		y = 1
		for line in lines:
			libtcod.console_print_ex(temp_con, 14, y, libtcod.BKGND_NONE, libtcod.CENTER,
				line)
			y += 1
			if y == 4: break
		
		libtcod.console_set_default_foreground(temp_con, libtcod.white)
		libtcod.console_print_ex(temp_con, 14, 4, libtcod.BKGND_NONE, libtcod.CENTER,
			GetDateText(campaign.today))
		
		# day result: survived or destroyed
		libtcod.console_print_ex(temp_con, 14, 7, libtcod.BKGND_NONE, libtcod.CENTER,
			'Outcome of Day:')
		
		if campaign.player_oob:
			col = libtcod.red
			text = 'COMMANDER OUT OF ACTION'
		elif campaign_day.abandoned_tank:
			col = libtcod.light_grey
			text = 'ABANDONED TANK'
		elif campaign.player_unit.immobilized:
			col = libtcod.light_red
			text = 'IMMOBILIZED'
		elif campaign.player_unit.alive:
			col = GOLD_COL
			text = 'SURVIVED'
		else:
			col = ENEMY_UNIT_COL
			text = 'TANK LOST'
		libtcod.console_set_default_foreground(temp_con, col)
		libtcod.console_print_ex(temp_con, 14, 8, libtcod.BKGND_NONE, libtcod.CENTER,
			text)
		
		# total VP
		libtcod.console_set_default_foreground(temp_con, libtcod.white)
		libtcod.console_print_ex(temp_con, 14, 11, libtcod.BKGND_NONE, libtcod.CENTER,
			'Total VP Earned:')
		libtcod.console_print_ex(temp_con, 14, 13, libtcod.BKGND_NONE, libtcod.CENTER,
			str(campaign.player_vp))
		
		# day stats
		y = 17
		for text in RECORD_LIST:
			libtcod.console_print(temp_con, 2, y, text + ':')
			libtcod.console_print_ex(temp_con, 26, y, libtcod.BKGND_NONE, libtcod.RIGHT,
				str(campaign_day.records[text]))
			y += 1
			if y == 49:
				break
		
		libtcod.console_set_default_foreground(temp_con, ACTION_KEY_COL)
		libtcod.console_print(temp_con, 7, 51, 'Enter')
		libtcod.console_set_default_foreground(temp_con, libtcod.light_grey)
		libtcod.console_print(temp_con, 14, 51, 'Continue')
		
		# display console to screen
		libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 31, 3)
		
		# get input from player
		exit_menu = False
		while not exit_menu:
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			if not GetInputEvent(): continue
			
			# end menu
			if key.vk in [libtcod.KEY_ESCAPE, libtcod.KEY_ENTER]:
				exit_menu = True

	
	##### Campaign Day Console Functions #####
	
	# generate/update the campaign day map console
	def UpdateCDMapCon(self):
		
		CHAR_LOCATIONS = [
			(3,1), (2,2), (3,2), (4,2), (1,3), (2,3), (3,3), (4,3), (5,3),
			(1,4), (2,4), (4,4), (5,4), (1,5), (2,5), (3,5), (4,5), (5,5),
			(2,6), (3,6), (4,6), (3,7)
		]
		
		def GetRandomLocation():
			return CHAR_LOCATIONS[libtcod.random_get_int(generator, 0, 21)]
		
		libtcod.console_clear(cd_map_con)
		self.cd_map_index = {}
		
		# draw map hexes to console
		
		# load base zone image - depends on current ground conditions
		if self.weather['Ground'] in ['Snow', 'Deep Snow']:
			dayhex = LoadXP('dayhex_openground_snow.xp')
			bg_col = libtcod.Color(158,158,158)
		else:
			dayhex = LoadXP('dayhex_openground.xp')
			bg_col = libtcod.Color(0,64,0)
		temp_con = libtcod.console_new(7, 9)
		libtcod.console_set_key_color(temp_con, KEY_COLOR)
		
		
		for (hx, hy), cd_hex in self.map_hexes.items():
			
			# generate console image for this zone's terrain type
			libtcod.console_blit(dayhex, 0, 0, 0, 0, temp_con, 0, 0)
			
			generator = libtcod.random_new_from_seed(cd_hex.console_seed)
			
			if cd_hex.terrain_type == 'Forest':
				
				for (x,y) in CHAR_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 10) <= 4: continue
					col = libtcod.Color(0,libtcod.random_get_int(generator, 100, 170),0)
					libtcod.console_put_char_ex(temp_con, x, y, 6, col, bg_col)
				
			elif cd_hex.terrain_type == 'Hills':
				
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
				
			elif cd_hex.terrain_type == 'Fields':
				
				for (x,y) in CHAR_LOCATIONS:
					c = libtcod.random_get_int(generator, 120, 190)
					libtcod.console_put_char_ex(temp_con, x, y, 176,
						libtcod.Color(c,c,0), bg_col)
				
			elif cd_hex.terrain_type == 'Marsh':
				
				elements = libtcod.random_get_int(generator, 7, 13)
				while elements > 0:
					(x,y) = GetRandomLocation()
					if libtcod.console_get_char(temp_con, x, y) == 176: continue
					libtcod.console_put_char_ex(temp_con, x, y, 176,
						libtcod.Color(45,0,180), bg_col)
					elements -= 1
				
			elif cd_hex.terrain_type == 'Villages':
				
				elements = libtcod.random_get_int(generator, 5, 9)
				while elements > 0:
					(x,y) = GetRandomLocation()
					if libtcod.console_get_char(temp_con, x, y) == 249: continue
					libtcod.console_put_char_ex(temp_con, x, y, 249,
						libtcod.Color(77,77,77), bg_col)
					elements -= 1
			
			# draw the final image to the map console
			(x,y) = self.PlotCDHex(hx, hy)
			libtcod.console_blit(temp_con, 0, 0, 0, 0, cd_map_con, x-3, y-4)
			
			# record screen locations of hex
			self.cd_map_index[(x, y-3)] = (hx, hy)
			for x1 in range(x-1, x+2):
				self.cd_map_index[(x1, y-2)] = (hx, hy)
				self.cd_map_index[(x1, y+2)] = (hx, hy)
			for x1 in range(x-2, x+3):
				self.cd_map_index[(x1, y-1)] = (hx, hy)
				self.cd_map_index[(x1, y)] = (hx, hy)
				self.cd_map_index[(x1, y+1)] = (hx, hy)
			self.cd_map_index[(x, y+3)] = (hx, hy)
			
		del temp_con, dayhex
		
		# draw dirt roads overtop
		for (hx, hy), map_hex in self.map_hexes.items():
			if len(map_hex.dirt_roads) == 0: continue
			
			(x1, y1) = self.PlotCDHex(hx, hy)
			
			for direction in map_hex.dirt_roads:
				# only draw if in direction 0-2
				if direction > 2: continue
				# get the other zone linked by road
				(hx2, hy2) = self.GetAdjacentCDHex(hx, hy, direction)
				if (hx2, hy2) not in self.map_hexes: continue
				
				# paint road
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
			
			# if map hex is on edge and has 1 dirt road connection, draw a road leading off the edge of the map
			if len(map_hex.dirt_roads) > 1: continue
			off_map_hexes = []
			for direction in range(6):
				(hx2, hy2) = self.GetAdjacentCDHex(hx, hy, direction)
				if (hx2, hy2) not in self.map_hexes:
					off_map_hexes.append((hx2, hy2))
			if len(off_map_hexes) == 0: continue
			
			(hx2, hy2) = off_map_hexes[0]
			(x2, y2) = self.PlotCDHex(hx2, hy2)
			line = GetLine(x1, y1, x2, y2)
			for (x, y) in line:
				if libtcod.console_get_char_background(cd_map_con, x, y) == libtcod.black:
					break
					
				libtcod.console_set_char_background(cd_map_con, x, y,
					DIRT_ROAD_COL, libtcod.BKGND_SET)
					
				# if character is not blank or hex edge, remove it
				if libtcod.console_get_char(cd_map_con, x, y) not in [0, 249, 250]:
					libtcod.console_set_char(cd_map_con, x, y, 0)
		
		# draw rivers overtop
		for (hx, hy), map_hex in self.map_hexes.items():
			if len(map_hex.rivers) == 0: continue
			
			(x, y) = self.PlotCDHex(hx, hy)
			
			# draw each river edge
			for direction in map_hex.rivers:
				for (xm, ym) in CD_HEX_EDGE_CELLS[direction]:
					libtcod.console_put_char_ex(cd_map_con, x+xm, y+ym, 0,
						libtcod.white, RIVER_COL)
					
			# draw any bridges
			for direction in map_hex.bridges:
				for (xm, ym) in CD_HEX_EDGE_CELLS[direction][1:-1]:
					libtcod.console_put_char_ex(cd_map_con, x+xm, y+ym, 240,
						libtcod.darkest_sepia, DIRT_ROAD_COL)
			
		
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
		
		# enemy strength level, player arty/air support
		libtcod.console_set_default_foreground(cd_unit_con, libtcod.red)
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			map_hex = self.map_hexes[(hx,hy)]
			
			(x,y) = self.PlotCDHex(hx, hy)
			
			if map_hex.controlled_by == 0: continue
			if not map_hex.known_to_player: continue
			libtcod.console_print(cd_unit_con, x, y-1, str(map_hex.enemy_strength))
		
		# draw player unit group
		(hx, hy) = self.player_unit_location
		(x,y) = self.PlotCDHex(hx, hy)
		
		# apply animation offset if any
		x += session.cd_x_offset
		y += session.cd_y_offset
		
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
		
		# highlight objective hexes
		for (hx, hy) in CAMPAIGN_DAY_HEXES:
			if self.map_hexes[(hx,hy)].objective is None: continue
			
			(x,y) = self.PlotCDHex(hx, hy)
			for (xm,ym) in CD_HEX_OBJECTIVE_CELLS:
				libtcod.console_put_char_ex(cd_control_con, x+xm,
					y+ym, chr(250), ACTION_KEY_COL, libtcod.black)
	
	
	# generate/update the GUI console
	def UpdateCDGUICon(self):
		libtcod.console_clear(cd_gui_con)
		
		# movement menu, direction currently selected
		if self.active_menu == 3 and self.selected_direction is not None:
			
			# draw directional line
			(hx, hy) = self.player_unit_location
			(x1,y1) = self.PlotCDHex(hx, hy)
			(hx, hy) = self.GetAdjacentCDHex(hx, hy, self.selected_direction)
			if (hx, hy) in self.map_hexes:
				(x2,y2) = self.PlotCDHex(hx, hy)
				line = GetLine(x1,y1,x2,y2)
				for (x,y) in line[1:-1]:
					libtcod.console_put_char_ex(cd_gui_con, x, y, 250, libtcod.green,
						libtcod.black)
				(x,y) = line[-1]
				libtcod.console_put_char_ex(cd_gui_con, x, y, CD_DIR_ARROW[self.selected_direction],
					libtcod.green, libtcod.black)
	
	
	# generate/update the player unit console
	def UpdateCDPlayerUnitCon(self):
		libtcod.console_clear(cd_player_unit_con)
		campaign.player_unit.DisplayMyInfo(cd_player_unit_con, 0, 0, status=False)
	
	
	# generate/update the command menu console 25x41
	def UpdateCDCommandCon(self):
		libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
		libtcod.console_set_default_background(cd_command_con, libtcod.black)
		libtcod.console_clear(cd_command_con)
		
		libtcod.console_set_default_foreground(cd_command_con, TITLE_COL)
		libtcod.console_print(cd_command_con, 6, 0, 'Command Menu')
		
		x = 0
		for (text, num, col) in CD_MENU_LIST:
			libtcod.console_set_default_background(cd_command_con, col)
			libtcod.console_rect(cd_command_con, x, 1, 2, 1, True, libtcod.BKGND_SET)
			
			# display menu number
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			libtcod.console_print(cd_command_con, x, 1, str(num))
			libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			
			x += 2
			
			# display menu text if tab is active
			if self.active_menu == num:
				libtcod.console_rect(cd_command_con, x, 1, len(text)+2, 1,
					True, libtcod.BKGND_SET)
				libtcod.console_print(cd_command_con, x, 1, text)
				x += len(text) + 2
		
		# fill in rest of menu line with final colour
		libtcod.console_rect(cd_command_con, x, 1, 25-x, 1, True, libtcod.BKGND_SET)
		libtcod.console_set_default_background(cd_command_con, libtcod.black)
		
		# support
		if self.active_menu == 1:
			
			libtcod.console_print(cd_command_con, 1, 10, 'Current Support Levels:')
			
			# display current support levels
			libtcod.console_set_default_foreground(cd_command_con, libtcod.light_grey)
			text = 'Air Support: '
			if self.air_support_level == 0.0:
				text += 'None'
			else:
				text += str(self.air_support_level)
			libtcod.console_print(cd_command_con, 1, 12, text)
			
			text = 'Artillery Support: '
			if self.arty_support_level == 0.0:
				text += 'None'
			else:
				text += str(self.arty_support_level)
			libtcod.console_print(cd_command_con, 1, 13, text)
			
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			libtcod.console_print(cd_command_con, 2, 38, 'R')
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			libtcod.console_print(cd_command_con, 5, 38, 'Request Additional')
			libtcod.console_print(cd_command_con, 5, 39, 'Support (15 mins.)')
		
		# crew
		elif self.active_menu == 2:
			
			DisplayCrew(campaign.player_unit, cd_command_con, 0, 3, self.selected_position)
			
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			libtcod.console_print(cd_command_con, 3, 38, EnKey('w').upper() + '/' + EnKey('s').upper())
			libtcod.console_print(cd_command_con, 3, 39, EnKey('f').upper())
			
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			libtcod.console_print(cd_command_con, 8, 38, 'Select Position')
			libtcod.console_print(cd_command_con, 8, 39, 'Crewman Menu')
		
		
		# travel
		elif self.active_menu == 3:
			
			# display directional options
			x1 = 12
			y1 = 6
			
			# display possible support/move/recon directions
			libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			libtcod.console_put_char(cd_command_con, x1, y1, '@')
			
			for direction in range(6):
				libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
				
				if self.selected_direction is not None:
					if self.selected_direction == direction:
						libtcod.console_set_default_foreground(cd_command_con, libtcod.light_green)
						
				(k, x, y, char) = CD_TRAVEL_CMDS[direction]
				libtcod.console_put_char(cd_command_con, x1+x, y1+y, EnKey(k).upper())
				if direction <= 2:
					x+=1
				else:
					x-=1
				libtcod.console_set_default_foreground(cd_command_con, libtcod.dark_green)
				libtcod.console_put_char(cd_command_con, x1+x, y1+y, chr(char))
			
			if self.selected_direction is None:
				libtcod.console_set_default_foreground(cd_command_con, libtcod.light_grey)
				libtcod.console_print_ex(cd_command_con, 13, y1+4, libtcod.BKGND_NONE, libtcod.CENTER,
					'Select a Direction')
			
			# display Wait command (always available)
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			libtcod.console_print(cd_command_con, 3, 37, EnKey('w').upper())
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			libtcod.console_print(cd_command_con, 10, 37, 'Wait/Defend')
			
			# check to see whether travel in selected direction is not possible
			if self.selected_direction is None:
				return
			(hx1, hy1) = self.player_unit_location
			(hx2, hy2) = self.GetAdjacentCDHex(hx1, hy1, self.selected_direction)
			if (hx2, hy2) not in self.map_hexes: return
				
			# display enemy strength/organization if any and chance of encounter
			map_hex = self.map_hexes[(hx2,hy2)]
			if map_hex.controlled_by == 1:
				
				libtcod.console_set_default_foreground(cd_command_con, libtcod.red)
				libtcod.console_print(cd_command_con, 3, 12, 'Destination is')
				libtcod.console_print(cd_command_con, 3, 13, 'Enemy Controlled')
				
				# display recon option
				if not map_hex.known_to_player:
					libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
					libtcod.console_print(cd_command_con, 1, 19, 'Recon: 15 mins.')
					libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
					libtcod.console_print(cd_command_con, 3, 38, EnKey('r').upper())
					
					libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
					libtcod.console_print(cd_command_con, 10, 38, 'Recon')
				else:
					libtcod.console_print(cd_command_con, 3, 15, 'Strength: ' + str(map_hex.enemy_strength))
					libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			
			# calculate and display travel time
			mins = self.CalculateTravelTime(hx1, hy1, hx2, hy2)
			# travel not allowed
			if mins == -1:
				text = 'N/A'
			else:
				text = str(mins) + ' mins.'
			libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			libtcod.console_print(cd_command_con, 1, 20, 'Travel Time: ' + text)
		
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			libtcod.console_print(cd_command_con, 3, 39, 'Enter')
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			libtcod.console_print(cd_command_con, 10, 39, 'Proceed')
			
			# display support commands
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			libtcod.console_print(cd_command_con, 1, 23, EnKey('t').upper())
			libtcod.console_print(cd_command_con, 1, 26, EnKey('g').upper())
			libtcod.console_print(cd_command_con, 1, 29, EnKey('b').upper())
			
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			libtcod.console_print(cd_command_con, 3, 23, 'Advancing Fire')
			if self.advancing_fire:
				text = 'ON'
			else:
				text = 'OFF'
			libtcod.console_print(cd_command_con, 4, 24, '(' + text + ')')
			
			# air support request
			if 'air_support_level' not in campaign.current_week or campaign_day.weather['Cloud Cover'] == 'Overcast':
				libtcod.console_set_default_foreground(cd_command_con, libtcod.darker_grey)
			libtcod.console_print(cd_command_con, 3, 26, 'Request Air Support')
			if self.air_support_request:
				text = 'ON'
			else:
				text = 'OFF'
			if 'air_support_level' in campaign.current_week:
				libtcod.console_print(cd_command_con, 4, 27, '(' + text + ')')
			
			# artillery support request
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			if 'arty_support_level' not in campaign.current_week:
				libtcod.console_set_default_foreground(cd_command_con, libtcod.darker_grey)
			libtcod.console_print(cd_command_con, 3, 29, 'Request Arty Support')
			if self.arty_support_request:
				text = 'ON'
			else:
				text = 'OFF'
			if 'arty_support_level' in campaign.current_week:
				libtcod.console_print(cd_command_con, 4, 30, '(' + text + ')')
			
		# group
		elif self.active_menu == 4:
			
			libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			libtcod.console_print(cd_command_con, 1, 3, 'Squad')
			text = str(campaign.player_squad_num) + '/' + str(campaign.player_squad_max) + ' ' + campaign.player_unit.unit_id
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			libtcod.console_print(cd_command_con, 1, 5, text)
		
		# main gun
		elif self.active_menu == 5:
			
			# display current main gun ammo levels
			weapon = campaign.player_unit.weapon_list[0]
			if weapon.GetStat('type') == 'Gun':
				libtcod.console_print(cd_command_con, 6, 3, weapon.stats['name'])
				weapon.DisplayAmmo(cd_command_con, 6, 5)
			
			libtcod.console_set_default_foreground(cd_command_con, libtcod.white)
			libtcod.console_print_ex(cd_command_con, 12, 14, libtcod.BKGND_NONE, libtcod.CENTER,
				'Request resupply:')
			libtcod.console_print_ex(cd_command_con, 12, 15, libtcod.BKGND_NONE, libtcod.CENTER,
				'30 mins.')
			
			libtcod.console_set_default_foreground(cd_command_con, ACTION_KEY_COL)
			libtcod.console_print(cd_command_con, 2, 36, EnKey('d').upper() + '/' + EnKey('a').upper())
			libtcod.console_print(cd_command_con, 4, 37, EnKey('c').upper())
			libtcod.console_print(cd_command_con, 4, 39, EnKey('r').upper())
			
			libtcod.console_set_default_foreground(cd_command_con, libtcod.lighter_grey)
			libtcod.console_print(cd_command_con, 6, 36, 'Add/Remove to RR')
			libtcod.console_print(cd_command_con, 6, 37, 'Cycle Ammo Type')
			libtcod.console_print(cd_command_con, 6, 39, 'Request Resupply')
	
	
	# generate/update the campaign info console 23x5
	def UpdateCDCampaignCon(self):
		libtcod.console_set_default_background(cd_campaign_con, libtcod.darkest_blue)
		libtcod.console_clear(cd_campaign_con)
		libtcod.console_set_default_foreground(cd_campaign_con, libtcod.light_blue)
		libtcod.console_print_ex(cd_campaign_con, 11, 0, libtcod.BKGND_NONE, libtcod.CENTER,
			'Day Mission')
		libtcod.console_print_ex(cd_campaign_con, 11, 3, libtcod.BKGND_NONE, libtcod.CENTER,
			'Total VP')
		libtcod.console_set_default_foreground(cd_campaign_con, libtcod.white)
		libtcod.console_print_ex(cd_campaign_con, 11, 1, libtcod.BKGND_NONE, libtcod.CENTER,
			campaign_day.mission)
		libtcod.console_print_ex(cd_campaign_con, 11, 4, libtcod.BKGND_NONE, libtcod.CENTER,
			str(campaign.player_vp))
	
	
	# generate/update the zone info console
	def UpdateCDHexInfoCon(self):
		libtcod.console_clear(cd_hex_info_con)
		
		libtcod.console_set_default_foreground(cd_hex_info_con, libtcod.blue)
		libtcod.console_print_ex(cd_hex_info_con, 11, 0, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Zone Info')
		
		x = mouse.cx - 29
		y = mouse.cy - 6
		
		# no zone here or mouse cursor outside of map area
		if (x,y) not in self.cd_map_index or x < 2 or x > 30:
			libtcod.console_set_default_foreground(cd_hex_info_con, libtcod.light_grey)
			libtcod.console_print(cd_hex_info_con, 2, 2, 'Mouseover an area')
			libtcod.console_print(cd_hex_info_con, 2, 3, 'for info')
			return
		
		# find the hex
		(hx, hy) = self.cd_map_index[(x,y)]
		cd_hex = self.map_hexes[(hx, hy)]
		
		# display hex zone coordinates
		libtcod.console_set_default_foreground(cd_hex_info_con, libtcod.light_green)
		libtcod.console_print_ex(cd_hex_info_con, 11, 1, libtcod.BKGND_NONE,
			libtcod.CENTER, cd_hex.coordinate)
		
		# DEBUG - display hx,hy
		if DEBUG:
			libtcod.console_set_default_foreground(cd_hex_info_con, libtcod.yellow)
			libtcod.console_print_ex(cd_hex_info_con, 22, 0, libtcod.BKGND_NONE,
				libtcod.RIGHT, str(hx) + ',' + str(hy))
		
		# terrain
		libtcod.console_set_default_foreground(cd_hex_info_con, libtcod.light_grey)
		libtcod.console_print(cd_hex_info_con, 0, 3, cd_hex.terrain_type)
		
		# control
		if cd_hex.controlled_by == 0:
			libtcod.console_set_default_foreground(cd_hex_info_con, ALLIED_UNIT_COL)
			libtcod.console_print(cd_hex_info_con, 0, 5, 'Friendly controlled')
		else:
			libtcod.console_set_default_foreground(cd_hex_info_con, ENEMY_UNIT_COL)
			libtcod.console_print(cd_hex_info_con, 0, 5, 'Enemy controlled')
			libtcod.console_print(cd_hex_info_con, 0, 6, 'Strength: ')
			if cd_hex.known_to_player:
				text = str(cd_hex.enemy_strength)
			else:
				text = 'Unknown'
			libtcod.console_print(cd_hex_info_con, 10, 6, text)
				
		# objective
		if cd_hex.objective is not None:
			libtcod.console_set_default_foreground(cd_hex_info_con, ACTION_KEY_COL)
			libtcod.console_print(cd_hex_info_con, 0, 8, 'Objective: ' + cd_hex.objective['objective_type'])
			libtcod.console_print(cd_hex_info_con, 0, 9, 'VP: ' + str(cd_hex.objective['vp_reward']))
		
		# roads
		if len(cd_hex.dirt_roads) > 0:
			libtcod.console_set_default_foreground(cd_hex_info_con, DIRT_ROAD_COL)
			libtcod.console_print(cd_hex_info_con, 0, 11, 'Dirt roads')
	
	
	# starts or re-starts looping animations based on weather conditions
	def InitAnimations(self):
		
		# reset animations
		self.animation['rain_active'] = False
		self.animation['rain_drops'] = []
		self.animation['snow_active'] = False
		self.animation['snowflakes'] = []
		
		# check for rain or snow animation
		if campaign_day.weather['Precipitation'] in ['Rain', 'Heavy Rain']:
			self.animation['rain_active'] = True
		elif campaign_day.weather['Precipitation'] in ['Light Snow', 'Snow', 'Blizzard']:
			self.animation['snow_active'] = True
		
		# set up rain if any
		if self.animation['rain_active']:
			self.animation['rain_drops'] = []
			num = 8
			if campaign_day.weather['Precipitation'] == 'Heavy Rain':
				num = 16
			for i in range(num):
				x = libtcod.random_get_int(0, 4, 36)
				y = libtcod.random_get_int(0, 0, 50)
				lifespan = libtcod.random_get_int(0, 1, 5)
				self.animation['rain_drops'].append((x, y, lifespan))		
		
		# set up snow if any
		if self.animation['snow_active']:
			self.animation['snowflakes'] = []
			if campaign_day.weather['Precipitation'] == 'Light Snow':
				num = 4
			elif campaign_day.weather['Precipitation'] == 'Snow':
				num = 8
			else:
				num = 16
			for i in range(num):
				x = libtcod.random_get_int(0, 4, 36)
				y = libtcod.random_get_int(0, 0, 50)
				lifespan = libtcod.random_get_int(0, 4, 10)
				self.animation['snowflakes'].append((x, y, lifespan))	
		
	
	# update campaign day animation frame and console 36x52
	def UpdateAnimCon(self):
		
		libtcod.console_clear(cd_anim_con)
		
		# update rain display
		if self.animation['rain_active']:
			
			# update location of each rain drop, spawn new ones if required
			for i in range(len(self.animation['rain_drops'])):
				(x, y, lifespan) = self.animation['rain_drops'][i]
				
				# respawn if finished
				if lifespan == 0:
					x = libtcod.random_get_int(0, 4, 36)
					y = libtcod.random_get_int(0, 0, 50)
					lifespan = libtcod.random_get_int(0, 1, 5)
				else:
					y += 2
					lifespan -= 1
				
				self.animation['rain_drops'][i] = (x, y, lifespan)
			
			# draw drops to screen
			for (x, y, lifespan) in self.animation['rain_drops']:
				
				# skip if off screen
				if x < 0 or y > 50: continue
				
				if lifespan == 0:
					char = 111
				else:
					char = 124
				libtcod.console_put_char_ex(cd_anim_con, x, y, char, libtcod.light_blue,
					libtcod.black)
		
		# update snow display
		if self.animation['snow_active']:
			
			# update location of each snowflake
			for i in range(len(self.animation['snowflakes'])):
				(x, y, lifespan) = self.animation['snowflakes'][i]
				
				# respawn if finished
				if lifespan == 0:
					x = libtcod.random_get_int(0, 4, 36)
					y = libtcod.random_get_int(0, 0, 50)
					lifespan = libtcod.random_get_int(0, 4, 10)
				else:
					x += choice([-1, 0, 1])
					y += 1
					lifespan -= 1
				
				self.animation['snowflakes'][i] = (x, y, lifespan)
			
			# draw snowflakes to screen
			for (x, y, lifespan) in self.animation['snowflakes']:
				
				# skip if off screen
				if x < 0 or y > 50: continue
				
				libtcod.console_put_char_ex(cd_anim_con, x, y, 249, libtcod.white,
					libtcod.black)
		
		# reset update timer
		session.anim_timer  = time.time()
	
	
	# draw all campaign day consoles to screen
	def UpdateCDDisplay(self):
		libtcod.console_clear(con)
		
		libtcod.console_blit(daymap_bkg, 0, 0, 0, 0, con, 0, 0)			# background frame
		libtcod.console_blit(cd_map_con, 0, 0, 0, 0, con, 29, 6)		# terrain map
		libtcod.console_blit(cd_control_con, 0, 0, 0, 0, con, 29, 6, 1.0, 0.0)	# zone control layer
		libtcod.console_blit(cd_unit_con, 0, 0, 0, 0, con, 29, 6, 1.0, 0.0)	# unit group layer
		libtcod.console_blit(cd_gui_con, 0, 0, 0, 0, con, 29, 6, 1.0, 0.0)	# GUI layer
		
		libtcod.console_blit(cd_anim_con, 0, 0, 0, 0, con, 28, 7, 1.0, 0.0)	# animation console
		
		libtcod.console_blit(time_con, 0, 0, 0, 0, con, 36, 1)			# date and time
		
		libtcod.console_blit(cd_player_unit_con, 0, 0, 0, 0, con, 1, 1)		# player unit info		
		libtcod.console_blit(cd_command_con, 0, 0, 0, 0, con, 1, 18)		# command menu
		
		libtcod.console_blit(cd_weather_con, 0, 0, 0, 0, con, 71, 3)		# weather info
		libtcod.console_blit(cd_campaign_con, 0, 0, 0, 0, con, 66, 18)		# campaign info
		libtcod.console_blit(cd_hex_info_con, 0, 0, 0, 0, con, 66, 24)		# zone info
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	
	# main campaign day input loop
	def DoCampaignDayLoop(self):
		
		# consoles for day map interface
		global daymap_bkg, cd_map_con, cd_anim_con, cd_unit_con, cd_control_con, cd_command_con
		global cd_player_unit_con, cd_gui_con, time_con, cd_campaign_con, cd_weather_con
		global cd_hex_info_con
		global scenario
		
		# create consoles
		daymap_bkg = LoadXP('daymap_bkg.xp')
		cd_map_con = NewConsole(35, 53, libtcod.black, libtcod.white)
		cd_anim_con = NewConsole(36, 52, libtcod.black, libtcod.white)
		cd_unit_con = NewConsole(35, 53, KEY_COLOR, libtcod.white)
		cd_control_con = NewConsole(35, 53, KEY_COLOR, libtcod.red)
		cd_gui_con = NewConsole(35, 53, KEY_COLOR, libtcod.red)
		time_con = NewConsole(21, 5, libtcod.darkest_grey, libtcod.white)
		cd_player_unit_con = NewConsole(25, 16, libtcod.black, libtcod.white)
		cd_command_con = NewConsole(25, 41, libtcod.black, libtcod.white)
		cd_weather_con = NewConsole(14, 12, libtcod.black, libtcod.white)
		cd_campaign_con = NewConsole(23, 5, libtcod.black, libtcod.white)
		cd_hex_info_con = NewConsole(23, 35, libtcod.black, libtcod.white)
		
		# generate consoles for the first time
		self.UpdateCDMapCon()
		self.UpdateCDUnitCon()
		self.UpdateCDControlCon()
		self.UpdateCDGUICon()
		self.UpdateCDPlayerUnitCon()
		self.UpdateCDCommandCon()
		self.UpdateCDCampaignCon()
		self.UpdateCDHexInfoCon()
		DisplayWeatherInfo(cd_weather_con)
		DisplayTimeInfo(time_con)
		
		if self.scenario is not None:
			self.UpdateCDDisplay()
		
		# init looping animations
		self.InitAnimations()
		
		# calculate initial time to travel to front lines
		if not self.travel_time_spent:
			minutes = 45 + (libtcod.random_get_int(0, 1, 9) * 15)
			self.AdvanceClock(0, minutes, skip_checks=True)
			DisplayTimeInfo(time_con)
			text = 'It takes you ' + str(minutes) + ' minutes to travel to the front lines.'
			ShowMessage(text)
			self.travel_time_spent = True
		
		# record mouse cursor position to check when it has moved
		mouse_x = -1
		mouse_y = -1
		
		SaveGame()
		
		exit_loop = False
		while not exit_loop:
			
			# player was taken out of action
			if campaign.player_oob:
				self.DisplayCampaignDaySummary()
				exit_loop = True
				continue
			
			# if we've initiated a scenario or are resuming a saved game with a scenario
			# running, go into the scenario loop now
			if scenario is not None:
				
				scenario.DoScenarioLoop()
				
				if session.exiting:
					exit_loop = True
					continue
				
				# scenario is finished
				if scenario.finished:
					
					self.scenario = None
					scenario = None
					
					# tank was immobilized, abandoned, or destroyed: campaign day is over
					if campaign.player_unit.immobilized or not campaign.player_unit.alive:
						self.DisplayCampaignDaySummary()
						self.ended = True
						self.DoCrewCheck(campaign.player_unit)
						exit_loop = True
						continue
					
					# capture area if player is still alive
					(hx, hy) = self.player_unit_location
					self.map_hexes[(hx,hy)].CaptureMe(0)
					self.DoCrewCheck(campaign.player_unit)
					self.CheckForEndOfDay()
					self.UpdateCDDisplay()
					libtcod.console_flush()
					self.CheckForRandomEvent()
					self.CheckForZoneCapture(zone_just_captured=True)
					SaveGame()
					
					# check for automatic unbog
					if campaign.player_unit.bogged:
						ShowMessage('You free your tank from being bogged down.')
						campaign.player_unit.bogged = False
						self.UpdateCDPlayerUnitCon()
					
					# check for CD map shift
					self.CheckForCDMapShift()
					
				DisplayTimeInfo(time_con)
				self.UpdateCDCampaignCon()
				self.UpdateCDControlCon()
				self.UpdateCDUnitCon()
				self.UpdateCDCommandCon()
				self.UpdateCDHexInfoCon()
				self.UpdateCDDisplay()
			
			# check for end of campaign day
			if self.ended:
				ShowMessage('Your combat day has ended.')
				self.DisplayCampaignDaySummary()
				exit_loop = True
				continue
			
			# check for animation update
			if time.time() - session.anim_timer >= 0.20:
				self.UpdateAnimCon()
				self.UpdateCDDisplay()
			
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			keypress = GetInputEvent()
			
			# check to see if mouse cursor has moved
			if mouse.cx != mouse_x or mouse.cy != mouse_y:
				mouse_x = mouse.cx
				mouse_y = mouse.cy
				self.UpdateCDHexInfoCon()
				self.UpdateCDDisplay()
			
			if not keypress: continue
			
			# game menu
			if key.vk == libtcod.KEY_ESCAPE:
				ShowGameMenu()
				if session.exiting:
					exit_loop = True
					continue
			
			# debug menu
			elif key.vk == libtcod.KEY_F2:
				if not DEBUG: continue
				ShowDebugMenu()
				continue
			
			# mapped key commands
			key_char = DeKey(chr(key.c).lower())
			
			# switch active menu
			if key_char in ['1', '2', '3', '4', '5']:
				if self.active_menu != int(key_char):
					self.active_menu = int(key_char)
					self.UpdateCDGUICon()
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
				continue
			
			# support menu active
			if self.active_menu == 1:
				
				# request additional support (not keymapped)
				if chr(key.c).lower() == 'r':
					
					# increase air support
					if 'air_support_level' in campaign.current_week:
						maximum = campaign.current_week['air_support_level']
						if self.air_support_level == maximum:
							ShowMessage('Already at maximum support level.')
							continue
					
					# increase artillery support
					else:
						maximum = campaign.current_week['arty_support_level']
						if self.arty_support_level == maximum:
							ShowMessage('Already at maximum support level.')
							continue
					
					ShowMessage('You radio in a request for additional support.')
					self.AdvanceClock(0, 15)
					DisplayTimeInfo(time_con)
					
					if 'air_support_level' in campaign.current_week:
						self.air_support_level += float(libtcod.random_get_int(0, 1, 5)) * 5.0
						if self.air_support_level > maximum:
							self.air_support_level = maximum
					else:
						self.arty_support_level += float(libtcod.random_get_int(0, 1, 5)) * 5.0
						if self.arty_support_level > maximum:
							self.arty_support_level = maximum
					
					SaveGame()
					continue
			
			# crew menu active
			elif self.active_menu == 2:
				
				# change selected crew position
				if key_char in ['w', 's']:
					if key_char == 'w':
						self.selected_position -= 1
						if self.selected_position < 0:
							self.selected_position = len(campaign.player_unit.positions_list) - 1
				
					else:
						self.selected_position += 1
						if self.selected_position == len(campaign.player_unit.positions_list):
							self.selected_position = 0
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
					continue
				
				# open crewman menu
				elif key_char == 'f':
					crewman = campaign.player_unit.positions_list[self.selected_position].crewman
					if crewman is None: continue
					crewman.ShowCrewmanMenu()
					self.UpdateCDDisplay()
					continue
			
			# travel menu active
			elif self.active_menu == 3:
				
				# select direction
				DIRECTION_KEYS = ['e', 'd', 'c', 'z', 'a', 'q'] 
				if key_char in DIRECTION_KEYS:
					direction = DIRECTION_KEYS.index(key_char)
					if self.selected_direction is None:
						self.selected_direction = direction
					else:
						# cancel direction
						if self.selected_direction == direction:
							self.selected_direction = None
						else:
							self.selected_direction = direction
					self.UpdateCDGUICon()
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
					continue
				
				# wait/defend
				if key_char == 'w':
					
					if ShowNotification('Remain in place for 15 minutes?', confirm=True):
						ShowMessage('You remain in place, ready for possible attack.')
						self.selected_direction = None
						self.AdvanceClock(0, 15)
						DisplayTimeInfo(time_con)
						self.UpdateCDDisplay()
						self.CheckForRandomEvent()
						self.CheckForZoneCapture()
						SaveGame()
					continue
				
				# toggle advancing fire
				if key_char == 't':
					self.advancing_fire = not self.advancing_fire
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
					SaveGame()
					continue
				
				# toggle air support request
				if key_char == 'g':
					if 'air_support_level' not in campaign.current_week:
						continue
					if self.weather['Cloud Cover'] == 'Overcast':
						continue
					self.air_support_request = not self.air_support_request
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
					SaveGame()
					continue
				
				# toggle artillery support request
				if key_char == 'b':
					if 'arty_support_level' not in campaign.current_week:
						continue
					self.arty_support_request = not self.arty_support_request
					self.UpdateCDCommandCon()
					self.UpdateCDDisplay()
					SaveGame()
					continue
				
				# recon or proceed with travel
				if key_char == 'r' or key.vk == libtcod.KEY_ENTER:
					
					# no direction set
					if self.selected_direction is None: continue
					
					# ensure that travel/recon is possible
					(hx1, hy1) = self.player_unit_location
					#map_hex1 = self.map_hexes[(hx1,hy1)]
					(hx2, hy2) = self.GetAdjacentCDHex(hx1, hy1, self.selected_direction)
					if (hx2, hy2) not in self.map_hexes:
						continue
					map_hex2 = self.map_hexes[(hx2,hy2)]
					
					# recon
					if key_char == 'r':
						# already reconned
						if map_hex2.known_to_player: continue
						# not enemy-controlled
						if map_hex2.controlled_by == 0: continue
						map_hex2.known_to_player = True
						text = 'Estimated enemy strength in zone: ' + str(map_hex2.enemy_strength)
						ShowMessage(text)
						campaign_day.AdvanceClock(0, 15)
						DisplayTimeInfo(time_con)
						self.UpdateCDUnitCon()
						self.UpdateCDCommandCon()
						self.UpdateCDHexInfoCon()
						self.UpdateCDDisplay()
						self.CheckForRandomEvent()
						
					# travel
					else:
						
						# get travel time and check for river block
						mins = self.CalculateTravelTime(hx1,hy1,hx2,hy2)
						
						# travel not allowed
						if mins == -1:
							ShowMessage('Route blocked by river crossing, cannot proceed.')
							continue
						
						# clear selected direction
						self.selected_direction = None
						self.UpdateCDGUICon()
						
						# calculate animation path
						(x,y) = self.PlotCDHex(hx1, hy1)
						(x2,y2) = self.PlotCDHex(hx2, hy2)
						x2 -= x
						y2 -= y
						line = GetLine(0, 0, x2, y2)
						
						# do sound effect
						PlaySoundFor(campaign.player_unit, 'movement')
						
						# show animation
						for (x, y) in line:
							session.cd_x_offset = x
							session.cd_y_offset = y
							self.UpdateCDUnitCon()
							self.UpdateCDDisplay()
							Wait(20)
						session.cd_x_offset = 0
						session.cd_y_offset = 0
					
						# advance clock
						campaign_day.AdvanceClock(0, mins)
						
						# set new player location and clear travel direction
						self.player_unit_location = (hx2, hy2)
						
						self.UpdateCDUnitCon()
						DisplayWeatherInfo(cd_weather_con)
						self.UpdateCDDisplay()
						
						# roll to trigger battle encounter if enemy-controlled
						if map_hex2.controlled_by == 1:
							
							text = 'You enter the enemy-held zone'
							if self.advancing_fire:
								text += ', firing at anything suspicious'
								
								# try to use ammo for main gun
								weapon = campaign.player_unit.weapon_list[0]
								if weapon.GetStat('type') == 'Gun':
									if 'HE' in weapon.ammo_stores:
										weapon.ammo_stores['HE'] -= libtcod.random_get_int(0, 4, 10)
										if weapon.ammo_stores['HE'] < 0:
											weapon.ammo_stores['HE'] = 0
								# FUTURE: how to handle tanks where main weapon is MG or similar, or no HE?
								# Don't allow advancing fire?
								
							ShowMessage(text + '.')
							
							# roll for scenario trigger
							roll = GetPercentileRoll()
							roll -= campaign_day.encounter_mod
							
							if DEBUG:
								if session.debug['Always Scenario']:
									roll = 1.0
								elif session.debug['Never Scenario']:
									roll = 100.0
							
							if roll <= (float(map_hex2.enemy_strength) * 9.5):
								ShowMessage('You encounter enemy resistance!')
								self.AdvanceClock(0, 15)
								scenario = Scenario(map_hex2)
								self.scenario = scenario
								self.encounter_mod = 0.0
								self.AddRecord('Battles Fought', 1)
								continue
							
							ShowMessage('You find no resistance and gain control of the area.')
							self.map_hexes[(hx2,hy2)].CaptureMe(0)
							self.encounter_mod += 30.0
							
							# spend support costs and reset flags
							if self.air_support_request:
								if GetPercentileRoll() <= self.air_support_level:
									self.air_support_level -= 10.0
								if self.air_support_level < 0.0:
									self.air_support_level = 0.0
								self.air_support_request = False
							
							if self.arty_support_request:
								if GetPercentileRoll() <= self.arty_support_level:
									self.arty_support_level -= 10.0
								if self.arty_support_level < 0.0:
									self.arty_support_level = 0.0
								self.arty_support_request = False
						
						# entering a friendly zone
						else:
							ShowMessage('You enter the allied-held zone.')
						
						# no battle triggered, check for map shift
						self.CheckForCDMapShift()
						
						# update consoles
						DisplayTimeInfo(time_con)
						self.UpdateCDCampaignCon()
						self.UpdateCDControlCon()
						self.UpdateCDUnitCon()
						self.UpdateCDCommandCon()
						self.UpdateCDHexInfoCon()
						self.UpdateCDDisplay()
						self.CheckForZoneCapture(zone_just_captured=True)
						self.CheckForRandomEvent()
					
					SaveGame()
				
			# main gun menu active
			elif self.active_menu == 5:
				
				weapon = campaign.player_unit.weapon_list[0]
				if weapon.GetStat('type') == 'Gun':
					
					# cycle active ammo type
					if key_char == 'c':
						if weapon.CycleAmmo():
							self.UpdateCDCommandCon()
							self.UpdateCDDisplay()
						continue
				
					# move shell to/from ready rack
					elif key_char in ['a', 'd']:
						if key_char == 'a':
							add_num = -1
						else:
							add_num = 1
						
						if weapon.ManageRR(add_num):
							self.UpdateCDCommandCon()
							self.UpdateCDDisplay()
						continue
					
				# request resupply
				if key_char == 'r':
					
					# check for clear path to friendly edge
					path_good = False
					(hx1, hy1) = self.player_unit_location
					
					if hy1 == 8:
						path_good = True
					else:
						for hx2 in range(-4, 1):
							if len(GetHexPath(hx1, hy1, hx2, 8, enemy_zones_block=True)) != 0:
								path_good = True
								break
					if not path_good:
						ShowMessage('You are cut off from friendly forces! No resupply possible.')
						continue
					
					if ShowNotification('Spend 30 minutes waiting for resupply?', confirm=True):
						ShowMessage('You contact HQ for resupply, which arrives 30 minutes later.')
						
						# spend time
						self.AdvanceClock(0, 30)
						DisplayTimeInfo(time_con)
						self.UpdateCDDisplay()
						
						# allow player to replenish ammo
						self.AmmoReloadMenu()
						self.UpdateCDDisplay()
						
						# check for player squad replenishment
						if campaign.player_squad_num < campaign.player_squad_max:
		
							campaign.player_squad_num = campaign.player_squad_max
							ShowMessage('You are joined by reserve units, bringing your squad back up to full strength.')
						
						self.UpdateCDDisplay()
						self.CheckForZoneCapture()
						self.CheckForRandomEvent()
						SaveGame()
					continue


# Zone Hex: a hex on the campaign day map, each representing a map of scenario hexes
class CDMapHex:
	def __init__(self, hx, hy, mission):
		self.hx = hx
		self.hy = hy
		
		self.terrain_type = ''		# placeholder for terrain type in this zone
		self.console_seed = libtcod.random_get_int(0, 1, 128)	# seed for console image generation
		
		self.dirt_roads = []		# directions linked by a dirt road
		self.stone_roads = []		# " stone road
		self.rivers = []		# river edges
		self.bridges = []		# bridged edges
		
		self.controlled_by = 1		# which player side currently controls this zone
		self.known_to_player = False	# player knows enemy strength and organization in this zone
		
		self.objective = None		# player objective for this zone
		
		# Pathfinding stuff
		self.parent = None
		self.g = 0
		self.h = 0
		self.f = 0
		
		# set enemy strength level
		if 'average_resistance' in campaign.current_week:
			avg_strength = int(campaign.current_week['average_resistance'])
		else:
			avg_strength = 5
		
		# apply mission modifiers
		if mission == 'Advance':
			avg_strength -= 1
		elif mission in ['Battle', 'Fighting Withdrawl']:
			avg_strength += 2
		elif mission == 'Counterattack':
			avg_strength += 1
		
		# roll for actual strength level
		self.enemy_strength = 0
		for i in range(2):
			self.enemy_strength += libtcod.random_get_int(0, 0, avg_strength)
		self.enemy_strength = int(self.enemy_strength / 2)
		
		if self.enemy_strength < 1:
			self.enemy_strength = 1
		elif self.enemy_strength > 10:
			self.enemy_strength = 10
		
		self.Reset()
	
	
	# reset zone stats
	def Reset(self):
		self.coordinate = (chr(self.hy+65) + str(5 + int(self.hx - (self.hy - self.hy&1) / 2)))
	
	
	# reset pathfinding info for this zone
	def ClearPathInfo(self):
		self.parent = None
		self.g = 0
		self.h = 0
		self.f = 0
	
	
	# generate a random terrain type for this zone hex
	def GenerateTerrainType(self):
		roll = GetPercentileRoll()
		terrain_dict = REGIONS[campaign.stats['region']]['cd_terrain_odds']
		for terrain_type, odds in terrain_dict.items():
			if roll <= odds:
				self.terrain_type = terrain_type
				return
			roll -= odds
	
	
	# set up a new objective in this CD hex or clear it
	def SetObjective(self, objective_dict):
		self.objective = objective_dict
	
	
	# set control of this hex by the given player
	# also handles successful defense of a friendly zone
	# if no_vp is True, player doesn't receive VP or credit for this capture
	def CaptureMe(self, player_num, no_vp=False):
		
		# if captured by enemy, we can just set the zone control and then return
		if player_num == 1:
			self.controlled_by = player_num
			return
		
		# check for VP reward
		if not no_vp:
			
			if self.controlled_by == 1:
				campaign_day.AddRecord('Map Areas Captured', 1)
				if campaign_day.mission == 'Advance':
					campaign.AwardVP(2)
				else:
					campaign.AwardVP(1)
			
			elif self.controlled_by == 0:
				campaign_day.AddRecord('Map Areas Defended', 1)
				if campaign_day.mission == 'Fighting Withdrawl':
					campaign.AwardVP(4)
				elif campaign_day.mission == 'Counterattack':
					campaign.AwardVP(2)
				else:
					campaign.AwardVP(1)
		
			# check for objective reward
			if self.objective is not None:
				
				if self.controlled_by == 0 and self.objective['objective_type'] == 'Defend':
					campaign.AwardVP(2)
					ShowMessage('You have defended an objective!')
				
				elif self.controlled_by == 1 and self.objective['objective_type'] == 'Capture':
					campaign.AwardVP(2)
					ShowMessage('You have captured an objective!')
		
		# set new zone control
		self.controlled_by = player_num
		
		# clear the objective if any
		self.objective = None



# Session: stores data that is generated for each game session and not stored in the saved game
class Session:
	def __init__(self):
		
		# flag for when player is exiting from game
		self.exiting = False
		
		# pointer to player unit
		self.player_unit = None
		
		# flag: the last time the keyboard was polled, a key was pressed
		self.key_down = False
		
		# load debug flags if in debug mode
		self.debug = {}
		if DEBUG:
			with open(DATAPATH + 'debug.json', encoding='utf8') as data_file:
				self.debug = json.load(data_file)
		
		# store player crew command defintions
		with open(DATAPATH + 'crew_command_defs.json', encoding='utf8') as data_file:
			self.crew_commands = json.load(data_file)
		
		# store nation definition info
		with open(DATAPATH + 'nation_defs.json', encoding='utf8') as data_file:
			self.nations = json.load(data_file)
		
		# load national flag images
		self.flags = {}
		for name, data in self.nations.items():
			self.flags[name] = LoadXP(data['flag_image'])
		
		# background for attack console
		self.attack_bkg = LoadXP('attack_bkg.xp')
		
		# field of view highlight on scenario hex map
		self.scen_hex_fov = LoadXP('scen_hex_fov.xp')
		libtcod.console_set_key_color(self.scen_hex_fov, KEY_COLOR)
		
		# animation timer, used by both the campaign day and the scenario object
		self.anim_timer = 0.0
		
		# pop-up message console
		self.msg_con = None
		self.msg_location = None
		
		# tank portrait for main menu
		self.tank_portrait = None
		with open(DATAPATH + 'unit_type_defs.json', encoding='utf8') as data_file:
			unit_types = json.load(data_file)
		for tries in range(300):
			unit_id = choice(list(unit_types.keys()))
			if 'portrait' not in unit_types[unit_id]: continue
			if unit_types[unit_id]['class'] not in ['Light Tank', 'Medium Tank', 'Heavy Tank', 'Tank Destroyer']: continue
			self.tank_portrait = LoadXP(unit_types[unit_id]['portrait'])
			break
		del unit_types
		
		# campaign day map player unit animation offset
		self.cd_x_offset = 0
		self.cd_y_offset = 0
		
	
	# try to initialize SDL2 mixer
	def InitMixer(self):
		mixer.Mix_Init(mixer.MIX_INIT_OGG)
		if mixer.Mix_OpenAudio(48000, mixer.MIX_DEFAULT_FORMAT,	2, 1024) == -1:
			print('ERROR in Mix_OpenAudio: ' + mixer.Mix_GetError())
			return False
		mixer.Mix_AllocateChannels(16)
		return True
	
	# load the main theme music
	def LoadMainTheme(self):
		global main_theme
		main_theme = mixer.Mix_LoadMUS((SOUNDPATH + 'armcom2_theme.ogg').encode('ascii'))
		mixer.Mix_VolumeMusic(80)



# Personnel Class: represents an individual person within a unit 
class Personnel:
	def __init__(self, unit, nation, position):
		self.unit = unit				# pointer to which unit they belong
		self.nation = nation				# nationality of person
		self.current_position = position		# pointer to current position in a unit
		
		self.first_name = ''				# placeholders for first and last name
		self.last_name = ''				#   set by GenerateName()
		self.GenerateName()				# generate random first and last name
		self.nickname = ''				# player-set nickname
		self.age = 21					# age in years
		self.rank = 0					# rank level
		
		self.stats = {					# default stat values
			'Perception' : 1,
			'Grit' : 1,
			'Knowledge' : 1,
			'Morale' : 1
		}
		
		# randomly increase two stats to 3
		for i in sample(range(3), 2):
			self.stats[CREW_STATS[i]] = 3
		
		self.skills = []				# list of skills
		
		# current level, exp, and advance points
		self.level = 1
		self.exp = 0
		self.adv = 1
		
		# commanders start higher
		if self.current_position.name in ['Commander', 'Commander/Gunner']:
			self.level = 3
			self.exp = GetExpRequiredFor(self.level)
			self.adv = 3
			self.age += libtcod.random_get_int(0, 3, 8)
			self.rank = 3
		
		# gunners a little higher
		elif self.current_position.name in ['Gunner', 'Gunner/Loader']:
			self.level = 2
			self.exp = GetExpRequiredFor(self.level)
			self.adv = 2
			self.age += libtcod.random_get_int(0, 1, 4)
			self.rank = 2
		
		# exposed / buttoned up status
		self.ce = False					# crewman is exposed in a vehicle
		self.SetCEStatus()				# set CE status
		
		self.cmd_list = []				# list of possible commands
		self.current_cmd = 'Spot'			# currently assigned command in scenario
		
		self.status = ''				# current status: Stunned, Unconscious, or Dead
		self.wound = ''					# current wound: Light, Serious, or Critical
		
		self.bailed_out = False				# has bailed out of an AFV
	
	
	# award a number of exp to this crewman
	def AwardExp(self, exp):
		self.exp += exp
	
	# display a menu for this crewman, used for members of player's unit
	def ShowCrewmanMenu(self):
		
		# update the crewman menu console
		def UpdateCrewmanMenuCon():
			libtcod.console_clear(crewman_menu_con)
			
			# frame and section dividers
			libtcod.console_set_default_foreground(crewman_menu_con, libtcod.grey)
			DrawFrame(crewman_menu_con, 8, 2, 73, 56)
			DrawFrame(crewman_menu_con, 29, 2, 32, 56)
			libtcod.console_hline(crewman_menu_con, 30, 5, 30)
			libtcod.console_hline(crewman_menu_con, 30, 8, 30)
			libtcod.console_hline(crewman_menu_con, 30, 10, 30)
			libtcod.console_hline(crewman_menu_con, 30, 12, 30)
			libtcod.console_hline(crewman_menu_con, 30, 15, 30)
			libtcod.console_hline(crewman_menu_con, 30, 20, 30)
			libtcod.console_hline(crewman_menu_con, 30, 22, 30)
			libtcod.console_hline(crewman_menu_con, 30, 49, 30)
			
			# main title
			libtcod.console_set_default_background(crewman_menu_con, libtcod.darker_blue)
			libtcod.console_rect(crewman_menu_con, 30, 3, 30, 2, False, libtcod.BKGND_SET)
			libtcod.console_set_default_background(crewman_menu_con, libtcod.black)
			libtcod.console_set_default_foreground(crewman_menu_con, libtcod.lightest_blue)
			libtcod.console_print(crewman_menu_con, 38, 3, 'Crewman Report')
			
			# section titles
			libtcod.console_set_default_foreground(crewman_menu_con, TITLE_COL)
			libtcod.console_print(crewman_menu_con, 30, 6, 'Name')
			libtcod.console_print(crewman_menu_con, 30, 9, 'Age')
			libtcod.console_print(crewman_menu_con, 30, 11, 'Rank')
			libtcod.console_print(crewman_menu_con, 30, 13, 'Current')
			libtcod.console_print(crewman_menu_con, 30, 14, 'Position')
			libtcod.console_print(crewman_menu_con, 30, 16, 'Stats')
			libtcod.console_print(crewman_menu_con, 30, 21, 'Status')
			libtcod.console_print(crewman_menu_con, 30, 23, 'Skills')
			libtcod.console_print(crewman_menu_con, 30, 50, 'Wounds')
			
			
			# info
			libtcod.console_set_default_foreground(crewman_menu_con, libtcod.white)
			self.DisplayName(crewman_menu_con, 39, 6)
			if self.nickname != '':
				libtcod.console_print(crewman_menu_con, 39, 7, self.nickname)
			
			# age and rank
			libtcod.console_print(crewman_menu_con, 39, 9, str(self.age))
			libtcod.console_print(crewman_menu_con, 39, 11, session.nations[self.nation]['rank_names'][str(self.rank)])
			
			
			# current position
			libtcod.console_print(crewman_menu_con, 39, 13, self.unit.unit_id)
			libtcod.console_print(crewman_menu_con, 39, 14, self.current_position.name)
			
			# stats
			libtcod.console_put_char_ex(crewman_menu_con, 39, 16, chr(4), libtcod.yellow, libtcod.black)
			libtcod.console_put_char_ex(crewman_menu_con, 39, 17, chr(3), libtcod.red, libtcod.black)
			libtcod.console_put_char_ex(crewman_menu_con, 39, 18, chr(5), libtcod.blue, libtcod.black)
			libtcod.console_put_char_ex(crewman_menu_con, 39, 19, chr(6), libtcod.green, libtcod.black)
			
			y = 16
			for t in CREW_STATS:
				libtcod.console_set_default_foreground(crewman_menu_con, libtcod.white)
				libtcod.console_print(crewman_menu_con, 41, y, t)
				libtcod.console_set_default_foreground(crewman_menu_con, libtcod.light_grey)
				libtcod.console_print_ex(crewman_menu_con, 53, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, str(self.stats[t]))
				y += 1
			
			libtcod.console_set_default_background(crewman_menu_con, libtcod.darkest_grey)
			libtcod.console_rect(crewman_menu_con, 39, 17, 15, 1, False, libtcod.BKGND_SET)
			libtcod.console_rect(crewman_menu_con, 39, 19, 15, 1, False, libtcod.BKGND_SET)
			libtcod.console_set_default_background(crewman_menu_con, libtcod.black)
			
			# status
			if self.status == '':
				text = 'Good Order'
			else:
				text = self.status
			libtcod.console_print(crewman_menu_con, 39, 21, text)
			
			# list of crew skills
			y = 23
			number_of_skills = 0
			libtcod.console_set_default_foreground(crewman_menu_con, libtcod.white)
			for skill in self.skills:
				libtcod.console_print(crewman_menu_con, 39, y, skill)
				y += 1
				number_of_skills += 1
			libtcod.console_print(crewman_menu_con, 39, y, '[Add New Skill]')
			
			# highlight selected skill
			libtcod.console_set_default_background(crewman_menu_con, HIGHLIGHT_MENU_COL)
			libtcod.console_rect(crewman_menu_con, 39, 23 + selected_skill, 21, 1, False, libtcod.BKGND_SET)
			libtcod.console_set_default_background(crewman_menu_con, libtcod.black)
			
			# display info about selected skill or info about adding a new skill
			libtcod.console_set_default_foreground(crewman_menu_con, TITLE_COL)
			libtcod.console_print(crewman_menu_con, 67, 23, 'Info')
			libtcod.console_set_default_foreground(crewman_menu_con, libtcod.light_grey)
			y = 25
			if selected_skill == number_of_skills:
				text = 'Select this option to spend an advance point and add a new skill'
			else:
				# grab skill description from campaign.skills dictionary
				text = campaign.skills[self.skills[selected_skill]]['desc']
			for line in wrap(text, 18):
				libtcod.console_print(crewman_menu_con, 62, y, line)
				y+=1	
			
			# current level, exp, points
			libtcod.console_set_default_background(crewman_menu_con, libtcod.darkest_grey)
			libtcod.console_rect(crewman_menu_con, 30, 46, 21, 3, False, libtcod.BKGND_SET)
			libtcod.console_set_default_background(crewman_menu_con, libtcod.black)
			
			libtcod.console_set_default_foreground(crewman_menu_con, TITLE_COL)
			libtcod.console_print(crewman_menu_con, 30, 46, 'Level')
			libtcod.console_print(crewman_menu_con, 30, 47, 'Exp')
			libtcod.console_print(crewman_menu_con, 30, 48, 'Advance Points')
			
			libtcod.console_set_default_foreground(crewman_menu_con, libtcod.white)
			libtcod.console_print_ex(crewman_menu_con, 50, 46, libtcod.BKGND_NONE,
				libtcod.RIGHT, str(self.level))
			libtcod.console_print_ex(crewman_menu_con, 50, 47, libtcod.BKGND_NONE,
				libtcod.RIGHT, str(self.exp))
			libtcod.console_print_ex(crewman_menu_con, 50, 48, libtcod.BKGND_NONE,
				libtcod.RIGHT, str(self.adv))
			
			# wounds if any
			if self.wound == '':
				text = 'None'
				col = libtcod.light_grey
			else:
				text = self.wound
				col = libtcod.red
			libtcod.console_set_default_foreground(crewman_menu_con, col)
			libtcod.console_print(crewman_menu_con, 39, 50, text)
			
			
			# player commands
			libtcod.console_set_default_foreground(crewman_menu_con, ACTION_KEY_COL)
			libtcod.console_print(crewman_menu_con, 10, 28, '1')
			libtcod.console_print(crewman_menu_con, 10, 29, '2')
			libtcod.console_print(crewman_menu_con, 10, 30, '3')
			libtcod.console_print(crewman_menu_con, 10, 31, '4')
			
			libtcod.console_print(crewman_menu_con, 10, 33, EnKey('w').upper() + '/' + EnKey('s').upper())
			if selected_skill == number_of_skills:
				libtcod.console_print(crewman_menu_con, 10, 34, EnKey('f').upper())
			libtcod.console_print(crewman_menu_con, 10, 35, 'Esc')
			
			libtcod.console_set_default_foreground(crewman_menu_con, libtcod.light_grey)
			libtcod.console_print(crewman_menu_con, 14, 28, 'Increase')
			libtcod.console_print(crewman_menu_con, 14, 29, 'Increase')
			libtcod.console_print(crewman_menu_con, 14, 30, 'Increase')
			libtcod.console_print(crewman_menu_con, 14, 31, 'Increase')
			libtcod.console_put_char_ex(crewman_menu_con, 23, 28, chr(4), libtcod.yellow, libtcod.black)
			libtcod.console_put_char_ex(crewman_menu_con, 23, 29, chr(3), libtcod.red, libtcod.black)
			libtcod.console_put_char_ex(crewman_menu_con, 23, 30, chr(5), libtcod.blue, libtcod.black)
			libtcod.console_put_char_ex(crewman_menu_con, 23, 31, chr(6), libtcod.green, libtcod.black)
			
			libtcod.console_print(crewman_menu_con, 14, 33, 'Select Skill')
			if selected_skill == number_of_skills:
				libtcod.console_print(crewman_menu_con, 14, 34, 'Add New Skill')	
			libtcod.console_print(crewman_menu_con, 14, 35, 'Exit Menu')
			
			libtcod.console_blit(crewman_menu_con, 0, 0, 0, 0, 0, 0, 0)
			
			return number_of_skills
			
		
		global crewman_menu_con
		crewman_menu_con = NewConsole(WINDOW_WIDTH, WINDOW_HEIGHT, libtcod.black, libtcod.white)
		
		selected_skill = 0				# which crew skill is currently selected
		number_of_skills = 0				# how many skills this crewman has
		
		# draw screen for first time (also counts current number of crewman skills)
		number_of_skills = UpdateCrewmanMenuCon()
		
		exit_menu = False
		while not exit_menu:
			
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			keypress = GetInputEvent()
			
			if not keypress: continue
			
			# exit menu
			if key.vk == libtcod.KEY_ESCAPE:
				exit_menu = True
				continue
			
			key_char = DeKey(chr(key.c).lower())
			
			# increase stat
			if key_char in ['1', '2', '3', '4']:
				
				stat_name = CREW_STATS[int(key_char) - 1]
				
				if self.stats[stat_name] == 10:
					ShowNotification('Stat already at maximum level.')
					continue
				
				# make sure crewman has 1+ advance point available
				pt_cost = 1
				if DEBUG:
					if session.debug['Free Crew Advances']:
						pt_cost = 0
				
				if self.adv - pt_cost < 0:
					ShowNotification('Crewman has no Advance Points remaining.')
					continue
				
				# determine increase amount
				if self.stats[stat_name] < 5:
					increase = 2
				else:
					increase = 1
				
				if ShowNotification('Spend an advance point and increase ' + stat_name + ' by ' + str(increase) + '?', confirm=True):
					self.adv -= pt_cost
					self.stats[stat_name] += increase
					UpdateCrewmanMenuCon()
					PlaySoundFor(None, 'add skill')
					SaveGame()
				
				continue
			
			# change selected skill
			elif key_char in ['w', 's']:
				
				if key_char == 'w':
					if selected_skill == 0:
						selected_skill = number_of_skills
					else:
						selected_skill -= 1
				else:
					if selected_skill == number_of_skills:
						selected_skill = 0
					else:
						selected_skill += 1
				
				UpdateCrewmanMenuCon()
				continue
			
			# display add skill menu
			elif key_char == 'f' and selected_skill == number_of_skills:
				result = ShowSkillMenu(self)
				if result != '':
					# spend an advance point and add the skill
					if DEBUG:
						if session.debug['Free Crew Advances']:
							self.adv += 1
					self.adv -= 1
					self.skills.append(result)
					PlaySoundFor(None, 'add skill')
					SaveGame()
					number_of_skills = UpdateCrewmanMenuCon()
				continue

	
	# generate a random first and last name for this person
	def GenerateName(self):
		
		name_okay = False
		while not name_okay:
			first_name = choice(session.nations[self.nation]['first_names'])
			last_name = choice(session.nations[self.nation]['surnames'])
			if first_name == last_name:
				continue
			name_okay = True
		self.first_name = first_name
		self.last_name = last_name
	
	
	# display this crewman's name to the screen, required because crew names use extended characters
	def DisplayName(self, console, x, y, firstname_only = False, lastname_only = False, first_initial = False):
	
		CHAR_MAP = {
			'Ą' : 256,
			'Ć' : 257,
			'Ę' : 258,
			'Ł' : 259,
			'Ń' : 260,
			'Ó' : 261,
			'Ś' : 262,
			'Ź' : 263,
			'Ż' : 264,
			'ą' : 265,
			'ć' : 266,
			'ę' : 267,
			'ł' : 268,
			'ń' : 269,
			'ó' : 270,
			'ś' : 271,
			'ź' : 272,
			'ż' : 273
		}
		
		# determine raw text string to use
		if firstname_only:
			name = self.first_name
		elif lastname_only:
			name = self.last_name
		elif first_initial:
			name = self.first_name[0] + '. ' + self.last_name
		else:
			name = self.first_name + ' ' + self.last_name
		
		cx = x
		for char in name:
			
			if char in CHAR_MAP:
				char_code = CHAR_MAP[char]
			else:
				char_code = ord(char.encode('IBM850'))
			
			libtcod.console_put_char(console, cx, y, char_code)
			cx += 1
	
	
	# return the effective modifier for a given action, based on relevant stat and current status
	def GetActionMod(self, action_type):
		
		modifier = 0.0
		
		if self.status in ['Dead', 'Unconscious']: return modifier
		
		if action_type == 'Spotting':
			modifier = float(self.stats['Perception']) * PERCEPTION_SPOTTING_MOD
			if not self.ce:
				modifier = modifier * 0.25
		elif action_type == 'Attempt HD':
			modifier = float(self.stats['Knowledge']) * 3.0
			if not self.ce:
				modifier = modifier * 0.5
		elif action_type == 'Direct Movement':
			modifier = float(self.stats['Knowledge']) * 2.0
			if not self.ce:
				modifier = modifier * 0.5
		elif action_type == 'Direct Fire':
			modifier = float(self.stats['Knowledge']) * 3.5
			if not self.ce:
				modifier = modifier * 0.5
		
		# modify by current status
		if self.status == 'Stunned':
			modifier = modifer * 0.5
		
		modifier = round(modifier, 1)
				
		return modifier 
	
	
	# check to see whether this personnel is wounded/KIA and return result if any
	def DoWoundCheck(self, fp=0, roll_modifier=0.0, show_messages=True, auto_kill=False, auto_serious=False):
		
		# can't get worse
		if self.status == 'Dead': return None
		
		# only show messages if this is the player unit
		if self.unit != scenario.player_unit: show_messages = False
		
		# final wound roll modifier
		modifier = 0
		
		# exposed to an fp attack
		if fp > 0:
			
			# currently in an armoured vehicle
			if self.unit.GetStat('armour') is not None:
				
				# not exposed
				if not self.ce: return None
				
				# Unconcious crew are assumed to be slumped down and are protected
				if self.status == 'Unconscious': return None
				
				if fp <= 4:
					modifier -= 10.0
				elif fp <= 6:
					modifier -= 5.0
				elif 8 < fp <= 10:
					modifier += 5.0
				elif fp <= 12:
					modifier += 10.0
				elif fp <= 16:
					modifier += 15.0
				else:
					modifier += 20.0
		
		# apply additional modifier if any
		modifier += roll_modifier
				
		# roll for wound
		roll = GetPercentileRoll()
		
		if DEBUG:
			if session.debug['Player Crew Hapless']:
				roll = 100.0
		if auto_kill:
			roll = 100.0
		elif auto_serious:
			roll = 85.0
		else:
		
			# unmodified 99.0-100.0 always counts as KIA, otherwise modifier is applied
			if roll < 99.0:
				roll += modifier

		if roll < 45.0:
			
			# near miss - no wound or other effect
			return None
		
		elif roll <= 55.0:
			
			if self.status in ['Stunned', 'Unconscious']:
				return None
				
			self.DoStunCheck(0)
			if self.status == 'Stunned':
				if show_messages:
					ShowMessage('Your ' + self.current_position.name + ' has been Stunned.')
				return 'Stunned'
			return None
		
		elif roll <= 70.0:
			
			if self.wound in ['Serious', 'Critical']: return None
			
			# light wound and possible stun
			self.wound = 'Light'
			if self.status not in ['Stunned', 'Unconscious']:
				self.DoStunCheck(15)
				if self.status == 'Stunned':
					if show_messages:
						ShowMessage('Your ' + self.current_position.name + ' has received a Light Wound and has been Stunned.')
					return 'Light Wound, Stunned'
			
			if show_messages:
				ShowMessage('Your ' + self.current_position.name + ' has received a Light Wound.')
			return 'Light Wound'
				
			
		elif roll <= 85.0:
			
			if self.wound == 'Critical': return None
			
			# serious wound, possibly knocked unconscious, otherwise stunned
			self.wound = 'Serious'
			
			if self.status != 'Unconscious':
				self.DoKOCheck(0)
				if self.status == 'Unconscious':
					if show_messages:
						ShowMessage('Your ' + self.current_position.name + ' has received a Serious Wound ' +
							'and has been knocked Unconscious')
					return 'Serious Wound, Unconscious'
			
			if show_messages:
				ShowMessage('Your ' + self.current_position.name + ' has received a Serious Wound and is Stunned.')
			return 'Serious Wound, Stunned'
			
			
		elif roll <= 97.0:
			
			# critical wound, possibly knocked unconscious, otherwise stunned, may die next recovery check
			self.wound = 'Critical'
			
			if self.status != 'Unconscious':
				self.DoKOCheck(15)
				if self.status == 'Unconscious':
					if show_messages:
						ShowMessage('Your ' + self.current_position.name + ' has received a Critical Wound ' +
							'and has been knocked Unconscious.')
					return 'Critical Wound, Unconscious'
				
				if show_messages:
					ShowMessage('Your ' + self.current_position.name + ' has received a Critical Wound and is Stunned.')
				return 'Critical Wound, Stunned'
		
		else:
			
			# killed
			self.status = 'Dead'
			self.wound = ''
			
			if show_messages:
				if self.current_position.name in PLAYER_POSITIONS:
					ShowMessage('You have been killed. Your campaign is over.')
				else:
					ShowMessage('Your ' + self.current_position.name + ' has been killed.')
			
			# check for commander death
			if self.current_position.name in PLAYER_POSITIONS:
				scenario.finished = True
				campaign_day.ended = True
				campaign.ended = True
				campaign.player_oob = True
			return 'Dead'
				
	
	# check to see if this personnel is Stunned
	def DoStunCheck(self, modifier):
		
		# can't make it worse
		if self.status in ['Stunned', 'Unconscious', 'Dead']: return
		
		roll = GetPercentileRoll() + modifier
		
		# roll passed
		if roll <= self.stats['Grit'] * 15.0: return
		
		self.status = 'Stunned'


	# check to see if this personnel is knocked unconscious
	def DoKOCheck(self, modifier):
		
		if self.status in ['Unconscious', 'Dead']: return False
		roll = GetPercentileRoll() + modifier
		if roll <= self.stats['Grit'] * 10.0:
			# not knocked out, but Stunned
			self.status = 'Stunned'
			return
		self.status = 'Unconscious'


	# check for recovery from any current status
	def DoRecoveryCheck(self):
		if self.status in ['', 'Dead']: return
		
		roll = GetPercentileRoll()
		if self.status == 'Unconscious': roll += 15.0
		
		if self.status == 'Critical':
			if roll > 97.0:
				self.status = 'Dead'
				self.wound = ''
				if self.unit == scenario.player_unit:
					ShowMessage('Your ' + self.current_position.name + ' has died from his wounds.')
			return
		
		if roll <= self.stats['Grit'] * 15.0:
			
			if self.status == 'Stunned':
				self.status = ''
				if self.unit == scenario.player_unit:
					ShowMessage('Your ' + self.current_position.name + ' recovers from being Stunned.')
			
			# unconscious
			else:
				self.status = 'Stunned'
				if self.unit == scenario.player_unit:
					ShowMessage('Your ' + self.current_position.name + ' regains consciousness and is now Stunned.')

	
	# (re)build a list of possible commands for this turn
	def BuildCommandList(self):
		self.cmd_list = []
		
		# unconscious and dead crewmen cannot act
		if self.status in ['Unconscious', 'Dead']:
			self.cmd_list.append('None')
			return
		
		for (k, d) in session.crew_commands.items():
			
			# don't add "None" automatically
			if k == 'None': continue
			
			# weapon operation needs a weapon in the unit
			if k in ['Operate Gun', 'Operate MG']:
				
				for weapon in self.unit.weapon_list:
					
					if k == 'Operate Gun' and weapon.GetStat('type') != 'Gun': continue
					if k == 'Operate MG' and weapon.GetStat('type') not in MG_WEAPONS: continue
					if weapon.GetStat('fired_by') is None: continue
					if self.current_position.name not in weapon.GetStat('fired_by'): continue
					
					# add the command to fire this weapon
					self.cmd_list.append(k)
					
				continue
			
			# manage ready rack needs a gun
			if k == 'Manage Ready Rack':
				for weapon in self.unit.weapon_list:
					if weapon.GetStat('type') != 'Gun': continue
					crewman_ok = False
					if weapon.GetStat('fired_by') is not None:
						if self.current_position.name in weapon.GetStat('fired_by'):
							crewman_ok = True
					if weapon.GetStat('reloaded_by') is not None:
						if self.current_position.name in weapon.GetStat('reloaded_by'):
							crewman_ok = True
					if crewman_ok:
						self.cmd_list.append(k)
				continue
			
			if 'position_list' in d:
				if self.current_position.name not in d['position_list']:
					continue
			
			if k == 'Abandon Tank':
				can_abandon = False
				if self.unit.immobilized:
					can_abandon = True 
				for position in self.unit.positions_list:
					if position.crewman is None: continue
					if position.crewman.status == 'Dead' or position.crewman.wound in ['Critical']:
						can_abandon = True
						break
				if not can_abandon:
					continue
			
			# can't drive if vehicle is immobilized or bogged
			elif k == 'Drive':
				if self.unit.immobilized: continue
				if self.unit.bogged: continue
			
			# can only unbog if vehicle is already bogged
			elif k == 'Attempt Unbog':
				if not self.unit.bogged: continue
			
			# check that a mortar is attached and is fired by this position
			elif k == 'Fire Smoke Mortar':
				position_name = self.unit.GetStat('smoke_mortar')
				if position_name is None: continue
				if self.current_position.name != position_name: continue
			
			# add the command
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
		
		# crewman unable to act
		if self.status in ['Dead', 'Unconscious']: return False
		
		self.current_position.hatch_open = not self.current_position.hatch_open
		
		# set CE status based on new hatch status
		self.SetCEStatus()
		
		# change other hatches in this group if any
		if self.current_position.hatch_group is None:
			return True
			
		for position in self.unit.positions_list:
			if position.hatch_group is None: continue
			if position.hatch_group == self.current_position.hatch_group:
				# set the hatch to this one's current status
				position.hatch_open = self.current_position.hatch_open
				# set CE status for crewman in position with linked hatch
				if position.crewman is not None:
					position.crewman.SetCEStatus()
		
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
		if not session.crew_commands[self.crewman.current_cmd]['spotting_allowed']:
			return
		
		if self.hatch_open:
			direction_list = self.ce_visible
		else:
			direction_list = self.bu_visible
		
		# rotate based on hull or turret facing
		rotate = 0
		if self.location == 'Hull':
			if self.unit.facing is not None:
				rotate = self.unit.facing
		elif self.location == 'Turret':
			if self.unit.turret_facing is not None:
				rotate = self.unit.turret_facing
		
		for direction in direction_list:
			hextant_hex_list = GetCoveredHexes(self.unit.hx, self.unit.hy, ConstrainDir(direction + rotate))
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
	def __init__(self, unit, stats):
		self.unit = unit			# unit that owns this weapon
		self.stats = stats			# dictionary of weapon stats
		
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
		
		# if weapon is a gun, set up ammo stores and ready rack
		self.ammo_stores = None
		self.rr_size = 0
		self.using_rr = False
		if self.GetStat('type') == 'Gun' and 'ammo_type_list' in self.stats:
			self.ammo_stores = {}
			self.ready_rack = {}
			
			# set maximum ready rack capacity
			if 'rr_size' in self.stats:
				self.rr_size = int(self.stats['rr_size'])
			else:
				self.rr_size = 6
			self.LoadGunAmmo()
		
		# weapon statuses
		self.covered_hexes = []			# map hexes that could be targeted by this weapon
		self.fired = False
		self.maintained_rof = False
		
		self.selected_target = None		# for player unit
		self.acquired_target = None		# acquired target status and target unit
	
	
	# check for the value of a stat, return None if stat not present
	def GetStat(self, stat_name):
		if stat_name not in self.stats:
			return None
		return self.stats[stat_name]
	
	
	# move a shell into or out of Ready Rack
	def ManageRR(self, add_num):
		
		# calculate current total general stores and RR load
		total_num = 0
		for ammo_type in AMMO_TYPES:
			if ammo_type in self.ammo_stores:
				total_num += self.ammo_stores[ammo_type]
		rr_num = 0
		for ammo_type in AMMO_TYPES:
			if ammo_type in self.ready_rack:
				rr_num += self.ready_rack[ammo_type]
		
		# no room in RR
		if rr_num + add_num > self.rr_size:
			return False
		
		# none remaining in stores
		elif self.ammo_stores[self.ammo_type] - add_num < 0:
			return False
		
		# none remaining in RR
		elif self.ready_rack[self.ammo_type] + add_num < 0:
			return False
		
		# no room in general stores
		elif total_num - add_num > int(self.stats['max_ammo']):
			return False
		
		self.ready_rack[self.ammo_type] += add_num
		self.ammo_stores[self.ammo_type] -= add_num
		
		PlaySoundFor(None, 'move_1_shell')
		
		return True
		
	
	# calculate the odds for maintain RoF with this weapon
	def GetRoFChance(self):
		
		# calculate base chance
		chance = float(self.GetStat('rof'))
		
		# guns need to be using RR for full benefit
		if self.GetStat('type') == 'Gun':
			if not self.using_rr:
				chance = round(chance * 0.50, 2)
		
		bonus = 0.0
		
		# Gun-specific bonuses
		if self.GetStat('type') == 'Gun':
			
			# guns must have at least one shell of the current type available
			if self.ammo_type is not None:
				
				if self.using_rr:
					if self.ready_rack[self.ammo_type] == 0:
						return 0.0
				else:
					if self.ammo_stores[self.ammo_type] == 0:
						return 0.0
			
			# if guns have a Loader on proper order, bonus is applied
			crewman_found = False
			
			position_list = self.GetStat('reloaded_by')
			if position_list is not None:
				for position in position_list:
					crewman = self.unit.GetPersonnelByPosition(position)
					if crewman is None: continue
					if crewman.current_cmd != 'Reload': continue
					
					bonus = 10.0
					if 'Fast Hands' in crewman.skills:
						bonus = 15.0
					break
		
		# more general bonuses based on firing crewman
		position_list = self.GetStat('fired_by')
		if position_list is not None:
			for position in position_list:
				crewman = self.unit.GetPersonnelByPosition(position)
				if crewman is None: continue
				
				if self.GetStat('type') == 'Gun':
					if 'Quick Trigger' in crewman.skills:
						bonus += 5.0
					if self.selected_target is not None:
						if 'Time on Target' in crewman.skills:
							bonus += 10.0
				
				elif self.GetStat('type') in MG_WEAPONS:
					if 'Burst Fire' in crewman.skills:
						bonus += 10.0
		
		return chance + bonus
		
	
	# display information about current available ammo to a console
	def DisplayAmmo(self, console, x, y, skip_active=False):
		
		# highlight if RR is in use
		if self.using_rr:
			libtcod.console_set_default_foreground(console, libtcod.white)
		else:
			libtcod.console_set_default_foreground(console, libtcod.grey)
		libtcod.console_print_ex(console, x+10, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'RR')
		
		y += 1
		# general stores and RR contents
		for ammo_type in AMMO_TYPES:
			if ammo_type in self.ammo_stores:
				
				# highlight if this ammo type currently active
				if self.ammo_type is not None and not skip_active:
					if self.ammo_type == ammo_type:
						libtcod.console_set_default_background(console, libtcod.darker_blue)
						libtcod.console_rect(console, x, y, 11, 1, True, libtcod.BKGND_SET)
						libtcod.console_set_default_background(console, libtcod.darkest_grey)
				
				libtcod.console_set_default_foreground(console, libtcod.white)
				libtcod.console_print(console, x, y, ammo_type)
				libtcod.console_set_default_foreground(console, libtcod.light_grey)
				libtcod.console_print_ex(console, x+7, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, str(self.ammo_stores[ammo_type]))
				
				libtcod.console_print_ex(console, x+10, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, str(self.ready_rack[ammo_type]))
				
				y += 1
		
		y += 1
		libtcod.console_print(console, x, y, 'Max')
		libtcod.console_set_default_foreground(console, libtcod.light_grey)
		libtcod.console_print_ex(console, x+7, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, self.stats['max_ammo'])
		libtcod.console_print_ex(console, x+10, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, str(self.rr_size))
	
	# add a target as the current acquired target, or add one level
	def AddAcquiredTarget(self, target):
		
		# target is not yet spotted
		if target.owning_player == 1 and not target.spotted: return
		
		# no target previously acquired
		if self.acquired_target == None:
			self.acquired_target = (target, 0)
		
		# adding one level
		elif self.acquired_target == (target, 0):
			self.acquired_target = (target, 1)
		
		# already at max
		elif self.acquired_target == (target, 1):
			return
		
		# same or new target
		else:
			self.acquired_target = (target, 0)
	
	
	# calculate the map hexes covered by this weapon
	def UpdateCoveredHexes(self):
		
		def AddAllAround():
			for r in range(1, self.max_range + 1):
				ring_list = GetHexRing(self.unit.hx, self.unit.hy, r)
				for (hx, hy) in ring_list:
					# make sure hex is on map
					if (hx, hy) in scenario.hex_dict:
						self.covered_hexes.append((hx, hy))
			
		
		self.covered_hexes = []
		
		# can always fire in own hex
		self.covered_hexes.append((self.unit.hx, self.unit.hy))
		
		# infantry can fire all around
		if self.unit.GetStat('category') == 'Infantry':
			AddAllAround()
			return
		
		# AA MGs normally can fire in any direction
		if self.GetStat('type') == 'AA MG':
			if self.GetStat('front_only') is None:
				AddAllAround()
				return
		
		# hull-mounted weapons fire in hull facing direction, also weapons mounted high on the hull
		# if no rotatable turret present
		if self.GetStat('mount') == 'Hull' or self.unit.turret_facing is None:
			hextant_hex_list = GetCoveredHexes(self.unit.hx, self.unit.hy, self.unit.facing)
			
		# turret-mounted weapons fire in turret direction
		elif self.GetStat('mount') == 'Turret':
			hextant_hex_list = GetCoveredHexes(self.unit.hx, self.unit.hy, self.unit.turret_facing)
		
		else:
			print('ERROR: Could not set covered hexes for weapon: ' + self.stats['name'])
			return
		
		for (hx, hy) in hextant_hex_list:
			if (hx, hy) not in scenario.hex_dict: continue		# hex is off map
			# out of range
			if GetHexDistance(self.unit.hx, self.unit.hy, hx, hy) > self.max_range:
				continue
			self.covered_hexes.append((hx, hy))
		
		
	# load this gun full of ammo
	def LoadGunAmmo(self):
		
		if not self.GetStat('type') == 'Gun': return
		
		# set up empty categories first, also ready rack contents
		for ammo_type in self.stats['ammo_type_list']:
			self.ammo_stores[ammo_type] = 0
			self.ready_rack[ammo_type] = 0
		
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

	
	# set/reset all scenario statuses for a new turn
	def ResetMe(self):
		self.fired = False
		self.maintained_rof = False
		self.UpdateCoveredHexes()
	
	
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
		self.disposition = 'None'		# records type of action for this activation
		self.recall = False			# unit is under orders to be recalled

	# do activation for this unit
	def DoActivation(self):
		
		# check for debug flag
		if DEBUG:
			if session.debug['No AI Actions']:
				return
		
		# no action if it's not alive
		if not self.owner.alive: return
		
		#print('AI DEBUG: ' + self.owner.unit_id + ' now acting')
		
		# check for being recalled because campaign day is over
		if campaign_day.ended and not self.recall:
			if GetPercentileRoll() <= 25.0:
				self.recall = True
		
		# if recalled, chance that unit simply disappears
		if self.recall:
			if GetPercentileRoll() <= 10.0:
				ShowMessage(self.owner.GetName() + ' withdraws from the battlefield.')
				self.owner.DestroyMe(no_vp=True)
				return
		
		roll = GetPercentileRoll()
		
		if DEBUG:
			if session.debug['AI Hates Player']:
				roll = 0.0
		
		# check for player crew vulnerability
		player_crew_vulnerable = False
		if len(scenario.player_unit.VulnerableCrew()) > 0:
			player_crew_vulnerable = True
		
		# Step 1: roll for unit action
		if self.owner.GetStat('category') == 'Infantry':
			
			if roll <= 25.0:
				if player_crew_vulnerable and roll <= 20.0:
					self.disposition = 'Harass Player'
				else:
					self.disposition = 'Attack Player'
			elif roll <= 40.0:
				self.disposition = 'Combat'
			elif roll <= 60.0:
				if self.owner.pinned:
					self.disposition = 'Combat'
				else:
					self.disposition = 'Movement'
			else:
				self.disposition = 'None'
		
		elif self.owner.GetStat('category') == 'Gun':
			
			if not self.owner.deployed:
				self.disposition = 'None'
			else:
				if roll <= 10.0:
					self.disposition = 'Attack Player'
				elif roll <= 65.0:
					self.disposition = 'Combat'
				else:
					self.disposition = 'None'
		
		# armoured train - doesn't move during a scenario
		elif self.owner.GetStat('class') == 'Armoured Train Car':
			
			if self.owner.unit_id == 'Locomotive':
				self.disposition = 'None'
			else:
				if roll <= 40.0:
					self.disposition = 'Combat'
				else:
					self.disposition = 'None'
			
		# non-combat unit
		elif self.owner.GetStat('class') == 'Truck':
			if roll <= 60.0:
				self.disposition = 'None'
			else:
				self.disposition = 'Movement'
		
		# combat vehicle
		else:
			if roll <= 15.0:
				if player_crew_vulnerable and roll <= 10.0:
					self.disposition = 'Harass Player'
				else:
					self.disposition = 'Attack Player'
			elif roll <= 40.0:
				self.disposition = 'Combat'
			elif roll <= 65.0:
				self.disposition = 'Movement'
			else:
				self.disposition = 'None'
		
		current_range = GetHexDistance(0, 0, self.owner.hx, self.owner.hy)
		
		# no combat if unit is off-map
		if current_range > 3:
			if self.disposition == 'Combat':
				self.disposition = 'None'
		
		# player squad doesn't move on its own and doesn't harass or attack the player
		if self.owner in scenario.player_unit.squad:
			if self.disposition in ['Harass Player', 'Attack Player', 'Movement']:
				self.disposition = 'Combat'
		
		# MG teams less likely to move
		if self.owner.GetStat('class') == 'MG Team':
			if self.disposition == 'Movement':
				if GetPercentileRoll() <= 80.0:
					self.disposition = 'Combat'
		
		# recalled units much more likely to move
		if self.recall:
			if self.disposition != 'Movement':
				if GetPercentileRoll() <= 80.0:
					self.disposition = 'Movement'
			
		#print('AI DEBUG: ' + self.owner.unit_id + ' set disposition to: ' + self.disposition)
		
		# Step 2: Determine action to take
		if self.disposition == 'Movement':
			
			# build a list of adjacent hexes
			hex_list = GetHexRing(self.owner.hx, self.owner.hy, 1)
			
			for (hx, hy) in reversed(hex_list):
				
				# don't move into player's hex
				if hx == 0 and hy == 0:
					hex_list.remove((hx, hy))
					continue
				
				# if destination is on map, check if 1+ enemy units present
				if (hx, hy) in scenario.hex_dict:
					for unit in scenario.hex_dict[(hx,hy)].unit_stack:
						if unit.owning_player != self.owner.owning_player:
							hex_list.remove((hx, hy))
							continue
				
				# if unit is being recalled, can only move further away
				dist = GetHexDistance(0, 0, hx, hy)
				if self.recall:
					if dist < current_range:
						hex_list.remove((hx, hy))
						continue
					
				# otherwise, if move would take them off map, large chance that this hex gets thrown out
				else:
					
					if dist == 4:
						if GetPercentileRoll() <= 75.0:
							hex_list.remove((hx, hy))
							continue
					
					# otherwise, if range would change, smaller chance that this hex gets thrown out
					elif dist != current_range:
						if GetPercentileRoll() <= 40.0:
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
			
			# turn to face destination
			if self.owner.facing is not None:
				direction = GetDirectionToAdjacent(self.owner.hx, self.owner.hy, hx, hy)
				self.owner.facing = direction
				if self.owner.turret_facing is not None:
					self.owner.turret_facing = direction
			
			# set statuses
			self.owner.moving = True
			self.owner.ClearAcquiredTargets()
			
			# do movement roll
			chance = self.owner.forward_move_chance
			roll = GetPercentileRoll()
			
			# move was not successful
			if roll > chance:
				self.owner.forward_move_chance += BASE_MOVE_BONUS
				return
			
			# move was successful but may be cancelled by a breakdown
			if self.owner.BreakdownCheck():
				return
			
			# clear any bonus and move into new hex
			self.owner.forward_move_chance = BASE_FORWARD_MOVE_CHANCE
			scenario.hex_dict[(self.owner.hx, self.owner.hy)].unit_stack.remove(self.owner)
			self.owner.hx = hx
			self.owner.hy = hy
			scenario.hex_dict[(hx, hy)].unit_stack.append(self.owner)
			for weapon in self.owner.weapon_list:
				weapon.UpdateCoveredHexes()
			
			self.owner.GenerateTerrain()
			self.owner.CheckForHD()
			self.owner.SetSmokeLevel()
			scenario.UpdateUnitCon()
			scenario.UpdateScenarioDisplay()
			
			# if new location is in ring 4, remove from game
			if GetHexDistance(0, 0, hx, hy) == 4:
				self.owner.RemoveFromPlay()
				
		
		elif self.disposition in ['Combat', 'Attack Player', 'Harass Player']:
			
			# determine target
			target_list = []
			
			if self.disposition in ['Attack Player', 'Harass Player']:
				target_list.append(scenario.player_unit)
			else:
				for unit in scenario.units:
					if unit == scenario.player_unit: continue
					if unit.owning_player == self.owner.owning_player: continue
					if GetHexDistance(0, 0, unit.hx, unit.hy) > 3: continue
					target_list.append(unit)
			
			# no possible targets
			if len(target_list) == 0:
				#print ('AI DEBUG: No possible targets for ' + self.owner.unit_id)
				return
			
			# score possible weapon-target combinations
			attack_list = []
			
			for target in target_list:
				for weapon in self.owner.weapon_list:
					
					# since we're ignoring our current hull/turret facing, make sure that target is in range
					if GetHexDistance(self.owner.hx, self.owner.hy, target.hx, target.hy) > weapon.max_range:
						continue
					
					# if Harassing player, only use MGs and small arms
					if self.disposition == 'Harass Player' and weapon.GetStat('type') == 'Gun': continue
					
					# gun weapons need to check multiple ammo type combinations
					if weapon.GetStat('type') == 'Gun':
						ammo_list = weapon.stats['ammo_type_list']
						for ammo_type in ammo_list:
							
							weapon.ammo_type = ammo_type
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
				#print ('AI DEBUG: No possible attacks for ' + self.owner.unit_id)
				return
			
			# score each possible weapon-ammo-target combination
			scored_list = []
			for (weapon, target, ammo_type) in attack_list:
				
				# skip small arms attacks on targets that have no chance of effect
				if self.disposition != 'Harass Player' and target.GetStat('category') == 'Vehicle':
					if weapon.GetStat('type') != 'Gun' and weapon.GetStat('type') not in MG_WEAPONS:
						continue
				
				# determine if a pivot or turret rotation would be required
				pivot_req = False
				turret_rotate_req = False
				mount = weapon.GetStat('mount')
				if mount is not None:
					if mount == 'Turret' and self.owner.turret_facing is not None:
						if (target.hx, target.hy) not in weapon.covered_hexes:
							turret_rotate_req = True
					else:
						if (target.hx, target.hy) not in weapon.covered_hexes:
							pivot_req = True
				
				# special: player squad cannot pivot
				if pivot_req and self.owner in scenario.player_unit.squad:
					continue
				
				# set ammo type if required
				if ammo_type != '':
					weapon.ammo_type = ammo_type
				
				# calculate odds of attack, taking into account if the attack
				# would require a pivot or turret rotation
				profile = scenario.CalcAttack(self.owner, weapon, target,
					pivot=pivot_req, turret_rotate=turret_rotate_req)
				
				# attack not possible
				if profile is None: continue
				
				score = profile['final_chance']
				
				# apply score modifiers
				
				# FUTURE: can factor armour penetration chance into score
				
				# try to avoid using HE on infantry in case MG is available too
				if target.GetStat('category') == 'Infantry' and ammo_type == 'HE':
					score -= 20.0
				
				# avoid small arms on armoured targets and MG attacks unless within AP range
				if self.disposition != 'Harass Player':
					if weapon.GetStat('type') != 'Gun' and target.GetStat('armour') is not None:
						if weapon.GetStat('type') not in MG_WEAPONS:
							score -= 40.0
						elif GetHexDistance(self.owner.hx, self.owner.hy, target.hx, target.hy) > MG_AP_RANGE:
							score -= 40.0
				
				if target.GetStat('category') == 'Vehicle':
				
					# avoid HE attacks on armoured targets
					if weapon.GetStat('type') == 'Gun' and target.GetStat('armour') is not None:
						if ammo_type == 'HE':
							score -= 20.0
					
					# avoid AP attacks on unarmoured vehicles
					if weapon.GetStat('type') == 'Gun' and target.GetStat('armour') is None:
						if ammo_type == 'AP':
							score -= 20.0
				
				# not sure if this is required, but seems to work
				score = round(score, 2)
				
				# add to list
				scored_list.append((score, weapon, target, ammo_type))
			
			# no possible attacks
			if len(scored_list) == 0:
				#print('AI DEBUG: ' + self.owner.unit_id + ': no possible scored attacks on targets')
				return
			
			# sort list by score
			scored_list.sort(key=lambda x:x[0], reverse=True)
			
			# DEBUG: list scored attacks
			#print ('AI DEBUG: ' + str(len(scored_list)) + ' possible attacks for ' + self.owner.unit_id + ':')
			#n = 1
			#for (score, weapon, target, ammo_type) in scored_list:
			#	text = '#' + str(n) + ' (' + str(score) + '): ' + weapon.stats['name']
			#	if ammo_type != '':
			#		text += '(' + ammo_type + ')'
			#	text += ' against ' + target.unit_id + ' in ' + str(target.hx) + ',' + str(target.hy)
			#	print (text)
			#	n += 1
			
			# select best attack
			(score, weapon, target, ammo_type) = scored_list[0]
			
			# no good attacks
			if score <= 3.0:
				#print('AI DEBUG: ' + self.owner.unit_id + ': no good scored attacks on target list')
				return
			
			# proceed with best attack
			
			# set ammo type if any
			if ammo_type != '': weapon.current_ammo = ammo_type
			
			# pivot or rotate turret if required
			mount = weapon.GetStat('mount')
			if mount is not None and (target.hx, target.hy) not in weapon.covered_hexes:
				
				direction = GetDirectionToward(self.owner.hx, self.owner.hy, target.hx, target.hy)
				
				if mount == 'Turret' and self.owner.turret_facing is not None:
					self.owner.turret_facing = direction
					#print('AI DEBUG: AI unit rotated turret to fire')
				
				elif mount == 'Hull' and self.owner.facing is not None:
					self.owner.facing = direction
					if self.owner.turret_facing is not None:
						self.owner.turret_facing = direction
					self.owner.ClearAcquiredTargets(no_enemy=True)
					#print('AI DEBUG: AI unit pivoted hull to fire')
				
				scenario.UpdateUnitCon()
				scenario.UpdateScenarioDisplay()
				for weapon in self.owner.weapon_list:
					weapon.UpdateCoveredHexes()
			
			#text = 'AI DEBUG: ' + self.owner.unit_id + ' attacking with ' + weapon.stats['name']
			#if ammo_type != '':
			#	text += '(' + ammo_type + ')'
			#text += ' against ' + target.unit_id + ' in ' + str(target.hx) + ',' + str(target.hy)
			#print(text)
			
			# move target to top of hex stack
			target.MoveToTopOfStack()
			scenario.UpdateUnitCon()
			scenario.UpdateScenarioDisplay()
			libtcod.console_flush()
			
			result = self.owner.Attack(weapon, target)



# Unit Class: represents a single vehicle or gun, or a squad or small team of infantry
class Unit:
	def __init__(self, unit_id):
		
		self.unit_id = unit_id			# unique ID for unit type
		self.nick_name = ''			# nickname for model, eg. Sherman
		self.unit_name = ''			# name of tank, etc.
		self.alive = True			# unit is alive
		self.immobilized = False		# vehicle or gun unit is immobilized
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
		
		if 'nick_name' in self.stats:
			self.nick_name = self.stats['nick_name']
		
		if 'crew_positions' in self.stats:
			for position_dict in self.stats['crew_positions']:
				self.positions_list.append(Position(self, position_dict))
		
		# roll for HVSS if any
		if 'HVSS' in self.stats:
			chance = float(self.stats['HVSS'])
			if GetPercentileRoll() <= chance:
				self.stats['HVSS'] = True
			else:
				del self.stats['HVSS']
		
		# set up weapons
		self.weapon_list = []			# list of unit weapons
		if 'weapon_list' in self.stats:
			weapon_list = self.stats['weapon_list']
			for weapon_dict in weapon_list:
				self.weapon_list.append(Weapon(self, weapon_dict))
			
			# clear this stat since we don't need it any more
			self.stats['weapon_list'] = None
		
		# set up initial scenario statuses
		self.ResetMe()
	
	
	# set/reset all scenario statuses for this unit
	def ResetMe(self):
		
		self.hx = 0				# location in scenario hex map
		self.hy = 0
		self.terrain = None			# surrounding terrain
		self.terrain_seed = 0			# seed for terrain depiction greebles
		self.dest_hex = None			# destination hex for move
		self.animation_cells = []		# list of x,y unit console locations for animation
		
		self.spotted = False			# unit has been spotted by opposing side
		self.smoke = [0,0,0,0,0,0]		# unit smoke level in 6 directions
		
		self.hull_down = []			# list of directions unit in which Hull Down
		self.moving = False
		self.bogged = False			# unit is bogged down, cannot move or pivot
		self.fired = False
		self.hit_by_fp = False			# was hit by an effective fp attack
		
		self.facing = None
		self.previous_facing = None
		self.turret_facing = None
		self.previous_turret_facing = None
		
		self.pinned = False
		self.deployed = False
		self.fatigue = 0			# fatigue points
		
		self.forward_move_chance = 0.0		# set by CalculateMoveChances()
		self.reverse_move_chance = 0.0
		self.bog_chance = 0.0			# "
		
		self.forward_move_bonus = 0.0
		self.reverse_move_bonus = 0.0
		
		self.fp_to_resolve = 0			# fp from attacks to be resolved
		self.ap_hits_to_resolve = []		# list of unresolved AP hits
	
	
	# reset this unit for new turn
	def ResetForNewTurn(self, skip_smoke=False):
		
		# check for smoke dispersal
		if not skip_smoke:
		
			for i in range(6):
				if self.smoke[i] > 0:
					roll = GetPercentileRoll()
					
					if self.moving:
						roll -= 5.0
					
					if campaign_day.weather['Precipitation'] == 'Rain':
						roll -= 5.0
					elif campaign_day.weather['Precipitation'] == 'Heavy Rain':
						roll -= 15.0
					
					if roll <= 5.0:
						self.smoke[i] -= 1
						
						# show message if player
						if self == scenario.player_unit:
							if self.smoke[i] > 0:
								ShowMessage('Some of the smoke nearby disperses somewhat.')
							else:
								ShowMessage('Some of the smoke nearby has dispersed.')
		
		self.moving = False
		self.previous_facing = self.facing
		self.previous_turret_facing = self.turret_facing
		
		self.fired = False
		for weapon in self.weapon_list:
			weapon.ResetMe()
		
		# select first player weapon if none selected so far
		if self == scenario.player_unit:
			if scenario.selected_weapon is None:
				scenario.selected_weapon = self.weapon_list[0]
		
		# update crew positions
		for position in self.positions_list:
			# update visible hexes
			position.UpdateVisibleHexes()
			if position.crewman is None: continue
			# check for crew status recovery
			position.crewman.DoRecoveryCheck()

	
	# check for the value of a stat, return None if stat not present
	def GetStat(self, stat_name):
		if stat_name not in self.stats:
			return None
		return self.stats[stat_name]
	
	
	# clear all ammo loads for all guns in this unit
	def ClearGunAmmo(self):
		for weapon in self.weapon_list:
			if weapon.GetStat('type') != 'Gun': continue
			for ammo_type in AMMO_TYPES:
				if ammo_type in weapon.ammo_stores:
					weapon.ammo_stores[ammo_type] = 0
	
	
	# do a bog check
	def DoBogCheck(self, forward, pivot=False, reposition=False):
		
		# some unit types don't bog
		if self.GetStat('category') not in ['Vehicle', 'Gun']:
			return
		
		chance = self.bog_chance
		
		if pivot:
			chance = chance * 0.25
		elif reposition:
			chance = chance * 0.5
		elif not forward:
			chance = chance * 1.5 
		chance = round(chance, 1)
		
		roll = GetPercentileRoll()
		
		if roll <= chance:
			self.bogged = True
	
	
	# attempt to unbog unit
	def DoUnbogCheck(self):
		if not self.bogged: return
		
		self.moving = True
		
		chance = self.bog_chance
		roll = GetPercentileRoll()
		
		if roll > chance:
			self.bogged = False
			return True
		return False
		
	
	# do a breakdown check
	def BreakdownCheck(self):
		
		# only certain classes of unit can break down
		if self.GetStat('category') not in ['Vehicle']:
			return False
		
		chance = 1.0
		
		if 'unreliable' in self.stats:
			chance = 5.0
		
		roll = GetPercentileRoll()
		if roll <= chance:
			return True
		return False
	
	
	# set a random smoke level for this unit, upon spawn or after move
	def SetSmokeLevel(self):
		
		# roll once for each direction
		for i in range(6):
		
			roll = GetPercentileRoll()
			
			# account for effects of rain
			if campaign_day.weather['Precipitation'] == 'Rain':
				roll -= 3.0
			elif campaign_day.weather['Precipitation'] == 'Heavy Rain':
				roll -= 5.0
			
			if roll <= 93.0:
				self.smoke[i] = 0
			elif roll <= 98.0:
				self.smoke[i] = 1
			else:
				self.smoke[i] = 2

	
	# returns list of crew in this unit that are vulnerable to small-arms fire
	def VulnerableCrew(self):
		
		crew_list = []
		
		for position in self.positions_list:
			if position.crewman is None: continue
			if not position.crewman.ce: continue
			if position.crewman.status in ['Dead', 'Unconscious']: continue
			crew_list.append(position.crewman)

		return crew_list
		
	
	# return a to-hit modifier given current terrain
	def GetTEM(self):
		
		if self.terrain not in SCENARIO_TERRAIN_EFFECTS: return 0.0
		terrain_dict = SCENARIO_TERRAIN_EFFECTS[self.terrain]
		if 'TEM' not in terrain_dict: return 0.0
		tem_dict = terrain_dict['TEM']
		
		if 'All' in tem_dict: return tem_dict['All']
		
		if self.GetStat('category') == 'Infantry':
			if 'Infantry' in tem_dict:
				return tem_dict['Infantry']
		
		if self.GetStat('category') == 'Gun':
			if self.deployed:
				if 'Deployed Gun' in tem_dict:
					return tem_dict['Deployed Gun']
		
		return 0.0
	
	
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
	# if no_enemy, enemy units retain AC on this unit
	def ClearAcquiredTargets(self, no_enemy=False):
		
		for weapon in self.weapon_list:
			weapon.acquired_target = None
		
		if no_enemy: return
		
		for unit in scenario.units:
			if unit.owning_player == self.owning_player: continue
			for weapon in unit.weapon_list:
				if weapon.acquired_target is None: continue
				(ac_target, level) = weapon.acquired_target
				if ac_target == self:
					weapon.acquired_target = None
		
	
	# calculate chances of a successful forward/reverse move action for this unit
	# also calculate bog chances
	def CalculateMoveChances(self):
		
		# set values to base values
		self.forward_move_chance = BASE_FORWARD_MOVE_CHANCE
		self.reverse_move_chance = BASE_REVERSE_MOVE_CHANCE
		self.bog_chance = 1.0
		
		# apply modifier from unit movement type
		movement_class = self.GetStat('movement_class')
		if movement_class == 'Slow Tank':
			self.forward_move_chance -= 15.0
			self.bog_chance += 2.0
		elif movement_class == 'Fast Tank':
			self.forward_move_chance += 10.0
		elif movement_class == 'Wheeled':
			# FUTURE: additional modifier here if using road movement
			self.forward_move_chance += 5.0
			self.bog_chance += 4.0
		
		if self.GetStat('powerful_engine') is not None:
			self.forward_move_chance += 5.0
			self.bog_chance -= 0.5
		if self.GetStat('HVSS') is not None:
			self.forward_move_chance += 10.0
			self.reverse_move_chance += 10.0
			self.bog_chance -= 1.5
		
		# apply modifier from current terrain type
		if self.terrain is not None:
			if 'Movement Mod' in SCENARIO_TERRAIN_EFFECTS[self.terrain]:
				mod = SCENARIO_TERRAIN_EFFECTS[self.terrain]['Movement Mod']
				self.forward_move_chance += mod
				self.reverse_move_chance += mod
			if 'Bog Mod' in SCENARIO_TERRAIN_EFFECTS[self.terrain]:
				mod = SCENARIO_TERRAIN_EFFECTS[self.terrain]['Bog Mod']
				self.bog_chance += mod
		
		# apply modifiers for ground conditions
		if campaign_day.weather['Ground'] != 'Dry':
			mod = 0.0
			bog_mod = 0.0
			if campaign_day.weather['Ground'] == 'Deep Snow':
				if movement_class == 'Wheeled':
					mod = -65.0
					bog_mod = 4.0
				else:
					mod = -50.0
					bog_mod = 2.0
			elif campaign_day.weather['Ground'] in ['Muddy', 'Snow']:
				if movement_class == 'Wheeled':
					mod = -45.0
					bog_mod = 2.0
				else:
					mod = -30.0
					bog_mod = 1.0
			self.forward_move_chance += mod
			self.reverse_move_chance += mod
			self.bog_chance += bog_mod
		
		# add bonuses from previous moves
		self.forward_move_chance += self.forward_move_bonus
		self.reverse_move_chance += self.reverse_move_bonus
		
		# add bonuses from commander direction
		for position in ['Commander', 'Commander/Gunner']:
			crewman = self.GetPersonnelByPosition(position)
			if crewman is not None:
				if crewman.current_cmd == 'Direct Movement':
					self.forward_move_chance += 15.0
					self.reverse_move_chance += 10.0
				break
		
		# limit chances
		self.forward_move_chance = RestrictChance(self.forward_move_chance)
		self.reverse_move_chance = RestrictChance(self.reverse_move_chance)
		
		if self.bog_chance < 0.5:
			self.bog_chance = 0.5
		elif self.bog_chance > 90.0:
			self.bog_chance = 90.0
	
	
	# upon spawning into a scenario map hex, or after moving or repositioning, roll to
	# see if this unit gains HD status
	# if driver_attempt is True, then the driver is actively trying to get HD
	def CheckForHD(self, driver_attempt=False):
		
		# unit not eligible for HD
		if self.GetStat('category') in ['Infantry', 'Gun']: return False
		
		# clear any previous HD status
		self.hull_down = []
		
		# calculate base chance of HD
		if self.terrain not in SCENARIO_TERRAIN_EFFECTS: return False
		chance = SCENARIO_TERRAIN_EFFECTS[self.terrain]['HD Chance']
		
		# apply size modifier
		size_class = self.GetStat('size_class')
		if size_class is not None:
			chance += HD_SIZE_MOD[size_class]
		
		# bonus for driver action and commander direction if any
		if driver_attempt:
			crewman = self.GetPersonnelByPosition('Driver')
			if crewman is not None:
				chance += crewman.GetActionMod('Attempt HD')
			
			for position in ['Commander', 'Commander/Gunner']:
				crewman = self.GetPersonnelByPosition(position)
				if crewman is None: continue
				if crewman.current_cmd == 'Direct Movement':
					chance += crewman.GetActionMod('Direct Movement')
					
					# check for skill modifier
					if 'Lay of the Land' in crewman.skills:
						chance += 15.0
					
				break
		
		# regular move action
		else:
			crewman = self.GetPersonnelByPosition('Driver')
			if crewman is not None:
				if 'Eye for Cover' in crewman.skills:
					chance += 5.0
		
		chance = RestrictChance(chance)
		
		roll = GetPercentileRoll()
		
		# check for debug flag
		if self == scenario.player_unit and DEBUG:
			if session.debug['Player Always HD']:
				roll = 1.0
		
		if roll > chance: return False
		
		if driver_attempt:
			direction = self.facing
		else:
			direction = choice(range(6))
		self.hull_down = [direction]
		self.hull_down.append(ConstrainDir(direction + 1))
		self.hull_down.append(ConstrainDir(direction - 1))
		return True
	
	
	# build lists of possible commands for each personnel in this unit
	def BuildCmdLists(self):
		for position in self.positions_list:
			if position.crewman is None: continue
			position.crewman.BuildCommandList()
			
			# cancel current command if no longer possible
			if position.crewman.current_cmd not in position.crewman.cmd_list:
				position.crewman.current_cmd = position.crewman.cmd_list[0]
	
	
	# do a round of spotting from this unit
	# for now, only the player unit does these
	def DoSpotChecks(self):
				
		# unit out of play range
		if GetHexDistance(0, 0, self.hx, self.hy) > 3:
			return
		
		# create a local list of crew positions in a random order
		position_list = sample(self.positions_list, len(self.positions_list))
		
		for position in position_list:
			
			# no crewman in position
			if position.crewman is None:
				continue
			
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
				
				# precipitation
				if campaign_day.weather['Precipitation'] in ['Rain', 'Snow']:
					chance -= 5.0 * float(distance)
				elif campaign_day.weather['Precipitation'] in ['Heavy Rain', 'Blizzard']:
					chance -= 10.0 * float(distance)
				
				# smoke concealment
				direction = GetDirectionToward(self.hx, self.hy, unit.hx, unit.hy)
				if self.smoke[direction] > 0:
					if self.smoke[direction] == 1:
						chance = chance * 0.75
					else:
						chance = chance * 0.5
				
				direction = GetDirectionToward(unit.hx, unit.hy, self.hx, self.hy)
				if unit.smoke[direction] > 0:
					if unit.smoke[direction] == 1:
						chance = chance * 0.75
					else:
						chance = chance * 0.5
				
				# target moving
				if unit.moving:
					chance = chance * 1.5
				
				# target fired
				if unit.fired:
					chance = chance * 2.0
				
				# infantry are not as good at spotting from their lower position
				if self.GetStat('category') == 'Infantry':
					chance = chance * 0.5
				
				# target terrain
				chance += unit.GetTEM()
				
				# spotting crew modifier
				chance += position.crewman.GetActionMod('Spotting')
				
				# spotting crew skill
				if 'Eagle Eyed' in position.crewman.skills and position.crewman.ce:
					chance += 10.0
				
				# target is HD to spotter
				if len(unit.hull_down) > 0:
					if GetDirectionToward(unit.hx, unit.hy, self.hx, self.hy) in unit.hull_down:
						chance = chance * 0.5
				
				chance = RestrictChance(chance)
				
				# special: target has been hit by effective fp
				if unit.hit_by_fp:
					chance = 100.0
				
				roll = GetPercentileRoll()
				
				if roll <= chance:
					
					unit.SpotMe()
					scenario.UpdateUnitCon()
					scenario.UpdateScenarioDisplay()
					
					# display message
					if self.owning_player == 0:
						text = unit.GetName() + ' spotted!'
						portrait = unit.GetStat('portrait')
						ShowMessage(text, portrait=portrait)
						
					elif unit == scenario.player_unit:
						ShowMessage('You have been spotted!')
	
	
	# reveal this unit after being spotted
	def SpotMe(self):
		self.spotted = True
	
	
	# generate new personnel sufficent to fill all personnel positions
	def GenerateNewPersonnel(self):
		self.personnel_list = []
		for position in self.positions_list:
			self.personnel_list.append(Personnel(self, self.nation, position))
			position.crewman = self.personnel_list[-1]
	
	
	# spawn this unit into the given scenario map hex
	def SpawnAt(self, hx, hy):
		self.hx = hx
		self.hy = hy
		
		scenario.units.append(self)
		for map_hex in scenario.map_hexes:
			if map_hex.hx == hx and map_hex.hy == hy:
				map_hex.unit_stack.append(self)
				break
		
		# generate terrain for this unit
		self.GenerateTerrain()
		# check for HD status
		self.CheckForHD()
		# set random smoke level
		self.SetSmokeLevel()
	
	
	# randomly determine what kind of terrain this unit is in
	def GenerateTerrain(self):
		
		self.terrain = None
		self.terrain_seed = 0
		
		if scenario is None: return
		
		self.terrain_seed = libtcod.random_get_int(0, 1, 128)
		odds_dict = SCENARIO_TERRAIN_ODDS[scenario.cd_map_hex.terrain_type]
		roll = GetPercentileRoll()
		for terrain, odds in odds_dict.items():
			if roll <= odds:
				self.terrain = terrain
				return
			roll -= odds
		
		# if we get here, something has gone wrong, so hopefully the first terrain type is always ok
		for terrain, odds in odds_dict.items():
			self.terrain = terrain
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
	
	
	# return the display character to use on the map viewport
	def GetDisplayChar(self):
		# player unit
		if scenario.player_unit == self: return '@'
		
		# unknown enemy unit
		if self.owning_player == 1 and not self.spotted: return '?'
		
		unit_category = self.GetStat('category')
		
		# infantry
		if unit_category == 'Infantry': return 176
		
		if unit_category == 'Train Car': return 7
		
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
		if len(self.animation_cells) > 0:
			(x,y) = self.animation_cells[0]
		else:
			(x,y) = scenario.PlotHex(self.hx, self.hy)
		
		# draw terrain greebles
		if self.terrain is not None and not (self.owning_player == 1 and not self.spotted):
			generator = libtcod.random_new_from_seed(self.terrain_seed)
			
			# FUTURE: Snow and Deep Snow need their own colours for greebles
			
			if self.terrain == 'Open Ground':
				for (xmod, ymod) in GREEBLE_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 9) <= 2: continue
					c_mod = libtcod.random_get_int(generator, 0, 20)
					col = libtcod.Color(30+c_mod, 90+c_mod, 20+c_mod)
					libtcod.console_put_char_ex(unit_con, x+xmod, y+ymod, 46, col, libtcod.black)
				
			elif self.terrain == 'Broken Ground':
				for (xmod, ymod) in GREEBLE_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 9) <= 2: continue
					c_mod = libtcod.random_get_int(generator, 10, 40)
					col = libtcod.Color(70+c_mod, 60+c_mod, 40+c_mod)
					if libtcod.random_get_int(generator, 1, 10) <= 4:
						char = 247
					else:
						char = 240
					libtcod.console_put_char_ex(unit_con, x+xmod, y+ymod, char, col, libtcod.black)

			elif self.terrain == 'Brush':
				for (xmod, ymod) in GREEBLE_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 9) <= 3: continue
					col = libtcod.Color(0,libtcod.random_get_int(generator, 80, 120),0)
					if libtcod.random_get_int(generator, 1, 10) <= 6:
						char = 15
					else:
						char = 37
					libtcod.console_put_char_ex(unit_con, x+xmod, y+ymod, char, col, libtcod.black)
				
			elif self.terrain == 'Woods':
				for (xmod, ymod) in GREEBLE_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 9) == 1: continue
					col = libtcod.Color(0,libtcod.random_get_int(generator, 100, 170),0)
					libtcod.console_put_char_ex(unit_con, x+xmod, y+ymod, 6, col, libtcod.black)
					
			elif self.terrain == 'Wooden Buildings':
				for (xmod, ymod) in GREEBLE_LOCATIONS:
					c_mod = libtcod.random_get_int(generator, 10, 40)
					col = libtcod.Color(70+c_mod, 60+c_mod, 40+c_mod)
					libtcod.console_put_char_ex(unit_con, x+xmod, y+ymod, 249, col, libtcod.black)
			
			elif self.terrain == 'Hills':
				for (xmod, ymod) in GREEBLE_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 9) <= 3: continue
					c_mod = libtcod.random_get_int(generator, 10, 40)
					col = libtcod.Color(20+c_mod, 110+c_mod, 20+c_mod)
					libtcod.console_put_char_ex(unit_con, x+xmod, y+ymod, 220, col, libtcod.black)
				
			elif self.terrain == 'Fields':
				for (xmod, ymod) in GREEBLE_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 9) == 1: continue
					c = libtcod.random_get_int(generator, 120, 190)
					col = libtcod.Color(c, c, 0)
					libtcod.console_put_char_ex(unit_con, x+xmod, y+ymod,
						176, col, libtcod.black)
			
			elif self.terrain == 'Marsh':
				for (xmod, ymod) in GREEBLE_LOCATIONS:
					if libtcod.random_get_int(generator, 1, 9) == 1: continue
					libtcod.console_put_char_ex(unit_con, x+xmod, y+ymod, 176,
						libtcod.Color(45,0,180), libtcod.black)
		
		# determine foreground color to use
		if self.owning_player == 1:
			col = ENEMY_UNIT_COL
		else:	
			if self == scenario.player_unit:
				col = libtcod.white
			else:
				col = ALLIED_UNIT_COL
		
		# armoured trains have more display characters
		if self.GetStat('class') == 'Armoured Train Car' and not (self.owning_player == 1 and not self.spotted):
			for x1 in range(x-4, x+5):
				libtcod.console_put_char_ex(unit_con, x1, y, 35, libtcod.dark_grey, libtcod.black)
			for x1 in range(x-1, x+2):
				libtcod.console_put_char_ex(unit_con, x1, y, 219, libtcod.grey, libtcod.black)
			
		# draw main display character
		libtcod.console_put_char_ex(unit_con, x, y, self.GetDisplayChar(), col, libtcod.black)
		
		# determine if we need to display a turret / gun depiction
		draw_turret = True
		
		if self.GetStat('category') == 'Infantry': draw_turret = False
		if self.owning_player == 1 and not self.spotted: draw_turret = False
		if self.GetStat('category') == 'Gun' and not self.deployed: draw_turret = False
		if len(self.weapon_list) == 0: draw_turret = False
		
		if draw_turret:
			# use turret facing if present, otherwise hull facing
			if self.turret_facing is not None:
				facing = self.turret_facing
			else:
				facing = self.facing
			
			# determine location to draw turret/gun character
			x_mod, y_mod = PLOT_DIR[facing]
			char = TURRET_CHAR[facing]
			libtcod.console_put_char_ex(unit_con, x+x_mod, y+y_mod, char, col, libtcod.black)
		
		# draw smoke levels if any
		for i in range(6):
			if self.smoke[i] == 0: continue
			if self.smoke[i] == 1:
				col = libtcod.light_grey
			else:
				col = libtcod.dark_grey
			for (x_mod, y_mod) in HEX_EDGE_CELLS[i]:
				libtcod.console_put_char_ex(unit_con, x+x_mod, y+y_mod, 247, col, libtcod.black)
	
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
		
		# display nickname if any overtop portrait
		libtcod.console_set_default_foreground(console, libtcod.white)
		if self.nick_name != '':
			libtcod.console_print(console, x, y+2, "'" + self.nick_name + "'")
		
		# display name if any overtop portrait
		if self.unit_name != '':
			libtcod.console_print_ex(console, x+24, y+2, libtcod.BKGND_NONE, libtcod.RIGHT,
				self.unit_name)
		
		# weapons - list turret and unmounted weapons on line 1, all others on line 2
		libtcod.console_set_default_background(console, libtcod.darkest_red)
		libtcod.console_rect(console, x, y+10, 25, 2, True, libtcod.BKGND_SET)
		
		text1 = ''
		text2 = ''
		for weapon in self.weapon_list:
			line1 = True
			if weapon.GetStat('mount') is not None:
				if weapon.GetStat('mount') != 'Turret':
					line1 = False
			
			if line1:
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
		
		# turret traverse if any
		if self.GetStat('turret'):
			if self.GetStat('turret') == 'Fast':
				libtcod.console_print(console, x+8, y+13, '(fast)')
		
		# movement class
		if self.immobilized:
			libtcod.console_set_default_foreground(console, libtcod.light_red)
			text = 'Immobilized'
		elif self.bogged:
			libtcod.console_set_default_foreground(console, libtcod.light_red)
			text = 'Bogged Down'
		else:
			libtcod.console_set_default_foreground(console, libtcod.light_green)
			text = self.GetStat('movement_class')
			if self.GetStat('powerful_engine') is not None:
				text += '+'
		libtcod.console_print_ex(console, x+24, y+12, libtcod.BKGND_NONE, libtcod.RIGHT,
			text)
		
		# HVSS, recce,  and/or off road
		libtcod.console_set_default_foreground(console, libtcod.dark_green)
		text = ''
		if self.GetStat('HVSS') is not None:
			text += 'HVSS'
		if self.GetStat('recce') is not None:
			if text != '':
				text += ' '
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
				libtcod.console_print(console, x+8, ys-1, 'HD')
				char = GetDirectionalArrow(self.hull_down[0])
				libtcod.console_put_char_ex(console, x+10, ys-1, char, libtcod.sepia, libtcod.black)
		
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
		if weapon is None or target is None: return False
		
		# make sure attack is possible
		if scenario.CheckAttack(self, weapon, target) != '': return False
		
		# if firing weapon is mounted on turret and turret has rotated, all weapons on turret lose acquired target
		if weapon.GetStat('Mount') == 'Turret' and self.turret_facing is not None:
			if self.turret_facing != self.previous_turret_facing:
				for weapon2 in self.weapon_list:
					if weapon2.GetStat('Mount') == 'Turret':
						if weapon2.GetStat('firing_group') == weapon.GetStat('firing_group'):
							weapon2.acquired_target = None
		
		# display message if player is the target
		if target == scenario.player_unit:
			text = self.GetName() + ' fires at you with ' + weapon.stats['name']
			ShowMessage(text)
		
		# attack loop, possible to maintain RoF and do multiple attacks within this loop
		attack_finished = False
		while not attack_finished:
			
			# calculate attack profile
			profile = scenario.CalcAttack(self, weapon, target)
			
			# attack not possible for some reason
			if profile is None:
				attack_finished = True
				continue
			
			# display attack profile on screen if is player involved
			if self == scenario.player_unit or target == scenario.player_unit:
				scenario.DisplayAttack(profile)
				# activate the attack console and display to screen
				scenario.attack_con_active = True
				scenario.UpdateScenarioDisplay()
			
				# allow player to cancel attack if not the target
				if not weapon.maintained_rof:
					if WaitForContinue(allow_cancel = (target != scenario.player_unit)):
						scenario.attack_con_active = False
						return True
			
			# set weapon and unit fired flags
			weapon.fired = True
			self.fired = True
			
			# expend a shell if gun weapon is firing
			if weapon.GetStat('type') == 'Gun' and weapon.ammo_type is not None:
				
				if weapon.using_rr:
					if weapon.ready_rack[weapon.ammo_type] > 0:
						weapon.ready_rack[weapon.ammo_type] -= 1
					else:
						# if no more RR ammo, default to general stores
						weapon.ammo_stores[weapon.ammo_type] -= 1
						weapon.using_rr = False
				else:
					weapon.ammo_stores[weapon.ammo_type] -= 1
				scenario.UpdateContextCon()
			
			
			##### Attack Animation and Sound Effects #####
			
			# skip if in fast mode
			if not (DEBUG and session.debug['Fast Mode']):
			
				if weapon.GetStat('type') == 'Gun':
					
					PlaySoundFor(weapon, 'fire')
					
					# start gun fire animation
					scenario.animation['gun_fire_active'] = True
					(x1, y1) = scenario.PlotHex(self.hx, self.hy)
					(x2, y2) = scenario.PlotHex(target.hx, target.hy)
					scenario.animation['gun_fire_line'] = GetLine(x1,y1,x2,y2)
					
					# continue when finished
					while scenario.animation['gun_fire_active']:
						if libtcod.console_is_window_closed(): sys.exit()
						libtcod.console_flush()
						CheckForAnimationUpdate()
					
					# add explosion effect if HE ammo
					if weapon.ammo_type == 'HE':
						
						PlaySoundFor(weapon, 'he_explosion')
						
						scenario.animation['bomb_effect'] = (x2, y2)
						scenario.animation['bomb_effect_lifetime'] = 7
						
						# let animation run
						while scenario.animation['bomb_effect'] is not None:
							if libtcod.console_is_window_closed(): sys.exit()
							libtcod.console_flush()
							CheckForAnimationUpdate()
				
				elif weapon.GetStat('type') == 'Small Arms' or weapon.GetStat('type') in MG_WEAPONS:
					
					PlaySoundFor(weapon, 'fire')
					# start small arms / MG animation
					
					scenario.animation['small_arms_fire_action'] = True
					(x1, y1) = scenario.PlotHex(self.hx, self.hy)
					(x2, y2) = scenario.PlotHex(target.hx, target.hy)
					scenario.animation['small_arms_fire_line'] = GetLine(x1,y1,x2,y2)
					scenario.animation['small_arms_lifetime'] = 12
					
					while scenario.animation['small_arms_fire_action']:
						if libtcod.console_is_window_closed(): sys.exit()
						libtcod.console_flush()
						CheckForAnimationUpdate()
			
			# do the roll, display results to the screen, and modify the attack profile
			profile = scenario.DoAttackRoll(profile)
			
			# add one level of acquired target if firing gun or MG
			if weapon.GetStat('type') == 'Gun' or weapon.GetStat('type') in MG_WEAPONS:
				weapon.AddAcquiredTarget(target)
			
			# wait for the player if they are involved
			# if RoF is maintained, may choose to attack again
			attack_finished = True
			if self == scenario.player_unit or target == scenario.player_unit:
				scenario.UpdateScenarioDisplay()
				
				end_pause = False
				while not end_pause:
					if libtcod.console_is_window_closed(): sys.exit()
					CheckForAnimationUpdate()
					libtcod.console_flush()
					if not GetInputEvent(): continue
					
					key_char = DeKey(chr(key.c).lower())
					
					if key.vk == libtcod.KEY_TAB:
						end_pause = True
					
					if self == scenario.player_unit:
						if key_char == 'f' and weapon.maintained_rof:
							attack_finished = False
							end_pause = True
			
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
					
					# also applies fp
					target.fp_to_resolve += profile['effective_fp']
			
			# point fire attack hit
			elif profile['result'] in ['CRITICAL HIT', 'HIT']:
				
				# record if player hit
				if self == scenario.player_unit:
					campaign_day.AddRecord('Gun Hits', 1)
				
				# infantry, gun, or unarmoured target
				if target.GetStat('category') in ['Infantry', 'Gun']:
					
					# if HE hit, apply effective FP
					if profile['ammo_type'] == 'HE':
						
						effective_fp = profile['weapon'].GetEffectiveFP()
						
						# apply critical hit multiplier
						if profile['result'] == 'CRITICAL HIT':
							effective_fp = effective_fp * 2
						
						# apply ground conditions modifier
						if campaign_day.weather['Ground'] == 'Deep Snow':
							effective_fp = int(float(effective_fp) * 0.25)
						elif campaign_day.weather['Ground'] in ['Muddy', 'Snow']:
							effective_fp = int(float(effective_fp) * 0.5)
						
						target.fp_to_resolve += effective_fp
						
						if not target.spotted:
							target.hit_by_fp = True
					
					# AP hits are very ineffective against infantry/guns, and
					# have no spotting effect
					elif profile['ammo_type'] == 'AP':
						target.fp_to_resolve += 1
				
				# unarmoured vehicle target, slightly different procedure
				elif target.GetStat('armour') is None:
					if profile['ammo_type'] == 'HE':
						effective_fp = profile['weapon'].GetEffectiveFP()
					else:
						effective_fp = 1
					if profile['result'] == 'CRITICAL HIT':
						effective_fp = effective_fp * 2
					target.fp_to_resolve += effective_fp
					if not target.spotted:
						target.hit_by_fp = True
				
				# armoured target
				elif target.GetStat('armour') is not None:
					target.ap_hits_to_resolve.append(profile)
			
			# update context console in case we maintained RoF
			scenario.UpdateContextCon()
			scenario.UpdateScenarioDisplay()
			
		
		# turn off attack console display if any
		scenario.attack_con_active = False
		scenario.UpdateScenarioDisplay()
		
		# reset weapon RoF
		weapon.maintained_rof = False
		
		# attack is finished
		return True
	
	
	# resolve all unresolved AP hits on this unit
	def ResolveAPHits(self):
		
		# no hits to resolve! doing fine!
		if len(self.ap_hits_to_resolve) == 0: return
		
		#print('Resolving AP hits on ' + self.unit_id)
		
		# no effect if infantry or gun
		if self.GetStat('category') in ['Infantry', 'Gun']:
			self.ap_hits_to_resolve = []
			return
		
		# move to top of hex stack
		self.MoveToTopOfStack()
		scenario.UpdateUnitCon()
		
		# handle AP hits
		for profile in self.ap_hits_to_resolve:
			
			profile = scenario.CalcAP(profile)
			
			# display and wait if player is involved
			if profile['attacker'] == scenario.player_unit or self == scenario.player_unit:
				scenario.DisplayAttack(profile)
				scenario.attack_con_active = True
				scenario.UpdateScenarioDisplay()
				
				# only wait if outcome is not automatic
				if profile['final_chance'] not in [0.0, 100.0]:
					WaitForContinue()
			
			# do the attack roll; modifies the attack profile
			profile = scenario.DoAttackRoll(profile)
			
			if profile['result'] == 'NO PENETRATION':
				PlaySoundFor(self, 'armour_save')
			
			# wait if player is involved
			if profile['attacker'] == scenario.player_unit or self == scenario.player_unit:
				scenario.UpdateScenarioDisplay()
				WaitForContinue()
			
			# turn off attack console display if any
			scenario.attack_con_active = False
			scenario.UpdateScenarioDisplay()
			
			# shock test
			roll = GetPercentileRoll()
			if roll > profile['final_chance']:
				for weapon in self.weapon_list:
					weapon.acquired_target = None
				
				if self == scenario.player_unit:
					ShowMessage('The impact has knocked your weapons off target. All acquired targets lost.')
			
			# apply result
			if profile['result'] == 'NO PENETRATION':
				
				# check for stun test
				difference = profile['final_chance'] - profile['roll']
				
				if 0.0 < difference <= AP_STUN_MARGIN:
					
					# player was target
					if self == scenario.player_unit:
						
						for position in self.positions_list:
							if position.crewman is None: continue
							position.crewman.DoStunCheck(AP_STUN_MARGIN - difference)
					
					# FUTURE: target was AI unit
					else:
						
						pass
					
			elif profile['result'] == 'PENETRATED':
				
				# if the player unit has been penetrated, multiple outcomes are possible
				if self == scenario.player_unit:
					
					# possible outcomes: minor damage, spalling, immobilized, knocked out
					
					# apply roll penalty based on how much original roll failed by
					difference = profile['roll'] - profile['final_chance']
					
					roll = GetPercentileRoll() + difference
					
					if DEBUG:
						if session.debug['Player Always Penetrated']:
							roll = 100.0
					
					# minor damage
					if roll <= 15.0:
						ShowMessage('Your tank suffers minor damage but is otherwise unharmed.')
						continue
					
					# immobilized
					elif roll <= 25.0:
						
						# already immobilized
						if scenario.player_unit.immobilized:
							ShowMessage('Your tank suffers minor damage but is otherwise unharmed.')
						else:
							ShowMessage('The hit damages the engine and drivetrain, immobilizing your tank.')
							scenario.player_unit.ImmobilizeMe()
							scenario.UpdatePlayerInfoCon()
						continue
					
					# spalling
					elif roll <= 45.0:
						text = 'The hit shatters the armour plate, sending shards of hot metal into the ' + profile['location']
						ShowMessage(text)
						for position in scenario.player_unit.positions_list:
							
							if position.crewman is None: continue
							
							# only affects turret or hull
							if position.location is not None:
								if position.location != profile['location']: continue
							
							# check for crew wound and apply modifier
							position.crewman.DoWoundCheck(roll_modifier=15.0)
							scenario.UpdateCrewInfoCon()
						
						continue
					
					# otherwise: destroyed
				
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
				ShowMessage(text)
				
				# don't resolve any further hits
				break

		# clear resolved hits
		self.ap_hits_to_resolve = []
	
	
	# resolve FP on this unit if any
	def ResolveFP(self):
		if self.fp_to_resolve == 0: return
		
		# move to top of hex stack
		self.MoveToTopOfStack()
		scenario.UpdateUnitCon()
		
		# fp has a different type of effect on vehicles and armoured trains
		if self.GetStat('category') in ['Vehicle', 'Train Car']:
			
			# FUTURE: if vehicle has any unarmoured area, possible that it will be destroyed
			if self.GetStat('armour') is None:
				for (fp, score) in VEH_FP_TK:
					if fp <= self.fp_to_resolve:
						break
				
				text = 'Resolving ' + str(self.fp_to_resolve) + ' firepower on ' + self.GetName() + '. '
				text += str(score) + '%% chance to destroy.'
				ShowMessage(text)
				
				if GetPercentileRoll() <= score:
					text = self.GetName() + ' was destroyed.'
					ShowMessage(text)
					self.DestroyMe()
				else:
					ShowMessage('No effect.')
				return
			
			# FUTURE: chance of minor damage to vehicle
			
			# check for crew wound - Player unit only
			# FUTURE: also apply to AI units?
			if self == scenario.player_unit:
				
				for position in self.positions_list:
					if position.crewman is None: continue
					position.crewman.DoWoundCheck(fp=self.fp_to_resolve)
				
			self.fp_to_resolve = 0
			return
		
		# calculate base chance of destruction
		base_chance = RESOLVE_FP_BASE_CHANCE
		for i in range(2, self.fp_to_resolve + 1):
			base_chance += RESOLVE_FP_CHANCE_STEP * (RESOLVE_FP_CHANCE_MOD ** (i-1)) 
		
		# apply any modifiers
		if self.fatigue > 0:
			base_chance += float(self.fatigue) * 15.0
		
		# restrict final chance
		base_chance = RestrictChance(base_chance)
		
		text = 'Resolving ' + str(self.fp_to_resolve) + ' firepower on ' + self.GetName() + '. '
		text += str(base_chance) + '%% chance to destroy.'
		ShowMessage(text)
		
		# roll for effect
		roll = GetPercentileRoll()
		
		if roll <= base_chance:
			text = self.GetName() + ' was destroyed.'
			ShowMessage(text)
			self.DestroyMe()
		else:
			# pin test if not already pinned
			if self.pinned:
				ShowMessage('No effect.')
			else:
				self.PinTest(self.fp_to_resolve)
				if not self.pinned:
					ShowMessage('No effect.')
		
		self.fp_to_resolve = 0
		self.fatigue += 1
	
	
	# do a morale check for this unit to recover from Broken or Pinned status
	def MoraleCheck(self, modifier):
		
		chance = MORALE_CHECK_BASE_CHANCE + modifier
		
		# FUTURE: apply terrain modifiers
		
		chance = RestrictChance(chance)
		
		roll = GetPercentileRoll()
		if roll <= chance:
			return True
		return False
	
	
	# do a pin test on this unit
	def PinTest(self, fp, no_msg=False):
		if self.pinned: return
		chance = RestrictChance(float(fp) * 5.0)
		roll = GetPercentileRoll()
		if roll <= chance:
			self.PinMe(no_msg)
	
	
	# pin this unit
	def PinMe(self, no_msg):
		self.pinned = True
		self.ClearAcquiredTargets()
		scenario.UpdateUnitCon()
		scenario.UpdateScenarioDisplay()
		if not no_msg:
			ShowMessage(self.GetName() + ' is now Pinned.')


	# immobilize this unit
	def ImmobilizeMe(self):
		if self.GetStat('category') not in ['Vehicle']: return
		self.moving = False
		self.immobilized = True
		self.bogged = False
	
	
	# destroy this unit and remove it from the game
	def DestroyMe(self, no_vp=False):
		
		# check for debug flag
		if self == scenario.player_unit and DEBUG:
			if session.debug['Player Immortality']:
				ShowMessage('Debug powers will save you from death!')
				self.ap_hits_to_resolve = []
				return
		
		if self.GetStat('category') == 'Vehicle':
			PlaySoundFor(self, 'vehicle_explosion')
		
		# set flag
		self.alive = False
		
		# remove from hex stack
		map_hex = scenario.hex_dict[(self.hx, self.hy)]
		if self in map_hex.unit_stack:
			map_hex.unit_stack.remove(self)
			
		# remove from scenario unit list
		if self in scenario.units:
			scenario.units.remove(self)
		
		# remove as selected target from all player weapons, and remove from target list
		for weapon in scenario.player_unit.weapon_list:
			if weapon.selected_target == self:
				weapon.selected_target = None
		if self in scenario.target_list:
			scenario.target_list.remove(self)
		
		# award VP to player for unit destruction
		if self.owning_player == 1:
			
			if not no_vp:
				
				# determine vp award amount and add to day records
				category = self.GetStat('category')
				
				if category == 'Infantry':
					campaign_day.AddRecord('Infantry Destroyed', 1)
					vp_amount = 1
				elif category == 'Gun':
					campaign_day.AddRecord('Guns Destroyed', 1)
					vp_amount = 2
				elif category == 'Vehicle':
					campaign_day.AddRecord('Vehicles Destroyed', 1)
					if self.GetStat('class') in ['Truck', 'Tankette']:
						vp_amount = 1
					elif self.GetStat('class') == 'Heavy Tank':
						vp_amount = 4
					else:
						vp_amount = 3
				elif category == 'Train Car':
					vp_amount = 3
				
				campaign.AwardVP(vp_amount)
		
		# friendly unit destroyed
		else:
		
			# player unit has been destroyed
			if self == scenario.player_unit:
				
				# set end-scenario flag
				scenario.finished = True
			
				# do bail-out procedure
				scenario.PlayerBailOut()
			
			# player squad member has been destroyed
			elif self in scenario.player_unit.squad:
				campaign.player_squad_num -= 1
		
		scenario.UpdateUnitCon()
		scenario.UpdateScenarioDisplay()
	
	
	# attempt to recover from pinned status at the end of an activation
	def DoRecoveryRoll(self):
		if not self.pinned: return
		if not self.MoraleCheck(0): return
		self.pinned = False
		scenario.UpdateUnitCon()
		scenario.UpdateScenarioDisplay()
		ShowMessage(self.GetName() + ' is no longer Pinned.')



# MapHex: a single hex on the scenario map
class MapHex:
	def __init__(self, hx, hy):
		self.hx = hx
		self.hy = hy
		self.unit_stack = []					# list of units present in this map hex



# Scenario: represents a single battle encounter
class Scenario:
	def __init__(self, cd_map_hex):
		
		self.init_complete = False			# flag to say that scenario has already been set up
		self.cd_map_hex = cd_map_hex			# Campaign Day map hex where this scenario is taking place
		self.ambush = False				# enemy units activate first, greater chance of spawning behind player
		self.finished = False				# Scenario has ended, returning to Campaign Day map
		
		# animation object; keeps track of active animations on the animation console
		self.animation = {
			'rain_active' : False,
			'rain_drops' : [],
			'snow_active' : False,
			'snowflakes' : [],
			'gun_fire_active' : False,
			'gun_fire_line' : [],
			'small_arms_fire_action' : False,
			'small_arms_fire_line' : [],
			'small_arms_lifetime' : 0,
			'air_attack' : None,
			'air_attack_line' : [],
			'bomb_effect' : None,
			'bomb_effect_lifetime' : 0
		}
		
		# current odds of a random event being triggered
		self.random_event_chance = BASE_RANDOM_EVENT_CHANCE
		
		# number of times enemy reinforcement random event has been triggered
		self.enemy_reinforcements = 0
		
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
		self.BuildHexmapDict()
		
		# attack console display is active
		self.attack_con_active = False
		
		self.units = []						# list of units in play
		
		# turn and phase information
		self.current_turn = 1					# current scenario turn
		self.active_player = 0					# currently active player (0 is human player)
		self.phase = PHASE_COMMAND				# current phase
		self.advance_phase = False				# flag for input loop to automatically advance to next phase/turn
		
		self.player_pivot = 0					# keeps track of player unit pivoting
		
		# player targeting
		self.target_list = []					# list of possible player targets
		self.selected_weapon = None				# player's currently selected weapon
		
		self.selected_position = 0				# index of selected position in player unit
	
	
	# roll at start of scenario to see whether player has been ambushed
	def DoAmbushRoll(self):
		roll = GetPercentileRoll()
		
		for position in ['Commander', 'Commander/Gunner']:
			crewman = self.player_unit.GetPersonnelByPosition(position)
			if crewman is None: continue
			if 'Enemy Spotted!' in crewman.skills:
				roll += 10.0
				break
		
		# FUTURE: recce status can modify this roll
		if roll <= 20.0:
			self.ambush = True
	
	
	# check for end of scenario and set flag if it has ended
	def CheckForEnd(self):
		all_enemies_dead = True
		for unit in self.units:
			if unit.owning_player == 1 and unit.alive:
				if GetHexDistance(0, 0, unit.hx, unit.hy) > 3: continue
				all_enemies_dead = False
				break
		if all_enemies_dead:
			ShowMessage('Victory! No enemy units remain in this area.')
			self.finished = True
			return
		
		# check for loss of player crew
		all_crew_dead = True
		for position in self.player_unit.positions_list:
			if position.crewman is None: continue
			if position.crewman.status != 'Dead':
				all_crew_dead = False
				break
		if all_crew_dead:
			ShowMessage('Your crew is all dead.')
			scenario.player_unit.DestroyMe()
			return
		
		# check for end of campaign day, but don't end the scenario
		campaign_day.CheckForEndOfDay()
		#if campaign_day.ended:
		#	ShowMessage('The campaign day is over.')
		#	self.finished = True
		#	return
	
	
	# check for triggering of a random event in a scenario
	def CheckForRandomEvent(self):
		
		roll = GetPercentileRoll()
		
		if roll > self.random_event_chance:
			self.random_event_chance += 1.5
			return
		
		# roll for type of event
		roll = GetPercentileRoll()
		
		# friendly air attack
		if roll <= 10.0:
			
			if 'air_support_level' not in campaign.current_week: return
			if campaign_day.weather['Cloud Cover'] == 'Overcast': return
			ShowMessage('Friendly air forces launch an attack!')
			self.DoAirAttack()
			
		# friendly arty attack
		elif roll <= 20.0:
			
			if 'arty_support_level' not in campaign.current_week: return
			ShowMessage('Friendly artillery forces fire a bombardment!')
			self.DoArtilleryAttack()
			
		# enemy reinforcement
		elif roll <= 30.0:
			
			if self.enemy_reinforcements > 0:
				if GetPercentileRoll() <= (float(self.enemy_reinforcements) * 40.0):
					return
			
			self.enemy_reinforcements += 1
			
			self.SpawnEnemyUnits(num_units=1)
			ShowMessage('Enemy reinforcements have arrived!')
		
		# random enemy unit is recalled
		elif roll <= 40.0:
			unit_list = []
			for unit in self.units:
				if not unit.alive: continue
				if unit.owning_player == 0: continue
				if unit.GetStat('category') in ['Gun', 'Train Car']: continue
				if unit.ai is None: continue		# probably not needed but safer
				if unit.ai.recall: continue
				unit_list.append(unit)
			if len(unit_list) == 0: return
			unit = choice(unit_list)
			unit.ai.recall = True
			ShowMessage(unit.GetName() + ' is being recalled from the battle.')
		
		# sniper attack on player
		elif roll <= 50.0:
			
			# check for vulnerable targets and select one if any
			crew_list = self.player_unit.VulnerableCrew()
			if len(crew_list) == 0: return
			crew_target = choice(crew_list)
			
			# do attack roll
			chance = BASE_SNIPER_TK_CHANCE
			
			# precipitation modifier
			if campaign_day.weather['Precipitation'] in ['Rain', 'Light Snow']:
				chance -= 5.0
			elif campaign_day.weather['Precipitation'] == ['Heavy Rain', 'Blizzard']:
				chance -= 15.0
			
			# target moving
			if self.player_unit.moving: chance -= 10.0
			
			# target terrain
			chance += self.player_unit.GetTEM()
			
			# odds too low
			if chance < 15.0: return
			
			# do attack roll
			roll = GetPercentileRoll()
			
			# miss
			if roll > chance:
				PlaySoundFor(None, 'ricochet')
				ShowMessage("The ricochet from a sniper's bullet rings out, narrowly missing your " + crew_target.current_position.name)
			else:
				PlaySoundFor(None, 'sniper_hit')
				ShowMessage('Your ' + crew_target.position.name + ' has been hit by a sniper.')
				crew_target.DoWoundCheck(roll_modifier = 45.0)
		
		# FUTURE: add more event types
		else:
			return
		
		# an event was triggered, so reset random event chance
		self.random_event_chance = BASE_RANDOM_EVENT_CHANCE
		
	
	# go through procedure for player crew bailing out of tank
	def PlayerBailOut(self, skip_ko=False):
		
		# (re)draw the bail-out console and display on screen
		def UpdateBailOutConsole():
			
			libtcod.console_clear(con)
			
			# window title
			libtcod.console_set_default_background(con, libtcod.light_red)
			libtcod.console_rect(con, 0, 2, WINDOW_WIDTH, 5, True, libtcod.BKGND_SET)
			libtcod.console_set_default_foreground(con, libtcod.black)
			libtcod.console_print_ex(con, WINDOW_XM, 4, libtcod.BKGND_NONE,
				libtcod.CENTER, 'BAILING OUT')
			
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_set_default_background(con, libtcod.black)
			
			
			# display player unit
			libtcod.console_set_default_foreground(con, libtcod.lighter_blue)
			libtcod.console_print(con, 33, 9, self.player_unit.unit_id)
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			libtcod.console_print(con, 33, 10, self.player_unit.GetStat('class'))
			libtcod.console_set_default_background(con, PORTRAIT_BG_COL)
			libtcod.console_rect(con, 33, 11, 25, 8, True, libtcod.BKGND_SET)
			portrait = self.player_unit.GetStat('portrait')
			if portrait is not None:
				libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, con, 33, 11)
			libtcod.console_set_default_foreground(con, libtcod.white)
			if self.player_unit.unit_name != '':
				libtcod.console_print(con, 33, 11, self.player_unit.unit_name)
			
			# roll column headers
			libtcod.console_print(con, 34, 21, 'KO Wound')
			libtcod.console_print(con, 49, 21, 'Bail Out')
			libtcod.console_print(con, 74, 21, 'Rescue')
			
			# list of crew
			x = 2
			y = 24
			
			for position in self.player_unit.positions_list:
				
				libtcod.console_set_default_foreground(con, libtcod.light_blue)
				libtcod.console_print(con, x, y, position.name)
				libtcod.console_set_default_foreground(con, libtcod.white)
				libtcod.console_print_ex(con, x+24, y, libtcod.BKGND_NONE, 
					libtcod.RIGHT, position.location)
				
				if position.crewman is None:
					libtcod.console_print(con, x, y+1, 'Empty')
				else:
					position.crewman.DisplayName(con, x, y+1, first_initial=True)
					if position.crewman.wound != '':
						libtcod.console_put_char_ex(con, x+21, y+1,
							position.crewman.wound[0], libtcod.black,
							libtcod.red)
					
					if position.crewman.ce:
						text = 'CE'
					else:
						text = 'BU'
					libtcod.console_print_ex(con, x+24, y+1, libtcod.BKGND_NONE, libtcod.RIGHT, text)
				
					# display current status
					if position.crewman.status != '':
						if position.crewman.status == 'Dead':
							libtcod.console_set_default_foreground(crew_con, libtcod.dark_grey)
						elif position.crewman.status == 'Unconscious':
							libtcod.console_set_default_foreground(crew_con, libtcod.grey)
						elif position.crewman.status == 'Stunned':
							libtcod.console_set_default_foreground(crew_con, libtcod.light_grey)
						libtcod.console_print_ex(con, x+24, y+2, libtcod.BKGND_NONE, libtcod.RIGHT, 
							position.crewman.status)
				
				y += 4
			
			# vertical dividing line
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			for y in range(23, 54):
				libtcod.console_put_char(con, 29, y, 250)
			
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_set_default_background(con, libtcod.black)
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			
		
		# draw screen for first time and pause
		UpdateBailOutConsole()
		
		Wait(120, ignore_animations=True)
		
		# do roll procedures
		
		if not skip_ko:
		
			# initial tank KO wound
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			y = 20
			for position in self.player_unit.positions_list:
				
				y += 4
				
				if position.crewman is None: continue
				if position.crewman.status == 'Dead': continue
				
				# FUTURE: modify by location on tank penetrated
				result = position.crewman.DoWoundCheck(show_messages=False)
				
				if DEBUG:
					if session.debug['Player Crew Safe in Bail Out']:
						result = None
				
				if result is None:
					text = 'OK'
				else:
					text = result
				
				lines = wrap(text, 14)
				y1 = y
				for line in lines:
					libtcod.console_print(con, 32, y1, line)
					y1 += 1
				
				libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
				libtcod.console_flush()
				Wait(100, ignore_animations=True)
			
			Wait(100, ignore_animations=True)
		
		# bail out roll
		y = 20
		for position in self.player_unit.positions_list:
			
			y += 4
			
			if position.crewman is None: continue
			
			if position.crewman.status in ['Unconscious', 'Dead']:
				text = 'N/A'
			else:
			
				modifier = 0.0
				if position.crewman.status == 'Stunned':
					modifier += 5.0
				
				if position.crewman.wound == 'Critical':
					modifier += 15.0
				elif position.crewman.wound == 'Serious':
					modifier += 10.0
				
				if not position.hatch:
					modifier += 15.0
				elif position.crewman.ce:
					modifier -= 20.0
				
				if 'Gymnast' in position.crewman.skills:
					modifier -= 10.0
				
				roll = GetPercentileRoll()
				
				if DEBUG:
					if session.debug['Player Crew Safe in Bail Out']:
						roll = 3.0
				
				# unmodified 97.0-100.0 always fail, otherwise modifier is applied
				if roll < 97.0:
					roll += modifier
				
				if roll <= 97.0:
					position.crewman.bailed_out = True
					text = 'Bailed'
				else:
					text = 'Failed'
			
			libtcod.console_print(con, 49, y, text)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			Wait(100, ignore_animations=True)
		
		# tank burn up roll
		chance = 80.0
		if self.player_unit.GetStat('wet_stowage') is not None:
			chance = 25.0
		
		# FUTURE: apply further modifiers based on killing hit
		burns = False
		
		roll = GetPercentileRoll()
		if DEBUG:
			if session.debug['Player Crew Safe in Bail Out']:
				roll = chance + 1.0
		
		if roll <= chance:
			libtcod.console_set_default_foreground(con, libtcod.light_red)
			libtcod.console_print(con, 60, 21, 'Tank Burns')
			burns = True
		else:
			libtcod.console_set_default_foreground(con, libtcod.light_grey)
			libtcod.console_print(con, 60, 21, 'No Burn-up')
		
		if burns:
			y = 20
			for position in self.player_unit.positions_list:
				y += 4
				if position.crewman is None: continue
				if position.crewman.bailed_out: continue
				
				libtcod.console_print(con, 60, y, 'Vulnerable')
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		Wait(100, ignore_animations=True)
		
		libtcod.console_set_default_foreground(con, libtcod.light_grey)
		
		# rescue rolls and final injuries
		y = 20
		for position in self.player_unit.positions_list:
			
			y += 4
			
			if position.crewman is None: continue
			
			if position.crewman.bailed_out: continue
			
			text = 'Rescued'
			
			if burns:
			
				# check for wound from burn-up before rescue
				result = position.crewman.DoWoundCheck(roll_modifier=20.0, show_messages=False)
				
				if result:
					text = result
			
			lines = wrap(text, 14)
			y1 = y
			for line in lines:
				libtcod.console_print(con, 74, y1, line)
				y1 += 1
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			Wait(100, ignore_animations=True)
		
		libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
		libtcod.console_print(con, 41, 56, 'Enter')
		libtcod.console_set_default_foreground(con, libtcod.white)
		libtcod.console_print(con, 47, 56, 'Continue')
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		
		exit_menu = False
		while not exit_menu:
			
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			keypress = GetInputEvent()
			if not keypress: continue
			
			if key.vk == libtcod.KEY_ENTER:
				exit_menu = True
				continue
		
	
	# spawn enemy units on the hex map
	# can be overidden to spawn a specific number of units
	# FUTURE: will pull more data from the campaign day and campaign objects
	def SpawnEnemyUnits(self, num_units=None):
		
		# pointer to unit type list from campaign object
		unit_type_list = campaign.stats['enemy_unit_list']
		
		# load unit stats for reference from JSON file
		with open(DATAPATH + 'unit_type_defs.json', encoding='utf8') as data_file:
			unit_types = json.load(data_file)
		
		# determine initial number of enemy units to spawn: 1-4
		if num_units is None:
			num_units = 4
			for i in range(3):
				if libtcod.random_get_int(0, 0, 10) >= self.cd_map_hex.enemy_strength:
					num_units -= 1
		
		enemy_unit_list = []
		while len(enemy_unit_list) < num_units:
			
			if libtcod.console_is_window_closed(): sys.exit()
		
			# choose a random unit class
			unit_class = None
			while unit_class is None:
				k, value = choice(list(campaign.stats['enemy_unit_class_odds'].items()))
				if GetPercentileRoll() <= float(value):
					unit_class = k
			
			# FUTURE: if class unit type has already been set, use that one instead
			
			# choose a random unit type
			type_list = []
			for unit_id in unit_type_list:
				# unrecognized unit id
				if unit_id not in unit_types: continue
				# not the right class
				if unit_types[unit_id]['class'] != unit_class: continue
				type_list.append(unit_id)
			
			# no units of the correct class found
			if len(type_list) == 0: continue
			
			# select unit type: run through shuffled list and roll against rarity if any
			shuffle(type_list)
			
			selected_unit_id = None
			for unit_id in type_list:
			
				# if no rarity factor given, select automatically
				if 'rarity' not in unit_types[unit_id]:
					selected_unit_id = unit_id
					break
				
				# roll against rarity for current date
				rarity = None
				for date, chance in unit_types[unit_id]['rarity'].items():
					
					# select the earliest rarity factor
					if rarity is None:
						
						# if the earliest rarity factor is still later than current date, do not spawn
						if date > campaign.today:
							break
						
						rarity = int(chance)
						continue
					
					# break if this date is later than current date
					if date > campaign.today: break
						
					# earlier than or equal to today's date, use this rarity factor 
					rarity = int(chance)
				
				# not able to get a rarity factor
				if rarity is None:
					continue
				
				# roll againt rarity rarting
				if GetPercentileRoll() <= float(rarity):
					selected_unit_id = unit_id
					break
			
			# if able to roll for rarity, add the final selected unit id to list to spawn
			if selected_unit_id is not None:
				enemy_unit_list.append(selected_unit_id)
		
		# spawn one unit per unit id in the list
		for unit_id in enemy_unit_list:
	
			# determine spawn location
			distance = libtcod.random_get_int(0, 1, 3)
			
			if distance == 1:
				if GetPercentileRoll() <= 65.0:
					distance += 1
			if unit_types[unit_id]['category'] == 'Infantry':
				if GetPercentileRoll() <= 75.0:
					distance -= 1
			elif unit_types[unit_id]['category'] == 'Vehicle':
				if GetPercentileRoll() <= 60.0:
					distance += 1
			
			if distance < 1:
				distance = 1
			elif distance > 3:
				distance = 3
			
			hex_list = GetHexRing(0, 0, distance)
			shuffle(hex_list)
			
			# choose a random hex in which to spawn
			for (hx, hy) in hex_list:
				
				# if player spotted enemy units first, unlikely that they will spawn behind the player
				if not self.ambush:
					if GetDirectionToward(hx, hy, 0, 0) in [5, 0, 1]:
						if GetPercentileRoll() <= 85.0: continue
				break
			
			# create the unit
			unit = Unit(unit_id)
			unit.owning_player = 1
			unit.nation = campaign.current_week['enemy_nation']
			unit.ai = AI(unit)
			unit.GenerateNewPersonnel()
			unit.SpawnAt(hx, hy)
			if unit.GetStat('category') == 'Gun':
				unit.deployed = True
			
			# set facing if any toward player
			direction = GetDirectionToward(unit.hx, unit.hy, 0, 0)
			if unit.GetStat('category') != 'Infantry':
				unit.facing = direction
			
			# turreted vehicle
			if 'turret' in unit.stats:
				unit.turret_facing = direction
			
			# special: some units are spawned with non-combat companion units
			if unit_id == 'Light Artillery Car':
				unit = Unit('Locomotive')
				unit.owning_player = 1
				unit.nation = campaign.current_week['enemy_nation']
				unit.ai = AI(unit)
				unit.GenerateNewPersonnel()
				unit.SpawnAt(hx, hy)
				unit.facing = GetDirectionToward(unit.hx, unit.hy, 0, 0)
			
			# if player used advancing fire, test for pin
			if campaign_day.advancing_fire:
				if unit.GetStat('category') not in ['Infantry', 'Gun']:
					continue
				unit.PinTest(10.0, no_msg=True)
	
	
	# given a combination of an attacker, weapon, and target, see if this would be a
	# valid attack; if not, return a text description of why not
	# if ignore_facing is true, we don't check whether weapon is facing correct direction
	def CheckAttack(self, attacker, weapon, target, ignore_facing=False):
		
		# check that proper crew command has been set if player is attacking
		if attacker == self.player_unit:
			
			# FUTURE: move this check to weapon object and use in
			# advance phase to skip shooting phase automatically
			position_list = weapon.GetStat('fired_by')
			if position_list is None:
				return 'No positions to fire this weapon'
			
			if weapon.GetStat('type') == 'Gun':
				command_req = 'Operate Gun'
			elif weapon.GetStat('type') in MG_WEAPONS:
				command_req = 'Operate MG'
			else:
				return 'Unknown weapon type!'
				
			crewman_found = False
			for position in position_list:
				crewman = attacker.GetPersonnelByPosition(position)
				if crewman is None: continue
				if crewman.current_cmd != command_req: continue
				crewman_found = True
				break
			
			if not crewman_found:
				return 'No crewman operating this weapon'
		
		# check that weapon hasn't already fired
		if weapon.fired:
			return 'Weapon has already fired this turn'
		
		# if we're not ignoring facing,
		# check that target is in covered hexes and range
		if not ignore_facing:
			if (target.hx, target.hy) not in weapon.covered_hexes:
				return "Target not in weapon's covered arc"
		
		# check that current ammo is available and this ammo would affect the target
		if weapon.GetStat('type') == 'Gun':
			
			if weapon.ammo_type is None:
				return 'No ammo loaded'
			
			# check that at least one shell of required ammo is available
			ammo_avail = False
			if weapon.using_rr:
				if weapon.ready_rack[weapon.ammo_type] > 0:
					ammo_avail = True
			if weapon.ammo_stores[weapon.ammo_type] > 0:
				ammo_avail = True
			if not ammo_avail:
				return 'No more ammo of the selected type'
			
			if weapon.ammo_type == 'AP' and target.GetStat('category') in ['Infantry', 'Gun']:
				return 'AP has no effect on target'
		
		# check firing group restrictions
		for weapon2 in attacker.weapon_list:
			if weapon2 == weapon: continue
			if not weapon2.fired: continue
			if weapon2.GetStat('firing_group') == weapon.GetStat('firing_group'):
				return 'A weapon on this mount has already fired'
		
		# check for hull-mounted weapons blocked by HD status
		if len(attacker.hull_down) > 0:
			mount = weapon.GetStat('mount')
			if mount is not None:
				if mount == 'Hull':
					if GetDirectionToward(attacker.hx, attacker.hy, target.hx, target.hy) in attacker.hull_down:
						return 'Weapon blocked by HD status'
			
		# attack can proceed
		return ''
	
	
	# generate a profile for a given attack
	# if pivot or turret_rotate are set to True or False, will override actual attacker status
	def CalcAttack(self, attacker, weapon, target, pivot=False, turret_rotate=False):
		
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
		
		# determine crewman operating weapon
		profile['crewman'] = None
		if weapon.GetStat('fired_by') is not None:
			profile['crewman'] = attacker.GetPersonnelByPosition(weapon.stats['fired_by'][0])
		
		# calculate distance to target
		distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
		
		# list of modifiers
		# [maximum displayable modifier description length is 18 characters]
		
		modifier_list = []
		
		# base critical hit chance
		profile['critical_hit'] = CRITICAL_HIT
		
		# point fire attacks (eg. large guns)
		if profile['type'] == 'Point Fire':
			
			# calculate critical hit chance modifier
			if profile['crewman'] is not None:
				if 'Knows Weak Spots' in profile['crewman'].skills:
					if weapon_type == 'Gun' and target.GetStat('armour') is not None:
						profile['critical_hit'] += 2.0
			
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
			elif pivot or attacker.facing != attacker.previous_facing:
				if weapon.GetStat('turntable') is not None:
					modifier_list.append(('Attacker Pivoted', -15.0))
				else:
					modifier_list.append(('Attacker Pivoted', -35.0))
			
			# player or player squad member attacker pivoted
			elif self.player_pivot != 0 and (attacker == scenario.player_unit or attacker in scenario.player_unit.squad):
				modifier_list.append(('Attacker Pivoted', -35.0))

			# weapon has turret rotated
			elif weapon.GetStat('mount') == 'Turret':
				if turret_rotate or attacker.turret_facing != attacker.previous_turret_facing:
					
					# calculate modifier - assume that vehicle has a turret
					if attacker.GetStat('turret') == 'Fast':
						mod = -10.0
					else:
						mod = -20.0
					modifier_list.append(('Turret Rotated', mod))
			
			# attacker pinned
			if attacker.pinned:
				modifier_list.append(('Attacker Pinned', -60.0))
			
			# precipitation effects
			if campaign_day.weather['Precipitation'] == 'Rain':
				modifier_list.append(('Rain', -5.0 * float(distance)))
			elif campaign_day.weather['Precipitation'] == 'Snow':
				modifier_list.append(('Snow', -10.0 * float(distance)))
			elif campaign_day.weather['Precipitation'] == 'Heavy Rain':
				modifier_list.append(('Heavy Rain', -15.0 * float(distance)))
			elif campaign_day.weather['Precipitation'] == 'Blizzard':
				modifier_list.append(('Blizzard', -20.0 * float(distance)))
			
			# smoke
			total_smoke = 0
			direction = GetDirectionToward(attacker.hx, attacker.hy, target.hx, target.hy)
			total_smoke += attacker.smoke[direction]
			direction = GetDirectionToward(target.hx, target.hy, attacker.hx, attacker.hy)
			total_smoke += target.smoke[direction]
			
			if total_smoke >= 2:
				modifier_list.append(('Smoke', -50.0))
			elif total_smoke == 1:
				modifier_list.append(('Smoke', -25.0))
			
			# unspotted target
			if not target.spotted:
				modifier_list.append(('Unspotted Target', -20.0))
			
			# spotted target
			else:
				
				# check to see if weapon has acquired target
				if weapon.acquired_target is not None:
					(ac_target, level) = weapon.acquired_target
					if ac_target == target:
						text = 'Acquired Target'
						if level == 1:
							text += '+'
						modifier_list.append((text, AC_BONUS[distance][level]))
				
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
				
				# target terrain
				tem = target.GetTEM()
				if tem != 0.0:
					modifier_list.append((target.terrain, tem))
			
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
				
				if weapon.stats['name'] == 'AT Rifle':
					calibre = 20
				else:
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
			elif attacker == scenario.player_unit and self.player_pivot != 0:
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
			
			# smoke
			total_smoke = 0
			direction = GetDirectionToward(attacker.hx, attacker.hy, target.hx, target.hy)
			total_smoke += attacker.smoke[direction]
			direction = GetDirectionToward(target.hx, target.hy, attacker.hx, attacker.hy)
			total_smoke += target.smoke[direction]
			
			if total_smoke > 0:
				if total_smoke >= 2:
					mod = round(base_chance / 2.0, 2)
				else:
					mod = round(base_chance / 3.0, 2)
				modifier_list.append(('Smoke', 0.0 - mod))
			
			if not target.spotted:
				modifier_list.append(('Unspotted Target', -10.0))
			else:
				
				# check to see if MG has acquired target
				if weapon.acquired_target is not None:
					(ac_target, level) = weapon.acquired_target
					if ac_target == target:
						mod = round(15.0 + (float(level) * 15.0), 2)
						if distance == 3:
							mod = round(mod * 1.15, 2)
						text = 'Acquired Target'
						if level == 1:
							text += '+'
						modifier_list.append((text, mod))
			
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
				
				# gun shield
				if target.GetStat('gun_shield') is not None:
					if GetFacing(attacker, target) == 'Front':
						modifier_list.append(('Gun Shield', -15.0))
				
		# check for Commander directing fire
		# FUTURE: may be possible for other positions as well (Commander/Driver?)
		for position in ['Commander']:
			crewman = attacker.GetPersonnelByPosition(position)
			if crewman is None: continue
			if crewman.current_cmd == 'Direct Fire':
				mod = crewman.GetActionMod('Direct Fire')
				if mod > 0.0:
					modifier_list.append(('Cmdr Direction', mod))
				
					# check for skill modifiers
					if 'Fire Spotter' in crewman.skills:
						modifier_list.append(('Fire Spotter', 3.0))
					
					if 'MG Spotter' in crewman.skills:
						if weapon_type in MG_WEAPONS:
							modifier_list.append(('MG Spotter', 7.0))
					
					if 'Gun Spotter' in crewman.skills:
						if weapon_type == 'Gun':
							modifier_list.append(('Gun Spotter', 7.0))
					
				break
		
		# check for firing crew skills
		if profile['crewman'] is not None:
			
			if weapon_type == 'Gun':
				if 'Crack Shot' in profile['crewman'].skills:
					modifier_list.append(('Crack Shot', 3.0))
				if target.moving and 'Target Tracker' in profile['crewman'].skills:
					modifier_list.append(('Target Tracker', 7.0))
				if distance == 3 and 'Sniper' in profile['crewman'].skills:
					modifier_list.append(('Sniper', 7.0))
		
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
		
		# set rear facing flag if applicable
		rear_facing = False
		if facing == 'Rear':
			rear_facing = True
			facing = 'Side'
		
		hit_location = (location + '_' + facing).lower()
		
		# generate a text description of location hit
		if location == 'Turret' and target.turret_facing is None:
			location = 'Upper Hull'
		profile['location_desc'] = location + ' '
		if rear_facing:
			profile['location_desc'] += 'Rear'
		else:
			profile['location_desc'] += facing
		
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
		
		# unarmoured targets use flat modifiers
		
		# FUTURE: check for unarmoured locations on otherwise armoured targets
		
		armour = target.GetStat('armour')
		if armour is None:
			
			if profile['result'] == 'CRITICAL HIT':
				modifier_list.append(('Critical Hit', 75.0))
			
			elif profile['ammo_type'] == 'HE':
				modifier_list.append(('Unarmoured Target', 25.0))
			
			# AP hits have a chance to punch right through
			else:
				modifier_list.append(('Unarmoured Target', -18.0))
			
		else:
		
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
		
			# hit location is armoured
			if armour[hit_location] != '-':
				target_armour = int(armour[hit_location])
				if target_armour >= 0:
					modifier = target_armour * -12.0
					modifier_list.append(('Target Armour', modifier))
					
					# apply rear facing modifier if any
					if rear_facing:
						modifier_list.append(('Rear Facing', 15.0))
					
					# apply critical hit modifier if any
					if profile['result'] == 'CRITICAL HIT':
						modifier = round(modifier * 0.8, 2)
						modifier_list.append(('Critical Hit', modifier))
		
		# save the list of modifiers
		profile['modifier_list'] = modifier_list[:]
		
		# calculate total modifer
		total_modifier = 0.0
		for (desc, mod) in modifier_list:
			total_modifier += mod
		
		# calculate final chance of success
		# possible to be impossible or for penetration to be automatic
		profile['final_chance'] = round(profile['base_chance'] + total_modifier, 2)
		if profile['final_chance'] < 0.0:
			profile['final_chance'] = 0.0
		elif profile['final_chance'] > 100.0:
			profile['final_chance'] = 100.0
		
		return profile
	
	
	# generate an attack console to display an attack or AP profile to the screen and prompt to proceed
	# does not alter the profile
	def DisplayAttack(self, profile):
		
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
			# AP checks may be automatic or impossible
			if profile['type'] == 'ap':
				if profile['final_chance'] == 0.0:
					text = 'Impossible'
				elif profile['final_chance'] == 100.0:
					text = 'Automatic'
			libtcod.console_print_ex(attack_con, 13, 47, libtcod.BKGND_NONE,
				libtcod.CENTER, text)
		
		# display prompts
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		if profile['attacker'] == self.player_unit and profile['type'] != 'ap':
			libtcod.console_print(attack_con, 6, 56, 'Bksp')
		libtcod.console_print(attack_con, 6, 57, 'Tab')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		if profile['attacker'] == self.player_unit and profile['type'] != 'ap':
			libtcod.console_print(attack_con, 12, 56, 'Cancel')
		libtcod.console_print(attack_con, 12, 57, 'Continue')
		
		
	
	# do a roll, animate the attack console, and display the results
	# returns an modified attack profile
	def DoAttackRoll(self, profile):
		
		# clear prompts from attack console
		libtcod.console_print(attack_con, 6, 56, '                  ')
		libtcod.console_print(attack_con, 6, 57, '                  ')
		
		result_text = ''
		
		# if AP roll, may not need to roll
		if profile['type'] == 'ap':
			if profile['final_chance'] == 0.0:
				result_text = 'NO PENETRATION'
			elif profile['final_chance'] == 100.0:
				result_text = 'PENETRATED'
		
		# only roll if outcome not yet determined
		if result_text == '':
		
			# don't animate percentage rolls if player is not involved
			if profile['attacker'] != scenario.player_unit and profile['target'] != scenario.player_unit:
				roll = GetPercentileRoll()
			else:
				for i in range(6):
					roll = GetPercentileRoll()
					
					# modifiers applied to the final roll, the one that counts
					if i == 5:
					
						# check for player fate point usage
						if profile['target'] == scenario.player_unit and campaign_day.fate_points > 0:
							
							# hit or penetration
							if roll <= profile['final_chance'] or roll <= profile['critical_hit']:
								
								# point fire hit
								if profile['type'] == 'Point Fire':
									
									# hit with large calibre weapon
									if profile['weapon'].GetStat('calibre') is not None:
										if int(profile['weapon'].GetStat('calibre')) > 25:
											
											# apply fate point
											campaign_day.fate_points -= 1
											roll = profile['final_chance'] + float(libtcod.random_get_int(0, 10, 500)) / 10.0
											if roll > 97.0:
												roll = 97.0
								
								# AP penetration
								elif profile['type'] == 'ap':
									
									# apply fate point
									campaign_day.fate_points -= 1
									roll = profile['final_chance'] + float(libtcod.random_get_int(0, 10, 500)) / 10.0
									if roll > 97.0:
										roll = 97.0
					
						# check for debug flag - force a hit or penetration
						if DEBUG:
							if profile['attacker'] == scenario.player_unit and session.debug['Player Always Hits']:
								while roll >= profile['final_chance']:
									roll = GetPercentileRoll()
							elif profile['target'] == scenario.player_unit and profile['type'] == 'ap' and session.debug['Player Always Penetrated']:
								while roll >= profile['final_chance']:
									roll = GetPercentileRoll()
							elif profile['target'] == scenario.player_unit and profile['type'] != 'ap' and session.debug['AI Hates Player']:	
								while roll >= profile['final_chance']:
									roll = GetPercentileRoll()
					
					# clear any previous text
					libtcod.console_print_ex(attack_con, 13, 49, libtcod.BKGND_NONE,
						libtcod.CENTER, '      ')
					
					text = str(roll) + '%%'
					libtcod.console_print_ex(attack_con, 13, 49, libtcod.BKGND_NONE,
						libtcod.CENTER, text)
					
					scenario.UpdateScenarioDisplay()
					
					# don't animate if fast mode debug flag is set
					if DEBUG and session.debug['Fast Mode']:
						continue
					
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
				elif roll <= profile['critical_hit']:
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
		if profile['attacker'] != scenario.player_unit and profile['target'] != scenario.player_unit:
			return profile
		
		# play sound effect for HD save
		if profile['result'] == 'MISS - HULL DOWN':
			PlaySoundFor(None, 'hull_down_save')
		
		# display result on screen
		libtcod.console_print_ex(attack_con, 13, 51, libtcod.BKGND_NONE,
			libtcod.CENTER, result_text)
		
		# display effective FP if it was successful area fire attack
		if profile['type'] == 'Area Fire' and result_text != 'NO EFFECT':
			libtcod.console_print_ex(attack_con, 13, 52, libtcod.BKGND_NONE,
				libtcod.CENTER, str(profile['effective_fp']) + ' FP')
		
		# check for RoF for gun / MG attacks
		if profile['type'] != 'ap' and profile['weapon'].GetStat('rof') is not None:
			
			# FUTURE: possibly allow AI units to maintain RoF?
			if profile['attacker'] == scenario.player_unit:
				
				if GetPercentileRoll() <= profile['weapon'].GetRoFChance():
					profile['weapon'].maintained_rof = True
				else:
					profile['weapon'].maintained_rof = False
				
				if profile['weapon'].maintained_rof:
					libtcod.console_print_ex(attack_con, 13, 53, libtcod.BKGND_NONE,
						libtcod.CENTER, 'Maintained Rate of Fire')
					libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
					libtcod.console_print(attack_con, 6, 56, EnKey('f').upper())
					libtcod.console_set_default_foreground(attack_con, libtcod.white)
					libtcod.console_print(attack_con, 12, 56, 'Fire Again')
		
		# display prompt
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		libtcod.console_print(attack_con, 6, 57, 'Tab')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		libtcod.console_print(attack_con, 12, 57, 'Continue')
		
		return profile
	
	
	# selecte a different weapon on the player unit
	def SelectWeapon(self, forward):
		
		if self.selected_weapon is None:
			self.selected_weapon = scenario.player_unit.weapon_list[0]
			return
		
		if forward:
			m = 1
		else:
			m = -1
		
		i = scenario.player_unit.weapon_list.index(self.selected_weapon)
		i += m
		
		if i < 0:
			self.selected_weapon = scenario.player_unit.weapon_list[-1]
		elif i > len(scenario.player_unit.weapon_list) - 1:
			self.selected_weapon = scenario.player_unit.weapon_list[0]
		else:
			self.selected_weapon = scenario.player_unit.weapon_list[i]
	
	
	# (re)build a sorted list of possible player targets
	def BuildTargetList(self):
		
		self.target_list = []
		
		for unit in self.units:
			# allied unit
			if unit.owning_player == 0: continue
			# beyond active part of map
			if GetHexDistance(0, 0, unit.hx, unit.hy) > 3: continue
			self.target_list.append(unit)
		
		# old player weapon target no longer on list
		for weapon in self.player_unit.weapon_list:
			if weapon.selected_target not in self.target_list:
				weapon.selected_target = None
	
	
	# cycle selected target for player weapon
	# FUTURE: combine into general "next in list, previous in list, wrap around" function
	def CycleTarget(self, forward):
		
		# no weapon selected
		if self.selected_weapon is None: return
		
		# no targets to select from
		if len(self.target_list) == 0: return
		
		# no target selected yet
		if self.selected_weapon.selected_target is None:
			self.selected_weapon.selected_target = self.target_list[0]
			return
		
		if forward:
			m = 1
		else:
			m = -1
		
		i = self.target_list.index(self.selected_weapon.selected_target)
		i += m
		
		if i < 0:
			self.selected_weapon.selected_target = self.target_list[-1]
		elif i > len(self.target_list) - 1:
			self.selected_weapon.selected_target = self.target_list[0]
		else:
			self.selected_weapon.selected_target = self.target_list[i]
		
		self.selected_weapon.selected_target.MoveToTopOfStack()
		self.UpdateUnitCon()
		self.UpdateUnitInfoCon()
	
	
	# roll to see if air and/or arty support requests were granted, and trigger attacks if so
	def ResolveSupportRequests(self):
		
		# FUTURE: calculate any skill effects for the roll(s) here
		
		# check for air attack first
		if campaign_day.air_support_request:
			roll = GetPercentileRoll()
			granted = False
			if DEBUG:
				if session.debug['Support Requests Always Granted']:
					granted = True
			if roll <= campaign_day.air_support_level:
				granted = True
			
			# check for weather restrictions
			if campaign_day.weather['Cloud Cover'] == 'Overcast':
				ShowMessage('Cannot offer air attack support - cloud cover too heavy.')
				granted = False
			
			if granted:
				campaign_day.air_support_level -= 10.0
				if campaign_day.air_support_level < 0.0:
					campaign_day.air_support_level = 0.0
				self.DoAirAttack()
			else:
				ShowMessage('Unable to provide air support at this time.')
		
		# check for artillery attack
		if campaign_day.arty_support_request:
			roll = GetPercentileRoll()
			granted = False
			if DEBUG:
				if session.debug['Support Requests Always Granted']:
					granted = True
			if roll <= campaign_day.arty_support_level:
				granted = True
			
			if granted:
				campaign_day.arty_support_level -= 10.0
				if campaign_day.arty_support_level < 0.0:
					campaign_day.arty_support_level = 0.0
				self.DoArtilleryAttack()
			else:
				ShowMessage('Unable to provide artillery support at this time.')
		
		# reset flags
		campaign_day.air_support_request = False
		campaign_day.arty_support_request = False
	
	
	# resolve an air support attack against enemy units
	def DoAirAttack(self):
		
		ShowMessage('Air support attack inbound! Trying to spot targets.')
		
		# calculate base spotting chance and add weather modifiers
		chance = 55.0
			
		if campaign_day.weather['Cloud Cover'] == 'Scattered':
			chance -= 10.0
		elif campaign_day.weather['Cloud Cover'] == 'Heavy':
			chance -= 20.0
		if campaign_day.weather['Precipitation'] in ['Rain', 'Snow']:
			chance -= 15.0
		elif campaign_day.weather['Precipitation'] in ['Heavy Rain', 'Blizzard']:
			chance -= 25.0
		
		# check each hex with 1+ enemy units present
		target_hex_list = []
		for map_hex in self.map_hexes:
			if len(map_hex.unit_stack) == 0: continue
			if map_hex.unit_stack[0].owning_player == 0: continue
			
			# roll to spot each enemy unit in hex
			for unit in map_hex.unit_stack:
			
				modifier = 0.0
					
				total_smoke = 0
				for i in range(6):
					total_smoke += unit.smoke[i]
				if total_smoke > 0:
					modifier -= 5.0
				
				size_class = unit.GetStat('size_class')
				if size_class is not None:
					if size_class == 'Small':
						modifier -= 7.0
					elif size_class == 'Very Small':
						modifier -= 18.0
					elif size_class == 'Large':
						modifier += 7.0
					elif size_class == 'Very Large':
						modifier += 18.0
				
				if unit.moving:
					modifier += 10.0
				
				modifier += unit.GetTEM()
				
				# not spotted
				if GetPercentileRoll() > RestrictChance(chance + round(modifier * 0.25, 2)):
					continue
				
				# spotted, add this hex to targets and don't check any other units present
				target_hex_list.append(map_hex)
				break
		
		if len(target_hex_list) == 0:
			ShowMessage('No targets spotted, ending attack.')
			return
		
		
		# roll for number of planes
		roll = libtcod.random_get_int(0, 1, 10)
		if roll <= 5:
			num_planes = 1
		elif roll <= 8:
			num_planes = 2
		else:
			num_planes = 3
		
		# determine type of plane
		plane_id = choice(campaign.stats['player_air_support'])
		
		# display message
		text = str(num_planes) + ' ' + plane_id + ' arrive'
		if num_planes == 1: text += 's'
		text += ' for an attack.'
		ShowMessage(text)
		
		# create plane units
		plane_unit_list = []
		for i in range(num_planes):
			plane_unit_list.append(Unit(plane_id))
		
		# determine calibre for bomb attack
		for weapon in plane_unit_list[0].weapon_list:
			if weapon.stats['name'] == 'Bombs':
				bomb_calibre = int(weapon.stats['calibre'])
				break
		
		# determine effective fp
		for (calibre, effective_fp) in HE_FP_EFFECT:
			if calibre <= bomb_calibre:
				break
		
		# do one attack animation per target hex
		for map_hex in target_hex_list:
		
			# determine attack direction and starting position
			(x, y) = self.PlotHex(map_hex.hx, map_hex.hy)
			(x2, y2) = (x, y)
			
			if y2 <= 30:
				y1 = y2 + 15
				if y1 > 51: y1 = 51
				# TODO: needs changing: y2 is incorrect
				y2 += 1
				direction = -1
			else:
				y1 = y2 - 15
				if y1 < 9: y1 = 9
				y2 -= 3
				direction = 1
			
			# create air attack animation
			self.animation['air_attack'] = GeneratePlaneCon(direction)
			self.animation['air_attack_line'] = GetLine(x, y1, x, y2)
			
			PlaySoundFor(None, 'plane_incoming')
			
			# let animation run
			while self.animation['air_attack'] is not None:
				if libtcod.console_is_window_closed(): sys.exit()
				libtcod.console_flush()
				CheckForAnimationUpdate()
			
			PlaySoundFor(None, 'stuka_divebomb')
			
			# create bomb animation
			self.animation['bomb_effect'] = (x, y2+direction)
			self.animation['bomb_effect_lifetime'] = 14
			
			# let animation run
			while self.animation['bomb_effect'] is not None:
				if libtcod.console_is_window_closed(): sys.exit()
				libtcod.console_flush()
				CheckForAnimationUpdate()
		
		# do one attack per plane per target hex
		results = False
		for map_hex in target_hex_list:
		
			for unit in plane_unit_list:
			
				# find a target unit in the target hex
				if len(map_hex.unit_stack) == 0:
					continue
				target = choice(map_hex.unit_stack)
			
				# calculate basic to-effect score required
				if not target.spotted:
					chance = PF_BASE_CHANCE[0][1]
				else:
					if target.GetStat('category') == 'Vehicle':
						chance = PF_BASE_CHANCE[0][0]
					else:
						chance = PF_BASE_CHANCE[0][1]
			
				# target size modifier
				size_class = target.GetStat('size_class')
				if size_class is not None:
					if size_class != 'Normal':
						chance += PF_SIZE_MOD[size_class]
				
				# smoke modifier
				total_smoke = 0
				for i in range(6):
					total_smoke += target.smoke[i]
				if total_smoke >= 2:
					chance -= 30.0
				elif total_smoke == 1:
					chance -= 15.0
				
				chance = RestrictChance(chance)
				roll = GetPercentileRoll()
				
				if roll > chance: continue
				
				# hit
				results = True
				
				# roll for direct hit / near miss
				direct_hit = False
				if GetPercentileRoll() <= DIRECT_HIT_CHANCE:
					direct_hit = True
				
				# infantry or gun target
				if target.GetStat('category') in ['Infantry', 'Gun']:
					
					# direct hit: destroyed
					if direct_hit:
						ShowMessage(target.GetName() + ' was destroyed by a direct hit from the air attack.')
						target.DestroyMe()
						continue
					
					if not target.spotted:
						target.hit_by_fp = True
					
					ShowMessage(target.GetName() + ' was hit by air attack')
				
				# vehicle hit
				elif target.GetStat('category') == 'Vehicle':
					
					# direct hit - unarmoured and open topped vehicles destroyed
					if direct_hit:
						if target.GetStat('armour') is None or target.GetStat('open_topped') is not None:
							ShowMessage(target.GetName() + ' was destroyed by a direct hit from the air attack.')
							target.DestroyMe()
							continue
					
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
					
					# direct hit modifier
					if direct_hit:
						chance = round(chance * 2.0, 1)
						print('DEBUG: Applied direct hit modifier, chance now ' + str(chance))
					
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
					
					# calculate final chance
					chance = RestrictChance(chance)
					
					# do AP roll
					roll = GetPercentileRoll()
					
					# no penetration
					if roll > chance:
						ShowMessage(target.GetName() + ' was unaffected by air attack')
						continue
					
					# penetrated
					target.DestroyMe()
					ShowMessage(target.GetName() + ' was destroyed by air attack')
				
		if not results:
			ShowMessage('Air attack had no effect.')
		
		# clean up
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
	
	
	# do an artillery attack against enemy units
	def DoArtilleryAttack(self):
		
		ShowMessage('Artillery support attack inbound! Trying to spot targets.')
		
		# do an attack on every hex with an enemy unit in it
		target_hex_list = []
		for map_hex in self.map_hexes:
			if len(map_hex.unit_stack) == 0: continue
			if map_hex.unit_stack[0].owning_player == 0: continue
			target_hex_list.append(map_hex)
		
		# no possible targets
		if len(target_hex_list) == 0:
			ShowMessage('No targets spotted, ending attack.')
			return
		
		ShowMessage('Target spotted, firing for effect.')
		
		# display bombardment animation
		for map_hex in target_hex_list:
			
			(x, y) = self.PlotHex(map_hex.hx, map_hex.hy)
			for i in range(3):
				xm = 3 - libtcod.random_get_int(0, 0, 6)
				ym = 3 - libtcod.random_get_int(0, 0, 6)
				PlaySoundFor(None, 'he_explosion')
				# create bomb animation
				self.animation['bomb_effect'] = (x+xm, y+ym)
				self.animation['bomb_effect_lifetime'] = 3
				
				# let animation run
				while self.animation['bomb_effect'] is not None:
					if libtcod.console_is_window_closed(): sys.exit()
					libtcod.console_flush()
					CheckForAnimationUpdate()
		
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
		
		# roll for possible hit against each enemy unit in each target hex
		results = False
		for map_hex in target_hex_list:
		
			for target in map_hex.unit_stack:
				
				if target.owning_player == 0: continue
				if not target.alive: continue
				
				# calculate base effect chance
				if target.GetStat('category') == 'Vehicle':
					chance = VEH_FP_BASE_CHANCE
				else:
					chance = INF_FP_BASE_CHANCE
				for i in range(2, effective_fp + 1):
					chance += FP_CHANCE_STEP * (FP_CHANCE_STEP_MOD ** (i-1)) 
				
				# FUTURE: apply further modifiers here
				
				chance = round(chance, 2)
				roll = GetPercentileRoll()
				
				# no effect
				if roll > chance:
					continue
				
				results = True
				
				# roll for direct hit / near miss
				direct_hit = False
				if GetPercentileRoll() <= DIRECT_HIT_CHANCE:
					direct_hit = True
				
				# infantry or gun target hit
				if target.GetStat('category') in ['Infantry', 'Gun']:
					
					# direct hit: destroyed
					if direct_hit:
						ShowMessage(target.GetName() + ' was destroyed by a direct hit from the artillery attack.')
						target.DestroyMe()
						continue
					
					if not target.spotted:
						target.hit_by_fp = True
					
					ShowMessage(target.GetName() + ' was hit by artillery attack.')
					
					target.ResolveFP()
				
				# vehicle hit
				elif target.GetStat('category') == 'Vehicle':
					
					# direct hit - unarmoured and open topped vehicles destroyed
					if direct_hit:
						if target.GetStat('armour') is None or target.GetStat('open_topped') is not None:
							ShowMessage(target.GetName() + ' was destroyed by a direct hit from the artillery attack.')
							target.DestroyMe()
							continue
					
					# determine location hit - use side locations and modify later
					# for aerial attack
					if GetPercentileRoll() <= 50.0:
						hit_location = 'hull_side'
					else:
						hit_location = 'turret_side'
					
					# start with base AP chance
					chance = ap_chance
					
					# direct hit modifier
					if direct_hit:
						chance = round(chance * 2.0, 1)
						print('DEBUG: Applied direct hit modifier, chance now ' + str(chance))
					
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
								
					# calculate final chance of AP and do roll
					chance = RestrictChance(chance)
					roll = GetPercentileRoll()
					
					# no penetration
					if roll > chance:
						ShowMessage(target.GetName() + ' was hit by artillery attack but is unharmed.')
						if not target.spotted:
							target.hit_by_fp = True
						continue
					
					# penetrated
					target.DestroyMe()
					ShowMessage(target.GetName() + ' was destroyed by artillery attack')
		
		if not results:
			ShowMessage('Artillery attack had no effect.')
	
	
	# execute a player move forward/backward, repositioning units on the hex map as needed
	def MovePlayer(self, forward, reposition=False):
		
		# check for double bog check 
		if not reposition:
		
			if 'Double Bog Check' in SCENARIO_TERRAIN_EFFECTS[self.player_unit.terrain]:
				# FUTURE: check for squad units too
				for unit in self.units:
					if unit != self.player_unit: continue
					unit.DoBogCheck(forward)
			
			# notify player and update consoles if player bogged
			if self.player_unit.bogged:
				ShowMessage('Your tank has becomed bogged.')
				self.UpdatePlayerInfoCon()
				self.UpdateUnitCon()
				self.advance_phase = True
				return
		
		# do sound effect
		PlaySoundFor(self.player_unit, 'movement')
		
		# set statuses
		self.player_unit.moving = True
		self.player_unit.ClearAcquiredTargets()
		for unit in scenario.player_unit.squad:
			unit.moving = True
			unit.ClearAcquiredTargets()
		
		if reposition:
			roll = -100.0
		else:
		
			# do move success roll
			if forward:
				chance = scenario.player_unit.forward_move_chance
			else:
				chance = scenario.player_unit.reverse_move_chance
			roll = GetPercentileRoll()
			
			# check for crew action modifier
			for position in ['Commander', 'Commander/Gunner']:
				crewman = self.player_unit.GetPersonnelByPosition(position)
				if crewman is None: continue
				if crewman.current_cmd == 'Direct Movement':
					chance += crewman.GetActionMod('Direct Movement')
					
					# check for skill modifiers
					if 'Driver Direction' in crewman.skills:
						chance += 5.0
					if forward and 'Forward!' in crewman.skills:
						chance += 10.0
					
				break
			
			# check for driver skill
			crewman = self.player_unit.GetPersonnelByPosition('Driver')
			if crewman is not None:
				if 'Quick Shifter' in crewman.skills:
					chance += 5.0
			
			# check for debug flag
			if DEBUG:
				if session.debug['Player Always Moves']:
					roll = 1.0
		
		# move was not successful
		if not reposition and roll > chance:
			
			# clear any alternative bonus and apply bonus for future moves
			if forward:
				self.player_unit.reverse_move_bonus = 0.0
				self.player_unit.forward_move_bonus += BASE_MOVE_BONUS
			else:
				self.player_unit.forward_move_bonus = 0.0
				self.player_unit.reverse_move_bonus += BASE_MOVE_BONUS
			
			# show pop-up message to player
			ShowMessage('You move but not far enough to enter a new map hex')
			
			# set new terrain for player and squad
			for unit in self.units:
				if unit != self.player_unit and unit not in self.player_unit.squad: continue
				unit.GenerateTerrain()
				unit.CheckForHD()
			
			# end movement phase
			self.advance_phase = True
			
			return
		
		# successful move may be cancelled by breakdown
		if self.player_unit.BreakdownCheck():
			ShowMessage('Your vehicle stalls, making you unable to move further.')
			if reposition: return
			self.advance_phase = True
			return
		
		if not reposition:
		
			# move was successful, clear all bonuses
			self.player_unit.forward_move_bonus = 0.0
			self.player_unit.reverse_move_bonus = 0.0
			
			# calculate new hex positions for each unit in play
			if forward:
				direction = 3
			else:
				direction = 0
			
			# run through list of units and move them
			# player movement will never move an enemy unit into ring 4 nor off board
			for unit in self.units:
				
				if unit == self.player_unit: continue
				if unit in self.player_unit.squad: continue
				
				(new_hx, new_hy) = GetAdjacentHex(unit.hx, unit.hy, direction)
				
				# skip if unit would end up in ring 4 or off board
				if GetHexDistance(0, 0, new_hx, new_hy) > 3:
					continue
					
				# special case: jump over player hex 0,0
				jump = False
				if new_hx == 0 and new_hy == 0:
					(new_hx, new_hy) = GetAdjacentHex(0, 0, direction)
					jump = True
				
				# set destination hex
				unit.dest_hex = (new_hx, new_hy)
				
				# calculate animation locations
				(x1, y1) = self.PlotHex(unit.hx, unit.hy)
				(x2, y2) = self.PlotHex(new_hx, new_hy)
				unit.animation_cells = GetLine(x1, y1, x2, y2)
				# special case: unit is jumping over 0,0
				if jump:
					for i in range(12, 0, -2):
						unit.animation_cells.pop(i)
			
			# animate movement
			for i in range(6):
				for unit in self.units:
					if unit == self.player_unit: continue
					if unit in self.player_unit.squad: continue
					if len(unit.animation_cells) > 0:
						unit.animation_cells.pop(0)
				self.UpdateUnitCon()
				self.UpdateScenarioDisplay()
				Wait(15)
			
			# set new hex location for each moving unit and move into new hex stack
			for unit in self.units:
				if unit.dest_hex is None: continue
				self.hex_dict[(unit.hx, unit.hy)].unit_stack.remove(unit)
				(unit.hx, unit.hy) = unit.dest_hex
				self.hex_dict[(unit.hx, unit.hy)].unit_stack.append(unit)
				# clear destination hex and animation data
				unit.dest_hex = None
				unit.animation_cells = []
		
		# set new terrain for player and squad
		for unit in self.units:
			if unit != self.player_unit and unit not in self.player_unit.squad: continue
			unit.GenerateTerrain()
			unit.CheckForHD()
			unit.SetSmokeLevel()
		
		self.UpdatePlayerInfoCon()
		self.UpdateUnitCon()
		
		# recalculate move chances and do bog check in new location
		# FUTURE: check AI units too
		for unit in self.units:
			if unit != self.player_unit: continue
			unit.CalculateMoveChances()
			unit.DoBogCheck(forward, reposition=reposition)
		
		# notify player and update consoles if player bogged
		if self.player_unit.bogged:
			ShowMessage('Your tank has becomed bogged.')
			self.UpdatePlayerInfoCon()
			self.UpdateUnitCon()
		
		if reposition: return
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
			if unit == self.player_unit: continue
			if unit in self.player_unit.squad: continue
			
			(new_hx, new_hy) = RotateHex(unit.hx, unit.hy, r)
			# set destination hex
			unit.dest_hex = (new_hx, new_hy)
		
		# FUTURE: animate movement?
		
		# set new hex location for each unit and move into new hex stack
		for unit in self.units:
			if unit == self.player_unit: continue
			if unit in self.player_unit.squad: continue
			self.hex_dict[(unit.hx, unit.hy)].unit_stack.remove(unit)
			(unit.hx, unit.hy) = unit.dest_hex
			self.hex_dict[(unit.hx, unit.hy)].unit_stack.append(unit)
			# clear destination hex
			unit.dest_hex = None
			
			# pivot unit facings if any
			if unit.facing is not None:
				unit.facing = ConstrainDir(unit.facing + f)
			if unit.turret_facing is not None:
				unit.turret_facing = ConstrainDir(unit.turret_facing + f)
			
			# pivot unit HD if any
			if len(unit.hull_down) > 0:
				for i in range(3):
					unit.hull_down[i] = ConstrainDir(unit.hull_down[i] + f)
			
			# pivot unit smoke levels
			if clockwise:
				unit.smoke.append(unit.smoke.pop(0))
			else:
				unit.smoke.insert(0, unit.smoke.pop(5))
		
		self.UpdatePlayerInfoCon()
		self.UpdateGuiCon()
		self.UpdateUnitCon()
		
		# pivot player HD if any
		if len(self.player_unit.hull_down) > 0:
			for i in range(3):
				self.player_unit.hull_down[i] = ConstrainDir(self.player_unit.hull_down[i] + f)
		
		# record player pivot
		self.player_pivot = ConstrainDir(self.player_pivot + f)
		
	# rotate turret of player unit
	def RotatePlayerTurret(self, clockwise):
		
		# no turret on vehicle
		if scenario.player_unit.turret_facing is None: return
		
		if clockwise:
			f = 1
		else:
			f = -1
		scenario.player_unit.turret_facing = ConstrainDir(scenario.player_unit.turret_facing + f)
		
		# update covered hexes for any turret-mounted weapons
		for weapon in scenario.player_unit.weapon_list:
			if weapon.GetStat('mount') != 'Turret': continue
			weapon.UpdateCoveredHexes()
		
		self.UpdateUnitCon()
		self.UpdateGuiCon()
	
	
	# display a pop-up window with info on a particular unit
	def ShowUnitInfoWindow(self, unit):
		
		# create a local copy of the current screen to re-draw when we're done
		temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
		libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
		# darken screen background
		libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
		
		# create window and draw frame
		window_con = libtcod.console_new(27, 26)
		libtcod.console_set_default_background(window_con, libtcod.black)
		libtcod.console_set_default_foreground(window_con, libtcod.white)
		DrawFrame(window_con, 0, 0, 27, 26)
		
		# draw unit info and command instructions
		unit.DisplayMyInfo(window_con, 1, 1)
		libtcod.console_set_default_foreground(window_con, ACTION_KEY_COL)
		libtcod.console_print(window_con, 7, 24, 'ESC')
		libtcod.console_set_default_foreground(window_con, libtcod.lighter_grey)
		libtcod.console_print(window_con, 12, 24, 'Return')
		
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
	
	
	# advance to next phase/turn and do automatic events
	def AdvanceToNextPhase(self):
		
		# do end of phase actions for player
		
		# end of player turn, switching to enemy turn
		if self.phase == PHASE_ALLIED_ACTION:
			
			# resolve fp on enemy units first
			for unit in reversed(self.units):
				if not unit.alive: continue
				if unit.owning_player == self.active_player: continue
				unit.ResolveFP()
				libtcod.console_flush()
			
			self.phase = PHASE_ENEMY_ACTION
			self.active_player = 1
		
		# end of enemy activation, player's turn
		elif self.phase == PHASE_ENEMY_ACTION:
		
			# resolve fp on player units first
			for unit in reversed(self.units):
				if not unit.alive: continue
				if unit.owning_player == self.active_player: continue
				unit.ResolveFP()
				libtcod.console_flush()
			
			# advance clock
			campaign_day.AdvanceClock(0, TURN_LENGTH)
			
			# check for end of scenario
			self.CheckForEnd()
			if self.finished: return
			
			# check for random event
			self.CheckForRandomEvent()
			
			self.active_player = 0
			self.phase = PHASE_COMMAND
			
			self.player_unit.ResetForNewTurn()
			for unit in scenario.player_unit.squad:
				unit.ResetForNewTurn()
			
			self.player_unit.MoveToTopOfStack()
		
		# still player turn, advance phase
		else:
			
			# end of movement phase
			if self.phase == PHASE_MOVEMENT:
				
				# player pivoted during movement phase
				if self.player_pivot != 0:
					self.player_unit.ClearAcquiredTargets(no_enemy=True)
					
					# do bog check for pivot
					if not self.player_unit.bogged:
						self.player_unit.DoBogCheck(False, pivot=True)
						if self.player_unit.bogged:
							ShowMessage('Your tank has becomed bogged.')
							self.UpdatePlayerInfoCon()
							self.UpdateUnitCon()
			
			# end of shooting phase
			elif self.phase == PHASE_SHOOTING:
				
				# clear GUI console and refresh screen
				libtcod.console_clear(gui_con)
				self.UpdateScenarioDisplay()
				libtcod.console_flush()
				
				# resolve AP hits on enemy units
				for unit in reversed(self.units):
					if not unit.alive: continue
					if unit.owning_player == self.active_player: continue
					unit.ResolveAPHits()
			
			self.phase += 1
		
		# update the displays
		DisplayTimeInfo(time_con)
		self.UpdateUnitCon()
		self.UpdateScenarioDisplay()
		libtcod.console_flush()
		
		# do automatic actions at start of phase
		
		# command phase: rebuild lists of commands
		if self.phase == PHASE_COMMAND:
			self.player_unit.BuildCmdLists()
		
		# spotting phase: do spotting then automatically advance
		elif self.phase == PHASE_SPOTTING:
			
			self.player_unit.DoSpotChecks()
			self.advance_phase = True
		
		# crew action phase:
		elif self.phase == PHASE_CREW_ACTION:
			
			input_command = False
			
			for position in self.player_unit.positions_list:
				if position.crewman is None: continue
				
				# check for abandoning tank
				if position.crewman.current_cmd == 'Abandon Tank':
					campaign.player_unit.alive = False
					ShowMessage('You abandon your tank.')
					self.PlayerBailOut(skip_ko=True)
					campaign_day.ended = True
					campaign_day.abandoned_tank = True
					self.finished = True
					return
				
				# check for reposition
				if position.crewman.current_cmd == 'Reposition':
					self.MovePlayer(False, reposition=True)
					self.UpdateUnitCon()
					self.UpdateScenarioDisplay()
					libtcod.console_flush()
				
				# check for unbog attempt
				if position.crewman.current_cmd == 'Attempt Unbog':
					if self.player_unit.DoUnbogCheck():
						ShowMessage('Your tank is no longer bogged down.')
						self.UpdatePlayerInfoCon()
					else:
						ShowMessage('Your tank remains bogged down.')
					self.UpdateScenarioDisplay()
					libtcod.console_flush()
				
				# check for smoke grenade
				if position.crewman.current_cmd == 'Smoke Grenade':
					for i in range(6):
						self.player_unit.smoke[i] = 2
					PlaySoundFor(None, 'smoke')
					ShowMessage('You throw a smoke grenade.')
					self.UpdateUnitCon()
					self.UpdateScenarioDisplay()
					libtcod.console_flush()
				
				# check for smoke mortar
				if position.crewman.current_cmd == 'Fire Smoke Mortar':
					direction = self.player_unit.turret_facing
					if direction is None:
						direction = self.player_unit.facing
					self.player_unit.smoke[direction] = 2
					PlaySoundFor(None, 'smoke')
					ShowMessage('The ' + position.name + ' fires off a smoke mortar round.')
					self.UpdateUnitCon()
					self.UpdateScenarioDisplay()
					libtcod.console_flush()
				
				# check for action that needs input in this phase
				if position.crewman.current_cmd in ['Manage Ready Rack']:
					input_command = True
			
			if not input_command:
				self.advance_phase = True
		
		# movement phase: 
		elif self.phase == PHASE_MOVEMENT:
			
			self.player_pivot = 0
			
			# skip phase if driver not on move command
			crewman = scenario.player_unit.GetPersonnelByPosition('Driver')
			if crewman is None:
				self.advance_phase = True
			else:
				# driver not on Drive command
				if crewman.current_cmd != 'Drive':
					self.advance_phase = True
			
			# if we're doing the phase, calculate move chances for player unit
			if not self.advance_phase:
				scenario.player_unit.CalculateMoveChances()
		
		# shooting phase
		elif self.phase == PHASE_SHOOTING:
			
			# check that 1+ crew are on correct order
			skip_phase = True
			for position in self.player_unit.positions_list:
				if position.crewman is None: continue
				if position.crewman.current_cmd in ['Operate Gun', 'Operate MG']:
					skip_phase = False
					break
			
			if skip_phase:
				self.advance_phase = True
			else:
				self.BuildTargetList()
				self.UpdateGuiCon()
		
		# close combat phase
		elif self.phase == PHASE_CC:
			
			# FUTURE: add in events for this phase
			self.advance_phase = True
		
		# allied action
		elif self.phase == PHASE_ALLIED_ACTION:
			
			# player squad acts
			for unit in scenario.player_unit.squad:
				unit.MoveToTopOfStack()
				self.UpdateUnitCon()
				self.UpdateScenarioDisplay()
				libtcod.console_flush()
				unit.ai.DoActivation()
				
				# do recover roll for this unit
				unit.DoRecoveryRoll()
				
				# resolve any ap hits caused by this unit
				for unit2 in self.units:
					if not unit2.alive: continue
					if unit2.owning_player == self.active_player: continue
					unit2.ResolveAPHits()
				
				libtcod.console_flush()
			
			self.advance_phase = True
		
		# enemy action
		elif self.phase == PHASE_ENEMY_ACTION:
			
			DisplayTimeInfo(time_con)
			self.UpdateScenarioDisplay()
			libtcod.console_flush()
			
			# run through list in reverse since we might remove units from play
			for unit in reversed(self.units):
				
				# if player has been destroyed, don't keep attacking
				if not self.player_unit.alive:
					break
				
				if unit.owning_player == 0: continue
				if not unit.alive: continue
				unit.ResetForNewTurn()
				unit.CalculateMoveChances()
				unit.ai.DoActivation()
				
				# resolve any ap hits caused by this unit
				for unit2 in self.units:
					if not unit2.alive: continue
					if unit2.owning_player == self.active_player: continue
					unit2.ResolveAPHits()
				
				libtcod.console_flush()
			
			self.advance_phase = True
		
		self.UpdateCrewInfoCon()
		self.UpdateUnitInfoCon()
		self.UpdateCmdCon()
		self.UpdateContextCon()
		self.UpdateGuiCon()
		self.UpdateScenarioDisplay()
		libtcod.console_flush()
			
	
	# update contextual info console
	# 18x12
	def UpdateContextCon(self):
		libtcod.console_clear(context_con)
		
		# if we're advancing to next phase automatically, don't display anything here
		if self.advance_phase: return
		
		# Command Phase: display info about current crew command
		if self.phase == PHASE_COMMAND:
			position = scenario.player_unit.positions_list[self.selected_position]
			libtcod.console_set_default_foreground(context_con, SCEN_PHASE_COL[self.phase])
			libtcod.console_print(context_con, 0, 0, position.crewman.current_cmd)
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			lines = wrap(session.crew_commands[position.crewman.current_cmd]['desc'], 18)
			y = 2
			for line in lines:
				libtcod.console_print(context_con, 0, y, line)
				y += 1
		
		# Movement Phase
		elif self.phase == PHASE_MOVEMENT:
			
			libtcod.console_set_default_foreground(context_con, libtcod.white)
			libtcod.console_print(context_con, 5, 0, 'Success')
			libtcod.console_print(context_con, 14, 0, 'Bog')
			
			libtcod.console_print(context_con, 0, 2, 'Fwd')
			libtcod.console_print(context_con, 0, 4, 'Rev')
			libtcod.console_print(context_con, 0, 6, 'Pivot')
			#libtcod.console_print(context_con, 0, 8, 'Repo')
			#libtcod.console_print(context_con, 0, 10, 'HD')
			
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			
			# forward move
			text = str(scenario.player_unit.forward_move_chance) + '%%'
			libtcod.console_print_ex(context_con, 10, 2, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			text = str(scenario.player_unit.bog_chance) + '%%'
			libtcod.console_print_ex(context_con, 16, 2, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			
			# reverse move
			text = str(scenario.player_unit.reverse_move_chance) + '%%'
			libtcod.console_print_ex(context_con, 10, 4, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			text = str(round(scenario.player_unit.bog_chance * 1.5, 1)) + '%%'
			libtcod.console_print_ex(context_con, 16, 4, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			
			# pivot
			libtcod.console_print_ex(context_con, 10, 6, libtcod.BKGND_NONE,
				libtcod.RIGHT, '100%%')
			text = str(round(scenario.player_unit.bog_chance * 0.25, 1)) + '%%'
			libtcod.console_print_ex(context_con, 16, 6, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			
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
		
		elif self.phase == PHASE_CREW_ACTION:
			position = scenario.player_unit.positions_list[self.selected_position]
			if position.crewman is None: return
			
			if position.crewman.current_cmd == 'Manage Ready Rack':
				weapon = self.selected_weapon
				if weapon is None: return
				
				weapon.DisplayAmmo(context_con, 0, 1)
			
		# Shooting Phase
		elif self.phase == PHASE_SHOOTING:
			
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
			
			# display target and acquired target status if any
			if weapon.selected_target is not None and weapon.acquired_target is not None:
				(ac_target, level) = weapon.acquired_target
				if ac_target == weapon.selected_target:
					text = 'Acquired Target'
					if level == 1:
						text += '+'
					libtcod.console_set_default_foreground(context_con, libtcod.light_blue)
					libtcod.console_print(context_con, 0, 8, text)
					libtcod.console_set_default_foreground(context_con, libtcod.red)
			
			# if weapon is a gun, display ammo info here
			if weapon.GetStat('type') == 'Gun':
				weapon.DisplayAmmo(context_con, 0, 1)
				
			if weapon.fired:
				libtcod.console_set_default_foreground(context_con, libtcod.red)
				libtcod.console_print(context_con, 0, 7, 'Fired')
				return
			
			# display RoF chance if any
			libtcod.console_set_default_foreground(context_con, libtcod.white)
			libtcod.console_print_ex(context_con, 17, 1, libtcod.BKGND_NONE,
				libtcod.RIGHT, 'RoF')
			
			libtcod.console_set_default_foreground(context_con, libtcod.light_grey)
			chance = weapon.GetRoFChance()
			if chance > 0.0:
				text = str(chance) + '%%'
			else:
				text = 'N/A'
			libtcod.console_print_ex(context_con, 17, 2, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			
			# display info about current target if any
			if weapon.selected_target is not None:
				
				result = self.CheckAttack(scenario.player_unit, weapon, weapon.selected_target)
				
				# attack is fine
				if result == '':
					libtcod.console_set_default_foreground(context_con, libtcod.light_blue)
					libtcod.console_print(context_con, 0, 9, 'Ready to fire!')
				# attack is not fine
				else:
					lines = wrap(result, 18)
					y = 9
					libtcod.console_set_default_foreground(context_con, libtcod.red)
					for line in lines:
						libtcod.console_print(context_con, 0, y, line)
						y += 1
						if y == 12: break
				
	
	
	# update player unit info console
	def UpdatePlayerInfoCon(self):
		libtcod.console_clear(player_info_con)
		scenario.player_unit.DisplayMyInfo(player_info_con, 0, 0)
	
	
	# update the player crew info console
	def UpdateCrewInfoCon(self):
		libtcod.console_clear(crew_con)
		
		y = 0
		i = 0
		
		for position in scenario.player_unit.positions_list:
			
			# highlight position if selected and in command phase
			if i == scenario.selected_position and scenario.phase in [PHASE_COMMAND, PHASE_CREW_ACTION]:
				libtcod.console_set_default_background(crew_con, libtcod.darker_blue)
				libtcod.console_rect(crew_con, 0, y, 25, 3, True, libtcod.BKGND_SET)
				libtcod.console_set_default_background(crew_con, libtcod.black)
			
			# display position name and location in vehicle (eg. turret/hull)
			libtcod.console_set_default_foreground(crew_con, libtcod.light_blue)
			libtcod.console_print(crew_con, 0, y, position.name)
			libtcod.console_set_default_foreground(crew_con, libtcod.white)
			libtcod.console_print_ex(crew_con, 0+24, y, libtcod.BKGND_NONE, 
				libtcod.RIGHT, position.location)
			
			# display name of crewman and buttoned up / exposed status if any
			if position.crewman is None:
				libtcod.console_print(crew_con, 0, y+1, 'Empty')
			else:
				
				# use nickname if any
				if position.crewman.nickname != '':
					libtcod.console_print(crew_con, 0, y+1, '"' + position.crewman.nickname + '"')
				else:
					position.crewman.DisplayName(crew_con, 0, y+1, first_initial=True)
				
				# display wound status if any
				if position.crewman.wound != '':
					libtcod.console_put_char_ex(crew_con, 21, y+1, position.crewman.wound[0], libtcod.black, libtcod.red)
				
				if not position.hatch:
					text = '--'
				elif position.crewman.ce:
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
				if position.crewman.status != '':
					if position.crewman.status == 'Dead':
						libtcod.console_set_default_foreground(crew_con, libtcod.dark_grey)
					elif position.crewman.status == 'Unconscious':
						libtcod.console_set_default_foreground(crew_con, libtcod.grey)
					elif position.crewman.status == 'Stunned':
						libtcod.console_set_default_foreground(crew_con, libtcod.light_grey)
					libtcod.console_print_ex(crew_con, 24, y+2, libtcod.BKGND_NONE, libtcod.RIGHT, 
						position.crewman.status)
			
			libtcod.console_set_default_foreground(crew_con, libtcod.darker_grey)
			for x in range(25):
				libtcod.console_print(crew_con, x, y+3, '-')
			
			libtcod.console_set_default_foreground(crew_con, libtcod.white)
			y += 4
			i += 1
	
	
	# update player command console 25x12
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
		if self.phase == PHASE_COMMAND:
			libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
			libtcod.console_print(cmd_menu_con, 1, 1, EnKey('w').upper() + '/' + EnKey('s').upper())
			libtcod.console_print(cmd_menu_con, 1, 2, EnKey('a').upper() + '/' + EnKey('d').upper())
			libtcod.console_print(cmd_menu_con, 1, 3, 'H')
			libtcod.console_print(cmd_menu_con, 1, 4, EnKey('f').upper())
			
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 1, 'Select Position')
			libtcod.console_print(cmd_menu_con, 8, 2, 'Select Command')
			libtcod.console_print(cmd_menu_con, 8, 3, 'Open/Shut Hatch')
			libtcod.console_print(cmd_menu_con, 8, 4, 'Crewman Menu')
		
		# Crew action phase
		elif self.phase == PHASE_CREW_ACTION:
			libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
			libtcod.console_print(cmd_menu_con, 1, 9, EnKey('w').upper() + '/' + EnKey('s').upper())
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 9, 'Select Position')
			
			# crew command specific actions
			if self.selected_position is None: return
			position = self.player_unit.positions_list[self.selected_position]
			if position.crewman is None: return
			
			if position.crewman.current_cmd == 'Manage Ready Rack':
				
				libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
				libtcod.console_print(cmd_menu_con, 1, 1, EnKey('d').upper() + '/' + EnKey('a').upper())
				libtcod.console_print(cmd_menu_con, 1, 2, EnKey('c').upper())
				
				libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
				libtcod.console_print(cmd_menu_con, 8, 1, 'Add/Remove Shell')
				libtcod.console_print(cmd_menu_con, 8, 2, 'Cycle Ammo Type')
		
			
		# Movement phase
		elif self.phase == PHASE_MOVEMENT:
			libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
			libtcod.console_print(cmd_menu_con, 1, 1, EnKey('w').upper() + '/' + EnKey('s').upper())
			libtcod.console_print(cmd_menu_con, 1, 2, EnKey('a').upper() + '/' + EnKey('d').upper())
			libtcod.console_print(cmd_menu_con, 1, 3, 'H')
			#libtcod.console_print(cmd_menu_con, 1, 4, EnKey('r').upper())
			
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 1, 'Forward/Reverse')
			libtcod.console_print(cmd_menu_con, 8, 2, 'Pivot Hull')
			libtcod.console_print(cmd_menu_con, 8, 3, 'Attempt HD')
			#libtcod.console_print(cmd_menu_con, 8, 4, 'Reposition')
			
		
		# Shooting phase
		elif self.phase == PHASE_SHOOTING:
			libtcod.console_set_default_foreground(cmd_menu_con, ACTION_KEY_COL)
			libtcod.console_print(cmd_menu_con, 1, 1, EnKey('w').upper() + '/' + EnKey('s').upper())
			libtcod.console_print(cmd_menu_con, 1, 2, EnKey('a').upper() + '/' + EnKey('d').upper())
			libtcod.console_print(cmd_menu_con, 1, 3, EnKey('q').upper() + '/' + EnKey('e').upper())
			libtcod.console_print(cmd_menu_con, 1, 4, EnKey('c').upper())
			libtcod.console_print(cmd_menu_con, 1, 5, EnKey('r').upper())
			libtcod.console_print(cmd_menu_con, 1, 6, EnKey('f').upper())
			
			libtcod.console_set_default_foreground(cmd_menu_con, libtcod.light_grey)
			libtcod.console_print(cmd_menu_con, 8, 1, 'Select Weapon')
			libtcod.console_print(cmd_menu_con, 8, 2, 'Select Target')
			libtcod.console_print(cmd_menu_con, 8, 3, 'Rotate Turret')
			libtcod.console_print(cmd_menu_con, 8, 4, 'Cycle Ammo Type')
			libtcod.console_print(cmd_menu_con, 8, 5, 'Toggle RR Use')
			libtcod.console_print(cmd_menu_con, 8, 6, 'Fire at Target')

	
	# plot the center of a given in-game hex on the scenario hex map console
	# 0,0 appears in centre of console
	def PlotHex(self, hx, hy):
		x = (hx*7) + 26
		y = (hy*6) + (hx*3) + 21
		return (x,y)
	
	
	# build a dictionary of console locations and their corresponding map hexes
	# only called once when Scenario is created
	def BuildHexmapDict(self):
		for map_hex in self.map_hexes:
			# stop when outer hex ring is reached
			if GetHexDistance(0, 0, map_hex.hx, map_hex.hy) > 3: return
			(x,y) = self.PlotHex(map_hex.hx, map_hex.hy)
			
			# record console positions to dictionary
			for x1 in range(x-2, x+3):
				self.hex_map_index[(x1, y-2)] = map_hex
				self.hex_map_index[(x1, y+2)] = map_hex
			for x1 in range(x-3, x+4):
				self.hex_map_index[(x1, y-1)] = map_hex
				self.hex_map_index[(x1, y+1)] = map_hex
			for x1 in range(x-4, x+5):
				self.hex_map_index[(x1, y)] = map_hex
	
	
	# update hexmap console 53x43
	def UpdateHexmapCon(self):
		
		libtcod.console_clear(hexmap_con)
		
		# select base hex console image to use
		if campaign_day.weather['Ground'] in ['Snow', 'Heavy Snow']:
			scen_hex = LoadXP('scen_hex_snow.xp')
		else:
			scen_hex = LoadXP('scen_hex.xp')
		libtcod.console_set_key_color(scen_hex, KEY_COLOR)
		
		# draw hexes to hex map console
		for map_hex in self.map_hexes:
			if GetHexDistance(0, 0, map_hex.hx, map_hex.hy) > 3: break
			(x,y) = self.PlotHex(map_hex.hx, map_hex.hy)
			libtcod.console_blit(scen_hex, 0, 0, 0, 0, hexmap_con, x-5, y-3)
			
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
		if self.phase == PHASE_COMMAND:
			
			position = scenario.player_unit.positions_list[scenario.selected_position]
			for (hx, hy) in position.visible_hexes:
				(x,y) = scenario.PlotHex(hx, hy)
				libtcod.console_blit(session.scen_hex_fov, 0, 0, 0, 0, gui_con,
					x-5, y-3)
		
		# crew action phase
		elif self.phase == PHASE_CREW_ACTION:
			
			pass
			
		
		# shooting phase
		elif self.phase == PHASE_SHOOTING:
			
			# display covered hexes if a weapon is selected
			if self.selected_weapon is not None:
				for (hx, hy) in self.selected_weapon.covered_hexes:
					(x,y) = scenario.PlotHex(hx, hy)
					libtcod.console_blit(session.scen_hex_fov, 0, 0, 0, 0, gui_con,
						x-5, y-3)
			
				# display target recticle if a weapon target is selected
				if self.selected_weapon.selected_target is not None:
					(x,y) = self.PlotHex(self.selected_weapon.selected_target.hx, self.selected_weapon.selected_target.hy)
					
					libtcod.console_put_char_ex(gui_con, x-1, y-1, 218, libtcod.red, libtcod.black)
					libtcod.console_put_char_ex(gui_con, x+1, y-1, 191, libtcod.red, libtcod.black)
					libtcod.console_put_char_ex(gui_con, x-1, y+1, 192, libtcod.red, libtcod.black)
					libtcod.console_put_char_ex(gui_con, x+1, y+1, 217, libtcod.red, libtcod.black)
	
	
	# update the scenario info console, on the top right of the screen
	# displays current weather and terrain type
	# 14x12
	def UpdateScenarioInfoCon(self):
		libtcod.console_clear(scen_info_con)
		DisplayWeatherInfo(scen_info_con)
	
		
	# update unit info console, which displays basic information about a unit under
	# the mouse cursor
	# 61x5
	def UpdateUnitInfoCon(self):
		libtcod.console_clear(unit_info_con)
		
		# check that cursor is in map area and on a map hex
		x = mouse.cx - 32
		y = mouse.cy - 9
		if (x,y) not in self.hex_map_index:
			libtcod.console_set_default_foreground(unit_info_con, libtcod.dark_grey)
			libtcod.console_print(unit_info_con, 18, 2, 'Mouseover a hex for details')
			return
		
		map_hex = self.hex_map_index[(x,y)]
	
		# range from player
		distance = GetHexDistance(0, 0, map_hex.hx, map_hex.hy)
		if distance == 0:
			text = '0-120m.'
		elif distance == 1:
			text = '120-480m.'
		elif distance == 2:
			text = '480-960m.'
		else:
			text = '960-1440m.'
		libtcod.console_set_default_foreground(unit_info_con, libtcod.light_grey)
		libtcod.console_print_ex(unit_info_con, 60, 0, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'Range: ' + text)
	
		# no units in hex
		if len(map_hex.unit_stack) == 0: return
		
		# display unit info
		unit = map_hex.unit_stack[0]
		
		if unit.owning_player == 1 and not unit.spotted:
			libtcod.console_set_default_foreground(unit_info_con, UNKNOWN_UNIT_COL)
			libtcod.console_print(unit_info_con, 0, 0, 'Unspotted Enemy')
		else:
			if unit == scenario.player_unit:
				col = libtcod.white
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
			
			# second column
			
			# facing if any
			if unit.facing is not None and unit.GetStat('category') != 'Infantry':
				libtcod.console_put_char_ex(unit_info_con, 23, 0, 'H',
					libtcod.light_grey, libtcod.darkest_grey)
				libtcod.console_put_char_ex(unit_info_con, 24, 0,
					GetDirectionalArrow(unit.facing), libtcod.light_grey,
					libtcod.darkest_grey)
			
			# HD status if any
			if len(unit.hull_down) > 0:
				libtcod.console_set_default_foreground(unit_info_con, libtcod.sepia)
				libtcod.console_print(unit_info_con, 26, 0, 'HD')
				libtcod.console_put_char_ex(unit_info_con, 28, 0,
					GetDirectionalArrow(unit.hull_down[0]), libtcod.sepia,
					libtcod.darkest_grey)
			
			# current terrain
			if unit.terrain is not None:
				libtcod.console_set_default_foreground(unit_info_con, libtcod.dark_green)
				libtcod.console_print(unit_info_con, 23, 1, unit.terrain)
			
			libtcod.console_set_default_foreground(unit_info_con, libtcod.dark_grey)
			libtcod.console_print(unit_info_con, 20, 3, 'Right click for details')
			libtcod.console_print(unit_info_con, 14, 4, 'Mousewheel to cycle units in stack')
	
	
	# starts or re-starts looping animations based on weather conditions
	def InitAnimations(self):
		
		# reset animations
		self.animation['rain_active'] = False
		self.animation['rain_drops'] = []
		self.animation['snow_active'] = False
		self.animation['snowflakes'] = []
		
		# check for rain animation
		if campaign_day.weather['Precipitation'] in ['Rain', 'Heavy Rain']:
			self.animation['rain_active'] = True
		elif campaign_day.weather['Precipitation'] in ['Light Snow', 'Snow', 'Blizzard']:
			self.animation['snow_active'] = True
		
		# set up rain if any
		if self.animation['rain_active']:
			self.animation['rain_drops'] = []
			num = 4
			if campaign_day.weather['Precipitation'] == 'Heavy Rain':
				num = 8
			for i in range(num):
				x = libtcod.random_get_int(0, 4, 50)
				y = libtcod.random_get_int(0, 0, 38)
				lifespan = libtcod.random_get_int(0, 1, 5)
				self.animation['rain_drops'].append((x, y, 4))
		
		# set up snow if any
		if self.animation['snow_active']:
			self.animation['snowflakes'] = []
			if campaign_day.weather['Precipitation'] == 'Light Snow':
				num = 4
			elif campaign_day.weather['Precipitation'] == 'Snow':
				num = 8
			else:
				num = 16
			for i in range(num):
				x = libtcod.random_get_int(0, 4, 50)
				y = libtcod.random_get_int(0, 0, 37)
				lifespan = libtcod.random_get_int(0, 4, 10)
				self.animation['snowflakes'].append((x, y, lifespan))
	
	
	# update the scenario animation frame and console 53x43
	def UpdateAnimCon(self):
		
		libtcod.console_clear(anim_con)
		
		# update rain display
		if self.animation['rain_active']:
			
			# update location of each rain drop, spawn new ones if required
			for i in range(len(self.animation['rain_drops'])):
				(x, y, lifespan) = self.animation['rain_drops'][i]
				
				# respawn if finished
				if lifespan == 0:
					x = libtcod.random_get_int(0, 4, 50)
					y = libtcod.random_get_int(0, 0, 37)
					lifespan = libtcod.random_get_int(0, 1, 5)
				else:
					y += 2
					lifespan -= 1
				
				self.animation['rain_drops'][i] = (x, y, lifespan)
			
			# draw drops to screen
			for (x, y, lifespan) in self.animation['rain_drops']:
				
				# skip if off screen
				if x < 0 or y > 50: continue
				
				if lifespan == 0:
					char = 111
				else:
					char = 124
				libtcod.console_put_char_ex(anim_con, x, y, char, libtcod.light_blue,
					libtcod.black)
		
		# update snow display
		if self.animation['snow_active']:
			
			# update location of each snowflake
			for i in range(len(self.animation['snowflakes'])):
				(x, y, lifespan) = self.animation['snowflakes'][i]
				
				# respawn if finished
				if lifespan == 0:
					x = libtcod.random_get_int(0, 4, 50)
					y = libtcod.random_get_int(0, 0, 37)
					lifespan = libtcod.random_get_int(0, 4, 10)
				else:
					x += choice([-1, 0, 1])
					y += 1
					lifespan -= 1
				
				self.animation['snowflakes'][i] = (x, y, lifespan)
			
			# draw snowflakes to screen
			for (x, y, lifespan) in self.animation['snowflakes']:
				
				# skip if off screen
				if x < 0 or y > 50: continue
				
				libtcod.console_put_char_ex(anim_con, x, y, 249, libtcod.white,
					libtcod.black)
		
		
		# update airplane animation if any
		if self.animation['air_attack'] is not None:
			
			# update draw location
			self.animation['air_attack_line'].pop(0)
			
			# clear if finished
			if len(self.animation['air_attack_line']) == 0:
				self.animation['air_attack'] = None
			else:
				(x,y) = self.animation['air_attack_line'][0]
				libtcod.console_blit(self.animation['air_attack'], 0, 0, 0, 0, anim_con, x-1, y)
		
		# update gun fire animation if any
		if self.animation['gun_fire_active']:
			
			self.animation['gun_fire_line'].pop(0)
			if len(self.animation['gun_fire_line']) > 0:
				self.animation['gun_fire_line'].pop(0)
			
			# clear if finished
			if len(self.animation['gun_fire_line']) == 0:
				self.animation['gun_fire_active'] = False
			else:
				(x,y) = self.animation['gun_fire_line'][0]
				libtcod.console_put_char_ex(anim_con, x, y, 250, libtcod.white,
					libtcod.black)
		
		# update small arms fire if any
		if self.animation['small_arms_fire_action']:
			
			if self.animation['small_arms_lifetime'] == 0:
				self.animation['small_arms_fire_action'] = None
			else:
				self.animation['small_arms_lifetime'] -= 1
				(x,y) = choice(self.animation['small_arms_fire_line'][1:])
				libtcod.console_put_char_ex(anim_con, x, y, 250, libtcod.yellow,
					libtcod.black)
		
		# update bomb/explosion animation if any
		if self.animation['bomb_effect'] is not None:
			
			if self.animation['bomb_effect_lifetime'] == 0:
				self.animation['bomb_effect'] = None
			else:
				self.animation['bomb_effect_lifetime'] -= 1
				(x,y) = self.animation['bomb_effect']
				if 3 & self.animation['bomb_effect_lifetime'] == 0:
					col = libtcod.red
				elif 2 & self.animation['bomb_effect_lifetime'] == 0:
					col = libtcod.yellow
				else:
					col = libtcod.black
				
				libtcod.console_put_char_ex(anim_con, x, y, 42, col,
					libtcod.black)
		
		# reset update timer
		session.anim_timer = time.time()
		
	
	# draw all scenario consoles to the screen
	def UpdateScenarioDisplay(self):
		libtcod.console_clear(con)
		
		# left column
		if self.attack_con_active:
			libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
		else:
			libtcod.console_blit(bkg_console, 0, 0, 0, 0, con, 0, 0)
			libtcod.console_blit(player_info_con, 0, 0, 0, 0, con, 1, 1)
			libtcod.console_blit(crew_con, 0, 0, 0, 0, con, 1, 21)
			libtcod.console_blit(cmd_menu_con, 0, 0, 0, 0, con, 1, 47)
		
		# main map display
		libtcod.console_blit(hexmap_con, 0, 0, 0, 0, con, 32, 9)
		libtcod.console_blit(unit_con, 0, 0, 0, 0, con, 32, 9, 1.0, 0.0)
		libtcod.console_blit(gui_con, 0, 0, 0, 0, con, 32, 9, 1.0, 0.0)
		libtcod.console_blit(anim_con, 0, 0, 0, 0, con, 32, 9, 1.0, 0.0)
		
		# consoles around the edge of map
		libtcod.console_blit(context_con, 0, 0, 0, 0, con, 28, 1)
		libtcod.console_blit(time_con, 0, 0, 0, 0, con, 48, 1)
		libtcod.console_blit(scen_info_con, 0, 0, 0, 0, con, 75, 1)
		libtcod.console_blit(unit_info_con, 0, 0, 0, 0, con, 28, 54)
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	
	# main input loop for scenarios
	def DoScenarioLoop(self):
		
		# set up and load scenario consoles
		global bkg_console, crew_con, cmd_menu_con, scen_info_con
		global player_info_con, context_con, time_con, hexmap_con, unit_con, gui_con
		global anim_con, attack_con, unit_info_con
		
		# background outline console for left column
		bkg_console = LoadXP('bkg.xp')
		
		player_info_con = NewConsole(25, 18, libtcod.black, libtcod.white)
		crew_con = NewConsole(25, 24, libtcod.black, libtcod.white)
		cmd_menu_con = NewConsole(25, 12, libtcod.black, libtcod.white)
		context_con = NewConsole(18, 12, libtcod.darkest_grey, libtcod.white)
		time_con = NewConsole(21, 6, libtcod.darkest_grey, libtcod.white)
		scen_info_con = NewConsole(14, 11, libtcod.darkest_grey, libtcod.white)
		unit_info_con = NewConsole(61, 5, libtcod.darkest_grey, libtcod.white)
		hexmap_con = NewConsole(53, 43, libtcod.black, libtcod.black)
		unit_con = NewConsole(53, 43, KEY_COLOR, libtcod.white, key_colour=True)
		gui_con = NewConsole(53, 43, KEY_COLOR, libtcod.white, key_colour=True)
		anim_con = NewConsole(53, 43, KEY_COLOR, libtcod.white, key_colour=True)
		attack_con = NewConsole(27, 60, libtcod.black, libtcod.white)
		
		# we're starting a new scenario
		if not self.init_complete:
		
			# set up player unit
			self.player_unit = campaign.player_unit
			self.player_unit.facing = 0
			self.player_unit.turret_facing = 0
			self.player_unit.squad = []
			self.player_unit.SpawnAt(0,0)
			self.player_unit.spotted = True
			
			# reset player crewman actions
			for position in self.player_unit.positions_list:
				if position.crewman is None: continue
				position.crewman.current_cmd = 'Spot'
			
			# spawn rest of player squad
			for i in range(campaign.player_squad_num):
				unit = Unit(self.player_unit.unit_id)
				unit.nation = self.player_unit.nation
				unit.ai = AI(unit)
				unit.GenerateNewPersonnel()
				unit.facing = 0
				unit.turret_facing = 0
				unit.spotted = True
				unit.SpawnAt(0,0)
				self.player_unit.squad.append(unit)
			
			# generate enemy units (also checks for pins from advancing fire)
			self.SpawnEnemyUnits()
			
			# set up player unit for first activation
			self.player_unit.BuildCmdLists()
			self.player_unit.ResetForNewTurn(skip_smoke=True)
			for unit in self.player_unit.squad:
				unit.BuildCmdLists()
				unit.ResetForNewTurn(skip_smoke=True)
			
			# roll for possible ambush if enemy-controlled
			if self.cd_map_hex.controlled_by == 1:
				self.DoAmbushRoll()
			
			# if player was ambushed, enemy units activate first
			if self.ambush:
				self.phase = PHASE_ALLIED_ACTION
				self.advance_phase = True
			
			self.init_complete = True
		
		# reset animation timer
		session.anim_timer = time.time()
		
		# init looping animations
		self.InitAnimations()
		
		SaveGame()
		
		# generate consoles and draw scenario screen for first time
		self.UpdateContextCon()
		DisplayTimeInfo(time_con)
		self.UpdateScenarioInfoCon()
		self.UpdatePlayerInfoCon()
		self.UpdateCrewInfoCon()
		self.UpdateCmdCon()
		self.UpdateUnitCon()
		self.UpdateGuiCon()
		self.UpdateAnimCon()
		self.UpdateHexmapCon()
		self.UpdateScenarioDisplay()
		
		# check for support request(s) and resolve if any
		if campaign_day.air_support_request or campaign_day.arty_support_request:
			self.ResolveSupportRequests()
		
		if self.ambush:
			ShowMessage('You have been ambushed by enemy forces!')
			# reset flag, no longer needed an prevent message from showing on load game
			self.ambush = False
		
		# record mouse cursor position to check when it has moved
		mouse_x = -1
		mouse_y = -1
		
		exit_scenario = False
		while not exit_scenario:
			
			# check for exiting game
			if session.exiting:
				return
			
			# check for scenario finished, return to campaign day map
			if self.finished:
				# copy the scenario unit over to the campaign version
				campaign.player_unit = self.player_unit
				return
			
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			
			# trigger advance to next phase
			if self.advance_phase:
				self.advance_phase = False
				self.AdvanceToNextPhase()
				SaveGame()
				continue
			
			# check for animation update
			if time.time() - session.anim_timer >= 0.20:
				self.UpdateAnimCon()
				self.UpdateScenarioDisplay()
			
			keypress = GetInputEvent()
			
			##### Mouse Commands #####
			
			# check to see if mouse cursor has moved
			if mouse.cx != mouse_x or mouse.cy != mouse_y:
				mouse_x = mouse.cx
				mouse_y = mouse.cy
				self.UpdateUnitInfoCon()
				self.UpdateScenarioDisplay()
			
			# mouse wheel has moved or right mouse button clicked
			if mouse.wheel_up or mouse.wheel_down or mouse.rbutton_pressed:
				
				# see if cursor is over a hex with 1+ units in it
				x = mouse.cx - 32
				y = mouse.cy - 9
				if (x,y) in self.hex_map_index:
					map_hex = self.hex_map_index[(x,y)]
					if len(map_hex.unit_stack) > 0:
						if mouse.rbutton_pressed:
							unit = map_hex.unit_stack[0]
							if not (unit.owning_player == 1 and not unit.spotted):
								self.ShowUnitInfoWindow(unit)
							continue
						elif len(map_hex.unit_stack) > 1:
						
							if mouse.wheel_up:
								map_hex.unit_stack[:] = map_hex.unit_stack[1:] + [map_hex.unit_stack[0]]
							elif mouse.wheel_down:
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
			
			# debug menu
			elif key.vk == libtcod.KEY_F2:
				if not DEBUG: continue
				ShowDebugMenu()
				continue
			
			# player not active
			if scenario.active_player == 1: continue
			
			# key commands
			key_char = DeKey(chr(key.c).lower())
			
			# Any Phase
			
			# advance to next phase
			if key.vk == libtcod.KEY_SPACE:
				self.advance_phase = True
				continue
			
			
			# Command Phase and Crew Action phase
			if self.phase in [PHASE_COMMAND, PHASE_CREW_ACTION]:
			
				# change selected crew position
				if key_char in ['w', 's']:
					
					if key_char == 'w':
						self.selected_position -= 1
						if self.selected_position < 0:
							self.selected_position = len(self.player_unit.positions_list) - 1
					
					else:
						self.selected_position += 1
						if self.selected_position == len(self.player_unit.positions_list):
							self.selected_position = 0
				
					self.UpdateContextCon()
					self.UpdateCrewInfoCon()
					self.UpdateCmdCon()
					self.UpdateGuiCon()
					self.UpdateScenarioDisplay()
					continue
			
			# command phase only
			if self.phase == PHASE_COMMAND:
			
				# change current command for selected crewman
				if key_char in ['a', 'd']:
					
					# no crewman in selected position
					crewman = self.player_unit.positions_list[self.selected_position].crewman
					if crewman is None:
						continue
					
					PlaySoundFor(None, 'command_select')
					
					crewman.SelectCommand(key_char == 'a')
					
					self.player_unit.positions_list[self.selected_position].UpdateVisibleHexes()
					
					self.UpdateContextCon()
					self.UpdateCrewInfoCon()
					self.UpdateGuiCon()
					self.UpdateScenarioDisplay()
					continue
				
				# toggle hatch for selected crewman (not mapped)
				elif chr(key.c).lower() == 'h':
					
					# no crewman in selected position
					crewman = self.player_unit.positions_list[self.selected_position].crewman
					if crewman is None: continue
					
					if crewman.ToggleHatch():
						PlaySoundFor(crewman, 'hatch')
						self.player_unit.positions_list[self.selected_position].UpdateVisibleHexes()
						self.UpdateCrewInfoCon()
						self.UpdateGuiCon()
						self.UpdateScenarioDisplay()
						continue
				
				# open crewman menu
				elif key_char == 'f':
					crewman = self.player_unit.positions_list[self.selected_position].crewman
					if crewman is None: continue
					crewman.ShowCrewmanMenu()
					self.UpdateScenarioDisplay()
					continue
			
			# crew action phase only
			elif self.phase == PHASE_CREW_ACTION:
				
				if self.selected_position is None: continue
				position = self.player_unit.positions_list[self.selected_position]
				if position.crewman is None: continue
				
				# ready rack commands
				if position.crewman.current_cmd == 'Manage Ready Rack':
					
					# cycle active ammo type
					if key_char == 'c':
						if scenario.selected_weapon.CycleAmmo():
							self.UpdateContextCon()
							self.UpdateScenarioDisplay()
						continue
					
					# try to move a shell into or out of Ready Rack
					if key_char in ['a', 'd']:
						
						if key_char == 'a':
							add_num = -1
						else:
							add_num = 1
						
						if scenario.selected_weapon.ManageRR(add_num):
							self.UpdateContextCon()
							self.UpdateScenarioDisplay()
						continue
					
			# Movement phase only
			elif scenario.phase == PHASE_MOVEMENT:
				
				# move forward/backward (also ends the phase)
				if key_char in ['w', 's']:
					self.MovePlayer(key_char == 'w')
					self.UpdateContextCon()
					self.UpdateUnitInfoCon()
					self.UpdateScenarioDisplay()
					continue
				
				# pivot hull
				elif key_char in ['a', 'd']:
					self.PivotPlayer(key_char == 'd')
					self.UpdatePlayerInfoCon()
					self.UpdateContextCon()
					self.UpdateUnitInfoCon()
					self.UpdateScenarioDisplay()
					continue
				
				# attempt HD (not keymapped)
				elif chr(key.c).lower() == 'h':
					
					# already in HD position
					if len(self.player_unit.hull_down) > 0:
						if self.player_unit.hull_down[0] == self.player_unit.facing:
							continue
					
					# set statuses and play sound
					self.player_unit.moving = True
					self.player_unit.ClearAcquiredTargets()
					PlaySoundFor(self.player_unit, 'movement')
					
					if self.player_unit.BreakdownCheck():
						ShowMessage('Your vehicle stalls, making you unable to move further.')
						self.advance_phase = True
						continue
					
					result = self.player_unit.CheckForHD(driver_attempt=True)
					if result:
						ShowMessage('You move into a Hull Down position')
					else:
						ShowMessage('You were unable to move into a Hull Down position')
					self.UpdatePlayerInfoCon()
					self.UpdateUnitInfoCon()
					self.UpdateScenarioDisplay()
					
					# end movement phase
					self.advance_phase = True
					continue
				
			# Shooting phase
			elif scenario.phase == PHASE_SHOOTING:
				
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
				
				# toggle read rack use
				elif key_char == 'r':
					scenario.selected_weapon.using_rr = not scenario.selected_weapon.using_rr
					self.UpdateContextCon()
					self.UpdateScenarioDisplay()
					continue
				
				# player fires active weapon at selected target
				elif key_char == 'f':
					result = scenario.player_unit.Attack(scenario.selected_weapon,
						scenario.selected_weapon.selected_target)
					if result:
						self.UpdateUnitInfoCon()
						self.UpdateContextCon()
						self.UpdateScenarioDisplay()
					continue



##########################################################################################
#                                  General Functions                                     #
##########################################################################################	

# return the amount of EXP required for a personel to be at a given level
def GetExpRequiredFor(level):
	exp = 0
	for l in range(1, level):
		exp += int(ceil(BASE_EXP_REQUIRED * (pow(float(l), EXP_EXPONENT))))
	return exp


# generate and return a console image of a plane
def GeneratePlaneCon(direction):
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
	return temp_con


# export the campaign log to a text file, normally done at the end of a campaign
def ExportLog():
	
	filename = 'ArmCom2_Campaign_Log_' + datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + '.txt'
	with open(filename, 'w') as f:
			
		# campaign information
		f.write(campaign.stats['name'] + '\n')
		f.write(campaign.stats['desc'] + '\n')
		f.write(GetDateText(campaign.stats['start_date']) + ' - ' + GetDateText(campaign.today) + '\n')
		f.write('\n')
		
		# final player tank and crew information
		f.write(campaign.player_unit.unit_id + '\n')
		f.write(campaign.player_unit.GetStat('class') + '\n')
		f.write('\n')
		
		for position in campaign.player_unit.positions_list:
			f.write(position.name + ':\n')
			if position.crewman is None:
				f.write('  [Empty]\n\n')
				continue
			f.write('  ' + position.crewman.first_name + ' ' + position.crewman.last_name + '\n')
			if position.crewman.wound != '':
				f.write('  ' + position.crewman.wound + '\n')
			f.write('\n')
		f.write('\n')
		
		# list of campaign day records
		for day, value in campaign.logs.items():
			f.write(GetDateText(day) + ':\n')
			for record in RECORD_LIST:
				f.write('  ' + record + ': ' + str(value[record]) + '\n')
			f.write('\n\n')


# show a menu for selecting a new crewman skill
def ShowSkillMenu(crewman):
	
	# build list of skills that can be added
	skill_list = []
	for k, value in campaign.skills.items():
		
		# crewman already has this skill
		if k in crewman.skills: continue
		
		# restricted to one or more positions
		if 'position_list' in value:
			if crewman.current_position.name not in value['position_list']: continue
		
		# crewman does not have prerequisite skill
		if 'prerequisite' in value:
			if value['prerequisite'] not in crewman.skills: continue
		
		# skill ok, add to list
		skill_list.append(k) 
	
	# no more skills can be added
	if len(skill_list) == 0:
		ShowMessage('No further skills available for this crewman.')
		return ''
	
	# create a local copy of the current screen to re-draw when we're done
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
	# darken background 
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.5)
	
	# create display console
	skill_menu_con = NewConsole(43, 36, libtcod.black, libtcod.white)
	
	selected_skill = 0
	result = ''
	exit_menu = False
	while not exit_menu:
		
		# update the display console
		libtcod.console_clear(skill_menu_con)
		libtcod.console_set_default_foreground(skill_menu_con, libtcod.grey)
		DrawFrame(skill_menu_con, 0, 0, 43, 36)
		
		libtcod.console_set_default_foreground(skill_menu_con, TITLE_COL)
		libtcod.console_print(skill_menu_con, 17, 1, 'Add Skill')
		
		# list of skills
		libtcod.console_set_default_foreground(skill_menu_con, libtcod.white)
		y = 4
		n = 0
		for skill_name in skill_list:
			libtcod.console_print(skill_menu_con, 2, y, skill_name)
			if n == selected_skill:
				
				# highlight selected skill
				libtcod.console_set_default_background(skill_menu_con, HIGHLIGHT_MENU_COL)
				libtcod.console_rect(skill_menu_con, 2, y, 20, 1, False, libtcod.BKGND_SET)
				libtcod.console_set_default_background(skill_menu_con, libtcod.black)
				
				# description of skill
				lines = wrap(campaign.skills[skill_name]['desc'], 19)
				y1 = 10
				libtcod.console_set_default_foreground(skill_menu_con, libtcod.light_grey)
				for line in lines:
					libtcod.console_print(skill_menu_con, 23, y1, line)
					y1 += 1
				libtcod.console_set_default_foreground(skill_menu_con, libtcod.white)
				
			y += 1
			n += 1
		
		# player commands
		libtcod.console_set_default_foreground(skill_menu_con, ACTION_KEY_COL)
		libtcod.console_print(skill_menu_con, 13, 32, EnKey('w').upper() + '/' + EnKey('s').upper())
		libtcod.console_print(skill_menu_con, 13, 33, EnKey('f').upper())
		libtcod.console_print(skill_menu_con, 13, 34, 'Esc')
		
		libtcod.console_set_default_foreground(skill_menu_con, libtcod.light_grey)
		libtcod.console_print(skill_menu_con, 20, 32, 'Select Skill')
		libtcod.console_print(skill_menu_con, 20, 33, 'Add Skill')
		libtcod.console_print(skill_menu_con, 20, 34, 'Cancel')
		
		libtcod.console_blit(skill_menu_con, 0, 0, 0, 0, 0, 24, 15)
		
		refresh_menu = False
		while not refresh_menu:
			
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			keypress = GetInputEvent()
			
			if not keypress: continue
			
			# exit menu
			if key.vk == libtcod.KEY_ESCAPE:
				exit_menu = True
				refresh_menu = True
				continue
			
			key_char = DeKey(chr(key.c).lower())
			
			# change selected skill
			if key_char in ['w', 's']:
				
				if key_char == 'w':
					if selected_skill == 0:
						selected_skill = len(skill_list) - 1
					else:
						selected_skill -= 1
				else:
					if selected_skill == len(skill_list) - 1:
						selected_skill = 0
					else:
						selected_skill += 1
				
				refresh_menu = True
				continue
			
			# add skill
			elif key_char == 'f':
				
				# make sure crewman has 1+ advance point to spend
				adv_pt = False
				if DEBUG:
					if session.debug['Free Crew Advances']:
						adv_pt = True
				if crewman.adv > 0:
					adv_pt = True
				
				if not adv_pt:
					ShowNotification('Crewman has no Advance Points remaining.')
					continue
				
				# get confirmation from player before adding skill
				if ShowNotification('Spend one advance point to gain the skill: ' + skill_list[selected_skill] + '?', confirm=True):
					result = skill_list[selected_skill]
					exit_menu = True
					refresh_menu = True
				continue
	
	# re-draw original screen
	libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
	del temp_con
	
	return result


# shortcut for generating consoles
def NewConsole(x, y, bg, fg, key_colour=False):
	new_con = libtcod.console_new(x, y)
	libtcod.console_set_default_background(new_con, bg)
	libtcod.console_set_default_foreground(new_con, fg)
	if key_colour:
		libtcod.console_set_key_color(new_con, KEY_COLOR)
	libtcod.console_clear(new_con)
	return new_con


# return a text description of a given calendar date
def GetDateText(text):
	date_list = text.split('.')
	return (MONTH_NAMES[int(date_list[1].lstrip('0'))] + ' ' + str(date_list[2].lstrip('0')) + 
		', ' + date_list[0])


# display date, time, and phase information to a console
# console should be 21x6
def DisplayTimeInfo(console):
	libtcod.console_clear(console)
	libtcod.console_set_default_foreground(console, libtcod.white)
	
	if campaign is None: return
	
	libtcod.console_print_ex(console, 10, 0, libtcod.BKGND_NONE, libtcod.CENTER, GetDateText(campaign.today))
	
	if campaign_day is None: return
	
	# depiction of time remaining in day
	libtcod.console_set_default_background(console, libtcod.darker_yellow)
	libtcod.console_rect(console, 0, 1, 21, 1, True, libtcod.BKGND_SET)
	
	time_str = campaign.current_week['day_start'].split(':')
	hours = campaign_day.day_clock['hour'] - int(time_str[0])
	minutes = campaign_day.day_clock['minute'] - int(time_str[1])
	if minutes < 0:
		hours -= 1
		minutes += 60
	minutes += (hours * 60)
	x = int(21.0 * float(minutes) / float(campaign_day.day_length))
	libtcod.console_set_default_background(console, libtcod.dark_yellow)
	libtcod.console_rect(console, 0, 1, x, 1, True, libtcod.BKGND_SET)
	libtcod.console_set_default_background(console, libtcod.black)
	
	text = str(campaign_day.day_clock['hour']).zfill(2) + ':' + str(campaign_day.day_clock['minute']).zfill(2)
	libtcod.console_print_ex(console, 10, 1, libtcod.BKGND_NONE, libtcod.CENTER, text)
	
	if scenario is None: return
	
	# current phase
	libtcod.console_set_default_foreground(console, SCEN_PHASE_COL[scenario.phase])
	libtcod.console_print_ex(console, 10, 2, libtcod.BKGND_NONE, libtcod.CENTER, 
		SCEN_PHASE_NAMES[scenario.phase] + ' Phase')
	


# display weather conditions info to a console, 14x12
def DisplayWeatherInfo(console):
	
	libtcod.console_clear(console)
	
	if campaign_day is None: return
	
	# cloud conditions on first two lines
	libtcod.console_set_default_background(console, libtcod.dark_blue)
	libtcod.console_rect(console, 0, 0, 14, 2, False, libtcod.BKGND_SET)
	
	if campaign_day.weather['Cloud Cover'] == 'Scattered':
		num = 4
	elif campaign_day.weather['Cloud Cover'] == 'Heavy':
		num = 8
	elif campaign_day.weather['Cloud Cover'] ==  'Overcast':
		num = 14
	else:
		# clear
		num = 0
	
	cell_list = (sample(list(range(14)), 14) + sample(list(range(14)), 14))
	for i in range(num):
		libtcod.console_set_char_background(console, cell_list[i], 0, libtcod.dark_grey,
			libtcod.BKGND_SET)
	for i in range(num):
		libtcod.console_set_char_background(console, cell_list[i+num], 1, libtcod.dark_grey,
			libtcod.BKGND_SET)
		
	libtcod.console_print_ex(console, 7, 1, libtcod.BKGND_NONE, libtcod.CENTER,
		campaign_day.weather['Cloud Cover'])
	
	# precipitation
	if campaign_day.weather['Precipitation'] in ['Rain', 'Heavy Rain']:
		char = 250
		libtcod.console_set_default_foreground(console, libtcod.light_blue)
		libtcod.console_set_default_background(console, libtcod.dark_blue)
	elif campaign_day.weather['Precipitation'] in ['Mist', 'Light Snow', 'Snow', 'Blizzard']:
		char = 249
		libtcod.console_set_default_foreground(console, libtcod.light_grey)
		libtcod.console_set_default_background(console, libtcod.dark_grey)
	else:
		char = 0
	libtcod.console_rect(console, 0, 2, 14, 7, False, libtcod.BKGND_SET)
	
	if campaign_day.weather['Precipitation'] in ['Rain', 'Light Snow']:
		num = 15
	elif campaign_day.weather['Precipitation'] in ['Heavy Rain', 'Snow']:
		num = 25
	elif campaign_day.weather['Precipitation'] == 'Blizzard':
		num = 30
	else:
		num = 0
	
	for i in range(num):
		x = libtcod.random_get_int(0, 0, 13)
		y = libtcod.random_get_int(0, 2, 7)
		libtcod.console_put_char(console, x, y, char)
	
	if campaign_day.weather['Precipitation'] != 'None':
		libtcod.console_print_ex(console, 7, 5, libtcod.BKGND_NONE, libtcod.CENTER,
			campaign_day.weather['Precipitation'])
	
	# ground conditions
	if campaign_day.weather['Ground'] in ['Dry', 'Wet']:
		libtcod.console_set_default_foreground(console, libtcod.white)
		libtcod.console_set_default_background(console, libtcod.dark_sepia)
	elif campaign_day.weather['Ground'] == 'Muddy':
		libtcod.console_set_default_foreground(console, libtcod.grey)
		libtcod.console_set_default_background(console, libtcod.darker_sepia)
	elif campaign_day.weather['Ground'] in ['Snow', 'Deep Snow']:
		libtcod.console_set_default_foreground(console, libtcod.light_blue)
		libtcod.console_set_default_background(console, libtcod.grey)
	libtcod.console_rect(console, 0, 9, 14, 2, False, libtcod.BKGND_SET)
	
	libtcod.console_print_ex(console, 7, 9, libtcod.BKGND_NONE, libtcod.CENTER,
		campaign_day.weather['Ground'])
	
	# current area terrain
	text = campaign_day.map_hexes[campaign_day.player_unit_location].terrain_type
	libtcod.console_print_ex(console, 7, 10, libtcod.BKGND_NONE,
		libtcod.CENTER, text)


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


# display a message window on the screen, pause, and then clear message from screen
# FUTURE: possible to highlight a CD/scenario hex, and have message appear near highlighed hex
# but not covering it
# FUTURE: game options may override this and display the message in the center of the map regardless
def ShowMessage(text, portrait=None, cd_highlight=None, scenario_highlight=None):
	
	# determine size of console
	if portrait is not None:
		width = 27
		height = 12
	else:
		width = 21
		height = 4
	
	lines = wrap(text, width-4)
	height += len(lines)
	
	# determine display location of console on screen
	x = WINDOW_XM + 1 - int(width / 2)
	
	if scenario is not None:
		if not scenario.finished:
			x += 12
	
	y = WINDOW_YM - int(height / 2)
	session.msg_location = (x, y)
	
	# create message console
	session.msg_con = NewConsole(width, height, libtcod.darkest_grey, libtcod.white) 
	DrawFrame(session.msg_con, 0, 0, width, height)
	
	# display portrait if any
	if portrait is not None:
		libtcod.console_set_default_background(session.msg_con, PORTRAIT_BG_COL)
		libtcod.console_rect(session.msg_con, 1, 1, 25, 8, True, libtcod.BKGND_SET)
		libtcod.console_blit(LoadXP(portrait), 0, 0, 0, 0, session.msg_con, 1, 1)
		libtcod.console_set_default_background(session.msg_con, libtcod.black)
	
	# display message
	# try to center message vertically in window
	x = int(width / 2)
	y = int(height / 2) - int(len(lines) / 2)
	if portrait is not None:
		y += 4
	
	for line in lines:
		libtcod.console_print_ex(session.msg_con, x, y, libtcod.BKGND_NONE, libtcod.CENTER, line.encode('IBM850'))
		if y == height-1: break
		y += 1
	
	# allow the message to be viewed by player
	Wait(100 + (40 * config['ArmCom2'].getint('message_pause')))
	
	# erase console and re-draw screen
	session.msg_con = None
	session.msg_location = None
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	libtcod.console_flush()



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
		libtcod.console_flush()
		event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
		if event != libtcod.EVENT_KEY_PRESS: exit = True
	session.key_down = False


# wait for a specified amount of miliseconds, refreshing the screen in the meantime
def Wait(wait_time, ignore_animations=False):
	
	# check for debug fast mode
	if DEBUG:
		if session.debug['Fast Mode']:
			wait_time = int(wait_time/4)
	
	wait_time = wait_time * 0.01
	start_time = time.time()
	while time.time() - start_time < wait_time:
		
		# check for animation update in scenario or campaign day or layer
		if not ignore_animations:
			CheckForAnimationUpdate()
			
		if libtcod.console_is_window_closed(): sys.exit()
		FlushKeyboardEvents()


# wait for player to press continue key
# option to allow backspace pressed instead, returns True if so 
def WaitForContinue(allow_cancel=False, ignore_animations=False):
	end_pause = False
	cancel = False
	while not end_pause:
		
		# check for animation update in scenario or campaign day or layer
		if not ignore_animations:
			CheckForAnimationUpdate()
		
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		if not GetInputEvent(): continue
		
		if key.vk == libtcod.KEY_BACKSPACE and allow_cancel:
			end_pause = True
			cancel = True
		elif key.vk == libtcod.KEY_TAB:
			end_pause = True
	if allow_cancel and cancel:
		return True
	return False


# check for animation frame update and console update
def CheckForAnimationUpdate():
	if scenario is not None:
		if scenario.init_complete:
			if time.time() - session.anim_timer >= ANIM_UPDATE_TIMER:
				scenario.UpdateAnimCon()
				scenario.UpdateScenarioDisplay()
		
	elif campaign_day is not None:
		if campaign_day.started and not campaign_day.ended:
			if time.time() - session.anim_timer >= ANIM_UPDATE_TIMER:
				campaign_day.UpdateAnimCon()
				campaign_day.UpdateCDDisplay()	
	
	# display message console overtop if any
	if session.msg_con is not None:
		(x, y) = session.msg_location
		libtcod.console_blit(session.msg_con, 0, 0, 0, 0, 0, x, y)


# load a console image from an .xp file
def LoadXP(filename):
	xp_file = gzip.open(DATAPATH + filename)
	raw_data = xp_file.read()
	xp_file.close()
	xp_data = xp_loader.load_xp_string(raw_data)
	console = libtcod.console_new(xp_data['width'], xp_data['height'])
	xp_loader.load_layer_to_console(console, xp_data['layer_data'][0])
	return console


# returns a path from one campaign day hex zone to another
# can be set to be blocked by river crossings and/or enemy-held zones
# based on function from ArmCom 1, which was based on:
# http://stackoverflow.com/questions/4159331/python-speed-up-an-a-star-pathfinding-algorithm
# http://www.policyalmanac.org/games/aStarTutorial.htm
def GetHexPath(hx1, hy1, hx2, hy2, rivers_block=True, enemy_zones_block=False):
	
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
	
	# sanity check
	if campaign_day is None:
		print('ERROR: Tried to generate a hex path without a campaign day object!')
		return []
	
	# clear any old pathfinding info
	for (hx, hy) in CAMPAIGN_DAY_HEXES:
		campaign_day.map_hexes[(hx,hy)].ClearPathInfo()
	
	node1 = campaign_day.map_hexes[(hx1, hy1)]
	node2 = campaign_day.map_hexes[(hx2, hy2)]
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
			hx, hy = campaign_day.GetAdjacentCDHex(current.hx, current.hy, direction)
			
			# no map hex exists here, skip
			if (hx, hy) not in CAMPAIGN_DAY_HEXES: continue
			
			node = campaign_day.map_hexes[(hx,hy)]
			
			# ignore nodes on closed list
			if node in closed_list: continue
			
			# check for route blocking
			if rivers_block:
				if direction in campaign_day.map_hexes[(current.hx, current.hy)].rivers:
					if direction not in campaign_day.map_hexes[(current.hx, current.hy)].bridges:
						continue
			
			if enemy_zones_block:
				if node.controlled_by == 1:
					continue
			
			# not really used yet
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
	return '*'


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
	
	(x1, y1) = scenario.PlotHex(hx1, hy1)
	(x2, y2) = scenario.PlotHex(hx2, hy2)
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
	if 140 < bearing < 220:
		return 'Rear'
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


# save the current game in progress
def SaveGame():
	if DEBUG:
		if session.debug['Suspend Save']: return
	save = shelve.open('savegame', 'n')
	save['campaign'] = campaign
	save['campaign_day'] = campaign_day
	save['scenario'] = scenario
	save['version'] = VERSION
	save.close()


# load a saved game
def LoadGame():
	global campaign, campaign_day, scenario
	save = shelve.open('savegame')
	campaign = save['campaign']
	campaign_day = save['campaign_day']
	scenario = save['scenario']
	save.close()


# check the saved game to see if it is compatible with the current game version
def CheckSavedGameVersion():
	save = shelve.open('savegame')
	saved_version = save['version']
	save.close()
	
	# if either is development version, must match exactly
	if '-' in saved_version or '-' in VERSION:
		if saved_version != VERSION:
			return saved_version
	
	# only allow loading the saved game if the first two components of the version numbers match
	version_list = saved_version.split('.')
	major_saved_version = version_list[0] + version_list[1]
	version_list = VERSION.split('.')
	major_current_version = version_list[0] + version_list[1]
	if major_saved_version == major_current_version:
		return ''
	return saved_version


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
			'animation_speed' : 1,			# not used yet
			'message_pause' : 1,
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
		libtcod.console_print(0, x+2, ly, line)
		ly += 1
	
	# if asking for confirmation, display yes/no choices, otherwise display a simple messages
	if confirm:
		text = 'Proceed? Y/N'
	else:
		text = 'Enter to Continue'
	
	libtcod.console_print_ex(0, WINDOW_XM, y+h-2, libtcod.BKGND_NONE, libtcod.CENTER,
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



# display the in-game menu: 84x54
def ShowGameMenu():
	
	# draw the menu console
	def DrawMenuCon():
		
		libtcod.console_clear(game_menu_con)
		
		# draw a frame to the game menu console
		libtcod.console_set_default_foreground(game_menu_con, libtcod.white)
		DrawFrame(game_menu_con, 0, 0, 84, 54)
		
		# display game name and version number
		libtcod.console_set_default_background(game_menu_con, libtcod.darker_grey)
		libtcod.console_rect(game_menu_con, 30, 2, 25, 7, True, libtcod.BKGND_SET)
		libtcod.console_set_default_background(game_menu_con, libtcod.black)
		DrawFrame(game_menu_con, 30, 2, 25, 7)
		
		libtcod.console_print_ex(game_menu_con, 42, 4, libtcod.BKGND_NONE,
			libtcod.CENTER, NAME)
		libtcod.console_print_ex(game_menu_con, 42, 6, libtcod.BKGND_NONE,
			libtcod.CENTER, VERSION)
		
		# section titles
		libtcod.console_set_default_foreground(game_menu_con, libtcod.white)
		libtcod.console_print_ex(game_menu_con, 42, 12, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Game Commands')
		libtcod.console_print_ex(game_menu_con, 42, 20, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Game Options')
		libtcod.console_set_default_background(game_menu_con, libtcod.darkest_blue)
		libtcod.console_rect(game_menu_con, 30, 12, 25, 1, False, libtcod.BKGND_SET)
		libtcod.console_rect(game_menu_con, 30, 20, 25, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(game_menu_con, libtcod.darker_blue)
		libtcod.console_rect(game_menu_con, 32, 12, 21, 1, False, libtcod.BKGND_SET)
		libtcod.console_rect(game_menu_con, 32, 20, 21, 1, False, libtcod.BKGND_SET)
		libtcod.console_set_default_background(game_menu_con, libtcod.black)
		
		# main commands
		libtcod.console_set_default_foreground(game_menu_con, ACTION_KEY_COL)
		libtcod.console_print(game_menu_con, 30, 14, 'Esc')
		libtcod.console_print(game_menu_con, 30, 15, 'Q')
		libtcod.console_set_default_foreground(game_menu_con, libtcod.lighter_grey)
		libtcod.console_print(game_menu_con, 35, 14, 'Close Menu')
		libtcod.console_print(game_menu_con, 35, 15, 'Save and Quit')
		
		# display game options
		DisplayGameOptions(game_menu_con, WINDOW_XM-15, 22, skip_esc=True)
		
		# display quote
		libtcod.console_set_default_foreground(game_menu_con, libtcod.grey)
		libtcod.console_print(game_menu_con, 25, 44, 'We are the Dead. Short days ago')
		libtcod.console_print(game_menu_con, 25, 45, 'We lived, felt dawn, saw sunset glow,')
		libtcod.console_print(game_menu_con, 25, 46, 'Loved and were loved, and now we lie')
		libtcod.console_print(game_menu_con, 25, 47, 'In Flanders fields.')
		libtcod.console_print(game_menu_con, 25, 49, 'John McCrae (1872-1918)')
		
		libtcod.console_blit(game_menu_con, 0, 0, 0, 0, 0, 3, 3)
		
	
	# create a local copy of the current screen to re-draw when we're done
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
	# darken screen background
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
	
	# generate menu console for the first time and blit to screen
	DrawMenuCon()
	
	# get input from player
	exit_menu = False
	while not exit_menu:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		if not GetInputEvent(): continue
		
		if key.vk == libtcod.KEY_ESCAPE:
			exit_menu = True
			continue
		
		key_char = DeKey(chr(key.c).lower())
		
		if chr(key.c).lower() == 'q':
			SaveGame()
			session.exiting = True
			exit_menu = True
		
		if ChangeGameSettings(key_char):
			# redraw menu to reflect new settings
			DrawMenuCon()
			continue
	
	# re-draw original screen
	libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
	del temp_con



# display a list of game options and current settings
def DisplayGameOptions(console, x, y, skip_esc=False):
	for (char, text) in [('F', 'Font Size'), ('S', 'Sound Effects'), ('P', 'Message Pause'), ('K', 'Keyboard'), ('Esc', 'Return to Main Menu')]:
		
		if char == 'Esc' and skip_esc: continue
		
		# extra spacing
		if char == 'Esc': y += 1
		
		libtcod.console_set_default_foreground(console, ACTION_KEY_COL)
		libtcod.console_print(console, x, y, char)
		
		libtcod.console_set_default_foreground(console, libtcod.lighter_grey)
		libtcod.console_print(console, x+4, y, text)
		
		# current option settings
		libtcod.console_set_default_foreground(console, libtcod.light_blue)
		
		# toggle font size
		if char == 'F':
			if config['ArmCom2'].getboolean('large_display_font'):
				text = '16x16'
			else:
				text = '8x8'
			libtcod.console_print(console, x+20, y, text)
		
		# sound effects
		elif char == 'S':
			if config['ArmCom2'].getboolean('sounds_enabled'):
				text = 'ON'
			else:
				text = 'OFF'
			libtcod.console_print(console, x+20, y, text)
		
		# message pause length
		elif char == 'P':
			text = ['Short', 'Normal', 'Long'][config['ArmCom2'].getint('message_pause')]
			libtcod.console_print(console, x+20, y, text)
		
		# keyboard settings
		elif char == 'K':
			libtcod.console_print(console, x+20, y, KEYBOARDS[config['ArmCom2'].getint('keyboard')])
		
		y += 1


# take a keyboard input and change game settings
def ChangeGameSettings(key_char, main_menu=False):
	
	global main_theme

	if key_char not in ['f', 's', 'p', 'k']:
		return False
	
	# switch font size
	if key_char == 'f':
		libtcod.console_delete(0)
		if config.getboolean('ArmCom2', 'large_display_font'):
			config['ArmCom2']['large_display_font'] = 'false'
			fontname = 'c64_8x8_ext.png'
		else:
			config['ArmCom2']['large_display_font'] = 'true'
			fontname = 'c64_16x16_ext.png'
		libtcod.console_set_custom_font(DATAPATH+fontname,
			libtcod.FONT_LAYOUT_ASCII_INROW, 16, 18)
		libtcod.console_init_root(WINDOW_WIDTH, WINDOW_HEIGHT,
			NAME + ' - ' + VERSION, fullscreen = False,
			renderer = RENDERER)
	
	# toggle sound effects on/off
	elif key_char == 's':
		if config['ArmCom2'].getboolean('sounds_enabled'):
			config['ArmCom2']['sounds_enabled'] = 'false'
			# stop main theme if in main menu
			if main_menu:
				mixer.Mix_FreeMusic(main_theme)
			main_theme = None
		else:
			config['ArmCom2']['sounds_enabled'] = 'true'
			# load main menu theme and play if in main menu
			session.LoadMainTheme()
			if main_menu:
				mixer.Mix_PlayMusic(main_theme, -1)
	
	# switch message pause length
	elif key_char == 'p':
		i = config['ArmCom2'].getint('message_pause')
		if i == 2:
			i = 0
		else:
			i += 1
		config['ArmCom2']['message_pause'] = str(i)
	
	# switch keyboard layout
	elif key_char == 'k':
		
		i = config['ArmCom2'].getint('keyboard')
		if i == len(KEYBOARDS) - 1:
			i = 0
		else:
			i += 1
		config['ArmCom2']['keyboard'] = str(i)
		GenerateKeyboards()
		
	SaveCFG()
	return True


# display a pop-up window with a prompt and allow player to enter a text string
# can also generate randomly selected strings from a given list
# returns the final string
def ShowTextInputMenu(prompt, original_text, max_length, string_list):
	
	# display the most recent text string to screen
	def ShowText(text):
		libtcod.console_rect(0, 28, 30, 32, 1, True, libtcod.BKGND_SET)
		libtcod.console_print_ex(0, 45, 30, libtcod.BKGND_NONE, libtcod.CENTER, text)
	
	# start with the original text string, can cancel input and keep this
	text = original_text
	
	# create a local copy of the current screen to re-draw when we're done
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
	# darken screen background
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
	
	# draw the text input menu to screen
	libtcod.console_rect(0, 27, 20, 34, 20, True, libtcod.BKGND_SET)
	DrawFrame(0, 27, 20, 34, 20)
	lines = wrap(prompt, 24)
	y = 23
	libtcod.console_set_default_foreground(0, libtcod.light_grey)
	for line in lines:
		libtcod.console_print_ex(0, 45, y, libtcod.BKGND_NONE, libtcod.CENTER, line.encode('IBM850'))
		y += 1
	
	libtcod.console_set_default_foreground(0, ACTION_KEY_COL)
	libtcod.console_print(0, 31, 34, 'Esc')
	libtcod.console_print(0, 31, 35, 'Del')
	libtcod.console_print(0, 31, 37, 'Enter')
	
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_print(0, 37, 34, 'Cancel')
	libtcod.console_print(0, 37, 35, 'Clear')
	libtcod.console_print(0, 37, 37, 'Confirm and Continue')
	
	if len(string_list) > 0:
		libtcod.console_set_default_foreground(0, ACTION_KEY_COL)
		libtcod.console_print(0, 31, 36, 'Tab')
		libtcod.console_set_default_foreground(0, libtcod.white)
		libtcod.console_print(0, 37, 36, 'Generate Random')
	
	# display current text string
	ShowText(text)
	
	exit_menu = False
	while not exit_menu:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		if not GetInputEvent(): continue
		
		# ignore shift key being pressed
		if key.vk == libtcod.KEY_SHIFT:
			session.key_down = False
		
		# cancel text input
		if key.vk == libtcod.KEY_ESCAPE:
			# re-draw original screen and return original text string
			libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
			del temp_con
			return original_text
		
		# confirm and return
		elif key.vk == libtcod.KEY_ENTER:
			exit_menu = True
			continue
		
		# select random string from list if any
		elif key.vk == libtcod.KEY_TAB:
			if len(string_list) == 0: continue
			text = choice(string_list)
		
		# clear string
		elif key.vk == libtcod.KEY_DELETE:
			text = ''
		
		# delete last character in string
		elif key.vk == libtcod.KEY_BACKSPACE:
			if len(text) == 0: continue
			text = text[:-1]
		
		# enter a new character
		else:
			# not a valid character
			if key.c == 0: continue
			
			# can't get any longer
			if len(text) == max_length: continue
			
			key_char = chr(key.c)
			if key.shift: key_char = key_char.upper()
			
			# filter key input
			if not ((32 <= ord(key_char) <= 126)):
				continue
			
			text += key_char
		
		FlushKeyboardEvents()
		ShowText(text)
		
	libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
	del temp_con
	return text


# allow the player to select one option from a list
def GetOption(option_list):
	
	# create a local copy of the current screen to re-draw when we're done
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	# darken screen background
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
	
	# show list of options
	c = 65
	y = 15
	for text in option_list:
		libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
		libtcod.console_put_char(con, 25, y, chr(c))
		libtcod.console_set_default_foreground(con, libtcod.light_grey)
		libtcod.console_print(con, 27, y, text)
		y += 1
		c += 1
	
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	option = None
	
	exit_menu = False
	while not exit_menu:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		if not GetInputEvent(): continue
		
		if key.vk == libtcod.KEY_ESCAPE:
			exit_menu = True
			continue
		
		option_code = key.c - 97
		if option_code < len(option_list):
			option = option_list[option_code]
			exit_menu = True
	
	# re-draw original root console
	libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
	del temp_con
	
	return option
	

# display the debug flags menu, not enabled in distribution versions
def ShowDebugMenu():
	
	# draw the debug menu to screen
	def DrawDebugMenu():
		libtcod.console_clear(con)
		libtcod.console_set_default_foreground(con, libtcod.light_red)
		libtcod.console_print_ex(con, WINDOW_XM, 2, libtcod.BKGND_NONE, libtcod.CENTER, 'DEBUG MENU')
		
		libtcod.console_set_default_foreground(con, TITLE_COL)
		libtcod.console_print(con, 6, 6, 'Flags')
		
		y = 8
		n = 1
		for k, value in session.debug.items():
			libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
			libtcod.console_print(con, 6, y, chr(n+64))
			if value:
				libtcod.console_set_default_foreground(con, libtcod.white)
			else:
				libtcod.console_set_default_foreground(con, libtcod.dark_grey)
			libtcod.console_print(con, 8, y, k)
			y += 2
			n += 1
		
		# special commands
		libtcod.console_set_default_foreground(con, TITLE_COL)
		libtcod.console_print(con, 50, 6, 'Commands')
		x = 50
		y = 8
		libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
		for xm in range(7):
			libtcod.console_print(con, x, y+(xm*2), str(xm+1))
		
		libtcod.console_set_default_foreground(con, libtcod.light_grey)
		libtcod.console_print(con, x+2, y, 'Regenerate CD Map Roads & Rivers')
		libtcod.console_print(con, x+2, y+2, 'Give Crewman Serious Wound')
		libtcod.console_print(con, x+2, y+4, 'Immobilize Player')
		libtcod.console_print(con, x+2, y+6, 'Set Time to End of Day')
		libtcod.console_print(con, x+2, y+8, 'End Current Scenario')
		libtcod.console_print(con, x+2, y+10, 'Export Campaign Log')
		libtcod.console_print(con, x+2, y+12, 'Generate New Weather')
		
		libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
		libtcod.console_print(con, 33, 56, 'Esc')
		libtcod.console_print(con, 33, 57, 'Enter')
		libtcod.console_set_default_foreground(con, libtcod.white)
		libtcod.console_print(con, 39, 56, 'Return to Game')
		libtcod.console_print(con, 39, 57, 'Save Flags and Return')
		
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		
	# build a dictionary of ordered letter to key values
	letter_dict = {}
	n = 1
	for k, value in session.debug.items():
		letter_dict[chr(n+64)] = k
		n += 1
	
	# save the current root console
	temp_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
	libtcod.console_blit(0, 0, 0, 0, 0, temp_con, 0, 0)
	
	# draw the menu for the first time
	DrawDebugMenu()
	
	exit_menu = False
	while not exit_menu:
		if libtcod.console_is_window_closed(): sys.exit()
		libtcod.console_flush()
		if not GetInputEvent(): continue
		
		if key.vk == libtcod.KEY_ESCAPE:
			exit_menu = True
			continue
		
		elif key.vk == libtcod.KEY_ENTER:
			# save current debug settings
			with open(DATAPATH + 'debug.json', 'w', encoding='utf8') as data_file:
				json.dump(session.debug, data_file, indent=1)
			exit_menu = True
			continue
		
		key_char = chr(key.c).upper()
		
		if key_char in letter_dict:
			k = letter_dict[key_char]
			# flip the flag setting
			session.debug[k] = not session.debug[k]
			DrawDebugMenu()
			continue
		
		key_num = int(key_char)
		
		# regenerate CD map roads
		if key_num == 1:
			if campaign_day is not None:
				campaign_day.GenerateRoads()
				campaign_day.GenerateRivers()
				campaign_day.UpdateCDMapCon()
				campaign_day.UpdateCDDisplay()
				ShowMessage('Roads and rivers regenerated')
				exit_menu = True
				continue
		
		# give crewman in selected position a serious wound
		elif key_num == 2:
			if scenario is not None:
				option_list = []
				for position in scenario.player_unit.positions_list:
					option_list.append(position.name)
				position_name = GetOption(option_list)
				if position_name is None: return
				crewman = scenario.player_unit.GetPersonnelByPosition(position_name)
				if crewman is None: continue
				crewman.DoWoundCheck(auto_serious=True)
				exit_menu = True
				continue
		
		# immobilize player
		elif key_num == 3:
			if scenario is not None:
				if scenario.player_unit.immobilized:
					continue
				scenario.player_unit.ImmobilizeMe()
				scenario.UpdatePlayerInfoCon()
				ShowMessage('Player tank immobilized')
				exit_menu = True
				continue
		
		# set current time to end of combat day
		elif key_num == 4:
			if campaign_day is not None:
				campaign_day.day_clock['hour'] = campaign_day.end_of_day['hour']
				campaign_day.day_clock['minute'] = campaign_day.end_of_day['minute']
				DisplayTimeInfo(time_con)
				text = 'Time is now ' + str(campaign_day.day_clock['hour']).zfill(2) + ':' + str(campaign_day.day_clock['minute']).zfill(2)
				ShowMessage(text)
				exit_menu = True
				continue
		
		# end the current scenario
		elif key_num == 5:
			if scenario is not None:
				scenario.finished = True
				ShowMessage('Scenario finished flag set to True')
				exit_menu = True
				continue
		
		# export current campaign log
		elif key_num == 6:
			if campaign is not None:
				ExportLog()
				ShowMessage('Log exported')
				exit_menu = True
				continue
		
		# generate new weather
		elif key_num == 7:
			if campaign_day is not None:
				campaign_day.GenerateWeather()
				ShowMessage('New weather conditions generated')
				DisplayWeatherInfo(cd_weather_con)
				campaign_day.InitAnimations()
				exit_menu = True
				continue
				
	
	# re-draw original root console
	libtcod.console_blit(temp_con, 0, 0, 0, 0, 0, 0, 0)
	del temp_con



# display a list of crew positions and their crewmen to a console
def DisplayCrew(unit, console, x, y, highlight):
	
	for position in unit.positions_list:
		
		# highlight selected position and crewman
		if highlight is not None:
			if unit.positions_list.index(position) == highlight:
				libtcod.console_set_default_background(console, libtcod.darker_blue)
				libtcod.console_rect(console, x, y, 24, 4, True, libtcod.BKGND_SET)
				libtcod.console_set_default_background(console, libtcod.black)
		
		# display position name and location in vehicle (eg. turret/hull)
		libtcod.console_set_default_foreground(console, libtcod.light_blue)
		libtcod.console_print(console, x, y, position.name)
		libtcod.console_set_default_foreground(console, libtcod.white)
		libtcod.console_print_ex(console, x+23, y, libtcod.BKGND_NONE, 
			libtcod.RIGHT, position.location)
		
		# display last name of crewman and buttoned up / exposed status if any
		if position.crewman is None:
			libtcod.console_print(console, x, y+1, 'Empty')
		else:
			position.crewman.DisplayName(console, x, y+1, firstname_only=True)
			position.crewman.DisplayName(console, x+1, y+2, lastname_only=True)
		
			if position.crewman.ce:
				text = 'CE'
			else:
				text = 'BU'
			libtcod.console_print_ex(console, x+23, y+1, libtcod.BKGND_NONE, libtcod.RIGHT, text)
			
			# display current nickname if any
			if position.crewman.nickname != '':
				libtcod.console_print(console, x, y+3, '"' + position.crewman.nickname + '"')
			
			# display current status if any
			if position.crewman.status != '':
				libtcod.console_set_default_foreground(console, libtcod.red)
				libtcod.console_print_ex(console, x+23, y+3, libtcod.BKGND_NONE, libtcod.RIGHT, 
					position.crewman.status)
			
		libtcod.console_set_default_foreground(console, libtcod.white)
		y += 5


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
def DeKey(key_char):
	if key_char in keyboard_decode:
		return keyboard_decode[key_char]
	return key_char



# turn a standard key into the one for the current keyboard layout
def EnKey(key_char):
	if key_char in keyboard_encode:
		return keyboard_encode[key_char]
	return key_char
	


##########################################################################################
#                                     Sound Effects                                      #
##########################################################################################

# play a given sample, and return the channel it is playing on
def PlaySound(sound_name):
	
	sample = mixer.Mix_LoadWAV((SOUNDPATH + sound_name + '.ogg').encode('ascii'))
	if sample is None:
		print('ERROR: Sound not found: ' + sound_name)
		return
	
	channel = mixer.Mix_PlayChannel(-1, sample, 0)
	
	del sample
	
	if channel == -1:
		print('ERROR: could not play sound: ' + sound_name)
		print(mixer.Mix_GetError())
		return
	
	return channel


# select and play a sound effect for a given situation
def PlaySoundFor(obj, action):
	
	# sounds disabled
	if not config['ArmCom2'].getboolean('sounds_enabled'):
		return
	
	if action == 'fire':
		if obj.GetStat('type') == 'Gun':
			
			if obj.GetStat('name') == 'AT Rifle':
				PlaySound('at_rifle_firing')
				return
			
			# temp - used for all large guns for now
			PlaySound('37mm_firing_0' + str(libtcod.random_get_int(0, 0, 3)))
			return
			
		if obj.stats['type'] in MG_WEAPONS:
			PlaySound('zb_53_mg_00')
			return
		
		if obj.GetStat('name') == 'Rifles':
			PlaySound('rifle_fire_0' + str(libtcod.random_get_int(0, 0, 3)))
			return
	
	elif action == 'he_explosion':
		PlaySound('37mm_he_explosion_0' + str(libtcod.random_get_int(0, 0, 1)))
		return
	
	elif action == 'armour_save':
		PlaySound('armour_save_0' + str(libtcod.random_get_int(0, 0, 1)))
		return
	
	elif action == 'vehicle_explosion':
		PlaySound('vehicle_explosion_00')
		return
	
	elif action == 'movement':
		
		if obj.GetStat('movement_class') in ['Wheeled', 'Fast Wheeled']:
			PlaySound('wheeled_moving_0' + str(libtcod.random_get_int(0, 0, 2)))
			return
		
		elif obj.GetStat('class') in ['Tankette', 'Light Tank', 'Medium Tank']:
			PlaySound('light_tank_moving_0' + str(libtcod.random_get_int(0, 0, 2)))
			return
	
	elif action == 'plane_incoming':
		PlaySound('plane_incoming_00')
		return
	
	elif action == 'stuka_divebomb':
		PlaySound('stuka_divebomb_00')
		return
	
	elif action == 'ricochet':
		PlaySound('ricochet')
		return
	
	elif action == 'sniper_hit':
		PlaySound('sniper_hit')
		return
	
	elif action == 'move_1_shell':
		PlaySound('shell_move_1')
		return
	
	elif action == 'move_10_shell':
		PlaySound('shell_move_10')
		return
	
	elif action == 'add skill':
		PlaySound('add_skill')
		return
	
	elif action == 'command_select':
		PlaySound('command_select')
		return
	
	elif action == 'smoke':
		PlaySound('smoke')
		return
	
	elif action == 'hatch':
		PlaySound('hatch')
		return
	
	elif action == 'hull_down_save':
		PlaySound('hull_down_save')
		return
	
	print ('ERROR: Could not determine which sound to play for action: ' + action)
			



##########################################################################################
#                                      Main Script                                       #
##########################################################################################

global main_title, main_theme
global campaign, campaign_day, scenario, session
global keyboard_decode, keyboard_encode

# save console output to a log file
if not DEBUG:
	sys.stdout = open('runtime_log.txt', 'w')

print('Starting ' + NAME + ' version ' + VERSION)	# startup message

# try to load game settings from config file, will create a new file if none present
LoadCFG()

os.putenv('SDL_VIDEO_CENTERED', '1')			# center game window on screen

# determine font to use based on settings file
if config['ArmCom2'].getboolean('large_display_font'):
	fontname = 'c64_16x16_ext.png'
else:
	fontname = 'c64_8x8_ext.png'

# set up custom font and root console
libtcod.console_set_custom_font(DATAPATH+fontname, libtcod.FONT_LAYOUT_ASCII_INROW,
        16, 18)
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
		# load main menu theme
		session.LoadMainTheme()
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
game_menu_con = libtcod.console_new(84, 54)
libtcod.console_set_default_background(game_menu_con, libtcod.black)
libtcod.console_set_default_foreground(game_menu_con, libtcod.white)
libtcod.console_clear(game_menu_con)

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()




##########################################################################################
#                                        Main Menu                                       #
##########################################################################################

# display studio logo and pause
if not DEBUG:
	libtcod.console_clear(0)
	libtcod.console_blit(LoadXP('cats.xp'), 0, 0, 0, 0, 0, WINDOW_XM-15, WINDOW_YM-19)
	libtcod.console_flush()
	Wait(120, ignore_animations=True)
	libtcod.console_clear(0)
	libtcod.console_flush()

# player main them if loaded
if main_theme is not None:
	mixer.Mix_PlayMusic(main_theme, -1)

# load and generate main title background
main_title = LoadXP('main_title.xp')
if session.tank_portrait is not None:
	libtcod.console_blit(session.tank_portrait, 0, 0, 0, 0, main_title, 7, 6)

# display version number and program info
libtcod.console_set_default_foreground(main_title, libtcod.light_grey)
libtcod.console_print_ex(main_title, WINDOW_XM, WINDOW_HEIGHT-6, libtcod.BKGND_NONE,
	libtcod.CENTER, VERSION)
libtcod.console_print_ex(main_title, WINDOW_XM, WINDOW_HEIGHT-4,
	libtcod.BKGND_NONE, libtcod.CENTER, 'Copyright 2019')
libtcod.console_print_ex(main_title, WINDOW_XM, WINDOW_HEIGHT-3,
	libtcod.BKGND_NONE, libtcod.CENTER, 'Free Software under the GNU GPL')
libtcod.console_print_ex(main_title, WINDOW_XM, WINDOW_HEIGHT-2,
	libtcod.BKGND_NONE, libtcod.CENTER, 'www.armouredcommander.com')

libtcod.console_blit(LoadXP('poppy.xp'), 0, 0, 0, 0, main_title, 1, WINDOW_HEIGHT-8)

# gradient animated effect for main menu
GRADIENT = [
	libtcod.Color(51, 51, 51), libtcod.Color(64, 64, 64), libtcod.Color(128, 128, 128),
	libtcod.Color(192, 192, 192), libtcod.Color(255, 255, 255), libtcod.Color(192, 192, 192),
	libtcod.Color(128, 128, 128), libtcod.Color(64, 64, 64), libtcod.Color(51, 51, 51),
	libtcod.Color(51, 51, 51)
]

# set up gradient animation timing
time_click = time.time()
gradient_x = WINDOW_WIDTH + 10

# draw the main title to the screen and display menu options
# if options_menu_active, draw the options menu instead
def UpdateMainTitleCon(options_menu_active):
	libtcod.console_blit(main_title, 0, 0, 0, 0, con, 0, 0)
	
	y = 38
	if options_menu_active:
		
		# display game options commands
		DisplayGameOptions(con, WINDOW_XM-10, 38)
		
	else:
		
		for (char, text) in [('C', 'Continue'), ('N', 'New Campaign'), ('O', 'Options'), ('Q', 'Quit')]:
			# grey-out continue game option if no saved game present
			disabled = False
			if char == 'C' and not os.path.exists('savegame.dat'):
				disabled = True
			
			if disabled:
				libtcod.console_set_default_foreground(con, libtcod.dark_grey)
			else:
				libtcod.console_set_default_foreground(con, ACTION_KEY_COL)
			libtcod.console_print(con, WINDOW_XM-5, y, char)
			
			if disabled:
				libtcod.console_set_default_foreground(con, libtcod.dark_grey)
			else:
				libtcod.console_set_default_foreground(con, libtcod.lighter_grey)
			libtcod.console_print(con, WINDOW_XM-3, y, text)	
			
			y += 1
	
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)


# update the animation effect
def AnimateMainMenu():
	
	global gradient_x
	
	for x in range(0, 10):
		if x + gradient_x > WINDOW_WIDTH: continue
		for y in range(19, 34):
			char = libtcod.console_get_char(con, x + gradient_x, y)
			fg = libtcod.console_get_char_foreground(con, x + gradient_x, y)
			if char != 0 and fg != GRADIENT[x]:
				libtcod.console_set_char_foreground(con, x + gradient_x,
					y, GRADIENT[x])
	gradient_x -= 2
	if gradient_x <= 0: gradient_x = WINDOW_WIDTH + 10

# activate root menu to start
options_menu_active = False

# draw the main title console to the screen for the first time
UpdateMainTitleCon(options_menu_active)

# Main Menu loop
exit_game = False

while not exit_game:
	
	# emergency exit in case of endless loop
	if libtcod.console_is_window_closed(): sys.exit()
	
	# trigger animation and update screen
	if time.time() - time_click >= 0.06:
		AnimateMainMenu()
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		time_click = time.time()
	
	libtcod.console_flush()
	
	if not GetInputEvent(): continue
	
	key_char = chr(key.c).lower()
	
	# options sub-menu
	if options_menu_active:
		
		if ChangeGameSettings(key_char, main_menu=True):
			UpdateMainTitleCon(options_menu_active)
			
		# exit options menu
		elif key.vk == libtcod.KEY_ESCAPE:
			options_menu_active = False
			UpdateMainTitleCon(options_menu_active)
	
	# root main menu
	else:
		
		if key_char == 'q':
			exit_game = True
			continue
		
		elif key_char == 'o':
			options_menu_active = True
			UpdateMainTitleCon(options_menu_active)
			continue
		
		# start or continue a campaign
		elif key_char in ['n', 'c']:
			
			# check/confirm menu option
			if key_char == 'c':
				if not os.path.exists('savegame.dat'):
					continue
				
				result = CheckSavedGameVersion() 
				if result != '':
					text = 'Saved game was saved with an older version of the program (' + result + '), cannot continue.'
					ShowNotification(text)
					libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
					continue
				
				libtcod.console_clear(0)
				libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER,
					'Loading...')
				libtcod.console_flush()
				
				# load the saved game
				LoadGame()
				
				# pause main theme if loaded
				if main_theme is not None:
					mixer.Mix_PauseMusic()
			
			else:
				# confirm savegame overwrite
				if os.path.exists('savegame.dat'):
					text = 'Starting a new campaign will PERMANTLY ERASE the existing saved campaign.'
					result = ShowNotification(text, confirm=True)
					# cancel and return to main menu
					if not result:
						libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
						continue
			        
			        ### Start a New Campaign ###
			        
			        # create a new campaign object and allow player to select a campaign
				campaign = Campaign()
				result = campaign.CampaignSelectionMenu()
				
				# player canceled new campaign start
				if not result:
					campaign = None
					UpdateMainTitleCon(options_menu_active)
					continue
				
				# pause main theme if loaded
				if main_theme is not None:
					mixer.Mix_PauseMusic()
				
				# allow player to select their tank and tank name
				(unit_id, tank_name) = campaign.TankSelectionMenu()
				
				# create the player unit
				campaign.player_unit = Unit(unit_id)
				campaign.player_unit.unit_name = tank_name
				campaign.player_unit.nation = campaign.stats['player_nation']
				campaign.player_unit.GenerateNewPersonnel()
				campaign.player_unit.ClearGunAmmo()
				
				# create a new campaign day
				campaign_day = CampaignDay()
				campaign_day.GenerateRoads()
				campaign_day.GenerateRivers()
				
				# placeholder for the currently active scenario
				scenario = None
				
			# go to campaign calendar loop
			campaign.DoCampaignCalendarLoop()
			
			# reset exiting flag
			session.exiting = False
			
			# restart main theme if loaded
			if main_theme is not None:
				if mixer.Mix_PausedMusic() == 1:
					mixer.Mix_RewindMusic()
					mixer.Mix_ResumeMusic()
				else:
					mixer.Mix_PlayMusic(main_theme, -1)
			
			UpdateMainTitleCon(options_menu_active)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)

print('Armoured Commander II shutting down')

# END #

