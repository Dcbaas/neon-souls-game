#!/usr/bin/env python3

import pygame
import sys
sys.path.append('../')
import league
from background import Background
from actors import Player
from actors import Projectile
from physics import GravityManager
from camera import CameraUpdates
from items.health_item import HealthItem
from actors import Player, SentinalEnemy
from physics import GravityManager
from flag import Flag
from overlay import Overlay
import neon_engine
import json
import random
import logging

logger = logging.getLogger('Main')


"""
Copied and modified from example.
game.py initalizes the game and all the objects needed for the game.
"""

def init_map(engine, player, gravity):
    """
    Loads up all the assets for the game map and 
    background sprites. Updates actors to hold world data. Does an inital render
    of all game objects.

    param - engine: The engine being used for this game instance
    param - player: The player being used for this game instance
    param - enemy_list: A list of enemey objects that are in this game instance.
    """
    league.Settings.tile_size = 16
    league.Settings.fill_color = (0, 0, 60)
    # league.Settings.tile_scale = 1.7

    sprites = league.Spritesheet('./assets/tileset-collapsed.png', league.Settings.tile_size, 14)
    level1 = league.Tilemap('./assets/level1.lvl', sprites, layer = 2)
    world_size = (level1.wide*league.Settings.tile_size, level1.high*league.Settings.tile_size)

    # initialize camera
    cam = CameraUpdates(player, world_size)
    engine.objects.append(cam)
    engine.drawables = cam # allow camera to override draw()

    # add in background and level1
    index = 0
    while index < world_size[0]:
        full_background = Background('./assets/skyline-a.png', x=index, layer=0)
        background = Background('./assets/buildings-bg.png', x=index, layer=1)
        engine.drawables.add(full_background)
        engine.drawables.add(background)
        index += league.Settings.width
    engine.drawables.add(level1.passable.sprites())

    # Gravity must be appended first
    engine.objects.append(gravity)
    player.world_size = world_size
    player.blocks.add(level1.impassable)

    engine.collisions[player] = []
    engine.objects.append(player)
    engine.drawables.add(player)

    place_random_items(engine, world_size, player)

    flag = Flag(world_size[0] - (league.Settings.tile_size * 10), world_size[1])
    engine.collisions[player].append((flag, flag.win))
    engine.objects.append(flag)
    engine.drawables.add(flag)

    # add background music with map creation
    ### MUSIC IS BROKEN WON' REPEAT 
    # pygame.mixer.music.load('assets/Blazer Rail.wav')
    # pygame.mixer.music.play(-1, 0.0)

    for enemy in engine.enemy_list:
        enemy.world_size = world_size
        enemy.rect = enemy.image.get_rect()
        enemy.blocks.add(level1.impassable)
        engine.objects.append(enemy)
        engine.drawables.add(enemy)
        engine.collisions[player].append((enemy, player.take_dmg))
    
def fire(engine, inputs):
    """
    A function that draws projectile objects when pressing the spacebar.
    It also handles projectile collisions with enemies.
    """
    if inputs['SPACE'] is True:
        if engine.objects[2].check_weapon_cooldown():
            pr = engine.objects[2].loadBullet()
            engine.objects.append(pr)
            engine.drawables.add(pr)
            pr.kill_function = engine.cleanup_projectile
            engine.collisions[pr] = []
            for enemy in engine.enemy_list:
                engine.collisions[pr].append((enemy, enemy.get_killed))
            # Sound effect added from
            # https://www.zapsplat.com/music/science-fiction-weapon-gun-shoot-powerful-2/
            pew = pygame.mixer.Sound('assets/laser1.wav')
            pew.play()

def place_random_items(engine, level_size, player):
    """
    Randomly places health items around the map
    """
    rand_start = level_size[0] // 4
    for i in range(2, 6):
        x = random.randrange(rand_start, rand_start * i)
        item = HealthItem(x, level_size[1])
        engine.drawables.add(item)
        engine.objects.append(item)
        engine.collisions[player].append((item, item.grab))

def main():
    """
    Sets up all the relevent object needed to run the game. This includes the 
    game engine, player, and all enemies in the game. The player and enemies load
    thier sprites from a list of paths in a json file that is loaded and referenced
    in a dict at the start. Once initalization finishes the game loop is run until
    the user exits. 
    """
    engine = neon_engine.NeonEngine('Neon Souls')
    
    engine.init_pygame()

    with open('player_sprites.json', 'r') as p_file:
        player_sprites = json.load(p_file)

    with open('sentinal_sprites.json') as file:
        sentinal_sprites = json.load(file)

    player_static = player_sprites['static_sprites']
    player_walking = player_sprites['walking_sprites']
    player_running = player_sprites['running_sprites']

    sentinal_sprites = sentinal_sprites['sprite_list']

    player = Player(player_static, player_walking, player_running, (128, 128), 'default', 2, 300, 400)
    engine.player_instance = player

    sentinal1 = SentinalEnemy(sentinal_sprites, (100,100), [(400, 500), (600, 500)], engine.kill_enemy, 2, 300, 475)
    sentinal2 = SentinalEnemy(sentinal_sprites, (100,100), [(1100, 0), (1300, 0)], engine.kill_enemy, 2, 1200, 400)
    sentinal3 = SentinalEnemy(sentinal_sprites, (100,100), [(1500, 0), (1700, 0)], engine.kill_enemy, 2, 1600, 450)

    engine.enemy_list.append(sentinal1)
    engine.enemy_list.append(sentinal2)
    engine.enemy_list.append(sentinal3)
    gravity_manager = GravityManager()
    gravity_manager.add_gravity('default', (0, 15))

    gravity_manager.add_object(player)
    
    # create background and level
    init_map(engine, player, gravity_manager)

    overlay = Overlay(player)
    engine.objects.append(overlay)
    engine.drawables.add(overlay)

    pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // league.Settings.gameTimeFactor)
    engine.movement_function = player.move_player
    engine.action_function = fire
    engine.physics_functions.append(player.process_gravity)

    engine.events[pygame.QUIT] = engine.stop
    engine.run()


#void main(int argc, char* argv[])...
if __name__=='__main__':
    league.logger_init()
    main()
