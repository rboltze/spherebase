# -*- coding: utf-8 -*-

"""
Constants used for creating a star_map from a database

"""

path = "../../examples/resources/icons/"
icons = ["icon_man.png", "icon_woman.png", "icon_lgbt.png", "icon_baby_boy.png", "icon_baby_girl.png",
         "icon_young_boy.png", "icon_boy.png", "icon_girl_toddler.png", "icon_boy_toddler.png", "icon_girl.png",
         "icon_young_girl.png", "icon_old_man.png", "icon_old_woman.png"]

DICT_AGE_SEX = {1: {'min': 0, 'max': 2, 'sex': 'M', 'img': 'icon_baby_boy.png'},
    2: {'min': 0, 'max': 2, 'sex': 'F', 'img': 'icon_baby_girl.png'},
    3: {'min': 2, 'max': 4, 'sex': 'M', 'img': 'icon_boy_toddler.png'},
    4: {'min': 2, 'max': 4, 'sex': 'F', 'img': 'icon_girl_toddler.png'},
    5: {'min': 4, 'max': 9, 'sex': 'M', 'img': 'icon_young_boy.png'},
    6: {'min': 4, 'max': 9, 'sex': 'F', 'img': 'icon_young_girl.png'},
    7: {'min': 9, 'max': 17, 'sex': 'M', 'img': 'icon_boy.png'},
    8: {'min': 9, 'max': 17, 'sex': 'F', 'img': 'icon_girl.png'},
    9: {'min': 17, 'max': 65, 'sex': 'M', 'img': 'icon_man.png'},
    10: {'min': 17, 'max': 65, 'sex': 'F', 'img': 'icon_woman.png'},
    11: {'min': 65, 'max': 120, 'sex': 'M', 'img': 'icon_old_man.png'},
    12: {'min': 65, 'max': 120, 'sex': 'F', 'img': 'icon_old_woman.png'}}
