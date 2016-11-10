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
#    Copyright (c) 2016 Gregory Adam Scott (sudasana@gmail.com)
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
#        The author does not condone any of the actions or events depicted herein        #
#                                                                                        #
##########################################################################################


##### Libraries #####
import libtcodpy as libtcod				# The Doryen Library
import pygame, pygame.mixer				# for sound effects
from pygame.locals import *
import ConfigParser					# for saving and loading settings
import time						# for animation timing
from random import choice, shuffle, sample
from textwrap import wrap				# for breaking up strings
from operator import attrgetter				# for list sorting
from math import atan, floor				# for heading calculation, math
import shelve						# for saving and loading games
import dbhash, anydbm					# need this for py2exe
import os, sys						# for OS-related stuff
import xp_loader, gzip					# for loading xp image files
import xml.etree.ElementTree as xml			# ElementTree library for xml


##########################################################################################
#                                   Constant Definitions                                 #
##########################################################################################

NAME = 'Armoured Commander II'
VERSION = 'Proof of Concept'				# determines saved game compatability
SUBVERSION = ''						# descriptive, no effect on compatability
DATAPATH = 'data/'.replace('/', os.sep)			# path to data files
LIMIT_FPS = 50						# maximum screen refreshes per second
WINDOW_WIDTH = 88					# width of game window in characters
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

SUPPRESSED_PENALTY = -3					# penalty to morale level for being suppressed

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
TARGET_HL_COL = libtcod.Color(255, 0, 0)		# target highlight background color 
SELECTED_HL_COL = libtcod.Color(50, 150, 255)		# selected PSG highlight colour
INACTIVE_COL = libtcod.Color(100, 100, 100)		# inactive option color
KEY_COLOR = libtcod.Color(255, 0, 255)			# key color for transparency

KEY_HIGHLIGHT_COLOR = libtcod.Color(70, 170, 255)	# highlight for key commands
HIGHLIGHT = (libtcod.COLCTRL_1, libtcod.COLCTRL_STOP)	# constant for highlight pair

SOUNDS = {}						# sound effects

# terrain type codes
OPEN_GROUND = 0
FOREST = 1
FIELDS = 2
POND = 3

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

DESTHEX = [(0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0)]	# change in hx, hy values for hexes in each direction
PLOT_DIR = [(0,-1), (1,-1), (1,1), (0,1), (-1,1), (-1,-1)]	# position of direction indicator
TURRET_CHAR = [254, 47, 92, 254, 47, 92]			# characters to use for turret display

# hexes covered by a weapon arc, with attacker in 0,0 and firing toward direction 0
# later to be rotated and shifted and modified by maximum range, hex visibility, etc.
ARC_HEXES = [
	(-3, -3), (-3, -2),
	(-2, -2), (-2, -3), (-2, -1),
	(-1, -1), (-1, -2), (-1, -3), (-1, -4), (-1, -5),
	(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6),
	(1, -2), (1, -3), (1, -4), (1, -5), (1, -6),
	(2, -4), (2, -5), (2, -6),
	(3, -5), (3, -4)
]

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


# AI class, assigned to all PSGs including player PSG

class AI:
	def __init__(self, owner):
		self.owner = owner		# pointer to owning PSG object
		
		self.mode = 'Defense'		# AI mode - determines change conditions
						#   for AI states
		self.state = 'Hold'		# temp - current AI state
		
		self.attack_target = None	# currently attacking this target
		
		self.guard_target = None	# target friendly unit to protect
						#   used by 'Guard' AI mode
		self.guard_hx = 0		# hex x offset position to keep relative to guard target
		self.guard_hy = 0		# "
		
		self.hunt_target = None		# target enemy unit
		
		self.move_target = None		# target hx, hy into which PSG is trying to move

	# print an AI report to the console
	def Report(self, text):
		print text

	# return a list of hexes between h1 and h2 so that the distance between each
	# location and h1 and h2 is not higher than the distance between h1 and h2
	# if needs_los, there must be a LoS to h2
	def GetListofInterveningHexes(self, hx1, hy1, hx2, hy2, needs_los=False):
		hex_list = []
		max_distance = GetHexDistance(hx1, hy1, hx2, hy2)
		radius_list = GetHexesWithin(hx2, hy2, max_distance)
		for (hx, hy) in radius_list:
			if GetHexDistance(hx, hy, hx2, hy2) >= max_distance:
				continue
			if GetHexDistance(hx, hy, hx1, hy1) >= max_distance:
				continue
			
			if needs_los:
				if not GetLoS(hx, hy, hx2, hy2): continue

			# special: can include h1 in list of locations
			if (hx, hy) == (hx1, hy1):
				hex_list.append((hx, hy))
				continue
			
			# make sure location is not occupied by an enemy PSG
			if not GetHexAt(hx, hy).IsOccupiedByEnemy(self.owner.owning_player):
				hex_list.append((hx, hy))
			
		return hex_list
		

	# TODO
	# calcuate the score for moving into a target location
	# higher scores for: better potential attacks from this position, less TU
	#  expended to reach it
	def ScoreMove(psg, target_hx, target_hy):
		pass
	
	# set guard offset position based on current location
	def SetGuardPosition(self):
		if self.guard_target is None:
			return
		self.guard_hx = self.owner.hx - self.guard_target.hx
		self.guard_hy = self.owner.hy - self.guard_target.hy

	# do AI action for this PSG
	def ResolveMode(self):
		
		# check for state change conditions
		text = 'Resolving AI Mode for ' + self.owner.GetName(true_name=True) + ': '
		text += self.mode + ':\n  '
		
		if self.mode == 'Guard':
			
			if self.guard_target is None:
				self.mode = 'Defense'
				self.state = 'Hold'
				text += 'No PSG to guard, switching to Defense mode'
			
			if self.guard_target not in scenario.psg_list:
				self.guard_target = None
				self.mode = 'Defense'
				self.state = 'Hold'
				text += 'Guard target destroyed, switching to Defense mode'
			
			# check that we are in the right position to guard
			hx_offset = self.owner.hx - self.guard_target.hx
			hy_offset = self.owner.hy - self.guard_target.hy
			
			if hx_offset != self.guard_hx or hy_offset != self.guard_hy:
				text += 'Moving to correct guard position, '
				hx = self.guard_target.hx + self.guard_hx
				hy = self.guard_target.hy + self.guard_hy
				map_hex = GetHexAt(hx, hy)
				
				if map_hex is None:
					text += 'ideal position off map, holding here'
					self.state = 'Hold'
				elif map_hex.IsOccupiedByEnemy(self.owner.owning_player):
					text += 'ideal position occupied by enemy, holding here'
					self.state = 'Hold'
				else:
					text += 'move possible'
					self.move_target = (map_hex.hx, map_hex.hy)
					self.state = 'Move'
				
			# in correct guard position, hold here
			else:
				text += 'In correct guard position, '
				if self.state == 'Hold':
					text += 'holding here.'
				else:
					self.state = 'Hold'
					text += 'switching state to Hold.'

		elif self.mode == 'Hunt':
			
			# need to find a new target
			if self.hunt_target is None:
				target_list = []
				for psg in scenario.psg_list:
					if psg.owning_player == self.owner.owning_player:
						continue
					distance = GetHexDistance(self.owner.hx, self.owner.hy, psg.hx, psg.hy)
					target_list.append((distance, psg))
				
				# enemy has no active PSGs
				if len(target_list) == None:
					text += 'no possible targets to hunt!'
					if self.state != 'Hold':
						self.state = 'Hold'
					self.Report(text)
					self.ResolveState()
					return
				else:
					# pick closest target
					target_list = sorted(target_list, key=lambda x: x[0])
					(distance, psg) = target_list[0]
					self.hunt_target = psg
					text += 'selected new target: ' + psg.GetName(true_name=True)
			
			# if we have a good attack on the target, stop and fire
			score = ScoreAttack(self.owner, self.owner.weapon_list[0],
				self.hunt_target)
			# account for possibly stopping and firing in later action
			if self.owner.moved[0]:
				score += 2
			if score >= 4:
				self.state = 'Hold'
				text += ' in LoS of target, good attack possible, holding here'
				
			# not in LoS or doesn't have a good attack
			else:
			
				# we need to move, pick a good location for an attack
				#   and which is also close
				self.state = 'Move'
				
				target_hex_list = self.GetListofInterveningHexes(self.owner.hx,
					self.owner.hy, self.hunt_target.hx,
					self.hunt_target.hy, needs_los=True)
				
				# score list based on proximity to current location and
				# proximity to target
				score_list = []
				for (hx, hy) in target_hex_list:
					score = GetHexDistance(self.owner.hx,
						self.owner.hy, hx, hy)
					score += GetHexDistance(self.hunt_target.hx,
						self.hunt_target.hy, hx, hy)
					score_list.append((score, (hx, hy)))
				score_list = sorted(score_list, key=lambda x: x[0])
				(score, (hx, hy)) = score_list[0]
				
				# set target as next step in path toward destination
				hex_path = GetHexPath(self.owner.hx, self.owner.hy,
					hx, hy)
				if len(hex_path) < 2:
					text += ' no path possible, switching to Hold'
					self.state = 'Hold'
				else:
					(hx, hy) = hex_path[1]
					self.move_target = (hx, hy)
					text += (' attack score was ' + str(score) +
						', moving to get a better attack on target')
			
		# defense state has no change conditions
		else:
			text += 'No change.'
		
		# print initial AI report to console
		self.Report(text)
		
		# do AI action according to current state
		self.ResolveState()
	
	# resolve the current AI state
	def ResolveState(self):
		
		text = ('Resolving AI State: for ' + self.owner.GetName(true_name=True) +
			': ' + self.state + ':\n  ')
		
		# pinned
		if self.owner.pinned:
			text += 'Pinned, cannot act.'
			self.Report(text)
			self.owner.SpendTU(8)
			return
		
		if self.state == 'Move':
			
			if self.move_target is None:
				text += 'ERROR: no move target set!'
				self.Report(text)
				self.owner.SpendTU(8)
				return
			
			(hx, hy) = self.move_target
			
			# not yet at target
			if self.owner.hx != hx or self.owner.hy != hy:
				
				# try to move closer to target hex
				hex_path = GetHexPath(self.owner.hx, self.owner.hy, hx, hy)
				
				# TODO: handle no path possible
				if len(hex_path) < 2:
					text += 'ERROR: no path possible to target'
					self.Report(text)
					self.owner.SpendTU(8)
					return
				
				# pick the next hex in the path
				(target_hx, target_hy) = hex_path[1]
				
				# see if a pivot is required
				if self.owner.gun or self.owner.vehicle:
					direction = GetDirectionToAdjacent(self.owner.hx,
						self.owner.hy, target_hx, target_hy)
					if direction != self.owner.facing:
						# TEMP - need a ChangeFacing function for PSGs
						self.owner.facing = direction
						if self.owner.turret_facing is not None:
							self.owner.turret_facing = direction
						self.changed_facing = True
						text += 'pivoted to face direction ' + str(self.owner.facing) + ','
						UpdateUnitConsole()
						DrawScreenConsoles()
				
				# try to do the move
				text += ' moving forward'
				self.Report(text)
				Message(self.owner.screen_x, self.owner.screen_y,
					self.owner.GetName() + ' moves forward')
				result = self.owner.MoveForward()
				
				# move was successful
				if result:
					return
				
				# move was not possible
				self.Report('Move not possible, switching to Hold.')
				self.state = 'Hold'
			
			# already at target
			else:
				text += 'Already arrived at destination, switching to Hold.\n  '
				self.move_target = None
				self.state = 'Hold'
		
		if self.state == 'Hold':
			
			# still reloading
			weapon = self.owner.weapon_list[0]
			if weapon.ord_weapon:
				if weapon.reloading_tu > 0:
					text += 'Still reloading gun - doing nothing'
					self.Report(text)
					self.owner.SpendTU(8)
					return
			
			# already have a hunt target
			if self.hunt_target is not None:
				psg = self.hunt_target
				score = ScoreAttack(self.owner, weapon, psg)
				text += 'Hunt Target is: ' + psg.GetName()
			
			else:
			
				# check all possible targets, scoring an attack against them
				# build a target list
				target_list = []
				
				for psg in scenario.psg_list:
					# same side
					if psg.owning_player == self.owner.owning_player:
						continue
					# beyond maximum range (for now)
					if GetHexDistance(self.owner.hx, self.owner.hy, psg.hx, psg.hy) > 6:
						continue
					# not in LoS
					if not GetLoS(self.owner.hx, self.owner.hy, psg.hx, psg.hy):
						continue
					
					score = ScoreAttack(self.owner, weapon, psg)
					
					# add the roll required to hit and the PSG as a tuple
					target_list.append((score, psg))
				
				if len(target_list) == 0:
					text += 'No valid targets found, waiting.'
					self.Report(text)
					self.owner.SpendTU(8)
					return
				
				text += str(len(target_list)) + ' possible target(s) found,'
				
				# sort the list, putting lowest score at front
				target_list = sorted(target_list, key=lambda x: x[0])
				# pick the last tuple
				(score, psg) = target_list[-1]
			
			if score <= 3:
				text += ' best attack is ' + str(score) + ' pts, not firing'
				self.Report(text)
				self.owner.SpendTU(8)
				return
			
			# pivot to face target if needed
			if GetFacing(psg, self.owner, False) != 'Front':
				hex_line = GetHexLine(self.owner.hx, self.owner.hy,
					psg.hx, psg.hy)
				(hx, hy) = hex_line[1]
				direction = GetDirectionToward(self.owner.hx, self.owner.hy,
					hx, hy)
				self.owner.facing = direction
				self.changed_facing = True
				text += ' pivoted to face direction ' + str(self.owner.facing) + ', '
				UpdateUnitConsole()
				DrawScreenConsoles()
			
			# init attack on chosen target
			text += ' starting attack on ' + psg.GetName(true_name=True)
			self.Report(text)
			
			InitAttack(self.owner, psg)


