"""
    Load kivy screens data from json
"""
import os
import json
import importlib


data_screen_dict = {}


def load_screen_json(data_file="screens_data.json"):
    """Load screens data from json"""

    with open(os.path.join(os.path.dirname(__file__), data_file)) as read_file:
        all_data = json.load(read_file)
        data_screens = list(all_data.keys())

    for key in all_data:
        if all_data[key]['Import']:
            import_data = all_data.get(key)['Import']
            import_to = import_data.split("import")[1].strip()
            import_from = import_data.split("import")[0].split('from')[1].strip()
            data_screen_dict[import_to] = importlib.import_module(import_from, import_to)
    return data_screens, all_data, data_screen_dict, 'success'
