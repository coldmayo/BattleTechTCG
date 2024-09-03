import json

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

    f = open('commanders_edition.txt', mode = 'r', encoding = "unicode-escape")
    lines = f.readlines()
    f.close()

    i = -1

    for line in lines:
        
        if line[0:13] == "Card Title:  ":
            i += 1
            name = line[13:len(line)-1]
            card_data["id"].append(i)
            card_data["Card Title"].append(name)

            splitname = name.split(' ')

            if splitname[0] == "Support:":
                card_data["Asset"].append(splitname[1])
            else:
                card_data["Asset"].append(0)
            
            if i != 0:
                for keys in card_data.keys():
                    if len(card_data["id"]) != len(card_data[keys]):
                        card_data[keys].append(0)

        elif line[0:13] == "Card Type:   ":
            types = line[13:len(line)-1].split(" - ")
            card_data["Card Type"].append(types)
        elif line[0:13] == "Cost:        ":
            toSave = [0, 0, 0, 0, 0, 0]
            costSplit = line[13:len(line)-1].split("+")

            for cost in costSplit:
                if len(cost) == 1:
                    toSave[0] = int(cost)
                elif cost[1] == 'A':
                    toSave[1] = int(cost[0])
                elif cost[1] == 'L':
                    toSave[2] = int(cost[0])
                elif cost[1] == 'M':
                    toSave[3] = int(cost[0])
                elif cost[1] == 'T':
                    toSave[4] = int(cost[0])
                elif cost[1] == 'P':
                    toSave[5] = int(cost[0])
                    
            card_data["Cost"].append(toSave)
        elif line[0:13] == "Arm/Str/Att: ":
            toSave = [0, 0, 0]
            armSplit = line[13:len(line)-1].split("/")
            j = 0
            for val in armSplit:
                #print(val)
                if val == '(n':
                    j += 1
                elif val[0] == '+' or val[0] == '-':
                    toSave[j] = int(val[1])
                    j += 1
                elif val != 'a)' and val != '(n':
                    #print(val)
                    toSave[j] = int(val)
                    j += 1
            card_data["Arm/Str/Att"].append(toSave)
            card_data["curr str"].append(toSave[1]+toSave[0])
        elif line[0:13] == "Rarity:      ":
            card_data["Rarity"].append(line[13:len(line)-1])
        elif line[0:13] == "Mass:        ":
            mass = line[13:len(line)-1].split(' ')
            card_data["Mass"].append(int(mass[0]))

    with open('cardData.json', 'w+') as f:
        json.dump(card_data, f)

if __name__ == "__main__":
    main()