# a single option in a CommandMenu list
class MenuOption:
	def __init__(self, option_id, key_code, option_text, desc, tu_cost, exit_option, inactive):
		self.option_id = option_id	# unique id of this option
		self.key_code = key_code	# the key used to activate this option
		self.option_text = option_text	# text displayed for this option
		self.desc = desc		# description of this option
		self.tu_cost = tu_cost		# TU cost for this action
		self.exit_option = exit_option	# this option exits the menu (mapped to #0)
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
	def AddOption(self, option_id, key_code, option_text, desc=None, tu_cost=None, exit_option=False, inactive=False):
		new_option = MenuOption(option_id, key_code, option_text, desc, tu_cost, exit_option, inactive)
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
		PlaySound('menu_selection')
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
		n = 0
		original_fg = libtcod.console_get_default_foreground(console)
		original_bg = libtcod.console_get_default_background(console)
		
		# menu is empty
		if len(self.cmd_list) == 0:
			libtcod.console_set_default_foreground(console, libtcod.dark_grey)
			libtcod.console_print(console, x, y, 'None')
			libtcod.console_set_default_foreground(console, original_fg)
			return
		
		max_w = 0
		for menu_option in self.cmd_list:
			
			w = 0
			
			# if this is the exit command, and it's not the only option,
			# leave a space before it
			if menu_option.exit_option and len(self.cmd_list) > 1:
				n += 1
			
			# display command key
			if menu_option.inactive:
				libtcod.console_set_default_foreground(console, INACTIVE_COL)
			else:
				libtcod.console_set_default_foreground(console, KEY_HIGHLIGHT_COLOR)
			libtcod.console_print(console, x, y+n, menu_option.key_code)
			
			# determine how far to shift command text over
			xn = len(menu_option.key_code) + 1
			
			if not menu_option.inactive:
				libtcod.console_set_default_foreground(console, libtcod.white)
			
			# display command text lines
			for line in menu_option.option_text_lines:
				libtcod.console_print(console, x+xn, y+n, line)
				n+=1
			# bit of a kludge, but this makes sure that the y position is only
			#   incremented if there's still another line to display
			n-=1
			
			w = xn + len(menu_option.option_text)
			
			# TU cost
			if menu_option.tu_cost is not None:
				if menu_option.tu_cost > 0:
					libtcod.console_print_ex(console, x+25, y+n, libtcod.BKGND_NONE,
						libtcod.RIGHT, str(menu_option.tu_cost))
					w = 26
			
			# set if widest option
			if w > max_w:
				max_w = w
			
			n += 1
			# reset display colour
			libtcod.console_set_default_foreground(console, original_fg)
			
		# highlight any selected option and display description if any
		max_n = n
		n = 0
		for menu_option in self.cmd_list:
			if menu_option.exit_option and len(self.cmd_list) > 1:
				n += 1
			if self.selected_option == menu_option:
				libtcod.console_set_default_background(console, HIGHLIGHT_BG_COLOR)
				libtcod.console_rect(console, x, y+n, max_w, menu_option.h, False, libtcod.BKGND_SET)
				libtcod.console_set_default_background(console, original_bg)
				
				if menu_option.desc is not None:
					if menu_option.inactive:
						libtcod.console_set_default_foreground(console, libtcod.dark_grey)
					else:
						libtcod.console_set_default_foreground(console, libtcod.white)
					lines = wrap(menu_option.desc, 24)
					# we re-use n here since we don't need it anymore
					n = 0
					for line in lines:
						libtcod.console_print(console,
							x, y+max_n+2+n,	line)
						n += 1
				
				break
						
			n += menu_option.h
		libtcod.console_set_default_foreground(console, original_fg)
		


