import gymnasium as gym
from gymnasium import spaces
import numpy as np

"""
decks:
    stockpile
    hand
    construction
    command post
    scrap heap
"""

class BattleTechEnv(gym.Env):
    def __init__(self, model_cards, enemy_cards):
        self.turn = 0
        self.model_deck = {"stock": model_cards[6:], "hand": model_cards[0:5], "const": [], "comm post": [], "scrap heap": [], "gaurd": [], "patrol": [], "all cards": model_cards}
        self.enemy_deck = {"stock": enemy_cards[6:], "hand": enemy_cards[0:5], "const": [], "comm post": [], "scrap heap": [], "gaurd": [], "patrol": [], "all cards": enemy_cards}
        self.model_counter = []
        self.enemy_counter = []
        self.model_tap = []
        self.enemy_tap = []
        self.done = 0
        self.attacksToResolve = {"model": 0, "enemy": 0}
        self.in_battle = [0, "none", "none"]  # battle num, model name, enemy name 
        self.action_space = spaces.Dict({
            'deploy': spaces.MultiBinary(60),   # 24 mechs in a deck and 24 is the amount of resources in the deck
            'mission': spaces.Discrete(60),   # rest might be mission cards
            'heal_mech': spaces.Discrete(60),   # model chooses mech to heal
            'attack': spaces.Discrete(1),   # if/where to attack (0: no attack, 1: attack stockpile)
            'move_mech': spaces.MultiBinary(60)   # this specifies which mechs will be switched from patrol to gaurd or vice versa
        })

        self.observation_space = spaces.Dict({
            'hand': spaces.Box(low=0, high=350, shape=(60,)),   # cards in the players hand
            'stockpile': spaces.Box(low=0, high=350, shape=(60,)),   # cards in the stockpile
            'construction': spaces.Box(low=0, high=350, shape=(24,)),   # mechs in construction
            'command post': spaces.Box(low=0, high=350, shape=(24,)),   # cards in the command post
            'scrap heap': spaces.Discrete(60),   # number of cards in the scrap heap
            'patrol': spaces.Box(low=0, high=350, shape=(24,)),   # mechs in patrol
            'guard': spaces.Box(low=0, high=350, shape=(24,)),   # mechs in gaurd
            'comm post': spaces.Box(low=0, high=350, shape=(24,)),
            'enemy patrol': spaces.Box(low=0, high=350, shape=(24,)),   # mechs in enemy's patrol
            'enemy gaurd': spaces.Box(low=0, high=350, shape=(24,))   # mechs in enemy's gaurd
        })

        self.state = self.update_obs().values()

    def reset(self):
        self.done = 0
        self.model_counter = []
        self.enemy_counter = []
        self.in_battle = [0, "none", "none"]
        self.model_deck = {"stock": self.model_deck["all cards"][6:], "hand": self.model_deck["all cards"][0:5], "const": [], "comm post": [], "scrap heap": [], "gaurd": [], "patrol": [], "all cards": self.model_deck["all cards"]}
        self.enemy_deck = {"stock": self.enemy_deck["all cards"][6:], "hand": self.enemy_deck["all cards"][0:5], "const": [], "comm post": [], "scrap heap": [], "gaurd": [], "patrol": [], "all cards": self.enemy_deck["all cards"]}
        return self.update_obs()

    def update_obs(self):
        self.state = {
            'hand': [],
            'stock': [],
            'const': [],
            'comm post': [],
            'scrap heap': [],
            'patrol': [],
            'gaurd': [],
            'enemy patrol': [],
            'enemy gaurd': []
        }
        
        for i in range(350):
            if i == 0:
                self.state["scrap heap"].append(len(self.model_deck["scrap heap"]))
            else:
                self.state["scrap heap"].append(-1)
            if len(self.model_deck["hand"]) > i:
                self.state["hand"].append(self.model_deck["hand"][i]["id"])
            else:
                self.state['hand'].append(-1)

            if len(self.model_deck["stock"]) > i:
                self.state["stock"].append(self.model_deck["stock"][i]["id"])
            else:
                self.state["stock"].append(-1)
                
            if len(self.model_deck["const"]) > i:
                self.state["const"].append(self.model_deck["const"][i]["id"])
            else:
                self.state["const"].append(-1)

            if len(self.model_deck["comm post"]) > i:
                self.state["comm post"].append(self.model_deck["comm post"][i]["id"])
            else:
                self.state["comm post"].append(-1)
                
            if len(self.model_deck["gaurd"]) > i:
                self.state["gaurd"].append(self.model_deck["gaurd"][i]["id"])
            else:
                self.state["gaurd"].append(-1)

            if len(self.model_deck["patrol"]) > i:
                self.state["patrol"].append(self.model_deck["patrol"][i]["id"])
            else:
                self.state["patrol"].append(-1)
                
            if len(self.enemy_deck["patrol"]) > i:
                self.state["enemy patrol"].append(self.enemy_deck["patrol"][i]["id"])
            else:
                self.state["enemy patrol"].append(-1)
                
            if len(self.enemy_deck["gaurd"]) > i:
                self.state["enemy gaurd"].append(self.enemy_deck["gaurd"][i]["id"])
            else:
                self.state["enemy gaurd"].append(-1)
                
        return self.state

    def move_card(self, deck, pile1, pile2, i):
        try:
            if type(i) == int:
                deck[pile2].append(deck[pile1][i])
                del deck[pile1][i]
            elif type(i) == list:
                for item in sorted(i, reverse=True):
                    deck[pile2].append(deck[pile1][item])
                    del deck[pile1][item]
            return deck
        except IndexError:
            return deck

    def check_game(self):
        if len(self.model_deck["stock"]) <= 0:
            self.done = -1
        elif len(self.enemy_deck["stock"]) <= 0:
            self.done = 1
        else:
            self.done = 0

    def draw_phase(self, player):
        if player == "model":
            try:
                self.model_deck = self.move_card(self.model_deck, "stock", "hand", 0)
                self.model_deck = self.move_card(self.model_deck, "stock", "hand", 0)
                return self.model_deck
            except IndexError:
                return -1
        elif player == "enemy":
            try:
                self.enemy_deck = self.move_card(self.model_deck, "stock", "hand", 0)
                self.enemy_deck = self.move_card(self.model_deck, "stock", "hand", 0)
                return self.enemy_deck
            except IndexError:
                return 1
            

    def step(self, action):   # model turn
        if self.in_battle[0] >= 0:
            # cards are drawn from the stockpile before this function runs (check out train.py)
            # untap phase
            reward = 0
            self.model_tap = []   # untap all cards

            # deploy
            toDeploy = action["deploy"]
            toMove = []
            for i in range(len(toDeploy)):
                card = self.model_deck["all cards"][i]
                if "'Mech" in card["Card Type"] and toDeploy[i] == 1:
                    for j in range(len(self.model_deck["hand"])):
                        if self.model_deck["hand"][j]["id"] == card["id"]:
                            #self.model_deck = self.move_card(self.model_deck, "hand", "const", j)
                            toMove.append(j)
                            max = card["Cost"][0]
                            self.model_counter.append([card["id"], 1, max, j])   # TODO: make the assets do something
                    self.model_deck = self.move_card(self.model_deck, "hand", "const", toMove)
                    
                elif "Command" in card["Card Type"] and toDeploy[i] == 1:
                    for j in range(len(self.model_deck["hand"])):
                        if self.model_deck["hand"][j]["id"] == card["id"]:
                            #self.model_deck = self.move(self.model_deck, "hand", "comm post", j)
                            toMove.append(j)
                    self.model_deck = self.move_card(self.model_deck, "hand", "comm post", toMove)

            # repair/reload phase

            if len(self.model_deck["patrol"]) > 0 and "Support: Assembly" in self.model_deck["comm post"]:
                for i in self.model_deck["patrol"]:
                    if i["id"] == self.model_deck["all cards"][action["heal_mech"]]["id"]:
                        if i["curr str"] < i["Arm/Str/Att"][1]:
                            i["curr str"] += 1

            if len(self.model_deck["gaurd"]) > 0 and "Support: Assembly" in self.model_deck["comm post"]:
                for i in self.model_deck["gaurd"]:
                    if i["id"] == self.model_deck["all cards"][action["heal_mech"]]["id"]:
                        if i["curr str"] < i["Arm/Str/Att"][1]:
                            i["curr str"] += 1
            # missions
            # make sure units are on patrol to launch attack, but we also need some units gaurding
            for i in range(len(action["move_mech"])):
                card = self.model_deck["all cards"][i]["id"]
                toMove = []
                for j in range(len(self.model_deck["patrol"])):
                    if card == self.model_deck["patrol"][j]["id"] and action["move_mech"][i] == 1:
                        toMove.append(j)
                        #self.move_card(self.model_deck, "patrol", "gaurd", j)

                self.model_deck = self.move_card(self.model_deck, "patrol", "gaurd", toMove)

                for j in range(len(self.model_deck["gaurd"])):
                    if card == self.model_deck["gaurd"][j]["id"] and action["move_mech"][i] == 1:
                        #self.move_card(self.model_deck, "gaurd", "patrol", j)
                        toMove.append(j)
                self.model_deck = self.move_card(self.model_deck, "gaurd", "patrol", toMove)
                
            if action["attack"] >= 1:
                if len(self.model_deck["patrol"]) > 0:
                    if action["attack"] == 1:
                        if len(self.enemy_deck["gaurd"]) == 0:
                            attack = 0
                            for i in self.model_deck["patrol"]:
                                attack += i["Arm/Str/Att"][2]
                            for i in range(attack):
                                self.enemy_deck = self.move_card(self.enemy_deck, "stock", "scrap heap", 0)
                        else:
                            # battle starts
                            self.in_battle[0] = 1
                            self.in_battle[1] = "patrol"
                            self.in_battle[2] = "gaurd"
                            # determine initiative
                            # model does not have initiative:
                            if len(self.model_deck["patrol"]) < len(self.enemy_deck["gaurd"]):
                                for i in self.model_deck["patrol"]:
                                    self.attacksToResolve["model"] += i["Arm/Str/Att"][2]
                                self.in_battle[0] += 1
                else:
                    reward -= 0.5

            # add counters
            for i in self.model_counter:
                i[1] += 1
                if i[1] == i[2]:
                    self.model_deck = self.move_card(self.enemy_deck, "const", "patrol", i[3])

        else:
            
            if self.in_battle[0] < 3:
                for i in self.model_deck[self.in_battle[1]]:
                    self.attacksToResolve["model"] += i["Arm/Str/Att"][2]
                self.in_battle[0] += 1

            if self.in_battle[0] == 3 and self.in_battle[1] == "patrol":
                # resolve damage
                self.model_deck[self.in_battle[1]][0]["curr str"] -= self.attacksToResolve["enemy"]
                self.enemy_deck[self.in_battle[2]][0]["curr str"] -= self.attacksToResolve["model"]

                # scrap dead mechs
                if self.model_deck[self.in_battle[1]][0]["curr str"] <= 0:
                    self.model_deck = self.move_card(self.model_deck, self.in_battle[1], "scrap heap", 0)
                elif self.enemy_deck[self.in_battle[2]][0]["curr str"] <= 0:
                    self.enemy_deck = self.move_card(self.enemy_deck, self.in_battle[2], "scrap heap", 0)

                # combat is now over
                self.in_battle[0] = 0

        self.check_game()
        return self.update_obs(), reward, self.done, False, {}

    def enemyTurn(self):
        if self.in_battle[0] == 0:
            # this is basically a bot that does random actions, I want the model to train on this

            # untap phase
            self.enemy_tap = []

            # deploy
            
            for i in range(len(self.enemy_deck["hand"])):
                i = int(np.random.choice(len(self.enemy_deck["hand"]), 1))
                if "'Mech" in self.enemy_deck["hand"][i]["Card Type"]:
                    cost = self.enemy_deck["hand"][i]["Cost"][0]
                    id = self.enemy_deck["hand"][i]["id"]
                    self.enemy_deck = self.move_card(self.enemy_deck, "hand", "const", i)
                    self.enemy_counter.append([id, 1, cost, i])
                elif "Command" in self.enemy_deck["hand"][i]["Card Type"]: 
                    self.enemy_deck = self.move_card(self.enemy_deck, "hand", "comm post", i)

            # repair/reload phase (repair 1 mech per turn, if allowed)
            if len(self.enemy_deck["patrol"]) > 0 and "Support: Assembly" in self.enemy_deck["comm post"]:
                choi = np.random.choice(len(self.enemy_deck["patrol"]), 1)
                if self.enemy_deck["patrol"][choi] < self.enemy_deck["patrol"][choi]["Arm/Str/Att"][1]:
                    self.enemy_deck["patrol"][choi]["curr str"] += 1
                    
            elif len(self.enemy_deck["gaurd"]) > 0 and "Support: Assembly" in self.enemy_deck["comm post"]:
                choi = np.random.choice(len(self.enemy_deck["gaurd"]), 1)
                if self.enemy_deck["gaurd"][choi] < self.enemy_deck["gaurd"][choi]["Arm/Str/Att"][1]:
                    self.enemy_deck["gaurd"][choi]["curr str"] += 1

            # missions
            # move mechs around
            if len(self.enemy_deck["patrol"]) > 1:
                choi = int(np.random.choice(len(self.enemy_deck["patrol"]), 1))
                self.enemy_deck = self.move_card(self.enemy_deck, "patrol", "gaurd", choi)

            if len(self.enemy_deck["gaurd"]) > 1:
                choi = int(np.random.choice(len(self.enemy_deck["gaurd"]), 1))
                self.enemy_deck = self.move_card(self.enemy_deck, "gaurd", "patrol", choi)

            choi = np.random.choice(1, 1)
            if choi == 1 and len(self.enemy_deck["patrol"]):
                if choi == 1:
                    if len(self.model_deck["gaurd"]) == 0:
                        attack = 0
                        for i in self.enemy_deck["patrol"]:
                            attack += i["Arm/Str/Att"][2]
                        for i in range(attack):
                            self.model_deck = self.move_card(self.model_cards, "stock", "scrap heap", 0)
                    else:
                        # start battle
                        self.in_battle[0] = 1
                        self.in_battle[2] = "patrol"
                        self.in_battle[1] = "gaurd"
                        # determine initiative
                        if len(self.enemy_deck["patrol"]) < len(self.model_deck["gaurd"]):
                            for i in self.enemy_deck["patrol"]:
                                self.attacksToResolve["model"] += i["Arm/Str/Att"][2]
                            self.in_battle[0] += 1
            # add counters
            for i in range(len(self.enemy_counter)):
                self.enemy_counter[i][1] += 1
                if self.enemy_counter[i][1]  == self.enemy_counter[i][2]:
                    self.enemy_deck = self.move_card(self.enemy_deck, "const", "patrol", self.enemy_counter[i][3])
        else:
            if self.in_battle[0] < 3:
                for i in self.enemy_deck[self.in_battle[2]]:
                    self.attacksToResolve["model"] += i["Arm/Str/Att"][2]
                self.in_battle[0] += 1

            if self.in_battle[0] == 3 and self.in_battle[2] == "patrol":
                # resolve damage
                self.model_deck[self.in_battle[1]][0]["curr str"] -= self.attacksToResolve["enemy"]
                self.enemy_deck[self.in_battle[2]][0]["curr str"] -= self.attacksToResolve["model"]

                # scrap dead mechs
                if self.model_deck[self.in_battle[1]][0]["curr str"] <= 0:
                    self.model_deck = self.move_card(self.model_deck, self.in_battle[1], "scrap heap", 0)
                elif self.enemy_deck[self.in_battle[2]][0]["curr str"] <= 0:
                    self.enemy_deck = self.move_card(self.enemy_deck, self.in_battle[2], "scrap heap", 0)

                # combat is now over
                self.in_battle[0] = 0
                self.attacksToResolve["model"] = 0
                self.attacksToResolve["enemy"] = 0

        self.check_game()
        return self.done
