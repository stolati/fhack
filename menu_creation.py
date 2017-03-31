import os, os.path
import io
import pickle

menu = {}


line_items = pickle.load(io.open('line_item_pkls/THEBURGERBARNMANVEL_line_items.pkl', 'r', encoding='utf-8'))

for item in line_items:
    main_item = item["main item"]
    if main_item in menu:
        menu[main_item]["sub_items"].update(set(item["sub items"]))
    else:
        cur_item = {
            "price": item["cost"],
            "sub_items": set(item["sub items"])
        }
        menu[main_item] = cur_item

for key in menu:
    #print key
    item = menu[key]
    #print item["price"]

    item_list = ""
    for sub_item in item["sub_items"]:
       item_list += " " + sub_item.strip()

    print item_list
    #print "\n"
