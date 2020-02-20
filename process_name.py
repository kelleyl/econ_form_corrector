import re
import editdistance
import argparse

fund_gs_list = ["test1", "test2", "test3", "dfasdf","sadfsa","asdfas"]
e_dict = {"Cp":"cap", " cp":"cap"}

def expand_name(name, exp_dict=e_dict):
    for k in exp_dict:
        if k in name:
            name = name.replace(k, exp_dict[k])
    return name

def score(fund, word):
    s = 0
    for i in range(min(len(fund), len(word))):
        if fund[i] == word[i]:
            s += 1
        else:
            break
    return s

def get_matches(fund, fund_list, num_matches=5):
    score_list = [(w, editdistance.eval(fund, w)) for w in fund_list if w.startswith(fund[0])]
    score_list = [(w, s-score(fund, w)) for (w, s) in score_list]
    score_list.sort(key=lambda x: x[1])
    return (score_list[:num_matches])

def expand_list(fund_list, exp_dict):
    return list(map(lambda x: expand_name(x, exp_dict), fund_list))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("fund_name")

    args = vars(ap.parse_args())
    fund_name = args["fund_name"]
    get_matches(fund_name)

    print(expand_name("hello"))
    print(expand_name("fund cp"))
    print(expand_name("fundcp"))