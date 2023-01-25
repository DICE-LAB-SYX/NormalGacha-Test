import json
import random
from re import sub
from typing import Dict, List, Set, Tuple

with open('./gacha_table.json', 'r', encoding='utf-8') as f:
    GACHA_TABLE = json.load(f)
with open('./character_table.json', 'r', encoding='utf-8') as f:
    CHARACTER_TABLE = json.load(f)


def parse_recruitable_chars(s: str) -> Set[str]:

    ret = set()
    min_pos = s.find("★" + r"\n")
    for rarity in range(1, 7):
        start_s = r"★" * rarity + r"\n"
        start_pos = s.find(start_s, min_pos) + len(start_s)
        end_pos = s.find("\n-", start_pos)
        if end_pos == -1:
            s2 = s[start_pos:]
        else:
            s2 = s[start_pos:end_pos]
        min_pos = end_pos
        s2 = sub(r"<.*?>", "", s2)
        sl = s2.split("/")
        for v in sl:
            ret.add(v.strip())

    return ret


def generate_recruitable_data() -> Tuple[Dict, Dict]:

    tag2name = {v["tagId"]: v["tagName"] for v in GACHA_TABLE["gachaTags"][:-2]}
    name2tag = {v: k for k, v in tag2name.items()}
    profession2tag = {
        "MEDIC": 4,
        "WARRIOR": 1,
        "PIONEER": 8,
        "TANK": 3,
        "SNIPER": 2,
        "CASTER": 6,
        "SUPPORT": 5,
        "SPECIAL": 7,
    }
    chars_list = {}
    char_data = {}

    recruitable = parse_recruitable_chars(GACHA_TABLE["recruitDetail"])

    for charId, value in CHARACTER_TABLE.items():
        if value["tagList"] is None:
            continue
        name = value["name"]

        if name not in recruitable:
            continue
        data = {
            "name": value["name"],
            "rarity": value["rarity"],
        }

        tags = [name2tag[tag_name] for tag_name in value["tagList"]]
        tags.append(11) if value["rarity"] == 5 else tags.append(14) if value["rarity"] == 4 else None
        tags.append(9) if value["position"] == "MELEE" else tags.append(10) if value["position"] == "RANGED" else None
        tags.append(profession2tag[value["profession"]])

        data["tags"] = tags
        char_data[charId] = data

    for char in char_data:
        if "char_" in char:
            chars_list.setdefault(char_data[char]["rarity"], [])
            chars_list[char_data[char]["rarity"]].append(char)

    return chars_list, char_data


def refresh_tag_list() -> List:

    rank_weights = {
        "6star": 0.210417,
        "5star": 0.523127,
        "4star": 14.988323,
        "3star": 81.11354,
        "2star": 1.51041,
        "1star": 0.554183
    }
    tags_set = []

    chars_list, char_data = generate_recruitable_data()
    ranks, probs = zip(*rank_weights.items())

    while len(tags_set) < 5:
        random_group = random.choices(ranks, probs, k=4)
        char_pool = [random.choice(chars_list[int(group[:1]) - 1]) for group in random_group]
        tags_set = list(set([tag for char in char_pool for tag in char_data[char]["tags"]]))

    tag_list = random.sample(tags_set, 5)
    tag_list.sort()

    tag2name = {v["tagId"]: v["tagName"] for v in GACHA_TABLE["gachaTags"][:-2]}
    for i in tag_list:
        print(tag2name[i])

    return tag_list


tag_list = refresh_tag_list()
