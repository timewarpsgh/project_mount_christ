import sys
import os
import json


PATH_TO_DIR = r'D:\data\code\python\project_mount_christ\src\server\models'
sys.path.append(PATH_TO_DIR)

from world_models import SESSION, ItemTemplate

hash_items = {
    ###### Voyager's Aid #####
    ###### consumables #####
    1: {
        'name': 'Balm',
        'price': 6000,
        'image': [12, 7],
        'description': "A perfumed oil believed to calm storms.",
        'effects': 9,
        'effects_description': 'Use: +9 max days at sea.',
        'type': 'consumable',
    },
    2: {
        'name': 'Lime Juice',
        'price': 1500,
        'image': [13, 7],
        'description': "A great remedy for scurvy, "
                       "the disease of poor nutrition "
                       "that often troubles a crew during long voyages.",
        'effects': 6,
        'effects_description': 'Use: +6 max days at sea.',
        'type': 'consumable',
    },
    3: {
        'name': 'Rat Poison',
        'price': 500,
        'image': [11, 7],
        'description': "A poison to get rid of rats on a ship. "
                       "Those pesky animals will feast on your precious food if you "
                       "don't have a way to get rid of them.",
        'effects': 3,
        'effects_description': 'Use: +3 max days at sea.',
        'type': 'consumable',
    },

    ###### tools #####
    4: {
        'name': 'Quadrant',
        'price': 4000,
        'image': [5, 7],
        'description': "A low precision instrument use for celestial navigation. "
                       "It measures longitude and latitude.",
        'type': 'instrument',
        'effects': 1,
        'effects_description': 'Equip: +1 fleet speed.',
    },
    5: {
        'name': 'Sextant',
        'price': 8000,
        'image': [6, 7],
        'description': "A high precision instrument used for celestial navigation. "
                       "It measures longitude and latitude.",
        'type': 'instrument',
        'effects': 2,
        'effects_description': 'Equip: +2 fleet speed.',
    },
    6: {
        'name': 'Theodolite',
        'price': 12000,
        'image': [7, 7],
        'description': "The most precise and reliable instrument used for celestial navigation. "
                       "It measures longitude and latitude.",
        'type': 'instrument',
        'effects': 3,
        'effects_description': 'Equip: +3 fleet speed.',
    },
    7: {
        'name': 'Pocket Watch',
        'price': 2000,
        'image': [8, 7],
        'description': "A handy portable watch. With it, you'll always know the correct time.",
        'type': 'watch',
        'effects_description': 'Equip: +2 max days at sea.',
    },
    8: {
        'name': 'Telescope',
        'price': 5000,
        'image': [9, 7],
        'description': "An optical instrument that will help you "
                       "find distant objects and ports at sea.",
        'type': 'telescope',
        'effects_description': 'Equip: +1 fleet speed.',

    },
    9: {
        'name': 'Cat',
        'price': 2000,
        'image': [10, 7],
        'description': "Not only does a cat make a nice pet, but it'll keep your ship rat-free!",
        'type': 'pet',
        'effects_description': 'Equip: +2 max days at sea.',
    },

    ###### permits #####
    10: {
        'name': 'Tax Free Permit (E)',
        'price': 10000,
        'image': [15, 7],
        'description': "A permit issued by England. "
                       "It gives one tax-exempt status when "
                       "trading in ports allied with England."
    },
    11: {
        'name': 'Tax Free Permit (H)',
        'price': 10000,
        'image': [15, 7],
        'description': "A permit issued by Holland. "
                       "It gives one tax-exempt status when trading "
                       "in ports allied with Holland."
    },
    12: {
        'name': 'Tax Free Permit (I)',
        'price': 10000,
        'image': [15, 7],
        'description': "A permit issued by Italy. "
                       "It gives one tax-exempt status when trading in ports allied with Italy."
    },
    13: {
        'name': 'Tax Free Permit (P)',
        'price': 10000,
        'image': [15, 7],
        'description': "A permit issued by Portugal. "
                       "It gives one tax-exempt status when trading in ports allied with Portugal."
    },
    14: {
        'name': 'Tax Free Permit (S)',
        'price': 10000,
        'image': [15, 7],
        'description': "A permit issued by Spain. "
                       "It gives one tax-exempt status when trading in ports allied with Spain."
    },
    15: {
        'name': 'Tax Free Permit (T)',
        'price': 10000,
        'image': [15, 7],
        'description': "A permit issued by Turkey. "
                       "It gives one tax-exempt status when trading in ports allied with Turkey."
    },

    ###### Treasure ######
    ###### Treasury ######
    16: {
        'name': 'Candleholder',
        'price': 3000,
        'image': [14, 8],
        'description': "An antique candleholder made of brass."
    },
    17: {
        'name': 'Crown of Glory',
        'price': 50000,
        'image': [4, 8],
        'description': "A gold crown with delicate decorations."
    },
    18: {
        'name': 'Garnet Brooch',
        'price': 20000,
        'image': [15, 8],
        'description': "A beautifully designed brooch set with beautiful garnets."
    },
    19: {
        'name': 'Gold Bracelet',
        'price': 15000,
        'image': [2, 8],
        'description': "A wide, heavy, solid gold bracelet set with diamonds."
    },
    20: {
        'name': 'Malachite Box',
        'price': 8000,
        'image': [5, 8],
        'description': "A small box cut out of malachite stone."
    },
    21: {
        'name': 'Mermaid Bangle',
        'price': 10000,
        'image': [2, 8],
        'description': "A dazzling gold bracelet decorated with beautiful opals."
    },
    22: {
        'name': 'Ruby Scepter',
        'price': 50000,
        'image': [13, 8],
        'description': "A scepter with a huge ruby size of an egg at the top."
    },

    ###### Accecory ######
    23: {
        'name': 'Aqua Tiara',
        'price': 5000,
        'image': [12, 8],
        'description': "An intricately decorated tiara set with "
                       "small but brilliant aquamarine stones."
    },
    24: {
        'name': 'China Dress',
        'price': 8000,
        'image': [7, 8],
        'description': "A beautiful, traditional Chinese dress, made of the finest Chinese silk."
    },
    25: {
        'name': 'Circlet',
        'price': 4000,
        'image': [9, 8],
        'description': "A beautiful tiara highlighted by a large sapphire in its center."
    },
    26: {
        'name': 'Ermine Coat',
        'price': 12000,
        'image': [1, 8],
        'description': "A luxurious coat made from the white winter fur of the rare ermine weasel."
    },
    27: {
        'name': 'Peacock Fan',
        'price': 3000,
        'image': [10, 8],
        'description': "A beautiful fan made of long and colorful peacock feathers."
    },
    28: {
        'name': 'Platinum Comb',
        'price': 10000,
        'image': [8, 8],
        'description': "A fancy comb made of platinum and decorated with rare gems."
    },
    29: {
        'name': 'Silk Scarf',
        'price': 1000,
        'image': [6, 8],
        'description': "A colorful scarf made of fine silk."
    },
    30: {
        'name': 'Silk Shawl',
        'price': 3000,
        'image': [11, 8],
        'description': "A soft shawl made of the best silk from China."
    },
    31: {
        'name': 'Velvet Coat',
        'price': 5000,
        'image': [1, 8],
        'description': "A velvet coat cut in the latest 16th century fashion."
    },

    ###### Armor ######
    32: {
        'name': 'Leather Armor',
        'price': 1000,
        'image': [1, 7],
        'description': "A relatively inexpensive armor "
                       "made of leather that has been hardened with animal grease.",
        'type': 'armor',
        'effects': 5,
        'effects_description': 'Equip: +5% damage reduction.',
    },
    33: {
        'name': 'Chain Mail',
        'price': 2000,
        'image': [2, 7],
        'description': "An armor made of thousands of tiny interlinked steel rings. "
                       "While it allows the wearer ease of movement, "
                       "it doesn't offer the best protection.",
        'type': 'armor',
        'effects': 10,
        'effects_description': 'Equip: +10% damage reduction.',
    },
    34: {
        'name': 'Half Plate',
        'price': 4000,
        'image': [3, 7],
        'description': "An armor with sheets of tough, "
                       "thin steel plates that cover only the upper body. "
                       "An improvement of plate armor, "
                       "it's designed for more active naval combats.",
        'type': 'armor',
        'effects': 15,
        'effects_description': 'Equip: +15% damage reduction.',
    },
    35: {
        'name': 'Plate Mail',
        'price': 8000,
        'image': [4, 7],
        'description': "A step up from chain mail armor, "
                       "this armor is formed by a combination of plate and mail. "
                       "It offers better protection than Half Plate Armor.",
        'type': 'armor',
        'effects': 20,
        'effects_description': 'Equip: +20% damage reduction.',
    },
    36: {
        'name': "Errol's Plate",
        'price': 300000,
        'image': [4, 7],
        'description': "Half plate armor made by the famous Copenhagen armorer, Errol. "
                       "It provides greater protection than plate mail armor.",
        'type': 'armor',
        'effects': 40,
        'effects_description': 'Equip: +40% damage reduction.',
    },
    37: {
        'name': 'Crusader Armor (*)',
        'price': 600000,
        'image': [4, 7],
        'description': "Armor that the famous armorer, "
                       "Montaguinus made-to-order for Affonso, "
                       "the founding king of Portugal.",
        'type': 'armor',
        'effects': 80,
        'effects_description': 'Equip: +80% damage reduction.',
    },

    ###### Weapon ######
    ###### Curved Sword ######
    38: {
        'name': 'Short Saber',
        'price': 1000,
        'image': [12, 6],
        'description': "A light, slender sword used by cavalry. "
                       "It's less effective in an attack than a Saber, "
                       "but its low price makes it popular.",
        'type': 'weapon',
        'effects': 5,
        'effects_description': 'Equip: +5% damage.',

    },
    39: {
        'name': 'Scimitar',
        'price': 8000,
        'image': [11, 6],
        'description': "A curved saber with an outer cutting edge. "
                       "A great weapon for attacking, "
                       "it's mainly used by Arabs and Persians.",
        'type': 'weapon',
        'effects': 25,
        'effects_description': 'Equip: +25% damage.',
    },
    40: {
        'name': 'Japanese Sword',
        'price': 20000,
        'image': [13, 6],
        'description': "A very sharp sword made in Japan. "
                       "It's especially effective for lashing attacks.",
        'type': 'weapon',
        'effects': 35,
        'effects_description': 'Equip: +35% damage.',
    },
    41: {
        'name': 'Saber',
        'price': 3000,
        'image': [12, 6],
        'description': "A curved single-edged cavalry sword that is more "
                       "effective for lashing than for thrusting.",
        'type': 'weapon',
        'effects': 15,
        'effects_description': 'Equip: +15% damage.',
    },
    42: {
        'name': 'Magic Muramasa(*)',
        'price': 380000,
        'image': [8, 6],
        'description': "A treasured sword made in the 15th century by a famous "
                       "Japanese sword smith, Muramasa.",
        'type': 'weapon',
        'effects': 80,
        'effects_description': 'Equip: +80% damage.',
    },
    43: {
        'name': "Siva's Sword(*)",
        'price': 280000,
        'image': [8, 6],
        'description': "A legendary sword that's believed to confine the "
                       "power of Siva, the Hindu god of destruction. A powerful lashing weapon.",
        'type': 'weapon',
        'effects': 60,
        'effects_description': 'Equip: +60% damage.',
    },

    ###### Fencing Sword ######
    44: {
        'name': 'Flamberge',
        'price': 14000,
        'image': [15, 6],
        'description': "A long decorative sword with wavy edges. "
                       "Its offensive capability is superior to both the Rapier and the Estock.",
        'type': 'weapon',
        'effects': 30,
        'effects_description': 'Equip: +30% damage.',
    },
    45: {
        'name': 'Rapier',
        'price': 3000,
        'image': [14, 6],
        'description': "A light, slender, two-edged sword used only for thrusting. "
                       "It came into use after guns made armor obsolete.",
        'type': 'weapon',
        'effects': 15,
        'effects_description': 'Equip: +15% damage.',
    },
    46: {
        'name': 'Epee',
        'price': 2000,
        'image': [14, 6],
        'description': "A light sword with a sharp-pointed blade but no cutting edge, "
                       "used only for thrusting in dueling. "
                       "It's not very effective when it comes to attacking.",
        'type': 'weapon',
        'effects': 10,
        'effects_description': 'Equip: +10% damage.',
    },
    47: {
        'name': 'Estock',
        'price': 6000,
        'image': [9, 6],
        'description': "A sword developed to pierce the armor of a mounyed enemy. "
                       "It has higher attack rate than a rapier.",
        'type': 'weapon',
        'effects': 20,
        'effects_description': 'Equip: +20% damage.',
    },
    48: {
        'name': 'Crusader Sword (*)',
        'price': 380000,
        'image': [10, 6],
        'description': "A special sword with razor-like sharpness made by "
                       "the renowned swordsmith, Michelangelo.",
        'type': 'weapon',
        'effects': 80,
        'effects_description': 'Equip: +80% damage.',
    },

    ###### Heavy Sword ######
    49: {
        'name': 'Cutlass',
        'price': 1500,
        'image': [6, 6],
        'description': "A heavy, curved sword that historically has been used by sailors.",
        'type': 'weapon',
        'effects': 8,
        'effects_description': 'Equip: +8% damage.',
    },
    50: {
        'name': 'Broad Sword',
        'price': 5000,
        'image': [7, 6],
        'description': "A sword with a wide, straight, single-edged blade. "
                       "It's especially effective for striking.",
        'type': 'weapon',
        'effects': 18,
        'effects_description': 'Equip: +18% damage.',
    },
    51: {
        'name': 'Blue Crescent(*)',
        'price': 24000,
        'image': [16, 6],
        'description': "A unique Chinese sword with a wide crescent-shaped blade. "
                       "It's quite good for attacking, especially striking.",
        'type': 'weapon',
        'effects': 40,
        'effects_description': 'Equip: +40% damage.',
    },
    52: {
        'name': 'Claymore',
        'price': 15000,
        'image': [15, 6],
        'description': "A large two-handed sword from Scotland that may weigh up to 10 pounds. "
                       "It's quite effective for striking.",
        'type': 'weapon',
        'effects': 30,
        'effects_description': 'Equip: +30% damage.',
    },
    53: {
        'name': 'Golden Dragon(*)',
        'price': 18000,
        'image': [16, 6],
        'description': "A unique Chinese sword with wide blade. It's quite effective for striking.",
        'type': 'weapon',
        'effects': 30,
        'effects_description': 'Equip: +30% damage.',
    },

    # treasure
    54: {
        'name': 'Treasure Box',
        'price': 100000,
        'image': [16, 8],
        'description': "A box full of shiny treasures."
    },

    55: {
        'name': 'Diamond Ring',
        'price': 30000,
        'image': [3, 8],
        'description': "A ring with a large diamond on it."
    }
}


def add_item_to_table_item_template():
    for _, dict in hash_items.items():

        item_type = None

        for key, value in dict.items():

            if key == 'name':
                name = value

            if key == 'description':
                description = value

            if key == 'image':
                img_id = str(value[0]) + '_' + str(value[1])

            if key == 'type':
                item_type = value

            if key == 'price':
                buy_price = value

        new_obj = ItemTemplate(
            name=name,
            description=description,
            img_id=img_id,
            item_type=item_type,
            buy_price=buy_price
        )


        SESSION.add(new_obj)

    SESSION.commit()


if __name__ == '__main__':
    add_item_to_table_item_template()
