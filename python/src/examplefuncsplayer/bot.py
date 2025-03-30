import random
from enum import Enum
#Hello world guys lol

from battlecode25.stubs import *

# This is NOT an example bot written by the developers!
# DON'T use this to help write your own code.
# Please only run it against your bot to see how well you can do!

class MessageType(Enum):
    SAVE_CHIPS = 0

# Globals
turn_count = 0
directions = [
    Direction.NORTH,
    Direction.NORTHEAST,
    Direction.EAST,
    Direction.SOUTHEAST,
    Direction.SOUTH,
    Direction.SOUTHWEST,
    Direction.WEST,
    Direction.NORTHWEST,
]
direction_indices = {
    Direction.NORTH : 0,
    Direction.NORTHEAST : 1,
    Direction.EAST : 2,
    Direction.SOUTHEAST : 3,
    Direction.SOUTH : 4,
    Direction.SOUTHWEST : 5,
    Direction.WEST : 6,
    Direction.NORTHWEST : 7,
}

# Pathfinding
prev_dest = MapLocation(100000, 100000)
line = set()
obstacle_start_dist = 0
tracing_dir = None
tracing = False

def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    return 0

def get_direction_to(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    return (sign(dx), sign(dy))

def create_line(a, b):
    locations = set()
    x, y = a.x, a.y
    dx = b.x - a.x
    dy = b.y - a.y
    sx = int(sign(dx))
    sy = int(sign(dy))
    dx = abs(dx)
    dy = abs(dy)
    d = d = dx if dx > dy else dy
    r = d // 2

    if dx > dy:
        for i in range(d):
            locations.add(MapLocation(x, y))
            x += sx
            r += dy
            if r >= dx:
                locations.add(MapLocation(x, y))
                y += sy
                r -= dx
    else:
        for i in range(d):
            locations.add(MapLocation(x, y))
            y += sy
            r += dx
            if r >= dy:
                locations.add(MapLocation(x, y))
                x += sx
                r -= dy

    locations.add(MapLocation(x, y))
    return locations

def bug2(target):
    global prev_dest, line, tracing, obstacle_start_dist, tracing_dir

    if get_location() == target:
        return

    if target.compare_to(prev_dest) != 0:
        prev_dest = target
        line = create_line(get_location(), target)

    if not tracing:
        dir = Direction(get_direction_to(get_location(), target))

        if can_move(dir):
            move(dir)
        else:
            tracing = True
            obstacle_start_dist = get_location().distance_squared_to(target)
            tracing_dir = dir
    else:
        if (get_location() in line 
                and get_location().distance_squared_to(target) < obstacle_start_dist):
            tracing = False
            return

        for i in range(9):
            if can_move(tracing_dir):
                move(tracing_dir)
                tracing_dir = tracing_dir.rotate_right()
                tracing_dir = tracing_dir.rotate_right()
                break
            else:
                tracing_dir = tracing_dir.rotate_left()

# Should add up to 100
buildable_towers = [UnitType.LEVEL_ONE_MONEY_TOWER, UnitType.LEVEL_ONE_PAINT_TOWER, UnitType.LEVEL_ONE_DEFENSE_TOWER]
bot_chance = {UnitType.SOLDIER : 40, UnitType.MOPPER : 25, UnitType.SPLASHER : 35}
tower_chance = {UnitType.LEVEL_ONE_MONEY_TOWER : 65, UnitType.LEVEL_ONE_PAINT_TOWER : 25, UnitType.LEVEL_ONE_DEFENSE_TOWER : 10}
bot_name = {UnitType.SOLDIER : "SOLDIER", UnitType.MOPPER : "MOPPER", UnitType.SPLASHER : "SPLASHER"}
direction_distribution = {
    Direction.NORTH : None,
    Direction.NORTHEAST: None,
    Direction.EAST: None,
    Direction.SOUTHEAST: None,
    Direction.SOUTH: None,
    Direction.SOUTHWEST: None,
    Direction.WEST: None,
    Direction.NORTHWEST: None,
}

CORRECT = 23
SEMICORRECT = 17
NEUTRAL = 13
SEMIWRONG = 7
WRONG = 3

LEFT = {
    Direction.NORTH : NEUTRAL,
    Direction.NORTHEAST: SEMIWRONG,
    Direction.EAST: WRONG,
    Direction.SOUTHEAST: SEMIWRONG,
    Direction.SOUTH: NEUTRAL,
    Direction.SOUTHWEST: SEMICORRECT,
    Direction.WEST: CORRECT,
    Direction.NORTHWEST: SEMICORRECT,
}

RIGHT = {
    Direction.NORTH : NEUTRAL,
    Direction.NORTHEAST: SEMICORRECT,
    Direction.EAST: CORRECT,
    Direction.SOUTHEAST: SEMICORRECT,
    Direction.SOUTH: NEUTRAL,
    Direction.SOUTHWEST: SEMIWRONG,
    Direction.WEST: WRONG,
    Direction.NORTHWEST: SEMIWRONG,
}

DOWN = {
    Direction.NORTH : WRONG,
    Direction.NORTHEAST: SEMIWRONG,
    Direction.EAST: NEUTRAL,
    Direction.SOUTHEAST: SEMICORRECT,
    Direction.SOUTH: CORRECT,
    Direction.SOUTHWEST: SEMICORRECT,
    Direction.WEST: NEUTRAL,
    Direction.NORTHWEST: SEMIWRONG,
}

UP = {
    Direction.NORTH : CORRECT,
    Direction.NORTHEAST: SEMICORRECT,
    Direction.EAST: NEUTRAL,
    Direction.SOUTHEAST: SEMIWRONG,
    Direction.SOUTH: WRONG,
    Direction.SOUTHWEST: SEMIWRONG,
    Direction.WEST: NEUTRAL,
    Direction.NORTHWEST: SEMICORRECT,
}

UNIFORM = {
    Direction.NORTH : NEUTRAL,
    Direction.NORTHEAST: NEUTRAL+1,
    Direction.EAST: NEUTRAL,
    Direction.SOUTHEAST: NEUTRAL+1,
    Direction.SOUTH: NEUTRAL,
    Direction.SOUTHWEST: NEUTRAL+1,
    Direction.WEST: NEUTRAL,
    Direction.NORTHWEST: NEUTRAL+1,
}

def update_bot_chance(soldier, mopper, splasher):
    global bot_chance
    bot_chance[UnitType.SOLDIER] = soldier
    bot_chance[UnitType.MOPPER] = mopper
    bot_chance[UnitType.SPLASHER] = splasher

def update_tower_chance(money, paint, defense):
    global tower_chance
    tower_chance[UnitType.LEVEL_ONE_MONEY_TOWER] = money
    tower_chance[UnitType.LEVEL_ONE_PAINT_TOWER] = paint
    tower_chance[UnitType.LEVEL_ONE_DEFENSE_TOWER] = defense

factor = 2
def update_direction_distribution():
    global direction_distribution
    cur_loc = get_location()
    left = cur_loc.x
    right = get_map_width() - left - 1
    down = cur_loc.y
    up = get_map_height() - down - 1
    left = left ** factor
    right = right ** factor
    up = up ** factor
    down = down ** factor
    total = left+right+down+up
    left = int(left/total*50)
    right = int(right/total*50)
    down = int(down/total*50)
    up = int(up/total*50)
    total = left+right+down+up
    leftover = 50-total
    if left > right: left += leftover
    else: right += leftover
    ul = (up + left)//2
    ur = (up + right)//2
    dl = (down + left)//2
    dr = (down + right)//2
    total = ul + ur + dl + dr
    leftover = 50 - total
    if left > right:
        if up > down:
            ul += leftover
        else:
            dl += leftover
    else:
        if up > down:
            ur += leftover
        else:
            dr += leftover
    direction_distribution[Direction.NORTH] = up
    direction_distribution[Direction.NORTHEAST] = ur
    direction_distribution[Direction.EAST] = right
    direction_distribution[Direction.SOUTHEAST] = dr
    direction_distribution[Direction.SOUTH] = down
    direction_distribution[Direction.SOUTHWEST] = dl
    direction_distribution[Direction.WEST] = left
    direction_distribution[Direction.NORTHWEST] = ul

def update_direction_distribution_2():
    global direction_distribution
    cur_loc = get_location()
    left = cur_loc.x
    right = get_map_width() - left - 1
    down = cur_loc.y
    up = get_map_height() - down - 1
    left = left ** factor
    right = right ** factor
    up = up ** factor
    down = down ** factor
    if left <= 5: left = 0
    if right <= 5: right = 0
    if down <= 5: down = 0
    if up <= 5: up = 0
    total = left + right + up + down
    temp = random.randint(1, total)
    if temp <= left:
        direction_distribution = LEFT
    elif temp <= left + right:
        direction_distribution = RIGHT
    elif temp <= left + right + down:
        direction_distribution = DOWN
    else:
        direction_distribution = UP

def get_random_dir():
    n = random.randint(1, 100)
    for (direction, prob) in direction_distribution.items():
        if n <= prob: return direction
        n -= prob

def get_random_unit(probabilities):
    n = random.randint(1, 100)
    for (unit, prob) in probabilities.items():
        if n <= prob: return unit
        n -= prob

# Determine build delays between each bot spawned by a tower
buildDelay = 15 # Tune
buildDeviation = 3

# When we're trying to build, how long should we save
save_turns = 45 # Tune

# How many turns after does a messenger repeats its tasks
messenger_work_distribution = 25

# How many turns after does a soldier senses towers
sense_tower_delay = 10

# Threshold for returning to ruin (splashers)
return_to_paint = {UnitType.SOLDIER : 0, UnitType.MOPPER : 0, UnitType.SPLASHER : 25}
back_to_aggresion = {UnitType.SOLDIER : 75, UnitType.MOPPER : 50, UnitType.SPLASHER : 85}
# Paint per transfer
paint_per_transfer = 50
# Min splashable squares to attack
splash_threshold = 2

# Privates
buildCooldown = 0
is_messenger = False # We designate half of moppers to be messangers
known_towers = []
known_paint_towers = []
should_save = False
savingTurns = 0
updated = 0
early_game = 200
mid_game = 800
tower_upgrade_minimum = 15000
closest_paint_tower = None
is_refilling = False
paintingSRP = False
tower_upgrade_threshold = 1
next_spawn = UnitType.SOLDIER
explore = 0
target_corner = None
explore_chance = 15
cur_tile = None
is_early_game = False
is_mid_game = False
is_late_game = False
nearby_tiles = []
SRP = get_resource_pattern()

def can_repeat_cooldowned_action(time_delay):
    return (get_id() % time_delay == turn_count % time_delay)

def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """
    global turn_count
    global is_messenger
    global updated
    global direction_distribution
    global buildDelay
    global explore, target_corner, explore_chance
    global is_early_game, is_mid_game, is_late_game
    # HOW DID NO ONE REALIZE TURN COUNT IS NOT COUNTING FROM THE START
    turn_count = get_round_num()

    thisisavariableforchoosingmethodofrandomwalking = random.randint(1, 100)
    thisisavariableforchoosingexploringdirection = random.randint(1, 100)
    if direction_distribution[Direction.NORTH] == None:
        if thisisavariableforchoosingmethodofrandomwalking <= 35:
            update_direction_distribution_2()
        elif thisisavariableforchoosingmethodofrandomwalking <= 95:
            update_direction_distribution()
        else:
            direction_distribution = UNIFORM

        # if thisisavariableforchoosingexploringdirection <= explore_chance:
        #     target_corner = MapLocation(0, 0)
        # elif thisisavariableforchoosingexploringdirection <= explore_chance*2:
        #     target_corner = MapLocation(get_map_width()-1, 0)
        # elif thisisavariableforchoosingexploringdirection <= explore_chance*3:
        #     target_corner = MapLocation(0, get_map_height()-1)
        # elif thisisavariableforchoosingexploringdirection <= explore_chance*4:
        #     target_corner = MapLocation(get_map_width()-1, get_map_height()-1)
        # if thisisavariableforchoosingexploringdirection <= explore_chance*4:
        #     explore = random.randint(0, 100) # needs tuning

    # Prioritize chips in early game
    # Seems like chips are a bit too popular
    if turn_count >= 0 and updated == 0:
        is_early_game = True
        is_mid_game = False
        is_late_game = False
        update_tower_chance(70, 30, 0)
        update_bot_chance(90, 5, 5)
        explore_chance = 20
        updated = 1
    if turn_count >= early_game and updated == 1:
        is_early_game = False
        is_mid_game = True
        is_late_game = False
        update_tower_chance(55, 40, 5)
        update_bot_chance(50, 20, 30)
        explore_chance = 10
        updated = 2
    if turn_count >= mid_game and updated == 2:
        is_early_game = False
        is_mid_game = False
        is_late_game = True
        update_tower_chance(40, 40, 20)
        update_bot_chance(40, 25, 35)
        explore_chance = 0
        updated = 3

    if not get_type().is_tower_type():
        if get_paint() == 0:
            disintegrate() # WASTING TOO MUCH RESOURCES

    if get_type() == UnitType.SOLDIER:
        run_soldier()
    elif get_type() == UnitType.MOPPER:
        if get_id() % 2 == 0: is_messenger = True
        run_mopper()
    elif get_type() == UnitType.SPLASHER:
        run_splasher()
    elif get_type().is_tower_type():
        update_direction_distribution()
        run_tower()
    else:
        pass  # Other robot types?

def update_phases():
    global early_game
    global mid_game
    game_area = get_map_height() * get_map_width()
    if game_area >= 400 and game_area < 1225: 
        early_game = 45
        mid_game = 450
    elif game_area < 2115: 
        early_game = 90
        mid_game = 700
    else:
        early_game = 140
        mid_game = 950

def run_tower():
    global buildCooldown
    global savingTurns
    global should_save
    global next_spawn
    # Pick a direction to build in.
    dir = get_random_dir()
    loc = get_location()
    next_loc = get_location().add(dir)
    enemy_robots = sense_nearby_robots(center=get_location(),team=get_team().opponent())

    # Ability for towers to attack
    if(is_action_ready() and len(enemy_robots) != 0):
        # Pick a random target to attack
        for random_enemy in enemy_robots:
            loc2 = random_enemy.get_location()
            if can_attack(random_enemy.get_location()):
                attack(loc2)
                break

    # Pick a random robot type to build.
    # Should hold off on building since we're gonna end up with all moppers!
    if savingTurns <= 0:
        should_save = False
        if buildCooldown <= 0: 
            robot_type = next_spawn
            if can_build_robot(robot_type, next_loc):
                build_robot(robot_type, next_loc)
                next_spawn = get_random_unit(bot_chance)
                buildCooldown = buildDelay + random.randint(-buildDeviation, buildDeviation)
                log("BUILT A " + bot_name[robot_type])

    if buildCooldown > 0: buildCooldown -= 1
    if savingTurns > 0: 
        savingTurns -= 1
        log("Saving for " + str(savingTurns) + " more turns")
    

    # Read incoming messages
    messages = read_messages()
    for m in messages:
        log(f"Tower received message: '#{m.get_sender_id()}: {m.get_bytes()}'")

        # If we are not currently saving and we receive the save chips message, start saving
        if not should_save and m.get_bytes() == 0:
            savingTurns = save_turns
            should_save = True


    # TODO: can we attack other bots?

def run_soldier():
    global explore, paintingSRP
    global nearby_tiles
    loc = get_location()
    # Try exploring?
    # if explore > 0 and (not paintingSRP):
    #     bug2(target_corner)
    #     if get_location().distance_squared_to(target_corner) <= 30:
    #         explore = 1
    #     explore -= 1
    # 
    # if explore == 0:
    #     update_direction_distribution()
    #     explore -= 1

    # Sense information about all visible nearby tiles.
    nearby_tiles = sense_nearby_map_infos(center=loc)

    cur_ruin = None
    dir = None
    cur_dist = 999999
    cur_dir = None
    cur_dist2 = 999999
    dir_paint_count = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
    for tile in nearby_tiles:
        tile_loc = tile.get_map_location()
        if tile.has_ruin():
            ruin = sense_robot_at_location(tile_loc)
            if ruin != None and ruin.get_team() != get_team(): # If enemy tower, attack
                if can_attack(tile_loc):
                    attack(tile_loc)
                dir = loc.direction_to(tile_loc)
                if not can_move(dir): continue
                dst = loc.distance_squared_to(tile_loc)
                idx = direction_indices[dir]
                dir_paint_count[idx] = dir_paint_count[idx] + 100
            elif ruin == None: # If not enemy tower, try to complete
                check_dist = tile_loc.distance_squared_to(loc)
                if check_dist < cur_dist:
                    cur_dist = check_dist
                    cur_ruin = tile
        elif not tile.is_wall() and tile.get_paint() == PaintType.EMPTY:
            dir = loc.direction_to(tile_loc)
            if not can_move(dir): continue
            dst = loc.distance_squared_to(tile_loc)
            idx = direction_indices[dir]
            dir_paint_count[idx] = dir_paint_count[idx] + 1/dst/dst/dst/dst
            dst = loc.distance_squared_to(tile_loc)
            if can_move(dir) and dst < cur_dist2:
                cur_dist2 = dst
                cur_dir = dir

    if paintingSRP:
        paint_nearby_marks()
        if can_complete_resource_pattern(loc):
            complete_resource_pattern(loc)
            log(f"Built a SRP at {loc}")
            paintingSRP = False
        return
    
    if is_mid_game or (is_late_game and random.randint(1, 100) <= 5):
        # Checks in a square if all squares are empty
        paintingSRP = can_SRP_here()
        if paintingSRP:
            if (can_mark_resource_pattern(loc)):
                mark_resource_pattern(loc)
                return
            else:
                paintingSRP = False

    if cur_ruin != None:
        for tile2 in nearby_tiles:
            if tile2.get_paint().is_enemy() and cur_ruin.get_map_location().distance_squared_to(tile2.get_map_location()) <= 8: 
                cur_ruin = None
                break
        if cur_ruin != None:
            # Should circle around tower to be able to paint all tiles
            target_loc = cur_ruin.get_map_location()
            # Complete the ruin if we can.
            for Tower_type in buildable_towers:
                if Tower_type.is_tower_type() and can_complete_tower_pattern(Tower_type, target_loc):
                    complete_tower_pattern(Tower_type, target_loc)
                    # Maybe try to remove mark
                    set_timeline_marker("Tower built", 0, 255, 0)
                    log("Built a tower at " + str(target_loc) + "!")
                    cur_ruin = None
            if cur_ruin != None:
                dir = loc.direction_to(target_loc)
                if can_move(dir):
                    move(dir)
                else:
                    # Circle to be able to color every tile
                    if dir == Direction.SOUTH: dir = Direction.EAST
                    elif dir == Direction.EAST: dir = Direction.NORTH
                    elif dir == Direction.NORTH: dir = Direction.WEST
                    elif dir == Direction.WEST: dir = Direction.SOUTH
                    elif dir == Direction.SOUTHEAST: dir = Direction.EAST
                    elif dir == Direction.NORTHEAST: dir = Direction.NORTH
                    elif dir == Direction.NORTHWEST: dir = Direction.WEST
                    elif dir == Direction.SOUTHWEST: dir = Direction.SOUTH
                    if can_move(dir):
                        move(dir)

                tower_type = get_random_unit(tower_chance)
                # Mark the pattern we need to draw to build a tower here if we haven't already.
                target_loc = cur_ruin.get_map_location()
                should_mark = target_loc.subtract(dir)
                if can_sense_location(should_mark):
                    if sense_map_info(should_mark).get_mark() == PaintType.EMPTY and can_mark_tower_pattern(tower_type, target_loc):
                        mark_tower_pattern(tower_type, target_loc)
                        log("Trying to build a tower at " + str(target_loc))

                # Fill in any spots in the pattern with the appropriate paint.
                paint_nearby_marks()


    # Fill in any spots in the pattern with the appropriate paint.
    paint_nearby_marks()

    # Upgrade towers
    if can_repeat_cooldowned_action(sense_tower_delay):
        try_to_upgrade_towers()

    # Make sure we go to empty square
    optimal_dir = -1
    optimal = 0
    for (test_dir, paint_count) in dir_paint_count.items():
        if paint_count > optimal:
            optimal = paint_count
            optimal_dir = test_dir

    if optimal_dir != -1:
        cur_dir = directions[optimal_dir]
        if can_move(cur_dir): move(cur_dir)

    dir = get_random_dir()
    if can_move(dir):
        move(dir)

    loc = get_location()

    # Try to paint beneath us as we walk to avoid paint penalties.
    # Avoiding wasting paint by re-painting our own tiles.
    current_tile = sense_map_info(loc)
    if is_action_ready() and not current_tile.get_paint().is_ally() and can_attack(loc):
        attack(loc)

def run_mopper():
    loc = get_location()
    if is_messenger:
        set_indicator_dot(loc, 255, 0, 0)

    if should_save and len(known_towers) > 0:
        # Move to first known tower if we are saving
        dir = loc.direction_to(known_towers[0])
        set_indicator_string(f"Returning to {known_towers[0]}")
        if can_move(dir):
            move(dir)

    # Move and attack randomly.
    # dir = directions[random.randint(0, len(directions) - 1)]
    dir = get_random_dir()
    enemy_robots = sense_nearby_robots(center=loc,radius_squared=2, team=get_team().opponent())
    nearby_tiles = sense_nearby_map_infos(center=loc,radius_squared=2)

    if is_action_ready():
        for tile in nearby_tiles:
            if tile.get_paint() == PaintType.ENEMY_PRIMARY or tile.get_paint() == PaintType.ENEMY_SECONDARY:
                mop_dir = loc.direction_to(tile.get_map_location())
                mop_loc = loc.add(mop_dir)
                if can_attack(mop_loc): 
                    attack(mop_loc)
                    break

        # Only attacks when sees enemy
        for enemy in enemy_robots:
            target_loc = enemy.get_location()
            swingDir = loc.direction_to(target_loc)
            if can_mop_swing(swingDir):
                mop_swing(swingDir)
                log("Mop Swing! Booyah!")
                break

        # Finds other allies to transfer paint
        ally_robots = sense_nearby_robots(center=get_location(),radius_squared=2,team=get_team())
        for ally in ally_robots:
            ally_loc = ally.get_location()
            if can_transfer_paint(ally_loc, 20): transfer_paint(ally_loc, 20)

    if can_move(dir):
        move(dir)


    will_do_messenger = (get_id() % messenger_work_distribution == turn_count % messenger_work_distribution) # Split the work over many turns
    if will_do_messenger and is_messenger:
        check_nearby_ruins()
        update_friendly_towers()

    if can_repeat_cooldowned_action(sense_tower_delay):
        try_to_upgrade_towers()

    # We can also move our code into different methods or classes to better organize it!
    # update_enemy_robots()

#TODO (LITERALLY THE BIGGEST TODO YET)
def run_splasher():
    global is_refilling
    # dir = directions[random.randint(0, len(directions) - 1)]
    # Prioritize where without ally paint
    # Splashers have max paint of 300
    paint_percentage = get_paint() / 3
    if len(known_paint_towers) == 0: run_aggresive_splasher()
    else:
        if not is_refilling and paint_percentage > return_to_paint[UnitType.SPLASHER]:
            run_aggresive_splasher()
        else:
            try_refill_paint(paint_percentage, UnitType.SPLASHER)

def run_aggresive_splasher():
    global known_paint_towers
    nearby_tiles = sense_nearby_map_infos(center=get_location())
    loc = get_location()
    # Get all tiles we're gonna paint over to avoid painting on marked tiles 
    # Total splashed tiles = 13. We're gonna splash if splash_threshold+ tiles are splashable
    if is_action_ready():
        if can_attack(loc):
            splashables = 0
            for tile in nearby_tiles:
                dst = loc.distance_squared_to(tile.get_map_location())
                if dst > 4: continue
                if dst > 2: # Can't override
                    if (not tile.has_ruin()) and (not tile.is_wall()) and (tile.get_paint() == PaintType.EMPTY): splashables += 1
                else:
                    if (not tile.has_ruin()) and (not tile.is_wall()) and (not tile.get_paint().is_ally()): splashables += 1
            
            if splashables >= splash_threshold:
                attack(loc, False)

    # Prioritize moving to empty squares
    dir_paint_count = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
    # Moppers should prioritize: cnt paint -> cnt enemy -> cnt ally. Each square has radius squared of 9
    for tile in nearby_tiles:
        tile_loc = tile.get_map_location()
        if tile.has_ruin():
            tower = sense_robot_at_location(tile_loc)
            if (tower != None) and tower.get_team() == get_team(): # Is ally tower
                if is_paint_tower(tower.get_type()): # Is paint tower
                    if not (tile_loc in known_paint_towers):
                        known_paint_towers.append(tile_loc)
        else:
            dir = loc.direction_to(tile_loc)
            if not can_move(dir): continue
            idx = direction_indices[dir]
            if not tile.is_wall() and not tile.get_paint().is_ally(): 
                dir_paint_count[idx] = dir_paint_count[idx] + 25
    nearby_robots = sense_nearby_robots(center=loc)
    for robot in nearby_robots:
        robot_loc = robot.get_location()
        dir = loc.direction_to(robot_loc)
        if not can_move(dir): continue
        idx = direction_indices[dir]
        # Move to places with allies / enemies
        dir_paint_count[idx] = dir_paint_count[idx] + 1

    optimal_dir = -1
    optimal = 0
    for (test_dir, paint_count) in dir_paint_count.items():
        if paint_count > optimal:
            optimal = paint_count
            optimal_dir = test_dir

    if optimal_dir != -1:
        cur_dir = directions[optimal_dir] if random.random() > 0.99 else get_random_dir() # Introduce some randomness
        if can_move(cur_dir): move(cur_dir)

    dir = get_random_dir()
    if can_move(dir):
        move(dir)

    if can_repeat_cooldowned_action(sense_tower_delay):
        try_to_upgrade_towers()

def check_nearby_ruins():
    global should_save
    nearby_tiles = sense_nearby_map_infos(center=get_location())

    # Search for a nearby ruin to complete.
    for tile in nearby_tiles:
        tile_loc = tile.get_map_location()
        if not tile.has_ruin() or sense_robot_at_location(tile_loc) != None:
            continue
        
        # Heuristic to see if the ruin is trying to be built on
        mark_loc = tile_loc.add(tile_loc.direction_to(get_location()))
        mark_info = sense_map_info(mark_loc)
        if not mark_info.get_mark().is_ally():
            continue

        should_save = True

        # Return early
        return

def update_friendly_towers():
    global should_save

    # Search for all nearby robots
    ally_robots  = sense_nearby_robots(team=get_team())
    for ally in ally_robots:
        # Only consider tower type
        if not ally.get_type().is_tower_type():
            continue

        ally_loc = ally.location
        if ally_loc in known_towers:
            # Send a message to the nearby tower
            if should_save and can_send_message(ally_loc):
                send_message(ally_loc, 0)
                should_save = False

            # Skip adding to the known towers array
            continue

        # Add to our known towers array
        known_towers.append(ally_loc)
        set_indicator_string(f"Found tower {ally.get_id()}")


def try_to_upgrade_towers():
    towers = sense_nearby_ruins(radius_squared=2)
    if get_chips() >= tower_upgrade_minimum:
        for ruins in towers:
            if can_upgrade_tower(ruins):
                upgrade_tower(ruins)
                log(f"Upgraded tower at {str(ruins)}!")

def try_refill_paint(paint_percentage, unitType):
    global known_paint_towers
    global is_refilling
    if len(known_paint_towers) == 0:
        is_refilling = False
        return
    if paint_percentage > back_to_aggresion[unitType]:
        is_refilling = False
    else:
        tower_loc = known_paint_towers[0]
        is_refilling = True
        bug2(tower_loc)
        if can_sense_location(tower_loc):
            paint_tower = sense_robot_at_location(tower_loc)
            if paint_tower == None:
                known_paint_towers.pop(0)
            elif can_transfer_paint(tower_loc, -paint_per_transfer): transfer_paint(tower_loc, -paint_per_transfer)

# Ensure marked squares are painted the right color if encountered
def paint_nearby_marks():
    if not is_action_ready(): return
    for pattern_tile in nearby_tiles:
        if pattern_tile.get_mark() != pattern_tile.get_paint() and pattern_tile.get_mark() != PaintType.EMPTY:
            use_secondary = (pattern_tile.get_mark() == PaintType.ALLY_SECONDARY)
            if can_attack(pattern_tile.get_map_location()):
                attack(pattern_tile.get_map_location(), use_secondary)
                return

# Check whether we can build an SRP here. Returns false if one is already present
def can_SRP_here():
    correct_count = 0
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            tiles = MapLocation(get_location().x+dx, get_location().y+dy)
            if not on_the_map(tiles):
                return False
            tile = sense_map_info(tiles)
            if tile.is_wall() or tile.has_ruin():
                return False
            if tile.get_paint().is_enemy() or ((tile.get_mark() == PaintType.ALLY_SECONDARY) != SRP[dx+2][dy+2] and tile.get_mark() != PaintType.EMPTY):
                return False
            if tile.get_mark() != PaintType.EMPTY and tile.get_mark() == tile.get_paint(): correct_count += 1
    return True if correct_count < 25 else False

def is_paint_tower(type):
    return type in {UnitType.LEVEL_ONE_PAINT_TOWER, UnitType.LEVEL_TWO_PAINT_TOWER, UnitType.LEVEL_THREE_PAINT_TOWER}