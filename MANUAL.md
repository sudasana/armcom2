# Armoured Commander II
### Game Manual for Alpha 12.0

## 1. General Principles

In *Armoured Commander II*, you play the role of a tank commander in World War II, leading your crew through a campaign in one of the major conflicts of the war.

## 2. Main Menu

![Main menu image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_main_menu.png "Main Menu")
In the **Main Menu**, you can continue a previously saved campaign, start a new campaign, change game options, or quit the game.

To **Continue** a campaign, it must have been saved with a compatible version of the game. If the first two version numbers (separated by single dots) match, it will be compatible. Otherwise you won't be able to resume your campaign.

If you start a **New Campaign**, any current saved campaign will be erased. You can only have one saved campaign at any one time.

**Game Options** can be accessed here and from the in-game menu as well. Changing the **Font Size** will change the total window size. **Sound Effects**, including the main menu theme, can be toggled here. Changing the **Master Volume** will change the volume of the theme music and all sound effects. **Message Pause** changes the length of time that pop-up messages are displayed before disappearing. Several **Keyboard** layouts are supported, and you can set your own keyboard mapping by editing the "custom" dictionary in the keyboard_mapping.json file in the data folder, and selecting it here.

## 3. Campaign Selection

![Campaign selection image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_campaign_selection.png "Campaign Selection")

Several campaigns are included with the game. Each one takes place over a fixed period of time between 1939 and 1945, placing you in the role of a tank and battlegroup commander. **Player Force** means the national military force that you will be a part of. **Enemy Forces** lists the expected national forces that will be your opponents in this campaign. Some campaigns are longer than others; the actual days within the campaign calendar on which you will be called up for action will be determined randomly.

From this screen you can select a campaign to start, or have the game select one randomly.

You can also set your **Campaign Options** in this menu. "Permadeath" means that your Commander represents you, and if he is killed or seriously injured, your campaign ends immediately. "Fate Points" are replenished at the start of each Campaign Day, and eash one silently saves you from an incoming attack that would have otherwise destroyed your tank.

## 4. Tank and Crew Selection

![Tank selection image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_tank_selection.png "Tank Selection")

A selection of tank models are available to you at the start of the campaign. During **Refit Weeks**, and if you have to abandon your tank, you will have an opportunity to select a new model. Available models depend on the current calendar date; some models will only become available to you later on in a campaign. Pay close attention to the stats of your chosen tank, since you may be riding in it for some time.

### 4.1 Tank Stats

Virtually everything you need to know about a unit is included in its unit information display. Your tank's stats are especially important, so here is an example of how to read them:

![Tank stats image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_tank_stats.png "Tank Stats")

* M4 Sherman: This is the unit identifier, unique to each model of tank
* Medium Tank: This is the unit's class, indicating generally what type of unit it is
* Portrait: A rough approximation of this unit as viewed from the side
* 75mm, etc. (dark red background): A list of weapon systems on this unit, starting with its main armament
  * Guns may be short (S) or long (L) barreled
  * Co-ax weapons are mounted on the turret alongside (or as) the main gun
  * Anti-Aircraft (AA) machine guns (MG) can fire in any direction, but must often be fired from outside of the tank
  * Bow MGs are fixed to the front of the hull
* Armoured or Unarmoured vehicles have their armour values listed here
  * The T line refers to turret armour, but if there is no rotatable turret it will appear as U (Upper Structure) instead; if the turret has a fast traverse, this will be noted by (fast)
  * H refers to hull armour
  * The two armour values x/x refer to front and side armour respectively for that area
  * Rear armour values for any location are one level lower than its side level
* The movement class of the unit is shown in green in the lower right
  * If a vehicle has light ground pressure this will be displayed in a light shade of green, if heaver ground pressure, a darker shade. Ground pressure affects the change of bogging down.
  * If a vehicle has an especially powerful engine, a plus sign will appear next to the movement class
* Any special vehicle features will appear below the movement class:
  * HVSS stands for Horizontal Volute Spring Suspension; vehicles with this upgrade are slightly faster and less likely to bog
  * Recce is short for reconnaissance, and means that the vehicle is less likely to be ambushed at the start of a scenario
  * ATV means that this is an All-terrain Vehicle (no effect yet)
* The size class of the unit appears below that. Larger targets are easiser to spot and hit
* Finally, the normal number of crew for this unit

A full crew, with yourself as the commander, will be automatically generated for your chosen tank.

### 4.2 Crew

![Crew image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_crewman_report.png "Crew")

Each crewman in your tank has their own set of stats, skills, and experience points. Names are randomly generated, but you can assign a nickname to each crewman.

**Crew Stats**

Each crewman has four stat values, which are randomly generated at the start of the game but can be improved by spending **Advance Points** later on.

* *Perception* is used during attempts to spot enemy units on the scenario layer
* *Morale* represents the crewman's ability to resist psychological stress and harm (not yet used as of Alpha 10)
* *Grit* is used to resist wounds and negative status effects such as Stunned
* *Knowledge* applies a small modifier to all skill bonuses

**Crew Experience**

Every time you earn a Victory Point in the game, any crewman who is conscious at the time also receives an experience point. At the end of each combat day they may go up one or more levels depending on their exp. Each time they go up a level, they are awarded with an Advance Point which can be spent increasing the crewman's stats or adding a skill.

**Crew Skills**

19 skills are available (as of Alpha 10), but not all are available to crewmen in all tank positions. Some of them have another skill as a prerequisite. All apply some kind of bonus as described in the skill description. (Full skill tree and description list to follow)


## 5. Game Menu

![Game menu image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_game_menu.png "Campaign Menu")

