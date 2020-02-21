import pickle
import numpy as np

import time
import matplotlib.pyplot as plt
from matplotlib import style
# style.use("ggplot")

import Game
import MyConstants

class Utility():
    def __init__(self):
        self.enemy_table_path = ""
        self.player_table_path = ""
        self.food_table_path = ""

        self.q_tables = {MyConstants.ENEMY : {},
                        MyConstants.FOOD : {},
                        MyConstants.PLAYER : {}}
    
    def load_q_table(self, table_path, SIZE):
        q_table = {}
        try:
            with open(table_path, "rb") as f:
                q_table = pickle.load(f)
        except Exception:
            q_table = {}
            for x1 in range(0, SIZE):
                for y1 in range(0, SIZE):
                    for x2 in range(0, SIZE):
                        for y2 in range(0, SIZE):
                            for x3 in range(0, SIZE):
                                for y3 in range(0, SIZE):
                                    q_table[((x1, y1),(x2, y2),(x3, y3))] = [np.random.uniform(-5, 0) for i in range(4) ]
        finally:
            return q_table

    def write_q_table(self, table_path, q_table):
        try:
            with open(table_path, "wb") as f:
                pickle.dump(q_table, f)
        except Exception as identifier:
            print("Failed to write q table")
            print(identifier)
        
    def write_all_tables(self):
        self.write_q_table(self.enemy_table_path, self.q_tables[MyConstants.ENEMY])
        self.write_q_table(self.player_table_path, self.q_tables[MyConstants.PLAYER])
        self.write_q_table(self.food_table_path, self.q_tables[MyConstants.FOOD])
    
    def make_path(self, level):
        path = "Models\\%s\\"%(level)
        filename = "_q_table-%s.pickle"%(level)
        self.enemy_table_path = path + "enemy" + filename
        self.player_table_path = path + "player" + filename
        self.food_table_path = path + "food" + filename
    
    def load_all_tables(self, level = "level1", SIZE = 10):
        self.make_path(level)
        self.q_tables[MyConstants.ENEMY] = self.load_q_table(self.enemy_table_path, SIZE)
        self.q_tables[MyConstants.PLAYER] = self.load_q_table(self.player_table_path, SIZE)
        self.q_tables[MyConstants.FOOD] = self.load_q_table(self.food_table_path, SIZE)
        
    def get_reward(self, player_col_st):
        reward = 0
        if player_col_st[Game.States.HIT_OBSTACLE]:
            reward = -MyConstants.OBSTACLE_PENALTY
        elif player_col_st[Game.States.HIT_TRAP]:
            reward = -MyConstants.TRAP_PENALTY
        elif player_col_st[Game.States.HIT_ENEMY]:
            reward = -MyConstants.ENEMY_PENALY
        elif player_col_st[Game.States.HIT_FOOD]:
            reward = MyConstants.FOOD_REWARD
        else:
            reward = -MyConstants.MOVE_PENALY
        return reward

    def calc_new_q_value(self, old_obs, new_obs, blob_name, action, reward):
        max_future_q = np.max(self.q_tables[blob_name][new_obs])
        current_q = self.q_tables[blob_name][old_obs][action]
            
        if reward == MyConstants.FOOD_REWARD: new_q = MyConstants.FOOD_REWARD
        else:
            new_q = (1 - MyConstants.LEARNING_RATE)*current_q + MyConstants.LEARNING_RATE*(reward +  MyConstants.DISCOUNT*max_future_q)
            self.q_tables[blob_name][old_obs][action] = new_q
            

    def save_figures(self, episode_iterations, score_player, score_enemy, score_food, trap_counter, level):
        # PLOT AND SAVE FIGURES
        episodes = np.arange(1 , int((MyConstants.HM_EPISODES/MyConstants.SHOW_EVERY) + 1))
        episodes = np.multiply(episodes, MyConstants.SHOW_EVERY)
        plt.figure(figsize=(15,15))
        plt.subplot(2, 1, 1)
        plt.xlabel('EPISODES')
        plt.ylabel('SCORE %')
        # plt.plot(episodes, episode_iterations, color = 'y', label = "ITERATIONS") 
        plt.plot(episodes, score_player, color = 'b', label = "PLAYER")
        plt.plot(episodes, score_food, color = 'g', label = "FOOD")
        plt.plot(episodes, score_enemy, color = 'r', label = "ENEMY")
        plt.xticks(np.arange(min(episodes), max(episodes)+1, MyConstants.SHOW_EVERY*10))
        plt.legend(loc = 'best')

        plt.subplot(2, 1, 2)
        plt.xlabel('EPISODES')
        plt.ylabel('ITERATIONS/TRAPS %')
        episode_iterations = np.array(episode_iterations)
        # plt.scatter(episodes, episode_iterations, color = 'y')
        # plt.plot(episodes, trap_counter, color = 'r', label = "TRAPS")
        zt = np.polyfit(episodes, trap_counter, 2)
        yt = np.poly1d(zt)
        plt.plot(episodes, yt(episodes), '-', color = 'r', label = "TRAPS")
        z = np.polyfit(episodes, episode_iterations, 2)
        y = np.poly1d(z)
        plt.plot(episodes, y(episodes), '-', color = 'y', label = "ITERATIONS")
        plt.xticks(np.arange(min(episodes), max(episodes)+1, MyConstants.SHOW_EVERY*10))
        plt.legend(loc = 'best')
        # plt.show()

        plt.savefig('Figures\\output-%s-%s.png'%(level ,int(time.time())))