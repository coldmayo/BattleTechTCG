import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class DQN(nn.Module):
    def __init__(self, n_obs, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_obs, 128)
        self.layer2 = nn.Linear(128, 128)
        self.deploy = nn.Linear(128, n_actions[0])
        self.mission = nn.Linear(128, n_actions[1])
        self.heal_mech = nn.Linear(128, n_actions[2])
        self.attack = nn.Linear(128, n_actions[3])
        self.move_mech = nn.Linear(128, n_actions[4])

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))

        deploy_action = torch.sigmoid(self.deploy(x))
        mission_action = self.mission(x)
        heal_mech_action = self.heal_mech(x)
        attack_action = self.attack(x)
        move_mech_action = torch.sigmoid(self.move_mech(x))
        decs = [deploy_action, mission_action, heal_mech_action, attack_action, move_mech_action]

        return decs
