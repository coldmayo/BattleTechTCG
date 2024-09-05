import json
import os
import random
import numpy as np

def gen_deck(faction):

    cards = []

    with open(os.path.abspath("gym_mod/gym_mod/engine/cardData.json")) as j:
        card_data = json.loads(j.read())
        
    if faction.lower() == "kurita" or faction.lower() == "draconis combine":
        # find mechs (24 cards)
        mechs = []
        # find resources (24 cards)
        res = []
        # find missions (12 cards)
        miss = []
        for i in range(len(card_data['id'])):
            card_type = card_data["Card Type"][i]
            if card_type != 0:
                if "'Mech" in card_type and "Inner Sphere" in card_type:
                    if "Kurita" in card_type or ("Davion" not in card_type and "St. Ives" not in card_type and "Marik" not in card_type and "Liao" not in card_type and "Steiner" not in card_type and "ComStar" not in card_type):
                        mechs.append({"id": card_data["id"][i], "Card Title": card_data["Card Title"][i], "Card Type": card_data["Card Type"][i], "Speed": card_data["Speed"][i], "Cost": card_data["Cost"][i], "Arm/Str/Att": card_data["Arm/Str/Att"][i], "Rarity": card_data["Rarity"][i], "curr str": card_data["curr str"][i]})
                elif card_data["Asset"][i] != 0:
                    #if "Davion" not in card_type and "St. Ives" not in card_type and "Marik" not in card_type and "Liao" not in card_type and "Steiner" not in card_type and "ComStar" not in card_type:
                    res.append({"id": card_data["id"][i], "Card Title": card_data["Card Title"][i], "Asset": card_data["Asset"][i], "Card Type": card_data["Card Type"][i], "Speed": card_data["Speed"][i], "Cost": card_data["Cost"][i], "Arm/Str/Att": card_data["Arm/Str/Att"][i], "Rarity": card_data["Rarity"][i], "curr str": 0})
                elif "Mission" in card_type:
                    miss.append({"id": card_data["id"][i], "Card Title": card_data["Card Title"][i], "Asset": card_data["Asset"][i], "Card Type": card_data["Card Type"][i], "Speed": card_data["Speed"][i], "Cost": card_data["Cost"][i], "Arm/Str/Att": card_data["Arm/Str/Att"][i], "Rarity": card_data["Rarity"][i], "curr str": 0})

    for i in np.random.choice(mechs, 24, replace = True):
        cards.append(i)
        
    for i in np.random.choice(res, 24, replace = True):
        cards.append(i)

    for i in np.random.choice(miss, 12, replace = True):
        cards.append(i)
    #print(random.shuffle(cards))
    shuffle_num = np.random.randint(0, 10)
    for i in range(shuffle_num):
        random.shuffle(cards)
    return cards

if __name__ == "__main__":
    gen_deck("kurita")