# platoon-sized group class
# represents a platoon, squadron, battery, etc.
class PSG:
	def __init__(self, name, unit_id, num_steps, facing, turret_facing, owning_player, skill_lvl, morale_lvl, player_psg=False):
		self.unit_id = unit_id			# unique ID for unit type of this PSG
		self.name = name			# name, eg. 'Tank Squadron'
		self.step_name = ''			# name of individual teams / vehicles w/in this PSG
		self.num_steps = num_steps		# number of unit steps in this PSG
		self.portrait = None			# portrait filename if any
		self.ai = AI(self)			# AI object
		
		self.hx = 0				# hex location of this PSG, will be set
		self.hy = 0				#   by SpawnAt()
		self.draw_x = 0				# draw location offset from center of hex
		self.draw_y = 0				#   set by DrawMe()
		self.screen_x = 0			# draw location on the screen
		self.screen_y = 0			#   set by DrawMe() based on draw_x and draw_y
		
		self.facing = facing			# facing direction, for vehicles this
							#   is their hull facing
		self.turret_facing = turret_facing	# turret facing if any
		
		self.movement_class = ''		# movement class
		self.armour = None			# armour ratings if any
		
		self.weapon_list = []			# list of weapons
		self.active_weapon = None		# used for player PSG TODO: remove?
		
		self.infantry = False			# PSG type flags
		self.gun = False
		self.vehicle = False
		
		self.recce = False			# unit has recce abilities
		
		self.owning_player = owning_player	# player that controls this PSG
		self.display_char = ''			# character to display on map, set below
		
		self.skill_lvl = skill_lvl		# skill and morale levels
		self.morale_lvl = morale_lvl
		
		# action flags (current status, newly applied for this turn)
		self.fired = [False, False]
		self.moved = [False, False]
		self.changed_facing = False
		self.changed_turret_facing = False
		
		# status flags
		self.dug_in = False			# only infantry units and guns can dig in
		self.hull_down = -1			# only vehicles can be hull down, number
							#   is direction
		
		self.hidden = True			# PSG identity is not yet known
		self.pinned = False			# move N/A, attacks less effective
		self.bogged = False			# move N/A
		self.suppressed = False			# move/fire N/A, penalty to morale
		self.melee = False			# held in melee
		
		self.max_tu = 36			# TU allowance per turn
		self.tu = 36				# remaining TU - can be negative, deficit
							#   is removed at start of next turn
		
		# load stats from data file
		self.LoadStats()
		
		# set initial display character
		self.display_char = self.GetDisplayChar()

	# return description of PSG
	# if using real name, transcode it to handle any special characters in it
	# if true_name, return the real identity of this PSG no matter what
	def GetName(self, true_name=False):
		if not true_name:
			if self.owning_player == 1 and self.hidden:
				return 'Possible Enemy PSG'
		return self.name.decode('utf8').encode('IBM850')

	# try to place this PSG into the target hex, if not possible, place in random adjacent hex
	#   also calls SetDrawLocation to determine location of glyph within hex
	def SpawnAt(self, hx, hy):
		hex_list = [(hx, hy)]
		adjacent_list = GetAdjacentHexesOnMap(hx, hy)
		shuffle(adjacent_list)
		hex_list.extend(adjacent_list)
		for (hx1, hy1) in hex_list:
			map_hex = GetHexAt(hx1, hy1)
			if not map_hex.water:
				# TODO: make sure we are within stacking limits
				self.hx = hx1
				self.hy = hy1
				map_hex.contained_psgs.append(self)
				self.SetDrawLocation()
				
				return
		print 'ERROR: unable to spawn PSG into or near ' + str(hx) + ',' + str(hy)

	# remove this PSG from the game
	def DestroyMe(self):
		scenario.psg_list.remove(self)
		map_hex = GetHexAt(self.hx, self.hy)
		# should not have to check, but was crashing
		if self in map_hex.contained_psgs:
			map_hex.contained_psgs.remove(self)
		if self in scenario.oob_list:
			scenario.oob_list.remove(self)
			UpdateOOBConsole()
		# remove from psg info map
		for key, psg in scenario.psg_info_map.iteritems():
			if psg == self:
				del scenario.psg_info_map[key]
				return

	# do any actions that automatically occur when PSG is activated
	def DoActivationActions(self):
		
		# test to recover from pinned/suppressed/etc.
		self.DoRecoveryTests()
	
		# do a spot check from this PSG to all enemy PSGs
		self.DoSpotCheck()
		
		# do a check to see if this PSG regains Hidden status
		if self.hidden: return
		
		# TODO: if an enemy PSG has aquired target on this PSG, cannot
		# regain hidden
		for psg in scenario.psg_list:
			if psg.owning_player == self.owning_player: continue
			distance = GetHexDistance(psg.hx, psg.hy, self.hx, self.hy)
			spotting_distance = GetSpottingDistance(psg, self)
			if distance <= spotting_distance:
				return
		self.HideMe()

	# do any actions that automatically occur after PSG has been activated
	def DoPostActivationActions(self):
		
		# check for objective hex capture
		map_hex = GetHexAt(self.hx, self.hy)
		if map_hex.CaptureMe():
			if self.owning_player == 0:
				text = 'You have'
			else:
				text = 'The enemy has'
			text += ' captured an objective!'
			Message(self.screen_x, self.screen_y, text)
		
		# apply any action flags from this turn, reset flags for next turn
		self.fired[0] = self.fired[1]
		self.fired[1] = False
		self.moved[0] = self.moved[1]
		self.moved[1] = False
		
		# facing flags only apply for own activation
		self.changed_facing = False
		self.changed_turret_facing = False

	# roll for recovery from negative statuses
	def DoRecoveryTests(self):
		if self.pinned or self.suppressed:
			morale_lvl = self.morale_lvl
			
			if self.suppressed:
				morale_lvl += SUPPRESSED_PENALTY
			terrain_mod = GetHexAt(self.hx, self.hy).GetTerrainMod(self)
			if terrain_mod > 0:
				morale_lvl += terrain_mod
			
			if morale_lvl < 2:
				morale_lvl = 2
			elif morale_lvl > 11:
				morale_lvl = 11
			
			# do the roll
			d1, d2, roll = Roll2D6()
			if roll <= morale_score:
				if self.pinned:
					text = self.GetName() + ' recovers from being Pinned.'
					Message(self.screen_x, self.screen_y, text)
					self.pinned = False
				else:
					text = self.GetName() + ' recovers from being Suppressed.'
					Message(self.screen_x, self.screen_y, text)
					self.suppressed = False
		
	# reset PSG for a new turn
	def ResetNewTurn(self):
		# replenish TU
		self.tu += self.max_tu

	# load the baseline stats for this PSG from XML data file
	def LoadStats(self):
		# find the unit type entry in the data file
		root = xml.parse(DATAPATH + 'armcom2_unit_defs.xml')
		item_list = root.findall('unit_def')
		for item in item_list:
			# this is the one we need
			if item.find('id').text == self.unit_id:
				if item.find('portrait') is not None:
					self.portrait = item.find('portrait').text
				self.step_name = item.find('name').text
				
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

	# spend TU, also update any TU countdown timers that are running (reloading, etc.)
	def SpendTU(self, tu):
		
		self.tu -= tu
		
		# check for reloading ordinance weapons
		for weapon in self.weapon_list:
			if weapon.ord_weapon:
				if weapon.reloading_tu > 0:
					weapon.reloading_tu -= tu
					if weapon.reloading_tu < 0: weapon.reloading_tu = 0
	
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
			
			# final step in PSG
			# TEMP - last step from player PSG cannot be removed
			if scenario.player_psg == self:
				print 'DEBUG: player PSG spared death'
				return
			
			self.num_steps = 0
			text = self.GetName() + ' has been destroyed!'
			Message(self.screen_x, self.screen_y, text)
			self.DestroyMe()
			UpdateUnitConsole()
			return
		
		text = self.GetName() + ' is Pinned.'
		Message(self.screen_x, self.screen_y, text)
		self.pinned = True
	
	# perform a check to see if this PSG can reveal any hidden enemy PSGs
	def DoSpotCheck(self):
		for psg in scenario.psg_list:
			if psg.owning_player == self.owning_player: continue
			# no need to check, already revealed
			if not psg.hidden: continue
			if GetHexDistance(self.hx, self.hy, psg.hx, psg.hy) > 6: continue
			if not GetLoS(self.hx, self.hy, psg.hx, psg.hy): continue
			
			distance = GetHexDistance(self.hx, self.hy, psg.hx, psg.hy)
			spotting_distance = GetSpottingDistance(self, psg)
			if distance <= spotting_distance:
				psg.RevealMe()
		
	# this PSG has been revealed by enemy forces
	def RevealMe(self):
		self.hidden = False

		# draw on map
		self.DrawMe(self.hx, self.hy)
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
		UpdateOOBConsole()
	
	# regain Hidden status for this PSG
	def HideMe(self):
		if self.owning_player == 0:
			text = self.GetName() + ' is now Hidden'
		else:
			text = 'Lost contact with ' + self.GetName()
		Message(self.screen_x, self.screen_y, text)
		self.hidden = True
	
	# get display character to be used on hex map
	def GetDisplayChar(self):
		# enemy Hidden PSG
		if self.owning_player == 1 and self.hidden:
			return '?'
		
		# gun, set according to deployed status / hull facing
		if self.gun:
			direction = CombineDirs(self.facing, scenario.player_psg.facing)
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

	# determine a draw location for the glyph representing this PSG on the screen
	#   based on current hex location, and avoiding other PSGs already in the hex
	def SetDrawLocation(self):
		
		map_hex = GetHexAt(self.hx, self.hy)
		
		# we are the only PSG in the hex
		if len(map_hex.contained_psgs) == 1:
			self.draw_x = 0
			self.draw_y = 0
			return
		
		LOCATIONS = [(0,0), (-1,-1), (1,-1), (-1,1), (1,1)]
	
		# try each possible location in turn
		for (x, y) in sample(LOCATIONS, len(LOCATIONS)):
			matched = False
			for psg in map_hex.contained_psgs:
				if psg.draw_x == x and psg.draw_y == y:
					matched = True
					break
			if not matched:
				self.draw_x = x
				self.draw_y = y
				return
		
		print 'ERROR: could not set a draw location within the hex for ' + self.GetName()
		


	# draw this PSG in given hex location in the map viewport
	def DrawMe(self, hx, hy):

		(x,y) = PlotHex(hx, hy)
		# modify for draw position within hex
		x += self.draw_x
		y += self.draw_y
		
		# record location that this PSG appears on the screen
		self.screen_x = x + 30
		self.screen_y = y + 1
		
		# de-register any old PSG draw location and register new one
		for key, psg in scenario.psg_info_map.iteritems():
			if psg == self:
				del scenario.psg_info_map[key]
				break
		scenario.psg_info_map[(self.screen_x, self.screen_y)] = self
		
		self.display_char = self.GetDisplayChar()
		
		# determine foreground color to use
		if self.hidden:
			col = libtcod.light_grey
		else:
			col = libtcod.white
		libtcod.console_put_char_ex(unit_con, x, y, self.display_char, col,
			libtcod.black)
		
		# if current target, record screen coords
		if scenario.target_psg == self:
			scenario.target_coords = (x,y)
		# if selected PSG, same
		elif scenario.selected_psg == self:
			scenario.selected_coords = (x,y)
		
		return
		
		# TODO: keep using following somehow?
		
		# draw turret if applicable
		if not self.vehicle and not self.gun: return
		if self.owning_player == 1 and self.hidden: return
		
		# guns use their hull facing
		if self.gun:
			facing = self.facing
		else:
			if self.turret_facing is None: return
			facing = self.turret_facing
		
		# determine relative turret facing given current viewport facing
		direction = CombineDirs(facing, scenario.player_psg.facing)
		
		# determine location to draw turret character
		x_mod, y_mod = PLOT_DIR[direction]
		char = TURRET_CHAR[direction]
		libtcod.console_put_char_ex(unit_con, x+x_mod, y+y_mod, char,
			col, libtcod.black)
	
	# determine if this PSG is able to move into the target hex
	# if hex is not on the map, occupied by known enemy units, or impassible terrain
	# then no
	def CheckMoveInto(self, hx, hy):
		if self.movement_class == 'Gun': return False
		if (hx, hy) not in scenario.hex_map.hexes: return False
		map_hex = GetHexAt(hx, hy)
		if map_hex.IsOccupiedByEnemy(self.owning_player): return False
		if map_hex.water: return False
		# TODO: check stacking limits
		return True
	
	# try to move this PSG forward into the adjacent hex
	# only works for units with a facing (guns and vehicles)
	# returns True if the move was successful
	def MoveForward(self, reverse=False):

		if self.facing is None:
			print 'ERROR: unit has no facing but is trying to move forward'
			return False
		
		# get the target hex
		if reverse:
			facing = ConstrainDir(self.facing + 3)
		else:
			facing = self.facing
		
		(new_hx, new_hy) = GetAdjacentHex(self.hx, self.hy, facing)
		
		# make sure move is allowed
		if not self.CheckMoveInto(new_hx, new_hy):
			return False
		
		# calculate cost of movement and spend required TU
		map_hex1 = GetHexAt(self.hx, self.hy)
		map_hex2 = GetHexAt(new_hx, new_hy)
		tu_cost = GetTUCostToMove(self, map_hex1, map_hex2)
		if reverse: tu_cost = tu_cost * 4
		self.SpendTU(tu_cost)
		
		# remove us from the list of PSGs in the old hex
		map_hex1.contained_psgs.remove(self)
		
		self.hx = new_hx
		self.hy = new_hy
		
		# add to list of new hex and set draw location
		map_hex2.contained_psgs.append(self)
		self.SetDrawLocation()
		
		# set action flag for next activation
		self.moved[1] = True
		
		return True
		
	# try to pivot the hull facing of this PSG
	def PivotHull(self, cw):
		if self.facing is None:
			return False
			
		if cw:
			facing_change = 1
		else:
			facing_change = -1
		
		self.facing = ConstrainDir(self.facing + facing_change)
		if self.turret_facing is not None:
			self.turret_facing = ConstrainDir(self.turret_facing + facing_change)
		self.changed_facing = True
		return True
		

	# resolve an IFT attack against this PSG
	def ResolveIFTAttack(self, attack_obj):
		
		# roll on the table
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
		
		# all steps must morale test or be destroyed
		elif result[0] == 'M':
			self.MoraleTest(int(result[1]))
		
		# suppression test
		elif result[0] == 'S':
			self.SupressionTest(int(result[1]))
	
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
class MapHex:
	def __init__(self, hx, hy, terrain_type, height):
		self.hx = hx
		self.hy = hy
		self.objective = None			# type of objective if any
		self.held_by = None			# if objective, currently held by this player
		self.spawn_point = False		# location is a spawn point for enemy units
		self.terrain_type = terrain_type
		
		self.height = height			# TODO: elevation, not used yet
		self.blocks_los = False			# hex blocks line of sight beyond it
		
		
		self.los_hinderance = 0			# effect on los into or though
		self.difficult = False			# counts as difficult terrain
		self.water = False			# water terrain, only boats or amphibious
							#   units may enter
		
		self.river_edges = []			# list of adjacent hexes with
							#   which this hex shares a river edge
		self.dirt_road_links = []		# list of directions in which
							#   this hex is connected by
							#   a dirt road
		
		self.vis_to_player = False		# hex is currently visible to player 0, 1
		
		self.contained_psgs = []		# list of active PSGs currently in this hex
		
		
		# Pathfinding stuff
		self.parent = None
		self.g = 0
		self.h = 0
		self.f = 0
	
	# returns true if there is at least one enemy PSG in this hex
	def IsOccupiedByEnemy(self, player):
		if len(self.contained_psgs) == 0:
			return False
		for psg in self.contained_psgs:
			if psg.owning_player != player:
				return True
		return False
	
	# return the terrain modifier to use for given PSG in this hex
	def GetTerrainMod(self, psg):
		
		if self.terrain_type == OPEN_GROUND:
			if psg.infantry:
				if psg.moved[0]:
					return -1
				elif psg.dug_in:
					return 1
				return 0
			elif psg.gun:
				if psg.moved[0]:
					return -2
				elif psg.dug_in:
					return 2
				return -1
			elif psg.vehicle:
				if psg.moved[0]:
					if psg.recce:
						return 2
					return 1
				return 0
		
		elif self.terrain_type == FOREST:
			if psg.infantry:
				if psg.moved[0]:
					return 1
				elif psg.dug_in:
					return 3
				return 2
			elif psg.gun:
				if psg.moved[0]:
					return 0
				elif psg.dug_in:
					return 3
				return 3
			elif psg.vehicle:
				if psg.moved[0]:
					if psg.recce:
						return 2
					return 1
				return 2
			
		elif self.terrain_type == FIELDS:
			if psg.infantry:
				if psg.moved[0]:
					return 1
				elif psg.dug_in:
					return 2
				return 1
			elif psg.gun:
				if psg.moved[0]:
					return 0
				elif psg.dug_in:
					return 2
				return 2
			elif psg.vehicle:
				if psg.recce:
					return 2
				return 1
		
		print 'ERROR: terrain type not found: ' + str(self.terrain_type)
		return 0

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
		# generate map hexes
		self.hexes = {}
		for hx in range(w):
			hy_start = 0 - hx//2
			hy_end = hy_start + h
			for hy in range(hy_start, hy_end):
				self.hexes[(hx,hy)] = MapHex(hx, hy, OPEN_GROUND, 0)
		self.vp_matrix = {}			# map viewport matrix
	
	# calculate field of view for human player
	def CalcFoV(self):
		
		# set all map hexes in range to not visible
		for key, map_hex in self.vp_matrix.items():
			map_hex.vis_to_player = False
		
		# raycast from player position to all hexes on edge of possible view
		hex_list = GetHexRing(scenario.player_psg.hx, scenario.player_psg.hy, 6)
		for (hx2, hy2) in hex_list:
			line = GetHexLine(scenario.player_psg.hx, scenario.player_psg.hy, hx2, hy2)
			for (hx, hy) in line:
				# if this hex is not on map, break the ray
				if (hx, hy) not in self.hexes: break
				
				map_hex = self.hexes[(hx, hy)]
				map_hex.vis_to_player = True
				
				# break ray if this hex blocks line of sight and is not
				#   the player's location
				if map_hex.blocks_los:
					if not (map_hex.hx == scenario.player_psg.hx and
						map_hex.hy == scenario.player_psg.hy):
						break
	
	# set a given hex on the campaign day map to a terrain type
	def SetHexTerrainType(self, hx, hy, terrain_type):
		self.hexes[(hx,hy)].terrain_type = terrain_type
	
	# calculates which hex to display for each hex in map viewport given player
	#   location and directional facing
	def UpdateMapVPMatrix(self):
		
		self.vp_matrix = {}
		
		# run through hexes in map viewport
		for (hx, hy) in VP_HEXES:
				
			# modify for player position
			map_hx = hx + scenario.player_psg.hx
			map_hy = hy + scenario.player_psg.hy
			
			# if player is not facing direction 0, rotate around player position
			if scenario.player_psg.facing != 0:
				map_hx -= scenario.player_psg.hx
				map_hy -= scenario.player_psg.hy
				(map_hx, map_hy) = RotateHex(map_hx, map_hy, scenario.player_psg.facing)
				map_hx += scenario.player_psg.hx
				map_hy += scenario.player_psg.hy
			
			# add the entry if it exists on map: pointer to the hex object
			if (map_hx, map_hy) in self.hexes:
				self.vp_matrix[(hx,hy)] = self.hexes[(map_hx, map_hy)]
		
		# trigger a field of view update as well
		self.CalcFoV()


