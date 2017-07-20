# -*- coding: UTF-8 -*-
# Python 2.7.8
# Libtcod 1.5.1
##########################################################################################
#                                                                                        #
#                                Armoured Commander II                                   #
#                                                                                        #
##########################################################################################
#                                                                                        #
#             Project Started February 23, 2016; Restarted July 25, 2016                 #
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

##### External Scripts #####
import languages

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
VIEW_ALL = False					# human player can see all hexes in viewport

NAME = 'Armoured Commander II'
#VERSION = 'Alpha 1.0'					# game version: determines saved game compatability
VERSION = 'July 21 2017'			
SUBVERSION = ''						# descriptive, no effect on compatability
DATAPATH = 'data/'.replace('/', os.sep)			# path to data files
LIMIT_FPS = 50						# maximum screen refreshes per second
WINDOW_WIDTH = 83					# width of game window in characters
WINDOW_HEIGHT = 60					# height "
WINDOW_XM = int(WINDOW_WIDTH/2)				# horizontal center of game window
WINDOW_YM = int(WINDOW_HEIGHT/2)			# vertical "

# list of unit images to display on main menu
TANK_IMAGES = ['unit_TK3.xp', 'unit_TKS_20mm.xp', 'unit_vickers_ejw.xp', 'unit_7TP.xp',
	'unit_pz_35t.xp', 'unit_pz_II.xp'
]

# gradient animated effect for main menu
GRADIENT = [
	libtcod.Color(51, 51, 51), libtcod.Color(64, 64, 64), libtcod.Color(128, 128, 128),
	libtcod.Color(192, 192, 192), libtcod.Color(255, 255, 255), libtcod.Color(192, 192, 192),
	libtcod.Color(128, 128, 128), libtcod.Color(64, 64, 64), libtcod.Color(51, 51, 51),
	libtcod.Color(51, 51, 51)
]

# Game engine constants, can be tweaked for slightly different results
MAX_LOS_DISTANCE = 6			# maximum distance that a Line of Sight can be drawn
MAX_LOS_MOD = 6				# maximum total terrain modifier along a LoS before it is blocked
MAX_BU_LOS_DISTANCE = 4			# " for buttoned-up crewmen
ELEVATION_M = 20.0			# each elevation level represents x meters of height
BASE_SPOT_SCORE = 5			# base score required to spot unknown enemy unit
HEX_STACK_LIMIT = 6			# maximum number of units in a map hex stack

# chance of extra turn / missed turn when moving in:
# Open Ground, Road, Difficult Terrain
# if negative, it's a chance to miss a turn; 0 means no chance, do not roll
MOVE_TURN_CHANCE = [
	[0, 7, -11],			# Infantry
	[4, 8, -10],			# Tank
	[-12, 9, -8]			# Wheeled
]

# base to-hit scores required for Point Fire attacks
BASE_TO_HIT = [
	[10,8,7],			# <= 1 hex range
	[9,7,7],			# 2 hex range
	[9,7,7],			# 3 "
	[8,6,8],			# 4 "
	[7,5,8],			# 5 "
	[6,4,7]				# 6 "
]

# Area Fire attack chart
# Final FP, infantry/gun score required, vehicle/other score required
AF_CHART = [
	(1, 5, 3),
	(2, 6, 4),
	(4, 7, 5),
	(6, 8, 6),
	(8, 9, 7),
	(12, 10, 8),
	(16, 11, 9),
	(20, 12, 10),
	(24, 13, 11),
	(30, 14, 12),
	(36, 15, 13)
]


# short forms for crew positions, used to fit information into player unit info console, etc.
CREW_POSITION_ABB = {
	'Commander' : 'C',
	'Commander/Gunner' : 'C/G',
	'Gunner' : 'G',
	'Gunner/Loader' : 'G/L',
	'Loader' : 'L',
	'Driver' : 'D',
	'Assistant Driver' : 'AD'
}

# order in which to display crew positions
CREW_POSITION_ORDER = ['Commander', 'Commander/Gunner', 'Gunner', 'Gunner/Loader', 'Loader',
	'Driver', 'Assistant Driver'
]

# order in which to display ammo types
AMMO_TYPE_ORDER = ['HE', 'AP']

# Colour definitions
ELEVATION_SHADE = 0.15					# difference in shading for map hexes of
							#   different elevations

RIVER_BG_COL = libtcod.Color(0, 0, 217)			# background color for river edges
DIRT_ROAD_COL = libtcod.Color(50, 40, 25)		# background color for dirt roads

NEUTRAL_OBJ_COL = libtcod.Color(0, 50, 255)		# neutral objective color
ENEMY_OBJ_COL = libtcod.Color(255, 50, 0)		# enemy-held "
FRIENDLY_OBJ_COL = libtcod.Color(50, 255, 0)		# friendly-held "

ACTION_KEY_COL = libtcod.Color(70, 170, 255)		# colour for key commands
TITLE_COL = libtcod.white				# fore and background colours for
TITLE_BG_COL = libtcod.Color(0, 50, 100)		#  console titles and highlighted options
SECTION_BG_COL = libtcod.Color(0, 32, 64)		# darker bg colour for sections
INFO_TEXT_COL = libtcod.Color(190, 190, 190)		# informational text colour
PORTRAIT_BG_COL = libtcod.Color(217, 108, 0)		# background color for unit portraits
HIGHLIGHT_COLOR = libtcod.Color(51, 153, 255)		# colour for highlighted text 
HIGHLIGHT_COLOR2 = libtcod.Color(0, 64, 0)		# alternate "
WEAPON_LIST_COLOR = libtcod.Color(25, 25, 90)		# background for weapon list in PSG console
SELECTED_WEAPON_COLOR = libtcod.Color(50, 50, 150)	# " selected weapon
ACTIVE_MSG_COL = libtcod.Color(0, 210, 0)		# active message colour

FRIENDLY_UNIT_COL = libtcod.Color(64, 0, 255)		# friendly unit and name color
FRIENDLY_HL_COL = libtcod.Color(0, 0, 60)		# " highlight background color
ENEMY_UNIT_COL = libtcod.Color(255, 0, 64)		# enemy unit and name color
ENEMY_HL_COL = libtcod.Color(60, 0, 0)			# " highlight background color
UNKNOWN_UNIT_COL = libtcod.Color(200, 200, 200)		# unknown unit and name color
UNKNOWN_HL_COL = libtcod.Color(40, 40, 0)		# " highlight background color

TARGET_HL_COL = libtcod.Color(55, 0, 0)			# target unit highlight background color 

INACTIVE_COL = libtcod.Color(100, 100, 100)		# inactive option color
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency

SMALL_CON_BKG = libtcod.Color(25, 25, 25)		# background colour for small info consoles

HIGHLIGHT_CHARS = [249, 7, 7, 7, 7, 249]		# characters for hex highlight animation
HEX_HIGHLIGHT_COL = libtcod.Color(100, 255, 100)	# color for hex highlight animation

# Descriptor definitions
MORALE_DESC = {
	6 : 'Reluctant',
	7 : 'Regular',
	8 : 'Confident',
	9 : 'Fearless',
	10 : 'Fanatic'
}
SKILL_DESC = {
	6 : 'Green',
	7 : '2nd Line',
	8 : '1st Line',
	9 : 'Veteran',
	10 : 'Elite'
}

MONTH_NAMES = [
	'', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
	'September', 'October', 'November', 'December'
]

# Note: hexes use an axial coordinate system:
# http://www.redblobgames.com/grids/hexagons/#coordinates-axial

DESTHEX = [(0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0)]	# change in hx, hy values for hexes in each direction
PLOT_DIR = [(0,-1), (1,-1), (1,1), (0,1), (-1,1), (-1,-1)]	# position of direction indicator
TURRET_CHAR = [254, 47, 92, 254, 47, 92]			# characters to use for turret display

# pre-calculated hexpairs and second hex step for lines of sight along hexspines
HEXSPINES = {
	0: [(0,-1), (1,-1), (1,-2)],
	1: [(1,-1), (1,0), (2,-1)],
	2: [(1,0), (0,1), (1,1)],
	3: [(0,1), (-1,1), (-1,2)],
	4: [(-1,1), (-1,0), (-2,1)],
	5: [(-1,0), (0,-1), (-1,-1)]
}

# tile locations of hex depiction edges
HEX_EDGE_TILES = [(-1,-2), (0,-2), (1,-2), (2,-1), (3,0), (2,1), (1,2), (0,2), (-1,2),
	(-2,1), (-3,0), (-2,-1)]

# internal coordinates for map viewport hexes
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



##########################################################################################
#                                         Classes                                        #
##########################################################################################

# Crewman: represents a crewman who can be assigned to a position in the player tank
# FUTURE: may also generate for AI vehicles as well?
class Crewman:
	def __init__(self):
		self.name = ['', '']			# first and last name
		self.position_training = {		# skill in working different tank positions
			'Commander/Gunner' : 0,
			'Loader' : 0,
			'Driver' : 0,
			'Assistant Driver' : 0
		}
		self.action = None			# current action, if None then
							#   crewman is spotting
	
	def GetName(self, shortname=False, lastname=False):
		if shortname:
			text = self.name[0]
			text = text[0]
			text += '. ' + self.name[1]
		elif lastname:
			text = self.name[1]
		else:
			text = self.name[0] + ' ' + self.name[1]
		return text.decode('utf8').encode('IBM850')


# represents a single position in a vehicle that can be occupied by a crewman
class CrewPosition:
	def __init__(self, name, turret, hatch, open_visible, closed_visible):
		
		self.name = name		# name of this position
		self.crewman = None		# pointer to crewman currently occupying this position
		self.turret = turret		# True if position is in turret, otherwise it's in hull
		self.hatch = hatch		# None if no hatch, otherwise 'Closed' or 'Open'
		self.large_hatch = False	# Later set to True if crewman is especially exposed when hatch is open
		
		# visible hextants, relative to hull/turret facing of the vehicle
		self.open_visible = open_visible	# list of visible hextants when hatch is open
		self.closed_visible = closed_visible	# " closed
		
		# set up list of possible crew actions
		self.actions = []
		
		# all positions can spot
		self.actions.append(('Spot', 'Try to spot and identify enemy units'))
		
		
	# toggle hatch status
	def ToggleHatch(self):
		if self.hatch is None: return
		if self.hatch == 'Closed':
			self.hatch = 'Open'
		else:
			self.hatch = 'Closed'
		

# Unit: represents a single vehicle, squad, gun, or small team
class Unit:
	def __init__(self, unit_id):
		self.alive = True			# unit is not out of action yet
		self.dummy = False			# unit is not a real one and will disappear
							#   when spotted - AI units only
		self.unit_id = unit_id			# unique ID for unit type, used to
							#   load basic stats from unit_defs.xml
		self.unit_name = ''			# descriptive name of unit type
		self.vehicle_name = None		# tank or other vehicle name
		self.portrait = None
		self.ai = AI(self)			# pointer to AI instance
		self.owning_player = None		# player that controls this unit
		#self.squadron_leader = None		# used for player squadron
							# Not used yet
		
		self.morale_lvl = 0			# morale rating, set during unit spawn
		self.skill_lvl = 0			# skill rating, "
		
		# location coordinates
		self.hx = -1				# hex location of this unit, will be set
		self.hy = -1				#   by PlaceAt()
		self.screen_x = 0			# draw location on the screen
		self.screen_y = 0			#   set by DrawMe()
		self.vp_hx = None			# location in viewport if any
		self.vp_hy = None			# "
		self.anim_x = 0				# animation location in console
		self.anim_y = 0
		
		# basic unit stats
		self.infantry = False			# unit type flags
		self.gun = False
		self.vehicle = False			
		self.known = False			# unit is known to the opposing side
		
		self.facing = None			# facing direction: guns and vehicles must have this set
		self.turret_facing = None		# facing of main turret on unit
		self.movement_class = ''		# movement class
		self.extra_turns = 0			# number of extra turns (positive) or missed
							#   turns (negative) this unit has coming to it
		
		self.armour = None			# armour factors if any
		self.max_ammo = 0			# maximum number of gun ammo carried
		self.weapon_list = []			# list of weapons
		
		self.unresolved_fp = 0			# fp from attacks to be resolved at end of action
		self.unresolved_ap = []			# list of unsolved AP hits
		
		self.acquired_target = None		# tuple: unit has acquired this unit to this level (1/2)
		
		# action flags
		self.moved = False			# unit moved or pivoted in this turn
		self.moved_last_action = False		# unit moved or pivoted in its previous turn
		self.fired = False			# unit fired 1+ weapons this turn
		self.changed_facing = False
		
		# status flags
		self.pinned = False
		self.broken = False
		self.shocked = False
		self.bogged = False
		
		# special abilities or traits
		self.recce = False
		self.unreliable = False
		
		# load the baseline stats for this unit from data file
	
		# find the unit type entry in the data file
		root = xml.parse(DATAPATH + 'unit_defs.xml')
		item_list = root.findall('unit_def')
		found = False
		for item in item_list:
			if item.find('id').text == self.unit_id:	# this is the one we need
				found = True
				break
		if not found:
			print 'ERROR: Could not find unit stats for: ' + self.unit_id
			return
		
		# load stats from item
		self.unit_name = item.find('name').text
		if item.find('portrait') is not None:
			self.portrait = item.find('portrait').text
		
		# weapon info
		xml_weapon_list = item.findall('weapon')
		if xml_weapon_list is not None:
			for weapon_item in xml_weapon_list:
				self.weapon_list.append(Weapon(weapon_item))
				
		# infantry stats if any
		if item.find('infantry') is not None:
			self.infantry = True
		
		# vehicle stats if any
		if item.find('vehicle') is not None:
			self.vehicle = True
			if item.find('turret') is not None:
				self.turret_facing = 0		# will later be set by scenario.SpawnEnemy()
			if item.find('size_class') is not None:
				self.size_class = item.find('size_class').text
			else:
				self.size_class = 'Normal'
			if item.find('armour') is not None:
				self.armour = {}
				armour_ratings = item.find('armour')
				self.armour['turret_front'] = int(armour_ratings.find('turret_front').text)
				self.armour['turret_side'] = int(armour_ratings.find('turret_side').text)
				self.armour['hull_front'] = int(armour_ratings.find('hull_front').text)
				self.armour['hull_side'] = int(armour_ratings.find('hull_side').text)
			if item.find('recce') is not None: self.recce = True
			if item.find('unreliable') is not None: self.unreliable = True
			
			# maximum total gun ammo load
			if item.find('max_ammo') is not None:
				self.max_ammo = int(item.find('max_ammo').text)
			
			# set up crew positions
			self.crew_positions = None
			if item.find('crew_position') is not None:
				self.crew_positions = []
				item_list = item.findall('crew_position')
				for i in item_list:
					name = i.find('name').text
					turret = False
					if i.find('turret') is not None:
						turret = True
					hatch = None
					if i.find('hatch') is not None:
						hatch = 'Open'
					
					# lists of hextants visible when hatch is open/closed
					open_visible = []
					if i.find('open_visible') is not None:
						string = i.find('open_visible').text
						for c in string:
							open_visible.append(int(c))
					
					closed_visible = []
					if i.find('closed_visible') is not None:
						string = i.find('closed_visible').text
						for c in string:
							closed_visible.append(int(c))
					
					new_position = CrewPosition(name, turret,
						hatch, open_visible, closed_visible)
					
					# check for special statuses
					if i.find('large_hatch') is not None:
						new_position.large_hatch = True
					
					self.crew_positions.append(new_position)
				
				# FUTURE: sort crew_positions by name based on CREW_POSITION_ORDER?
				
		
		# gun stats
		elif item.find('gun') is not None:
			self.gun = True
			self.deployed = True
			if item.find('size_class') is not None:
				self.size_class = item.find('size_class').text
			else:
				self.size_class = 'Normal'
			if item.find('gun_shield') is not None:
				self.gun_shield = True
		
		self.movement_class = item.find('movement_class').text
		self.display_char = self.GetDisplayChar()	# set initial display character

	# perform pre-activation automatic actions
	def DoPreActivation(self):
		self.moved = False
		self.fired = False
		for weapon in self.weapon_list:
			weapon.fired = False
			weapon.no_rof_this_turn = False
		self.changed_facing = False
		self.RecoveryCheck()
		# turn on LoS display if this is player and we have a weapon active
		if self == scenario.player_unit and scenario.selected_weapon is not None:
			scenario.display_los = True
		# move to top of hex stack
		map_hex = GetHexAt(self.hx, self.hy)
		if len(map_hex.unit_stack) > 1:
			self.MoveToTopOfStack(map_hex)
		
		# player unit
		if self == scenario.player_unit:
			# reset player crew flags
			for crew_position in scenario.player_unit.crew_positions:
				if crew_position.crewman is None: continue
				crew_position.crewman.action = None
			scenario.AddMessage('Your activation begins', None)
		
		# check for regaining unknown status
		if not self.known:
			return
		
		for unit in scenario.unit_list:
			if not unit.alive: continue
			if unit.owning_player == self.owning_player: continue
			if unit.dummy: continue
			los = GetLoS(unit.hx, unit.hy, self.hx, self.hy)
			if los != -1:
				return
		# no enemy units in LoS
		self.HideMe()
			
			
	# perform post-activation automatic actions
	def DoPostActivation(self):
		
		# player unit only
		if self == scenario.player_unit:
			
			# turn off any LoS display
			scenario.display_los = False
			
			# recalculate FoV
			scenario.hex_map.CalcFoV()
			UpdateVPConsole()
			DrawScreenConsoles()
		
		# resolve any hits
		for unit in scenario.unit_list:
			if unit.owning_player == self.owning_player: continue
			if not unit.alive: continue
			if unit.unresolved_fp > 0 or len(unit.unresolved_ap) > 0:
				unit.ResolveHits()
		
		# set moved flag for next activation
		self.moved_last_action = self.moved

	# find the crewman in the given position and set their current action
	# returns False if no such position, position is empty, or crewman already has a different action
	def SetCrewmanAction(self, position_name, action):
		for position in self.crew_positions:
			if position.name == position_name:
				if position.crewman is None:
					return False
				if position.crewman.action is not None:
					if position.crewman.action != action:
						return False
				position.crewman.action = action
				return True
		return False
		
	# return the chance of getting an extra turn / missing a turn if unit moves into target hex
	def GetMovementTurnChance(self, hx, hy):
		# move not possible
		if not self.CheckMoveInto(hx, hy): return 0
		if self.infantry:
			row = MOVE_TURN_CHANCE[0]
		elif self.movement_class in ['Tank', 'Fast Tank']:
			row = MOVE_TURN_CHANCE[1]
		elif self.movement_class == 'Wheeled':
			row = MOVE_TURN_CHANCE[2]
		else:
			# movement class not recognized
			return 0
		map_hex2 = GetHexAt(hx, hy)
		if map_hex2.terrain_type.difficult:
			score = row[2]
		else:
			map_hex1 = GetHexAt(self.hx, self.hy)
			if GetDirectionToAdjacent(self.hx, self.hy, hx, hy) in map_hex1.dirt_road_links:
				score = row[1]
			else:
				if map_hex2.terrain_type.terrain_mod == 0:
					score = row[0]
				else:
					return 0
		
		# apply modifiers to base score
		if self.movement_class == 'Fast Tank':
			if score > 0:
				score += 1
			else:
				score -= 1
			
		# ignore impossible rolls
		if score < -12: return 0
		
		return score

	# move this unit to the top of its map hex stack
	def MoveToTopOfStack(self, map_hex):
		map_hex.unit_stack.remove(self)
		map_hex.unit_stack.insert(0, self)
		UpdateUnitConsole()
		UpdateHexInfoConsole()

	# resolve any outstanding hits at the end of an action
	def ResolveHits(self):
		
		# FUTURE: possible damage to unprotected crew
		if self.unresolved_fp > 0 and self.armour is not None:
			text = 'Firepower attack has no effect on ' + self.GetName()
			scenario.AddMessage(text, (self.hx, self.hy))
			self.unresolved_fp = 0
		
		# unresolved area fire hits to resolve
		if self.unresolved_fp > 0:
		
			text = ('Resolving ' + str(self.unresolved_fp) + ' fp of attacks on ' +
				self.GetName())
			scenario.AddMessage(text, (self.hx, self.hy))
			
			# get base score to equal/beat
			for (chart_fp, inf_score, veh_score) in reversed(AF_CHART):
				if chart_fp <= self.unresolved_fp:
					if self.infantry or self.gun:
						score = inf_score
					else:
						score = veh_score
					break
			
			d1, d2, roll = Roll2D6()
			
			if roll == 2 or float(roll) < float(score) * 0.5:
				text = self.GetName() + ' is destroyed!'
				scenario.AddMessage(text, (self.hx, self.hy))
				self.DestroyMe()
				return
			
			elif roll == score:
				if not self.MoraleCheck(0):
					self.PinMe()
				else:
					text = 'Attack had no effect on ' + self.GetName()
					scenario.AddMessage(text, (self.hx, self.hy))
			
			elif roll < score:
				text = self.GetName() + ' must take a Morale Test'
				scenario.AddMessage(text, (self.hx, self.hy))
				if not self.MoraleCheck(0):
					# failed
					self.BreakMe()
				else:
					# passed
					self.PinMe()
			else:
				text = 'Attack had no effect on ' + self.GetName()
				scenario.AddMessage(text, (self.hx, self.hy))
			
			# reset unresolved fp
			self.unresolved_fp = 0
		
		if len(self.unresolved_ap) == 0: return
		
		# do AP rolls for unresolved ap hits
		for attack_obj in self.unresolved_ap:
			if self.ResolveAPHit(attack_obj):
				
				# DEBUG - player cannot be killed
				#if self == scenario.player_unit:
				#	text = 'Your magical armour protects you.'
				#	scenario.AddMessage(text, None)
				#	return
				
				# FUTURE: different outcomes for penetrations possible
				text = self.GetName() + ' is destroyed!'
				scenario.AddMessage(text, (self.hx, self.hy))
				self.DestroyMe()
				return
		self.unresolved_ap = []
	
	# perform a morale check for this unit
	def MoraleCheck(self, modifier):
		
		# calculate effective morale level
		morale_lvl = self.morale_lvl
		
		# modifier provided by test conditions
		morale_lvl += modifier
		
		# protective terrain
		map_hex = GetHexAt(self.hx, self.hy)
		if map_hex.terrain_type.terrain_mod > 0:
			morale_lvl += map_hex.terrain_type.terrain_mod
		
		# normalize
		if morale_lvl < 3:
			morale_lvl = 3
		elif morale_lvl > 10:
			morale_lvl = 10
		
		# do the roll
		d1, d2, roll = Roll2D6()
		
		if roll <= morale_lvl:
			return True
		return False
	
	# break this unit
	def BreakMe(self):
		# double break, destroy instead
		if self.broken:
			text = self.GetName() + ' failed a Break test while broken and is destroyed!'
			scenario.AddMessage(text, (self.hx, self.hy))
			self.DestroyMe()
			return
		self.broken = True
		text = self.GetName() + ' is Broken'
		scenario.AddMessage(text, (self.hx, self.hy))
		# any pinned status is cancelled
		if self.pinned:
			self.pinned = False
	
	# pin this unit
	def PinMe(self):
		# already pinned or broken
		if self.pinned or self.broken:
			text = 'Attack had no further effect on ' + self.GetName()
		else:
			self.pinned = True
			text = self.GetName() + ' is Pinned'
		scenario.AddMessage(text, (self.hx, self.hy))
	
	# remove this unit from the game
	def DestroyMe(self):
		# remove from map hex
		map_hex = GetHexAt(self.hx, self.hy)
		map_hex.unit_stack.remove(self)
		# change alive flag, will no longer be activated
		self.alive = False
		# clear acquired target records
		self.ClearAcquiredTargets()
		# clear player's target if it was this unit
		if scenario.player_target == self:
			scenario.player_target = None
		UpdateUnitConsole()

	# roll for recovery from negative statuses
	def RecoveryCheck(self):
		
		if self.pinned:
			if self.MoraleCheck(0):
				self.pinned = False
				text = self.GetName() + ' recovers from being Pinned'
				scenario.AddMessage(text, (self.hx, self.hy))
			return
		
		if self.broken:
			if self.MoraleCheck(0):
				self.broken = False
				self.pinned = True
				text = self.GetName() + ' recovers from being Broken and is now Pinned'
				scenario.AddMessage(text, (self.hx, self.hy))

	# return a description of this unit
	# if true_name, return the real identity of this PSG no matter what
	def GetName(self, true_name=False):
		if not true_name:
			if self.owning_player == 1 and not self.known:
				return 'Unknown Unit'
		return self.unit_name.decode('utf8').encode('IBM850')
	
	# assign a crewmember to a crew position
	def SetCrew(self, position_name, crewman, player=False):
		
		for position in self.crew_positions:
			if position.name == position_name:
				position.crewman = crewman
				return
		
		print ('ERROR: tried to assign crew to ' + position_name + ' position but ' +
			'no such position exists!')
	
	# check to see if this unit is spotted
	# if just_moved is True, the unit just now completed a move action
	# if just_fired is True, the unit just now completed an attack action
	def DoSpotCheck(self, just_moved=False, just_fired=False):
		
		# unit is already spotted, no need to test
		if self.known: return
		
		# get current terrain status
		open_ground = False
		if GetHexAt(self.hx, self.hy).terrain_type.terrain_mod == 0:
			open_ground = True
		
		# get list of enemy units in LoS
		enemy_list = []
		for unit in scenario.unit_list:
			if not unit.alive: continue
			if unit.owning_player == self.owning_player: continue
			if unit.dummy: continue
			# FUTURE: check LoS for each crewmember in enemy unit
			los = GetLoS(unit.hx, unit.hy, self.hx, self.hy)
			if los == -1: continue
			distance = GetHexDistance(unit.hx, unit.hy, self.hx, self.hy)
			# recce units count as being in close range up to 5 hexes
			if 3 < distance <= 5 and unit.recce:
				distance = 3
			enemy_list.append((distance, unit))
			
			# check for enemy unit's loss of concealment
			if self.dummy: continue
			if not unit.known and not unit.infantry and not unit.gun:
				if GetHexAt(unit.hx, unit.hy).terrain_type.terrain_mod == 0:
					unit.SpotMe()
		
		# no enemies in LoS
		if len(enemy_list) == 0: return
		
		# get range of nearest enemy unit with LoS
		enemy_list.sort(key=lambda x: x[0])
		(distance, unit) = enemy_list[0]
		close_range = False
		if distance <= 3:
			close_range = True
		
		if self.infantry:
			if not (not close_range and not open_ground) and just_fired:
				#print 'DEBUG: spotted unit just fired'
				self.SpotMe()
			elif open_ground and close_range and just_moved:
				#print 'DEBUG: spotted unit just moved'
				self.SpotMe()
		
		# emplaced guns
		# FUTURE: distinguish when a gun is being towed vs. emplaced
		elif self.gun:
			if close_range and just_fired:
				#print 'DEBUG: spotted unit just fired'
				self.SpotMe()
		
		# vehicles, etc.
		else:
			if open_ground:
				#print 'DEBUG: spotted unit was in open ground'
				self.SpotMe()
			elif close_range and just_fired:
				#print 'DEBUG: spotted unit just fired'
				self.SpotMe()
			elif close_range and just_moved:
				#print 'DEBUG: spotted unit just moved'
				self.SpotMe()
	
	# this unit has been spotted by an enemy unit
	def SpotMe(self):
		if self.known: return
		
		# dummy unit reveal
		if self.dummy:
			text = 'No enemy unit actually there.'
			scenario.AddMessage(text, (self.hx, self.hy))
			self.DestroyMe()
			return
		
		self.known = True

		# update unit console
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		
		# show message
		if self.owning_player == 0:
			text = 'Your '
		else:
			text = 'Enemy '
		text += self.GetName() + ' has been spotted!'
		scenario.AddMessage(text, (self.hx, self.hy))
	
	# regain unknown status for this unit
	def HideMe(self):
		# update console and screen to make sure unit has finished move animation
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		if self.owning_player == 0:
			if self == scenario.player_unit:
				text = 'You are'
			else:
				text = self.GetName() + ' is'
			text += ' now unseen by the enemy'
		else:
			text = 'Lost contact with ' + self.GetName()
		scenario.AddMessage(text, (self.hx, self.hy))
		self.known = False
		UpdateUnitConsole()
		if scenario.active_unit == self:
			UpdatePlayerUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
	
	# get display character to be used on hex map
	def GetDisplayChar(self):
		
		# player unit
		if scenario.player_unit == self:
			return '@'
		
		# unknown enemy unit
		if self.owning_player == 1 and not self.known:
			return '?'
		
		# infantry
		if self.infantry:
			return 176
		
		# gun, set according to deployed status / hull facing
		if self.gun:
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
		if self.vehicle:
			
			# turretless vehicle
			if self.turret_facing is None:
				return 249
			return 9

		# default
		return '!'
	
	

