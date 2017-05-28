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
VERSION = 'PoC 4'					# determines saved game compatability
SUBVERSION = ''						# descriptive, no effect on compatability
DATAPATH = 'data/'.replace('/', os.sep)			# path to data files
LIMIT_FPS = 50						# maximum screen refreshes per second
WINDOW_WIDTH = 83					# width of game window in characters
WINDOW_HEIGHT = 60					# height "
WINDOW_XM = int(WINDOW_WIDTH/2)				# horizontal center of game window
WINDOW_YM = int(WINDOW_HEIGHT/2)			# vertical "

# gradient animated effect for main menu
GRADIENT = [
	libtcod.Color(51, 51, 51), libtcod.Color(64, 64, 64), libtcod.Color(128, 128, 128),
	libtcod.Color(192, 192, 192), libtcod.Color(255, 255, 255), libtcod.Color(192, 192, 192),
	libtcod.Color(128, 128, 128), libtcod.Color(64, 64, 64), libtcod.Color(51, 51, 51),
	libtcod.Color(51, 51, 51)
]

# Game engine constants, can be tweaked for slightly different results
MAX_LOS_DISTANCE = 6				# maximum distance that a Line of Sight can be drawn
MAX_BU_LOS_DISTANCE = 4				# " for buttoned-up crewmen
ELEVATION_M = 20.0				# each elevation level represents x meters of height
BASE_SPOT_SCORE = 5				# base score required to spot unknown enemy unit
HEX_STACK_LIMIT = 6				# maximum number of units in a map hex stack
MP_COSTS = [
	[1,1,1],				# infantry
	[3,6,3],				# tank
	[3,6,3]					# fast tank
]

# short forms for crew positions, used to fit information into player unit info console, etc.
CREW_POSITION_ABB = {
	'Commander' : 'C',
	'Commander/Gunner' : 'C/G',
	'Gunner' : 'G',
	'Loader' : 'L',
	'Driver' : 'D',
	'Assistant Driver' : 'AD'
}

# order in which to display crew positions
CREW_POSITION_ORDER = ['Commander', 'Commander/Gunner', 'Gunner', 'Loader', 'Driver',
	'Assistant Driver'
]

# order in which to display ammo types
AMMO_TYPE_ORDER = ['HE', 'AP']

# turn phases, in order
PHASE_LIST = ['Crew Actions', 'Movement', 'Shooting', 'Close Combat']

# Colour definitions
RIVER_BG_COL = libtcod.Color(0, 0, 217)			# background color for river edges
DIRT_ROAD_COL = libtcod.Color(50, 40, 25)		# background color for dirt roads

NEUTRAL_OBJ_COL = libtcod.Color(0, 255, 255)		# neutral objective color
ENEMY_OBJ_COL = libtcod.Color(255, 31, 0)		# enemy-held "
FRIENDLY_OBJ_COL = libtcod.Color(50, 255, 0)		# friendly-held "

ACTION_KEY_COL = libtcod.Color(70, 170, 255)		# colour for key commands
TITLE_COL = libtcod.white				# fore and background colours for
TITLE_BG_COL = libtcod.Color(0, 50, 100)		#  console titles and highlighted options
SECTION_BG_COL = libtcod.Color(0, 32, 64)		# darker bg colour for sections
INFO_TEXT_COL = libtcod.Color(190, 190, 190)		# informational text colour
PORTRAIT_BG_COL = libtcod.Color(217, 108, 0)		# background color for unit portraits
HIGHLIGHT_COLOR = libtcod.Color(51, 153, 255)		# colour for highlighted text 
WEAPON_LIST_COLOR = libtcod.Color(25, 25, 90)		# background for weapon list in PSG console
SELECTED_WEAPON_COLOR = libtcod.Color(50, 50, 150)	# " selected weapon
ACTIVE_MSG_COL = libtcod.Color(0, 210, 0)		# active message colour

TARGET_HL_COL = libtcod.Color(55, 0, 0)			# target highlight background color 
SELECTED_HL_COL = libtcod.Color(100, 255, 255)		# selected PSG highlight colour
ENEMY_HL_COL = libtcod.Color(40, 0, 0)
INACTIVE_COL = libtcod.Color(100, 100, 100)		# inactive option color
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency

HIGHLIGHT_CHARS = [250, 249, 7, 7, 7, 7, 249, 250]


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

# Note: hexes use an axial coordinate system:
# http://www.redblobgames.com/grids/hexagons/#coordinates-axial

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
		self.player_position = False	# position occupied by player character
		
		# note: the following visble hextants are relative to the hull/turret facing of the vehicle
		self.closed_visible = closed_visible	# set of visible hextants when hatch is closed
		self.open_visible = open_visible	# " open
	
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
		self.unit_id = unit_id			# unique ID for unit type, used to
							#   load basic stats from unit_defs.xml
		self.unit_name = ''			# descriptive name of unit type
		self.vehicle_name = None		# tank or other vehicle name
		self.portrait = None
		self.ai = AI(self)			# pointer to AI instance
		self.owning_player = None		# player that controls this unit
		self.squadron_leader = None		# used for player squadron
		
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
		self.identified = False			# unit has been identified by the opposing side
		
		self.facing = None			# facing direction: guns and vehicles must have this set
		self.turret_facing = None		# facing of main turret on unit
		self.movement_class = ''		# movement class
		self.max_mp = 0				# maximum movement points per turn
		self.mp = 0				# current " remaining
		
		self.armour = None			# armour factors if any
		self.max_ammo = 0			# maximum number of gun ammo carried
		self.weapon_list = []			# list of weapons
		
		self.acquired_target = None		# PSG has acquired this unit as target
		self.acquired_by = []			# PSG has been acquired by this/these unit(s)
		self.rof_target = None			# target for maintaining RoF
		
		# action flags
		self.moved = False
		self.fired = False
		self.changed_facing = False
		
		# status flags
		self.broken = False
		self.shocked = False
		self.bogged = False
		
		# special abilities or traits
		self.recce = False
		self.unreliable = False
		
		self.LoadStats()				# load stats from unit_defs.xml
		self.display_char = self.GetDisplayChar()	# set initial display character

	# attempt to place this unit into the map at hx, hy
	# if this location is impassible to unit, try adjacent hexes as well
	def PlaceAt(self, hx, hy):
		hex_list = [(hx, hy)]
		hex_list.extend(GetAdjacentHexesOnMap(hx, hy))
		for (hx1, hy1) in hex_list:
			map_hex = GetHexAt(hx1, hy1)
			if map_hex.terrain_type.water: continue
			if len(map_hex.unit_stack) > HEX_STACK_LIMIT: continue
			if len(map_hex.unit_stack) > 0:
				if map_hex.unit_stack[0].owning_player != self.owning_player: continue
			# found a good target location
			self.hx = hx1
			self.hy = hy1
			map_hex.unit_stack.append(self)
			return
		
		print ('ERROR: Could not place ' + GetName(self, true_name=True) +
			' into map at ' + str(hx) + ',' + str(hy))

	# load the baseline stats for this unit from data file
	def LoadStats(self):
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
						hatch = 'Closed'
					open_visible = set()
					if i.find('open_visible') is not None:
						string = i.find('open_visible').text
						for c in string:
							open_visible.add(int(c))
					closed_visible = set()
					if i.find('closed_visible') is not None:
						string = i.find('closed_visible').text
						for c in string:
							closed_visible.add(int(c))
					
					new_position = CrewPosition(name, turret,
						hatch, open_visible, closed_visible)
					
					# check for special statuses
					if i.find('large_hatch') is not None:
						new_position.large_hatch = True
					
					self.crew_positions.append(new_position)
				
				# TODO: sort crew_positions by name based on CREW_POSITION_ORDER?
				
		
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
		
		# set up maximum mp for each movement class
		if self.movement_class == 'Infantry':
			self.max_mp = 1
		elif self.movement_class == 'Tank':
			self.max_mp = 6
		elif self.movement_class == 'Fast Tank':
			self.max_mp = 9
		self.mp = self.max_mp
	
	# return a description of this unit
	# if using real name, transcode it to handle any special characters in it
	# if true_name, return the real identity of this PSG no matter what
	def GetName(self, true_name=False):
		if not true_name:
			if self.owning_player == 1 and not self.known:
				return 'Suspected Enemy'
		return self.unit_name.decode('utf8').encode('IBM850')
	
	# assign a crewmember to a crew position
	def SetCrew(self, position_name, crewman, player=False):
		
		for position in self.crew_positions:
			if position.name == position_name:
				position.crewman = crewman
				# position is occupied by player character
				if player:
					position.player_position = True
				return
		
		print ('ERROR: tried to assign crew to ' + position_name + ' position but ' +
			'no such position exists!')
			

