#!/usr/bin/env python3

import pygame
import sys
sys.path.append('../')
import league
from background import Background
from actors import Player
from physics import GravityManager
import neon_engine
import json
import logging


logger = logging.getLogger('Main')
"""
Copied and modified from example.
"""
def init_map(engine, player, gravity):
    """Create map and background"""
    league.Settings.tile_size = 16
    league.Settings.fill_color = (31, 38, 84)

    sprites = league.Spritesheet('./assets/tileset-collapsed.png', league.Settings.tile_size, 14)
    level1 = league.Tilemap('./assets/level1.lvl', sprites, layer = 2)
    engine.drawables.add(level1.passable.sprites()) 
    full_background = Background('./assets/skyline-a.png', 0)
    background = Background('./assets/buildings-bg.png', 1)

    logger.info(full_background)
    logger.info(background)
    engine.drawables.add(full_background)
    engine.drawables.add(background)
    world_size = (level1.wide*league.Settings.tile_size, level1.high*league.Settings.tile_size)

    # cam = league.LessDumbCamera(400, 200, player, engine.drawables, world_size)
    # engine.objects.append(cam)

    # Gravity must be appended first
    engine.objects.append(gravity)
    player.world_size = world_size
    player.rect = player.image.get_rect()
    player.blocks.add(level1.impassable)
    engine.objects.append(player)
    engine.drawables.add(player)

def main():
    ## Debug Versions
    
    logger.info(pygame.version.ver)
    logger.info(pygame.get_sdl_version())

    engine = neon_engine.NeonEngine('Neon Souls')
    
    engine.init_pygame()

    with open('player_sprites.json', 'r') as p_file:
        player_sprites = json.load(p_file)

    player_static = player_sprites['static_sprites']
    player_walking = player_sprites['walking_sprites']

    player = Player(player_static, player_walking,(128, 128), 'default', 2, 300, 400)

    gravity_manager = GravityManager()
    gravity_manager.add_gravity('default', (0, 15))

    gravity_manager.add_object(player)
    
    # create background and level
    init_map(engine, player, gravity_manager)

    pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // league.Settings.gameTimeFactor)
    engine.movement_function = player.move_player
    engine.physics_functions.append(player.process_gravity)

    engine.events[pygame.QUIT] = engine.stop
    # exit(0)
    engine.run()

if __name__=='__main__':
    league.logger_init()
    main()
