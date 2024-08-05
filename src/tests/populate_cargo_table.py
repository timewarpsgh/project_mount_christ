import sys
import os
import json


PATH_TO_DIR = r'D:\data\code\python\project_mount_christ\src\server\models'
sys.path.append(PATH_TO_DIR)

from world_models import SESSION, CargoTemplate


hash_markets_price_details = {
    0  : {#iberia
        'Available_items' : {
            'Cheese'        : [ 30, 20 ],
            'Fish'          : [ 20, 10 ],
            'Olive Oil'   : [ 28, 10 ],
            'Wine'        : [ 36, 20 ],
            'Velvet'        : [ 80, 50 ],
            'Linen Cloth' : [ 50, 25 ],
            'Dye'           : [ 120, 50 ],
            'Arms'          : [ 120, 100 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 140 ],
            'Cinnamon' : [ 0, 120 ],
            'Pepper'   : [ 0, 80 ],
            'Nutmeg'   : [ 0, 95 ],
            'Pimento'  : [ 0, 60 ],
            'Ginger'   : [ 0, 55 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 220 ],
            'Tea'     : [ 0, 200 ],
            'Coffee'  : [ 0, 5 ],
            'Cacao'   : [ 0, 105 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 45 ],
            'Cheese'      : [ 30, 20 ],
            'Fish'        : [ 20, 10 ],
            'Grain'       : [ 0, 32 ],
            'Olive Oil' : [ 28, 10 ],
            'Wine'        : [ 36, 20 ],
            'Rock Salt' : [ 0, 65 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 180 ],
            'Cotton' : [ 0, 50 ],
            'Wool'   : [ 0, 75 ],
            'Flax'   : [ 0, 40 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 40 ],
            'Silk Cloth'   : [ 0, 220 ],
            'Wool Cloth'   : [ 0, 70 ],
            'Velvet'         : [ 80, 50 ],
            'Linen Cloth'  : [ 50, 25 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 280 ],
            'Amber'            : [ 0, 300 ],
            'Ivory'            : [ 0, 280 ],
            'Pearl'            : [ 0, 310 ],
            'Tortoise Shell' : [ 0, 120 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 1000 ],
            'Silver' : [ 0, 240 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 180 ],
            'Tin Ore'    : [ 0, 100 ],
            'Iron Ore'   : [ 0, 190 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 400 ],
            'Carpet'  : [ 0, 300 ],
            'Musk'    : [ 0, 120 ],
            'Perfume' : [ 0, 110 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 120, 50 ],
            'Porcelain'     : [ 0, 120 ],
            'Glassware'     : [ 0, 230 ],
            'Arms'          : [ 120, 100 ],
            'Wood'          : [ 0, 130 ],
        # },
    },

    1  : {# N Europe
        'Available_items' : {
            'Cheese'     : [ 25, 15 ],
            'Fish'       : [ 20, 10 ],
            'Grain'      : [ 20, 8 ],
            'Cotton'     : [ 45, 20 ],
            'Iron Ore' : [ 110, 70 ],
            'Porcelain'  : [ 90, 55 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 160 ],
            'Cinnamon' : [ 0, 130 ],
            'Pepper'   : [ 0, 140 ],
            'Nutmeg'   : [ 0, 110 ],
            'Pimento'  : [ 0, 55 ],
            'Ginger'   : [ 0, 70 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 250 ],
            'Tea'     : [ 0, 220 ],
            'Coffee'  : [ 0, 5 ],
            'Cacao'   : [ 0, 110 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 49 ],
            'Cheese'      : [ 25, 15 ],
            'Fish'        : [ 20, 10 ],
            'Grain'       : [ 20, 8 ],
            'Olive Oil' : [ 0, 38 ],
            'Wine'        : [ 0, 58 ],
            'Rock Salt' : [ 0, 65 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 240 ],
            'Cotton' : [ 45, 20 ],
            'Wool'   : [ 0, 60 ],
            'Flax'   : [ 0, 45 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 60, 35 ],
            'Silk Cloth'   : [ 0, 260 ],
            'Wool Cloth'   : [ 0, 90 ],
            'Velvet'         : [ 0, 90 ],
            'Linen Cloth'  : [ 0, 65 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 285 ],
            'Amber'            : [ 0, 305 ],
            'Ivory'            : [ 0, 290 ],
            'Pearl'            : [ 0, 320 ],
            'Tortoise Shell' : [ 0, 130 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 1100 ],
            'Silver' : [ 0, 260 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 170 ],
            'Tin Ore'    : [ 0, 110 ],
            'Iron Ore'   : [ 110, 70 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 400 ],
            'Carpet'  : [ 0, 350 ],
            'Musk'    : [ 0, 130 ],
            'Perfume' : [ 0, 130 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 0, 130 ],
            'Porcelain'     : [ 90, 55 ],
            'Glassware'     : [ 0, 225 ],
            'Arms'          : [ 0, 100 ],
            'Wood'          : [ 0, 100 ],
        # },
    },

    2  : {# Medit
        'Available_items' : {
            'Fish'          : [ 25, 10 ],
            'Grain'         : [ 18, 8 ],
            'Olive Oil'   : [ 30, 15 ],
            'Wine'          : [ 40, 20 ],
            'Cotton'        : [ 38, 15 ],
            'Wool'          : [ 65, 25 ],
            'Linen Cloth' : [ 50, 30 ],
            'Glass Beads' : [ 3, 2 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 150 ],
            'Cinnamon' : [ 0, 120 ],
            'Pepper'   : [ 0, 120 ],
            'Nutmeg'   : [ 0, 100 ],
            'Pimento'  : [ 0, 70 ],
            'Ginger'   : [ 0, 65 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 200 ],
            'Tea'     : [ 0, 200 ],
            'Coffee'  : [ 0, 5 ],
            'Cacao'   : [ 0, 95 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 48 ],
            'Cheese'      : [ 0, 40 ],
            'Fish'        : [ 25, 10 ],
            'Grain'       : [ 18, 8 ],
            'Olive Oil' : [ 30, 15 ],
            'Wine'        : [ 40, 20 ],
            'Rock Salt' : [ 0, 65 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 160 ],
            'Cotton' : [ 38, 15 ],
            'Wool'   : [ 65, 25 ],
            'Flax'   : [ 0, 42 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 65 ],
            'Silk Cloth'   : [ 0, 200 ],
            'Wool Cloth'   : [ 0, 65 ],
            'Velvet'         : [ 0, 75 ],
            'Linen Cloth'  : [ 50, 30 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 265 ],
            'Amber'            : [ 0, 320 ],
            'Ivory'            : [ 0, 280 ],
            'Pearl'            : [ 0, 300 ],
            'Tortoise Shell' : [ 0, 110 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 1000 ],
            'Silver' : [ 0, 240 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 175 ],
            'Tin Ore'    : [ 0, 90 ],
            'Iron Ore'   : [ 0, 185 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 400 ],
            'Carpet'  : [ 0, 300 ],
            'Musk'    : [ 0, 120 ],
            'Perfume' : [ 0, 100 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 3, 2 ],
            'Dye'           : [ 0, 125 ],
            'Porcelain'     : [ 0, 130 ],
            'Glassware'     : [ 0, 230 ],
            'Arms'          : [ 0, 100 ],
            'Wood'          : [ 0, 125 ],
        # },
    },

    3  : {# N Africa
        'Available_items' : {
            'Fish'          : [ 25, 10 ],
            'Olive Oil'   : [ 35, 12 ],
            'Rock Salt'   : [ 60, 45 ],
            'Wool'          : [ 70, 30 ],
            'Flax'          : [ 35, 10 ],
            'Linen Cloth' : [ 50, 35 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 145 ],
            'Cinnamon' : [ 0, 110 ],
            'Pepper'   : [ 0, 100 ],
            'Nutmeg'   : [ 0, 95 ],
            'Pimento'  : [ 0, 65 ],
            'Ginger'   : [ 0, 60 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 180 ],
            'Tea'     : [ 0, 180 ],
            'Coffee'  : [ 0, 320 ],
            'Cacao'   : [ 0, 75 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 50 ],
            'Cheese'      : [ 0, 35 ],
            'Fish'        : [ 25, 10 ],
            'Grain'       : [ 0, 25 ],
            'Olive Oil' : [ 35, 12 ],
            'Wine'        : [ 0, 40 ],
            'Rock Salt' : [ 60, 45 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 110 ],
            'Cotton' : [ 0, 40 ],
            'Wool'   : [ 70, 30 ],
            'Flax'   : [ 35, 10 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 65 ],
            'Silk Cloth'   : [ 0, 120 ],
            'Wool Cloth'   : [ 0, 45 ],
            'Velvet'         : [ 0, 65 ],
            'Linen Cloth'  : [ 50, 35 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 270 ],
            'Amber'            : [ 0, 300 ],
            'Ivory'            : [ 0, 260 ],
            'Pearl'            : [ 0, 270 ],
            'Tortoise Shell' : [ 0, 80 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 900 ],
            'Silver' : [ 0, 240 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 160 ],
            'Tin Ore'    : [ 0, 95 ],
            'Iron Ore'   : [ 0, 170 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 300 ],
            'Carpet'  : [ 0, 170 ],
            'Musk'    : [ 0, 100 ],
            'Perfume' : [ 0, 120 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 0, 100 ],
            'Porcelain'     : [ 0, 110 ],
            'Glassware'     : [ 0, 230 ],
            'Arms'          : [ 0, 100 ],
            'Wood'          : [ 0, 100 ],
        # },
    },

    4  : {# Otto
        'Available_items' : {
            'Cheese'       : [ 30, 15 ],
            'Grain'        : [ 14, 7 ],
            'Rock Salt'  : [ 55, 20 ],
            'Cotton'       : [ 65, 40 ],
            'Wool'         : [ 60, 60 ],
            'Copper Ore' : [ 100, 60 ],
            'Dye'          : [ 115, 50 ],
            'Wood'         : [ 70, 40 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 110 ],
            'Cinnamon' : [ 0, 150 ],
            'Pepper'   : [ 0, 75 ],
            'Nutmeg'   : [ 0, 90 ],
            'Pimento'  : [ 0, 60 ],
            'Ginger'   : [ 0, 65 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 280 ],
            'Tea'     : [ 0, 160 ],
            'Coffee'  : [ 0, 340 ],
            'Cacao'   : [ 0, 85 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 50 ],
            'Cheese'      : [ 30, 15 ],
            'Fish'        : [ 0, 35 ],
            'Grain'       : [ 14, 7 ],
            'Olive Oil' : [ 0, 42 ],
            'Wine'        : [ 0, 15 ],
            'Rock Salt' : [ 55, 20 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 140 ],
            'Cotton' : [ 65, 40 ],
            'Wool'   : [ 60, 60 ],
            'Flax'   : [ 0, 30 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 60 ],
            'Silk Cloth'   : [ 0, 180 ],
            'Wool Cloth'   : [ 0, 90 ],
            'Velvet'         : [ 0, 95 ],
            'Linen Cloth'  : [ 0, 60 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 300 ],
            'Amber'            : [ 0, 300 ],
            'Ivory'            : [ 0, 290 ],
            'Pearl'            : [ 0, 240 ],
            'Tortoise Shell' : [ 0, 85 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 1000 ],
            'Silver' : [ 0, 200 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 100, 60 ],
            'Tin Ore'    : [ 0, 100 ],
            'Iron Ore'   : [ 0, 190 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 400 ],
            'Carpet'  : [ 0, 150 ],
            'Musk'    : [ 0, 140 ],
            'Perfume' : [ 0, 120 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 115, 50 ],
            'Porcelain'     : [ 0, 100 ],
            'Glassware'     : [ 0, 235 ],
            'Arms'          : [ 0, 100 ],
            'Wood'          : [ 70, 40 ],
        # },
    },

    5  : {# W Africa
        'Available_items' : {
            'Cacao'         : [ 50, 10 ],
            'Fish'          : [ 25, 5 ],
            'Flax'          : [ 35, 15 ],
            'Linen Cloth' : [ 45, 17 ],
            'Amber'         : [ 220, 90 ],
            'Gold'          : [ 1000, 300 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 45 ],
            'Cinnamon' : [ 0, 40 ],
            'Pepper'   : [ 0, 40 ],
            'Nutmeg'   : [ 0, 45 ],
            'Pimento'  : [ 0, 45 ],
            'Ginger'   : [ 0, 40 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 10 ],
            'Tea'     : [ 0, 20 ],
            'Coffee'  : [ 0, 15 ],
            'Cacao'   : [ 50, 10 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 60 ],
            'Cheese'      : [ 0, 45 ],
            'Fish'        : [ 25, 5 ],
            'Grain'       : [ 0, 50 ],
            'Olive Oil' : [ 0, 60 ],
            'Wine'        : [ 0, 30 ],
            'Rock Salt' : [ 0, 22 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 38 ],
            'Cotton' : [ 0, 45 ],
            'Wool'   : [ 0, 10 ],
            'Flax'   : [ 35, 15 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 75 ],
            'Silk Cloth'   : [ 0, 80 ],
            'Wool Cloth'   : [ 0, 15 ],
            'Velvet'         : [ 0, 85 ],
            'Linen Cloth'  : [ 45, 17 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 80 ],
            'Amber'            : [ 220, 90 ],
            'Ivory'            : [ 0, 45 ],
            'Pearl'            : [ 0, 70 ],
            'Tortoise Shell' : [ 0, 15 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 700, 300 ],
            'Silver' : [ 0, 180 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 30 ],
            'Tin Ore'    : [ 0, 20 ],
            'Iron Ore'   : [ 0, 35 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 80 ],
            'Carpet'  : [ 0, 110 ],
            'Musk'    : [ 0, 60 ],
            'Perfume' : [ 0, 90 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 50 ],
            'Dye'           : [ 0, 60 ],
            'Porcelain'     : [ 0, 40 ],
            'Glassware'     : [ 0, 50 ],
            'Arms'          : [ 0, 140 ],
            'Wood'          : [ 0, 20 ],
        # },
    },

    6  : {# Central America
        'Available_items' : {
            'Pimento'          : [ 20, 5 ],
            'Fish'             : [ 15, 8 ],
            'Rock Salt'      : [ 40, 15 ],
            'Coral'            : [ 120, 70 ],
            'Tortoise Shell' : [ 60, 40 ],
            'Dye'              : [ 35, 15 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 55 ],
            'Cinnamon' : [ 0, 45 ],
            'Pepper'   : [ 0, 30 ],
            'Nutmeg'   : [ 0, 40 ],
            'Pimento'  : [ 20, 5 ],
            'Ginger'   : [ 0, 30 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 70 ],
            'Tea'     : [ 0, 25 ],
            'Coffee'  : [ 0, 30 ],
            'Cacao'   : [ 0, 20 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 80 ],
            'Cheese'      : [ 0, 45 ],
            'Fish'        : [ 15, 8 ],
            'Grain'       : [ 0, 35 ],
            'Olive Oil' : [ 0, 30 ],
            'Wine'        : [ 0, 35 ],
            'Rock Salt' : [ 40, 15 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 40 ],
            'Cotton' : [ 0, 50 ],
            'Wool'   : [ 0, 15 ],
            'Flax'   : [ 0, 20 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 85 ],
            'Silk Cloth'   : [ 0, 90 ],
            'Wool Cloth'   : [ 0, 20 ],
            'Velvet'         : [ 0, 70 ],
            'Linen Cloth'  : [ 0, 65 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 120, 70 ],
            'Amber'            : [ 0, 280 ],
            'Ivory'            : [ 0, 120 ],
            'Pearl'            : [ 0, 105 ],
            'Tortoise Shell' : [ 60, 40 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 250 ],
            'Silver' : [ 0, 140 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 40 ],
            'Tin Ore'    : [ 0, 22 ],
            'Iron Ore'   : [ 0, 35 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 120 ],
            'Carpet'  : [ 0, 105 ],
            'Musk'    : [ 0, 35 ],
            'Perfume' : [ 0, 50 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 35, 15 ],
            'Porcelain'     : [ 0, 50 ],
            'Glassware'     : [ 0, 50 ],
            'Arms'          : [ 0, 180 ],
            'Wood'          : [ 0, 28 ],
        # },
    },

    7  : {# South America
        'Available_items' : {
            'Pimento'          : [ 20, 7 ],
            'Grain'            : [ 25, 15 ],
            'Tortoise Shell' : [ 55, 30 ],
            'Silver'           : [ 150, 100 ],
            'Iron Ore'       : [ 90, 30 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 50 ],
            'Cinnamon' : [ 0, 50 ],
            'Pepper'   : [ 0, 35 ],
            'Nutmeg'   : [ 0, 45 ],
            'Pimento'  : [ 20, 7 ],
            'Ginger'   : [ 0, 25 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 70 ],
            'Tea'     : [ 0, 30 ],
            'Coffee'  : [ 0, 20 ],
            'Cacao'   : [ 0, 15 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 85 ],
            'Cheese'      : [ 0, 50 ],
            'Fish'        : [ 0, 10 ],
            'Grain'       : [ 25, 15 ],
            'Olive Oil' : [ 0, 25 ],
            'Wine'        : [ 0, 30 ],
            'Rock Salt' : [ 0, 50 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 37 ],
            'Cotton' : [ 0, 52 ],
            'Wool'   : [ 0, 12 ],
            'Flax'   : [ 0, 25 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 82 ],
            'Silk Cloth'   : [ 0, 88 ],
            'Wool Cloth'   : [ 0, 18 ],
            'Velvet'         : [ 0, 68 ],
            'Linen Cloth'  : [ 0, 67 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 100 ],
            'Amber'            : [ 0, 270 ],
            'Ivory'            : [ 0, 110 ],
            'Pearl'            : [ 0, 95 ],
            'Tortoise Shell' : [ 55, 30 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 270 ],
            'Silver' : [ 150, 100 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 42 ],
            'Tin Ore'    : [ 0, 23 ],
            'Iron Ore'   : [ 90, 30 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 130 ],
            'Carpet'  : [ 0, 100 ],
            'Musk'    : [ 0, 42 ],
            'Perfume' : [ 0, 60 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 0, 20 ],
            'Porcelain'     : [ 0, 50 ],
            'Glassware'     : [ 0, 50 ],
            'Arms'          : [ 0, 170 ],
            'Wood'          : [ 0, 3 ],
        # },
    },

    8  : {# East Africa
        'Available_items' : {
            'Fish'         : [ 20, 7 ],
            'Rock Salt'  : [ 18, 6 ],
            'Flax'         : [ 30, 10 ],
            'Coral'        : [ 120, 60 ],
            'Gold'         : [ 550, 150 ],
            'Copper Ore' : [ 80, 40 ],
            'Dye'          : [ 40, 20 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 25 ],
            'Cinnamon' : [ 0, 20 ],
            'Pepper'   : [ 0, 20 ],
            'Nutmeg'   : [ 0, 25 ],
            'Pimento'  : [ 0, 20 ],
            'Ginger'   : [ 0, 20 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 10 ],
            'Tea'     : [ 0, 16 ],
            'Coffee'  : [ 0, 12 ],
            'Cacao'   : [ 0, 10 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 65 ],
            'Cheese'      : [ 0, 45 ],
            'Fish'        : [ 20, 7 ],
            'Grain'       : [ 0, 55 ],
            'Olive Oil' : [ 0, 15 ],
            'Wine'        : [ 0, 35 ],
            'Rock Salt' : [ 18, 6 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 28 ],
            'Cotton' : [ 0, 55 ],
            'Wool'   : [ 0, 8 ],
            'Flax'   : [ 30, 10 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 80 ],
            'Silk Cloth'   : [ 0, 80 ],
            'Wool Cloth'   : [ 0, 20 ],
            'Velvet'         : [ 0, 80 ],
            'Linen Cloth'  : [ 0, 70 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 120, 60 ],
            'Amber'            : [ 0, 120 ],
            'Ivory'            : [ 0, 40 ],
            'Pearl'            : [ 0, 75 ],
            'Tortoise Shell' : [ 0, 50 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 550, 150 ],
            'Silver' : [ 0, 170 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 80, 40 ],
            'Tin Ore'    : [ 0, 25 ],
            'Iron Ore'   : [ 0, 35 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 70 ],
            'Carpet'  : [ 0, 120 ],
            'Musk'    : [ 0, 55 ],
            'Perfume' : [ 0, 95 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 100 ],
            'Dye'           : [ 40, 20 ],
            'Porcelain'     : [ 0, 30 ],
            'Glassware'     : [ 0, 105 ],
            'Arms'          : [ 0, 160 ],
            'Wood'          : [ 0, 25 ],
        # },
    },

    9  : {# Middle East
        'Available_items' : {
            'Coffee'         : [ 35, 15 ],
            'Olive Oil'    : [ 10, 5 ],
            'Rock Salt'    : [ 20, 12 ],
            'Cotton'         : [ 15, 5 ],
            'Wool'           : [ 30, 16 ],
            'Cotton Cloth' : [ 32, 14 ],
            'Wool Cloth'   : [ 45, 22 ],
            'Carpet'         : [ 75, 30 ],
            'Perfume'        : [ 50, 28 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 30 ],
            'Cinnamon' : [ 0, 28 ],
            'Pepper'   : [ 0, 22 ],
            'Nutmeg'   : [ 0, 18 ],
            'Pimento'  : [ 0, 40 ],
            'Ginger'   : [ 0, 35 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 15 ],
            'Tea'     : [ 0, 90 ],
            'Coffee'  : [ 35, 15 ],
            'Cacao'   : [ 0, 5 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 50 ],
            'Cheese'      : [ 0, 35 ],
            'Fish'        : [ 0, 20 ],
            'Grain'       : [ 0, 15 ],
            'Olive Oil' : [ 10, 5 ],
            'Wine'        : [ 0, 10 ],
            'Rock Salt' : [ 20, 12 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 100 ],
            'Cotton' : [ 15, 5 ],
            'Wool'   : [ 30, 16 ],
            'Flax'   : [ 0, 30 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 32, 14 ],
            'Silk Cloth'   : [ 0, 110 ],
            'Wool Cloth'   : [ 45, 22 ],
            'Velvet'         : [ 0, 115 ],
            'Linen Cloth'  : [ 0, 65 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 80 ],
            'Amber'            : [ 0, 310 ],
            'Ivory'            : [ 0, 70 ],
            'Pearl'            : [ 0, 60 ],
            'Tortoise Shell' : [ 0, 65 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 950 ],
            'Silver' : [ 0, 170 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 75 ],
            'Tin Ore'    : [ 0, 60 ],
            'Iron Ore'   : [ 0, 120 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 320 ],
            'Carpet'  : [ 75, 30 ],
            'Musk'    : [ 0, 120 ],
            'Perfume' : [ 50, 28 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 0, 120 ],
            'Porcelain'     : [ 0, 35 ],
            'Glassware'     : [ 0, 35 ],
            'Arms'          : [ 0, 240 ],
            'Wood'          : [ 0, 120 ],
        # },
    },

    10 : {# India
        'Available_items' : {
            'Clove'         : [ 25, 12 ],
            'Pepper'        : [ 15, 5 ],
            'Tea'           : [ 20, 8 ],
            'Grain'         : [ 12, 4 ],
            'Cotton'        : [ 25, 10 ],
            'Flax'          : [ 8, 3 ],
            'Linen Cloth' : [ 30, 18 ],
            'Copper Ore'  : [ 60, 30 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 25, 12 ],
            'Cinnamon' : [ 0, 10 ],
            'Pepper'   : [ 15, 5 ],
            'Nutmeg'   : [ 0, 13 ],
            'Pimento'  : [ 0, 15 ],
            'Ginger'   : [ 0, 14 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 12 ],
            'Tea'     : [ 20, 8 ],
            'Coffee'  : [ 0, 6 ],
            'Cacao'   : [ 0, 5 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 68 ],
            'Cheese'      : [ 0, 15 ],
            'Fish'        : [ 0, 15 ],
            'Grain'       : [ 12, 4 ],
            'Olive Oil' : [ 0, 8 ],
            'Wine'        : [ 0, 45 ],
            'Rock Salt' : [ 0, 5 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 75 ],
            'Cotton' : [ 25, 10 ],
            'Wool'   : [ 0, 20 ],
            'Flax'   : [ 8, 3 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 30 ],
            'Silk Cloth'   : [ 0, 85 ],
            'Wool Cloth'   : [ 0, 59 ],
            'Velvet'         : [ 0, 220 ],
            'Linen Cloth'  : [ 30, 18 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 70 ],
            'Amber'            : [ 0, 290 ],
            'Ivory'            : [ 0, 90 ],
            'Pearl'            : [ 0, 40 ],
            'Tortoise Shell' : [ 0, 20 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 1050 ],
            'Silver' : [ 0, 180 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 60, 30 ],
            'Tin Ore'    : [ 0, 55 ],
            'Iron Ore'   : [ 0, 130 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 200 ],
            'Carpet'  : [ 0, 35 ],
            'Musk'    : [ 0, 130 ],
            'Perfume' : [ 0, 135 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 0, 140 ],
            'Porcelain'     : [ 0, 200 ],
            'Glassware'     : [ 0, 300 ],
            'Arms'          : [ 0, 230 ],
            'Wood'          : [ 0, 22 ],
        # },
    },

    11 : {# Southeast Asia
        'Available_items' : {
            'Pepper'           : [ 3, 2 ],
            'Ginger'           : [ 3, 2 ],
            'Fish'             : [ 15, 5 ],
            'Coral'            : [ 50, 20 ],
            'Tortoise Shell' : [ 30, 10 ],
            'Tin Ore'        : [ 45, 25 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 3 ],
            'Cinnamon' : [ 0, 2 ],
            'Pepper'   : [ 3, 2 ],
            'Nutmeg'   : [ 0, 3 ],
            'Pimento'  : [ 0, 2 ],
            'Ginger'   : [ 3, 2 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 12 ],
            'Tea'     : [ 0, 6 ],
            'Coffee'  : [ 0, 5 ],
            'Cacao'   : [ 0, 5 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 70 ],
            'Cheese'      : [ 0, 12 ],
            'Fish'        : [ 15, 5 ],
            'Grain'       : [ 0, 4 ],
            'Olive Oil' : [ 0, 10 ],
            'Wine'        : [ 0, 45 ],
            'Rock Salt' : [ 0, 6 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 40 ],
            'Cotton' : [ 0, 16 ],
            'Wool'   : [ 0, 18 ],
            'Flax'   : [ 0, 20 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 38 ],
            'Silk Cloth'   : [ 0, 42 ],
            'Wool Cloth'   : [ 0, 42 ],
            'Velvet'         : [ 0, 40 ],
            'Linen Cloth'  : [ 0, 32 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 50, 20 ],
            'Amber'            : [ 0, 210 ],
            'Ivory'            : [ 0, 120 ],
            'Pearl'            : [ 0, 35 ],
            'Tortoise Shell' : [ 30, 10 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 1020 ],
            'Silver' : [ 0, 190 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 70 ],
            'Tin Ore'    : [ 45, 25 ],
            'Iron Ore'   : [ 0, 50 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 0, 100 ],
            'Carpet'  : [ 0, 45 ],
            'Musk'    : [ 0, 65 ],
            'Perfume' : [ 0, 55 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 0, 20 ],
            'Porcelain'     : [ 0, 40 ],
            'Glassware'     : [ 0, 95 ],
            'Arms'          : [ 0, 190 ],
            'Wood'          : [ 0, 18 ],
        # },
    },

    12 : {#  Far East
        'Available_items' : {
            'Ginger'        : [ 20, 10 ],
            'Tea'           : [ 20, 8 ],
            'Fish'          : [ 10, 3 ],
            'Linen Cloth' : [ 25, 15 ],
            'Pearl'         : [ 60, 30 ],
            'Art'           : [ 120, 80 ],
            'Porcelain'     : [ 30, 12 ],
        },
        # 'Spice'           : {
            'Clove'    : [ 0, 30 ],
            'Cinnamon' : [ 0, 40 ],
            'Pepper'   : [ 0, 50 ],
            'Nutmeg'   : [ 0, 45 ],
            'Pimento'  : [ 0, 3 ],
            'Ginger'   : [ 20, 10 ],
        # },
        # 'Special'         : {
            'Tobacco' : [ 0, 320 ],
            'Tea'     : [ 20, 8 ],
            'Coffee'  : [ 0, 5 ],
            'Cacao'   : [ 0, 5 ],
        # },
        # 'Food'            : {
            'Sugar'       : [ 0, 90 ],
            'Cheese'      : [ 0, 20 ],
            'Fish'        : [ 10, 3 ],
            'Grain'       : [ 0, 5 ],
            'Olive Oil' : [ 0, 7 ],
            'Wine'        : [ 0, 70 ],
            'Rock Salt' : [ 0, 5 ],
        # },
        # 'Fabric'          : {
            'Silk'   : [ 0, 50 ],
            'Cotton' : [ 0, 18 ],
            'Wool'   : [ 0, 23 ],
            'Flax'   : [ 0, 14 ],
        # },
        # 'Cloth'           : {
            'Cotton Cloth' : [ 0, 40 ],
            'Silk Cloth'   : [ 0, 30 ],
            'Wool Cloth'   : [ 0, 70 ],
            'Velvet'         : [ 0, 310 ],
            'Linen Cloth'  : [ 25, 15 ],
        # },
        # 'Gem'             : {
            'Coral'            : [ 0, 55 ],
            'Amber'            : [ 0, 250 ],
            'Ivory'            : [ 0, 300 ],
            'Pearl'            : [ 60, 30 ],
            'Tortoise Shell' : [ 0, 20 ],
        # },
        # 'Jewelry'         : {
            'Gold'   : [ 0, 900 ],
            'Silver' : [ 0, 200 ],
        # },
        # 'Ore'             : {
            'Copper Ore' : [ 0, 50 ],
            'Tin Ore'    : [ 0, 35 ],
            'Iron Ore'   : [ 0, 140 ],
        # },
        # 'Luxury'          : {
            'Art'     : [ 120, 80 ],
            'Carpet'  : [ 0, 52 ],
            'Musk'    : [ 0, 140 ],
            'Perfume' : [ 0, 160 ],
        # },
        # 'Other'           : {
            'Glass Beads' : [ 0, 2 ],
            'Dye'           : [ 0, 200 ],
            'Porcelain'     : [ 30, 12 ],
            'Glassware'     : [ 0, 450 ],
            'Arms'          : [ 0, 70 ],
            'Wood'          : [ 0, 15 ],
        # },
    },

}

cargo_type_2_name = {

    'Spice'           : {
        'Clove': [0, 140],
        'Cinnamon': [0, 120],
        'Pepper': [0, 80],
        'Nutmeg': [0, 95],
        'Pimento': [0, 60],
        'Ginger': [0, 55],
    },

    'Special'         : {
        'Tobacco': [0, 220],
        'Tea': [0, 200],
        'Coffee': [0, 5],
        'Cacao': [0, 105],
    },

    'Food'            : {
        'Sugar': [0, 45],
        'Cheese': [30, 20],
        'Fish': [20, 10],
        'Grain': [0, 32],
        'Olive Oil': [28, 10],
        'Wine': [36, 20],
        'Rock Salt': [0, 65],
    },

    'Fabric'          : {
        'Silk': [0, 180],
        'Cotton': [0, 50],
        'Wool': [0, 75],
        'Flax': [0, 40],
    },


    'Cloth'           : {
        'Cotton Cloth': [0, 40],
        'Silk Cloth': [0, 220],
        'Wool Cloth': [0, 70],
        'Velvet': [80, 50],
        'Linen Cloth': [50, 25],
    },

    'Gem'             : {
        'Coral': [0, 280],
        'Amber': [0, 300],
        'Ivory': [0, 280],
        'Pearl': [0, 310],
        'Tortoise Shell': [0, 120],
    },

    'Jewelry'         : {
        'Gold': [0, 1000],
        'Silver': [0, 240],
    },

    'Ore'             : {
        'Copper Ore': [0, 180],
        'Tin Ore': [0, 100],
        'Iron Ore': [0, 190],
    },

    'Luxury'          : {
        'Art': [0, 400],
        'Carpet': [0, 300],
        'Musk': [0, 120],
        'Perfume': [0, 110],
    },

    'Other'           : {
        'Glass Beads': [0, 2],
        'Dye': [120, 50],
        'Porcelain': [0, 120],
        'Glassware': [0, 230],
        'Arms': [120, 100],
        'Wood': [0, 130],
    }
}

def add_cargo_to_table_cargo_template():
    for cargo_type, dict in cargo_type_2_name.items():
        # print(cargo_type)
        for name, _ in dict.items():
            print(name, cargo_type)

            market_id_2_buy_price = {

            }

            for market_id, dict in hash_markets_price_details.items():
                if name in dict['Available_items']:
                    market_id_2_buy_price[market_id] = dict['Available_items'][name][0]


            market_id_2_sell_price = {

            }
            for market_id, dict in hash_markets_price_details.items():
                if name in dict:
                    market_id_2_sell_price[market_id] = dict[name][1]

            new_obj = CargoTemplate(
                name=name,
                cargo_type=cargo_type,
                required_economy_value=300,
                buy_price=json.dumps(market_id_2_buy_price),
                sell_price=json.dumps(market_id_2_sell_price),

            )


            SESSION.add(new_obj)

    SESSION.commit()


if __name__ == '__main__':
    add_cargo_to_table_cargo_template()
