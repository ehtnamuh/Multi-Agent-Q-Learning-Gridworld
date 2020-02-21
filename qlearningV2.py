import numpy as np  
from PIL import Image
from cv2 import cv2
import traceback
import time

import Game
import Utility
import MyConstants

# Score trackers
score_player = []
score_enemy = []
score_food = []
episode_iterations = []
trap_counter = []

# Video production & Display related
W_HEIGHT = 300
W_WIDTH = 300
img_array = []

show = False
make_video = False
# wait time between frames displayed
frame_wait_time = 200
if (MyConstants.HM_EPISODES <= 100):
    show = True
    make_video = True
else: 
    show = False
    make_video = False

# *****************************
# LEVEL SELECT 
level = "level1"    # OR #level = "level2"
# *****************************

# Maximum episodes, step count and Epsilon 
# decay rate are in the MyConstant.py file

# *****************************
# Learning randomness
epsilon = 1
# *****************************


# LOAD Q_TABLES IN BACKEND CLASS UTILITY
q_utility = Utility.Utility()
q_utility.load_all_tables(level, MyConstants.SIZE)

# ****************************
# Everything loaded and ready
print("Q learning program has started")
print("epsilon: %s, epsilon_decay: %s, Max episodes: %s, Max steps: %s"%(epsilon, MyConstants.EPS_DECAY ,MyConstants.HM_EPISODES, MyConstants.STEP_COUNT))
print("level: %s"%(level))

episode_rewards = []
episode_reward = 0
game_draw_counter = 0
cummulitive_steps = 0
cummulitive_trap_counter = 0
# Game object created
game = Game.MyGame(level = level, SIZE = MyConstants.SIZE, is_training = False)

try:
    for episode in range(1, MyConstants.HM_EPISODES+1):
        # reset game before each new episode
        game.reset_environment()
        episode_reward = 0
        if episode % MyConstants.SHOW_EVERY == 0:
            print("on # %3f, epsilon: %s"%(episode, epsilon))
            print("%sep mean_reward: %s"%(episode, np.mean(episode_rewards[-MyConstants.SHOW_EVERY:])))
            if int(MyConstants.HM_EPISODES / MyConstants.SHOW_EVERY) <= 100:
                make_video = True
            score_player.append((game.get_blobs()[MyConstants.PLAYER].score / episode)*100)
            score_enemy.append((game.get_blobs()[MyConstants.ENEMY].score / episode)*100)
            score_food.append((game.get_blobs()[MyConstants.FOOD].score / episode)*100)
            episode_iterations.append( ( (cummulitive_steps/MyConstants.SHOW_EVERY)/MyConstants.STEP_COUNT)*100)
            trap_counter.append( ( (cummulitive_trap_counter/ MyConstants.SHOW_EVERY)/3)*100)
            cummulitive_steps = 0
            cummulitive_trap_counter = 0
        else: make_video = False

        for step in range(1, MyConstants.STEP_COUNT + 1):
            obs_enemy = game.get_obeservation(MyConstants.ENEMY)
            obs_food = game.get_obeservation(MyConstants.FOOD)
            obs_player = game.get_obeservation(MyConstants.PLAYER)
            
            if np.random.random() > epsilon: 
                enemy_action =  np.argmax(q_utility.q_tables[MyConstants.ENEMY][obs_enemy])
                food_action =  np.argmax(q_utility.q_tables[MyConstants.FOOD][obs_food])
                player_action = np.argmax(q_utility.q_tables[MyConstants.PLAYER][obs_player])
            else:
                food_action = False
                enemy_action = False
                player_action = False
            
            new_obs_player, player_col_st, game_ended = game.env_step(player_action, MyConstants.PLAYER)
            new_obs_enemy, enemy_col_st, game_ended = game.env_step(enemy_action, MyConstants.ENEMY)
            new_obs_food, food_col_st, game_ended = game.env_step(food_action, MyConstants.FOOD)

            if (episode <= MyConstants.STOP_TRAINING_EPISODE):
                reward_enemy = q_utility.get_reward(enemy_col_st)
                reward_food = q_utility.get_reward(food_col_st)
                q_utility.calc_new_q_value(obs_enemy, new_obs_enemy, MyConstants.ENEMY, enemy_action, reward_enemy)
                q_utility.calc_new_q_value(obs_food, new_obs_player, MyConstants.FOOD, food_action, reward_food)
            
            reward_player = q_utility.get_reward(player_col_st)
            q_utility.calc_new_q_value(obs_player, new_obs_player, MyConstants.PLAYER, player_action, reward_player)
            episode_reward += reward_player

            if step == MyConstants.STEP_COUNT:
                game_draw_counter += 1
            if game_ended or step == MyConstants.STEP_COUNT:
                if make_video:
                    img = game.render(W_WIDTH = W_WIDTH, W_HEIGHT = W_HEIGHT, final_frame= True)
                    for i in range(25): img_array.append(img)
                cummulitive_steps += step
                cummulitive_trap_counter += game.get_trap_counter()
                if show: cv2.waitKey(frame_wait_time)
            else:
                if make_video:
                    img = game.render(W_WIDTH = W_WIDTH, W_HEIGHT = W_HEIGHT, show = show)
                    img_array.append(img)
                if show: cv2.waitKey(int(frame_wait_time/4))
            
            if game_ended or step == MyConstants.STEP_COUNT:
                break
        
        episode_rewards.append(episode_reward)
        epsilon *= MyConstants.EPS_DECAY
except  Exception as e: traceback.print_exc()
finally:
    if make_video:
        out = cv2.VideoWriter('Videos\\catchAFly-%s-%s.avi'%(level ,int(time.time())), 0, 25, (W_WIDTH, W_HEIGHT))
        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()
        cv2.destroyAllWindows()
    q_utility.write_all_tables()
    print("DONE")

# figures saved in figures folder
q_utility.save_figures(episode_iterations=episode_iterations, score_player=score_player, score_enemy= score_enemy, score_food= score_food, trap_counter = trap_counter,level= level)
