def dictToArr(dic):
    ret = []
    for key in dic.keys():
        for i in dic[key]:
            ret.append(i)
    return ret