##########################################################################################

	# clear any acquired target links between this unit and any other
	def ClearAcquiredTargets(self):
		self.acquired_target = None
		for unit in scenario.unit_list:
			if unit.acquired_target is None: continue
			(ac_target, ac_level) = unit.acquired_target
			if ac_target == self:
				unit.acquired_target = None

	# draw this unit to the unit console in the given viewport hx, hy location
	# if stack_size > 1, indicate total number of units in hex stack
	def DrawMe(self, hx, hy, stack_size):
		
		# don't draw if unknown enemy outside of FoV
		if not self.known and self.owning_player == 1:
			if not GetHexAt(self.hx, self.hy).vis_to_player:
				return
		
		# calculate draw position
		if self.anim_x == 0 or self.anim_y == 0:
			(x,y) = PlotHex(hx, hy)
		# position override for animations
		else:
			x = self.anim_x
			y = self.anim_y
			
		# record draw position on screen
		self.screen_x = x + 27
		self.screen_y = y + 4
		# record viewport hex location as well
		self.vp_hx = hx
		self.vp_hy = hy
		
		self.display_char = self.GetDisplayChar()
		
		# determine foreground color to use
		if self.owning_player == 1:
			if not self.known:
				col = UNKNOWN_UNIT_COL
			else:
				col = ENEMY_UNIT_COL
		else:	
			col = libtcod.white
		libtcod.console_put_char_ex(unit_con, x, y, self.display_char, col,
			libtcod.black)
		
		# display stack size if required
		if stack_size > 1:
			if self.facing is None:
				direction = 0
			elif self.turret_facing is not None:
				direction = self.turret_facing
			else:
				direction = self.facing
			direction = ConstrainDir(direction - scenario.player_unit.facing + 3)
			if direction in [5, 0, 1]:
				direction = 0
			else:
				direction = 3
			
			x_mod, y_mod = PLOT_DIR[direction]
			libtcod.console_put_char_ex(unit_con, x+x_mod, y+y_mod, str(stack_size),
				libtcod.dark_grey, libtcod.black)
		
		# determine if we need to display a turret / gun depiction
		if self.infantry: return
		if self.owning_player == 1 and not self.known: return
		
		# use turret facing if present, otherwise hull facing
		if self.turret_facing is not None:
			facing = self.turret_facing
		else:
			facing = self.facing
		
		# determine location to draw character
		direction = ConstrainDir(facing - scenario.player_unit.facing)
		x_mod, y_mod = PLOT_DIR[direction]
		char = TURRET_CHAR[direction]
		libtcod.console_put_char_ex(unit_con, x+x_mod, y+y_mod, char, col, libtcod.black)
		
	# determine if this unit is able to move into the target hex
	def CheckMoveInto(self, new_hx, new_hy):
		if self.movement_class == 'Gun': return False
		if (new_hx, new_hy) not in scenario.hex_map.hexes: return False
		if GetDirectionToAdjacent(self.hx, self.hy, new_hx, new_hy) < 0: return False
		map_hex = GetHexAt(new_hx, new_hy)
		if map_hex.terrain_type.water: return False
		if len(map_hex.unit_stack) > HEX_STACK_LIMIT: return False
		if len(map_hex.unit_stack) > 0:
			for unit in map_hex.unit_stack:
				# friendly unit
				if unit.owning_player == self.owning_player: continue
				# unspotted unit
				if not unit.known: continue
				# at least one known enemy unit here
				return False
		return True
	
	# try to move this unit into the target hex
	# vehicles must be facing this direction to move, or can do a reverse move
	# returns True if the move was successful
	
	# FUTURE: check for reverse move and apply modifiers if so
	def MoveInto(self, new_hx, new_hy):
		
		# make sure move is allowed
		if not self.CheckMoveInto(new_hx, new_hy):
			return False
		
		# set driver crew action - for now, player only
		if self == scenario.player_unit:
			self.SetCrewmanAction('Driver', 'Drive')
			UpdatePlayerUnitConsole()	
		
		map_hex1 = GetHexAt(self.hx, self.hy)
		map_hex2 = GetHexAt(new_hx, new_hy)
		
		# check for unspotted enemy in target hex
		# if so, all units in target hex are spotted and action ends
		if len(map_hex2.unit_stack) > 0:
			spotted_enemy = False
			for unit in reversed(map_hex2.unit_stack):
				if unit.owning_player != self.owning_player and not unit.known:
					spotted_enemy = True
					unit.SpotMe()
			if spotted_enemy:
				# rebuild menu since move may no longer possible into this hex
				scenario.BuildCmdMenu()
				DrawScreenConsoles()
				return False
		
		# record score for extra/missed turn if applicable
		extra_turn_score = self.GetMovementTurnChance(new_hx, new_hy)
		
		# check for squadron movement
		unit_list = [self]
		#for unit in map_hex1.unit_stack:
		#	if unit.squadron_leader == self:
		#		unit_list.append(unit)
		
		# set location in new hex for all moving units
		for unit in unit_list:
			map_hex1.unit_stack.remove(unit)
			unit.hx = new_hx
			unit.hy = new_hy
			# player units always get bumped to top of stack
			if scenario.player_unit == unit:
				map_hex2.unit_stack.insert(0, unit)
			else:
				map_hex2.unit_stack.append(unit)
		
		# display movement animation if on viewport
		if self.vp_hx is not None and self.vp_hy is not None:
		
			direction = GetDirectionToAdjacent(map_hex1.hx, map_hex1.hy, new_hx, new_hy)
			direction = ConstrainDir(direction - scenario.player_unit.facing)
			(new_vp_hx, new_vp_hy) = GetAdjacentHex(self.vp_hx, self.vp_hy, direction)
		
			(x1,y1) = PlotHex(self.vp_hx, self.vp_hy)
			(x2,y2) = PlotHex(new_vp_hx, new_vp_hy)
			line = GetLine(x1,y1,x2,y2)
			pause_time = config.getint('ArmCom2', 'animation_speed') * 0.1
			for (x,y) in line[1:-1]:
				self.anim_x = x
				self.anim_y = y
				UpdateUnitConsole()
				DrawScreenConsoles()
				libtcod.console_flush()
				Wait(pause_time)
			self.anim_x = 0
			self.anim_y = 0
		
		# set action flag for next activation
		self.moved = True
		
		# clear any acquired targets
		self.ClearAcquiredTargets()
		
		# if player was targeting this unit, clear the player's target
		if scenario.player_target == self:
			scenario.player_target = None
		
		# recalculate viewport and update consoles for player movement
		if scenario.player_unit == self:
			UpdateContextCon()
			scenario.SetVPHexes()
			scenario.hex_map.CalcFoV()
			UpdateVPConsole()
			UpdateHexInfoConsole()
			UpdateObjectiveConsole()
		
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		
		# check for concealment loss
		self.DoSpotCheck(just_moved=True)
		
		# do extra/missed turn roll if any
		if extra_turn_score != 0:
			d1, d2, roll = Roll2D6()
			if extra_turn_score > 0:
				if roll <= extra_turn_score:
					# extra turn!
					self.extra_turns += 1
					if scenario.player_unit == self:
						scenario.AddMessage('You have moved swiftly enough to take another action', None)
			else:
				if roll >= abs(extra_turn_score):
					# missed turn!
					self.extra_turns -= 1
					if scenario.player_unit == self:
						scenario.AddMessage('You have been delayed by difficult terrain and will miss your next action', None)
		
		# default movement message
		if scenario.player_unit == self and self.extra_turns == 0:
			scenario.AddMessage('You move into a new area.', None)
		
		return True
	
	# attempt to pivot this unit to face the given direction
	# FUTURE: first check if possible, might be immobilized, etc.
	def PivotToFace(self, direction):
		if self.facing is None: return False
		facing_change = direction - self.facing
		self.facing = direction
		self.changed_facing = True
		
		# rotate turret facing direction if any
		if self.turret_facing is not None:
			self.turret_facing = CombineDirs(self.turret_facing, facing_change)
		
		# rotate viewport if player pivot
		if scenario.player_unit == self:
			UpdatePlayerUnitConsole()
			scenario.SetVPHexes()
			UpdateContextCon()
			UpdateVPConsole()
			UpdateHexInfoConsole()
			UpdateObjectiveConsole()
		
		UpdateUnitConsole()
		
		return True
	
	# rotate turret to face new direction
	def RotateTurret(self, direction):
		if self.turret_facing is None: return False
		self.turret_facing = direction
		UpdateUnitConsole()
		return True
	
	# resolve an AP hit on this unit
	def ResolveAPHit(self, attack_obj):
		
		# calculate and save armour penetration roll
		(base_ap, modifiers, final_ap) = CalcAPRoll(attack_obj)
		attack_obj.base_ap = base_ap
		attack_obj.modifiers = modifiers
		attack_obj.final_ap = final_ap
		
		# display AP roll
		DisplayAttack(attack_obj, ap_roll=True)
		WaitForEnter()
		
		# do dice roll and display animation
		pause_time = config.getint('ArmCom2', 'animation_speed') * 0.5
		for i in range(5):
			d1, d2, roll = Roll2D6()
			DrawDie(attack_con, 9, 50, d1)
			DrawDie(attack_con, 14, 50, d2)
			libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			Wait(pause_time)
		
		# display roll result
		text = str(roll) + ': '
		if roll <= attack_obj.final_ap:
			text += 'Shot penetrated!'
		else:
			text += 'Shot bounced off!'
			
		libtcod.console_print_ex(attack_con, 13, 54, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		libtcod.console_rect(attack_con, 1, 57, 24, 1, True, libtcod.BKGND_NONE)
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		libtcod.console_print(attack_con, 6, 57, 'Enter')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		libtcod.console_print(attack_con, 12, 57, 'Continue')
		libtcod.console_blit(attack_con, 0, 0, 30, 60, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		
		WaitForEnter()
		
		if roll <= attack_obj.final_ap:
			return True
		return False


# Weapon class: represents a weapon carried by or mounted on a unit
class Weapon:
	def __init__(self, item):
		
		self.name = ''			# name of this weapon if not automatically generated
		self.fired = False		# weapon has fired this turn
		self.no_rof_this_turn = False	# RoF now allowed this turn
		self.firing_group = None
		
		self.stats = {}
		
		# load weapon stats from xml item
		self.weapon_type = item.find('type').text
		if item.find('name') is not None:
			self.name = item.find('name').text
		
		if item.find('firing_group') is not None:
			self.firing_group = int(item.find('firing_group').text)
		
		self.stats['rof'] = 0
		if item.find('rof') is not None:
			self.stats['rof'] = int(item.find('rof').text)
		
		# gun stats
		if self.weapon_type == 'gun':
			self.stats['calibre'] = 0
			if item.find('calibre') is not None:
				self.stats['calibre'] = int(item.find('calibre').text)
			
			self.stats['long_range'] = ''
			if item.find('long_range') is not None:
				self.stats['long_range'] = item.find('long_range').text
			
			self.stats['max_range'] = 6
			if item.find('max_range') is not None:
				self.stats['max_range'] = int(item.find('max_range').text)
			
			self.stats['rr_size'] = 0
			self.stats['use_ready_rack'] = None
			if item.find('rr_size') is not None:
				self.stats['rr_size'] = int(item.find('rr_size').text)
				self.stats['use_ready_rack'] = True
			
			# list of allowed ammo types
			ammo_type_list = []
			if item.find('ammo_type') is not None:
				item_list = item.findall('ammo_type')
				for i in item_list:
					ammo_type_list.append(i.text)
			self.stats['ammo_types'] = ammo_type_list[:]
			
			
			# ammo load stats
			# FUTURE: these should be set to 0/empty and set by player
			self.stats['loaded_ammo'] = 'AP'
			self.stats['reload_ammo'] = 'AP'
			
			self.stores = {}
			self.stores['HE'] = 26
			self.stores['AP'] = 40
			self.ready_rack = {}
			self.ready_rack['HE'] = 3
			self.ready_rack['AP'] = 3
		
		# area fire weapon stats
		elif self.weapon_type in ['small_arms', 'coax_mg', 'hull_mg']:
			self.stats['fp'] = int(item.find('fp').text)
			if item.find('max_range') is not None:
				self.stats['max_range'] = int(item.find('max_range').text)
			else:
				if self.weapon_type == 'small_arms':
					self.stats['max_range'] = 1
				elif self.weapon_type == 'coax_mg':
					self.stats['max_range'] = 4
				else:
					self.stats['max_range'] = 2
			
		# weapon mount
		if item.find('mount') is not None:
			self.stats['mount'] = item.find('mount').text
		
		# firing crew if any
		if item.find('fired_by') is not None:
			fired_by = []
			item_list = item.findall('fired_by')
			for i in item_list:
				fired_by.append(i.text)
			self.stats['fired_by'] = fired_by
	
	# return a short display name for this weapon
	def GetName(self):
		if self.name != '':
			return self.name
		if self.weapon_type == 'gun':
			text = str(self.stats['calibre']) + 'mm'
			if self.stats['long_range'] != '':
				text += '(' + self.stats['long_range'] + ')'
		elif self.weapon_type == 'coax_mg':
			text = 'Co-ax MG'
		elif self.weapon_type == 'hull_mg':
			text = 'Hull MG'
		else:
			text = 'ERROR'
		return text
	
	# find an appropriate crewman and set the action to fire this weapon
	def SetFiredAction(self, unit):
		# no such stat for this weapon
		if 'fired_by' not in self.stats:
			return
		for position_name in self.stats['fired_by']:
			if unit.SetCrewmanAction(position_name, 'Fire ' + self.GetName()):
				return
		print 'ERROR: Could not find a crewman to fire ' + self.GetName()
	
	# load ammo into an empty gun or switch out loaded ammo for different type
	def CycleAmmoLoad(self):
		if not self.weapon_type == 'gun':
			return False
		
		# determine type of shell to try to load
		if self.stats['loaded_ammo'] is None:
			switch_type = self.stats['reload_ammo']
		else:
			ammo_types_list = self.stats['ammo_types']
			i = ammo_types_list.index(self.stats['loaded_ammo'])
			if i == len(self.stats['ammo_types']) - 1:
				i = 0
			else:
				i += 1
			switch_type = ammo_types_list[i]
		
		# see if a such a shell is available, and 
		if self.stores[switch_type] > 0:
			self.stores[switch_type] -= 1
		elif self.ready_rack[switch_type] > 0:
			self.ready_rack[switch_type] -= 1
		else:
			return False
		
		# put back the current shell if any
		if self.stats['loaded_ammo'] is not None:
			self.stores[self.stats['loaded_ammo']] += 1
		
		# load the new shell
		self.stats['loaded_ammo'] = switch_type
		
		self.no_rof_this_turn = False
		text = ('Your loader loads ' + self.GetName() + ' with a ' +
			switch_type + ' shell.')
		scenario.AddMessage(text, None)
		
		return True
	
	# toggle use of ready rack to reload next shell
	def ToggleRR(self):
		if not self.weapon_type == 'gun':
			return False
		if self.stats['use_ready_rack'] is None:
			return False
		self.stats['use_ready_rack'] = not self.stats['use_ready_rack']
		
		text = self.GetName() + ' will'
		if not self.stats['use_ready_rack']:
			text += ' not'
		text += ' use the ready rack to reload.'
		scenario.AddMessage(text, None)
		
		return True
	
	# cycle the type of ammo to reload next
	def CycleAmmoReload(self):
		if len(self.stats['ammo_types']) < 2:
			return False
		ammo_types_list = self.stats['ammo_types']
		i = ammo_types_list.index(self.stats['reload_ammo'])
		if i == len(self.stats['ammo_types']) - 1:
			i = 0
		else:
			i += 1
		self.stats['reload_ammo'] = ammo_types_list[i]
		text = self.GetName() + ' will now be reloaded with ' + self.stats['reload_ammo']
		text += ' ammo'
		scenario.AddMessage(text, None)
		return True
		

# animation handler
# keeps track of animations in progress and updates the animation console layer
class AnimHandler:
	def __init__(self):
		
		# flag to let rest of program know when a limited-lifespan animation has finished
		self.anim_finished = False
		
		# rain animation effect
		self.raindrops = []
		for i in range(14):
			x = libtcod.random_get_int(0, 0, 56)
			y = libtcod.random_get_int(0, 0, 56)
			lifetime = libtcod.random_get_int(0, 4, 7)
			self.raindrops.append([x, y, lifetime])
		self.rain_timer = time.time()
		# FUTURE: will be set by weather handler
		self.rain_active = False
		
		# gun weapon attack effect
		self.gun_line = []			# path of projectile on screen
		self.gun_location = 0			# index number of current x,y location of projectile
		self.gun_timer = time.time()		# animation timer
		self.gun_click = 0			# time between animation updates
		self.gun_active = False
		
		# MG / small arms attack effect
		self.af_attack_line = []		# path of attack on screen
		self.af_attack_timer = time.time()	# animation timer
		self.af_attack_click = 0		# time between animation updates
		self.af_attack_remaining = 0		# remaining number of updates before end
		self.af_attack_active = False
		
		# map hex highlight effect
		self.highlight_vp_hex = None
		self.highlight_timer = time.time()	# animation timer
		self.highlight_click = 0		# time between animation updates
		self.highlight_char = 0			# current character of animation
	
	# start an MG / small arms attack effect
	def InitAFAttackEffect(self, x1, y1, x2, y2):
		self.af_attack_line = GetLine(x1, y1, x2, y2, los=True)
		self.af_attack_timer = time.time()
		self.af_attack_click = float(config.getint('ArmCom2', 'animation_speed')) * 0.001
		self.af_attack_positions = sample(self.af_attack_line, int(len(self.af_attack_line) / 5))
		self.af_attack_remaining = 20
		self.af_attack_active = True
	
	# start a gun projectile animation
	def InitGunEffect(self, x1, y1, x2, y2):
		self.gun_line = GetLine(x1, y1, x2, y2, los=True)
		self.gun_location = 0
		self.gun_timer = time.time()
		self.gun_click = float(config.getint('ArmCom2', 'animation_speed')) * 0.001
		self.gun_active = True
	
	# start a map hex highlight animation
	def InitHexHighlight(self, (hx, hy)):
		
		map_hex = GetHexAt(hx, hy)
		
		# do not init if this hex is off the current map viewport
		if not map_hex.IsOnViewport():
			self.anim_finished = True
			return
		
		# get its viewport location
		for (vp_hx, vp_hy) in VP_HEXES:
			if scenario.map_vp[(vp_hx, vp_hy)] == (hx, hy):
				break
		
		self.highlight_vp_hex = (vp_hx, vp_hy)
		self.highlight_timer = time.time()
		self.highlight_click = float(config.getint('ArmCom2', 'animation_speed')) * 0.004
		self.highlight_char = 0
	
	# stop all animations in progress
	def StopAll(self):
		self.rain_active = False
		self.gun_active = False
		self.highlight_psg = None
		self.message_lines = None
		libtcod.console_clear(anim_con)
	
	# update animation statuses and animation console
	def Update(self):
		
		updated_animation = False
		
		# rain effect
		if self.rain_active:
			if time.time() - self.rain_timer >= 0.1:
				updated_animation = True
				self.rain_timer = time.time()
				
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
		
		# gun projectile effect
		if self.gun_active:
			if time.time() - self.gun_timer >= self.gun_click:
				updated_animation = True
				self.gun_timer = time.time()
				
				# remove gun animation if it's reached its end
				if self.gun_location == len(self.gun_line) - 1:
					self.gun_location = 0
					self.gun_active = False
					self.anim_finished = True
				# otherwise, update its position
				else:
					self.gun_location += 1
		
		# AF attack effect
		if self.af_attack_active:
			if time.time() - self.af_attack_timer >= self.af_attack_click:
				updated_animation = True
				self.af_attack_timer = time.time()
				# remove animation if it's reached its end
				if self.af_attack_remaining == 0:
					self.af_attack_active = False
					self.anim_finished = True
				else:
					# randomly choose character positions along line
					self.af_attack_positions = sample(self.af_attack_line, int(len(self.af_attack_line) / 5))
					self.af_attack_remaining -= 1
		
		# map hex highlight
		if self.highlight_vp_hex:
			if time.time() - self.highlight_timer >= self.highlight_click:
				updated_animation = True
				self.highlight_timer =  time.time()
				# remove animation if it's reached its end
				if self.highlight_char == len(HIGHLIGHT_CHARS) - 1:
					self.highlight_vp_hex = None
					self.anim_finished = True
				self.highlight_char += 1
		
		# if we updated any animations, draw all of them to the screen
		if updated_animation:
			libtcod.console_clear(anim_con)
			if self.rain_active:
				for drop in self.raindrops:
					if drop[2] == 1:
						char = '*'
					else:
						char = chr(92)
					libtcod.console_put_char_ex(anim_con, drop[0], drop[1], char,
						libtcod.light_blue, libtcod.black)
			if self.af_attack_active:
				for (x,y) in self.af_attack_positions:
					libtcod.console_put_char_ex(anim_con, x, y, 250,
						libtcod.yellow, libtcod.black)
			if self.gun_active:
				(x,y) = self.gun_line[self.gun_location]
				libtcod.console_put_char_ex(anim_con, x, y, 249, libtcod.white,
					libtcod.black)
			if self.highlight_vp_hex:
				(hx, hy) = self.highlight_vp_hex
				(x,y) = PlotHex(hx, hy)
				x += 1
				y += 1
				for (xm, ym) in HEX_EDGE_TILES:
					libtcod.console_put_char_ex(anim_con, x+xm, y+ym,
						HIGHLIGHT_CHARS[self.highlight_char],
						HEX_HIGHLIGHT_COL, libtcod.black)
		
		return updated_animation


# AI: used to determine actions of non-player-controlled units
class AI:
	def __init__(self, owner):
		self.owner = owner			# the unit to whom this AI instance belongs
	
	# randomly determine an action for this unit and do it
	def DoAction(self):

		# don't do anything if we're going to be removed at end of turn
		if not self.owner.alive: return
		
		# FUTURE: Check for automatic actions based on current situation
		
		# roll for basic action
		# assume that the AI side is taking a defensive attitude
		# FUTURE: different attitudes possible
		d1, d2, roll = Roll2D6()
		
		# doubles 6 or over: no action
		if d1 == d2 and roll >= 6:
			#print 'AI: ' + self.owner.GetName(true_name=True) + ' does nothing'
			return
		
		# enemy in LoS, greater chance of attacking
		for unit in scenario.unit_list:
			if unit.owning_player == 1: continue
			if GetLoS(self.owner.hx, self.owner.hy, unit.hx, unit.hy) > -1:
				#print 'AI: player unit in LoS'
				roll += 2
				break
		
		# try a move action (guns can't move yet)
		if roll <= 4 and not self.owner.gun:
			if self.DoMoveAction():
				return
		
		# try to fire weapons at an enemy target
		if self.DoFireAction():
			return
		
		# final chance to do a move action
		d1, d2, roll = Roll2D6()
		if roll <= 6:
			if self.DoMoveAction():
				return
		
		#print 'AI: ' + self.owner.GetName(true_name=True) + " wasn't able to do any AI actions"
		
	# do a move action
	def DoMoveAction(self):
		
		# FUTURE: add ability to look in radius and choose target destination
		
		# build a list of adjacent hexes
		hex_list = []
		for (hx, hy) in GetAdjacentHexesOnMap(self.owner.hx, self.owner.hy):
			map_hex = GetHexAt(hx, hy)
			# see if a move into this hex is possible
			if self.owner.CheckMoveInto(hx, hy):
				hex_list.append(map_hex)
		
		# no possible move destinations
		if len(hex_list) == 0:
			return False
		
		# sort list by tactical scores
		hex_list.sort(key=lambda x: x.score, reverse=True)
		map_hex = hex_list[0]
		
		# chance of not moving if score is lower than that of current location
		current_hex = GetHexAt(self.owner.hx, self.owner.hy)
		if map_hex.score < current_hex.score:
			d1, d2, roll = Roll2D6()
			if roll > 7:
				return False

		# pivot to face new target hex
		direction = GetDirectionToAdjacent(self.owner.hx, self.owner.hy, map_hex.hx, map_hex.hy)
		if self.owner.facing != direction:
			self.owner.PivotToFace(direction)
		if self.owner.turret_facing is not None:
			if self.owner.turret_facing != direction:
				self.owner.RotateTurret(direction)
		
		# try to do move
		return self.owner.MoveInto(map_hex.hx, map_hex.hy)
	
	# do a fire weapons action
	def DoFireAction(self):
		
		# dummy units can't fire!
		if self.owner.dummy:
			return False
		
		# build a list of possible targets
		# FUTURE: check each weapon separately
		
		target_list = []
		for unit in scenario.unit_list:
			if unit.owning_player == 1: continue
			
			# check range
			distance = GetHexDistance(self.owner.hx, self.owner.hy, unit.hx, unit.hy)
			if distance > self.owner.weapon_list[0].stats['max_range']:
				continue
			
			# check LoS
			if GetLoS(self.owner.hx, self.owner.hy, unit.hx, unit.hy) == -1:
				continue
				
			# check attack odds
			attack_obj = CalcAttack(self.owner, self.owner.weapon_list[0], unit)
			
			# area fire attack against armoured target
			if not attack_obj.to_hit_attack and unit.armour is not None:
				continue
			
			# too difficult to hit/affect
			if attack_obj.final_to_hit < 2:
				continue
			
			target_list.append(unit)
		
		if len(target_list) == 0:
			return False
		
		target = choice(target_list)
		
		# pivot and/or rotate turret if required
		direction = GetDirectionToward(self.owner.hx, self.owner.hy, target.hx,
			target.hy)
		if self.owner.facing != direction:
			self.owner.PivotToFace(direction)
		if self.owner.turret_facing is not None:
			if self.owner.turret_facing != direction:
				self.owner.RotateTurret(direction)
		
		if target == scenario.player_unit:
			text = 'you'
		else:
			text = target.GetName()
		scenario.AddMessage(self.owner.GetName() + ' fires at ' + text + '!', None)
		DrawScreenConsoles()
		
		InitAttack(self.owner, self.owner.weapon_list[0], target)
		
		return True

		

# terrain type: determines effect of different types of map hex terrain
class TerrainType:
	def __init__(self):
		self.console = []
		self.display_name = ''
		self.los_height = 0
		self.base_image = ''
		self.terrain_mod = 0
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
						bg = bg * (1.0 - ELEVATION_SHADE)
					elif elevation == 2:
						bg = bg * (1.0 + ELEVATION_SHADE)
					else:
						bg = bg * (1.0 + (ELEVATION_SHADE * 2.0))
					libtcod.console_set_char_background(self.console[elevation],x,y,bg)


# Attack class, used for attack objects holding scores to use in an attack
# generated by CalcAttack
class Attack:
	def __init__(self, attacker, weapon, target):
		self.attacker = attacker
		self.weapon = weapon
		self.target = target
		
		self.modifiers = []		# list of dice roll modifiers
		self.to_hit_attack = True	# attack is a to-hit attack
		
		# Area Fire variables
		self.base_fp = 0		# base attack firepower
		self.fp_mods = []		# list of firepower modifiers (multipliers)
		self.final_fp = 0		# final firepower
		
		# Point and Area Fire variables
		self.base_to_hit = 0		# base score required to hit
		self.final_to_hit = 0		# final to-hit score required

		# AP variables
		self.location_desc = ''		# description of location hit
		self.base_ap = 0		# base armour-penetration roll required
		self.final_ap = 0		# final "
		
		# final roll variables
		self.critical_hit = False	# roll was an original 2


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
		width = 6 + len(self.option_text)
		if width > 24:
			self.option_text_lines = wrap(self.option_text, 18)
		else:
			self.option_text_lines = [self.option_text]
		# calculate display height
		self.h = len(self.option_text_lines)


# a list of options for the player
class CommandMenu:
	def __init__(self, menu_id):
		self.menu_id = menu_id			# a unique id for this menu
		self.title = ''				# title for when the menu is displayed
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
			if option.key_code == 'Bksp' and key.vk == libtcod.KEY_BACKSPACE:
				return option
			if option.key_code == 'Esc' and key.vk == libtcod.KEY_ESCAPE:
				return option
			if option.key_code == 'End' and key.vk == libtcod.KEY_END:
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
	# FUTURE: add maximum height
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
				libtcod.console_set_default_foreground(console, ACTION_KEY_COL)
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
				libtcod.console_set_default_background(console, TITLE_BG_COL)
				libtcod.console_rect(console, x, y+n, w, menu_option.h, False, libtcod.BKGND_SET)
				libtcod.console_set_default_background(console, original_bg)
				
				if menu_option.desc:
					libtcod.console_set_default_foreground(console, INFO_TEXT_COL)
					lines = wrap(menu_option.desc, w)
					# we re-use n here since we don't need it anymore
					n = 0
					for line in lines:
						libtcod.console_print(console, x, y+max_n+2+n,	line)
						n += 1
				
				break
						
			n += menu_option.h
		libtcod.console_set_default_foreground(console, original_fg)


# a single terrain hex on the game map
# must have elevation and terrain type set before use
class MapHex:
	def __init__(self, hx, hy):
		self.hx = hx
		self.hy = hy
		
		self.score = 0				# tactical score for AI, set by HexMap.GenerateTacticalMap()
		
		self.unit_stack = []			# list of units in this hex
		
		self.elevation = None			# elevation in steps above baseline
		self.terrain_type = None		# pointer to type of terrain in the hex
		
		self.objective = False			# hex is an objective
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
	
	# return True if this hex is currently within the player's map viewport
	def IsOnViewport(self):
		if GetHexDistance(self.hx, self.hy, scenario.player_unit.hx, scenario.player_unit.hy) > 6:
			return False
		return True
	
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
		for psg in scenario.unit_list:
			if psg.hx == self.hx and psg.hy == self.hy:
				return psg.owning_player
		return -1

	# reset pathfinding info for this map hex
	def ClearPathInfo(self):
		self.parent = None
		self.g = 0
		self.h = 0
		self.f = 0
	
	# check to see if the objective in this hex has changed status
	def CheckObjectiveStatus(self, no_message=False):
		
		if not self.objective: return
		
		holding_player = None
		
		# 1+ units here
		# FUTURE: unit must be unbroken to hold objective
		if len(self.unit_stack) > 0:
			holding_player = self.unit_stack[0].owning_player
		
		# not held, and no unit here to hold it: no change
		if self.held_by is None and holding_player is None:
			return
		
		# held by player that is here: no change
		if self.held_by == holding_player:
			return
		
		# not currently held but doesn't have to be: no change
		if holding_player is None and self.objective != 'Capture and Hold':
			return
		
		# change in status: lost control or gained control
		self.held_by = holding_player
		
		UpdateVPConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		
		if no_message: return
		
		if holding_player is None:
			text = 'Objective control lost'
		else:
			if holding_player == 0:
				text = 'You have captured an objective!'
			else:
				text = 'The enemy has captured an objective.'
			
		scenario.AddMessage(text, (self.hx, self.hy))


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
	
	# for AI side, generate a Dijkstra map of tactical scores for each map hex
	# based on terrain, visibility, and proximity to objectives
	def GenerateTacticalMap(self):
		
		start_time = time.time()
		
		for (hx, hy) in self.hexes:
			
			map_hex = self.hexes[(hx, hy)]
			
			# clear any old score
			map_hex.score = 0
			
			# skip water hexes
			if map_hex.terrain_type.water: continue
		
			# calculate new score
			map_hex.score = 1
			
			# FUTURE: visible hexes
			#hex_list = GetHexesWithin(hx, hy, 6)
			#for (hx2, hy2) in hex_list:
				
			#	if (hx2, hy2) == (hx, hy): continue
				
			#	direction = GetDirectionToward(hx, hy, hx2, hy2)
			#	if not scenario.player_direction - 1 <= direction <= scenario.player_direction + 1:
			#		continue
				
			#	if GetLoS(hx, hy, hx2, hy2) > 0:
			#		map_hex.score += 1
				
				# added this to stop window from freezing
			#	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			#		key, mouse)
				# FUTURE: update a progress bar on loading screen?
			
			# terrain in hex
			if map_hex.terrain_type.terrain_mod > 0:
				map_hex.score = map_hex.score * map_hex.terrain_type.terrain_mod
			
			if map_hex.objective:
				map_hex.score = map_hex.score * 20
				continue
			
			# FUTURE: proximity to objectives
			#for (hx2, hy2) in hex_list:
			#	map_hex2 = GetHexAt(hx2, hy2)
			#	if not map_hex2.objective: continue
			#	distance = GetHexDistance(hx, hy, hx2, hy2)
			#	map_hex.score = map_hex.score * (8 - distance)
		
		time_taken = round((time.time() - start_time), 1)
		print 'Generated tactical scores for map hexes in ' + str(time_taken) + ' seconds.'
	
	# place an objective in the given hex
	def AddObjectiveAt(self, hx, hy, objective_type):
		map_hex = GetHexAt(hx, hy)
		map_hex.objective = objective_type
		scenario.objective_hexes.append(map_hex)
	
	# calculate field of view for human player
	def CalcFoV(self):
		
		# debug mode
		if VIEW_ALL:
			for (hx, hy) in scenario.hex_map.hexes:
				scenario.hex_map.hexes[(hx, hy)].vis_to_player = True
			return
		
		# set all hexes to not visible to start
		for (hx, hy) in scenario.hex_map.hexes:
			scenario.hex_map.hexes[(hx, hy)].vis_to_player = False
		
		# no player unit
		if not scenario.player_unit:
			return
		
		# set hex location of player unit to visible
		scenario.hex_map.hexes[(scenario.player_unit.hx, scenario.player_unit.hy)].vis_to_player = True
		
		# start field of view calculations
		#start_time = time.time()
		
		# build list of hexes to check based on crew who are able to spot
		hex_list = []

		for crew_position in scenario.player_unit.crew_positions:
			if crew_position.crewman is None: continue
			# crewman must not being doing another action to spot
			if crew_position.crewman.action is not None: continue
			
			# visible_hextants is a slice of the original since we want a local copy and
			#   don't want to change the original values
			if crew_position.hatch is None:
				visible_hextants = crew_position.closed_visible[:]
				max_distance = MAX_BU_LOS_DISTANCE
			else:
				if crew_position.hatch == 'Closed':
					visible_hextants = crew_position.closed_visible[:]
					max_distance = MAX_BU_LOS_DISTANCE
				else:
					visible_hextants = crew_position.open_visible[:]
					max_distance = MAX_LOS_DISTANCE
			
			# rotate visible hextants based on current turret/hull facing
			if crew_position.turret:
				direction = scenario.player_unit.turret_facing
			else:
				direction = scenario.player_unit.facing
			if direction != 0:
				for i, hextant in enumerate(visible_hextants):
					visible_hextants[i] = ConstrainDir(hextant + direction)
					
			
			# go through hexes in each hextant and add to spotting list if within max distance
			for hextant in visible_hextants:
				for (hxm, hym) in HEXTANTS[hextant]:
					
					hx = scenario.player_unit.hx + hxm
					hy = scenario.player_unit.hy + hym
					
					# check that it's on the map
					if (hx, hy) not in scenario.hex_map.hexes:
						continue
					
					# check that it's within range
					if GetHexDistance(0, 0, hxm, hym) > max_distance:
						continue
					
					if (hx, hy) not in hex_list:
						hex_list.append((hx, hy))
		
		# raycast from player unit to each visible map hex
		for (hx, hy) in hex_list:
			# skip already visible hexes
			if scenario.hex_map.hexes[(hx, hy)].vis_to_player: continue
			
			if GetLoS(scenario.player_unit.hx, scenario.player_unit.hy, hx, hy) != -1:
				scenario.hex_map.hexes[(hx, hy)].vis_to_player = True
		
		#end_time = time.time()
		#time_taken = round((end_time - start_time) * 1000, 3) 
		#print 'FoV raycasting finished, took ' + str(time_taken) + ' ms.'
		
	# set a given hex on the campaign day map to a terrain type
	def SetHexTerrainType(self, hx, hy, terrain_type):
		self.hexes[(hx,hy)].terrain_type = terrain_type


# holds information about a scenario in progress
# on creation, also set the map size
class Scenario:
	def __init__(self, map_w, map_h):
		
		self.game_version = VERSION		# record game version for compatibility
		
		self.map_vp = {}			# dictionary of map viewport hexes and
							#   their corresponding map hexes
		
		self.map_index = {}			# dictionary of screen console locations and
							#   their corresponding map hexes
		
		self.anim = AnimHandler()		# animation handler
		
		self.name = ''				# scenario name
		self.battlefront = ''			# text description of battlefront
		self.year = 0				# current calendar year
		self.month = 0				# current calendar month
		self.hour = 0				# current time
		self.minute = 0
		
		self.hour_limit = 0			# time at which scenario ends
		self.minute_limit = 0
		self.time_limit_winner = 1		# player who wins if time limit is reached
		
		self.unit_list = []			# list of all units in play
		self.active_unit = None			# currently active unit
		self.player_unit = None			# pointer to player-controlled unit
		
		self.messages = []			# log of game messages
		
		self.selected_crew_position = None	# selected crew position in player unit
		self.selected_weapon = None		# currently active weapon for player
		self.player_target = None		# unit currently being targeted by player unit
		
		self.player_direction = 3		# direction of player-friendly forces
		self.enemy_direction = 0		# direction of enemy forces
		
		# game state flags
		self.display_los = False		# display a LoS from the player unit to a target
		
		# scenario end variables
		self.winner = None			# number of player that has won the scenario,
							#   None if no winner yet
		self.end_text = ''			# description of how scenario ended
		
		self.cmd_menu = CommandMenu('scenario_menu')		# current command menu for player
		self.active_cmd_menu = None				# currently active command menu
		
		self.messages = []			# game message log
		
		# create the hex map
		self.hex_map = HexMap(map_w, map_h)
		self.objective_hexes = []			# list of objective hexes
	
	# load unit portraits for all active units into a dictionary
	def LoadUnitPortraits(self):
		for unit in self.unit_list:
			if unit.portrait is None: continue
			if unit.unit_id not in unit_portraits:
				unit_portraits[unit.unit_id] = LoadXP(unit.portrait)
		print 'Loaded unit portraits'
	
	# return the FP of an HE hit from a given calibre of gun
	def GetGunHEFP(self, calibre):
		
		if calibre <= 60:
			return 8
		if calibre <= 57:
			return 7
		if calibre <= 50:
			return 6
		if calibre <= 45:
			return 5
		if calibre <= 37:
			return 4
		if calibre <= 30:
			return 2
		return 1
	
	
	# spawn a given enemy unit into the map at a random location
	def SpawnEnemy(self, unit_id, morale_lvl, skill_lvl, dummy=False):
		new_unit = Unit(unit_id)
		new_unit.owning_player = 1
		new_unit.facing = self.player_direction
		if new_unit.turret_facing is not None:
			new_unit.turret_facing = self.player_direction
		new_unit.morale_lvl = morale_lvl
		new_unit.skill_lvl = skill_lvl
		new_unit.dummy = dummy			# used to set dummy AI units
		
		# try to find a suitable place to spawn this unit
		for tries in range(300):
			(hx, hy) = choice(scenario.hex_map.hexes.keys())
			map_hex = GetHexAt(hx, hy)
			if map_hex.terrain_type.water: continue
			if len(map_hex.unit_stack) > HEX_STACK_LIMIT: continue
			if len(map_hex.unit_stack) > 0:
				if map_hex.unit_stack[0].owning_player != 1: continue
			if self.player_unit is not None:
				distance = GetHexDistance(hx, hy, self.player_unit.hx, self.player_unit.hy)
				if distance <= 6: continue
			
			# place unit here
			new_unit.hx = hx
			new_unit.hy = hy
			map_hex.unit_stack.append(new_unit)
			break
		self.unit_list.append(new_unit)
	
	# do the automatic actions to start a new game turn
	def StartNewTurn(self):
		
		# end of old turn
		
		# check objective status change
		for map_hex in self.objective_hexes:
			map_hex.CheckObjectiveStatus()
		UpdateObjectiveConsole()
		
		# check for scenario end
		self.CheckForEnd()
		if self.winner is not None:
			return
		
		# advance the game clock
		self.AdvanceClock()
	
	# calculate the likely effectiveness of a fire attack between two units
	# returns (bool, int), where bool is true if a turret rotation or facing change would
	#   if move_allowed / pivot_allowed are false, then turret rotation / hull pivot are
	#   not permitted before the attack
	#   if returned value == -1, attack is not possible, and the reason is returned as desc
	def GetAttackScore(self, attacker, weapon, target, rotate_allowed=True, pivot_allowed=True):
		
		# weapon has already fired
		if weapon.fired:
			return (-1, 'Cannot fire this weapon group again this turn')
		
		# check range
		if GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy) > weapon.stats['max_range']:
			return (-1, 'Target beyond maximum weapon range')
		
		# gun specific checks
		if weapon.weapon_type == 'gun':
			if weapon.stats['loaded_ammo'] == 'AP':
				if not target.known:
					return (-1, 'AP attacks possible on known targets only.')
				if target.infantry:
					return (-1, 'AP attacks have no effect on infantry')	
		
		# see if target must current be in weapon arc
		arc_check = False
		if weapon.stats['mount'] == 'turret':
			if not rotate_allowed and not pivot_allowed:
				arc_check = True
		else:
			if not pivot_allowed:
				arc_check = True
		if arc_check:
			# check weapon arc
				
			# calculate target location as if attacker is in 0,0 and facing 0
			hx = target.hx - attacker.hx
			hy = target.hy - attacker.hy
			
			if weapon.stats['mount'] == 'turret':
				(hx, hy) = RotateHex(hx, hy, ConstrainDir(0 - attacker.turret_facing))
			else:
				(hx, hy) = RotateHex(hx, hy, ConstrainDir(0 - attacker.facing))
			
			in_arc = True
			if hx == 0 and hy >= 0:
				in_arc = False
			elif hx == -1 and hy >= 0:
				in_arc = False
			elif hx == 1 and hy >= -1:
				in_arc = False
			elif hx == -2 and hy >= -1:
				in_arc = False
			elif hx == 2 and hy >= -3:
				in_arc = False
			elif hx == -3 and hy >= -2:
				in_arc = False
			elif hx == 3 and hy >= -5:
				in_arc = False
			elif hx <= -4 or hx >= 4:
				in_arc = False
			
			if not in_arc:
				return (-1, 'Target outside weapon firing arc')
			 
		# FUTURE: calculate a better score for this attack
		return (1, '')
		
	# randomize the order of units in unit_list to reflect activation order in each turn
	def GenerateUnitOrder(self):
		shuffle(self.unit_list)
	
	# activate the next unit in the list, or start a new turn
	def ActivateNextUnit(self):
		
		# do post-activation actions for currently active unit
		self.active_unit.DoPostActivation()
		
		# check for extra turn for currently activated unit
		if self.active_unit.alive and self.active_unit.extra_turns > 0:
			self.active_unit.extra_turns -= 1
			self.active_unit.DoPreActivation()
			scenario.BuildCmdMenu()
			# save the game if the player has been activated
			if self.active_unit == self.player_unit:
				SaveGame()
			return
		
		unit_activated = False
		while not unit_activated:
		
			# get index number of previously active unit
			i = self.unit_list.index(self.active_unit)
			
			# start a new turn or activate next unit in list
			if i == len(self.unit_list) - 1:
				self.StartNewTurn()
				
				# scenario is over
				if self.winner is not None:
					return
				
				# activate first unit in list
				self.active_unit = self.unit_list[0]
				
			else:
				self.active_unit = self.unit_list[i+1]
			
			# skip dead units
			if not self.active_unit.alive: continue
			
			# check for missed turn
			if self.active_unit.extra_turns < 0:
				self.active_unit.extra_turns += 1
				continue
			
			# do pre-activation actions for newly activated unit
			self.active_unit.DoPreActivation()
			scenario.BuildCmdMenu()
			
			# save the game if the player has been activated
			if self.active_unit == self.player_unit:
				SaveGame()
			
			unit_activated = True
		
	# add a new message to the log, and display it on the current message console
	def AddMessage(self, text, highlight_hex):
		self.messages.append(text)
		UpdateMsgConsole()
		# we do this so as not to mess up the attack console being displayed
		libtcod.console_blit(msg_con, 0, 0, 0, 0, con, 27, 58)
		if highlight_hex is not None:
			scenario.anim.InitHexHighlight(highlight_hex)
			WaitForAnimation()
	
	# set up map viewport hexes based on current player tank position and facing
	def SetVPHexes(self):
		for (hx, hy) in VP_HEXES:
			map_hx = hx + scenario.player_unit.hx
			map_hy = hy + scenario.player_unit.hy
			# rotate based on player tank facing
			(hx, hy) = RotateHex(hx, hy, ConstrainDir(0 - scenario.player_unit.facing))
			self.map_vp[(hx, hy)] = (map_hx, map_hy)
	
	# select next possible player target for shooting
	def SelectNextPlayerTarget(self):
		
		# build a list of possible targets
		target_list = []
		for unit in scenario.unit_list:
			if unit.owning_player == 0: continue
			if not unit.alive: continue
			map_hex = GetHexAt(unit.hx, unit.hy)
			if not map_hex.vis_to_player: continue
			target_list.append(unit)
		
		# old target no longer allowed
		if self.player_target is not None:
			if self.player_target not in target_list:
				self.player_target = None
		
		# no possible targets
		if len(target_list) == 0:
			scenario.display_los = False
			return
		
		# make sure that los display is on
		scenario.display_los = True
		
		# no target selected yet, select the first one
		if self.player_target is None:
			self.player_target = target_list[0]
		
		# last target in list selected, select the first one
		elif self.player_target == target_list[-1]:
			self.player_target = target_list[0]
		
		# select next target in list
		else:
			n = target_list.index(self.player_target)
			self.player_target = target_list[n+1]
		
		# move target to top of unuit stack
		# move to top of hex stack
		map_hex = GetHexAt(self.player_target.hx, self.player_target.hy)
		if len(map_hex.unit_stack) > 1:
			self.player_target.MoveToTopOfStack(map_hex)
		scenario.AddMessage('Now targeting ' + self.player_target.GetName(), None)
	
	# check for scenario end and set up data if so
	def CheckForEnd(self):
		
		# player has died
		if not self.player_unit.alive:
			self.winner = 1
			self.end_text = 'Your tank has been destroyed.'
			return
		
		# objective capture win
		objective_win = True
		for map_hex in scenario.objective_hexes:
			if map_hex.held_by is None:
				objective_win = False
				break
			if map_hex.held_by == 1:
				objective_win = False
				break
		if objective_win:
			self.winner = 0
			self.end_text = 'You have captured all the objectives!'
			return

		# time limit has been reached
		if self.hour == self.hour_limit and self.minute >= self.minute_limit:
			self.winner = 1
			self.end_text = 'You have run out of time to complete the mission.'
			return
		
	
	# display a screen of info about a completed scenario
	def DisplayEndScreen(self):
		
		# stop any animations
		scenario.anim.StopAll()
		
		# darken the screen background
		libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
		
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
	
	# end of turn, advance the scenario clock by one turn
	def AdvanceClock(self):
		self.minute += 2
		if self.minute >= 60:
			self.minute -= 60
			self.hour += 1
		UpdateScenInfoConsole()
		self.AddMessage('Time is now: ' + str(scenario.hour) + ':' + 
			str(scenario.minute).zfill(2), None)

	# rebuild a list of commands for the command menu based on current active menu
	def BuildCmdMenu(self):
		
		# clear any existing command menu
		self.cmd_menu.Clear()
		
		# don't display anything if human player is not active
		if scenario.active_unit.owning_player == 1:
			UpdateCmdConsole()
			return
		
		# root menu
		if self.active_cmd_menu == 'root':
			self.cmd_menu.title = 'Commands'
			menu_option = self.cmd_menu.AddOption('command_menu', '1', 'Command')
			menu_option.inactive = True
			menu_option = self.cmd_menu.AddOption('crew_menu', '2', 'Crew')
			menu_option.inactive = True
			self.cmd_menu.AddOption('movement_menu', '3', 'Movement')
			self.cmd_menu.AddOption('weapons_menu', '4', 'Weapons')
		
		# crew menu (not used yet)
		elif self.active_cmd_menu == 'crew':
			self.cmd_menu.title = 'Tank Crew'
			# generate one command per crew position
			n = 0
			for crew_position in scenario.player_unit.crew_positions:
				cmd = 'crewposition_' + str(n)
				menu_option = self.cmd_menu.AddOption(cmd, str(n+1), crew_position.name)
				if crew_position.crewman is None:
					text = '[Position empty]'
					menu_option.inactive = True
				else:
					text = 'Actions for ' + crew_position.crewman.GetName()
				menu_option.desc = text
				n += 1
			
			self.cmd_menu.AddOption('return_to_root', 'Bksp', 'Root Menu',
				desc='Return to root command menu')
		
		# movement menu
		elif self.active_cmd_menu == 'movement':
			self.cmd_menu.title = 'Movement'
			
			self.cmd_menu.AddOption('rotate_turret_cc', 'Q', 'Turret C/clockwise')
			self.cmd_menu.AddOption('rotate_turret_cw', 'E', 'Turret Clockwise')
			self.cmd_menu.AddOption('pivot_hull_port', 'A', 'Pivot to Port')
			self.cmd_menu.AddOption('pivot_hull_stb', 'D', 'Pivot to Starboard')
			
			menu_option = self.cmd_menu.AddOption('move_forward', 'W', 'Forward')
			(hx, hy) = GetAdjacentHex(scenario.player_unit.hx,
				scenario.player_unit.hy, scenario.player_unit.facing)
			if not scenario.player_unit.CheckMoveInto(hx, hy):
				menu_option.inactive = True
			
			menu_option = self.cmd_menu.AddOption('move_backward', 'S', 'Backward')
			(hx, hy) = GetAdjacentHex(scenario.player_unit.hx,
				scenario.player_unit.hy,
				CombineDirs(scenario.player_unit.facing, 3))
			if not scenario.player_unit.CheckMoveInto(hx, hy):
				menu_option.inactive = True
			
			self.cmd_menu.AddOption('return_to_root', 'Bksp', 'Root Menu',
				desc='Return to root command menu')
			
		# weapons menu
		elif self.active_cmd_menu == 'weapons':
			
			self.cmd_menu.title = 'Weapons'
			
			# list all weapon systems
			WEAPON_KEYS = ['Q', 'W', 'E', 'R', 'T', 'Y']
			n = 0
			for weapon in scenario.player_unit.weapon_list:
				cmd = 'weapon_menu_' + str(n)
				cmd_key = WEAPON_KEYS[n]
				self.cmd_menu.AddOption(cmd, cmd_key, weapon.GetName(), 
					desc='Actions for this weapon')
				n += 1
			menu_option = self.cmd_menu.AddOption('return_to_root', 'Bksp',
				'Root Menu', desc='Return to root command menu')
			# can't return to root menu if already fired
			if scenario.player_unit.fired:
				menu_option.inactive = True
				menu_option.desc = 'You have already fired a weapon this action'
		
		# menu for a specific weapon
		elif self.active_cmd_menu[:12] == 'weapon_menu_':
			
			self.cmd_menu.title = scenario.selected_weapon.GetName()
			
			self.cmd_menu.AddOption('next_target', 'T', 'Next Target')
			
			# see if we can fire this weapon at current target
			menu_option = self.cmd_menu.AddOption('fire_weapon', 'F', 'Fire')
			if scenario.player_target is None:
				menu_option.inactive = True
				menu_option.desc = 'No target selected'
			else:
				(score, desc) = scenario.GetAttackScore(scenario.player_unit,
					scenario.selected_weapon, scenario.player_target,
					rotate_allowed=False, pivot_allowed=False)
				if score == -1:
					menu_option.inactive = True
					menu_option.desc = desc
				else:
					menu_option.desc = 'Fire at ' + scenario.player_target.GetName()
			
			# load ammo into an empty gun or switch out loaded ammo for different type
			if scenario.selected_weapon.weapon_type == 'gun':
			
				menu_option = self.cmd_menu.AddOption('cycle_weapon_load', 'L', 'Change Gun Load')
				
				if scenario.selected_weapon.stats['loaded_ammo'] is None:
					# no shell loaded
					menu_option.desc = 'Load a shell into the gun'
				elif len(scenario.selected_weapon.stats['ammo_types']) > 1:
					# can switch out for different type
					menu_option.desc = ('Switch loaded shell for different ammo type. ' +
						'If weapon is fired this turn, RoF is not possible.')
				else:
					# command not allowed
					self.cmd_menu.remove(menu_option)
				# TODO: check if loader can do this instant action
			
				# toggle use of ready rack to reload
				if scenario.selected_weapon.stats['use_ready_rack'] is not None:
					menu_option = self.cmd_menu.AddOption('toggle_rr', 'R', 'Toggle Ready Rack')
					if scenario.selected_weapon.stats['use_ready_rack']:
						text = "Don't use ready rack to reload"
					else:
						text = 'Use ready rack to reload'
					menu_option.desc = text
				
				# cycle type of ammo to use to reload
				if len(scenario.selected_weapon.stats['ammo_types']) > 1:
					menu_option = self.cmd_menu.AddOption('cycle_weapon_reload',
						'A', 'Cycle reload ammo',
						desc='Cycle the type of ammo to use when reloading the gun')
			
			self.cmd_menu.AddOption('next_weapon', 'Tab', 'Next weapon',
				desc='Quickly switch to next weapon')
			self.cmd_menu.AddOption('return_to_weapons', 'Bksp',
				'Return to Weapons', desc='Return to main Weapons menu')

		# all menus get this command
		self.cmd_menu.AddOption('end_action', 'Space', 'End Action',
			desc='End your current activation')
		
		UpdateCmdConsole()



##########################################################################################
#                                     General Functions                                  #
##########################################################################################

# retrive the text of an in-game text from the languages data based on current game language
def GetMsg(msg_id):
	return lang_dict[msg_id].decode('utf8').encode('IBM850')


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
		if item.find('terrain_mod') is not None:
			new_type.terrain_mod = int(item.find('terrain_mod').text)
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
	# load unit portraits
	scenario.LoadUnitPortraits()


# remove a saved game, either because the scenario is over or the player abandoned it
def EraseGame():
	os.remove('savegame')


# calculate an attack
def CalcAttack(attacker, weapon, target):
	
	# create a new attack object
	attack_obj = Attack(attacker, weapon, target)
	
	# get distance to target
	distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
	
	# determine whether this is a to-hit or a FP attack
	to_hit_attack = False
	if weapon.weapon_type == 'gun':
		to_hit_attack = True
	
	######################
	#   To-Hit Attacks   #
	######################
	
	if to_hit_attack:
	
		# calculate base to-hit roll required
		if distance <= 1:
			column = 0
		else:
			column = distance - 1
		to_hit_list = BASE_TO_HIT[column]
		
		if target.vehicle:
			attack_obj.base_to_hit = to_hit_list[0]
		else:
			attack_obj.base_to_hit = to_hit_list[1]
		
		# calculate dice roll modifiers
		if attacker.moved_last_action:
			attack_obj.modifiers.append(('Moved Last Action', -2))

		if attacker.pinned:
			attack_obj.modifiers.append(('Attacker Pinned', -2))
		
		if attacker.acquired_target is not None:
			(ac_target, ac_level) = attacker.acquired_target
			if ac_target == target:
				attack_obj.modifiers.append(('Acquired Target', int(ac_level)))
		
		# Long Range gun Modifiers
		if weapon.stats['long_range'] == 'S':
			if distance >= 4:
				attack_obj.modifiers.append(('Low Muzzle Velocity', -1))
		elif weapon.stats['long_range'] == 'L':
			if 4 <= distance <= 6:
				attack_obj.modifiers.append(('L Weapon', 1))
		elif weapon.stats['long_range'] == 'LL':
			if 4 <= distance <= 5:
				attack_obj.modifiers.append(('LL Weapon', 1))
			elif distance == 6:
				attack_obj.modifiers.append(('LL Weapon', 2))
		
		# calibre range modifiers
		if weapon.stats['calibre'] <= 40:
			if 4 <= distance <= 6:
				attack_obj.modifiers.append(('Small Calibre', -1))
		elif weapon.stats['calibre'] <= 57:
			if 4 <= distance <= 5:
				attack_obj.modifiers.append(('Medium Calibre', -1))
			elif distance == 6:
				attack_obj.modifiers.append(('Medium Calibre', -2))
		
		# vehicle targets
		if target.vehicle:
			if target.moved:
				attack_obj.modifiers.append(('Target vehicle moved', -2))
		
			# size class
			if target.size_class != 'Normal':
				if target.size_class == 'Small':
					attack_obj.modifiers.append(('Small Target', -1))
				elif target.size_class == 'Very Small':
					attack_obj.modifiers.append(('Very Small Target', -2))
		
		# LoS terrain modifier
		los = GetLoS(attacker.hx, attacker.hy, target.hx, target.hy)
		if los > 0:
			attack_obj.modifiers.append(('Terrain', 0-los))
		
		# apply modifiers to calculate final to-hit score required 
		attack_obj.final_to_hit = attack_obj.base_to_hit
		for (text, mod) in attack_obj.modifiers:
			attack_obj.final_to_hit += mod
		
		# normalize final to-hit required
		# FUTURE: if < 2 required, attack not possible
		if attack_obj.final_to_hit > 11:
			attack_obj.final_to_hit = 11

	#####################
	# Area Fire Attacks #
	#####################

	else:
		attack_obj.to_hit_attack = False
		
		# get base firepower of weapon used
		attack_obj.base_fp = weapon.stats['fp']
		
		# calculate fp modifiers (multipliers)
		if attacker.moved_last_action:
			attack_obj.fp_mods.append(('Moved Last Action', '/2'))
		
		if attacker.pinned:
			attack_obj.fp_mods.append(('Pinned', '/2'))
		
		if not target.known:
			attack_obj.fp_mods.append(('Target Concealed', '/2'))
		
		# calculate final fp
		float_final_fp = float(attack_obj.base_fp)
		for (desc, mod) in attack_obj.fp_mods:
			if mod == '/2':
				float_final_fp = float_final_fp * 0.5
			elif mod == '*2':
				float_final_fp = float_final_fp * 2.0
		
		# round down and convert back to int
		attack_obj.final_fp = int(floor(float_final_fp))
		
		# FUTURE: how to handle attacks of FP 0?
		if attack_obj.final_fp < 1:
			attack_obj.final_fp = 1
		
		# get base score to equal/beat
		for (chart_fp, inf_score, veh_score) in reversed(AF_CHART):
			if chart_fp <= attack_obj.final_fp:
				if attack_obj.target.infantry or attack_obj.target.gun:
					attack_obj.base_to_hit = inf_score
				else:
					attack_obj.base_to_hit = veh_score
				break
		
		# calculate dice roll modifiers
		# FUTURE: if target is not known, don't apply any target-specific modifiers?
		
		# LoS terrain modifier
		los = GetLoS(attacker.hx, attacker.hy, target.hx, target.hy)
		if los > 0:
			attack_obj.modifiers.append(('Terrain', 0-los))
		
		# total up modifiers
		total_modifiers = 0
		for (desc, mod) in attack_obj.modifiers:
			total_modifiers += mod
		
		# get final score to equal/beat
		attack_obj.final_to_hit = attack_obj.base_to_hit
		for (text, mod) in attack_obj.modifiers:
			attack_obj.final_to_hit += mod
		
		# normalize final score required
		# FUTURE: if < 2 required, attack not possible
		if attack_obj.final_to_hit > 11:
			attack_obj.final_to_hit = 11
		
	return attack_obj


# calculate a armour penetration roll
def CalcAPRoll(attack_obj):
	
	# determine location hit on target
	if libtcod.random_get_int(0, 1, 6) <= 4:
		location = 'Hull'
		turret_facing = False
	else:
		location = 'Turret'
		turret_facing = True
	
	facing = GetFacing(attack_obj.attacker, attack_obj.target, turret_facing=turret_facing)
	hit_location = (location + '_' + facing).lower()
	
	# generate a text description of location hit
	if attack_obj.target.turret_facing is None:
		location = 'Upper Hull'
	attack_obj.location_desc = location + ' ' + facing
	
	# calculate base AP score required
	if attack_obj.weapon.name == 'AT Rifle':
		base_ap = 5
	else:
		gun_rating = str(attack_obj.weapon.stats['calibre']) + attack_obj.weapon.stats['long_range']
		if gun_rating == '37L':
			base_ap = 9
		elif gun_rating in ['37', '47S']:
			base_ap = 8
		elif gun_rating == '20L':
			base_ap = 6
	
	# apply critical hit if any
	if attack_obj.critical_hit:
		base_ap = base_ap * 2
	
	# calculate modifiers
	modifiers = []
	
	# calibre/range modifier
	distance = GetHexDistance(attack_obj.attacker.hx, attack_obj.attacker.hy,
		attack_obj.target.hx, attack_obj.target.hy)
	if distance <= 1:
		if attack_obj.weapon.stats['calibre'] <= 57:
			modifiers.append(('Close Range', 1))
	elif distance == 5:
		modifiers.append(('800 m. Range', -1))
	elif distance == 6:
		if attack_obj.weapon.stats['calibre'] < 65:
			modifiers.append(('960 m. Range', -2))
		else:
			modifiers.append(('960 m. Range', -1))
	
	# target armour modifier
	if attack_obj.target.armour:
		target_armour = attack_obj.target.armour[hit_location]
		if target_armour > 0:
			modifiers.append(('Target Armour', 0-target_armour))
	
	# calculate final AP score required
	final_ap = base_ap
	for (text, mod) in modifiers:
		final_ap += mod
	
	return (base_ap, modifiers, final_ap)


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
	for psg in scenario.unit_list:
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
	direction = dir1 + dir2
	return ConstrainDir(direction)


# plot the center of a given in-game hex on the viewport console
# 0,0 appears in centre of vp console
def PlotHex(hx, hy):
	x = hx*4 + 23
	y = (hy*4) + (hx*2) + 23
	return (x+4,y+3)


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

# returns which hexspine hx,hy2 is along if the two hexes are along a hexspine
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


# returns a path from one hex to another, avoiding impassible and difficult terrain
# based on function from ArmCom 1, which was based on:
# http://stackoverflow.com/questions/4159331/python-speed-up-an-a-star-pathfinding-algorithm
# http://www.policyalmanac.org/games/aStarTutorial.htm
def GetHexPath(hx1, hy1, hx2, hy2, psg=None, road_path=False):
	
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
	#last_good_node = None
	
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
			
			# calculate movement cost based on psg type
			if psg:
				# can't move into an occupied location unless it's our destination
				if node != node2 and node.IsOccupied() != -1:
					continue
				# FUTURE: calculate cost based on odds of extra/missed turn
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
	wait_time = wait_time * 0.01
	start_time = time.time()
	while time.time() - start_time < wait_time:
	
		# added this to avoid the spinning wheel of death in Windows
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			key, mouse)
		if libtcod.console_is_window_closed(): sys.exit()
		
		# check for animation update
		if scenario.anim.Update():
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_blit(anim_con, 0, 0, 0, 0, 0, 26, 3, 1.0, 0.0)
			
		libtcod.console_flush()