# holds information about a scenario in progress
# on creation, also set the map size
class Scenario:
	def __init__(self, map_w, map_h):
		
		self.winner = None			# number of player that has won the scenario,
							#   None if no winner yet
		self.end_text = ''			# description of how scenario ended
		
		self.psg_list = []			# list of all platoon-sized groups in play
		self.oob_list = []			# ordered list of PSG still to act this turn
		self.active_psg = None			# currently active PSG
		self.player_psg = None			# pointer to player-controlled PSG
		self.player_active_weapon = None	# " pointer to currently active weapon
		self.selected_psg = None		# pointer to currently selected PSG
		self.active_los = None			# currently displaying a LoS btw a pair of PSGs
		
		self.cmd_menu = CommandMenu('scenario_menu')		# current command menu for player
		self.active_cmd_menu = None		# currently active command menu
		
		self.psg_under_orders = None		# PSG currently being given orders
		
		# hex location selection
		self.selected_vp_hex = None		# currently selected viewport hex
		self.allowed_vp_hexes = []		# list of selectable viewport hexes
		
		self.messages = []			# list of game messages
		
		self.psg_info_map = {}			# dictionary of draw locations for
							#   PSGs on the screen, used for info console
							
		self.target_hexes = []			# list of hexes in the viewport that are
							#   within target arc and range
		self.target_list = []			# list of possible enemy targets
		self.target_psg = None			# currently selected target
		self.target_coords = None		# x,y location of target in window
							#  updated by psg.DrawMe()
		self.selected_coords = None		# " selected PSG
		
		# create the hex map
		self.hex_map = HexMap(map_w, map_h)
		self.objective_hexes = []			# list of objective hexes
		self.spawn_hexes = []				# list of enemy spawn hexes
	
	# check to see if scenario has ended, triggered at start of every new turn
	def CheckForEnd(self):
		
		# player PSG has been destroyed
		if not self.player_psg in self.psg_list:
			self.winner = 1
			self.end_text = 'Player PSG was destroyed'
			return
		
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
	
	
	# clear hex selection mode
	def EndHexSelection(self):
		self.selected_vp_hex = None
		self.allowed_vp_hexes = []
	
	# start a new scenario turn
	def NextTurn(self):
		for psg in self.psg_list:
			psg.ResetNewTurn()
		self.RebuildOOBList()
		self.CheckForEnd()
	
	# re-order psg list so that PSGs that are next to act are at top
	def RebuildOOBList(self, flash_animate=False):
		self.oob_list = []
		self.active_psg = None
		for n in range(1, 100):
			n_list = []
			for psg in self.psg_list:
				if psg.tu == n: n_list.append(psg)
			if len(n_list) == 0: continue
			# randomly shuffle this sub-list of PSGs in place
			shuffle(n_list)
			# add this list to the oob
			self.oob_list.extend(n_list[:])
		# set a pointer to the PSG at the top of the list, it is now active
		if len(self.oob_list) > 0:
			self.active_psg = self.oob_list[0]
		# re-draw the console, animate highlight top line
		UpdateOOBConsole(flash_animate=flash_animate)
	
	# the active PSG has acted, move it down the list and pick a new active PSG
	def MoveActivePSGInList(self):
		
		# trigger post-activation automatic actions for active PSG
		if self.active_psg is not None:
			self.active_psg.DoPostActivationActions()
		
		self.oob_list.remove(self.active_psg)
		
		# PSG has not finished acting for this turn
		if self.active_psg.tu > 0:
		
			# find where this PSG should go in the list
			n = 0
			for psg in self.oob_list:
				# reached end of list, add unit at end of list
				if len(self.oob_list) <= n+1:
					self.oob_list.append(self.active_psg)
					break
				# check following psg, if it has less TU than active unit,
				#   insert it here
				if self.oob_list[n+1].tu < self.active_psg.tu:
					self.oob_list.insert(n, self.active_psg)
					break
				n += 1
		
		# select new active PSG if any remain
		self.active_psg = None
		if len(self.oob_list) > 0:
			self.active_psg = self.oob_list[0]
		
		# re-draw the console
		UpdateOOBConsole(flash_animate=True)
		
	# build a list of hexes that can be targeted
	# TODO: change based on scenario.player_active_weapon
	def BuildTargetHexes(self):
		# clear any existing list
		self.target_hexes = []
		
		for (hx, hy) in ARC_HEXES:
			
			# rotate based on player turret rotation
			(hx, hy) = RotateHex(hx, hy, self.player_psg.turret_facing)
			
			# shift to player position
			hx += self.player_psg.hx
			hy += self.player_psg.hy
			
			# skip if off map, not visible, or out of range
			if (hx, hy) not in self.hex_map.hexes: continue
			if not self.hex_map.hexes[(hx, hy)].vis_to_player: continue
			if self.player_active_weapon.ift_weapon:
				dist = GetHexDistance(hx, hy, self.player_psg.hx,
					self.player_psg.hy)
				if self.player_active_weapon.stats['normal_range'] < dist:
					continue
			
			self.target_hexes.append((hx, hy))
	
	# build a list of possible enemy targets
	def BuildTargetList(self):
		# clear any existing list
		self.target_list = []
		for psg in self.psg_list:
			if psg.owning_player == 0: continue
			
			# if MG weapon is active and attacker has moved, can't target vehicles
			if 'ift_class' in self.player_active_weapon.stats:
				if self.player_active_weapon.stats['ift_class'] == 'MG':
					if self.player_psg.moved[0] and psg.vehicle:
						continue
			if (psg.hx, psg.hy) in self.target_hexes:
				self.target_list.append(psg)
	
	# select next (or first) target in list
	def SelectNextTarget(self):
		
		# no targets to select
		if len(self.target_list) == 0: return
		
		if self.target_psg is None:
			self.target_psg = self.target_list[0]
		else:
			n = self.target_list.index(self.target_psg)
			if n == len(self.target_list) - 1:
				self.target_psg = self.target_list[0]
			else:
				self.target_psg = self.target_list[n+1]
		
		# set LoS to display
		self.active_los = (self.player_psg, self.target_psg)
		
		# update unit console to record the x, y coordinate of the target unit
		UpdateUnitConsole()
		UpdateMapGUIConsole()
		DrawScreenConsoles()
		
		# add message describing chance to hit
		#(base_th, roll_req, drm) = CalcTH(self.player_psg,
		#	self.player_active_weapon, self.target_psg)
		#text = 'To hit: ' + str(roll_req)
		#Message(self.target_psg.screen_x, self.target_psg.screen_y, text)
	
	# cancel target mode
	def CancelTarget(self):
		self.player_active_weapon = None
		self.target_list = []
		self.target_psg = None
		self.active_los = None
		self.target_hexes = []			
			
	# rebuild a list of commands for the command menu based on current phase and
	#   game state
	def BuildCmdMenu(self):
		
		# clear any existing command menu
		self.cmd_menu.Clear()
		
		weapon = scenario.player_active_weapon
		
		# don't display anything if player PSG is not active
		if scenario.active_psg != scenario.player_psg:
			UpdateCmdConsole()
			return
		
		# root command menu
		if self.active_cmd_menu == 'root':
			self.cmd_menu.AddOption('movement', '1', 'Movement',
				desc='Commands associated with moving around the map')
			self.cmd_menu.AddOption('shooting', '2', 'Shooting',
				desc='Initiate a ranged attack with one or more weapons')
			new_option = self.cmd_menu.AddOption('assault', '3', 'Assault')
			new_option.inactive = True
			self.cmd_menu.AddOption('orders', '4', 'Orders',
				desc='Issue new orders to a subordinate unit')
			if scenario.player_psg.tu >= 8:
				tu_cost = 8
			else:
				tu_cost = scenario.player_psg.tu
			self.cmd_menu.AddOption('wait', '0', 'Wait', exit_option=True,
				tu_cost=tu_cost, desc='Do nothing for the moment')
		
		# movement menu
		elif self.active_cmd_menu == 'movement':
			# forward move
			map_hex1 = GetHexAt(self.player_psg.hx, self.player_psg.hy)
			(hx, hy) = GetAdjacentHex(self.player_psg.hx, self.player_psg.hy,
				self.player_psg.facing)
			map_hex2 = GetHexAt(hx, hy)
			tu_cost = GetTUCostToMove(self.player_psg, map_hex1, map_hex2)
			new_option = self.cmd_menu.AddOption('move_fwd', 'W', 'Forward Move',
				tu_cost=tu_cost, desc='Move your squadron forward ' +
				'into the adjacent map hex, maintaining facing')
			# move not allowed
			if not self.player_psg.CheckMoveInto(hx, hy):
				new_option.inactive = True
			
			# reverse move
			(hx, hy) = GetAdjacentHex(self.player_psg.hx, self.player_psg.hy,
				ConstrainDir(self.player_psg.facing + 3))
			map_hex2 = GetHexAt(hx, hy)
			tu_cost = GetTUCostToMove(self.player_psg, map_hex1, map_hex2) * 4
			
			new_option = self.cmd_menu.AddOption('move_rev', 'S', 'Reverse Move',
				tu_cost=tu_cost, desc='Move your squadron in ' +
				'reverse into the adjacent map hex, maintaining facing')
			# move not allowed
			if not self.player_psg.CheckMoveInto(hx, hy):
				new_option.inactive = True
			
			new_option = self.cmd_menu.AddOption('hull_ccw', 'A', 'Hull C/Clockwise',
				tu_cost=0, desc='Pivot your hull counter-clockwise')
			new_option = self.cmd_menu.AddOption('hull_cw', 'D', 'Hull Clockwise',
				tu_cost=0, desc='Pivot your hull clockwise')
			self.cmd_menu.AddOption('return_to_root', '0', 'Return to Root Menu',
				exit_option=True, desc='Return to the root command menu')
		
		# shooting menu
		elif self.active_cmd_menu == 'shooting':
			# list all possible weapon systems in PSG
			n = 0
			for weapon in self.player_psg.weapon_list:
				action_id = 'act_weap_' + str(n)
				action_key = str(n+1)
				text = weapon.GetName()
				tu_cost = weapon.stats['fire_tu']
				
				new_option = self.cmd_menu.AddOption(action_id, action_key,
					text, tu_cost=tu_cost,
					desc='Fire this weapon at an enemy unit')
				# see if this weapon cannot be fired right now
				if weapon.ord_weapon:
					if weapon.reloading_tu > 0:
						new_option.inactive = True
				n += 1
			self.cmd_menu.AddOption('return_to_root', '0', 'Return to Root Menu',
				exit_option=True, desc='Return to the root command menu')
		
		# targeting weapon menu
		elif self.active_cmd_menu == 'targeting':
			new_option = self.cmd_menu.AddOption('next_target', 'Tab',
				'Select Next Target')
			# no targets available
			if len(self.target_list) == 0: new_option.inactive = True
			
			tu_cost = weapon.stats['fire_tu']
			
			new_option = self.cmd_menu.AddOption('fire', 'F', 'Fire at Target',
				tu_cost=tu_cost)
			# no target selected
			if self.target_psg is None:
				new_option.inactive = True
			
			self.cmd_menu.AddOption('return_to_shooting', '0', 'Return to Shooting Menu', exit_option=True)
		
		# orders menu
		elif self.active_cmd_menu == 'orders':
			# list all subordinate units
			n = 0
			for psg in scenario.psg_list:
				if psg == scenario.player_psg: continue
				if psg.owning_player == 0:
					action_id = 'order_unit_' + str(n)
					key_code = str(n+1)
					text = psg.GetName()
					self.cmd_menu.AddOption(action_id, key_code,
						text, desc='Issue new orders to ' +
						text)
			
			self.cmd_menu.AddOption('return_to_root', '0', 'Return to Root Menu',
				exit_option=True, desc='Return to the root command menu')
		
		# PSG orders menu
		elif self.active_cmd_menu == 'psg_orders':
			
			# FUTURE: list all possible orders
			# for now, start of a generic hex selection menu
			self.cmd_menu.AddOption('hex_sel_q', 'Q', 'Up and Left',
				desc='Move selected hex up and left')
			self.cmd_menu.AddOption('hex_sel_w', 'W', 'Up',
				desc='Move selected hex up')
			self.cmd_menu.AddOption('hex_sel_e', 'E', 'Up and Right',
				desc='Move selected hex up and right')
			self.cmd_menu.AddOption('hex_sel_a', 'A', 'Down and Left',
				desc='Move selected hex down and left')
			self.cmd_menu.AddOption('hex_sel_s', 'S', 'Down',
				desc='Move selected hex down')
			self.cmd_menu.AddOption('hex_sel_d', 'D', 'Down and Right',
				desc='Move selected hex down and right')
			self.cmd_menu.AddOption('order_to_hex', 'F', 'Take New Position',
				desc='Order the selected unit to take up this position ' +
				'relative to your unit')
			
			self.cmd_menu.AddOption('cancel_psg_orders', '0', 'Cancel',
				exit_option=True, desc='Return to orders command menu')
			
		
		UpdateCmdConsole()
		return
		
		
		# TODO: add back in these commands:
		self.cmd_menu.AddOption('turret_ccw', 'Q', 'Turret C/Clockwise')
		self.cmd_menu.AddOption('turret_cw', 'E', 'Turret Clockwise')

	# spawn random enemy units near all spawn hexes
	def SpawnEnemyUnits(self):
		for map_hex in self.spawn_hexes:
			
			# roll for how many units are spawned nearby
			d1, d2, roll = Roll2D6()
			
			if d1 <= 4:
				n = 1
			else:
				n = 2
			
			# get list of possible spawn locations
			hex_list = GetHexesWithin(map_hex.hx, map_hex.hy, 3)
			
			for i in range(n):
				
				shuffle(hex_list)
				
				# determine type of unit
				d1, d2, roll = Roll2D6()
				
				if roll <= 8:
					new_psg = PSG('AT Gun Platoon', '37mm wz. 36', 1,
						3, None, 1, 10, 9)
				else:
					new_psg = PSG('Czolgów Platoon', '7TP jw', 2, 3,
						3, 1, 10, 9)
				
				self.psg_list.append(new_psg)
				
				# determine the location to spawn the new unit
				for (hx, hy) in hex_list:
					
					spawn_hex = GetHexAt(hx, hy)
					if spawn_hex.water: continue
					d1, d2, roll = Roll2D6()
					
					roll += spawn_hex.GetTerrainMod(new_psg)
					distance = GetHexDistance(map_hex.hx, map_hex.hy,
						hx, hy)
					roll += distance
					
					if roll <= 7:
						new_psg.hx = hx
						new_psg.hy = hy
						spawn_hex.contained_psgs.append(new_psg)
						new_psg.SetDrawLocation()
						break
					
				print ('DEBUG: Spawned a ' + new_psg.GetName(true_name=True) +
					' at ' + str(new_psg.hx) + ',' + str(new_psg.hy))
	
		# now that we've added new enemy units, rebuild the OOB list
		scenario.RebuildOOBList()



