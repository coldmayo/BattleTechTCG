import sys
sys.path.append('gym_mod/')

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

from model.DQN import *
from model.memory import *
from model.utils import *

from tqdm import tqdm
import gymnasium as gym

from gym_mod.engine.genDeck import *
from gym_mod.envs.BT_TCG import *

import warnings
warnings.filterwarnings("ignore") 

print("\nTraining...\n")

n_actions = []

env = gym.make("BT_TCG_v0", disable_env_checker=True, model_cards=gen_deck("kurita"), enemy_cards=gen_deck("kurita"))
state = env.reset()
model_deck, reward, in_battle = env.draw_phase("model")
n_actions = [60, 60, 60, 1, 60]

n_observations = 3150

policy_net = DQN(n_observations, n_actions).to(device)
target_net = DQN(n_observations, n_actions).to(device)
target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.AdamW(policy_net.parameters(), lr = 0.0025)

memory = ReplayMemory(10000)

numGames = 5

pbar = tqdm(total=numGames)

state = env.reset()

end = False

game_num = 0

tau = 0.005
#print(state.values())
i = 0
done = 0
in_battle = 0

while end == False:
    
    enemy_deck, reward, in_battle = env.draw_phase("enemy")
    if in_battle == False:
        print("enemy draws 2 cards")

    if type(enemy_deck) == int:
        done = enemy_deck

    #print("Enemy hand:", enemy_deck["hand"], "\n")
    done, reward = env.enemyTurn()
    if i != 0:
        model_deck, reward, in_battle = env.draw_phase("model")
        if in_battle == False:
            print("model draws 2 cards")
        if type(model_deck) == int:
            done = model_deck
    if in_battle == False:
        print("Enemy stockpile:", len(enemy_deck["stock"]), "Model stockpile:", len(model_deck["stock"]))
    if done == 0:
        if type(state) == dict:
            state_vals = np.array(list(state.values())).astype(float)
            state = torch.tensor(flatten_list(state_vals), dtype=torch.float32, device=device).unsqueeze(0)
        else:
            state = torch.tensor(flatten_list(state), dtype=torch.float32, device=device).unsqueeze(0)

        action = select_action(env, state, i, policy_net, model_deck)
        action_dict = convertToDict(action)

        next_obs, reward, done, info, _ = env.step(action_dict)

        reward = torch.tensor([reward], device=device)
    
        next_state = torch.tensor(np.array(list(next_obs.values())).astype(float), dtype=torch.float32, device=device).unsqueeze(0)
        memory.push(state, action, next_state, reward)

        state = next_state
        loss = optimize_model(policy_net, target_net, optimizer, memory, n_observations, model_deck)

        for key in policy_net.state_dict():
            target_net.state_dict()[key] = policy_net.state_dict()[key]*tau + target_net.state_dict()[key]*(1-tau)
        target_net.load_state_dict(target_net.state_dict())

    elif done != 0:
        pbar.update(1)
        game_num += 1

        if done == -1:
            print("enemy won")
        elif done == 1:
            print("model won")
        elif done == 0.5:
            print("tied!")
        new_model_deck = gen_deck("kurita")
        new_enemy_deck = gen_deck("kurita")
        #print(new_model_deck)
        state = env.reset(model_deck = new_model_deck, enemy_deck = new_enemy_deck)
        done = 0
    if game_num == numGames:
        end = True
        pbar.close()
    i += 1
    
env.close()