# function to update animations, used while waiting for a particular animation to finish
def WaitForAnimation():
	while not scenario.anim.anim_finished:
		# added this to avoid the spinning wheel of death in Windows
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			key, mouse)
		if libtcod.console_is_window_closed(): sys.exit()
		
		# check for animation update
		if scenario.anim.Update():
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_blit(anim_con, 0, 0, 0, 0, 0, 26, 3, 1.0, 0.0)
			
		libtcod.console_flush()
	# reset flag before returning
	scenario.anim.anim_finished = False


# wait for player to press enter before continuing
# option to allow backspace pressed instead, returns True if so 
def WaitForEnter(allow_cancel=False):
	end_pause = False
	cancel = False
	while not end_pause:
		# get input from user
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			key, mouse)
		
		# emergency exit from game
		if libtcod.console_is_window_closed(): sys.exit()
		
		elif key.vk == libtcod.KEY_ENTER: 
			end_pause = True
		
		elif key.vk == libtcod.KEY_BACKSPACE and allow_cancel:
			end_pause = True
			cancel = True
		
		# check for animation update
		if scenario.anim.Update():
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_blit(anim_con, 0, 0, 0, 0, 0, 26, 3, 1.0, 0.0)
		
		# refresh the screen
		libtcod.console_flush()
	
	if allow_cancel and cancel:
		return True
	return False


