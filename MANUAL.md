# Armoured Commander II
### Game Manual for Alpha 10.0

## 1. General Principles

In *Armoured Commander II*, you play the role of a tank commander in World War II, leading your crew through a campaign in one of the major conflicts of the war.

## 2. Main Menu

![Main menu image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_main_menu.png "Main Menu")
In the **Main Menu**, you can continue a previously saved campaign, start a new campaign, change game options, or quit the game.

To **Continue** a campaign, it must have been saved with a compatible version of the game. If the first two version numbers (separated by single dots) match, it will be compatible. Otherwise you won't be able to resume your campaign.

If you start a **New Campaign**, any current saved campaign will be erased. You can only have one saved campaign at any one time.

**Game Options** can be accessed here and from the in-game menu as well. Changing the **Font Size** will change the total window size. **Sound Effects**, including the main menu theme, can be toggled here. **Message Pause** changes the length of time that pop-up messages are displayed before disappearing. Several **Keyboard** layouts are supported, and you can set your own keyboard mapping by editing the "custom" dictionary in the keyboard_mapping.json file in the data folder, and selecting it here.

## 3. Campaign Selection

![Campaign selection image](https://raw.githubusercontent.com/sudasana/armcom2/master/manual_images/armcom2_campaign_selection.png "Campaign Selection")

Several campaigns are included with the game. Each one takes place over a fixed period of time between 1939 and 1945, placing you in the role of a tank and battlegroup commander. **Player Force** means the national military force that you will be a part of. **Enemy Forces** lists the expected national forces that will be your opponents in this campaign. Some campaigns are longer than others; the actual days within the campaign calendar on which you will be called up for action will be determined randomly.

From this screen you can select a campaign to start, or have the game select one randomly.

## 4. Tank Selection

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
  * Co-ax weapons are mounted on the turret as or alongside the main gun
  * Anti-Aircraft (AA) MG can fire in any direction, but must often be fired from outside of the tank
  * Bow MGs are fixed to the front of the hull
* Armoured or Unarmoured vehicles have their armour values listed here
  * The T line refers to turret armour, but if there is no rotatable turret it will appear as U (Upper Structure) instead. The if the turret has a fast traverse, this will be noted by (fast)
  * H refers to hull armour
  * The two armour values x/x refer to front and side armour respectively for that area
  * Rear armour values for any location are one level lower than its side level
* The movement class of the unit is shown in green in the lower right.
* The size class of the unit appears below that. Larger targets are easiser to spot and hit.
* Finally, the normal number of crew for this unit

A full crew, with yourself as the commander, will be automatically generated for your chosen tank.

## 5. The Campaign Calendar Layer

## 6. The Campaign Day Layer

## 7. The Scenario Layer