##########################################################################################
#                                     General Functions                                  #
##########################################################################################

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
	if not GetLoS(attacker.hx, attacker.hy, target.hx, target.hy):
		return -1
	
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
	
	# target hex terrain modifier
	map_hex = GetHexAt(target.hx, target.hy)
	terrain_mod = map_hex.GetTerrainMod(target)
	if terrain_mod != 0:
		attack_obj.drm.append(('Terrain Modifier', terrain_mod))
	
	if attacker.moved[0]:
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
		
		if attacker.moved[0]:
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
		# target hex terrain modifier
		map_hex = GetHexAt(target.hx, target.hy)
		terrain_mod = map_hex.GetTerrainMod(target)
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


# returns the three grid locations on given edge relative to x,y
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


# plot the center of a given hex on an orthographic grid
def PlotHex(hx, hy):
	x = hx*4
	y = (hy*4) + (hx*2)
	# place it in the middle of the map console on the screen
	return (x+28,y+28)


# rotates a hex location around 0, 0, clockwise r times
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
				if GetHexAt(hx2, hy2).IsOccupiedByEnemy(skip_occupied):
					continue
			hex_list.append((hx2, hy2))
	return hex_list
	

# returns the direction to an adjacent hex
def GetDirectionToAdjacent(hx1, hy1, hx2, hy2):
	hx_mod = hx2 - hx1
	hy_mod = hy2 - hy1
	if (hx_mod, hy_mod) in DESTHEX:
		return DESTHEX.index((hx_mod, hy_mod))
	print 'ERROR: GetDirectionToAdjacent() hex is not adjacent'
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


# calcualte the TU required to move into the target hex
def GetTUCostToMove(psg, map_hex1, map_hex2):
	
	# linked by road
	road = False
	direction = GetDirectionToAdjacent(map_hex1.hx, map_hex1.hy, map_hex2.hx, map_hex2.hy)
	if direction in map_hex1.dirt_road_links: road = True
	
	if psg.movement_class == 'Infantry':
		if map_hex2.difficult: return 12
		if road: return 8
		return 12
	
	if psg.movement_class == 'Fast Tank':
		if map_hex2.difficult: return 10
		if road: return 4
		return 6
	
	if psg.movement_class == 'Wheeled':
		if map_hex2.difficult: return 24
		if road: return 4
		return 6


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
			if node.water: continue
			
			# TODO: calculate movement cost
			if movement_class is not None:
				pass
			
			# TEMP - intended for roads only
			if node.terrain_type == FOREST:
				cost = 6
			elif node.terrain_type == FIELDS:
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


# returns the bearing from x1, y1 to x2, y2
def GetBearing(x1, y1, x2, y2):
	xdist = float(x2 - x1)
	ydist = float(y2 - y1)
	# prevent dividing by zero for 0 slope lines
	if ydist == 0.0:
		if xdist > 0.0:
			return 90
		else:
			return 270
	if y1 > y2:
		angle = atan(xdist/ydist)*180.0/PI*-1.0
	else:
		angle = atan(xdist*-1/ydist*-1)*180.0/PI*-1.0
		angle -= 180.0
	return RectifyHeading(int(angle))


# returns true if a line of sight exists between the two hexes, false if not
def GetLoS(hx1, hy1, hx2, hy2):
	# same hex
	if hx1 == hx2 and hy1 == hy2:
		return True
	# adjacent hex
	if GetHexDistance(hx1, hy1, hx2, hy2) == 1:
		return True
	line = GetHexLine(hx1, hy1, hx2, hy2)
	# skip first and last hex, only check hexes in between
	for (hx, hy) in line[1:-1]:
		map_hex = GetHexAt(hx, hy)
		if map_hex.blocks_los:
			return False
	return True
	