You can access the in-game menu from any layer of the game and at any time. From here you can save your campaign to continue later, as well as change game options.

## 6. The Campaign Calendar Layer

![Campaign calendar image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_campaign_calendar.png "Campaign Menu")

In the **Campaign Calendar** layer you can view information about the upcoming or a just-completed combat day. Pressing **2** will bring up the Crew and Tank tab of the command menu. Here you can review each of your crew, see your tank's stats, and assign crew and tank nicknames if you have not done so already. Most layers display the main list of commands in this area of the screen.

Press **1** to return to the Proceed menu tab, and press **Enter** to start your combat day. If you survive your combat day, you will return to this layer from which you can proceed to the next combat day.

## 7. The Campaign Day Layer

![Campaign day image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_campaign_day_map.png "Campaign Day Layer")

In this layer you lead your tank and battlegroup across a terrain map of hex zones. Your own tank is displayed in the upper left of the screen, and several tabs of commands appear in the lower left. Current weather and ground conditions are displayed in the upper right, campaign and day mission information on the right, and hovering the mouse cursor over any map zone will display information about it in the lower right corner of the screen.

The campaign day map is made up of 41 hex zones, each of which are randomly generated as one of six different terrain types. The terrain type of a hex zone influences the time required to travel into it, as well as the terrain for units on the scenario layer if a battle encounter occurs there.

Dark brown lines joining hex zones are roads; travel along roads is usually faster than cross-country. Dark blue lines along the edges of hex zones are rivers; these can only br crossed at a bridge or ford, indicated by a dark brown cell with three horizontal lines.

Objectives are indicated by a ring of light blue dots; capturing these hexes is worth extra VP.

If you reach the top hex row (or the bottom one in Fighting Withdrawl mission), a new hex map will be generated.

Five menu tabs are available in the command menu:
* Supply
  * Here you can view the stats of your tank's main gun, and manage the contents of the Ready Rack. From here you can also **Request Resupply** which, if granted, allows you to replenish main gun ammo, will replace dead or seriously injured crewmen, and will also bring your tank squadron up to full strength.
* Crew
  * Displays a list of current crewmen in your tank. From here you can open the crew menu for any of them, and open/close their hatch if they have one.
* Travel
  * In this menu you can select a direction from your current location, and either request reconnaissance information about an adjacent enemy-held hex, or travel to an adjacent hex. When moving, you can toggle advancing fire and air and artillery support requests on and off. Advancing fire uses up HE ammo but if a battle encounter is triggered, it has the chance of pinning enemy units before combat begins. You can also Wait in place, but there's a possibility that enemy forces may attack your hex.
* Group
  * Lists the current members of your tank squadron.

The campaign day ends when you abandon your tank, your character is killed or seriously wounded, or you reach sunset as indicated by the background of the time display in the top centre of the screen.

### 7.1 Strategy on the Campaign Day Layer

* Always recon enemy-held zones so that you know what you're getting into
* Pay close attention to the time required to travel to a new zone, which varies depending on terrain, weather, and presence of a road connection
* Rivers can only be crossed by the player at bridges, so plan your route ahead of time
* Use advancing fire and air/artillery support, especially when moving into heavy resistance
* If you are cut off from the friendly map edge, you will not be able to call for resupply

## 8. The Scenario Layer

![Scenario image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_scenario.png "Scenario Layer")

Once you encounter enemy resistance on the Campaign Day map, or if you wait in place and are attacked, play shifts to the Scenario layer where battles take place.

On the right of the scenario interface is the Scenario Map, made up of 36 hexes arranged in 3 rings surrounding a central hex. The map represents, in an abstract way, all terrain in a 1,440 meter radius around the player. Your tank, represented in traditional roguelike fashion by the @ character, is located in the centre of the map. All other units on the map are represented from your point of view, so if you pivot your tank counter-clockwise, units will appear to rotate clockwise around the map. Likewise, if you move into a new hex, all other units will shift around you. Hovering your mouse cursor over any hex will display its info at the bottom of the map; scrolling with the mouse wheel will shift the order of any unit stacks in the hex.

Above and to the left of the scenario map is the contextual console, which displays different information depending on the current phase. Above and to the right is the Environmental Conditions console, which displays information about current weather conditions.

Play on the Scenario Layer proceeds though a series of Phases, each one of which either allows the player to perform certain actions, or allows allied and enemy AI units to act. Each set of phases takes 2 minutes of in-game time to resolve.

### 8.1 Scenario Phases

* Command Phase

In this phase you can open and close the hatch for each crewman that has one, and you can assign one command to each of your tank crew that is neither unconscious nor dead. Each command will allow the crewman to do different types of tasks in the remainder of the turn. The sight radius of your crewman is highlighted on the scenario map in blue; different hatch statuses and commands will result in different areas of the map where your crewman can spot in the following phase. Descriptions for each command are displayed in the Contextual Console.

Note that some commands will only become available when certain conditions are met; for example, you can only abandon your tank if it is immobilized or if you have 1+ crewmen who have been seriously injured.

* Spotting Phase

Dureing this phase no input is required from the player; any crewman who can do so will automatically try to spot any hidden enemy unit in his line of sight. If an enemy unit is spotted, its identity will be displayed in a pop-up message.

* Crew Action Phase

Certain crew commands require additional input or will result in automatic actions during this phase. For example, a Gunner can manage his Ready Rack, moving shells into or out of it, or the Commander might throw a smoke grenade, providing some concealment for the player tank.

* Movement Phase

If the Driver has been given the "Drive" command, then the player can move the tank in this phase.

* Shooting Phase
* Close Combat Phase
* Allied Action Phase
* Enemy Action Phase