##########################################################################################

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

	# return the name of a single step within this PSG
	def GetStepName(self):
		return self.step_name.decode('utf8').encode('IBM850')

	# clear any acquired target links between this PSG and any other
	def ClearAcquiredTargets(self):
		self.acquired_target = None
		self.acquired_by = []
		for psg in scenario.unit_list:
			if self in psg.acquired_by:
				psg.acquired_by.remove(self)
			if psg.acquired_target == self:
				psg.acquired_target = None

	# remove this unit from the game
	def DestroyMe(self):
		text = self.GetName() + ' has been destroyed!'
		Message(text, target_unit=self)
		scenario.unit_list.remove(self)
		# clear acquired target records
		self.ClearAcquiredTargets()
		UpdateUnitConsole()

	# do any automatic actions for this unit for start of current phase
	def ResetForPhase(self):
		
		# clear any targets and selected weapon
		self.target_list = []
		self.target_psg = None
		self.selected_weapon = None
		
		# start of movement phase (and new player turn)
		if scenario.GetCurrentPhase() == 'Movement':
			self.mp = self.max_mp
			self.moved = False
			self.changed_facing = False
			
			scenario.DoAutomaticSpotCheck()
			
			# if enemy player, roll for action this turn
			if self.owning_player == 1:
				self.ai.GenerateAction()
			
		# start of shooting phase
		elif scenario.GetCurrentPhase() == 'Shooting':
			self.fired = False
			for weapon in self.weapon_list:
				weapon.fired = False

	# do spot checks from this unit to enemy units
	def DoSpotChecks(self):
		
		# build a list of enemy units that can be spotted and/or identified
		target_list = []
		for unit in scenario.unit_list:
			if unit.owning_player == self.owning_player: continue
			if unit.known and unit.identified: continue
			los = GetLoS(self.hx, self.hy, unit.hx, unit.hy)
			if (unit.hx, unit.hy) not in los: continue
			target_list.append(unit)
		
		# no units to spot
		if len(target_list) == 0:
			return
		
		# if unit is fully crewed, use more complex spotting procedure
		if self.crew_positions is not None:
			for crew_position in self.crew_positions:
				# no crew present
				if crew_position.crewman is None: continue
				# TODO: check that crewman status and action allows spot check
				
				if crew_position.hatch is None:
					visible_hextants = crew_position.closed_visible
					max_distance = MAX_BU_LOS_DISTANCE
				else:
					if crew_position.hatch == 'Closed':
						visible_hextants = crew_position.closed_visible
						max_distance = MAX_BU_LOS_DISTANCE
					else:
						visible_hextants = crew_position.open_visible
						max_distance = MAX_LOS_DISTANCE
				
				shuffle(target_list)
				for unit in reversed(target_list):
					distance = GetHexDistance(self.hx, self.hy,
						unit.hx, unit.hy)
					if distance > max_distance:
						continue
					
					direction = GetDirectionToward(self.hx, self.hy,
						unit.hx, unit.hy)
					
					# TODO: rotate visible hextants based on turret/hull direction
					
					if direction not in visible_hextants:
						continue
					
					# found a viable spot target, do the roll
					score = BASE_SPOT_SCORE
					
					# apply modifiers
					if distance >= 10:
						score -= 3
					elif distance >= 7:
						score -= 2
					elif distance >= 4:
						score -= 1
					
					if unit.size_class == 'Small':
						score -= 1
					
					map_hex = GetHexAt(unit.hx, unit.hy)
					if map_hex.terrain_type.terrain_mod != 0:
						score -= map_hex.terrain_type.terrain_mod
					
					# normalize final score required
					if score < 2:
						score = 2
					
					d1, d2, roll = Roll2D6()
					
					if roll <= score:
						unit.SpotMe()
						target_list.remove(unit)
						break
		
		else:
			# TODO: simplified spotting procedure for units without crew?
			pass
					
		
		pass


	# roll for recovery from negative statuses
	# TODO: move into its own phase eventually
	def DoRecoveryTests(self):
		
		# TEMP
		return
		
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
			Message(text, target_unit=self)
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
			Message(text, target_unit=self)
			return
		
		# test failed, unit is suppressed
		self.SuppressMe()
			
	# this PSG has been spotted by an enemy unit
	def SpotMe(self):
		
		if self.known: return
		
		self.known = True

		# update unit console
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		
		# don't display any message for squadron members
		if self.squadron_leader is not None: return
		
		# TEMP - disabled
		return
		
		# show message
		if self.owning_player == 0:
			text = 'Your '
		else:
			text = 'Enemy '
		text += self.GetName() + ' has been spotted!'
		Message(text, target_unit=self)
	
	# identify this unit to the enemy player
	def IdentifyMe(self):
		
		if self.identified: return
		
		pass
	
	
	# regain unspotted status for this PSG
	# TODO: update, not used right now
	def HideMe(self):
		# update console and screen to make sure unit has finished move animation
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_flush()
		if self.owning_player == 0:
			text = self.GetName() + ' is now unseen by the enemy'
		else:
			text = 'Lost contact with ' + self.GetName()
		Message(text, target_unit=self)
		self.suspected = True
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
	
	

	# draw this PSG to the unit console in the given viewport hx, hy location
	# if stack_size > 1, indicate total number of units in hex stack
	def DrawMe(self, hx, hy, stack_size):
		
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
				col = libtcod.dark_red
			else:
				col = libtcod.red
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
		
		# determine if we need to display a turret
		if not self.gun and not self.vehicle: return
		if self.owning_player == 1 and not self.known: return
		if self.turret_facing is None: return
		
		# determine location to draw turret character
		direction = ConstrainDir(self.turret_facing - scenario.player_unit.facing)
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
			if map_hex.unit_stack[0].owning_player != self.owning_player: return False
		return True
	
	# try to move this PSG into the target hex
	# vehicles must be facing this direction to move, or can do a reverse move
	# returns True if the move was successful
	
	# TODO: check for reverse move and apply modifiers if so
	def MoveInto(self, new_hx, new_hy, free_move=False):
		
		# make sure move is allowed
		if not self.CheckMoveInto(new_hx, new_hy):
			return False
		
		map_hex1 = GetHexAt(self.hx, self.hy)
		map_hex2 = GetHexAt(new_hx, new_hy)
		
		# TEMP
		free_move = True
		
		if not free_move:
			
			# check cost of move
			mp_cost = GetMPCostToMove(self, map_hex1, map_hex2)
			
			# not enough MP for this move
			if mp_cost > self.mp:
				return False
			# spend mp
			self.mp -= mp_cost
		
		# check for squadron movement
		unit_list = [self]
		for unit in map_hex1.unit_stack:
			if unit.squadron_leader == self:
				unit_list.append(unit)
		
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
		
		# display movement animation
		if not (self.owning_player == 1 and self.suspected):
			
			pause_time = config.getint('ArmCom2', 'animation_speed') * 0.1
			(x1,y1) = PlotHex(self.vp_hx, self.vp_hy)
			direction = GetDirectionToAdjacent(map_hex1.hx, map_hex1.hy, new_hx, new_hy)
			# modify by player unit facing?
			direction = ConstrainDir(direction - scenario.player_unit.facing)
			(new_vp_hx, new_vp_hy) = GetAdjacentHex(self.vp_hx, self.vp_hy, direction)
			(x2,y2) = PlotHex(new_vp_hx, new_vp_hy)
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
		
		# set action flag for next activation
		self.moved = True
		
		# clear any acquired targets
		self.ClearAcquiredTargets()
		
		# recalculate viewport and update consoles for player movement
		if scenario.player_unit == self:
			UpdatePlayerUnitConsole()
			scenario.SetVPHexes()
			scenario.hex_map.CalcFoV()
			UpdateVPConsole()
			UpdateHexInfoConsole()
		
		UpdateUnitConsole()
		
		# check for objective capture
		#map_hex2.CheckCapture()
		
		# check for automatic spot
		scenario.DoAutomaticSpotCheck()
		
		return True
	
	# attempt to pivot this unit to face the given direction
	# TODO: first check if possible, might be immobilized, etc.
	def PivotToFace(self, direction):
		if self.facing is None: return False
		facing_change = direction - self.facing
		self.facing = direction
		self.changed_facing = True
		
		# rotate turret facing direction if any
		if self.turret_facing is not None:
			self.turret_facing = CombineDirs(self.turret_facing, facing_change)
		
		# recalculate viewport and update consoles for player pivot
		if scenario.player_unit == self:
			UpdatePlayerUnitConsole()
			scenario.SetVPHexes()
			scenario.hex_map.CalcFoV()
			UpdateVPConsole()
			UpdateHexInfoConsole()
		
		UpdateUnitConsole()
		
		return True
	
	# rotate turret to face new direction
	def RotateTurret(self, direction):
		if self.turret_facing is None: return False
		self.turret_facing = direction
		UpdateUnitConsole()
		return True
	
	# resolve an attack against this unit
	def ResolveAttack(self, attack_obj):
		
		# clear "Backspace to Cancel" and "Enter to Roll" line
		libtcod.console_print_ex(attack_con, 13, 55, libtcod.BKGND_NONE,
			libtcod.CENTER, '                   ')
		libtcod.console_print_ex(attack_con, 13, 57, libtcod.BKGND_NONE,
			libtcod.CENTER, '             ')
		libtcod.console_blit(attack_con, 0, 0, 30, 60, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		
		# do dice roll and display animation
		pause_time = config.getint('ArmCom2', 'animation_speed') * 0.5
		for i in range(5):
			d1, d2, roll = Roll2D6()
			DrawDie(attack_con, 9, 48, d1)
			DrawDie(attack_con, 14, 48, d2)
			libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			Wait(pause_time)
		
		# display roll result on attack console
		libtcod.console_print_ex(attack_con, 13, 52, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Roll: ' + str(roll))
		
		# determine result
		if roll <= attack_obj.final_to_hit:
			text = 'Shot hit!'
		else:
			text = 'Shot missed'
			
		libtcod.console_print_ex(attack_con, 13, 54, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		libtcod.console_print_ex(attack_con, 13, 57, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Enter to Continue')
		libtcod.console_blit(attack_con, 0, 0, 30, 60, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		WaitForEnter()
		
		# no result
		if roll > attack_obj.final_to_hit:
			return
		
		# calculate and save armour penetration roll
		(base_ap, modifiers, final_ap) = CalcAPRoll(attack_obj)
		attack_obj.base_ap = base_ap
		attack_obj.modifiers = modifiers
		attack_obj.final_ap = final_ap
		
		# display AP roll
		DisplayAttack(attack_obj, ap_roll=True)
		WaitForEnter()
		
		# clear "Enter to Roll" line
		libtcod.console_print_ex(attack_con, 13, 57, libtcod.BKGND_NONE,
			libtcod.CENTER, '             ')
		libtcod.console_blit(attack_con, 0, 0, 30, 60, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		
		# do dice roll and display animation
		pause_time = config.getint('ArmCom2', 'animation_speed') * 0.5
		for i in range(5):
			d1, d2, roll = Roll2D6()
			DrawDie(attack_con, 9, 48, d1)
			DrawDie(attack_con, 14, 48, d2)
			libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			Wait(pause_time)
		
		# display roll result on attack console
		libtcod.console_print_ex(attack_con, 13, 52, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Roll: ' + str(roll))
		
		# determine result
		if roll <= attack_obj.final_ap:
			text = 'Shot penetrated armour!'
		else:
			text = 'Shot bounced off armour!'
			
		libtcod.console_print_ex(attack_con, 13, 54, libtcod.BKGND_NONE,
			libtcod.CENTER, text)
		libtcod.console_print_ex(attack_con, 13, 57, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Enter to Continue')
		libtcod.console_blit(attack_con, 0, 0, 30, 60, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
		WaitForEnter()
		
		# no effect
		if roll > attack_obj.final_ap:
			return
		
		# TODO: resolve effect on target
		
	
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
		Message(text, target_unit=self)
	
	# unit recovers from being suppressed
	def UnSuppressMe(self):
		self.suppressed = False
		text = self.GetName() + ' has rallied and recovers from being suppressed.'
		Message(text, target_unit=self)
	
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
			Message(text, target_unit=self)
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
			Message(text, target_unit=self)
			self.DestroyMe()
			return
		
		# FUTURE: choose location based on terrain modifier and distance from known enemy
		(hx, hy) = choice(hex_list)
		self.MoveInto(hx, hy, free_move=True)


# Weapon class: represents a weapon carried by or mounted on a unit
class Weapon:
	def __init__(self, item):
		
		self.fired = False		# weapon has fired this turn
		self.rof_target = None		# RoF pointer to target, None if no RoF maintained
		
		self.stats = {}
		
		# load weapon stats from xml item
		self.weapon_type = item.find('type').text
		self.firing_group = int(item.find('firing_group').text)
		
		# gun stats
		if self.weapon_type == 'gun':
			self.stats['calibre'] = int(item.find('calibre').text)
			if item.find('long_range') is not None:
				self.stats['long_range'] = item.find('long_range').text
			else:
				self.stats['long_range'] = ''
			self.stats['max_range'] = 6
			
			self.stats['rr_size'] = 0
			self.stats['use_ready_rack'] = None
			if item.find('rr_size') is not None:
				self.stats['rr_size'] = int(item.find('rr_size').text)
				self.stats['use_ready_rack'] = True
			
			self.stats['rof'] = 0
			if item.find('rof') is not None:
				self.stats['rof'] = int(item.find('rof').text)
			
			# ammo load stats: current selections are TEMP
			self.stats['loaded_ammo'] = 'AP'
			self.stats['reload_ammo'] = 'AP'
			# starting amounts are TEMP
			self.stats['HE'] = (26, 3)
			self.stats['AP'] = (40, 3)
		
		# vehicle mg stats
		elif self.weapon_type in ['coax_mg', 'hull_mg']:
			self.stats['max_range'] = 3
			self.stats['fp'] = int(item.find('fp').text)
		
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
		# TEMP - FUTURE: will be set by weather handler
		self.rain_active = False
		
		# gun weapon attack effect
		self.gun_line = []			# path of projectile on screen
		self.gun_location = 0			# index number of current x,y location of projectile
		self.gun_timer = time.time()		# animation timer
		self.gun_click = 0			# time between animation updates
		self.gun_active = False
		
		# PSG highlight effect
		self.highlight_psg = None
		self.highlight_timer = time.time()	# animation timer
		self.highlight_click = 0		# time between animation updates
		self.highlight_char = 0			# current character of animation
		
		# on-map message
		self.message_lines = None		# lines of message text
		self.message_started = False		# flag that message has been drawn once
		self.message_x = 0			# location on which message is centered
		self.message_y = 0
		self.message_timer = time.time()
		self.message_lifetime = 0
	
	# start a gun projectile animation
	def InitGunEffect(self, x1, y1, x2, y2):
		self.gun_line = GetLine(x1, y1, x2, y2, los=True)
		self.gun_location = 0
		self.gun_timer = time.time()
		self.gun_click = float(config.getint('ArmCom2', 'animation_speed')) * 0.001
		self.gun_active = True
	
	# start a PSG highlight animation
	def InitHighlight(self, psg):
		self.highlight_psg = psg
		self.highlight_timer = time.time()
		self.highlight_click = float(config.getint('ArmCom2', 'animation_speed')) * 0.003
		self.highlight_char = 0
	
	# display a message on the scenario map
	def InitMessage(self, x, y, text):
		self.message_lines = wrap(text, 16)
		self.message_started = False
		self.message_x = x - 26
		self.message_y = y - 2
		# reposition messages that would appear off-screen
		if self.message_x < 8:
			self.message_x = 8
		elif self.message_x > WINDOW_WIDTH - 8:
			self.message_x = WINDOW_WIDTH - 8
		if self.message_y < 3:
			self.message_y = 3
		elif self.message_y + len(self.message_lines) > 56:
			self.message_y = 56 - len(self.message_lines)
		# TEMP - need to set according to cfg file
		self.message_lifetime = 1.2
	
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
		
		# PSG highlight
		if self.highlight_psg:
			if time.time() - self.highlight_timer >= self.highlight_click:
				updated_animation = True
				self.highlight_timer =  time.time()
				# remove animation if it's reached its end
				if self.highlight_char == len(HIGHLIGHT_CHARS) - 1:
					self.highlight_psg = None
				self.highlight_char += 1
		
		# on-map message
		if self.message_lines:
			
			# first appearance
			if not self.message_started:
				self.message_started = True
				self.message_timer = time.time()
				updated_animation = True
				
				# bit of a kludge but might work
				libtcod.console_rect(con, self.message_x+18, self.message_y+3,
					16, len(self.message_lines), True, libtcod.BKGND_SET)
			
			# remove if expired
			if self.message_timer + self.message_lifetime <= time.time():
				self.message_lines = None
				updated_animation = True
				self.anim_finished = True
				
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
			if self.gun_active:
				(x,y) = self.gun_line[self.gun_location]
				libtcod.console_put_char_ex(anim_con, x, y, 250, libtcod.white,
					libtcod.black)
			if self.highlight_psg:
				x = self.highlight_psg.screen_x - 26
				y = self.highlight_psg.screen_y - 3
				for (xm, ym) in HEX_EDGE_TILES:
					libtcod.console_put_char_ex(anim_con, x+xm, y+ym,
						HIGHLIGHT_CHARS[self.highlight_char],
						ACTIVE_MSG_COL, libtcod.black)
			if self.message_lines:
				n=0
				libtcod.console_set_default_background(anim_con, libtcod.black)
				for line in self.message_lines:
					libtcod.console_print_ex(anim_con, self.message_x,
						self.message_y+n, libtcod.BKGND_SET,
						libtcod.CENTER, line)
					n+=1
				libtcod.console_set_default_background(anim_con, KEY_COLOR)
		
		return updated_animation


# AI: used to determine actions of non-player-controlled units
class AI:
	def __init__(self, owner):
		self.owner = owner			# the PSG for whom this AI instance is
		self.turn_action = ''			# PSG action for this turn
	
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
			
			# suspected target
			if target.suspected:
				
				# no AF attack possible
				if weapon.stats['area_strength'] == 0:
					continue
			
			# known target
			else:
			
				# area fire target only but no area fire possible
				if target.af_target and not target.pf_target and weapon.stats['area_strength'] == 0:
					continue
				
				# point fire target only but no point fire possible
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
				attack_obj = CalcAttack(self.owner, weapon, target, True,
					assume_pivot=pivot_required)
				attack_list.append((attack_obj.final_column, weapon, target,
					True, False))
			
			if weapon.stats['point_strength'] > 0 and target.pf_target:
				attack_obj = CalcAttack(self.owner, weapon, target, False,
					assume_pivot=pivot_required)
				attack_list.append((attack_obj.final_column, weapon, target,
					False, False))
	
			del attack_obj
	
		# check for possible anti-tank attack
		if self.owner.infantry and target.vehicle and target.armour and distance == 0:
			attack_obj = CalcAttack(self.owner, None, target, False, at_attack=True)
			attack_list.append((attack_obj.final_column, None, target, False, True))
		
		# no attacks possible
		if len(attack_list) == 0:
			return None
		
		return attack_list
	
	# randomly determine action for this turn
	def GenerateAction(self):
		
		# TEMP - no actions
		return
		
		# TEMP: assume a defensive attitude
		d1, d2, roll = Roll2D6()
		
		# re-roll move result if we have an acquired target
		if roll <= 5 and self.owner.acquired_target:
			d1, d2, roll = Roll2D6()
		
		# modify result if infantry in open
		map_hex = GetHexAt(self.owner.hx, self.owner.hy)
		if self.owner.infantry and map_hex.terrain_type.af_modifier >= 0:
			roll -= 3
		
		if self.owner.vehicle:
			if len(self.owner.visible_enemies) == 0:
				self.turn_action = 'Move'
				print ('AI: no visible targets for ' + self.owner.GetName(true_name=True) +
					', moving automatically')
				return
			has_attack = False
			for psg in self.owner.visible_enemies:
				if self.GetBestAttacks(psg):
					has_attack = True
					break
			if not has_attack:
				self.turn_action = 'Move'
				print 'AI: No possible attacks from current position, moving'
				return
		
		if roll <= 5:
			self.turn_action = 'Move'
			if self.owner.gun:
				self.turn_action = 'Shoot'
		else:
			self.turn_action = 'Shoot'
		print 'AI: set turn action for ' + self.owner.GetName(true_name=True) + ' to ' + self.turn_action
	
	# execute an action for the current phase
	def DoPhaseAction(self):
		
		# Movement Phase actions
		if scenario.GetCurrentPhase() == 'Movement':
			
			# unit is not moving this turn
			if self.turn_action != 'Move':
				return
			print ('AI: Starting move action for ' + self.owner.GetName(true_name=True) +
				' at ' + str(self.owner.hx) + ',' + str(self.owner.hy))
			current_hex = GetHexAt(self.owner.hx, self.owner.hy)
			
			# Infantry
			if self.owner.infantry:
			
				# stay put if on objective
				if current_hex.objective:
					print 'AI: Already on objective, not moving'
					return
				
				# try to move to better terrain if possible
				move_paths = []
				current_modifier = current_hex.terrain_type.af_modifier
				
				# check paths to all hexes within 4
				hex_list = GetHexesWithin(current_hex.hx, current_hex.hy, 4)
				for (hx, hy) in hex_list:
					map_hex = GetHexAt(hx, hy)
					if map_hex.IsOccupied() > -1:
						continue
					if map_hex.terrain_type.af_modifier >= current_modifier:
						continue
					hex_path = GetHexPath(current_hex.hx, current_hex.hy,
						hx, hy, psg=self.owner)
					# no move path possible
					if len(hex_path) == 0:
						continue
					move_paths.append((map_hex.terrain_type.af_modifier, hex_path))
				
				if len(move_paths) == 0:
					print 'AI: No move paths to a better location, not moving'
					return
				
				sorted(move_paths,key=itemgetter(0))
				
				# try to move along best path in list
				(af_modifier, hex_path) = move_paths[0]
				(hx, hy) = hex_path[-1]
				print 'AI: Moving along path to ' + str(hx) + ',' + str(hy)
				for (hx, hy) in hex_path[1:-1]:
					print 'AI: Trying to move to ' + str(hx) + ',' + str(hy)
					if not self.owner.CheckMoveInto(hx, hy):
						print 'AI: Move along path was not possible, stopping here'
						return
					self.owner.MoveInto(hx, hy)
				print 'AI: Move completed'
			
			# Vehicles - if no valid target within range, move toward closest target
			if self.owner.vehicle:
				
				if len(self.owner.visible_enemies) > 0:
					for psg in self.owner.visible_enemies:
						if self.GetBestAttacks(psg):
							print 'AI: Have a possible attack, not moving'
							return
				
				move_targets = []
				for psg in scenario.unit_list:
					if psg.owning_player == self.owner.owning_player:
						continue
					distance = GetHexDistance(self.owner.hx, self.owner.hy,
						psg.hx, psg.hy)
					move_targets.append((distance, psg))
				
				# sort by nearest to unit at top
				reversed(sorted(move_targets,key=itemgetter(0)))
				
				for (distance, psg) in move_targets:
					print 'AI: Found an enemy at ' + str(psg.hx) + ',' + str(psg.hy)
					hex_path = GetHexPath(self.owner.hx, self.owner.hy,
						psg.hx, psg.hy, psg=self.owner)
					# no move path possible
					if len(hex_path) == 0:
						print 'AI: No path to ' + str(psg.hx) + ',' + str(psg.hy)
						continue
					for (hx, hy) in hex_path[1:-1]:
						print 'AI: Trying to move to ' + str(hx) + ',' + str(hy)
						if not self.owner.CheckMoveInto(hx, hy):
							print 'AI: Move along path was not possible, stopping here'
							return
						self.owner.MoveInto(hx, hy)
					print 'AI: Move completed'
					return
				
				print 'AI: Could not find a path to an enemy, not moving'
			
			# TEMP - no other move actions
		
		# Shooting Phase actions
		elif scenario.GetCurrentPhase() == 'Shooting':
			
			print 'AI: Starting shoot action for ' + self.owner.GetName(true_name=True)
			
			# build list of possible targets
			target_list = []
			for psg in scenario.unit_list:
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
				if target_attack_list:
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
		
		self.base_to_hit = 0		# base score required to hit
		self.modifiers = []		# list of dice roll modifiers
		self.final_to_hit = 0		# final to-hit score required
		
		self.base_ap = 0		# base armour-penetration roll required
		self.final_ap = 0		# final "


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
	# TODO: add maximum height
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


# a single terrain hex on the game map
# must have elevation and terrain type set before use
class MapHex:
	def __init__(self, hx, hy):
		self.hx = hx
		self.hy = hy
		
		self.unit_stack = []			# list of units in this hex
		
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
	
	# check to see if this hex has been captured
	def CheckCapture(self, no_message=False):
		# this hex is not an objective
		if self.objective is False: return
		
		resident_psg = None
		for psg in scenario.unit_list:
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
			text += ' captured an objective!'
			(x,y) = PlotHex(self.hx, self.hy)
			#Message(text, x+26, y+2)
		
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
		
		# check visible hextants for commander crew position
		crew_position = scenario.player_unit.crew_positions[0]
		if crew_position.hatch is None:
			visible_hextants = crew_position.closed_visible
			max_distance = MAX_BU_LOS_DISTANCE
		else:
			if crew_position.hatch == 'Closed':
				visible_hextants = crew_position.closed_visible
				max_distance = MAX_BU_LOS_DISTANCE
			else:
				visible_hextants = crew_position.open_visible
				max_distance = MAX_LOS_DISTANCE
		
		# TODO: rotate visible hextants based on turret/hull direction
		
		# raycast from crewman position to each map hex
		#start_time = time.time()
		for (hx, hy) in scenario.hex_map.hexes:
			# skip already visible hexes
			if scenario.hex_map.hexes[(hx, hy)].vis_to_player: continue
			
			# skip hexes not visible to crew position
			direction = GetDirectionToward(scenario.player_unit.hx, scenario.player_unit.hy, hx, hy)
			if direction not in visible_hextants: continue
			
			# get max LoS distance
			distance = GetHexDistance(scenario.player_unit.hx, scenario.player_unit.hy, hx, hy)
			if distance > max_distance: continue
			
			los_line = GetLoS(scenario.player_unit.hx, scenario.player_unit.hy, hx, hy)
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
# TODO: change to BattleEncounter ?
class Scenario:
	def __init__(self, map_w, map_h):
		
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
		
		self.active_player = 0			# currently active player (0 or 1)
		self.current_phase = 0			# current action phase (full list defined by PHASE_LIST)
		
		self.unit_list = []			# list of all units in play
		self.active_unit = None			# currently active unit
		self.player_unit = None			# pointer to player-controlled unit
		self.selected_crew_position = None	# selected crew position in player unit
		self.player_target = None		# unit currently being targeted by player unit
		
		self.player_direction = 3		# direction of player-friendly forces
		self.enemy_direction = 0		# direction of enemy forces
		
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
	
	# check for automatic spotting and identification of units
	def DoAutomaticSpotCheck(self):
		for unit in self.unit_list:
			if unit.known and unit.identified: continue
			map_hex = GetHexAt(unit.hx, unit.hy)
			if map_hex.terrain_type.terrain_mod != 0: continue
			
			# unit is in open terrain
			for unit2 in self.unit_list:
				# check for adjacent enemies
				if unit2.owning_player == unit.owning_player: continue
				if GetHexDistance(unit.hx, unit.hy, unit2.hx, unit2.hy) == 1:
					unit.SpotMe()
					unit.IdentifyMe()
					break
				
				# check for enemy in LoS
				if (unit.hx, unit.hy) in GetLoS(unit2.hx, unit2.hy, unit.hx, unit.hy):
					unit.SpotMe()
					unit.IdentifyMe()
					break
	
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
			map_hex = GetHexAt(unit.hx, unit.hy)
			if not map_hex.vis_to_player: continue
			target_list.append(unit)
		
		# no possible targets
		if len(target_list) == 0:
			return
		
		# no target selected yet, select the first one
		if self.player_target is None:
			self.player_target = target_list[0]
			return
		
		# last target in list selected, select the first one
		if self.player_target == target_list[-1]:
			self.player_target = target_list[0]
			return
		
		# select next target in list
		n = target_list.index(self.player_target)
		self.player_target = target_list[n+1]
	
	
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
			'Gun': 20,
			'Infantry': 30,
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
		self.unit_list.extend(enemy_oob)
		
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
		for psg in self.unit_list:
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
	
	# return a text string for the current turn phase
	def GetCurrentPhase(self):
		return PHASE_LIST[self.current_phase]
	
	# do enemy AI actions for this phase
	def DoAIPhase(self):
		
		# TEMP
		return
		
		# build a list of units that can be activated this phase
		activate_list = []
		for psg in self.unit_list:
			if psg.owning_player == 0: continue
			activate_list.append(psg)
		shuffle(activate_list)
		for psg in activate_list:
			scenario.active_unit = psg
			UpdateUnitConsole()
			DrawScreenConsoles()
			libtcod.console_flush()
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
		
		# crew actions -> Movement
		if self.GetCurrentPhase() == 'Crew Actions':
			self.SetPhase('Movement')
			self.active_cmd_menu = 'movement_root'
			self.selected_crew_position = None
		
		# Movement -> Shooting Phase
		elif self.GetCurrentPhase() == 'Movement':
			self.SetPhase('Shooting')
			self.active_cmd_menu = 'shooting_root'
		
		# Shooting -> Close Combat
		elif self.GetCurrentPhase() == 'Shooting':
			
			self.SetPhase('Close Combat')
			self.active_cmd_menu = 'cc_root'
			self.active_unit = None
			
		# Close Combat Phase -> New Active Player and Crew Actions Phase
		elif self.GetCurrentPhase() == 'Close Combat':
			
			if self.active_player == 0:
				self.active_player = 1
				# clear active PSG
				self.active_unit = None
			else:
				# end of turn, check for scenario end
				#self.CheckForEnd()
				if self.winner is not None:
					# display scenario report
					self.DisplayEndScreen()
					# delete saved game
					EraseGame()
					return
				self.AdvanceClock()
				UpdateScenInfoConsole()
				self.active_player = 0
				self.active_unit = None
				scenario.SelectNextPSG()
				UpdatePlayerUnitConsole()
			self.SetPhase('Crew Actions')
			self.active_cmd_menu = 'crew_actions'
			# select first crew position in player unit
			self.selected_crew_position = self.player_unit.crew_positions[0]
			
			for psg in self.unit_list:
				if psg.owning_player == self.active_player:
					psg.DoRecoveryTests()
		
		# do automatic actions for active player's units for this phase
		for psg in self.unit_list:
			if psg.owning_player == self.active_player:
				psg.ResetForPhase()
		
		self.BuildCmdMenu()
		DrawScreenConsoles()
		libtcod.console_flush()
		SaveGame()
		
		
		SaveGame()
	
	# select the next player PSG; or the first one in the list if none selected
	def SelectNextPSG(self):
		
		reverse = False
		if libtcod.console_is_key_pressed(libtcod.KEY_SHIFT):
			reverse = True
		
		player_psgs = []
		for psg in self.unit_list:
			if psg.owning_player == 0: player_psgs.append(psg)
		
		if len(player_psgs) == 0:
			print 'ERROR: No player PSGs to select!'
			return
		
		# none selected yet, select the first one in the list
		if self.active_unit is None:
			self.active_unit = player_psgs[0]
			return
		
		n = 0
		for psg in player_psgs:
			if psg == self.active_unit:
				# try to select the previous unit in the list
				if reverse:
					if n > 0:
						self.active_unit = player_psgs[n-1]
					else:
						self.active_unit = player_psgs[-1]
					return
				# try to select the next unit in the list
				else:
					if n < len(player_psgs) - 1:
						self.active_unit = player_psgs[n+1]
					else:
						self.active_unit = player_psgs[0]
					return
			n += 1
		
	
	# rebuild a list of commands for the command menu based on current phase and
	#   game state
	def BuildCmdMenu(self):
		
		# clear any existing command menu
		self.cmd_menu.Clear()
		
		# don't display anything if human player is not active
		if scenario.active_player != 0:
			UpdateCmdConsole()
			return
		
		# crew actions
		if self.active_cmd_menu == 'crew_actions':
			# TODO: add options back in
			
			menu_option = self.cmd_menu.AddOption('toggle_hatch', 'H', 'Toggle Hatch')
			if self.selected_crew_position.hatch is None:
				menu_option.inactive = True
				menu_option.desc = 'Crew position has no hatch'
		
		# movement phase
		elif self.active_cmd_menu == 'movement_root':
			self.cmd_menu.AddOption('rotate_turret_cc', 'Q', 'Turret C/clockwise')
			self.cmd_menu.AddOption('rotate_turret_cw', 'E', 'Turret Clockwise')
			self.cmd_menu.AddOption('pivot_hull_port', 'A', 'Pivot to Port')
			self.cmd_menu.AddOption('pivot_hull_stb', 'D', 'Pivot to Starboard')
			
			map_hex1 = GetHexAt(scenario.player_unit.hx, scenario.player_unit.hy)
			
			menu_option = self.cmd_menu.AddOption('move_forward', 'W', 'Forward')
			(hx, hy) = GetAdjacentHex(scenario.player_unit.hx,
				scenario.player_unit.hy, scenario.player_unit.facing)
			if not scenario.player_unit.CheckMoveInto(hx, hy):
				menu_option.inactive = True
			else:
				map_hex2 = GetHexAt(hx, hy)
				mp_cost = GetMPCostToMove(scenario.player_unit, map_hex1, map_hex2)
				if mp_cost > scenario.player_unit.mp:
					menu_option.inactive = True
					menu_option.desc = str(mp_cost) + ' MP required'
			
			menu_option = self.cmd_menu.AddOption('move_backward', 'S', 'Backward')
			(hx, hy) = GetAdjacentHex(scenario.player_unit.hx,
				scenario.player_unit.hy,
				CombineDirs(scenario.player_unit.facing, 3))
			if not scenario.player_unit.CheckMoveInto(hx, hy):
				menu_option.inactive = True
			else:
				map_hex2 = GetHexAt(hx, hy)
				mp_cost = GetMPCostToMove(scenario.player_unit, map_hex1, map_hex2)
				if mp_cost > scenario.player_unit.mp:
					menu_option.inactive = True
					menu_option.desc = str(mp_cost) + ' MP required'
			
		# shooting phase menu
		elif self.active_cmd_menu == 'shooting_root':
			# no target selected yet
			if not scenario.player_target:
				self.cmd_menu.AddOption('next_target', 'T', 'Select Target')
			# already have a target
			else:
				self.cmd_menu.AddOption('next_target', 'T', 'Next Target')
				self.cmd_menu.AddOption('clear_target', 'Bksp', 'Clear Target')
				
				# add commands to try to fire weapons
				n = 0
				for weapon in scenario.player_unit.weapon_list:
					cmd = 'fire_' + str(n)
					desc = 'Fire ' + weapon.GetName()
					menu_option = self.cmd_menu.AddOption(cmd, str(n+1), desc)
					
					# check that weapon can fire
					if weapon.fired:
						menu_option.inactive = True
						menu_option.desc = 'Cannot fire this weapon group again this turn'
					
					# check for RoF exception
					if weapon.rof_target is not None:
						if weapon.rof_target == scenario.player_target:
							menu_option.inactive = False
							menu_option.desc = 'Maintained RoF against this target'
					
					n += 1
			
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


# remove a saved game, either because the scenario is over or the player abandoned it
def EraseGame():
	os.remove('savegame')


# calculate an attack
def CalcAttack(attacker, weapon, target, assume_pivot=False):
	# create a new attack object
	attack_obj = Attack(attacker, weapon, target)
	
	# TEMP: assume gun AP attack
	
	# calculate base to-hit roll required
	
	# get distance to target
	distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
	
	BASE_TO_HIT = [
		[10,8,7],		# <= 1 hex range
		[9,7,7],		# 2 hex range
		[9,7,7],		# 3 "
		[8,6,8],		# 4 "
		[7,5,8],		# 5 "
		[6,4,7]			# 6 "
	]
	
	if distance <= 1:
		column = 0
	else:
		column = distance - 1
	to_hit_list = BASE_TO_HIT[column]
	
	if target.vehicle:
		attack_obj.base_to_hit = to_hit_list[0]
	else:
		attack_obj.base_to_hit = to_hit_list[1]
	
	#################################
	# Calculate dice roll modifiers
	#################################
	
	# Long Range gun Modifiers
	if weapon.stats['long_range'] == 'L':
		if 4 <= distance <= 6:
			attack_obj.modifiers.append(('L Weapon', -1))
	elif weapon.stats['long_range'] == 'LL':
		if 4 <= distance <= 5:
			attack_obj.modifiers.append(('LL Weapon', -1))
		elif distance == 6:
			attack_obj.modifiers.append(('LL Weapon', -2))
	
	# calibre range modifiers
	if weapon.stats['calibre'] <= 40:
		if 4 <= distance <= 6:
			attack_obj.modifiers.append(('<=40mm', 1))
	elif weapon.stats['calibre'] <= 57:
		if 4 <= distance <= 5:
			attack_obj.modifiers.append(('<=57mm', 1))
		elif distance == 6:
			attack_obj.modifiers.append(('<=57mm', 2))
	
	# moving vehicle target
	if target.vehicle and target.moved:
		attack_obj.modifiers.append(('Target vehicle moved', 2))
	
	# target terrain modifier
	map_hex = GetHexAt(target.hx, target.hy)
	if map_hex.terrain_type.terrain_mod != 0:
		attack_obj.modifiers.append(('Target terrain', 0-map_hex.terrain_type.terrain_mod))
	
	# apply modifiers to calculate final to-hit score required 
	attack_obj.final_to_hit = attack_obj.base_to_hit
	for (text, mod) in attack_obj.modifiers:
		attack_obj.final_to_hit += mod
	
	# normalize final to-hit required
	# FUTURE: if < 2 required, attack not possible
	if attack_obj.final_to_hit > 11:
		attack_obj.final_to_hit = 11

	return attack_obj


# calculate a armour penetration roll
def CalcAPRoll(attack_obj):
	
	# calculate base AP score required
	gun_rating = str(attack_obj.weapon.stats['calibre']) + attack_obj.weapon.stats['long_range']
	
	if gun_rating == '37L':
		base_ap = 9
	elif gun_rating == '37':
		base_ap = 8
	
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
		facing = GetFacing(attack_obj.attacker, attack_obj.target)
		target_armour = attack_obj.target.armour[facing]
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
def GetMPCostToMove(unit, map_hex1, map_hex2):

	direction = GetDirectionToAdjacent(map_hex1.hx, map_hex1.hy, map_hex2.hx, map_hex2.hy)
	if direction in map_hex1.dirt_road_links:
		# road movement
		column = 2
	elif map_hex2.terrain_type.difficult:
		# movement in difficult terrain
		column = 1
	else:
		# open terrain
		column = 0
	
	if unit.movement_class == 'Infantry':
		table = 0
	elif unit.movement_class == 'Tank':
		table = 1
	elif unit.movement_class == 'Fast Tank':
		table = 2
	
	return MP_COSTS[table][column]


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
				# TEMP
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


# initiate an attack by one unit on another
def InitAttack(attacker, weapon, target):
	
	distance = GetHexDistance(attacker.hx, attacker.hy, target.hx, target.hy)
	
	# determine if a pivot would be required
	pivot_required = False
	if not attacker.infantry and distance > 0:
		bearing = GetRelativeBearing(attacker, target)
		if 30 < bearing < 330:
			pivot_required = True

	# send information to CalcAttack, which will return an Attack object with the
	#   calculated stats to use for the attack
	attack_obj = CalcAttack(attacker, weapon, target, assume_pivot=pivot_required)
	
	# do the pivot if it was required
	if pivot_required:
		direction = GetDirectionToward(attacker.hx, attacker.hy, target.hx,
			target.hy)
		attacker.PivotToFace(direction)
		UpdateUnitConsole()
		DrawScreenConsoles()
		libtcod.console_blit(attack_con, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		libtcod.console_flush()
	
	# if not close combat and player wasn't attacker, display LoS from attacker to target
	if distance > 0 and attacker.owning_player == 1:
		line = GetLine(attacker.screen_x, attacker.screen_y, target.screen_x,
			target.screen_y)
		for (x,y) in line[2:-2]:
			libtcod.console_set_char(con, x, y, 250)
			libtcod.console_set_char_foreground(con, x, y, libtcod.red)
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_flush()
			Wait(5)
	
	# display attack console and wait for confirmation before proceeding
	# player has chance to cancel a ranged attack at this point
	DisplayAttack(attack_obj)
	cancel_attack = WaitForEnter(allow_cancel=True)
	if attacker == scenario.player_unit and cancel_attack:
		DrawScreenConsoles()
		return
	
	# set unit fired flag
	attacker.fired = True
	# mark this weapon and all others in same group as having fired
	for check_weapon in attacker.weapon_list:
		if check_weapon.firing_group == weapon.firing_group:
			check_weapon.fired = True
	
	# clear player target so that LoS display is removed
	if attacker == scenario.player_unit:
		scenario.player_target = None
	
	# clear any LoS drawn above from screen
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
	elif weapon.weapon_type in ['coax_mg', 'hull_mg']:
		pass
		#MGAttackAnimation(attack_obj)
	
	# resolve attack
	# TODO: change to CalcPointFire?
	target.ResolveAttack(attack_obj)
	
	# TODO: handle newly acquired target
	
	# handle reloading procedure for gun
	if weapon.weapon_type == 'gun':
		# 'unload' fired shell
		weapon.stats['loaded_ammo'] = None
		
		# check for ready rack use
		use_rr = False
		if weapon.stats['use_ready_rack'] is not None:
			if weapon.stats['use_ready_rack']:
				use_rr = True
		
		# check for new shell of reload type and load it if possible
		(main_ammo, rr_ammo) = weapon.stats[weapon.stats['reload_ammo']]
		if use_rr:
			if rr_ammo > 0:
				rr_ammo -= 1
				weapon.stats['loaded_ammo'] = weapon.stats['reload_ammo']
			else:
				# no shell of the right type in the ready rack, but we can
				#   default to general stores
				weapon.stats['use_ready_rack'] = False
				use_rr = False
		
		if not use_rr:
			if main_ammo > 0:
				main_ammo -= 1
				weapon.stats['loaded_ammo'] = weapon.stats['reload_ammo']
		
		# update new ammo amounts
		weapon.stats[weapon.stats['reload_ammo']] = (main_ammo, rr_ammo)
		
		# no shell loaded, can't maintain RoF
		if weapon.stats['loaded_ammo'] == None:
			return
		
	# check for RoF; first clear any previous stored RoF target
	weapon.rof_target = None
	
	# no RoF possible
	if weapon.stats['rof'] == 0:
		return
	if target not in scenario.unit_list:
		return
	
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
		weapon.rof_target = target
		if attacker == scenario.player_unit:
			Message('Maintained Rate of Fire', target_unit=attacker)


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
	#libtcod.console_set_default_background(attack_con, libtcod.black)
	if unit.portrait is not None:
		temp = LoadXP(unit.portrait)
		if temp is not None:
			libtcod.console_blit(temp, 0, 0, 0, 0, attack_con, 1, 2)
			del temp
	libtcod.console_print_ex(attack_con, 13, 10, libtcod.BKGND_NONE,
		libtcod.CENTER, unit.GetName())
	
	# roll description
	if ap_roll:
		text = ' hit by ' + attack_obj.weapon.GetName()
	else:
		text = 'firing ' + attack_obj.weapon.GetName() + ' at'
	libtcod.console_print_ex(attack_con, 13, 11, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	# target name and portrait if to-hit roll
	if not ap_roll:
		libtcod.console_print_ex(attack_con, 13, 12, libtcod.BKGND_NONE,
			libtcod.CENTER, attack_obj.target.GetName())
		libtcod.console_set_default_background(attack_con, PORTRAIT_BG_COL)
		libtcod.console_rect(attack_con, 1, 13, 24, 8, False, libtcod.BKGND_SET)
		#libtcod.console_set_default_background(attack_con, libtcod.black)
		if attack_obj.target.portrait is not None:
			temp = LoadXP(attack_obj.target.portrait)
			if temp is not None:
				libtcod.console_blit(temp, 0, 0, 0, 0, attack_con, 1, 13)
				del temp

	# base to-hit / AP roll
	if ap_roll:
		text = 'Base roll required: ' + str(attack_obj.base_ap)
	else:
		text = 'Base to-hit: ' + str(attack_obj.base_to_hit)
	libtcod.console_print_ex(attack_con, 13, 22, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	# list of roll modifiers
	libtcod.console_set_default_background(attack_con, TITLE_BG_COL)
	libtcod.console_rect(attack_con, 1, 24, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 13, 24, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Roll Modifiers')
	y = 26
	if len(attack_obj.modifiers) == 0:
		libtcod.console_print_ex(attack_con, 13, y, libtcod.BKGND_NONE,
			libtcod.CENTER, 'None')
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
		y += 1
	
	# final to-hit/AP roll required
	if ap_roll:
		text = 'Final roll required: ' + str(attack_obj.final_ap)
	else:
		text = 'Final to-hit: ' + str(attack_obj.final_to_hit)
	libtcod.console_print_ex(attack_con, 13, 44, libtcod.BKGND_NONE,
		libtcod.CENTER, text)
	
	libtcod.console_rect(attack_con, 1, 46, 24, 1, False, libtcod.BKGND_SET)
	
	# player attacks have chance to cancel
	if not ap_roll and attack_obj.attacker == scenario.player_unit:
		libtcod.console_print_ex(attack_con, 13, 55, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Backspace to Cancel')
	libtcod.console_print_ex(attack_con, 13, 57, libtcod.BKGND_NONE,
		libtcod.CENTER, 'Enter to Roll')
	
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
	print 'Terrain Generation: ' + str(hex_num) + ' map hexes'
	
	# clear map
	for (hx, hy) in map_hex_list:
		map_hex = GetHexAt(hx, hy)
		map_hex.SetTerrainType('Fields')
		map_hex.SetElevation(1)
		map_hex.dirt_road_links = []
	
	# terrain settings
	# FUTURE: will be supplied by battleground settings
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
	#                             Elevation / Hills                                  #
	##################################################################################
	
	print 'Terrain Generation: Generating ' + str(hill_num) + ' hills'
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
	
	print 'Terrain Generation: Generating ' + str(forest_num) + ' forest areas'
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
	print 'Terrain Generation: Generating ' + str(num_villages) + ' villages'
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
	
	print 'Terrain Generation: Generating ' + str(fields_num) + ' tall field areas'
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
	print 'Terrain Generation: Generating ' + str(num_ponds) + ' ponds'
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
	
	##################################################################################
	#                                   Roads                                        #
	##################################################################################
	
	# add two roads
	CreateRoad()
	CreateRoad(vertical=False)



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
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
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
		libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
		libtcod.console_flush()
		Wait(pause_time)
	
	libtcod.console_clear(map_gui_con)
	DrawScreenConsoles()
	libtcod.console_blit(attack_con, 0, 0, 30, 60, 0, 0, 0)
	libtcod.console_flush()


# add a new message to the message log and displays it on the map
# for now, a unit must be specified
def Message(text, target_unit=None):
	if target_unit is None: return
	for (hx, hy) in VP_HEXES:
		(map_hx, map_hy) = scenario.map_vp[(hx, hy)]
		if map_hx == target_unit.hx and map_hy == target_unit.hy:
			(x,y) = PlotHex(hx, hy)
			x += 27
			y += 4
			scenario.messages.append(text)
			scenario.anim.InitMessage(x, y, text)
			DrawScreenConsoles()
			WaitForAnimation()
			DrawScreenConsoles()
			libtcod.console_flush()
			return
	print 'ERROR: unit for message not on viewport'


# draw the map viewport console
# each hex is 5x5 cells, but edges overlap with adjacent hexes
def UpdateVPConsole():

	libtcod.console_set_default_background(map_vp_con, libtcod.black)
	libtcod.console_clear(map_vp_con)
	scenario.map_index = {}
	
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
	
	# section title backgrounds
	libtcod.console_set_default_background(player_unit_con, SECTION_BG_COL)
	libtcod.console_rect(player_unit_con, 0, 2, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_rect(player_unit_con, 0, 6, 11, 1, False, libtcod.BKGND_SET)
	libtcod.console_rect(player_unit_con, 13, 6, 11, 1, False, libtcod.BKGND_SET)
	libtcod.console_rect(player_unit_con, 0, 13, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_set_default_background(player_unit_con, libtcod.black)
	
	# section titles
	libtcod.console_set_default_foreground(player_unit_con, TITLE_COL)
	libtcod.console_print(player_unit_con, 0, 2, 'Gun         Load Next RR')
	libtcod.console_print(player_unit_con, 0, 6, 'Rounds  RR')
	libtcod.console_print(player_unit_con, 18, 6, 'Status')
	libtcod.console_print(player_unit_con, 0, 13, 'Crew')
	libtcod.console_set_default_foreground(player_unit_con, INFO_TEXT_COL)
	
	# main armament info
	if len(scenario.player_unit.weapon_list) > 0:
		weapon = scenario.player_unit.weapon_list[0]
		libtcod.console_print(player_unit_con, 0, 3, weapon.GetName())
	
		# main armament ammo
		if weapon.stats['loaded_ammo'] is None:
			text = 'None'
		else:
			text = weapon.stats['loaded_ammo']
		libtcod.console_print_ex(player_unit_con, 14, 3, libtcod.BKGND_NONE, libtcod.CENTER,
			text)
		if weapon.stats['reload_ammo'] is None:
			text = 'None'
		else:
			text = weapon.stats['reload_ammo']
		libtcod.console_print_ex(player_unit_con, 19, 3, libtcod.BKGND_NONE, libtcod.CENTER,
			text)
		if weapon.stats['use_ready_rack'] is None:
			text = 'NA'
		else:
			if weapon.stats['use_ready_rack']:
				text = 'Y'
			else:
				text = 'N'
		libtcod.console_print_ex(player_unit_con, 23, 3, libtcod.BKGND_NONE, libtcod.RIGHT,
			text)
		
		y = 7
		for ammo_type in AMMO_TYPE_ORDER:
			if weapon.stats[ammo_type] is not None:
				libtcod.console_print(player_unit_con, 0, y, ammo_type)
				(ammo, rr_ammo) = weapon.stats[ammo_type]
				libtcod.console_print_ex(player_unit_con, 6, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, str(ammo))
				libtcod.console_print_ex(player_unit_con, 9, y, libtcod.BKGND_NONE,
					libtcod.RIGHT, str(rr_ammo))
				y+=1
		y+=1
		libtcod.console_print(player_unit_con, 0, y, 'Max')
		libtcod.console_print_ex(player_unit_con, 6, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, str(scenario.player_unit.max_ammo))
		if weapon.stats['rr_size'] == 0:
			text = '--'
		else:
			text = str(weapon.stats['rr_size'])
		libtcod.console_print_ex(player_unit_con, 9, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
		
	# unit statuses
	if scenario.player_unit.moved:
		text = 'Moving'
	else:
		text = 'Stopped'
	libtcod.console_print_ex(player_unit_con, 23, 7, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	if scenario.player_unit.fired:
		text = 'Fired'
	else:
		text = ''
	libtcod.console_print_ex(player_unit_con, 23, 8, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	
	# Movement Class and mp
	libtcod.console_set_default_foreground(player_unit_con, libtcod.light_green)
	libtcod.console_print(player_unit_con, 0, 12, scenario.player_unit.movement_class)
	if scenario.GetCurrentPhase() == 'Movement':
		text = str(scenario.player_unit.mp) + '/' + str(scenario.player_unit.max_mp) + ' MP'
		libtcod.console_print_ex(player_unit_con, 23, 12, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
	libtcod.console_set_default_foreground(player_unit_con, INFO_TEXT_COL)
	
	# list of crew and crew positions
	if unit.crew_positions is not None:
		y = 14
		for position in unit.crew_positions:
			
			# highlight if selected
			if scenario.selected_crew_position is not None:
				if scenario.selected_crew_position == position:
					libtcod.console_set_default_background(player_unit_con, SELECTED_WEAPON_COLOR)
					libtcod.console_rect(player_unit_con, 0, y, 24,
						2, True, libtcod.BKGND_SET)
					libtcod.console_set_default_background(player_unit_con, libtcod.black)
		
			libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
			text = CREW_POSITION_ABB[position.name]
			libtcod.console_print(player_unit_con, 0, y, text)
			
			if position.crewman is None:
				libtcod.console_set_default_foreground(player_unit_con, INFO_TEXT_COL)
				text = '[Empty]'
			else:
				text = position.crewman.GetName(lastname=True)
			libtcod.console_print(player_unit_con, 5, y, text)
			
			libtcod.console_set_default_foreground(player_unit_con, INFO_TEXT_COL)
			
			# hatch status
			if position.hatch is None:
				text = '--'
			else:
				if position.hatch == 'Closed':
					text = 'BU'
				else:
					text = 'CE'
			libtcod.console_print_ex(player_unit_con, 23, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
			
			libtcod.console_hline(player_unit_con, 0, y+2, 24)
			
			y += 3
	
	# TEMP
	return
	
	# unit type
	libtcod.console_set_default_foreground(player_unit_con, HIGHLIGHT_COLOR)
	libtcod.console_print(player_unit_con, 0, 1, psg.GetStepName())
	libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
	
	# number of steps in unit
	text = 'x' + str(psg.num_steps)
	libtcod.console_print_ex(player_unit_con, 23, 1, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	
	# vehicle portrait
	libtcod.console_set_default_background(player_unit_con, PORTRAIT_BG_COL)
	libtcod.console_rect(player_unit_con, 0, 2, 24, 8, False, libtcod.BKGND_SET)
	libtcod.console_set_default_background(player_unit_con, libtcod.black)
	
	if psg.portrait is not None:
		temp = LoadXP(psg.portrait)
		if temp is not None:
			x = 11 - int(libtcod.console_get_width(temp) / 2)
			libtcod.console_blit(temp, 0, 0, 0, 0, player_unit_con, x, 2)
		else:
			print 'ERROR: unit portrait not found: ' + psg.portrait
	
	# unit special skills
	libtcod.console_set_default_foreground(player_unit_con, libtcod.black)
	if psg.recce:
		libtcod.console_print(player_unit_con, 0, 2, 'Recce')
	
	libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
	
	# morale and skill levels
	libtcod.console_set_default_background(player_unit_con, libtcod.dark_grey)
	libtcod.console_rect(player_unit_con, 0, 10, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print(player_unit_con, 0, 10, MORALE_DESC[str(psg.morale_lvl)])
	libtcod.console_print_ex(player_unit_con, 23, 10, libtcod.BKGND_NONE, libtcod.RIGHT,
		SKILL_DESC[str(psg.skill_lvl)])
	
	# weapon list
	# TODO: only show max three, allow scrolling
	libtcod.console_set_default_foreground(player_unit_con, libtcod.grey)
	libtcod.console_print_ex(player_unit_con, 23, 11, libtcod.BKGND_NONE, libtcod.RIGHT,
		'Rng AF PF')
	libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
	y = 12
	libtcod.console_set_default_background(player_unit_con, TITLE_BG_COL)
	
	for weapon in psg.weapon_list:
		libtcod.console_set_default_background(player_unit_con, WEAPON_LIST_COLOR)
		# highlight selected weapon if active and in shooting phase
		if scenario.active_unit == psg and scenario.GetCurrentPhase() == 'Shooting' and psg.selected_weapon is not None:
			if weapon == psg.selected_weapon:
				libtcod.console_set_default_background(player_unit_con, SELECTED_WEAPON_COLOR)
		libtcod.console_rect(player_unit_con, 0, y, 24, 1, False, libtcod.BKGND_SET)
		libtcod.console_print(player_unit_con, 0, y, weapon.stats['name'])
		text = str(weapon.stats['max_range']) + weapon.stats['long_range']
		libtcod.console_print_ex(player_unit_con, 17, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
		if weapon.stats['area_strength'] == 0:
			text = '-'
		else:
			text = str(weapon.stats['area_strength'])
		libtcod.console_print_ex(player_unit_con, 20, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
		if weapon.stats['point_strength'] == 0:
			text = '-'
		else:
			text = str(weapon.stats['point_strength'])
		libtcod.console_print_ex(player_unit_con, 23, y, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
		y += 1
	
	# armour ratings if any
	if psg.armour:
		text = ('Armour ' + str(psg.armour['front']) + '/' + str(psg.armour['side']))
		libtcod.console_print(player_unit_con, 0, 16, text)
	
	# Movement class
	libtcod.console_set_default_foreground(player_unit_con, libtcod.green)
	libtcod.console_print_ex(player_unit_con, 23, 16, libtcod.BKGND_NONE,
		libtcod.RIGHT, psg.movement_class)
	
	# display MP if in movement phase
	if scenario.GetCurrentPhase() == 'Movement' and scenario.active_player == psg.owning_player:
		text = str(psg.mp) + '/' + str(psg.max_mp) + ' MP'
		libtcod.console_print_ex(player_unit_con, 23, 17, libtcod.BKGND_NONE,
			libtcod.RIGHT, text)
	
	# status flags
	libtcod.console_set_default_foreground(player_unit_con, libtcod.lighter_blue)
	libtcod.console_set_default_background(player_unit_con, TITLE_BG_COL)
	libtcod.console_rect(player_unit_con, 0, 19, 24, 1, False, libtcod.BKGND_SET)
	
	# movement- and position-related flags
	if psg.moved:
		libtcod.console_print(player_unit_con, 0, 19, 'Moved')
	elif psg.changed_facing:
		libtcod.console_print(player_unit_con, 0, 19, 'Changed Facing')
	
	# fired last turn
	if psg.fired:
		libtcod.console_print_ex(player_unit_con, 23, 19, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'Fired')
	
	# negative statuses
	libtcod.console_set_default_foreground(player_unit_con, libtcod.light_red)
	libtcod.console_set_default_background(player_unit_con, libtcod.darkest_red)
	libtcod.console_rect(player_unit_con, 0, 20, 24, 1, False, libtcod.BKGND_SET)
	
	if psg.pin_points > 0:
		libtcod.console_print(player_unit_con, 0, 20, 'Pin Pts: ' + str(psg.pin_points))
	if psg.suppressed:
		libtcod.console_print_ex(player_unit_con, 23, 20, libtcod.BKGND_NONE,
			libtcod.RIGHT, 'Suppressed')
	
	libtcod.console_set_default_foreground(player_unit_con, libtcod.white)
	libtcod.console_set_default_background(player_unit_con, libtcod.black)


# displays a window with information about a particular PSG
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
		scenario.GetCurrentPhase())
	libtcod.console_set_default_foreground(cmd_con, INFO_TEXT_COL)
	libtcod.console_set_default_background(cmd_con, libtcod.black)
	scenario.cmd_menu.DisplayMe(cmd_con, 0, 2, 24)


# draw scenario info to the scenario info console
def UpdateScenInfoConsole():
	libtcod.console_clear(scen_info_con)
	
	# scenario battlefront, current and time
	libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
	libtcod.console_print_ex(scen_info_con, 28, 0, libtcod.BKGND_NONE, libtcod.CENTER,
		scenario.battlefront)
	text = MONTH_NAMES[scenario.month] + ' ' + str(scenario.year)
	libtcod.console_print_ex(scen_info_con, 28, 1, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	text = str(scenario.hour) + ':' + str(scenario.minute).zfill(2)
	libtcod.console_print_ex(scen_info_con, 28, 2, libtcod.BKGND_NONE, libtcod.CENTER,
		text)
	
	# TODO: pull wind and weather info from scenario object
	text = 'No Wind'
	libtcod.console_print_ex(scen_info_con, 56, 0, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	text = 'Clear'
	libtcod.console_print_ex(scen_info_con, 56, 1, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)
	# FUTURE: pull light and visibility info from scenario object
	text = ''
	libtcod.console_print_ex(scen_info_con, 56, 2, libtcod.BKGND_NONE, libtcod.RIGHT,
		text)


# update the map hex info console
def UpdateHexInfoConsole():
	libtcod.console_clear(hex_info_con)
	libtcod.console_set_default_foreground(hex_info_con, TITLE_COL)
	libtcod.console_set_default_background(hex_info_con, TITLE_BG_COL)
	libtcod.console_rect(hex_info_con, 0, 0, 24, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(hex_info_con, 12, 0, libtcod.BKGND_NONE, libtcod.CENTER,
		'Map Hex & Unit Info')
	libtcod.console_print(hex_info_con, 0, 13, '[M]essage Log')
	libtcod.console_put_char_ex(hex_info_con, 1, 13, 'M', ACTION_KEY_COL, libtcod.black)
	libtcod.console_set_default_foreground(hex_info_con, INFO_TEXT_COL)
	libtcod.console_set_default_background(hex_info_con, libtcod.black)
	
	# see if we can display info about a map hex
	
	# mouse cursor outside of map area
	if mouse.cx < 27: return
	
	x = mouse.cx - 27
	y = mouse.cy - 4

	if (x,y) in scenario.map_index:
		(hx, hy) = scenario.map_index[(x,y)]
		map_hex = GetHexAt(hx, hy)
		
		# coordinates and elevation
		text = str(map_hex.hx) + ',' + str(map_hex.hy) + ':'
		elevation = int(map_hex.terrain_type.los_height + (map_hex.elevation * ELEVATION_M))
		text += str(elevation) + 'm'
		libtcod.console_print(hex_info_con, 0, 2, text)
		
		# objective status
		if map_hex.objective:
			libtcod.console_print_ex(hex_info_con, 23, 2, libtcod.BKGND_NONE,
				libtcod.RIGHT, 'Objective')

		# hex terrain type
		libtcod.console_print(hex_info_con, 0, 3, map_hex.terrain_type.display_name)

		# road status
		if len(map_hex.dirt_road_links) > 0:
			libtcod.console_print_ex(hex_info_con, 23, 3, libtcod.BKGND_NONE,
				libtcod.RIGHT, 'Dirt Road')
		
		return
		
		# TODO: unit(s) present
		for psg in scenario.unit_list:
			if psg.hx == map_hex.hx and psg.hy == map_hex.hy:
				if psg.owning_player == 1:
					libtcod.console_set_default_foreground(hex_info_con, libtcod.red)
				else:
					libtcod.console_set_default_foreground(hex_info_con, HIGHLIGHT_COLOR)
				
				lines = wrap(psg.GetName(), 23)
				n = 0
				for line in lines[:2]:
					libtcod.console_print(hex_info_con, 0, 4+n, line)
					n += 1
				libtcod.console_set_default_foreground(hex_info_con, libtcod.white)
				
				if psg.owning_player == 1 and psg.suspected:
					return

				# name of squads/vehicles and number of steps in PSG
				text = psg.GetStepName() + ' x' + str(psg.num_steps)
				libtcod.console_print(hex_info_con, 0, 5+n, text)
				
				if psg.suppressed:
					libtcod.console_print(hex_info_con, 0, 8, 'Suppressed')
				if psg.suspected:
					libtcod.console_print_ex(hex_info_con, 23, 8,
						libtcod.BKGND_NONE, libtcod.RIGHT,
						'Unknown to Enemy')
				break
		

# layer the display consoles onto the screen
def DrawScreenConsoles():
	
	def DrawHighlights():
		
		# don't highlight unit if enemy and its hex is not visible to player
		if scenario.active_unit.owning_player == 1:
			map_hex = GetHexAt(scenario.active_unit.hx, scenario.active_unit.hy)
			if not map_hex.vis_to_player:
				return
		
		#libtcod.console_set_char_background(con, scenario.active_unit.screen_x,
		#	scenario.active_unit.screen_y, SELECTED_HL_COL, flag=libtcod.BKGND_SET)
		
		# only highlight hex if not in move animation
		if scenario.active_unit.anim_x == 0 and scenario.active_unit.anim_y == 0:
		
			for (xm, ym) in HEX_EDGE_TILES:
				x = scenario.active_unit.screen_x+xm
				y = scenario.active_unit.screen_y+ym
				if libtcod.console_get_char(con, x, y) == 250:
					libtcod.console_set_char_foreground(con, x, y, SELECTED_HL_COL)
	
		# highlight player's targeted unit if any
		psg = scenario.player_target
		if psg:
			libtcod.console_set_char_background(con, psg.screen_x, psg.screen_y,
				TARGET_HL_COL, flag=libtcod.BKGND_SET)
			
			# TEMP - show LoS hexes
			#los_line = GetLoS(scenario.active_unit.hx, scenario.active_unit.hy,
			#	psg.hx, psg.hy)
			
			#for (hx, hy) in los_line:
			#	(x,y) = PlotHex(hx, hy)
			#	x += 26
			#	y += 3
			#	libtcod.console_set_char(con, x, y, 250)
			#	libtcod.console_set_char_foreground(con, x, y, libtcod.red)
			
			# draw LoS line
			line = GetLine(scenario.active_unit.screen_x, scenario.active_unit.screen_y,
				psg.screen_x, psg.screen_y)
			for (x, y) in line[2:-1]:
				libtcod.console_set_char(con, x, y, 250)
				libtcod.console_set_char_foreground(con, x, y, libtcod.red)
	
	
	libtcod.console_clear(con)
	
	# map viewport layers
	libtcod.console_blit(bkg_console, 0, 0, 0, 0, con, 0, 0)		# grey outline
	libtcod.console_blit(map_vp_con, 0, 0, 0, 0, con, 27, 4)		# map terrain
	libtcod.console_blit(unit_con, 0, 0, 0, 0, con, 27, 4, 1.0, 0.0)	# map unit layer
	libtcod.console_blit(map_gui_con, 0, 0, 0, 0, con, 26, 3, 1.0, 0.0)	# map GUI layer

	# left column consoles
	libtcod.console_blit(player_unit_con, 0, 0, 0, 0, con, 1, 1)
	libtcod.console_blit(cmd_con, 0, 0, 0, 0, con, 1, 33)
	libtcod.console_blit(hex_info_con, 0, 0, 0, 0, con, 1, 50)
	
	# scenario info
	libtcod.console_blit(scen_info_con, 0, 0, 0, 0, con, 26, 0)

	# highlight player's targeted unit if any
	if scenario.player_target:
		libtcod.console_set_char_background(con, scenario.player_target.screen_x,
			scenario.player_target.screen_y, TARGET_HL_COL, flag=libtcod.BKGND_SET)
		# draw LoS line
		line = GetLine(scenario.player_unit.screen_x, scenario.player_unit.screen_y,
			scenario.player_target.screen_x, scenario.player_target.screen_y)
		for (x, y) in line[2:-1]:
			libtcod.console_set_char(con, x, y, 250)
			libtcod.console_set_char_foreground(con, x, y, libtcod.red)
	
	#if scenario.active_unit:
	#	DrawHighlights()
		
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
	global scen_menu_con, bkg_console, map_vp_con, map_fov_con, map_gui_con
	global unit_con, player_unit_con, anim_con, cmd_con, attack_con, scen_info_con
	global hex_info_con, fov_hex_con
	global dice
	
	# TODO: change to UpdateConsoles()
	def UpdateScreen():
		UpdateUnitConsole()
		UpdateGUIConsole()
		UpdatePlayerUnitConsole()
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
	map_vp_con = libtcod.console_new(55, 52)
	libtcod.console_set_default_background(map_vp_con, libtcod.black)
	libtcod.console_set_default_foreground(map_vp_con, libtcod.white)
	libtcod.console_clear(map_vp_con)
	
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
	scen_info_con = libtcod.console_new(57, 3)
	libtcod.console_set_default_background(scen_info_con, libtcod.black)
	libtcod.console_set_default_foreground(scen_info_con, libtcod.white)
	libtcod.console_clear(scen_info_con)
	
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
	
	# attack resolution console
	attack_con = libtcod.console_new(26, 60)
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.white)
	libtcod.console_clear(attack_con)

	# load dark tile to indicate tiles that aren't visible to the player
	fov_hex_con = LoadXP('ArmCom2_tile_fov.xp')
	libtcod.console_set_key_color(fov_hex_con, KEY_COLOR)

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
		UpdateVPConsole()
	
	else:
	
		##################################################################################
		#                            Start a new Scenario                                #
		##################################################################################
		
		# create a new campaign day object and hex map
		scenario = Scenario(26, 26)
		
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
		scenario.hour_limit = 9
		scenario.minute_limit = 0
		
		# display scenario info: chance to cancel scenario start
		# TEMP disabled
		#if not ScenarioSummary():
		#	del scenario
		#	return
		
		# spawn the player unit
		new_unit = Unit('Panzer 35t')
		scenario.unit_list.append(new_unit)
		new_unit.owning_player = 0
		new_unit.vehicle_name = 'Gretchen'
		new_unit.facing = 0
		new_unit.turret_facing = 0
		scenario.player_unit = new_unit		# record this as the player unit
		new_unit.PlaceAt(6, 22)
		
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
		for i in range(4):
			new_unit = Unit('Panzer 35t')
			scenario.unit_list.append(new_unit)
			new_unit.owning_player = 0
			new_unit.facing = 0
			new_unit.turret_facing = 0
			new_unit.squadron_leader = scenario.player_unit
			new_unit.PlaceAt(6, 22)
		
		UpdatePlayerUnitConsole()
		
		# set up our objectives
		#scenario.hex_map.AddObjectiveAt(5, 4)
		#scenario.hex_map.AddObjectiveAt(6, -2)
		
		# generate enemy OOB and spawn into map
		#scenario.GenerateEnemyOOB()
		
		# do initial objective capture
		#for map_hex in scenario.objective_hexes:
		#	map_hex.CheckCapture(no_message=True)
		
		# TEMP set up test enemy unit
		new_unit = Unit('7TP')
		scenario.unit_list.append(new_unit)
		new_unit.owning_player = 1
		new_unit.facing = 3
		new_unit.turret_facing = 3
		new_unit.PlaceAt(6, 15)
		
		# set up map viewport
		scenario.SetVPHexes()
		# calculate initial field of view for player
		scenario.hex_map.CalcFoV()
		# draw viewport console for first time
		UpdateVPConsole()
	
		# select first crew position in player unit
		scenario.selected_crew_position = scenario.player_unit.crew_positions[0]
		# build initial command menu
		scenario.active_cmd_menu = 'crew_actions'
		scenario.BuildCmdMenu()
		
		#UpdateScreen()
		
		
	
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
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
			libtcod.console_blit(anim_con, 0, 0, 0, 0, 0, 26, 3, 1.0, 0.0)
		
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
						#elif mouse.rbutton and not (psg.suspected and psg.owning_player == 1):
						#	DisplayPSGInfoWindow(psg)
						#	break
		
		# open scenario menu screen
		if key.vk == libtcod.KEY_ESCAPE:
			if ScenarioMenu():
				exit_scenario = True
			else:
				DrawScreenConsoles()
			continue
		
		# check for scenario end
		#if scenario.winner is not None:
		#	exit_scenario = True
		#	continue
		
		##### AI Actions #####
		if scenario.active_player == 1:
			scenario.DoAIPhase()
			scenario.NextPhase()
			UpdateScreen()
			continue
		
		##### Automatic Phase Actions #####
		if scenario.GetCurrentPhase() == 'Close Combat':
			# TEMP - nothing happens in this phase yet
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
		if option.option_id == 'next_phase':
			scenario.NextPhase()
			UpdatePlayerUnitConsole()
			DrawScreenConsoles()
		
		##################################################################
		# Crew Action Phase Actions
		##################################################################
		elif option.option_id == 'toggle_hatch':
			scenario.selected_crew_position.ToggleHatch()
			UpdatePlayerUnitConsole()
			
			# update FoV if required
			if scenario.selected_crew_position.player_position:
				scenario.hex_map.CalcFoV()
				UpdateVPConsole()
			
			DrawScreenConsoles()
		
		##################################################################
		# Movement Phase Actions
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
				scenario.BuildCmdMenu()
				DrawScreenConsoles()
		
		##################################################################
		# Shooting Phase Actions
		##################################################################
		elif option.option_id == 'next_target':
			scenario.SelectNextPlayerTarget()
			scenario.BuildCmdMenu()
			DrawScreenConsoles()
		elif option.option_id == 'clear_target':
			scenario.player_target = None
			scenario.BuildCmdMenu()
			DrawScreenConsoles()
		elif option.option_id[:5] == 'fire_':
			# get number of weapon from rest of string
			n = int(option.option_id[5])
			weapon = scenario.player_unit.weapon_list[n]
			InitAttack(scenario.player_unit, weapon, scenario.player_target)
			UpdatePlayerUnitConsole()
			scenario.player_target = None
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
cmd_menu.AddOption('toggle_font_size', 'F', 'Font Size',
	desc='Switch between 12px and 16px font size')
cmd_menu.AddOption('select_msg_speed', 'M', 'Message Pause',
	desc='Change how long messages are displayed before being cleared')
cmd_menu.AddOption('select_ani_speed', 'A', 'Animation Speed',
	desc='Change the display speed of in-game animations')
cmd_menu.AddOption('return_to_main', '0', 'Main Menu')
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
	active_menu.DisplayMe(0, WINDOW_XM-12, 38, 24)
	
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
		libtcod.console_print(0, WINDOW_XM-12, 48, text)
		
		text = 'Animation Speed: '
		ani_time = config.getint('ArmCom2', 'animation_speed')
		if ani_time == 16:
			text += 'Fast'
		elif ani_time == 30:
			text += 'Normal'
		else:
			text += 'Slow'
		libtcod.console_print(0, WINDOW_XM-12, 49, text)
		
		libtcod.console_set_default_foreground(0, libtcod.white)
	
UpdateScreen()

# animation timing
time_click = time.time()
gradient_x = WINDOW_WIDTH + 20



# jump right into a new scenario
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
		# check for already-existing saved game
		if os.path.exists('savegame'):
			text = 'Starting a new game will erase the previous one. Proceed?'
			if not GetConfirmation(text):
				UpdateScreen()
				continue
			
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