##########################################################################################
#                                  Campaign Day Functions                                #
##########################################################################################

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
	if map_hex.GetTerrainMod(target) > 0: distance -= 1
	if target.fired[0]: distance += 3
	if target.moved[0]: distance += 1
	if target.dug_in: distance -= 1
	if target.suppressed: distance -= 1
	if target.pinned: distance -= 1
	
	# spotter modifiers
	if spotter.recce: distance += 2
	if spotter.dug_in: distance += 1
	if spotter.moved[0]: distance -= 1
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
	
	# clear any LoS and target hex displays
	if scenario.active_los is not None:
		scenario.active_los = None
		scenario.target_hexes = []
		libtcod.console_clear(map_gui_con)
		DrawScreenConsoles()
	
	# determine weapon used in attack
	if attacker == scenario.player_psg:
		weapon = scenario.player_active_weapon
	else:
		# TEMP - assume first weapon in list
		weapon = attacker.weapon_list[0]
	
	# spend TU required for this attack
	tu_cost = weapon.stats['fire_tu']
	
	# can always perform action if have at least min TU required
	# TEMP?
	if tu_cost > attacker.tu: tu_cost = attacker.tu
	
	# spend the TU
	attacker.SpendTU(tu_cost)
	
	# send information to CalcAttack, which will return an Attack object with the
	# calculated stats to use for the attack
	attack_obj = CalcAttack(attacker, weapon, target)

	# display attack console for this attack
	# NEW: if attacker or target are player PSG
	skip_wait = True
	if attacker == scenario.player_psg or target == scenario.player_psg:
		if attack_obj.ift_attack:
			DisplayIFTRoll(attack_obj)
		else:
			DisplayToHitRoll(attack_obj)
		skip_wait = False
	
	# animate LoS from attacker to target
	line = GetLine(attacker.screen_x, attacker.screen_y, target.screen_x, target.screen_y)
	for (x,y) in line[1:-1]:
		libtcod.console_put_char_ex(map_gui_con, x-30, y-1, 250,
			libtcod.red, libtcod.black)
		libtcod.console_blit(map_gui_con, 0, 0, 57, 58, 0, 30, 1, 1.0, 0.0)
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
		if key.vk == libtcod.KEY_ENTER:
			skip_wait = True
			break
		Wait(50)
	
	if not skip_wait:
		WaitForEnter()
	
	# clear LoS from screen
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0)
	libtcod.console_flush()
	
	# Perform Attack
	
	# IFT attack: roll once for entire PSG
	# TODO: separate animations for MGs and small arms
	if attack_obj.ift_attack:
		IFTAttackAnimation(attack_obj)
		target.ResolveIFTAttack(attack_obj)
	
	# to-hit attack, roll once for each step
	else:
	
		# roll for attacks and show animations
		total_hits = 0
		
		for i in range(attacker.num_steps):
			d1, d2, roll = Roll2D6()
			hit = False
			if roll <= attack_obj.roll_req:
				hit = True
			OrdAttackAnimation(attack_obj, hit)
			if hit:
				total_hits += 1
		
		# display message stating how many hits
		if total_hits == 0:
			text = 'No hits on target'
			Message(attack_obj.target.screen_x, attack_obj.target.screen_y,
				text)
			
		else:
		
			text = str(total_hits) + ' hit'
			if total_hits > 1: text += 's'
			text += ' on target!'
			Message(attack_obj.target.screen_x, attack_obj.target.screen_y,
				text)
			
			# resolve hits
			# TEMP: shells magically transform based on target type
			
			# AP attack
			if attack_obj.target.vehicle:
				for h in range(total_hits):
					attack_obj.target.ResolveAPHit(attack_obj)
					# add extra pause to distinguish 2+ messages
					Wait(config.getint('ArmCom2', 'message_pause_time'))
					# possible that PSG was destroyed
					if attack_obj.target not in scenario.psg_list:
						break
			
			# HE attack
			else:
				
				# calculate the IFT attack of HE hit(s)
				hit_object = CalcIFT(attack_obj.attacker,
					attack_obj.weapon, attack_obj.target,
					hit_result=True, multiple_hits=total_hits)
				
				# display hit result IFT and resolve it
				if attacker == scenario.player_psg or target == scenario.player_psg:
					DisplayIFTRoll(hit_object, hit_result=True)
					WaitForEnter()
				target.ResolveIFTAttack(hit_object)
				
	# set reload timer if IFT weapon
	if weapon.ord_weapon:
		weapon.reloading_tu = libtcod.random_get_int(0,
			weapon.stats['reload_tu_min'], weapon.stats['reload_tu_max'])
	
	# set action flag
	attacker.fired[1] = True


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
	libtcod.console_print_ex(attack_con, 15, 47, libtcod.BKGND_NONE, libtcod.CENTER,
		'Total Modifier: ' + text)
	
	# display possible rolls and outcomes
	libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR2)
	libtcod.console_rect(attack_con, 1, 51, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print(attack_con, 3, 51, '2 3 4 5 6 7 8 9 10 11 12')
	
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
		libtcod.console_print(attack_con, x, 52, result[0])
		libtcod.console_print(attack_con, x, 53, result[1])
	
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
	
	# final to-hit roll required
	libtcod.console_set_default_background(attack_con, HIGHLIGHT_BG_COLOR2)
	libtcod.console_rect(attack_con, 1, 51, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print_ex(attack_con, 15, 51, libtcod.BKGND_NONE, libtcod.CENTER,
		'Final To-Hit: ' + chr(243) + str(attack_obj.roll_req))
	
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

	# do first pass of terrain generation
	for map_hex in hex_list:
		
		# if there's already an adjcacent pond, don't create another one
		if HasAdjacent(map_hex, POND):
			pond_chance = 0
		else:
			pond_chance = 5
		
		# if there's already an adjacent forest, higher chance of there being one
		if HasAdjacent(map_hex, FOREST):
			forest_chance = 30
		else:
			forest_chance = 10
		
		# if there's already an adjacent field, higher chance of there being one
		if HasAdjacent(map_hex, FIELDS):
			field_chance = 10
		else:
			field_chance = 5
		
		roll = libtcod.random_get_int(0, 1, 100)
		
		if roll <= pond_chance:
			map_hex.terrain_type = POND
			map_hex.water = True
			continue
		
		roll -= pond_chance
		
		if roll <= forest_chance:
			map_hex.terrain_type = FOREST
			map_hex.blocks_los = True
			map_hex.difficult = True
			continue
		
		roll -= forest_chance
			
		if roll <= field_chance:
			map_hex.terrain_type = FIELDS
	
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
			

# show an ordinance attack firing animation
def OrdAttackAnimation(attack_obj, hit):
	
	# redraw screen consoles to clear any old GUI display
	DrawScreenConsoles()
	libtcod.console_flush()
	
	# use draw locations, but we'll be drawing to the GUI console so
	#   modify by -30, -1
	x1, y1 = attack_obj.attacker.screen_x-30, attack_obj.attacker.screen_y-1
	x2, y2 = attack_obj.target.screen_x-30, attack_obj.target.screen_y-1
	
	# scatter actual hit location if shot missed
	# uses the turret character plot locations for simplicity
	if not hit:
		(xmod, ymod) = choice(PLOT_DIR)
		x2 += xmod
		y2 += ymod
	
	# projectile animation
	line = GetLine(x1, y1, x2, y2, los=True)
	
	pause_time = config.getint('ArmCom2', 'animation_speed')
	pause_time2 = int(pause_time / 2)
	
	for (x, y) in line:
		UpdateMapGUIConsole()
		libtcod.console_put_char_ex(map_gui_con, x, y, 250,
			libtcod.white, libtcod.black)
		DrawScreenConsoles()
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
		libtcod.console_flush()
		Wait(pause_time2)
		
	libtcod.console_clear(map_gui_con)
	DrawScreenConsoles()
	libtcod.console_flush()


# show a small arms / MG firing animation
def IFTAttackAnimation(attack_obj):
	
	# redraw screen consoles to clear any old GUI display
	DrawScreenConsoles()
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
		libtcod.console_flush()
		Wait(pause_time)
	
	libtcod.console_clear(map_gui_con)
	DrawScreenConsoles()
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


# re-paint the map viewport layer, drawing information from the campaign day map
# each hex is 5x5 cells, but edges overlap with adjacent hexes
def PaintMapVP():
	
	# paint a single hex onto the map vp console
	# hx, hy is local to the viewport: 0,0 is player location at center of VP
	def PaintHex(hx, hy):
		
		if (hx, hy) not in scenario.hex_map.vp_matrix: return
		
		# find this hex on the campaign day map
		map_hex = scenario.hex_map.vp_matrix[(hx,hy)]
		
		(x,y) = PlotHex(hx, hy)
		
		# paint hex console image here, if not visible use grey hex
		if not map_hex.vis_to_player:
			h_con = grey_hex_con
		else:
			h_con = hex_con
		libtcod.console_blit(h_con, 0, 0, 7, 5, map_vp_con, x-3, y-2)

		# draw greebles overtop if required
		if map_hex.terrain_type != OPEN_GROUND:
			
			char = None
			col = None
			bg_col = None
			
			if map_hex.terrain_type == POND:
				bg_col = WATER_COL
			if map_hex.terrain_type == FOREST:
				col = FOREST_COL
				bg_col = FOREST_BG_COL
				char = 6
			elif map_hex.terrain_type == FIELDS:
				col = FIELDS_COL
				char = 177
			
			# grey out if tile is not visible to player
			if not map_hex.vis_to_player:
				if col is not None:
					col = col * libtcod.grey
				if bg_col is not None:
					bg_col = bg_col * libtcod.grey
			
			for dy in range(y-1, y+2):
				if dy == y:
					min_x = x-2
					max_x = x+2
				else:
					min_x = x-1
					max_x = x+1
				for dx in range(min_x, max_x+1):
					if char is not None:
						libtcod.console_set_char(map_vp_con,
							dx, dy, char)
					if col is not None:
						libtcod.console_set_char_foreground(map_vp_con,
							dx, dy, col)
					if bg_col is not None:
						libtcod.console_set_char_background(map_vp_con,
							dx, dy, bg_col)

	
	libtcod.console_set_default_background(map_vp_con, KEY_COLOR)
	libtcod.console_clear(map_vp_con)
	libtcod.console_set_default_background(map_vp_con, OPEN_GROUND_COL)
	libtcod.console_set_default_foreground(map_vp_con, libtcod.grey)
	
	for (hx, hy) in VP_HEXES:
		PaintHex(hx,hy)
	
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
		#			libtcod.console_set_char_background(map_vp_con, rx, ry, RIVER_BG_COL, flag=libtcod.BKGND_SET)
		
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
					libtcod.console_set_char_background(map_vp_con, x, y, col, libtcod.BKGND_SET)
					
					# if character is not blank or hex edge, remove it
					if libtcod.console_get_char(map_vp_con, x, y) not in [0, 250]:
						libtcod.console_set_char(map_vp_con, x, y, 0)

	# highlight any objective hexes
	for (vp_hx, vp_hy), map_hex in scenario.hex_map.vp_matrix.iteritems():
		if map_hex.objective is not None:
			(x,y) = PlotHex(vp_hx, vp_hy)
			temp = LoadXP('ArmCom2_objective_highlight.xp')
			libtcod.console_set_key_color(temp, KEY_COLOR)
			libtcod.console_blit(temp, 0, 0, 7, 5, map_vp_con, x-3, y-2, 1.0, 0.0)
			del temp
	
	# draw indicators for any off-map objective hexes
	libtcod.console_set_default_background(map_vp_con, libtcod.black)
	libtcod.console_set_default_foreground(map_vp_con, libtcod.white)
	y = 0
	for map_hex in scenario.objective_hexes:
		distance = GetHexDistance(scenario.player_psg.hx, scenario.player_psg.hy,
			map_hex.hx, map_hex.hy)
		if distance > 6:
			direction = GetDirectionToward(scenario.player_psg.hx,
				scenario.player_psg.hy, map_hex.hx, map_hex.hy)
			direction = ConstrainDir(direction - scenario.player_psg.facing)
			char = GetDirectionalArrow(direction)
			
			text = 'Objective ' + char + ' ' + str(distance*160) + 'm.'
			libtcod.console_print_ex(map_vp_con, 56, y, libtcod.BKGND_SET,
				libtcod.RIGHT, text)
			y += 1
			


# updates the map viewport gui layer
def UpdateMapGUIConsole():
	libtcod.console_clear(map_gui_con)
	
	# highlight current target hexes
	if len(scenario.target_hexes) > 0:
		temp = LoadXP('ArmCom2_tile_highlight.xp')
		for (vp_hx, vp_hy), map_hex in scenario.hex_map.vp_matrix.iteritems():
			if (map_hex.hx, map_hex.hy) in scenario.target_hexes:
				(x,y) = PlotHex(vp_hx, vp_hy)
				libtcod.console_blit(temp, 0, 0, 7, 5, map_gui_con, x-3, y-2)
		del temp
	
	# display active targeting LoS if any
	if scenario.active_los is not None:
		(psg1, psg2) = scenario.active_los
		line = GetLine(psg1.screen_x, psg1.screen_y, psg2.screen_x, psg2.screen_y)
		# TODO: determine if attacker has turret character to skip
		for (x,y) in line[2:-1]:
			libtcod.console_put_char_ex(map_gui_con, x-30, y-1, 250,
				libtcod.red, libtcod.black)

	# display currently selected hex if any
	if scenario.selected_vp_hex is not None:
		(vp_hx, vp_hy) = scenario.selected_vp_hex
		(x,y) = PlotHex(vp_hx, vp_hy)
		temp = LoadXP('ArmCom2_tile_highlight.xp')
		libtcod.console_blit(temp, 0, 0, 7, 5, map_gui_con, x-3, y-2)
		del temp
		

# paints active and visible PSGs onto unit console
def UpdateUnitConsole():
	libtcod.console_clear(unit_con)
	
	# run through locations in map viewport, and if there's a psg here, draw it
	for (vp_hx, vp_hy), map_hex in scenario.hex_map.vp_matrix.iteritems():
		for psg in scenario.psg_list:
			if psg.hx == map_hex.hx and psg.hy == map_hex.hy:
				psg.DrawMe(vp_hx, vp_hy)


# updates the player tank info console
# TODO: in future, will display detailed info on any PSG
def UpdateTankConsole():
	libtcod.console_clear(tank_con)
	
	# TEMP - always show player PSG info
	psg = scenario.player_psg
	
	# PSG name
	libtcod.console_print(tank_con, 0, 0, psg.GetName())
	
	# unit type
	libtcod.console_set_default_foreground(tank_con, HIGHLIGHT_COLOR)
	libtcod.console_print(tank_con, 0, 1, psg.step_name)
	libtcod.console_set_default_foreground(tank_con, libtcod.white)
	
	# vehicle portrait
	libtcod.console_set_default_background(tank_con, PORTRAIT_BG_COL)
	libtcod.console_rect(tank_con, 0, 2, 28, 8, False, libtcod.BKGND_SET)
	libtcod.console_set_default_background(tank_con, libtcod.black)
	
	if psg.portrait is not None:
		temp = LoadXP(psg.portrait)
		if temp is not None:
			x = 14 - int(libtcod.console_get_width(temp) / 2)
			libtcod.console_blit(temp, 0, 0, 0, 0, tank_con, x, 2)
		else:
			print 'ERROR: unit portrait not found: ' + psg.portrait
	
	y = 10
	
	# morale and skill levels
	libtcod.console_set_default_background(tank_con, libtcod.dark_grey)
	libtcod.console_rect(tank_con, 0, y, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print(tank_con, 0, y, MORALE_DESC[str(psg.morale_lvl)])
	libtcod.console_print_ex(tank_con, 27, y, libtcod.BKGND_NONE, libtcod.RIGHT,
		SKILL_DESC[str(psg.skill_lvl)])
	
	# weapon list
	y += 2
	libtcod.console_set_default_background(tank_con, HIGHLIGHT_BG_COLOR)
	
	for weapon in psg.weapon_list:
		libtcod.console_rect(tank_con, 0, y, 28, 1, False, libtcod.BKGND_SET)
		if weapon.ord_weapon:
			text = str(weapon.stats['calibre']) + 'mm' + weapon.stats['long_range']
			libtcod.console_print(tank_con, 0, y, text)
			# reload status
			# TEMP: no ammo type displayed
			text = ''
			if weapon.reloading_tu > 0:
				text = ('Reloading ' + text + ' (' + 
					str(weapon.reloading_tu) + ')')
			else:
				text += ' Loaded'
			libtcod.console_print_ex(tank_con, 27, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
		else:
			libtcod.console_print(tank_con, 0, y, weapon.stats['name'])
			text = str(weapon.stats['fp']) + '-' + str(weapon.stats['normal_range'])
			libtcod.console_print_ex(tank_con, 27, y, libtcod.BKGND_NONE,
				libtcod.RIGHT, text)
		y += 1
	y += 1
	
	# armour ratings if any
	if psg.armour:
		text = ('Turret ' + str(psg.armour['turret_front']) + '/' +
			str(psg.armour['turret_side']))
		libtcod.console_print(tank_con, 0, y, text)
		text = ('Hull   ' + str(psg.armour['hull_front']) + '/' +
			str(psg.armour['hull_side']))
		libtcod.console_print(tank_con, 0, y+1, text)
	
	# Movement class and TU
	libtcod.console_set_default_foreground(tank_con, libtcod.green)
	libtcod.console_print_ex(tank_con, 27, y, libtcod.BKGND_NONE,
		libtcod.RIGHT, psg.movement_class)
	text = str(psg.tu) + '/' + str(psg.max_tu) + ' TU'
	libtcod.console_print_ex(tank_con, 27, y+1, libtcod.BKGND_NONE,
		libtcod.RIGHT, text)
	
	y += 3
	
	# action status flags
	libtcod.console_set_default_foreground(tank_con, libtcod.lighter_blue)
	libtcod.console_set_default_background(tank_con, HIGHLIGHT_BG_COLOR2)
	libtcod.console_rect(tank_con, 0, y, 28, 1, False, libtcod.BKGND_SET)
	
	if psg.moved[0]:
		libtcod.console_print(tank_con, 0, y, 'Moved')
	elif psg.dug_in:
		libtcod.console_print(tank_con, 0, y, 'Dug-in')
	elif psg.hull_down > -1:
		text = 'HD '
		# TODO: add directional character
		libtcod.console_print(tank_con, 0, y, text)
	if psg.fired[0]:
		libtcod.console_print(tank_con, 8, y, 'Fired')
	if psg.changed_facing:
		libtcod.console_print(tank_con, 14, y, 'Pivoted')
	if psg.changed_turret_facing:
		libtcod.console_print(tank_con, 22, y, 'Turret')
	
	y += 1
	
	# status flags
	libtcod.console_set_default_foreground(tank_con, libtcod.light_red)
	libtcod.console_set_default_background(tank_con, libtcod.darkest_red)
	libtcod.console_rect(tank_con, 0, y, 28, 1, False, libtcod.BKGND_SET)
	
	if psg.suppressed:
		libtcod.console_print(tank_con, 0, y, 'Suppressed')
	elif psg.pinned:
		libtcod.console_print(tank_con, 0, y, 'Pinned')
	
	
	# TODO: current terrain type
	
	# TODO: vehicle crew?
	#libtcod.console_set_default_background(tank_con, libtcod.dark_grey)
	#libtcod.console_set_default_foreground(tank_con, libtcod.light_grey)
	#libtcod.console_rect(tank_con, 0, 15, 28, 1, False, libtcod.BKGND_SET)
	#libtcod.console_print(tank_con, 0, 15, 'Crew')
	
	libtcod.console_set_default_foreground(tank_con, libtcod.white)
	libtcod.console_set_default_background(tank_con, libtcod.black)


# updates the command console
def UpdateCmdConsole():
	libtcod.console_clear(cmd_con)
	libtcod.console_set_default_background(cmd_con, HIGHLIGHT_BG_COLOR)
	libtcod.console_rect(cmd_con, 0, 0, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print(cmd_con, 0, 0, 'Action')
	libtcod.console_print(cmd_con, 25, 0, 'TU')
	libtcod.console_set_default_background(cmd_con, libtcod.black)
	scenario.cmd_menu.DisplayMe(cmd_con, 1, 2, 28)


# draw PSG info to the PSG info console based on current mouse location
def UpdatePSGInfoConsole():
	libtcod.console_clear(psg_info_con)
	
	# mouse cursor outside of map area
	if mouse.cx < 31 or mouse.cx > 85: return
	if mouse.cy < 3 or mouse.cy > 55: return

	# no PSG being draw here
	if (mouse.cx, mouse.cy) not in scenario.psg_info_map: return
	
	psg = scenario.psg_info_map[(mouse.cx, mouse.cy)]
	
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
	text = str(psg.num_steps) + ' ' + psg.step_name
	libtcod.console_print(psg_info_con, 0, 2, text)
	
	# important unit abilities
	if psg.recce:
		libtcod.console_print(psg_info_con, 0, 4, 'Recce')
	
	# status line
	text = ''
	if psg.pinned:
		text = 'PINNED'
	elif psg.suppressed:
		text = 'SUPPRESSED'
	libtcod.console_print(psg_info_con, 0, 5, text)
	
	text = ''
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
	if mouse.cx < 31 or mouse.cx > 85: return
	if mouse.cy < 3 or mouse.cy > 55: return
	
	x = mouse.cx - 30
	y = mouse.cy - 1
	
	if (x,y) in SCREEN_TO_VP_HEX:
		(vp_hx, vp_hy) = SCREEN_TO_VP_HEX[(x,y)]
		
		# this hex is not on the map
		if (vp_hx, vp_hy) not in scenario.hex_map.vp_matrix: return
		
		map_hex = scenario.hex_map.vp_matrix[(vp_hx, vp_hy)]
		
		# TEMP: TODO need a terrain class?
		if map_hex.terrain_type == OPEN_GROUND:
			text = 'Open Ground'
		elif map_hex.terrain_type == POND:
			text = 'Pond'
		elif map_hex.terrain_type == FOREST:
			text = 'Woods'
		elif map_hex.terrain_type == FIELDS:
			text = 'Fields'
		libtcod.console_print(hex_info_con, 0, 0, text)
		
		if len(map_hex.dirt_road_links) > 0:
			libtcod.console_print(hex_info_con, 0, 1, 'Dirt Road')
		
		if map_hex.objective is not None:
			libtcod.console_print(hex_info_con, 0, 2, 'Objective')
		

# update the Order of Battle console; if flash_animate, show an animation for the new
#   top PSG in the list
def UpdateOOBConsole(flash_animate=False):
	libtcod.console_set_default_foreground(oob_con, libtcod.white)
	libtcod.console_set_default_background(oob_con, libtcod.black)
	libtcod.console_clear(oob_con)
	
	libtcod.console_set_default_background(oob_con, HIGHLIGHT_BG_COLOR)
	libtcod.console_rect(oob_con, 0, 0, 28, 1, False, libtcod.BKGND_SET)
	libtcod.console_print(oob_con, 0, 0, 'Order of Battle')
	libtcod.console_print(oob_con, 25, 0, 'TU')
	
	# list first 8 PSGs to act next in order, 
	n = 1
	for psg in scenario.oob_list:
		
		if psg.owning_player == 1 and psg.hidden:
			col = libtcod.grey
			name_text = ['Possible Enemy Platoon']
			tu_text = '?'
		else:
			col = libtcod.white
			name_text = wrap(psg.GetName(), 23, subsequent_indent = ' ')
			tu_text = str(psg.tu)
		
		libtcod.console_set_default_foreground(oob_con, col)
		h = len(name_text)
		libtcod.console_print(oob_con, 1, n, name_text[0])
		if h > 1:
			n += 1
			libtcod.console_print(oob_con, 1, n, name_text[1])	
		libtcod.console_print_ex(oob_con, 26, n, libtcod.BKGND_NONE,
			libtcod.RIGHT, tu_text)
		
		# highlight if currently active PSG
		if scenario.active_psg is not None:
			if scenario.active_psg == psg:
				libtcod.console_put_char_ex(oob_con, 0, n-(h-1), '[',
					libtcod.light_blue, libtcod.black)
				libtcod.console_put_char_ex(oob_con, 27, n, ']',
					libtcod.light_blue, libtcod.black)
		n += 1
		if n == 9: break
	

# layer the display consoles onto the screen
def DrawScreenConsoles():
	# viewport stuff
	libtcod.console_blit(bkg_console, 0, 0, 88, 60, con, 0, 0)
	libtcod.console_blit(map_vp_con, 0, 0, 57, 58, con, 30, 1)
	libtcod.console_blit(unit_con, 0, 0, 57, 58, con, 30, 1, 1.0, 0.0)
	libtcod.console_blit(map_gui_con, 0, 0, 57, 58, con, 30, 1, 1.0, 0.0)
	libtcod.console_blit(hex_info_con, 0, 0, 21, 6, con, 30, 53)
	libtcod.console_blit(psg_info_con, 0, 0, 21, 6, con, 66, 53)
	
	# highlight current target PSG if any
	if scenario.target_psg is not None:
		(x, y) = scenario.target_coords
		libtcod.console_set_char_background(con, x+30, y+1, TARGET_HL_COL, flag=libtcod.BKGND_SET)
	
	# highlight selected PSG if any
	if scenario.selected_psg is not None:
		(x, y) = scenario.selected_coords
		libtcod.console_set_char_background(con, x+30, y+1, SELECTED_HL_COL, flag=libtcod.BKGND_SET)
	
	libtcod.console_blit(tank_con, 0, 0, 28, 26, con, 1, 1)
	libtcod.console_blit(cmd_con, 0, 0, 28, 20, con, 1, 28)
	libtcod.console_blit(oob_con, 0, 0, 28, 10, con, 1, 49)
	
	libtcod.console_blit(con, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, 0, 0)


# display the in-game menu
def ScenarioMenu():
	
	def UpdateScreen():
		libtcod.console_blit(scen_menu_con, 0, 0, 0, 0, 0, 7, 3)
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
		'playing the scenario in progress', exit_option=True)
	
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
		PlaySound('menu_choice')
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
	global scen_menu_con
	global bkg_console, map_vp_con, map_gui_con
	global unit_con, tank_con, cmd_con, oob_con, attack_con
	global hex_info_con, psg_info_con
	global hex_con, grey_hex_con
	
	def UpdateScreen():
		PaintMapVP()
		UpdateUnitConsole()
		UpdateMapGUIConsole()
		UpdateTankConsole()
		UpdateCmdConsole()
		DrawScreenConsoles()
	
	# create screen consoles
	bkg_console = LoadXP('ArmCom2_bkg.xp')
	
	scen_menu_con = LoadXP('ArmCom2_menu.xp')
	libtcod.console_set_default_background(scen_menu_con, libtcod.black)
	libtcod.console_set_default_foreground(scen_menu_con, libtcod.white)
	libtcod.console_print_ex(scen_menu_con, 37, 2, libtcod.BKGND_NONE, libtcod.CENTER,
		VERSION + SUBVERSION)
	
	# map viewport console
	map_vp_con = libtcod.console_new(57, 58)
	libtcod.console_set_default_background(map_vp_con, KEY_COLOR)
	libtcod.console_set_default_foreground(map_vp_con, libtcod.white)
	libtcod.console_set_key_color(map_vp_con, KEY_COLOR)
	libtcod.console_clear(map_vp_con)
	
	# map gui console
	map_gui_con = libtcod.console_new(57, 58)
	libtcod.console_set_default_background(map_gui_con, KEY_COLOR)
	libtcod.console_set_default_foreground(map_gui_con, libtcod.white)
	libtcod.console_set_key_color(map_gui_con, KEY_COLOR)
	libtcod.console_clear(map_gui_con)
	
	# unit console
	unit_con = libtcod.console_new(57, 58)
	libtcod.console_set_default_background(unit_con, KEY_COLOR)
	libtcod.console_set_default_foreground(unit_con, libtcod.grey)
	libtcod.console_set_key_color(unit_con, KEY_COLOR)
	libtcod.console_clear(unit_con)
	
	# player tank info console
	tank_con = libtcod.console_new(28, 26)
	libtcod.console_set_default_background(tank_con, libtcod.black)
	libtcod.console_set_default_foreground(tank_con, libtcod.white)
	libtcod.console_clear(tank_con)
	
	# command menu console
	cmd_con = libtcod.console_new(28, 20)
	libtcod.console_set_default_background(cmd_con, libtcod.black)
	libtcod.console_set_default_foreground(cmd_con, libtcod.white)
	libtcod.console_clear(cmd_con)
	
	# order of battle (PSG list) console
	oob_con = libtcod.console_new(28, 10)
	libtcod.console_set_default_background(oob_con, libtcod.black)
	libtcod.console_set_default_foreground(oob_con, libtcod.white)
	libtcod.console_clear(oob_con)
	
	# attack resolution console
	attack_con = libtcod.console_new(30, 60)
	libtcod.console_set_default_background(attack_con, libtcod.black)
	libtcod.console_set_default_foreground(attack_con, libtcod.light_grey)
	libtcod.console_clear(attack_con)
	
	# psg info console - used to display info about a psg when mouse cursor
	#   is over its depiction on the map
	psg_info_con = libtcod.console_new(21, 6)
	libtcod.console_set_default_background(psg_info_con, libtcod.black)
	libtcod.console_set_default_foreground(psg_info_con, libtcod.white)
	libtcod.console_clear(psg_info_con)
	
	# map hex info console
	hex_info_con = libtcod.console_new(21, 6)
	libtcod.console_set_default_background(hex_info_con, libtcod.black)
	libtcod.console_set_default_foreground(hex_info_con, libtcod.white)
	libtcod.console_clear(hex_info_con)
	
	# hex image consoles
	# TODO: can be set to a different base colour
	hex_con = LoadXP('ArmCom2_tile_green.xp')
	libtcod.console_set_key_color(hex_con, KEY_COLOR)
	
	# load grey tile to indicate tiles that aren't visible to the player
	grey_hex_con = LoadXP('ArmCom2_tile_grey.xp')
	libtcod.console_set_key_color(grey_hex_con, KEY_COLOR)
	
	
	# here is where a saved game in-progress would be loaded
	if load_savegame:
		LoadGame()
	
	else:
	
		##################################################################################
		#                            Start a new Scenario                                #
		##################################################################################
		
		# create a new campaign day object and hex map
		scenario = Scenario(26, 88)
		GenerateTerrain()
		
		# FUTURE: following will be handled by a Scenario Generator
		# for now, things are set up manually
		
		# set up our objective
		map_hex = GetHexAt(6, 64)
		map_hex.SetObjective('Capture')
		
		
		# spawn the player PSGs
		new_psg = PSG('HQ Panzer Squadron', 'Panzer 35t', 5, 0, 0, 0, 9, 9)
		scenario.player_psg = new_psg
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(6, 82)
		
		new_psg = PSG('Light Panzerspäh Platoon', 'sd_kfz_221', 3, 0, 0, 0, 9, 9)
		scenario.psg_list.append(new_psg)
		new_psg.SpawnAt(5, 82)
		# set AI to protect player
		new_psg.ai.mode = 'Guard'
		new_psg.ai.guard_target = scenario.player_psg
		new_psg.ai.SetGuardPosition()
		
		
		# set up enemy spawn points
		total_map_hexes = len(scenario.hex_map.hexes)
		num_spawn_points = int(total_map_hexes / 170)
		if num_spawn_points < 1:
			num_spawn_points = 1
		
		# TEMP
		num_spawn_points = 0
		
		for i in range(num_spawn_points):
			for map_key, map_hex in sample(scenario.hex_map.hexes.items(), len(scenario.hex_map.hexes)):
				if GetHexDistance(map_hex.hx, map_hex.hy, scenario.player_psg.hx, scenario.player_psg.hy) <= 6:
					continue
				map_hex.spawn_point = True
				scenario.spawn_hexes.append(map_hex)
				print 'Set spawn point at ' + str(map_hex.hx) + ',' + str(map_hex.hy)
				break
	
		# TEMP - testing
		map_hex = GetHexAt(6, 76)
		map_hex.spawn_point = True
		scenario.spawn_hexes.append(map_hex)
		
		map_hex = GetHexAt(6, 70)
		map_hex.spawn_point = True
		scenario.spawn_hexes.append(map_hex)
	
	
		# set up map viewport, also calculates field of view
		scenario.hex_map.UpdateMapVPMatrix()
		
		# build initial command menu
		scenario.active_cmd_menu = 'root'
		scenario.BuildCmdMenu()
		
		UpdateScreen()
		
		# do initial enemy spawn
		scenario.SpawnEnemyUnits()
		
		# do initial OOB list
		scenario.RebuildOOBList()
	
	
	# TODO: End new game set-up
	
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
		
		# TEMP: only way to exit for now
		if libtcod.console_is_window_closed(): sys.exit()
		
		# no more PSGs to act this turn: replenish TU, rebuild OOB list and redraw
		#   OOB console
		if scenario.active_psg is None:
			scenario.NextTurn()
			
			# check to see if scenario has ended
			if scenario.winner is not None:
				os.remove('savegame')
				scenario.DisplayEndScreen()
				exit_scenario = True
			UpdateScreen()
			continue
		
		# trigger automatic pre-activation actions
		scenario.active_psg.DoActivationActions()
		
		# active PSG is an AI unit
		if scenario.active_psg != scenario.player_psg:
			scenario.active_psg.ai.ResolveMode()
			scenario.MoveActivePSGInList()
			UpdateScreen()
			continue
		
		# active PSG is player, hand over control
		scenario.BuildCmdMenu()
		UpdateScreen()
		
		# save the game in progress at this point
		SaveGame()
		
		while scenario.active_psg == scenario.player_psg and not exit_scenario:
			
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
				UpdatePSGInfoConsole()
				DrawScreenConsoles()
			
			##### Mouse Commands #####
			#if mouse.rbutton:
				# there is a PSG here
			#	if (mouse.cx, mouse.cy) in scenario.psg_draw_map.keys():
			#		psg = scenario.psg_draw_map[(mouse.cx, mouse.cy)]
			#		UpdatePSGInfoConsole(psg)
			#		UpdateScreen()
			#	else:
			#		libtcod.console_clear(psg_info_con)
			#		UpdateScreen()
			
			#elif mouse.lbutton:
			#	if (mouse.cx, mouse.cy) in scenario.psg_draw_map.keys():
			#		scenario.selected_psg = scenario.psg_draw_map[(mouse.cx, mouse.cy)]
			#		UpdateScreen()
			#	else:
			#		scenario.selected_psg = None
			#		UpdateScreen()
				
			
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
			PlaySound('menu_choice')
			UpdateScreen()
			libtcod.console_flush()
			Wait(100)
			
			# Returning to Root Menu
			if option.option_id == 'return_to_root':
				scenario.active_cmd_menu = 'root'
				scenario.player_active_weapon = None
				scenario.BuildCmdMenu()
				UpdateScreen()
			
			# Root Menu Options
			elif option.option_id == 'orders':
				scenario.active_cmd_menu = 'orders'
				scenario.BuildCmdMenu()
				UpdateScreen()
			
			elif option.option_id == 'movement':
				scenario.active_cmd_menu = 'movement'
				scenario.BuildCmdMenu()
				UpdateScreen()
			
			elif option.option_id == 'shooting':
				scenario.active_cmd_menu = 'shooting'
				scenario.BuildCmdMenu()
				UpdateScreen()
			
			elif option.option_id == 'wait':
				scenario.player_psg.SpendTU(option.tu_cost)
				scenario.MoveActivePSGInList()
			
			# Movement Commands
			elif option.option_id in ['move_fwd', 'move_rev']:
				
				# try to move player PSG forward or reverse
				if scenario.player_psg.MoveForward():
					scenario.hex_map.UpdateMapVPMatrix()
					UpdateScreen()
					scenario.MoveActivePSGInList()
					scenario.BuildCmdMenu()
					UpdateScreen()		
			elif option.option_id == 'hull_ccw':
				if scenario.player_psg.PivotHull(False):
					scenario.hex_map.UpdateMapVPMatrix()
					UpdateOOBConsole()
					scenario.BuildCmdMenu()
					UpdateScreen()
			elif option.option_id == 'hull_cw':
				if scenario.player_psg.PivotHull(True):
					scenario.hex_map.UpdateMapVPMatrix()
					UpdateOOBConsole()
					scenario.BuildCmdMenu()
					UpdateScreen()
			elif option.option_id == 'turret_ccw':
				scenario.player_psg.turret_facing = ConstrainDir(scenario.player_psg.turret_facing - 1)
				UpdateScreen()
			elif option.option_id == 'turret_cw':
				scenario.player_psg.turret_facing = ConstrainDir(scenario.player_psg.turret_facing + 1)
				UpdateScreen()
			
			# Shooting Commands: select a weapon and start target mode
			elif option.option_id[:9] == 'act_weap_':
				# find the weapon to be activated and activate it
				n = int(option.option_id[9])
				scenario.player_active_weapon = scenario.player_psg.weapon_list[n]
				scenario.active_cmd_menu = 'targeting'
				scenario.BuildTargetHexes()
				scenario.BuildTargetList()
				scenario.BuildCmdMenu()
				UpdateMapGUIConsole()
				UpdateScreen()
			
			elif option.option_id == 'next_target':
				scenario.SelectNextTarget()
				scenario.BuildCmdMenu()
				UpdateMapGUIConsole()
				UpdateScreen()
			
			elif option.option_id == 'fire':
				# TODO: where to put TU cost?
				InitAttack(scenario.player_psg, scenario.target_psg)
				scenario.CancelTarget()
				scenario.MoveActivePSGInList()
				scenario.active_cmd_menu = 'shooting'
				scenario.BuildCmdMenu()
				UpdateMapGUIConsole()
				UpdateScreen()
			
			# cancel target mode and return to shooting menu
			elif option.option_id == 'return_to_shooting':
				scenario.CancelTarget()
				scenario.active_cmd_menu = 'shooting'
				scenario.BuildCmdMenu()
				UpdateMapGUIConsole()
				UpdateScreen()
			
			# Orders Commands: select a friendly PSG to order
			elif option.option_id[:11] == 'order_unit_':
				
				# find the unit to order
				n = 0
				for psg in scenario.psg_list:
					if psg == scenario.player_psg: continue
					if psg.owning_player == 0:
						if n == int(option.key_code) - 1:
							scenario.psg_under_orders = psg
							
							# set currently selected hex to psg location
							hx = scenario.psg_under_orders.hx
							hy = scenario.psg_under_orders.hy
							scenario.selected_vp_hex = GetVPHex(hx, hy)
							
							# build list of allowable locations
							scenario.allowed_vp_hexes.append(GetVPHex(scenario.player_psg.hx, scenario.player_psg.hy))
							for (hx, hy) in GetHexesWithin(scenario.player_psg.hx, scenario.player_psg.hy, 2):
								map_hex = GetHexAt(hx, hy)
								if map_hex.water: continue
								if map_hex.IsOccupiedByEnemy(0): continue
								scenario.allowed_vp_hexes.append(GetVPHex(hx, hy))
							
							print 'DEBUG: added ' + str(len(scenario.allowed_vp_hexes)) + ' possible locations'
							
							scenario.active_cmd_menu = 'psg_orders'
							scenario.BuildCmdMenu()
							UpdateMapGUIConsole()
							UpdateScreen()
			
			# issue take up new position order
			elif option.option_id == 'order_to_hex':
				(vp_hx, vp_hy) = scenario.selected_vp_hex
				map_hex = scenario.hex_map.vp_matrix[(vp_hx, vp_hy)]
				scenario.psg_under_orders.ai.guard_hx = map_hex.hx - scenario.psg_under_orders.ai.guard_target.hx
				scenario.psg_under_orders.ai.guard_hy = map_hex.hy - scenario.psg_under_orders.ai.guard_target.hy
				print ('DEBUG: new guard offset set: ' + str(scenario.psg_under_orders.ai.guard_hx) +
					',' + str(scenario.psg_under_orders.ai.guard_hy))
				scenario.psg_under_orders = None
				scenario.EndHexSelection()
				scenario.active_cmd_menu = 'orders'
				scenario.BuildCmdMenu()
				UpdateScreen()
				
			
			# cancel PSG orders
			elif option.option_id == 'cancel_psg_orders':
				scenario.psg_under_orders = None
				scenario.EndHexSelection()
				scenario.active_cmd_menu = 'orders'
				scenario.BuildCmdMenu()
				UpdateScreen()
			
			# hex selection commands
			elif option.option_id[:8] == 'hex_sel_':
				
				direction = option.option_id[8]
				(hx, hy) = scenario.selected_vp_hex
				new_hx = hx
				new_hy = hy
				if direction == 'q':
					new_hx -= 1
				elif direction == 'w':
					new_hy -= 1
				elif direction == 'e':
					new_hx += 1
					new_hy -= 1
				elif direction == 'a':
					new_hx -= 1
					new_hy += 1
				elif direction == 's':
					new_hy += 1
				elif direction == 'd':
					new_hx += 1
				
				if (new_hx, new_hy) in scenario.allowed_vp_hexes:
					scenario.selected_vp_hex = (new_hx, new_hy)
					UpdateMapGUIConsole()
					UpdateScreen()
	
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


# load game sound effects
def LoadSounds():
	SOUND_LIST = ['menu_selection', 'menu_choice']
	for sound_name in SOUND_LIST:
		sound = pygame.mixer.Sound(DATAPATH + sound_name + '.wav')
		SOUNDS[sound_name] = sound

# play a sound
def PlaySound(sound_name):
	# make sure sound is actually part of archive
	if not sound_name in SOUNDS:
		print 'ERROR: Sound file not found: ' + sound_name + '.wav'
		return
	SOUNDS[sound_name].play()



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


# init pygame mixer stuff
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
pygame.mixer.init()

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()

# load sound effects
LoadSounds()

# set up colour control for highlighting command keys
libtcod.console_set_color_control(libtcod.COLCTRL_1, KEY_HIGHLIGHT_COLOR, libtcod.black)

# set up constant hex defintitions for viewport
# list of viewport hexes, with 0,0 in the center and a 6-hex radius around it
VP_HEXES = []
for hx in range(-6, 7):
	if hx <= 0:
		hy_start = 0 - (hx+6)
		hy_end = 6
	else:
		hy_start = -6
		hy_end = 6-hx

	for hy in range(hy_start, hy_end+1):
		VP_HEXES.append((hx, hy))

# sort list of hexes by hex distance from 0,0
range_list = []
for (hx, hy) in VP_HEXES:
	range_list.append(GetHexDistance(hx, hy, 0, 0))
VP_HEXES = [x[0] for x in sorted(zip(VP_HEXES, range_list))]
# delete this list since we don't need it any more
del range_list[:]


# create a dictionary of screen locations within each viewport hex
# used to quickly display info about that map hex
SCREEN_TO_VP_HEX = {}
for (hx, hy) in VP_HEXES:
	(x,y) = PlotHex(hx, hy)
	for x1 in range(x-1, x+2):
		SCREEN_TO_VP_HEX[(x1,y-1)] = (hx, hy)
		SCREEN_TO_VP_HEX[(x1,y+1)] = (hx, hy)
	for x1 in range(x-2, x+3):
		SCREEN_TO_VP_HEX[(x1,y)] = (hx, hy)



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
	libtcod.BKGND_NONE, libtcod.CENTER, 'Copyright 2016' )
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
cmd_menu.AddOption('quit', 'Q', 'Quit', desc='Quit to desktop', exit_option=True)
menus.append(cmd_menu)

cmd_menu = CommandMenu('settings_menu')
cmd_menu.AddOption('toggle_font_size', 'F', 'Toggle Font/Window Size',
	desc='Switch between 8px and 16px font size')
cmd_menu.AddOption('select_msg_speed', 'M', 'Select Message Pause Time',
	desc='Change how long messages are displayed before being cleared')
cmd_menu.AddOption('select_ani_speed', 'A', 'Select Animation Speed',
	desc='Change the display speed of in-game animations')
cmd_menu.AddOption('return_to_main', '0', 'Return to Main Menu', exit_option=True)
menus.append(cmd_menu)

active_menu = menus[0]

global gradient_x

def AnimateScreen():
	
	global gradient_x
	
	# draw gradient
	for x in range(0, 10):
		if x + gradient_x > WINDOW_WIDTH: continue
		for y in range(16, 31):
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
	active_menu.DisplayMe(0, WINDOW_XM-12, 34, 25)
	
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
	PlaySound('menu_choice')
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

