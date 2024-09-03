import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import collections
import numpy as np
import pandas as pd
import os
import json

import itertools

import random
import numpy as np

from collections import namedtuple

EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 1000
GAMMA = 0.99

BATCH_SIZE = 128

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

Transition = namedtuple('Transition',('state', 'action', 'next_state', 'reward'))

def pad_tensor(tensor, target_shape):
    padding = (0, target_shape[1] - tensor.size(1))
    return torch.tensor(F.pad(tensor, padding, mode='constant', value=0)).requires_grad_()

def filter_q(deck, q, filter="hand"):
    ret = []
    ids = []
    if filter == "hand":
        
        for i in deck["hand"]:
            if "Mission" not in i["Card Type"]:
                ids.append(i["id"])
                
        for i in range(len(q)):
            if i not in ids:
                ret.append(0)
            else:
                ret.append(q[i])
    elif filter == "mission":
        
        for i in deck["hand"]:
            if "Mission" in i["Card Type"]:
                ids.append(i["id"])
                
        for i in range(len(q)):
            if i not in ids:
                ret.append(0)
            else:
                ret.append(q[i])
    elif filter == "mech":
        for i in deck["patrol"]:
            ids.append(i["id"])

        for i in range(len(q)):
            if i not in ids:
                ret.append(0)
            else:
                ret.append(q[i])
    return ret

def find_id(card, model_deck):
    for i in range(len(model_deck["all cards"])):
        if card["id"] == model_deck["all cards"][i]["id"]:
            return i

def random_action(model_deck):

    deploy = np.zeros(len(model_deck["all cards"]))
    mission = 0
    heal_mech = 0
    attack = 0
    move_mech = np.zeros(len(model_deck["all cards"]))

    for i in range(len(model_deck["hand"])):
        if "Mission" not in model_deck["hand"][i]["Card Type"]:
            choi = int(np.random.choice([0, 1], 1))

            if choi == 1:
                deploy[find_id(model_deck["hand"][i], model_deck)] = 1

    avail = []
    for i in model_deck["hand"]:
        if "Mission" in i:
            avail.append(i)
    if len(avail) > 0:
        choi = np.random.choice(avail, 1)
        mission = find_id(choi, model_deck)

    if len(model_deck["patrol"]) > 0:
        choi = int(np.random.choice(len(model_deck["patrol"])))
        heal_mech = find_id(model_deck["patrol"][choi], model_deck)

    elif len(model_deck["gaurd"]) > 0:
        choi = int(np.random.choice(len(model_deck["gaurd"])))
        heal_mech = find_id(model_deck["gaurd"][choi], model_deck)

    choi = int(np.random.choice([0,1], 1))
    attack = choi

    for i in range(len(model_deck["gaurd"])):
        choi = int(np.random.choice([0, 1], 1))

        if choi == 1:
            move_mech[find_id(model_deck["gaurd"][i], model_deck)] = 1

    for i in range(len(model_deck["patrol"])):
        choi = int(np.random.choice([0, 1], 1))

        if choi == 1:
            move_mech[find_id(model_deck["patrol"][i], model_deck)] = 1

    return [deploy, mission, heal_mech, attack, move_mech]

def unflatten_list(arr):
    norm_list = []
    struct = [60, 1, 1, 1, 60]
    i = 0
    for size in struct:
        norm_list.append(arr[i:i + size])
        i += size
    return norm_list

def flatten_list(arr):
    flattened = []
    for item in arr:
        if isinstance(item, (list, tuple, np.ndarray)):
            flattened.extend(flatten_list(item))
        elif torch.is_tensor(item):
            flattened.extend(item.numpy().flatten())  # Convert tensor to a NumPy array and flatten it
        else:
            flattened.append(item)
    return flattened

