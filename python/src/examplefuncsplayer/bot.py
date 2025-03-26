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

bot_chance = {UnitType.SOLDIER : 40, UnitType.MOPPER : 25, UnitType.SPLASHER : 35}
tower_chance = {UnitType.LEVEL_ONE_MONEY_TOWER : 65, UnitType.LEVEL_ONE_PAINT_TOWER : 25, UnitType.LEVEL_ONE_DEFENSE_TOWER : 10}
bot_name = {UnitType.SOLDIER : "SOLDIER", UnitType.MOPPER : "MOPPER", UnitType.SPLASHER : "SPLASHER"}

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

def get_random_unit(probabilities):
    n = random.randint(1, 100)
    for (unit, prob) in probabilities.items():
        if n <= prob: return unit
        n -= prob

# Determine build delays between each bot spawned by a tower
buildDelay = 11 # Tune
buildDeviation = 2

# When we're trying to build, how long should we save
save_turns = 70 # Tune

# Privates
buildCooldown = 0
is_messanger = False # We designate half of moppers to be messangers
known_towers = []
should_save = False
savingTurns = 0
updated = False

tower_upgrade_threshold = 1

def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """
    global turn_count
    global is_messanger
    global is_messanger
    global updated
    turn_count += 1

    # Prioritize chips in early game
    if turn_count >= 50 and not updated:
        update_tower_chance(25, 70, 5)
        updated = True

    if get_type() == UnitType.SOLDIER:
        run_soldier()
    elif get_type() == UnitType.MOPPER:
        if get_id() % 2 == 0: is_messanger = True
        run_mopper()
    elif get_type() == UnitType.SPLASHER:
        run_splasher()
    elif get_type().is_tower_type():
        run_tower()
    else:
        pass  # Other robot types?

def run_tower():
    global buildCooldown
    global savingTurns
    global should_save
    # Pick a direction to build in.
    dir = directions[random.randint(0, len(directions) - 1)]
    loc = get_location()
    next_loc = get_location().add(dir)
    enemy_robots = sense_nearby_robots(center=get_location(),team=get_team().opponent())

    # Ability for towers to attack
    if(is_action_ready() and len(enemy_robots) != 0):
        # Pick a random target to attack
        for random_enemy in enemy_robots:
            loc2 = random_enemy.get_location()
            dist = (loc.x - loc2.x) ** 2 + (loc.y - loc2.y) ** 2
            if can_attack(random_enemy.get_location()):
                attack(loc2)
                break

    # Pick a random robot type to build.
    # Should hold off on building since we're gonna end up with all moppers!
    if savingTurns <= 0:
        should_save = False
        if buildCooldown <= 0: 
            robot_type = get_random_unit(bot_chance)
            if can_build_robot(robot_type, next_loc):
                build_robot(robot_type, next_loc)
                buildCooldown = buildDelay + random.randint(-buildDeviation, buildDeviation)
                log("BUILT A " + bot_name[robot_type])

    if buildCooldown > 0: buildCooldown -= 1
    if savingTurns > 0: 
        savingTurns -= 1
        log("Saving for " + savingTurns + " more turns")
    

    # Read incoming messages
    messages = read_messages()
    for m in messages:
        log(f"Tower received message: '#{m.get_sender_id()}: {m.get_bytes()}'")

        # If we are not currently saving and we receive the save chips message, start saving
        if not should_save and m.get_bytes() == int(MessageType.SAVE_CHIPS):
            savingTurns = save_turns
            should_save = True


    # TODO: can we attack other bots?

def run_soldier():
    # Sense information about all visible nearby tiles.
    nearby_tiles = sense_nearby_map_infos(center=get_location())

    # Search for a nearby ruin to complete.
    cur_ruin = None
    tower_type = None
    dir = None
    cur_dist = 999999
    for tile in nearby_tiles:
        if tile.has_ruin() and sense_robot_at_location(tile.get_map_location()) == None:
            check_dist = tile.get_map_location().distance_squared_to(get_location())
            if check_dist < cur_dist:
                cur_dist = check_dist
                cur_ruin = tile


    if cur_ruin is not None:
        for tile2 in nearby_tiles:
                if tile2.get_paint().is_enemy() and cur_ruin.get_map_location().distance_squared_to(tile2.get_map_location()) <= 8: 
                    cur_ruin = None
                    break
        if cur_ruin is not None:
            # Should circle around tower to be able to paint all tiles
            target_loc = cur_ruin.get_map_location()
            dir = get_location().direction_to(target_loc)
            if can_move(dir):
                move(dir)
            else:
                # Circle
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
            should_mark = cur_ruin.get_map_location().subtract(dir)
            if can_sense_location(should_mark):
                if sense_map_info(should_mark).get_mark() == PaintType.EMPTY and can_mark_tower_pattern(tower_type, target_loc):
                    mark_tower_pattern(tower_type, target_loc)
                    log("Trying to build a tower at " + str(target_loc))

            # Fill in any spots in the pattern with the appropriate paint.
            for pattern_tile in sense_nearby_map_infos(target_loc):
                if pattern_tile.get_mark() != pattern_tile.get_paint() and pattern_tile.get_mark() != PaintType.EMPTY:
                    use_secondary = pattern_tile.get_mark() == PaintType.ALLY_SECONDARY
                    if can_attack(pattern_tile.get_map_location()):
                        attack(pattern_tile.get_map_location(), use_secondary)

            # Complete the ruin if we can.
            if can_complete_tower_pattern(tower_type, target_loc):
                complete_tower_pattern(tower_type, target_loc)
                cur_ruin = None
                tower_type = None
                set_timeline_marker("Tower built", 0, 255, 0)
                log("Built a tower at " + str(target_loc) + "!")
    # Make sure we go to empty square
    cur_dir = None
    cur_dist = 999999
    for tile in nearby_tiles:
        if not tile.is_wall() and not tile.has_ruin() and tile.get_paint() == PaintType.EMPTY:
            dir = get_location().direction_to(tile.get_map_location())
            dst = get_location().distance_squared_to(tile.get_map_location())
            if can_move(dir) and dst < cur_dist:
                cur_dist = dst
                cur_dir = dir
    if cur_dir is not None and can_move(cur_dir): move(cur_dir)

    # If we can't find empty squares, go randomly
    dir = directions[random.randint(0, len(directions) - 1)]
    if can_move(dir):
        move(dir)

    # Try to paint beneath us as we walk to avoid paint penalties.
    # Avoiding wasting paint by re-painting our own tiles.
    current_tile = sense_map_info(get_location())
    if not current_tile.get_paint().is_ally() and can_attack(get_location()):
        attack(get_location())

def run_mopper():
    if is_messanger:
        set_indicator_dot(get_location(), 255, 0, 0)

    if should_save and len(known_towers) > 0:
        # Move to first known tower if we are saving
        dir = get_location().direction_to(known_towers[0])
        set_indicator_string(f"Returning to {known_towers[0]}")
        if can_move(dir):
            move(dir)

    # Move and attack randomly.
    dir = directions[random.randint(0, len(directions) - 1)]
    next_loc = get_location().add(dir)
    enemy_robots = sense_nearby_robots(center=get_location(),radius_squared=2, team=get_team().opponent())
    nearby_tiles = sense_nearby_map_infos(center=get_location(),radius_squared=2)

    if can_move(dir):
        move(dir)

    attacked = False
    # Only attacks when sees enemy
    for enemy in enemy_robots:
        target_loc = enemy.get_location()
        swingDir = get_location().direction_to(target_loc)
        if can_mop_swing(swingDir):
            mop_swing(swingDir)
            log("Mop Swing! Booyah!")
            attacked = True
            break

    if not attacked:
        for tile in nearby_tiles:
            if tile.get_paint() == PaintType.ENEMY_PRIMARY or tile.get_paint() == PaintType.ENEMY_SECONDARY:
                mop_dir = get_location().direction_to(tile.get_map_location())
                mop_loc = get_location().add(mop_dir)
                if can_attack(mop_loc): attack(mop_loc)
                break

    if is_messanger:
        update_friendly_towers()

    # We can also move our code into different methods or classes to better organize it!
    update_enemy_robots()

#TODO (LITERALLY THE BIGGEST TODO YET)
def run_splasher():
    dir = directions[random.randint(0, len(directions) - 1)]
    next_loc = get_location().add(dir)
    if can_move(dir):
        move(dir)

    # Get all tiles we're gonna paint over to avoid painting on marked tiles 
    # Total splashed tiles = 13. We're gonna splash if 5+ tiles are splashable
    if can_attack(next_loc):
        loc = get_location()
        see_primary = False
        see_secondary = False
        splashables = 0
        painted_over = sense_nearby_map_infos(center=loc, radius_squared=4)
        for tile in painted_over:
            if tile.get_mark() == PaintType.ALLY_SECONDARY: 
                see_secondary = True
            elif tile.get_mark() == PaintType.ALLY_PRIMARY:
                see_primary = True
            if not tile.get_mark().is_ally(): splashables += 1
        
        if splashables >= 5:
            if see_primary and see_secondary: # Impossible
                pass
            elif see_secondary: 
                attack(loc, True)
            else:
                attack(loc, False)

def check_nearby_ruins():
    global should_save
    nearby_tiles = sense_nearby_map_infos(center=get_location())

    # Search for a nearby ruin to complete.
    cur_ruin = None
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
                send_message(ally_loc, int(MessageType.SAVE_CHIPS))
                should_save = False

            # Skip adding to the known towers array
            continue

        # Add to our known towers array
        known_towers.append(ally_loc)
        set_indicator_string(f"Found tower {ally.get_id()}")


def update_enemy_robots():
    # Sensing methods can be passed in a radius of -1 to automatically 
    # use the largest possible value.
    enemy_robots = sense_nearby_robots(team=get_team().opponent())
    if len(enemy_robots) == 0:
        return

    set_indicator_string("There are nearby enemy robots! Scary!");

    # Save an array of locations with enemy robots in them for possible future use.
    enemy_locations = [None] * len(enemy_robots)
    for i in range(len(enemy_robots)):
        enemy_locations[i] = enemy_robots[i].get_location()

    # Occasionally try to tell nearby allies how many enemy robots we see.
    # if get_round_num() % 20 == 0:
    #     for ally in ally_robots:
    #         if can_send_message(ally.location):
    #             send_message(ally.location, len(enemy_robots))