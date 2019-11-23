import numpy as np  
from PIL import Image
from cv2 import cv2
import matplotlib.pyplot as plt
import pickle
from matplotlib import style
import time
import Game

style.use("ggplot")

SIZE = 10
HM_EPISODES = 50
STEP_COUNT = 100
SHOW_EVERY = 1
SECTIONS = 5
SECTION_SIZE = int(HM_EPISODES/SECTIONS)

# Epsilon is a value 0 to 1 which dictates the %chance of taking a random move not in the q table
epsilon = 0
EPS_DECAY = 0.9998
INTER_EPSILON = 0

LEARNING_RATE = 0.1
DISCOUNT = 0.95
# REWARDS
MOVE_PENALY = 1
OBSTACLE_PENALTY = 50
TRAP_PENALTY = 200
ENEMY_PENALY = 300
FOOD_REWARD = 25

start_q_table = "Models\\qtable-1573701411.pickle" 
enemy_q_table = "Models\\qtable-1573701411.pickle" # "Models\\qtable-1573674094.pickle"
# Video production
W_HEIGHT = 300
W_WIDTH = 300
img_array = []

# q_table = {}
if start_q_table is None:
    q_table = {}
    for x1 in range(0, SIZE):
        for y1 in range(0, SIZE):
            for x2 in range(0, SIZE):
                for y2 in range(0, SIZE):
                    for x3 in range(0, SIZE):
                        for y3 in range(0, SIZE):
                            q_table[((x1, y1),(x2, y2),(x3, y3))] = [np.random.uniform(-5, 0) for i in range(4) ]
else:
    with open(start_q_table, "rb") as f:
        q_table = pickle.load(f)
    if not enemy_q_table is None:
        with open(start_q_table, "rb") as f:
            q_table_enemy = pickle.load(f)
    
    
######################### DONE LOADING STUFF ####################################################
print("Runnin in the 90s.....")
episode_rewards = []
episode_reward = 0
game_draw_counter = 0
game = Game.MyGame(is_training = False)
try:
    for episode in range(0,HM_EPISODES+1):
        game.reset_environment()
        episode_reward = 0
        # if episode%SECTION_SIZE == 0: epsilon = INTER_EPSILON
        if episode % SHOW_EVERY == 0 and episode > 0:
            # print("on # %3f, epsilon: %s"%(episode, epsilon))
            # print("%s ep mean: %s"%(episode, np.mean(episode_rewards[-SHOW_EVERY:])))
            show = True
            # show = False
        else: show = False
        
        for step in range(1, STEP_COUNT + 1):
            obs_enemy = game.get_obeservation('enemy')
            obs_food = game.get_obeservation('food')
            enemy_action =  np.argmax(q_table_enemy[obs_enemy])
            food_action =  np.argmax(q_table_enemy[obs_food])
            obs = game.get_obeservation()
            reward = 0
            if np.random.random() > epsilon: action = np.argmax(q_table[obs])
            else: action = False
            # new_obs, player_col_st = game.env_step(player_action = action, is_training = True)
            new_obs, player_col_st, game_ended = game.env_step(player_action = action, enemy_action = enemy_action, food_action = food_action)

            if player_col_st[game.HIT_OBSTACLE]:
                reward = -OBSTACLE_PENALTY
            elif player_col_st[game.HIT_TRAP]:
                reward = -TRAP_PENALTY
            elif player_col_st[game.HIT_ENEMY]:
                reward = -ENEMY_PENALY
            elif player_col_st[game.HIT_FOOD]:
                reward = FOOD_REWARD
            else:
                reward = -MOVE_PENALY
            
            max_future_q = np.max(q_table[new_obs])
            current_q = q_table[obs][action]
            
            if reward == FOOD_REWARD: new_q = FOOD_REWARD
            else:
                new_q = (1 - LEARNING_RATE)*current_q + LEARNING_RATE*(reward + DISCOUNT*max_future_q)
            q_table[obs][action] = new_q
            episode_reward += reward  
            
            if show:
                if step == STEP_COUNT:
                    game_draw_counter += 1
                if game_ended or step == STEP_COUNT:
                    # & 0xFF to get rid of extrabits added by numlock on
                    img = game.render(W_WIDTH = W_WIDTH, W_HEIGHT = W_HEIGHT, final_frame= True)
                    for i in range(25): img_array.append(img)
                    cv2.waitKey(50)
                else:
                    img = game.render(W_WIDTH = W_WIDTH, W_HEIGHT = W_HEIGHT)
                    img_array.append(img)
                    cv2.waitKey(10)
            
            if game_ended or step == STEP_COUNT:
                break
            # if reward == FOOD_REWARD or reward == (-ENEMY_PENALY) or reward == (-TRAP_PENALTY):   
            #     break
        
        episode_rewards.append(episode_reward)
        epsilon *= EPS_DECAY
except  Exception as e: print(e)
finally:
    out = cv2.VideoWriter('Videos\\catchAFly.avi', 0, 25, (W_WIDTH, W_HEIGHT))
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    cv2.destroyAllWindows()
    with open("Models\\qtable-%s.pickle"%(int(time.time())), "wb") as f:
        pickle.dump(q_table, f)

# hist = {"player": game.player.score, "enemy": game.enemy.score, "food": game.food.score, "draw": game_draw_counter}
bar_labels = "player", "enemy", "food", "draw"
x = np.arange(1, 5)
plt.bar(1, (0, game.player.score), color = 'b', width= 0.5, label = "PLAYER")
plt.bar(2, (0, game.enemy.score), color = 'r', width= 0.5, label = "ENEMY")
plt.bar(3, (0, game.food.score), color = 'g', width= 0.5, label = "FOOD")
plt.bar(4, (0, game_draw_counter), color = 'w', width= 0.5, label = "DRAW")
plt.title("Blob Scores", fontsize = 20)
plt.xticks(x, bar_labels)
plt.legend(fontsize = 15, loc = (0.8, 0.8))
plt.show()
# # smooths the curve a bit
# moving_avg = np.convolve(episode_rewards, np.ones(SHOW_EVERY) / SHOW_EVERY, mode ="valid")

# plt.plot([i for i in range(len(moving_avg))], moving_avg)
# plt.ylabel("reward %s ma"%SHOW_EVERY)
# plt.xlabel("episode #" )
# plt.show()


