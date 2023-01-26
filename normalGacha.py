import json
import os
import random
from re import sub
from typing import Dict, List, Set, Tuple

with open('./gacha_table.json', 'r', encoding='utf-8') as f:
    GACHA_TABLE = json.load(f)
with open('./character_table.json', 'r', encoding='utf-8') as f:
    CHARACTER_TABLE = json.load(f)

player_data = {
    "track": {
        "recruit": {
            "pool": None
        }
    }
}


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
        "3star": 79.11354,
        "2star": 3.51041,
        "1star": 0.554183
    }
    tags_set = []

    chars_list, char_data = generate_recruitable_data()
    ranks, probs = zip(*rank_weights.items())

    while len(tags_set) < 5:
        random_group = random.choices(ranks, probs, k=15)
        char_pool = [random.choice(chars_list[int(group[:1]) - 1]) for group in random_group]
        tags_set = list(set([tag for char in char_pool for tag in char_data[char]["tags"]]))

    tag_list = random.sample(tags_set, 5)
    tag_list.sort()
    player_data["track"]["recruit"]["pool"] = char_pool

    tag2name = {v["tagId"]: v["tagName"] for v in GACHA_TABLE["gachaTags"][:-2]}
    print("-" * 20)
    for i in tag_list:
        print(tag2name[i])
    print("-" * 20)
    return tag_list


def generate_valid_tags(duration: int) -> tuple[str, List]:

    char_list, char_data = generate_recruitable_data()
    selected_tags = random.sample(tag_list, random.randint(0, 3))
    print(f"selected_tags：\t\t{selected_tags}\nduration：\t\t{duration}")
    if duration <= 13800:
        char_range = [0, 3]
    elif duration <= 27000:
        char_range = [1, 4]
    else:
        if 11 in selected_tags:
            char_range = [5, 5]
        elif 14 in selected_tags:
            char_range = [4, 4]
        else:
            char_range = [2, 4]

    char_pool = player_data["track"]["recruit"]["pool"]

    alternate_list = []
    for charId in char_pool:
        if char_range[0] <= char_data[charId]["rarity"] <= char_range[1]:
            alternate_list.append(charId)

    alternate_char_data = {k: v for k, v in char_data.items() if k in alternate_list}
    matching_chars = {char: alternate_char_data[char] for char in alternate_char_data if set(alternate_char_data[char]['tags']).intersection(set(selected_tags))}
    sorted_matching_chars = sorted(matching_chars.items(), key=lambda x: len(set(x[1]['tags']).intersection(set(selected_tags))), reverse=True)
    print(f"matching_chars：\t{sorted_matching_chars}")

    if len(selected_tags) == 1:
        compensation = 6.3 - (duration // 600 * 0.05)
        cross_tag = random.choices([0, 1], weights=[100 - compensation, compensation], k=1)[0]
        if cross_tag:
            sorted_matching_chars = []
            print("\033[1;31mcross_tag：\t\tTrue\033[0;0m")
        else:
            print("cross_tag：\t\tFalse")

    if len(sorted_matching_chars) == 0:
        char_range[1] += 1
        group_weights = [5 if rank == 0 else 15 if rank == 1 else 77 if rank == 2 else 2 if rank == 3 else 1 for rank in range(*char_range)]
        group = random.choices([rank for rank in range(*char_range)], group_weights, k=1)[0]
        all_chars = [char for char in char_list[group]]
        random_char_id = random.choice(all_chars)
    else:
        random_char_id = random.choice(sorted_matching_chars)[0]

    filter_tags = [x for x in selected_tags if x not in char_data[random_char_id]["tags"]]
    print(f"random_char_id：\t{random_char_id}\nfilter_tags：\t\t{filter_tags}")

    return random_char_id, filter_tags


if __name__ == "__main__":

    os.system("")

    for i in range(100):
        tag_list = refresh_tag_list()
        print(f"tag_list：\t\t{tag_list}")

        generate_valid_tags(3600 + 600 * random.randint(0, 48))
