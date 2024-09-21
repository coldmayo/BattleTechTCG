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
        self.reward = 0
        
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

    def reset(self, model_deck = None, enemy_deck = None):
        self.done = 0
        self.model_counter = []
        self.enemy_counter = []
        self.in_battle = [0, "none", "none"]
        if model_deck != None:
            self.model_deck = {"stock": model_deck[6:], "hand": model_deck[0:5], "const": [], "comm post": [], "scrap heap": [], "gaurd": [], "patrol": [], "all cards": model_deck}
        else:
            self.model_deck = {"stock": self.model_deck["all cards"][6:], "hand": self.model_deck["all cards"][0:5], "const": [], "comm post": [], "scrap heap": [], "gaurd": [], "patrol": [], "all cards": self.model_deck["all cards"]}
        if enemy_deck != None:
            self.enemy_deck = {"stock": model_deck[6:], "hand": model_deck[0:5], "const": [], "comm post": [], "scrap heap": [], "gaurd": [], "patrol": [], "all cards": model_deck}
        else:
            self.enemy_deck = {"stock": self.enemy_deck["all cards"][6:], "hand": self.enemy_deck["all cards"][0:5], "const": [], "comm post": [], "scrap heap": [], "gaurd": [], "patrol": [], "all cards": self.enemy_deck["all cards"]}

        self.reward = 0
        
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

    def move_card(self, player, pile1, pile2, i):
        deck = self.model_deck if player == "model" else self.enemy_deck
        try:
            if isinstance(i, int):
                deck[pile2].append(deck[pile1][i])
                del deck[pile1][i]
            elif isinstance(i, list):
                for item in sorted(i, reverse=True):
                    deck[pile2].append(deck[pile1][item])
                    del deck[pile1][item]
        except IndexError:
            pass
        return deck

    def check_game(self):
        if len(self.model_deck["stock"]) == 0 and len(self.enemy_deck["stock"]) == 0:
            self.done = 0.5
            self.reward -= 0.1
        elif len(self.model_deck["stock"]) <= 0:
            self.done = -1
            self.reward -= 1
        elif len(self.enemy_deck["stock"]) <= 0:
            self.done = 1
            self.reward += 1
        else:
            self.done = 0

    def draw_phase(self, player):
        if self.in_battle[0] == 0:
            if player == "model":
                try:
                    self.model_deck = self.move_card("model", "stock", "hand", 0)
                    self.model_deck = self.move_card("model", "stock", "hand", 0)
                    return self.model_deck, self.reward, False
                except IndexError:
                    self.reward -= -1
                    return -1, self.reward, False
            elif player == "enemy":
                try:
                    self.enemy_deck = self.move_card("enemy", "stock", "hand", 0)
                    self.enemy_deck = self.move_card("enemy", "stock", "hand", 0)
                    return self.enemy_deck, self.reward, False
                except IndexError:
                    self.reward += 1
                    return 1, self.reward, False
        else:
            if player == "model":
                return self.model_deck, self.reward, True
            elif player == "enemy":
                return self.model_deck, self.reward, True

    def mechStatus(self):
        print("Model: ")
        print('patrol'+': ')
        for i in range(len(self.model_deck['patrol'])):
            print(self.model_deck['patrol'][i]["Card Title"], ":", self.model_deck['patrol'][i]["curr str"])
        print('gaurd'+': ')
        for i in range(len(self.model_deck['gaurd'])):
            print(self.model_deck['gaurd'][i]["Card Title"], ":", self.model_deck['gaurd'][i]["curr str"])

        print("Enemy: ")
        print('patrol'+': ')
        for i in range(len(self.enemy_deck['patrol'])):
            print(self.enemy_deck['patrol'][i]["Card Title"], ":", self.enemy_deck['patrol'][i]["curr str"])

        print('gaurd'+': ')
        for i in range(len(self.enemy_deck['gaurd'])):
            print(self.enemy_deck['gaurd'][i]["Card Title"], ":", self.enemy_deck['gaurd'][i]["curr str"])

        print("Enemy stockpile:", len(self.enemy_deck["stock"]), "Model stockpile:", len(self.model_deck["stock"]))

    def card_is_tapped(self, index, site, player):
        if player == "model":
            tapped = self.model_tap
        elif player == "enemy":
            tapped = self.enemy_tap

        for i in tapped:
            if i[0] == index and i[1] == site:
                return True
        return False

    def step(self, action):   # model turn
        if self.in_battle[0] == 0:
            # cards are drawn from the stockpile before this function runs (check out train.py)
            # untap phase
            reward = 0
            self.model_tap = []   # untap all cards

            # deploy
            toDeploy = action["deploy"]
            toMove1 = []
            toMove2 = []
            #print("The Model has the following cards in its hand:", self.model_deck["hand"])
            for i in range(len(toDeploy)):
                card = self.model_deck["all cards"][i]
                #print(card["Card Title"], card["Card Type"])
                if "'Mech" in card["Card Type"] and toDeploy[i] == 1 and "Command" not in card["Card Type"]:
                    for j in range(len(self.model_deck["hand"])):
                        if self.model_deck["hand"][j]["id"] == card["id"]:
                            #self.model_deck = self.move_card(self.model_deck, "hand", "const", j)
                            toMove1.append(j)
                            max = card["Cost"][0]+card["Cost"][1]+card["Cost"][2]+card["Cost"][3]+card["Cost"][4]+card["Cost"][5]
                            found = [0, 0, 0, 0, 0]
                            for k in range(len(self.model_deck['comm post'])):
                                com_c = self.model_deck["comm post"][k]
                                if com_c["Card Title"] == "Support: Assembly" and found[0] == 0 and self.card_is_tapped(k, "comm post", "model") == False:
                                    max -= card["Cost"][1]
                                    reward += 0.1
                                    found[0] = 1
                                    self.model_tap.append(["comm post", k])
                                    if card["Cost"][1] != 0:
                                        print("Model tapped Support: Assembly card")
                                elif com_c["Card Title"] == "Support: Logistics" and found[1] == 0 and self.card_is_tapped(k, "comm post", "model") == False:
                                    max -= card["Cost"][2]
                                    reward += 0.1
                                    found[1] = 1
                                    self.model_tap.append(["comm post", k])
                                    if card["Cost"][2] != 0:
                                        print("Model tapped Support: Logistics card")
                                elif com_c["Card Title"] == "Support: Munitions" and found[2] == 0 and self.card_is_tapped(k, "comm post", "model") == False:
                                    max -= card["Cost"][3]
                                    reward += 0.1
                                    found[2] = 1
                                    self.model_tap.append(["comm post", k])
                                    if card["Cost"][3] != 0:
                                        print("Model tapped Support: Munitions card")
                                elif com_c["Card Title"] == "Support: Tactics" and found[3] == 0 and self.card_is_tapped(k, "comm post", "model") == False:
                                    max -= card["Cost"][4]
                                    reward += 0.1
                                    found[3] = 1
                                    self.model_tap.append(["comm post", k])
                                    if card["Cost"][4] != 0:
                                        print("Model tapped Support: Tactics card")
                                elif com_c["Card Title"] == "Support: Politics" and found[4] == 0 and self.card_is_tapped(k, "comm post", "model") == False:
                                    max -= card["Cost"][5]
                                    reward += 0.1
                                    found[4] = 1
                                    self.model_tap.append(["comm post", k])
                                    if card["Cost"][5] != 0:
                                        print("Model tapped Support: Politics card")

                            print("Model starts construction on:", card["Card Title"], "with", max, "counters")
                            self.model_counter.append([card["id"], 0, max, len(self.model_counter)])   # TODO: make the assets do something
                    
                elif "Command" in card["Card Type"] and toDeploy[i] == 1:
                    for j in range(len(self.model_deck["hand"])):
                        if self.model_deck["hand"][j]["id"] == card["id"]:
                            print("Model deploys:", card["Card Title"])
                            #self.model_deck = self.move(self.model_deck, "hand", "comm post", j)
                            toMove2.append(j)

            self.model_deck = self.move_card("model", "hand", "const", toMove1)
            self.model_deck = self.move_card("model", "hand", "comm post", toMove2)

            # add counters from remaining resources
            toMove = []
            resources = 0
            for i in range(len(self.model_deck["comm post"])):
                if self.model_deck["comm post"][i]["Card Title"][0:7] == "Support" and self.card_is_tapped(i, "comm post", "model") == False:
                    resources += 1
            j = 0
            for i in range(resources):
                if len(self.model_counter) > j and len(self.model_counter) > 0:
                    self.model_counter[j][1] += 1
                    if self.model_counter[j][1]  == self.model_counter[j][2]:
                        for k in range(len(self.model_deck['const'])):
                            if self.model_counter[j][0] == self.model_deck['const'][k]['id']:
                                print("Model moved", self.model_deck["const"][k]["Card Title"], "to patrol")
                                self.model_counter.remove(self.model_counter[j])
                                toMove.append(k)
                                break
            self.model_deck = self.move_card("model", "const", "patrol", toMove)

            # repair/reload phase

            if len(self.model_deck["patrol"]) > 0 and "Support: Assembly" in self.model_deck["comm post"]:
                for i in self.model_deck["patrol"]:
                    if i["id"] == self.model_deck["all cards"][action["heal_mech"]]["id"]:
                        if i["curr str"] < i["Arm/Str/Att"][1]:
                            print("Model heals:", i["Card Title"])
                            i["curr str"] += 1

            if len(self.model_deck["gaurd"]) > 0 and "Support: Assembly" in self.model_deck["comm post"]:
                for i in self.model_deck["gaurd"]:
                    if i["id"] == self.model_deck["all cards"][action["heal_mech"]]["id"]:
                        if i["curr str"] < i["Arm/Str/Att"][1]:
                            print("Model heals:", i["Card Title"])
                            i["curr str"] += 1
            # missions
            # make sure units are on patrol to launch attack, but we also need some units gaurding
            for i in range(len(action["move_mech"])):
                card = self.model_deck["all cards"][i]["id"]
                toMove = []
                done = 0
                for j in range(len(self.model_deck["patrol"])):
                    if card == self.model_deck["patrol"][j]["id"] and action["move_mech"][i] == 1:
                        print("Model moves", self.model_deck["patrol"][j]["Card Title"], "to gaurd")
                        toMove.append(j)
                        done = 1
                        #self.move_card(self.model_deck, "patrol", "gaurd", j)

                self.model_deck = self.move_card("model", "patrol", "gaurd", toMove)

                if done == 0:
                    for j in range(len(self.model_deck["gaurd"])):
                        if card == self.model_deck["gaurd"][j]["id"] and action["move_mech"][i] == 1:
                            #self.move_card(self.model_deck, "gaurd", "patrol", j)
                            print("Model moves", self.model_deck["gaurd"][j]["Card Title"], "to patrol")
                            toMove.append(j)
                    self.model_deck = self.move_card("model", "gaurd", "patrol", toMove)
                
            if action["attack"] >= 1:
                print("Model attempts an attack")
                if len(self.model_deck["patrol"]) > 0:
                    if action["attack"] == 1:
                        self.reward += 0.5
                        if len(self.enemy_deck["gaurd"]) == 0:
                            print("No enemy mechs on gaurd, all damage goes to enemy stockpile")
                            attack = 0
                            for i in self.model_deck["patrol"]:
                                attack += i["Arm/Str/Att"][2]
                            print("Model did", attack, "damage to the enemy's stockpile")
                            #print(self.model_deck, "\n\n", self.enemy_deck, "\n")
                            for i in range(attack):
                                print(len(self.enemy_deck["stock"]), len(self.model_deck["stock"]))
                                self.enemy_deck = self.move_card("enemy", "stock", "scrap heap", 0)
                            self.mechStatus()
                        else:
                            print("Enemy mechs on gaurd, battle started")
                            self.mechStatus()
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
                    print("No mechs in patrol")
                    self.reward -= 0.1
            elif action["attack"] == 0 and len(self.model_deck["patrol"]) > 0:
                self.reward -= 0.5

            

        else:
            
            if self.in_battle[0] < 3:
                for i in self.model_deck[self.in_battle[1]]:
                    self.attacksToResolve["model"] += i["Arm/Str/Att"][2]
                self.in_battle[0] += 1

            if self.in_battle[0] == 3 and self.in_battle[1] == "patrol":
                # resolve damage
                # TODO distribute damage, allow the model to choose which enemy mech to target
                
                # resolve damage
                j = 0
                for i in range(self.attacksToResolve["enemy"]):
                    self.model_deck[self.in_battle[1]][j]["curr str"] -= 1
                    if self.model_deck[self.in_battle[1]][j]["curr str"] == 0:
                        j += 1
                        if j == len(self.model_deck[self.in_battle[1]]):
                            print("All Mechs gone, doing damage to Model stockpile...")
                            #self.model_deck = self.move_card(self.model_deck, "stock", "scrap heap", self.attacksToResolve["enemy"]-i)
                            for i in range(self.attacksToResolve["enemy"]-i):
                                self.model_deck = self.move_card("model", "stock", "scrap heap", 0)
                            break

                
                k = 0
                for i in range(self.attacksToResolve["model"]):
                    self.enemy_deck[self.in_battle[2]][k]["curr str"] -= 1
                    if self.enemy_deck[self.in_battle[2]][k]["curr str"] == 0:
                        k += 1
                        if k == len(self.enemy_deck[self.in_battle[2]]):
                            print("All Mechs gone, doing damage to Enemy stockpile...")
                            for i in range(self.attacksToResolve["model"]-i):
                                self.enemy_deck = self.move_card("enemy", "stock", "scrap heap", 0)
                            break

                # scrap dead mechs
                #self.enemy_deck = self.move_card(self.enemy_deck, self.in_battle[2], "scrap heap", k-1)
                #self.model_deck = self.move_card(self.model_deck, self.in_battle[1], "scrap heap", j-1)
                toMove = []
                for i in range(len(self.enemy_deck[self.in_battle[2]])):
                    if self.enemy_deck[self.in_battle[2]][i]["curr str"] <= 0:
                        #self.enemy_deck = self.move_card(self.enemy_deck, self.in_battle[2], "scrap heap", i)
                        print(self.enemy_deck[self.in_battle[2]][i]["Card Title"], "is getting scrapped")
                        toMove.append(i)
                self.enemy_deck = self.move_card("enemy", self.in_battle[2], "scrap heap", toMove)
                
                toMove = []
                for i in range(len(self.model_deck[self.in_battle[1]])):
                    if self.model_deck[self.in_battle[1]][i]["curr str"] <= 0:
                        #self.model_deck = self.move_card(self.model_deck, self.in_battle[1], "scrap heap", i)
                        toMove.append(i)
                        print(self.model_deck[self.in_battle[1]][i]["Card Title"], "is getting scrapped")

                self.model_deck = self.move_card("model", self.in_battle[1], "scrap heap", toMove)

                # combat is now over
                print("Model will do", self.attacksToResolve["model"], "damage")
                print("Enemy will do", self.attacksToResolve["enemy"], "damage")
                self.in_battle[0] = 0
                self.attacksToResolve["model"] = 0
                self.attacksToResolve["enemy"] = 0

                # show mechs and their current strength
                self.mechStatus()
        self.check_game()
        return self.update_obs(), self.reward, self.done, False, {}

    def enemyTurn(self):
        if self.in_battle[0] == 0:
            # this is basically a bot that does random actions, I want the model to train on this

            # untap phase
            self.enemy_tap = []

            # deploy
            #print("The Enemy has the following cards in its hand:", self.enemy_deck["hand"])
            for i in range(len(self.enemy_deck["hand"])):
                i = int(np.random.choice(len(self.enemy_deck["hand"]), 1))
                #print(self.enemy_deck["hand"][i]["Card Title"], self.enemy_deck["hand"][i]["Card Type"])
                if "'Mech" in self.enemy_deck["hand"][i]["Card Type"] and "Command" not in self.enemy_deck["hand"][i]["Card Type"]:
                    cost = 0
                    for n in range(len(self.enemy_deck["hand"][i]["Cost"])):
                        cost += n

                    found = [0, 0, 0, 0, 0]
                    
                    for k in range(len(self.enemy_deck["comm post"])):
                        card = self.enemy_deck["comm post"][k]
                        if card["Card Title"] == "Support: Assembly" and found[0] == 0 and self.card_is_tapped(k, "comm post", "enemy") == False:
                            cost -= self.enemy_deck["hand"][i]["Cost"][1]
                            found[0] = 1
                            self.enemy_tap.append(["comm post", k])
                            if self.enemy_deck["hand"][i]["Cost"][1] != 0:
                                print("Enemy tapped Support: Assembly")
                                
                        elif card["Card Title"] == "Support: Logistics" and found[1] == 0 and self.card_is_tapped(k, "comm post", "enemy") == False:
                            cost -= self.enemy_deck["hand"][i]["Cost"][2]
                            found[1] = 1
                            self.enemy_tap.append(["comm post", k])
                            if self.enemy_deck["hand"][i]["Cost"][2] != 0:
                                print("Enemy tapped Support: Logistics")
                                
                        elif card["Card Title"] == "Support: Munitions" and found[2] == 0 and self.card_is_tapped(k, "comm post", "enemy") == False:
                            cost -= self.enemy_deck["hand"][i]["Cost"][3]
                            found[2] = 1
                            self.enemy_tap.append(["comm post", k])
                            if self.enemy_deck["hand"][i]["Cost"][3] != 0:
                                print("Enemy tapped Support: Munitions")
                                
                        elif card["Card Title"] == "Support: Tactics" and found[3] == 0 and self.card_is_tapped(k, "comm post", "enemy") == False:
                            cost -= self.enemy_deck["hand"][i]["Cost"][4]
                            found[3] = 1
                            self.enemy_tap.append(["comm post", k])
                            if self.enemy_deck["hand"][i]["Cost"][4] != 0:
                                print("Enemy tapped Support: Tactics")
                                
                        elif card["Card Title"] == "Support: Politics" and found[4] == 0 and self.card_is_tapped(k, "comm post", "enemy") == False:
                            cost -= self.enemy_deck["hand"][i]["Cost"][5]
                            found[4] = 1
                            self.enemy_tap.append(["comm post", k])
                            if self.enemy_deck["hand"][i]["Cost"][5] != 0:
                                print("Enemy tapped Support: Politics")
                    id = self.enemy_deck["hand"][i]["id"]
                    print("Enemy starts construction on:", self.enemy_deck["hand"][i]["Card Title"], "with", cost, "counters")
                    self.enemy_deck = self.move_card("enemy", "hand", "const", i)
                    self.enemy_counter.append([id, 0, cost, i])
                elif "Command" in self.enemy_deck["hand"][i]["Card Type"]: 
                    print("Enemy deploys:", self.enemy_deck["hand"][i]["Card Title"])
                    self.enemy_deck = self.move_card("enemy", "hand", "comm post", i)


            # add counters from remaining resources
            toMove = []
            resources = 0
            for i in range(len(self.enemy_deck["comm post"])):
                if self.enemy_deck["comm post"][i]["Card Title"][0:7] == "Support" and self.card_is_tapped(i, "comm post", "enemy") == False:
                    resources += 1
            j = 0
            for i in range(resources):
                if len(self.enemy_counter) > j and len(self.enemy_counter) > 0:
                    self.enemy_counter[j][1] += 1
                    if self.enemy_counter[j][1]  == self.enemy_counter[j][2]:
                        for k in range(len(self.enemy_deck['const'])):
                            if self.enemy_counter[j][0] == self.enemy_deck['const'][k]['id']:
                                print("Enemy moved", self.enemy_deck["const"][k]["Card Title"], "to patrol")
                                self.enemy_counter.remove(self.enemy_counter[j])
                                toMove.append(k)
                                break
            self.enemy_deck = self.move_card("enemy", "const", "patrol", toMove)

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
                print("Enemy moved", self.enemy_deck["patrol"][choi]["Card Title"], "to gaurd")
                self.enemy_deck = self.move_card("enemy", "patrol", "gaurd", choi)
                
            if len(self.enemy_deck["gaurd"]) > 1:
                choi = int(np.random.choice(len(self.enemy_deck["gaurd"]), 1))
                print("Enemy moved", self.enemy_deck["gaurd"][choi]["Card Title"], "to patrol")
                self.enemy_deck = self.move_card("enemy", "gaurd", "patrol", choi)

            choi = np.random.choice(1, 1)
            if choi == 1 and len(self.enemy_deck["patrol"]):
                if choi == 1:
                    if len(self.model_deck["gaurd"]) == 0:
                        print("Model had no mechs in gaurd, enemy attacks the stockpile")
                        self.reward -= 0.5
                        attack = 0
                        for i in self.enemy_deck["patrol"]:
                            attack += i["Arm/Str/Att"][2]
                        print("Enemy does", attack, "damage to model's stockpile")
                        for i in range(attack):
                            self.model_deck = self.move_card("model", "stock", "scrap heap", 0)
                    else:
                        # start battle
                        print("Battle started...")
                        self.mechStatus()
                        self.in_battle[0] = 1
                        self.in_battle[2] = "patrol"
                        self.in_battle[1] = "gaurd"
                        # determine initiative
                        if len(self.enemy_deck["patrol"]) < len(self.model_deck["gaurd"]):
                            for i in self.enemy_deck["patrol"]:
                                self.attacksToResolve["model"] += i["Arm/Str/Att"][2]
                            self.in_battle[0] += 1

        else:
            if self.in_battle[0] < 3:
                for i in self.enemy_deck[self.in_battle[2]]:
                    self.attacksToResolve["enemy"] += i["Arm/Str/Att"][2]
                self.in_battle[0] += 1

            if self.in_battle[0] == 3 and self.in_battle[2] == "patrol":
                # resolve damage
                j = 0
                for i in range(self.attacksToResolve["enemy"]):
                    self.model_deck[self.in_battle[1]][j]["curr str"] -= 1
                    if self.model_deck[self.in_battle[1]][j]["curr str"] == 0:
                        j += 1
                        if j == len(self.model_deck[self.in_battle[1]]):
                            print("All Mechs gone, doing damage to Model stockpile...")
                            for i in range(self.attacksToResolve["enemy"]-i):
                                self.model_deck = self.move_card("model", "stockpile", "scrap heap", 0)
                            break

                
                k = 0
                for i in range(self.attacksToResolve["model"]):
                    self.enemy_deck[self.in_battle[2]][k]["curr str"] -= 1
                    if self.enemy_deck[self.in_battle[2]][k]["curr str"] == 0:
                        k += 1
                        if k == len(self.enemy_deck[self.in_battle[2]]):
                            print("All Mechs gone, doing damage to Enemy stockpile...")
                            for i in range(self.attacksToResolve["model"]-i):
                                self.enemy_deck = self.move_card("enemy", "stockpile", "scrap heap", 0)
                            break

                # scrap dead mechs

                toMove = []
                for i in range(len(self.enemy_deck[self.in_battle[2]])):
                    if self.enemy_deck[self.in_battle[2]][i]["curr str"] <= 0:
                        #self.enemy_deck = self.move_card(self.enemy_deck, self.in_battle[2], "scrap heap", i)
                        print(self.enemy_deck[self.in_battle[2]][i]["Card Title"], "is getting scrapped")
                        toMove.append(i)
                self.enemy_deck = self.move_card("enemy", self.in_battle[2], "scrap heap", toMove)
                
                toMove = []
                for i in range(len(self.model_deck[self.in_battle[1]])):
                    if self.model_deck[self.in_battle[1]][i]["curr str"] <= 0:
                        #self.model_deck = self.move_card(self.model_deck, self.in_battle[1], "scrap heap", i)
                        print(self.model_deck[self.in_battle[1]][i]["Card Title"], "is getting scrapped")
                        toMove.append(i)
                        
                self.model_deck = self.move_card("model", self.in_battle[1], "scrap heap", toMove)

                # show mechs and their current strength
                self.mechStatus()

                print("Enemy stockpile:", len(self.enemy_deck["stock"]), "Model stockpile:", len(self.model_deck["stock"]))
                # combat is now over
                self.in_battle[0] = 0
                self.attacksToResolve["model"] = 0
                self.attacksToResolve["enemy"] = 0

        self.check_game()
        return self.done, self.reward
