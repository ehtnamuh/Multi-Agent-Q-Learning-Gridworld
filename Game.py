import numpy as np
from PIL import Image
from PIL import ImageDraw
from cv2 import cv2
from typing import overload
import Blob

class MyGame():
    # PLAYER COLLISION STATES
    HIT_ENEMY = 'hit_enemy'
    HIT_OBSTACLE = 'hit_obstacle'
    HIT_FOOD = 'hit_food'
    HIT_TRAP = 'hit_trap'

    # Object Color data
    PLAYER_N = 1
    FOOD_N = 2
    ENEMY_N = 3
    OBSTACLE_N = 4
    TRAP_N = 5
    d = {1: (255, 175, 0),
        2: (0, 255, 0),
        3: (0, 0, 255),
        4: (255, 255, 255),
        5: (0, 165, 255)}
    
    # Obstacles N trap locations by lvl
    levels = {'level1': {
        'obstacles': [(2, 3), (2, 5), (2, 6), (2, 7),
                    (6, 3), (6, 5), (6, 6), (6, 7),
                    (4, 3), (4, 8)],
        'traps': [(4, 5), (8, 1)]
    }}

    # Game States
    STATE_ENEMY_WIN = "ENEMY_WIN"
    STATE_PLAYER_WIN = "PLAYER_WIN"
    STATE_FOOD_WIN = "FOOD_WIN"
    STATE_DRAW = "DRAW"
    
    
    def __init__(self, level='level1', SIZE=10, is_training = False):
        if (SIZE < 10):
            SIZE = 10
        self.SIZE = SIZE
        self.environment = []
        self.is_training = is_training
        self.game_state = self.STATE_DRAW
        # TODO: READ LEVELS FORM FILE LATER
        # self.levels = some file read operation
        self.load_level(level)
        self.player, self.enemy, self.food = None, None, None
        self.create_blobs()

    def load_level(self, level='level1'):
        self.obstacle_list = self.levels[level]['obstacles']
        self.trap_list = self.levels[level]['traps']

    def update_environment(self):
        self.environment = np.zeros(
            (self.SIZE, self.SIZE, 3), dtype=np.uint8)
        for obstacle in self.obstacle_list:
            self.environment[obstacle[1]][obstacle[0]] = self.d[self.OBSTACLE_N]
        for trap in self.trap_list:
            self.environment[trap[1]][trap[0]] = self.d[self.TRAP_N]
        self.environment[self.food.y][self.food.x] = self.food.color
        self.environment[self.player.y][self.player.x] = self.player.color
        self.environment[self.enemy.y][self.enemy.x] = self.enemy.color

    def reset_environment(self):
        self.environment = []
        self.create_blobs()
        self.update_environment()

    def create_blobs(self):
        if (self.player == None): self.player = Blob.Blob(self.d[self.PLAYER_N], self.SIZE)
        if (self.enemy == None): self.enemy = Blob.Blob(self.d[self.ENEMY_N] ,self.SIZE)
        if (self.food == None): self.food = Blob.Blob(self.d[self.FOOD_N], self.SIZE)
        self.player.randomize_pos()
        self.enemy.randomize_pos()
        self.food.randomize_pos()
        while (self.player.get_pos() in self.obstacle_list or
                self.player.get_pos() in self.trap_list):
            self.player.randomize_pos()
        while (self.enemy.get_pos() in self.obstacle_list or
                self.enemy.get_pos() in self.trap_list):
            self.enemy.randomize_pos()
        while (self.food.get_pos() in self.obstacle_list or
                self.food.get_pos() in self.trap_list):
            self.food.randomize_pos()
    
    def draw_message(self, image, location, my_msg, my_color):
        ImageDraw.Draw(
            image  # Image
        ).text(
            location,  # Coordinates
            my_msg,  # Text
            my_color  # Color
        )

    def draw_score(self, image):
        my_message = "PLAYER SCORE: " + str( self.player.score )
        self.draw_message(image, (0,0),  my_message, self.player.color)
        my_message = "ENEMY SCORE: " + str( self.enemy.score )
        self.draw_message(image, (0,10),  my_message, self.enemy.color)
        my_message = "FOOD SCORE: " + str( self.food.score )
        self.draw_message(image, (0,20),  my_message, self.food.color)

    def render(self, W_WIDTH=300, W_HEIGHT=300, final_frame=False):
        img = Image.fromarray(self.environment, "RGB")
        img = img.resize((W_WIDTH, W_HEIGHT))
        self.draw_score(img)
        img = np.array(img)
        cv2.imshow("Catch A Fly", img)
        return img

    def update_scores(self):
        if self.player.get_pos() == self.food.get_pos(): 
            self.player.score += 1
            self.game_state = self.STATE_PLAYER_WIN
        elif self.enemy.get_pos() == self.player.get_pos(): 
            self.enemy.score += 1
            self.game_state = self.STATE_ENEMY_WIN
        elif self.food.get_pos() == self.enemy.get_pos(): 
            self.food.score += 1
            self.game_state = self.STATE_FOOD_WIN
        else: self.game_state = self.STATE_DRAW

    def check_collisions(self, position):
        # TODO: check collisions with enemy food obstacle and return state
        if position in self.obstacle_list or position in self.trap_list:
            return True
        else:
            return False

    # returns player collision state
    def check_player_collisions(self, position):
        player_col_st = {self.HIT_OBSTACLE: False, self.HIT_TRAP: False,
                        self.HIT_ENEMY: False, self.HIT_FOOD: False}
        if position in self.obstacle_list:
            player_col_st[self.HIT_OBSTACLE] = True
        if position in self.trap_list:
            player_col_st[self.HIT_TRAP] = True
        if position == self.enemy.get_pos():
            player_col_st[self.HIT_ENEMY] = True
        if position == self.food.get_pos():
            player_col_st[self.HIT_FOOD] = True
        return player_col_st

    # every entity takes 1 step , 1  tick of this game
    def env_step(self, player_action=False, enemy_action=False, food_action=False):
        # Prevent things from crossing over walls
        if not player_action:
            player_action = np.random.randint(0, 4)
        player_col_st = self.check_player_collisions(
            self.player.try_action(player_action))
        hit_obstacle = player_col_st['hit_obstacle']
        if not hit_obstacle:
            self.player.action(player_action)
        if not self.is_training:
            if not enemy_action:
                enemy_action = np.random.randint(0, 4)
            if not self.check_collisions(self.enemy.try_action(enemy_action)):
                self.enemy.action(enemy_action)

            if not food_action:
                food_action = np.random.randint(0, 4)
            if not self.check_collisions(self.food.try_action(food_action)):
                self.food.action(food_action)
        
        self.update_environment()
        self.update_scores()
        return (self.get_obeservation(), player_col_st, self.game_end_condition())

    def game_end_condition(self):
        if self.game_state == self.STATE_DRAW: return False
        else: return True
    
    # format (player, enemy, food)
    def get_obeservation(self, viewer="player"):
        if viewer == "player":
            return (self.player.get_pos(), self.enemy.get_pos(), self.food.get_pos())
        if viewer == "enemy":
            return (self.enemy.get_pos(), self.food.get_pos(), self.player.get_pos())
        if viewer == "food":
            return (self.food.get_pos(), self.player.get_pos(), self.enemy.get_pos())