# get a confirmation from the player that they really want to do this
# can also display a warning/error without asking for yes/no input
def GetConfirmation(text, warning_only=False):
	
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
	
	if warning_only:
		libtcod.console_set_default_foreground(0, HIGHLIGHT_COLOR)
		libtcod.console_print_ex(0, WINDOW_XM-2, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'Enter')
		libtcod.console_set_default_foreground(0, libtcod.white)
		libtcod.console_print(0, WINDOW_XM, y, 'Continue')
	else:
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
		
		if warning_only:
			if key.vk == libtcod.KEY_ENTER:
				return
		else:
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


# returns -1 if there is no clear LoS from hx1, hy1 to hx2, hy2, otherwise returns the
# total terrain modifier for the line
def GetLoS(hx1, hy1, hx2, hy2):
	
	# handle the easy cases first
	
	# too far away
	if GetHexDistance(hx1, hy1, hx2, hy2) > MAX_LOS_DISTANCE:
		return -1
	
	# same hex and adjacent hex
	if hx1 == hx2 and hy1 == hy2:
		return scenario.hex_map.hexes[(hx, hy)].terrain_type.terrain_mod
	distance = GetHexDistance(hx1, hy1, hx2, hy2)
	if distance == 1:
		return scenario.hex_map.hexes[(hx2, hy2)].terrain_type.terrain_mod
	
	# store info about the starting and ending hexes for this LoS
	start_elevation = float(GetHexAt(hx1, hy1).elevation)
	end_elevation = float(GetHexAt(hx2, hy2).elevation)
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
	
	# now that we have the list of hexes along the LoS, run through them, and if an
	#   intervening hex elevation blocks the line, we can return -1
	
	# if a terrain feature intersects the line, we add its effect to the total LoS hinderance
	total_mod = 0
	
	# we need a few variables to temporarily store information about the first hex of
	#   a hex pair, to compare it with the second of the pair
	hexpair_floor_slope = None
	hexpair_terrain_slope = None
	hexpair_terrain_mod = None
	
	for (hx, hy) in hex_list:
		
		# hex is off map
		if (hx, hy) not in scenario.hex_map.hexes: continue
		
		# hex is beyond the maximum LoS distance
		if GetHexDistance(hx1, hy1, hx, hy) > MAX_LOS_DISTANCE: return -1
		
		map_hex = scenario.hex_map.hexes[(hx, hy)]
		elevation = (float(map_hex.elevation) - start_elevation) * ELEVATION_M
		distance = float(GetHexDistance(hx1, hy1, hx, hy))
		floor_slope = elevation / (distance * 160.0)
		terrain_slope = (elevation + float(map_hex.terrain_type.los_height)) / (distance * 160.0)
		terrain_mod = map_hex.terrain_type.terrain_mod
		
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
				return -1

	return total_mod


