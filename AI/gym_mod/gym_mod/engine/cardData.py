import json
import pandas as pd
import re

"""
Data from: https://www.sarna.net/files/info/data/ccg/card_data/commanders_edition.zip

columns:
    id: unique id for the card
    card title: name of the card
    card type: Card type listed on the card
    Speed: slow
    Cost: [base cost, Assembly, Logistics, Munitions, Tactics, Politics]
    arm/str/att: [Base Armor Value, Base Structure Value, Base Attack Value]
    asset: what asset the card provides
    Rarity: rarity of the card
"""

def main():
    card_data = {"id": [], "Card Title": [], "Card Type": [], "Speed": [], "Cost": [], "Arm/Str/Att": [], "curr str": [], "Mass": [], "Asset": [], "Rarity": []}
    #keys = ["Speed", "Cost", ""]
    with open('commanders_edition.txt', mode = 'r', encoding = "unicode-escape") as f:
        content = f.read()
        cards = content.split('Card Title')[1:]
        #print(cards)

    for i, card in enumerate(cards):
        card_data['id'].append(i)

        lines = ['Card Title:' + card.strip()][0].split('\n')
        for line in lines:
            if ':' in line:

                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                #print(key)
                if key == 'Card Title':
                    val = value[3:]
                    card_data['Card Title'].append(val)
                    splitname = val.split(" ")
                    #print(value)
                    if splitname[0] == "Support:":
                        card_data["Asset"].append(splitname[1])
                    else:
                        card_data["Asset"].append(0)
                elif key == 'Card Type':
                    card_data['Card Type'].append(value.split(" - "))
                elif key == 'Speed':
                    card_data['Speed'].append(value)
                elif key == 'Cost':
                    toSave = [0, 0, 0, 0, 0, 0]
                    costSplit = value.split('+')

                    for cost in costSplit:
                        if cost[-1].isnumeric():
                            toSave[0] = int(cost)
                        else:
                            if cost[-1] == 'A':
                                toSave[1] = int(cost[:-1])
                            elif cost[-1] == 'L':
                                toSave[2] = int(cost[:-1])
                            elif cost[-1] == 'M':
                                toSave[3] = int(cost[:-1])
                            elif cost[-1] == 'T':
                                toSave[4] = int(cost[:-1])
                            elif cost[-1] == 'P':
                                toSave[5] = int(cost[:-1])
                                
                    card_data['Cost'].append(toSave)
                elif key == 'Arm/Str/Att':
                    toSave = [0, 0, 0]
                    armSplit = value.split('/')
                    j = 0
                    
                    for val in armSplit:
                        if val == '(n':
                            j += 1
                        elif val[0] == '+' or val[0] == '-':
                            toSave[j] = int(val[1])
                            j += 1
                        elif val != 'a)' and val != '(n':
                            #print(val)
                            toSave[j] = int(val)
                            j += 1

                    card_data['Arm/Str/Att'].append(toSave)
                    card_data["curr str"].append(toSave[1]+toSave[0])

                elif key == 'Mass':
                    card_data['Mass'].append(value)
                elif key == 'Rarity':
                    card_data['Rarity'].append(value)

        for j in card_data.keys():
            if len(card_data[j]) < i + 1:
                card_data[j].append(0)

    for j in card_data.keys():
        print(j, len(card_data[j]))
    print(card_data)
    with open('cardData.json', 'w+') as f:
        json.dump(card_data, f)

if __name__ == "__main__":
    main()