def select_action(env, state, steps_done, policy_net, model_deck):
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * np.exp(-1 * steps_done / EPS_DECAY)

    steps_done += 1
    
    if sample > eps_threshold:
        with torch.no_grad():
            dec = policy_net(state)
            action = []
            for i in range(len(dec)):
                q_vals = dec[i]
                #print(len(q_vals.numpy().tolist()[0]), "\n")
                if type(q_vals.numpy().tolist()[0]) == list:
                    q_vals = q_vals.numpy().tolist()[0]
                else:
                    q_vals = q_vals.numpy().tolist()
                if i == 0:   # deploy action
                    chosen = []
                    q_vals = np.array(filter_q(model_deck, q_vals))

                    for i in q_vals:
                        if i > 0.5:
                            chosen.append(1)
                        else:
                            chosen.append(0)
                    action.append(chosen)
                elif i == 1:   # mission action
                        
                    q_vals = filter_q(model_deck, q_vals, "mission")

                    action.append([np.argmax(q_vals)])
                elif i == 2:   # heal_mech action
                    q_vals = filter_q(model_deck, q_vals, "mech")

                    action.append([np.argmax(q_vals)])
                elif i == 3:   # attack action
                    action.append([np.argmax(q_vals)])
                elif i == 4:   # move_mech
                    chosen = []
                    q_vals = filter_q(model_deck, q_vals, "mech")

                    for i in q_vals:
                        if i > 0.5:
                            chosen.append(1)
                        else:
                            chosen.append(0)
                    action.append(chosen)
            action = flatten_list(action)
            #print(action)
            return action
    else:
        
        sample_action = random_action(model_deck)
        
        action = [
            sample_action[0],
            sample_action[1],
            sample_action[2],
            sample_action[3],
            sample_action[4]
        ]
        #print(type(action))
        #action = torch.tensor(action)
        return action

def convertToDict(action):
    if len(action) > 5:
        naction = unflatten_list(action)
        #print(naction)
        
        action_dict = {
            'deploy': naction[0],
            'mission': naction[1][0],
            'heal_mech': naction[2][0],
            'attack': naction[3][0],
            'move_mech': naction[4]
        }
    else:
        naction = action
        action_dict = {
            'deploy': naction[0],
            'mission': naction[1],
            'heal_mech': naction[2],
            'attack': naction[3],
            'move_mech': naction[4]
        }
    return action_dict

def populate_arr(arr, desired_shape = (128, 5)):
    reshaped_array = np.zeros(desired_shape)

    for i, row in enumerate(arr):
        if len(row) == 1:
            reshaped_array[:, i] = row[0]
        elif len(row) == 128:
            reshaped_array[:, i] = row
    return reshaped_array

def optimize_model(policy_net, target_net, optimizer, memory, n_obs, model_deck):
    if len(memory) < BATCH_SIZE:
        return 0

    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
    
    desired_shape = (1, n_obs)
    processed_states = [state.view(desired_shape) for state in batch.state]
    state_batch = torch.cat(processed_states, dim=0)
    processed_states = []
    for i in batch.action:
        processed_states.append(torch.tensor(flatten_list(i)))
    action_batch = torch.cat(processed_states)
    reward_batch = torch.cat(batch.reward)
    state_action_values = policy_net(state_batch)
    deploy, mission, heal_mech, attack, move_mech = state_action_values
    deploy = deploy.unsqueeze(0)
    arr = [
        deploy,
        mission,
        heal_mech,
        attack,
        move_mech
    ]
    next_state_values = torch.zeros(BATCH_SIZE, len(arr), device=device)
    with torch.no_grad():
        dec = target_net(torch.tensor(np.array(non_final_next_states).reshape(128, 3150)))
        actions = []
        for i in range(len(dec)):
            q_vals = dec[i].numpy().tolist()[0]
            if i == 0:
                chosen = []
                q_vals = np.array(filter_q(model_deck, q_vals))
                for val in q_vals:
                    chosen.append(1 if val > 0.5 else 0)
                actions.append(chosen)
            elif i in [1, 2]:
                q_vals = filter_q(model_deck, q_vals, "mission" if i == 1 else "mech")
                actions.append([np.argmax(q_vals)])
            elif i == 3:
                actions.append([np.argmax(q_vals)])
            elif i == 4:
                chosen = []
                q_vals = filter_q(model_deck, q_vals, "mech")
                for val in q_vals:
                    chosen.append(1 if val > 0.5 else 0)
                actions.append(chosen)

        act = populate_arr(actions)
        actions_tensor = torch.tensor(act, dtype=torch.float, device=device)
        next_state_values[non_final_mask] = actions_tensor

    expected_state_action_values = (next_state_values * GAMMA) + reward_batch.unsqueeze(1)
    criterion = nn.SmoothL1Loss()
    filled = [pad_tensor(tensor,(1, 5)) for tensor in state_action_values]
    filled = torch.stack(filled)
    filled = filled.mean(dim=0)
    #print(filled.shape, expected_state_action_values.shape)
    loss = criterion(filled, expected_state_action_values)
    #print(expected_state_action_values)
    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()
    return loss.item()