# get the bearing from psg1 to psg2, rotated for psg1's facing
def GetRelativeBearing(psg1, psg2):
	(x1, y1) = PlotHex(psg1.hx, psg1.hy)
	(x2, y2) = PlotHex(psg2.hx, psg2.hy)
	bearing = GetBearing(x1, y1, x2, y2)
	return RectifyHeading(bearing - (psg1.facing * 60))


# get the relative facing of one PSG from the pov of another PSG
# psg1 is the observer, psg2 is being observed
def GetFacing(attacker, target, turret_facing=False):
	bearing = GetRelativeBearing(target, attacker)
	if turret_facing and target.turret_facing is not None:
		bearing = RectifyHeading(bearing - (target.turret_facing * 60))
	if bearing >= 300 or bearing <= 60:
		return 'Front'
	return 'Side'


# initiate an attack by one unit on another
def InitAttack(attacker, weapon, target):
	
	# send information to CalcAttack, which will return an Attack object
	attack_obj = CalcAttack(attacker, weapon, target)
	
	# if player wasn't attacker, display LoS from attacker to target
	# TODO: this will pause any ongoing animations, need to integrate into animation handler
	if attacker.owning_player == 1:
		line = GetLine(attacker.screen_x, attacker.screen_y, target.screen_x,
			target.screen_y)
		for (x,y) in line[2:-2]:
			libtcod.console_set_char(con, x, y, 250)
			libtcod.console_set_char_foreground(con, x, y, libtcod.red)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			Wait(3)
	
	# display attack console
	DisplayAttack(attack_obj)
	
	# if player is attacker, they have a chance to cancel
	if WaitForEnter(allow_cancel = (attacker == scenario.player_unit)):
		DrawScreenConsoles()
		return
	
	# set unit fired flag
	attacker.fired = True
	# mark this weapon and all others in same group as having fired
	if weapon.firing_group is not None:
		for check_weapon in attacker.weapon_list:
			if check_weapon.firing_group is not None:
				if check_weapon.firing_group == weapon.firing_group:
					check_weapon.fired = True
	
	# if player is attacking, set action for crewman firing this weapon
	if attacker == scenario.player_unit:
		weapon.SetFiredAction(scenario.player_unit)
	
	# turn off LoS display and clear any LoS drawn above from screen for animation
	scenario.display_los = False
	DrawScreenConsoles()
	libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	libtcod.console_flush()
	
	# display appropriate attack animation
	if weapon.weapon_type == 'gun':
		x1, y1 = attack_obj.attacker.screen_x-26, attack_obj.attacker.screen_y-3
		x2, y2 = attack_obj.target.screen_x-26, attack_obj.target.screen_y-3
		scenario.anim.InitGunEffect(x1, y1, x2, y2)
		WaitForAnimation()
	elif weapon.weapon_type in ['small_arms', 'coax_mg', 'hull_mg']:
		x1, y1 = attack_obj.attacker.screen_x-26, attack_obj.attacker.screen_y-3
		x2, y2 = attack_obj.target.screen_x-26, attack_obj.target.screen_y-3
		scenario.anim.InitAFAttackEffect(x1, y1, x2, y2)
		WaitForAnimation()
	
	# do to-hit roll
	# clear "Enter to Roll" and "Backspace to Cancel" lines
	libtcod.console_rect(attack_con, 1, 57, 24, 1, True, libtcod.BKGND_NONE)
	libtcod.console_rect(attack_con, 1, 58, 24, 1, True, libtcod.BKGND_NONE)
	libtcod.console_blit(attack_con, 0, 0, 30, 60, con, 0, 0)
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	libtcod.console_flush()
	
	# do dice roll and display animation
	pause_time = config.getint('ArmCom2', 'animation_speed') * 0.5
	for i in range(5):
		d1, d2, roll = Roll2D6()
		DrawDie(attack_con, 9, 49, d1)
		DrawDie(attack_con, 14, 49, d2)
		libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		Wait(pause_time)
	
	# display roll result
	text = str(roll) + ': '
	if roll == 2 and roll <= attack_obj.final_to_hit:
		text += 'Critical hit!'
		attack_obj.critical_hit = True
	elif roll <= attack_obj.final_to_hit:
		text += 'Attack hit!'
	else:
		text += 'Attack missed'
	libtcod.console_print_ex(attack_con, 13, 53, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	# if target was hit, save attack details to target to be resolved at end of attacker activation
	if roll <= attack_obj.final_to_hit:
		if attack_obj.to_hit_attack:
			
			# see if we apply an AP or a FP hit
			if weapon.stats['loaded_ammo'] == 'AP':
				target.unresolved_ap.append(attack_obj)
				text = 'AP hit applied'
			else:
				fp = scenario.GetGunHEFP(weapon.stats['calibre'])
				if attack_obj.critical_hit:
					fp = fp * 2
				target.unresolved_fp += fp
				text = str(fp) + ' FP applied'
		else:
			fp = attack_obj.final_fp
			if attack_obj.critical_hit:
				fp = fp * 2
			target.unresolved_fp += fp
			text = str(attack_obj.final_fp) + ' FP applied'
		libtcod.console_print_ex(attack_con, 13, 54, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
			
		# target spotted if hit
		if not target.known:
			#print 'DEBUG: spotted unit was hit by an attack'
			target.SpotMe()
	
	# check for concealment loss for attacker
	attacker.DoSpotCheck(just_fired=True)
	
	# newly acquired target
	if attacker.acquired_target is None:
		attacker.acquired_target = (target, 1)
	else:
		(ac_target, ac_level) = attacker.acquired_target
		# new target
		if ac_target != target:
			attacker.ClearAcquiredTargets()
			attacker.acquired_target = (target, 1)
		else:
			# additional level
			if ac_level < 2:
				attacker.acquired_target = (target, 2)

	# check for RoF and handle reloading gun
	rof_possible = True
	
	# reloading procedure for gun
	if weapon.weapon_type == 'gun':
		# clear fired shell
		weapon.stats['loaded_ammo'] = None
		
		# check for ready rack use
		use_rr = False
		if weapon.stats['use_ready_rack'] is not None:
			if weapon.stats['use_ready_rack']:
				use_rr = True
		
		# for player unit: set loader action
		# FUTURE: check for failure
		if attacker == scenario.player_unit:
			scenario.player_unit.SetCrewmanAction('Loader', 'Reload')
		
		# check for new shell of reload type and load it if possible
		reload_type = weapon.stats['reload_ammo']
		if use_rr:
			if weapon.ready_rack[reload_type] > 0:
				weapon.ready_rack[reload_type] -= 1
				weapon.stats['loaded_ammo'] = weapon.stats['reload_ammo']
			else:
				# no shell of the right type in the ready rack, but we can
				#   default to general stores
				weapon.stats['use_ready_rack'] = False
				use_rr = False
		
		if not use_rr:
			if weapon.stores[reload_type] > 0:
				weapon.stores[reload_type] -= 1
				weapon.stats['loaded_ammo'] = weapon.stats['reload_ammo']
		
		# no shell could be loaded, can't maintain RoF
		if weapon.stats['loaded_ammo'] is None:
			rof_possible = False
	
	# weapon has no RoF capability
	if weapon.stats['rof'] == 0:
		rof_possible = False
	# gun had shell switched out or loaded this turn
	elif weapon.no_rof_this_turn:
		rof_possible = False
	
	# FUTURE: allow AI units to get RoF?
	if attacker != scenario.player_unit:
		rof_possible = False
	
	rof_maintained = False
	
	# do RoF roll if possible
	if rof_possible:
		roll_required = weapon.stats['rof']
		if weapon.weapon_type == 'gun':
			if use_rr:
				roll_required += 2
		if roll_required > 10:
			roll_required = 10
		elif roll_required < 2:
			roll_required = 2
		d1, d2, roll = Roll2D6()
		if roll <= roll_required:
			rof_maintained = True
			text = 'RoF maintained'
		else:
			text = 'RoF not maintained'
		libtcod.console_print_ex(attack_con, 13, 55, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
	
	# player maintained RoF
	if attacker == scenario.player_unit and rof_maintained:
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		libtcod.console_print(attack_con, 5, 57, 'Enter')
		libtcod.console_print(attack_con, 6, 58, 'Bksp')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		libtcod.console_print(attack_con, 11, 57, 'Fire Again')
		libtcod.console_print(attack_con, 11, 58, 'Stop Firing')
	else:
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		libtcod.console_print(attack_con, 5, 57, 'Enter')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		libtcod.console_print(attack_con, 11, 57, 'Continue')
	
	libtcod.console_blit(attack_con, 0, 0, 30, 60, con, 0, 0)
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	libtcod.console_flush()
	
	choice = WaitForEnter(allow_cancel=True)
	
	# player wasn't attacker, no choice to be made
	if attacker != scenario.player_unit:
		return True
	
	# player kept RoF and chose to keep firing, return False to start the function again
	if rof_maintained and not choice:
		return False
	
	# player either didn't keep RoF or chose not to continue firing
	# turn LoS display back on
	scenario.display_los = True
	return True


# display the factors and odds for an attack on the screen
# can also display armour penetration roll
def DisplayAttack(attack_obj, ap_roll=False):
	libtcod.console_clear(attack_con)
	
	# display the background outline
	temp = LoadXP('ArmCom2_attack_bkg.xp')
	libtcod.console_blit(temp, 0, 0, 0, 0, attack_con, 0, 0)
	del temp
	
	# title
	libtcod.console_set_default_background(attack_con, TITLE_BG_COL)
	libtcod.console_rect(attack_con, 1, 1, 24, 1, False, libtcod.BKGND_SET)
	if ap_roll:
		text = 'Armour Penetration'
	else:
		text = 'Attack Roll'
	libtcod.console_print_ex(attack_con, 13, 1, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	# attacker or target portrait
	if ap_roll:
		unit = attack_obj.target
	else:
		unit = attack_obj.attacker
	libtcod.console_set_default_background(attack_con, PORTRAIT_BG_COL)
	libtcod.console_rect(attack_con, 1, 2, 24, 8, False, libtcod.BKGND_SET)
	
	if not (unit.owning_player == 1 and not unit.known):
		if unit.unit_id in unit_portraits:
			libtcod.console_blit(unit_portraits[unit.unit_id], 0, 0, 0, 0, attack_con, 1, 2)
	libtcod.console_print_ex(attack_con, 13, 10, libtcod.BKGND_NONE, libtcod.CENTER,
		unit.GetName())
	
	# roll description
	if attack_obj.attacker.owning_player == 1 and not attack_obj.attacker.known:
		text = 'unknown weapon'
	else:
		text = attack_obj.weapon.GetName()
	if ap_roll:
		text = ' hit by ' + text
	else:
		text = 'firing ' + text + ' at'
	libtcod.console_print_ex(attack_con, 13, 11, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	# target name and portrait if to-hit roll
	if not ap_roll:
		libtcod.console_print_ex(attack_con, 13, 12, libtcod.BKGND_NONE,
			libtcod.CENTER, attack_obj.target.GetName())
		libtcod.console_set_default_background(attack_con, PORTRAIT_BG_COL)
		libtcod.console_rect(attack_con, 1, 13, 24, 8, False, libtcod.BKGND_SET)
		
		if not (attack_obj.target.owning_player == 1 and not attack_obj.target.known):
			if attack_obj.target.unit_id in unit_portraits:
				libtcod.console_blit(unit_portraits[attack_obj.target.unit_id], 0, 0, 0, 0, attack_con, 1, 13)
	else:
		# location hit in AP roll
		libtcod.console_print_ex(attack_con, 13, 12, libtcod.BKGND_NONE,
			libtcod.CENTER, 'in ' + attack_obj.location_desc)
		if attack_obj.critical_hit:
			libtcod.console_print_ex(attack_con, 13, 14, libtcod.BKGND_NONE,
				libtcod.CENTER, 'Critical Hit')
				
	# firepower and modifiers
	if not ap_roll and not attack_obj.to_hit_attack:
		
		if not (attack_obj.attacker.owning_player == 1 and not attack_obj.attacker.known):
			text = 'Base FP: ' + str(attack_obj.base_fp)
			libtcod.console_print_ex(attack_con, 13, 21, libtcod.BKGND_NONE,
				libtcod.CENTER, text)
			y = 22
			libtcod.console_set_default_foreground(attack_con, INFO_TEXT_COL)
			for (text, mod_text) in attack_obj.fp_mods:
				libtcod.console_print(attack_con, 2, y, text)
				libtcod.console_print_ex(attack_con, 23, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, mod_text)
				y+=1
		
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		text = 'Final FP: ' + str(attack_obj.final_fp)
		libtcod.console_print_ex(attack_con, 13, 25, libtcod.BKGND_NONE,
			libtcod.CENTER, text)

	# base to-hit / AP roll
	if ap_roll:
		text = 'Base roll required: ' + str(attack_obj.base_ap)
	else:
		text = 'Base to-hit: ' + str(attack_obj.base_to_hit)
	libtcod.console_print_ex(attack_con, 13, 26, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	# list of roll modifiers
	libtcod.console_set_default_background(attack_con, TITLE_BG_COL)
	libtcod.console_rect(attack_con, 1, 27, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 13, 27, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Roll Modifiers')
	y = 29
	
	if attack_obj.attacker.owning_player == 1 and not attack_obj.attacker.known:
		libtcod.console_print_ex(attack_con, 13, y, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Unknown')
	
	elif len(attack_obj.modifiers) == 0:
		libtcod.console_print_ex(attack_con, 13, y, libtcod.BKGND_NONE,
			libtcod.CENTER, 'None')
	
	else:
		total_mod = 0
		for (text, mod) in attack_obj.modifiers:
			
			lines = wrap(text, 18, subsequent_indent = ' ')
			for line in lines:
				libtcod.console_print(attack_con, 2, y, line)
				y += 1
			y -= 1
			mod_text = str(mod)
			if mod > 0: mod_text = '+' + mod_text
			libtcod.console_print_ex(attack_con, 23, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, mod_text)
			total_mod += mod
			y += 1
		
		text = str(total_mod)
		if total_mod > 0:
			text = '+' + text
		libtcod.console_print_ex(attack_con, 13, 39, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Total Modifier: ' + text)
	
	# final roll required
	libtcod.console_rect(attack_con, 1, 41, 24, 1, False, libtcod.BKGND_SET)
	if ap_roll:
		text = 'Score to penetrate:'
	else:
		text = 'Score to hit:'
	libtcod.console_print_ex(attack_con, 13, 41, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	if ap_roll:
		text = str(attack_obj.final_ap)
	else:
		text = str(attack_obj.final_to_hit)
	libtcod.console_print_ex(attack_con, 13, 43, libtcod.BKGND_NONE,
		libtcod.CENTER, chr(243) + text)
	
	# draw title line for where roll result will appear
	libtcod.console_rect(attack_con, 1, 47, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 13, 47, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Roll')
	
	# display prompts
	libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
	libtcod.console_print(attack_con, 7, 57, 'Enter')
	libtcod.console_set_default_foreground(attack_con, libtcod.white)
	libtcod.console_print(attack_con, 13, 57, 'Roll')
		
	if attack_obj.attacker == scenario.player_unit and not ap_roll:
		libtcod.console_set_default_foreground(attack_con, ACTION_KEY_COL)
		libtcod.console_print(attack_con, 6, 58, 'Bksp')
		libtcod.console_set_default_foreground(attack_con, libtcod.white)
		libtcod.console_print(attack_con, 11, 58, 'Cancel')
	
	libtcod.console_set_default_background(attack_con, libtcod.black)
	
	# display console on screen
	libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	libtcod.console_flush()


# draw a representation of a die face to the console
def DrawDie(console, x, y, d):
	libtcod.console_blit(dice, 0+((d-1)*3), 0, 3, 3, console, x, y)
	

# fill the hex map with terrain
def GenerateTerrain():
	
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
			
			road_finished = True
	
	
	# create a local list of all hx, hy locations in map
	map_hex_list = []
	for key, map_hex in scenario.hex_map.hexes.iteritems():
		map_hex_list.append((map_hex.hx, map_hex.hy))
	hex_num = len(map_hex_list)				# total number of map hexes
	#print 'Terrain Generation: ' + str(hex_num) + ' map hexes'
	
	# clear map
	for (hx, hy) in map_hex_list:
		map_hex = GetHexAt(hx, hy)
		map_hex.SetTerrainType('Open Ground')
		map_hex.SetElevation(1)
		map_hex.dirt_road_links = []
	
	# terrain settings
	# FUTURE: will be supplied by battleground settings
	rough_ground_num = int(hex_num / 50)
	
	hill_num = int(hex_num / 80)		# number of hills to generate
	hill_min_size = 3			# minimum width/height of hill area
	hill_max_size = 6			# maximum "
	
	forest_num = int(hex_num / 70)		# number of forest areas to generate
	forest_size = 6				# total maximum height + width of areas
	
	village_max = int(hex_num / 100)	# maximum number of villages to generate
	village_min = int(hex_num / 50)		# minimum "
	
	fields_num = int(hex_num / 50)		# number of tall field areas to generate
	field_min_size = 3			# minimum width/height of field area
	field_max_size = 6			# maximum "
	
	ponds_min = 0				# minimum number of ponds to generate
	ponds_max = int(hex_num / 70)		# maximum "
	
	##################################################################################
	#                                Rough Ground                                    #
	##################################################################################
	
	for rough_ground_pass in range(rough_ground_num):
		(hx, hy) = choice(map_hex_list)
		map_hex = GetHexAt(hx, hy)
		map_hex.SetTerrainType('Rough Ground')
	
	
	##################################################################################
	#                             Elevation / Hills                                  #
	##################################################################################
	
	#print 'Terrain Generation: Generating ' + str(hill_num) + ' hills'
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
			map_hex = GetHexAt(hx, hy)
			if map_hex is not None:
				map_hex.SetElevation(2)
	
	##################################################################################
	#                                  Forests                                       #
	##################################################################################
	
	#print 'Terrain Generation: Generating ' + str(forest_num) + ' forest areas'
	if forest_size < 2:
		forest_size = 2
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
			map_hex = GetHexAt(hx, hy)
			if map_hex is not None:
				# small chance of gaps in area
				if libtcod.random_get_int(0, 1, 15) == 1:
					continue
				map_hex.SetTerrainType('Sparse Forest')
	
	##################################################################################
	#                                 Villages                                       #
	##################################################################################
	
	num_villages = libtcod.random_get_int(0, village_min, village_max)
	#print 'Terrain Generation: Generating ' + str(num_villages) + ' villages'
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
	
	##################################################################################
	#                                Tall Fields                                     #
	##################################################################################
	
	#print 'Terrain Generation: Generating ' + str(fields_num) + ' tall field areas'
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
	
	##################################################################################
	#                                   Ponds                                        #
	##################################################################################
	
	num_ponds = libtcod.random_get_int(0, ponds_min, ponds_max)
	#print 'Terrain Generation: Generating ' + str(num_ponds) + ' ponds'
	for terrain_pass in range(num_ponds):
		shuffle(map_hex_list)
		for (hx, hy) in map_hex_list:
			map_hex = GetHexAt(hx, hy)
			if map_hex.terrain_type.display_name != 'Open Ground':
				continue
			if map_hex.elevation != 1:
				continue
			map_hex.SetTerrainType('Pond')
			break
	
	##################################################################################
	#                                   Roads                                        #
	##################################################################################
	
	# add two roads
	CreateRoad()
	CreateRoad(vertical=False)


# update the contextual info console
def UpdateContextCon():
	libtcod.console_clear(context_con)
	
	if scenario.active_unit.owning_player != 0: return
	
	# Movement Menu
	if scenario.active_cmd_menu == 'movement':
		libtcod.console_set_default_foreground(context_con, libtcod.white)
		libtcod.console_print(context_con, 0, 0, 'Movement')
		libtcod.console_set_default_foreground(context_con, libtcod.light_green)
		libtcod.console_print(context_con, 0, 1, scenario.player_unit.movement_class)
		
		# display chance of extra/missed turn
		(hx, hy) = GetAdjacentHex(scenario.player_unit.hx,
			scenario.player_unit.hy, scenario.player_unit.facing)
		chance = scenario.player_unit.GetMovementTurnChance(hx, hy)
		# move not possible or no chance of extra/missed turn
		if chance == 0: return
		if chance < 0:
			text = '-1 turn: ' + chr(242) + str(abs(chance))
		else:
			text = '+1 turn: ' + chr(243) + str(chance)
		libtcod.console_print(context_con, 0, 2, text)
	
	# Weapons Menu
	# TODO: display contextual info for this particular weapon
	elif scenario.active_cmd_menu[:12] == 'weapon_menu_':
		libtcod.console_set_default_foreground(context_con, libtcod.white)
		libtcod.console_print(context_con, 0, 0, 'Main Gun')
		
		libtcod.console_set_default_foreground(context_con, INFO_TEXT_COL)
		weapon = scenario.player_unit.weapon_list[0]
		libtcod.console_print(context_con, 0, 1, weapon.GetName())
		libtcod.console_print(context_con, 0, 2, 'Load')
		libtcod.console_print(context_con, 0, 3, 'Next')
		
		libtcod.console_set_default_foreground(context_con, INFO_TEXT_COL)
		if weapon.stats['loaded_ammo'] is None:
			text = 'None'
		else:
			text = weapon.stats['loaded_ammo']
		libtcod.console_print(context_con, 5, 2, text)
		if weapon.stats['reload_ammo'] is None:
			text = 'None'
		else:
			text = weapon.stats['reload_ammo']
		libtcod.console_print(context_con, 5, 3, text)
		
		if weapon.stats['use_ready_rack'] is not None:
			if weapon.stats['use_ready_rack']:
				col = libtcod.white
			else:
				col = libtcod.dark_grey
			libtcod.console_set_default_foreground(context_con, col)
			libtcod.console_print(context_con, 10, 4, 'RR')
		
		y = 5
		for ammo_type in AMMO_TYPE_ORDER:
			if ammo_type in weapon.stats['ammo_types']:
				
				libtcod.console_set_default_foreground(context_con, libtcod.white)
				libtcod.console_print(context_con, 2, y, ammo_type)
				libtcod.console_set_default_foreground(context_con, INFO_TEXT_COL)
				libtcod.console_print_ex(context_con, 8, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, str(weapon.stores[ammo_type]))
				libtcod.console_print_ex(context_con, 11, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, str(weapon.ready_rack[ammo_type]))
				y+=1
		
		libtcod.console_set_default_foreground(context_con, libtcod.white)
		libtcod.console_print(context_con, 2, 9, 'Max')
		libtcod.console_set_default_foreground(context_con, INFO_TEXT_COL)
		libtcod.console_print_ex(context_con, 8, 9, libtcod.BKGND_NONE,
			libtcod.RIGHT, str(scenario.player_unit.max_ammo))
		libtcod.console_print_ex(context_con, 11, 9, libtcod.BKGND_NONE,
			libtcod.RIGHT, str(weapon.stats['rr_size']))


# update the objective info console
def UpdateObjectiveConsole():
	libtcod.console_clear(objective_con)
	libtcod.console_set_default_foreground(objective_con, libtcod.white)
	libtcod.console_print(objective_con, 0, 0, 'Objectives')
	
	# sort objectives by distance to player
	obj_list = []
	for map_hex in scenario.objective_hexes:
		distance = GetHexDistance(scenario.player_unit.hx, scenario.player_unit.hy,
			map_hex.hx, map_hex.hy)
		# convert to meters
		distance = distance * 160
		obj_list.append((distance, map_hex))
	
	if len(obj_list) == 0: return
	
	obj_list.sort(key=lambda x: x[0])
	
	y = 2
	for (distance, map_hex) in obj_list:
		
		# display colour
		if map_hex.held_by is None:
			col = NEUTRAL_OBJ_COL
		else:
			if map_hex.held_by == 0:
				col = FRIENDLY_OBJ_COL
			else:
				col = ENEMY_OBJ_COL
		libtcod.console_set_default_foreground(objective_con, col)
		
		# display distance to objective
		if distance > 1000:
			text = str(float(distance) / 1000.0) + ' km.'
		else:
			text = str(distance) + ' m.'
		libtcod.console_print_ex(objective_con, 9, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
		
		# directional arrow if required
		if distance > 0:
			direction = GetDirectionToward(scenario.player_unit.hx, scenario.player_unit.hy,
				map_hex.hx, map_hex.hy)
			direction = CombineDirs(direction, 0 - scenario.player_unit.facing)
			char = GetDirectionalArrow(direction)
			libtcod.console_put_char_ex(objective_con, 11, y, char, col, SMALL_CON_BKG)
		y += 1


# update the current message console with the most recent game message
# truncated if too long to display (55x2)
def UpdateMsgConsole():
	libtcod.console_clear(msg_con)
	lines = wrap(scenario.messages[-1], 55, subsequent_indent = ' ')
	libtcod.console_print(msg_con, 0, 0, lines[0])
	if len(lines) > 1:
		libtcod.console_print(msg_con, 0, 1, lines[1])
	if len(lines) > 2:
		libtcod.console_print_ex(msg_con, 54, 1, libtcod.BKGND_NONE,
			libtcod.RIGHT, '...')


# draw the map viewport console
# each hex is 5x5 cells, but edges overlap with adjacent hexes
def UpdateVPConsole():

	libtcod.console_set_default_background(map_vp_con, libtcod.black)
	libtcod.console_clear(map_vp_con)
	scenario.map_index = {}
	
	# draw off-map hexes first
	for (hx, hy), (map_hx, map_hy) in scenario.map_vp.items():
		if (map_hx, map_hy) not in scenario.hex_map.hexes:
			(x,y) = PlotHex(hx, hy)
			libtcod.console_blit(tile_offmap, 0, 0, 0, 0, map_vp_con, x-3, y-2)
	
	obj_hexes = []
	
	for elevation in range(4):
		for (hx, hy) in VP_HEXES:
			(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
			map_hex = GetHexAt(map_hx, map_hy)
			if map_hex is None: continue
			if map_hex.elevation != elevation: continue
			(x,y) = PlotHex(hx, hy)
			h_con = map_hex.terrain_type.console[map_hex.elevation]
			libtcod.console_blit(h_con, 0, 0, 0, 0, map_vp_con, x-3, y-2)
			
			# add FoV mask if required
			if not map_hex.vis_to_player:
				libtcod.console_blit(fov_hex_con, 0, 0, 0, 0, map_vp_con, x-3, y-2, 0.4, 0.4)
			
			# record map hexes of screen locations
			for x1 in range(x-1, x+2):
				scenario.map_index[(x1,y-1)] = (map_hx, map_hy)
				scenario.map_index[(x1,y+1)] = (map_hx, map_hy)
			for x1 in range(x-2, x+3):
				scenario.map_index[(x1,y)] = (map_hx, map_hy)
			
			# mark objective hexes for display on viewport later
			if map_hex in scenario.objective_hexes:
				obj_hexes.append((hx, hy, map_hex))
	
	# draw roads and rivers overtop
	for (hx, hy), (map_hx, map_hy) in scenario.map_vp.items():
		# no map hex here
		if (map_hx, map_hy) not in scenario.hex_map.hexes: continue
		map_hex = scenario.hex_map.hexes[(map_hx, map_hy)]
		# no road here
		if len(map_hex.dirt_road_links) == 0: continue
		for direction in map_hex.dirt_road_links:
			# only draw each road link once
			if 3 <= direction <= 5: continue
			
			# paint road
			(x1, y1) = PlotHex(hx, hy)
			(hx2, hy2) = GetAdjacentHex(hx, hy, ConstrainDir(direction - scenario.player_unit.facing))
			(x2, y2) = PlotHex(hx2, hy2)
			line = GetLine(x1, y1, x2, y2)
			for (x, y) in line:
				libtcod.console_set_char_background(map_vp_con, x, y,
					DIRT_ROAD_COL, libtcod.BKGND_SET)
				
				# if character is not blank or hex edge, remove it
				if libtcod.console_get_char(map_vp_con, x, y) not in [0, 250]:
					libtcod.console_set_char(map_vp_con, x, y, 0)
	
	# highlight objective hexes
	for (hx, hy, map_hex) in obj_hexes:
		if map_hex.held_by is None:
			col = NEUTRAL_OBJ_COL
		else:
			if map_hex.held_by == 0:
				col = FRIENDLY_OBJ_COL
			else:
				col = ENEMY_OBJ_COL
		(x, y) = PlotHex(hx, hy)
		for (xm, ym) in HEX_EDGE_TILES:
			libtcod.console_set_char_foreground(map_vp_con, x+xm, y+ym, col)


# run through active PSGs and draw them to the unit console
def UpdateUnitConsole():
	libtcod.console_clear(unit_con)
	for (hx, hy) in VP_HEXES:
		(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
		map_hex = GetHexAt(map_hx, map_hy)
		if map_hex is None: continue
		if len(map_hex.unit_stack) == 0: continue
		# draw the top unit in the stack
		map_hex.unit_stack[0].DrawMe(hx, hy, len(map_hex.unit_stack))


# updates the player unit info console
# displays essential info about the player's current vehicle and crew
def UpdatePlayerUnitConsole():
	libtcod.console_clear(player_unit_con)
	unit = scenario.player_unit
	
	# vehicle name if any
	if unit.vehicle_name:
		libtcod.console_set_default_foreground(player_unit_con, HIGHLIGHT_COLOR)
		libtcod.console_print(player_unit_con, 0, 0, unit.vehicle_name)
		
	# unit type name
	libtcod.console_set_default_foreground(player_unit_con, INFO_TEXT_COL)
	libtcod.console_print(player_unit_con, 0, 1, unit.GetName())
	
	# unit portrait
	if unit.unit_id in unit_portraits:
		libtcod.console_blit(unit_portraits[unit.unit_id], 0, 0, 0, 0, player_unit_con, 0, 2)
	
	
	# crew skill and morale ratings
	libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
	libtcod.console_set_default_background(player_unit_con, SECTION_BG_COL)
	libtcod.console_rect(player_unit_con, 0, 10, 24, 1, True, libtcod.BKGND_SET)
	libtcod.console_set_default_background(player_unit_con, libtcod.black)
	libtcod.console_print(player_unit_con, 0, 10, SKILL_DESC[unit.skill_lvl])
	libtcod.console_print_ex(player_unit_con, 23, 10, libtcod.BKGND_NONE,
		libtcod.RIGHT, MORALE_DESC[unit.morale_lvl])
	
	# list of crew and crew positions
	if unit.crew_positions is not None:
		y = 12
		for position in unit.crew_positions:
			# highlight crew line if selected
			if scenario.selected_crew_position is not None:
				if scenario.selected_crew_position == position:
					libtcod.console_set_default_background(player_unit_con, SELECTED_WEAPON_COLOR)
					libtcod.console_rect(player_unit_con, 0, y, 24,
						1, True, libtcod.BKGND_SET)
					libtcod.console_set_default_background(player_unit_con, libtcod.black)
			
			# abbreviated crew position name
			libtcod.console_set_default_foreground(player_unit_con, libtcod.light_grey)
			text = CREW_POSITION_ABB[position.name]
			libtcod.console_print(player_unit_con, 0, y, text)
			
			# hatch status
			if position.hatch is None:
				text = '--'
			else:
				if position.hatch == 'Closed':
					text = 'BU'
				else:
					text = 'CE'
			libtcod.console_set_default_foreground(player_unit_con, libtcod.dark_grey)
			libtcod.console_print(player_unit_con, 4, y, text)
			
			# current crewman action or other status
			if position.crewman is None:
				text = '[Position Empty]'
			else:
				if position.crewman.action is None:
					libtcod.console_set_default_foreground(player_unit_con, INFO_TEXT_COL)
					text = 'Spot'
				else:
					libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
					text = position.crewman.action
			libtcod.console_print_ex(player_unit_con, 23, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			
			# buttoned up / crew exposed hatch status
			libtcod.console_set_default_foreground(player_unit_con, libtcod.dark_grey)
			libtcod.console_hline(player_unit_con, 0, y+1, 24)
			
			y += 2

	libtcod.console_set_default_background(player_unit_con, SECTION_BG_COL)
	libtcod.console_rect(player_unit_con, 0, 22, 24, 1, True, libtcod.BKGND_SET)
	libtcod.console_set_default_background(player_unit_con, libtcod.black)

	# armour
	libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
	if scenario.player_unit.armour is None:
		libtcod.console_print(player_unit_con, 0, 22, 'Unarmoured')
	else:
		libtcod.console_print(player_unit_con, 0, 22, 'Armour')
		libtcod.console_set_default_foreground(player_unit_con, INFO_TEXT_COL)
		# display armour for turret and hull
		if scenario.player_unit.turret_facing is None:
			text = 'U '
		else:
			text = 'T '
		text += str(scenario.player_unit.armour['turret_front']) + '/' + str(scenario.player_unit.armour['turret_side'])
		libtcod.console_print(player_unit_con, 0, 23, text)
		text = 'H ' + str(scenario.player_unit.armour['hull_front']) + '/' + str(scenario.player_unit.armour['hull_side'])
		libtcod.console_print(player_unit_con, 0, 24, text)
		
	# unit statuses
	libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
	libtcod.console_print_ex(player_unit_con, 23, 22, libtcod.BKGND_NONE,
		libtcod.RIGHT, 'Status')
	libtcod.console_set_default_foreground(player_unit_con, INFO_TEXT_COL)
	
	if scenario.player_unit.moved:
		text = 'Moving'
	elif scenario.player_unit.moved_last_action:
		text = 'Moved'
	else:
		text = 'Stopped'
	libtcod.console_print_ex(player_unit_con, 23, 23, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	
	if scenario.player_unit.fired:
		text = 'Fired'
	else:
		text = ''
	libtcod.console_print_ex(player_unit_con, 23, 24, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	
	if not scenario.player_unit.known:
		libtcod.console_print_ex(player_unit_con, 23, 25, libtcod.BKGND_NONE, libtcod.RIGHT,
			'Concealed')


# displays a window with information about a particular PSG
# (Not used any more)
def DisplayPSGInfoWindow(psg):
	
	# darken the screen background
	libtcod.console_blit(darken_con, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.7)
	
	# display PSG info in the centre of the screen
	
	UpdatePlayerUnitConsole(psg=psg)
	y = 14
	libtcod.console_rect(0, WINDOW_XM-12, y, 24, 23, True, libtcod.BKGND_SET)
	libtcod.console_blit(player_unit_con, 0, 0, 0, 0, 0, WINDOW_XM-12, y)
	
	libtcod.console_print_ex(0, WINDOW_XM, y+22, libtcod.BKGND_NONE,
		libtcod.CENTER, 'X to Return')
	
	# Note: animations are paused while this window is active
	exit_menu = False
	while not exit_menu:
		
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		if key is None: continue
		
		key_char = chr(key.c).lower()
		
		if key_char == 'x':
			exit_menu = True
	
	# restore the PSG console and blit the main console to the screen again
	UpdatePlayerUnitConsole()
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	libtcod.console_flush()
	

# updates the command console
def UpdateCmdConsole():
	libtcod.console_clear(cmd_con)
	libtcod.console_set_default_foreground(cmd_con, TITLE_COL)
	libtcod.console_set_default_background(cmd_con, TITLE_BG_COL)
	libtcod.console_rect(cmd_con, 0, 0, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(cmd_con, 12, 0, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.cmd_menu.title)
	libtcod.console_set_default_foreground(cmd_con, INFO_TEXT_COL)
	libtcod.console_set_default_background(cmd_con, libtcod.black)
	scenario.cmd_menu.DisplayMe(cmd_con, 0, 2, 24)


# draw scenario info to the scenario info console
def UpdateScenInfoConsole():
	libtcod.console_clear(scen_info_con)
	
	# scenario battlefront, current and time
	libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
	libtcod.console_print_ex(scen_info_con, 14, 0, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.battlefront)
	text = MONTH_NAMES[scenario.month] + ' ' + str(scenario.year)
	libtcod.console_print_ex(scen_info_con, 14, 1, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	text = str(scenario.hour) + ':' + str(scenario.minute).zfill(2)
	libtcod.console_print_ex(scen_info_con, 14, 2, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	
	# FUTURE: move wind and weather info to own console
	#text = 'No Wind'
	#libtcod.console_print_ex(scen_info_con, 56, 0, libtcod.BKGND_NONE, libtcod.RIGHT,
	#	text)
	#text = 'Clear'
	#libtcod.console_print_ex(scen_info_con, 56, 1, libtcod.BKGND_NONE, libtcod.RIGHT,
	#	text)
	# FUTURE: pull light and visibility info from scenario object
	#text = ''
	#libtcod.console_print_ex(scen_info_con, 56, 2, libtcod.BKGND_NONE, libtcod.RIGHT,
	#	text)


# update the map hex info console
def UpdateHexInfoConsole():
	libtcod.console_set_default_background(hex_info_con, libtcod.black)
	libtcod.console_clear(hex_info_con)
	libtcod.console_set_default_foreground(hex_info_con, TITLE_COL)
	libtcod.console_set_default_background(hex_info_con, TITLE_BG_COL)
	libtcod.console_rect(hex_info_con, 0, 0, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print(hex_info_con, 0, 0, 'Hex Info')
	
	# see if we can display info about a map hex
	
	# mouse cursor outside of map area
	if mouse.cx < 27: return
	x = mouse.cx - 27
	y = mouse.cy - 4
	if (x,y) not in scenario.map_index: return
	
	(hx, hy) = scenario.map_index[(x,y)]
	map_hex = GetHexAt(hx, hy)
	
	# replace window title with terrain type
	libtcod.console_rect(hex_info_con, 0, 0, 24, 1, True, libtcod.BKGND_SET)
	libtcod.console_print(hex_info_con, 0, 0, map_hex.terrain_type.display_name)
	
	# DEBUG: display coordinates; disable in distribution version?
	libtcod.console_set_default_foreground(hex_info_con, INFO_TEXT_COL)
	libtcod.console_print_ex(hex_info_con, 23, 0, libtcod.BKGND_NONE,
		libtcod.RIGHT, str(map_hex.hx) + ',' + str(map_hex.hy))
	
	# road
	if len(map_hex.dirt_road_links) > 0:
		libtcod.console_set_default_foreground(hex_info_con, DIRT_ROAD_COL)
		libtcod.console_print(hex_info_con, 0, 1, 'Road')
		libtcod.console_set_default_foreground(hex_info_con, INFO_TEXT_COL)
	
	# FUTURE: stone road, rail, river
	
	# elevation
	libtcod.console_print_ex(hex_info_con, 23, 1, libtcod.BKGND_NONE, libtcod.RIGHT,
		str(int(map_hex.elevation * ELEVATION_M)) + 'm')
	
	# objective status
	if map_hex.objective:
		if map_hex.held_by is None:
			col = NEUTRAL_OBJ_COL
		else:
			if map_hex.held_by == 0:
				col = FRIENDLY_OBJ_COL
			else:
				col = ENEMY_OBJ_COL
		libtcod.console_set_default_foreground(hex_info_con, col)
		text = 'Objective: ' + map_hex.objective
		libtcod.console_print_ex(hex_info_con, 23, 2, libtcod.BKGND_NONE, libtcod.RIGHT,
			text)
		libtcod.console_set_default_foreground(hex_info_con, INFO_TEXT_COL)
	
	# FUTURE: display ground conditions here
	# DEBUG: tactical score
	#libtcod.console_print(hex_info_con, 0, 2, 'AI Score: ' + str(map_hex.score))

	# no units present
	unit_num = len(map_hex.unit_stack)
	if unit_num == 0: return
	
	# get top unit in stack
	unit = map_hex.unit_stack[0]
	
	if unit.owning_player == 1 and not unit.known:
		col = UNKNOWN_HL_COL
	else:
		if unit.owning_player == 1:
			col = ENEMY_HL_COL
		else:
			col = FRIENDLY_HL_COL
	libtcod.console_set_default_background(hex_info_con, col)
	libtcod.console_rect(hex_info_con, 0, 4, 24, 1, False, libtcod.BKGND_SET)
	#libtcod.console_set_default_background(hex_info_con, libtcod.black)
	
	libtcod.console_set_default_foreground(hex_info_con, libtcod.white)
	libtcod.console_print(hex_info_con, 0, 4, unit.GetName())
	libtcod.console_set_default_foreground(hex_info_con, INFO_TEXT_COL)
	
	# FUTURE: display unit statuses on line 5
	
	# unresolved hits on top unit in stack
	if unit.unresolved_fp > 0 or len(unit.unresolved_ap) > 0:
		text = 'Hit by '
		if unit.unresolved_fp > 0:
			text += str(unit.unresolved_fp) + ' FP'
		if len(unit.unresolved_ap) > 0:
			if unit.unresolved_fp > 0:
				text += '; '
			text += str(len(unit.unresolved_ap)) + ' AP'
		libtcod.console_print(hex_info_con, 1, 6, text)
	
	# acquired target status of top unit in stack
	libtcod.console_set_default_foreground(hex_info_con, libtcod.white)
	libtcod.console_set_default_background(hex_info_con, INFO_TEXT_COL)
	if scenario.player_unit.acquired_target is not None:
		(ac_target, ac_level) = scenario.player_unit.acquired_target
		if ac_target == unit:
			text = 'AC'
			if ac_level > 1: text += '2'
			libtcod.console_print_ex(hex_info_con, 0, 7, libtcod.BKGND_SET,
				libtcod.LEFT, text)
	if unit.acquired_target is not None:
		(ac_target, ac_level) = unit.acquired_target
		if ac_target == scenario.player_unit:
			text = 'AC'
			if ac_level > 1: text += '2'
			libtcod.console_set_default_foreground(hex_info_con, ENEMY_UNIT_COL)
			libtcod.console_print_ex(hex_info_con, 4, 7, libtcod.BKGND_SET,
				libtcod.LEFT, text)
	
	libtcod.console_set_default_foreground(hex_info_con, libtcod.white)
	libtcod.console_set_default_background(hex_info_con, libtcod.black)
	
	# note if additional units in stack
	if unit_num > 1:
		text = '+' + str(unit_num-1) + ' more unit'
		if unit_num > 2: text += 's'
		libtcod.console_print(hex_info_con, 0, 8, text)
	
	
# draw all the display consoles to the screen
def DrawScreenConsoles():
	
	libtcod.console_clear(con)
	
	# map viewport layers
	libtcod.console_blit(bkg_console, 0, 0, 0, 0, con, 0, 0)		# grey outline
	libtcod.console_blit(map_vp_con, 0, 0, 0, 0, con, 27, 4)		# map viewport
	libtcod.console_blit(vp_mask, 0, 0, 0, 0, con, 27, 4)			# map viewport mask
	libtcod.console_blit(unit_con, 0, 0, 0, 0, con, 27, 4, 1.0, 0.0)	# map unit layer

	# left column consoles
	libtcod.console_blit(player_unit_con, 0, 0, 0, 0, con, 1, 1)
	libtcod.console_blit(cmd_con, 0, 0, 0, 0, con, 1, 33)
	libtcod.console_blit(hex_info_con, 0, 0, 0, 0, con, 1, 50)
	
	# scenario info, contextual info, objective info, and most recent message if any
	libtcod.console_blit(scen_info_con, 0, 0, 0, 0, con, 40, 0)
	libtcod.console_blit(context_con, 0, 0, 0, 0, con, 27, 1)
	libtcod.console_blit(objective_con, 0, 0, 0, 0, con, 70, 50)
	libtcod.console_blit(msg_con, 0, 0, 0, 0, con, 27, 58)

	# LoS display for player unit
	if scenario.display_los and scenario.player_target is not None:
		libtcod.console_set_char_background(con, scenario.player_target.screen_x,
			scenario.player_target.screen_y, TARGET_HL_COL, flag=libtcod.BKGND_SET)
		# draw LoS line
		line = GetLine(scenario.player_unit.screen_x, scenario.player_unit.screen_y,
			scenario.player_target.screen_x, scenario.player_target.screen_y)
		for (x, y) in line[2:-1]:
			libtcod.console_set_char(con, x, y, 250)
			libtcod.console_set_char_foreground(con, x, y, libtcod.red)
		
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	libtcod.console_blit(anim_con, 0, 0, 0, 0, 0, 26, 3, 1.0, 0.0)	# animation layer


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
	# FUTURE: this info should be part of scenario object as well
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
	global scen_menu_con, bkg_console, map_vp_con, vp_mask, map_fov_con
	global unit_con, player_unit_con, anim_con, cmd_con, attack_con, scen_info_con
	global context_con, objective_con, hex_info_con, fov_hex_con, msg_con, tile_offmap
	global dice
	
	# update every display console and draw everything to screen
	# FUTURE: change to UpdateConsoles()
	def UpdateScreen():
		UpdateUnitConsole()
		UpdatePlayerUnitConsole()
		UpdateCmdConsole()
		UpdateContextCon()
		UpdateObjectiveConsole()
		UpdateMsgConsole()
		DrawScreenConsoles()
	
	# generate screen consoles
	
	# background console
	bkg_console = LoadXP('ArmCom2_bkg.xp')
	
	# main menu console
	scen_menu_con = LoadXP('ArmCom2_menu.xp')
	libtcod.console_set_default_background(scen_menu_con, libtcod.black)
	libtcod.console_set_default_foreground(scen_menu_con, libtcod.white)
	libtcod.console_print_ex(scen_menu_con, 37, 2, libtcod.BKGND_NONE, libtcod.CENTER,
		VERSION + SUBVERSION)
	
	# map viewport console
	map_vp_con = libtcod.console_new(55, 53)
	libtcod.console_set_default_background(map_vp_con, libtcod.black)
	libtcod.console_set_default_foreground(map_vp_con, libtcod.white)
	libtcod.console_clear(map_vp_con)
	
	# map viewport mask
	vp_mask = LoadXP('vp_mask.xp')
	libtcod.console_set_key_color(vp_mask, KEY_COLOR)
	
	# field of view overlay console
	map_fov_con = libtcod.console_new(57, 57)
	libtcod.console_set_default_background(map_fov_con, libtcod.black)
	libtcod.console_set_default_foreground(map_fov_con, libtcod.white)
	libtcod.console_set_key_color(map_fov_con, KEY_COLOR)
	libtcod.console_clear(map_fov_con)
	
	# unit layer console
	unit_con = libtcod.console_new(55, 52)
	libtcod.console_set_default_background(unit_con, KEY_COLOR)
	libtcod.console_set_default_foreground(unit_con, libtcod.grey)
	libtcod.console_set_key_color(unit_con, KEY_COLOR)
	libtcod.console_clear(unit_con)
	
	# animation layer console
	anim_con = libtcod.console_new(57, 57)
	libtcod.console_set_default_background(anim_con, KEY_COLOR)
	libtcod.console_set_default_foreground(anim_con, libtcod.white)
	libtcod.console_set_key_color(anim_con, KEY_COLOR)
	libtcod.console_clear(anim_con)
	
	# top banner scenario info console
	scen_info_con = libtcod.console_new(28, 3)
	libtcod.console_set_default_background(scen_info_con, libtcod.black)
	libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
	libtcod.console_clear(scen_info_con)
	
	# contextual info console
	context_con = libtcod.console_new(12, 10)
	libtcod.console_set_default_background(context_con, SMALL_CON_BKG)
	libtcod.console_set_default_foreground(context_con, libtcod.white)
	libtcod.console_clear(context_con)
	
	# objective info console
	objective_con = libtcod.console_new(12, 7)
	libtcod.console_set_default_background(objective_con, SMALL_CON_BKG)
	libtcod.console_set_default_foreground(objective_con, libtcod.white)
	libtcod.console_clear(objective_con)
	
	# player unit info console
	player_unit_con = libtcod.console_new(24, 31)
	libtcod.console_set_default_background(player_unit_con, libtcod.black)
	libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
	libtcod.console_clear(player_unit_con)
	
	# command menu console
	cmd_con = libtcod.console_new(24, 16)
	libtcod.console_set_default_background(cmd_con, libtcod.black)
	libtcod.console_set_default_foreground(cmd_con, libtcod.white)
	libtcod.console_clear(cmd_con)
	
	# hex and unit info console
	hex_info_con = libtcod.console_new(24, 9)
	libtcod.console_set_default_background(hex_info_con, libtcod.black)
	libtcod.console_set_default_foreground(hex_info_con, libtcod.white)
	libtcod.console_clear(hex_info_con)
	
	# most recent message display console
	msg_con = libtcod.console_new(55, 2)
	libtcod.console_set_default_background(msg_con, libtcod.black)
	libtcod.console_set_default_foreground(msg_con, libtcod.white)
	libtcod.console_clear(msg_con)
	
	# attack resolution console
	attack_con = libtcod.console_new(26, 60)
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.white)
	libtcod.console_clear(attack_con)

	# load dark tile to indicate tiles that aren't visible to the player
	fov_hex_con = LoadXP('ArmCom2_tile_fov.xp')
	libtcod.console_set_key_color(fov_hex_con, KEY_COLOR)
	# indicator for off-map tiles on viewport
	tile_offmap = LoadXP('ArmCom2_tile_offmap.xp')
	libtcod.console_set_key_color(tile_offmap, KEY_COLOR)

	# die face image
	dice = LoadXP('dice.xp')
	
	# load terrain type definitions
	terrain_types = LoadTerrainTypes()
	
	# here is where a saved game in-progress would be loaded
	if load_savegame:
		LoadGame()
		
		# check for saved game compatibility
		if scenario.game_version != VERSION:
			text = ('This save was created with version ' + scenario.game_version +
				' of the game. It is not compatible with the current version.')
			GetConfirmation(text, warning_only=True)
			del scenario
			return
		
		# reset pointers to terrain consoles for each map hex
		# (needed because consoles can't be pickled)
		for map_key, map_hex in scenario.hex_map.hexes.iteritems():
			map_hex.SetTerrainType(map_hex.terrain_type.display_name)
		UpdateVPConsole()
	
	else:
	
		##################################################################################
		#                            Start a new Scenario                                #
		##################################################################################
		
		# create a new campaign day object and hex map
		scenario = Scenario(26, 26)
		
		# FUTURE: following will be handled by a Scenario Generator
		# for now, things are set up manually
		scenario.battlefront = 'Western Poland'
		scenario.name = 'Spearhead'
		scenario.description = ('Your forces have broken through enemy lines, ' +
			'and are advancing to capture strategic objectives before the ' +
			'defenders have a chance to react.')
		scenario.objectives = 'Capture all objectives'
		scenario.year = 1939
		scenario.month = 9
		scenario.hour = 5
		scenario.minute = 0
		scenario.hour_limit = 9
		scenario.minute_limit = 0
		
		# display scenario info: chance to cancel scenario start
		#if not ScenarioSummary():
		#	del scenario
		#	return
		
		libtcod.console_clear(0)
		libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Generating map...')
		libtcod.console_flush()
		
		GenerateTerrain()
		
		# spawn the player unit
		# FUTURE: integrate into a single spawn function with deployment zones
		#  for each side
		new_unit = Unit('Panzer 35t')
		new_unit.owning_player = 0
		new_unit.vehicle_name = 'Gretchen'
		new_unit.facing = 0
		new_unit.turret_facing = 0
		new_unit.morale_lvl = 8
		new_unit.skill_lvl = 8
		scenario.player_unit = new_unit		# record this as the player unit
		map_hex = GetHexAt(6, 22)
		if not map_hex.terrain_type.water:
			new_unit.hx = 6
			new_unit.hy = 22
		else:
			map_hex = GetHexAt(7, 22)
			new_unit.hx = 7
			new_unit.hy = 22
		map_hex.unit_stack.append(new_unit)
		scenario.unit_list.append(new_unit)
		
		# set up player tank crew
		new_crew = Crewman()
		new_crew.name = ['Günter', 'Bauer']
		new_crew.position_training['Commander/Gunner'] = 30
		new_unit.SetCrew('Commander/Gunner', new_crew, player=True)
		
		new_crew = Crewman()
		new_crew.name = ['Hans', 'Eichelberger']
		new_crew.position_training['Loader'] = 20
		new_unit.SetCrew('Loader', new_crew)
		
		new_crew = Crewman()
		new_crew.name = ['Werner', 'Kaufmann']
		new_crew.position_training['Driver'] = 20
		new_unit.SetCrew('Driver', new_crew)
		
		new_crew = Crewman()
		new_crew.name = ['Horst', 'Schwicker']
		new_crew.position_training['Assistant Driver'] = 10
		new_unit.SetCrew('Assistant Driver', new_crew)
		
		# spawn player squadron
		#for i in range(4):
		#	new_unit = Unit('Panzer 35t')
		#	scenario.unit_list.append(new_unit)
		#	new_unit.owning_player = 0
		#	new_unit.facing = 0
		#	new_unit.turret_facing = 0
		#	new_unit.morale_lvl = 8
		#	new_unit.skill_lvl = 8
		#	new_unit.squadron_leader = scenario.player_unit
		
		UpdatePlayerUnitConsole()
		
		# set up our objectives: 3 distributed randomly but not too close to the player
		#   and not too close to another objective
		# FUTURE: move to its own function within Scenario class
		total_objectives = 3
		for tries in range(300):
			if total_objectives == 0: break
			(hx, hy) = choice(scenario.hex_map.hexes.keys())
			map_hex = scenario.hex_map.hexes[(hx, hy)]
			if map_hex.terrain_type.water: continue
			distance = GetHexDistance(scenario.player_unit.hx,
				scenario.player_unit.hy, hx, hy)
			if distance <= 12: continue
			too_close = False
			for obj_hex in scenario.objective_hexes:
				distance = GetHexDistance(obj_hex.hx, obj_hex.hy, hx, hy)
				if distance <= 8:
					too_close = True
					break
			if too_close: continue
			scenario.hex_map.AddObjectiveAt(hx, hy, 'Capture')
			total_objectives -= 1
		
		#print 'Objectives placed: took ' + str(tries) + ' tries'
		
		# generate tactical scores for map hexes for AI
		# FUTURE - not used for anything yet
		#scenario.hex_map.GenerateTacticalMap()
		
		# do initial objective status check
		for map_hex in scenario.objective_hexes:
			map_hex.CheckObjectiveStatus(no_message=True)
		
		# spawn enemy units and dummy unit
		# FUTURE: use a more complex deployment table
		ENEMY_LIST = ['TK_3', '7TP', '37mm_wz_36', 'TKS_20mm', 'vickers_ejw',
			'rifle_squad_atr']
		for i in range(6):
			unit_id = choice(ENEMY_LIST)
			scenario.SpawnEnemy(unit_id, 9, 9)
		for i in range(4):
			unit_id = choice(ENEMY_LIST)
			scenario.SpawnEnemy(unit_id, 9, 9, dummy=True)
		
		# all units spawned, load unit portraits into consoles
		scenario.LoadUnitPortraits()
		
		# set up map viewport
		scenario.SetVPHexes()
		
		# calculate initial field of view for player and draw viewport console for first time
		scenario.hex_map.CalcFoV()
		UpdateVPConsole()
		
		# generate action order for all units in the scenario
		scenario.GenerateUnitOrder()
		
		# activate first unit in list
		scenario.active_unit = scenario.unit_list[0]
		scenario.active_unit.DoPreActivation()
		
		# build initial command menu
		scenario.active_cmd_menu = 'root'
		scenario.BuildCmdMenu()
		
		scenario.AddMessage('Time is now: ' + str(scenario.hour) + ':' + 
			str(scenario.minute).zfill(2), None)
		
		
	# End of new/continued game set-up
	
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
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_blit(anim_con, 0, 0, 0, 0, 0, 26, 3, 1.0, 0.0)
		
		libtcod.console_flush()
	
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
			key, mouse)
		
		# end of scenario
		if scenario.winner is not None:
			scenario.DisplayEndScreen()
			EraseGame()
			exit_scenario = True
			continue
		
		# emergency loop escape
		if libtcod.console_is_window_closed(): sys.exit()
		
		# check to see if mouse cursor has moved
		if mouse.cx != mouse_x or mouse.cy != mouse_y:
			mouse_x = mouse.cx
			mouse_y = mouse.cy
			UpdateHexInfoConsole()
			DrawScreenConsoles()
		
		##### Mouse Commands #####
		#if mouse.lbutton or mouse.rbutton:
		#	x = mouse.cx - 26
		#	y = mouse.cy - 3
		#	if (x,y) in scenario.map_index:
		#		(hx, hy) = scenario.map_index[(x,y)]
		#		for psg in scenario.unit_list:
		#			if psg.hx == hx and psg.hy == hy:
						
						# left button: select this PSG
		#				if mouse.lbutton and psg.owning_player == 0:
		#					scenario.active_unit = psg
		#					UpdatePlayerUnitConsole()
		#					scenario.BuildCmdMenu()
		#					DrawScreenConsoles()
		#					break
						
						# right button: display PSG info window
						#elif mouse.rbutton and not (psg.owning_player == 1 and not psg.known):
						#	DisplayPSGInfoWindow(psg)
						#	break
		
		# open scenario menu screen
		if key.vk == libtcod.KEY_ESCAPE:
			if ScenarioMenu():
				exit_scenario = True
			else:
				DrawScreenConsoles()
			continue
		
		##### AI Actions #####
		if scenario.active_unit.owning_player == 1:
			scenario.active_unit.ai.DoAction()
			scenario.ActivateNextUnit()
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
		
		# selected an inactive menu option
		if option.inactive: continue
		
		##################################################################
		# Generic and Root Menu Actions
		##################################################################
		if option.option_id == 'end_action':
			scenario.ActivateNextUnit()
			UpdateScreen()
			continue
		elif option.option_id == 'return_to_root':
			scenario.active_cmd_menu = 'root'
			scenario.BuildCmdMenu()
			scenario.display_los = False
			UpdateScreen()
			continue
		elif option.option_id == 'crew_menu':
			scenario.active_cmd_menu = 'crew'
			scenario.BuildCmdMenu()
			UpdateScreen()
			continue
		elif option.option_id == 'movement_menu':
			scenario.active_cmd_menu = 'movement'
			scenario.BuildCmdMenu()
			UpdateScreen()
			continue
		elif option.option_id == 'weapons_menu':
			scenario.active_cmd_menu = 'weapons'
			scenario.BuildCmdMenu()
			UpdateScreen()
			continue
		
		##################################################################
		# Movement Menu Actions
		##################################################################
		elif option.option_id in ['move_forward', 'move_backward']:
			if option.option_id == 'move_forward':
				direction = scenario.player_unit.facing
			else:
				direction = CombineDirs(scenario.player_unit.facing, 3)
			(hx, hy) = GetAdjacentHex(scenario.player_unit.hx,
				scenario.player_unit.hy, direction)
			# attempt the move
			if scenario.player_unit.MoveInto(hx, hy):
				scenario.BuildCmdMenu()
				DrawScreenConsoles()
				scenario.ActivateNextUnit()
				continue
		
		elif option.option_id in ['pivot_hull_port', 'pivot_hull_stb']:
			if option.option_id == 'pivot_hull_port':
				new_direction = CombineDirs(scenario.player_unit.facing, -1)
			else:
				new_direction = CombineDirs(scenario.player_unit.facing, 1)
			if scenario.player_unit.PivotToFace(new_direction):
				scenario.BuildCmdMenu()
				DrawScreenConsoles()
		
		elif option.option_id in ['rotate_turret_cc', 'rotate_turret_cw']:
			if option.option_id == 'rotate_turret_cc':
				new_direction = CombineDirs(scenario.player_unit.turret_facing, -1)
			else:
				new_direction = CombineDirs(scenario.player_unit.turret_facing, 1)
			if scenario.player_unit.RotateTurret(new_direction):
				DrawScreenConsoles()
		
		##################################################################
		# Weapons Menu Actions
		##################################################################
		elif option.option_id[:12] == 'weapon_menu_':
			scenario.active_cmd_menu = option.option_id
			i = int(option.option_id[12])
			scenario.selected_weapon = scenario.player_unit.weapon_list[i]
			scenario.BuildCmdMenu()
			UpdateContextCon()
			scenario.display_los = True
			DrawScreenConsoles()
		
		##################################################################
		# Individual Weapon Actions
		##################################################################
		elif option.option_id == 'next_target':
			scenario.SelectNextPlayerTarget()
			scenario.BuildCmdMenu()
			DrawScreenConsoles()

		elif option.option_id == 'fire_weapon':
			# loop for RoF maintained
			result = False
			while result is False:
				result = InitAttack(scenario.player_unit, scenario.selected_weapon,
					scenario.player_target)
				UpdateContextCon()
				libtcod.console_flush()
			UpdatePlayerUnitConsole()
			scenario.BuildCmdMenu()
			DrawScreenConsoles()
			SaveGame()
		
		elif option.option_id == 'cycle_weapon_load':
			if scenario.selected_weapon.CycleAmmoLoad():
				UpdateContextCon()
				UpdatePlayerUnitConsole()
				scenario.BuildCmdMenu()
				DrawScreenConsoles()
		
		elif option.option_id == 'toggle_rr':
			if scenario.selected_weapon.ToggleRR():
				UpdateContextCon()
				UpdatePlayerUnitConsole()
				scenario.BuildCmdMenu()
				DrawScreenConsoles()
		
		elif option.option_id == 'cycle_weapon_reload':
			if scenario.selected_weapon.CycleAmmoReload():
				UpdateContextCon()
				UpdatePlayerUnitConsole()
				scenario.BuildCmdMenu()
				DrawScreenConsoles()
	
		elif option.option_id == 'next_weapon':
			i = scenario.player_unit.weapon_list.index(scenario.selected_weapon)
			if i == len(scenario.player_unit.weapon_list) - 1:
				i = 0
			else:
				i += 1
			scenario.selected_weapon = scenario.player_unit.weapon_list[i]
			UpdateContextCon()
			scenario.BuildCmdMenu()
			DrawScreenConsoles()
		
		elif option.option_id == 'return_to_weapons':
			scenario.active_cmd_menu = 'weapons'
			scenario.selected_weapon = None
			UpdateContextCon()
			scenario.BuildCmdMenu()
			scenario.display_los = False
			DrawScreenConsoles()

	# we're exiting back to the main menu, so delete the scenario object
	del scenario


# try to load game settings from config file
def LoadCFG():
	
	global config
	
	config = ConfigParser.RawConfigParser()
	
	# create a new config file
	if not os.path.exists(DATAPATH + 'armcom2.cfg'):
		print 'No config file found, creating a new one'
		config.add_section('ArmCom2')
		config.set('ArmCom2', 'language', 'English')
		config.set('ArmCom2', 'large_display_font', 'true')
		config.set('ArmCom2', 'animation_speed', '30')
		
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



##########################################################################################
#                                                                                        #
#                                       Main Script                                      #
#                                                                                        #
##########################################################################################

global config, unit_portraits
global mouse, key, con, darken_con
global lang_dict			# pointer to the current language dictionary of game msgs
global gradient_x			# for main menu animation

print 'Starting ' + NAME + ' version ' + VERSION

# dictionary of unit portraits
unit_portraits = {}

# try to load game settings from config file, will create a new file if none present
LoadCFG()

# set up language dictionary pointer
lang_dict = languages.game_msgs[config.get('ArmCom2', 'language')]

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

# display loading screen
libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM, libtcod.BKGND_NONE, libtcod.CENTER,
	GetMsg('loading'))
libtcod.console_flush()

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

# FUTURE: put into its own function so can be re-called after language change

# generate main menu console
main_menu_con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(main_menu_con, libtcod.black)
libtcod.console_set_default_foreground(main_menu_con, libtcod.white)
libtcod.console_clear(main_menu_con)
main_menu_image = LoadXP('ArmCom2_title.xp')
# randomly load a tank image to use for this session
tank_image = LoadXP(choice(TANK_IMAGES))
libtcod.console_blit(tank_image, 0, 0, 20, 8, main_menu_image, 5, 6)
del tank_image

# main title
libtcod.console_blit(main_menu_image, 0, 0, 88, 60, main_menu_con, 0, 0)
# localized title if any
libtcod.console_print_ex(main_menu_con, WINDOW_XM, 35, libtcod.BKGND_NONE,
	libtcod.CENTER, GetMsg('title'))

# version number and program info
libtcod.console_set_default_foreground(main_menu_con, libtcod.red)
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-8, libtcod.BKGND_NONE,
	libtcod.CENTER, 'Weekly Development Build: Has bugs and incomplete features')

libtcod.console_set_default_foreground(main_menu_con, libtcod.light_grey)
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-6, libtcod.BKGND_NONE,
	libtcod.CENTER, VERSION + SUBVERSION)
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-4,
	libtcod.BKGND_NONE, libtcod.CENTER, 'Copyright 2016-2017')
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-3,
	libtcod.BKGND_NONE, libtcod.CENTER, GetMsg('license'))
libtcod.console_print_ex(main_menu_con, WINDOW_XM, WINDOW_HEIGHT-2,
	libtcod.BKGND_NONE, libtcod.CENTER, 'www.armouredcommander.com')

libtcod.console_set_default_foreground(main_menu_con, libtcod.white)

# build main menus
menus = []

cmd_menu = CommandMenu('main_menu')
cmd_menu.AddOption('continue_scenario', 'C', GetMsg('continue_game'))
cmd_menu.AddOption('new_scenario', 'N', GetMsg('new_game'))
cmd_menu.AddOption('options', 'O', GetMsg('game_options'))
cmd_menu.AddOption('quit', 'Q', GetMsg('quit_game'))
menus.append(cmd_menu)

cmd_menu = CommandMenu('settings_menu')
menu_option = cmd_menu.AddOption('switch_language', 'L', 'Language',
	desc='Cycle between in-game languages')
menu_option.inactive = True
cmd_menu.AddOption('toggle_font_size', 'F', 'Font Size',
	desc='Switch between 12px and 16px font size')
cmd_menu.AddOption('select_ani_speed', 'A', 'Animation Speed',
	desc='Change the display speed of in-game animations')
cmd_menu.AddOption('return_to_main', 'Bksp', 'Main Menu',
	desc='Return to main menu')
menus.append(cmd_menu)

active_menu = menus[0]

# Main Menu functions

def AnimateMainMenu():
	
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
	
def UpdateMainMenu():
	libtcod.console_blit(main_menu_con, 0, 0, 88, 60, con, 0, 0)
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0)
	active_menu.DisplayMe(0, WINDOW_XM-12, 38, 24)
	
	# settings menu active
	if active_menu == menus[1]:
		libtcod.console_set_default_foreground(0, HIGHLIGHT_COLOR)
		
		text = 'Language: ' + config.get('ArmCom2', 'language').decode('utf8').encode('IBM850')
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

# check for presence of a saved game file and disable the 'continue' menu option if not present
def CheckSavedGame(menu):
	for menu_option in menu.cmd_list:
		if menu_option.option_id != 'continue_scenario': continue
		if os.path.exists('savegame'):
			menu_option.inactive = False
		else:
			menu_option.inactive = True
		return


# set up animation timing
time_click = time.time()
gradient_x = WINDOW_WIDTH + 20

CheckSavedGame(active_menu)

UpdateMainMenu()

exit_game = False

while not exit_game:
	
	# trigger animation
	if time.time() - time_click >= 0.05:
		AnimateMainMenu()
		UpdateMainMenu()
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
		UpdateMainMenu()
		continue
		
	elif key.vk == libtcod.KEY_DOWN:
		active_menu.SelectNextOption()
		UpdateMainMenu()
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
	UpdateMainMenu()
	libtcod.console_flush()
	
	# selected an inactive menu option
	if option.inactive: continue
	
	# main menu
	if option.option_id == 'continue_scenario':
		DoScenario(load_savegame=True)
		active_menu = menus[0]
		CheckSavedGame(active_menu)
		UpdateMainMenu()
	elif option.option_id == 'new_scenario':
		# check for already-existing saved game
		if os.path.exists('savegame'):
			text = 'Starting a new game will erase the previous one. Proceed?'
			if not GetConfirmation(text):
				UpdateMainMenu()
				continue
			
		DoScenario()
		active_menu = menus[0]
		CheckSavedGame(active_menu)
		UpdateMainMenu()
	elif option.option_id == 'options':
		active_menu = menus[1]
		UpdateMainMenu()
	elif option.option_id == 'quit':
		exit_game = True
	
	# settings menu
	elif option.option_id == 'switch_language':
		current_language = config.get('ArmCom2', 'language')
		i = languages.LANGUAGE_LIST.index(current_language)
		if i == len(languages.LANGUAGE_LIST) - 1:
			i = 0
		else:
			i += 1
		config.set('ArmCom2', 'language', languages.LANGUAGE_LIST[i])
		lang_dict = languages.game_msgs[config.get('ArmCom2', 'language')]
		SaveCFG()
		UpdateMainMenu()
	
	elif option.option_id == 'toggle_font_size':
		libtcod.console_delete(0)
		if config.getboolean('ArmCom2', 'large_display_font'):
			config.set('ArmCom2', 'large_display_font', 'false')
			fontname = 'c64_12x12.png'
		else:
			config.set('ArmCom2', 'large_display_font', 'true')
			fontname = 'c64_16x16.png'
		libtcod.console_set_custom_font(DATAPATH+fontname,
			libtcod.FONT_LAYOUT_ASCII_INROW, 0, 0)
		libtcod.console_init_root(WINDOW_WIDTH, WINDOW_HEIGHT,
			NAME + ' - ' + VERSION + SUBVERSION, fullscreen = False,
			renderer = libtcod.RENDERER_GLSL)
		SaveCFG()
		UpdateMainMenu()
	
	elif option.option_id == 'select_ani_speed':
		ani_time = config.getint('ArmCom2', 'animation_speed')
		if ani_time == 16:
			config.set('ArmCom2', 'animation_speed', 30)
		elif ani_time == 30:
			config.set('ArmCom2', 'animation_speed', 46)
		else:
			config.set('ArmCom2', 'animation_speed', 16)
		SaveCFG()
		UpdateMainMenu()
	
	elif option.option_id == 'return_to_main':
		active_menu = menus[0]
		UpdateMainMenu()

# END #

