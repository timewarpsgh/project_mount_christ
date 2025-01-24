import random
import pygame_gui
import pygame
import json
from functools import partial

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'packets'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from login_pb2 import *
import login_pb2 as pb
from my_ui_elements import MyButton, only_show_top_window
from create_account_dialog import CreateAccountDialog
from packet_params_dialog import PacketParamsDialog
from my_ui_elements import MyMenuWindow, MyPanelWindow, MyFleetPanelWindow, MyMatePanelWindow
from asset_mgr import sAssetMgr
from map_maker import sMapMaker
from translator import sTr, tr, Language

from object_mgr import sObjectMgr
import constants as c


class OptionsDialog:

    def __init__(self, mgr, client):
        self.mgr = mgr
        self.client = client

        # add ui window
        self.ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((-20 + 5, c.WINDOW_HEIGHT - 100 + 30), (c.WINDOW_WIDTH + 40, 50)),
            manager=self.mgr,
            object_id='#options_window',
        )

        # buttons to add
        buttons_texts = ['Buildings', 'Options', 'Cmds', 'Fight', 'Items', 'Mates', 'Ships']

        if c.IS_DEV:
            pass
        else:
            buttons_texts[0] = ' '

        for id, button_text in enumerate(buttons_texts):
            MyButton(
                relative_rect=pygame.Rect((0 + id * 100, 0), (120, 60)),
                text=sTr.tr(button_text),
                manager=self.mgr,
                container=self.ui_window,
                on_click=partial(self.__open_menu, button_text),
            )


    def __open_menu(self, button_text):
        # on click options windows gets to the top !!!!

        # clear other menu windows
        stacked_windows = self.mgr.get_window_stack().get_stack()
        length = len(stacked_windows)
        reversed_stacked_windows = stacked_windows[::-1]
        if length >= 3:
            for i, window in enumerate(reversed_stacked_windows):
                if i in {0, length - 1}:
                    pass
                else:
                    window.kill()
        else:
            # open new window
            getattr(self, f'show_{button_text.lower()}_menu')()

    def __make_menu(self, dict):
        translated_dict = {}
        for key, value in dict.items():
            translated_dict[sTr.tr(key)] = value

        MyMenuWindow(
            title='',
            option_2_callback=translated_dict,
            mgr=self.mgr
        )


    def __send_get_available_cargos(self):
        self.client.send(GetAvailableCargos())

    def get_ship_mgr(self):
        return self.client.game.graphics.model.role.ship_mgr

    def get_mate_mgr(self):
        return self.client.game.graphics.model.role.mate_mgr

    def get_friend_mgr(self):
        return self.client.game.graphics.model.role.friend_mgr

    def __send_packet_to_get_cargo_cnt_and_sell_price(self, ship_id):
        packet = GetCargoCntAndSellPrice()
        packet.ship_id = ship_id

        self.client.send(packet)

    def __show_persons_investments(self):
        self.client.send(GetPersonsInvestments())

    def __get_nations_investments(self):
        self.client.send(GetNationsInvestments())

    def __show_invest_dialog(self):
        pack = pb.Invest()
        PacketParamsDialog(self.mgr, self.client, ['ingots_cnt'], pack)

        self.building_speak(tr("How many ingots do you want to invest?"))

    def __show_investment_state_menu(self):
        option_2_callback = {
            'By Nation': partial(self.__get_nations_investments),
            'By Person': partial(self.__show_persons_investments),
        }

        self.__make_menu(option_2_callback)

    def __show_ships_with_cargo_to_sell(self):
        ship_mgr = self.get_ship_mgr()

        option_2_callback = {
        }

        for ship_id, ship in ship_mgr.id_2_ship.items():
            if ship.has_cargo():
                option_2_callback[ship.name] = partial(self.__send_packet_to_get_cargo_cnt_and_sell_price, ship_id)

        self.__make_menu(option_2_callback)

        if len(option_2_callback) == 0:
            self.__building_speak(tr('You seem to have no cargo to sell.'))

    def is_window_essential(self, window):
        object_ids = window.get_object_ids()
        if '#console_window' in object_ids or '#options_window' in object_ids:
            return True
        return False

    def pop_some_menus(self, cnt):
        # reset windows if top window is essential
        stacked_windows = self.mgr.get_window_stack().get_stack()
        top_window = stacked_windows[-1]
        if self.is_window_essential(top_window) and len(stacked_windows) != 2:
            self.mgr.get_window_stack().clear()
            self.client.packet_handler.init_essential_windows()

        for i in range(cnt):
            stacked_windows = self.mgr.get_window_stack().get_stack()

            if len(stacked_windows) >= 3:
                top_window = stacked_windows.pop()
                top_window.kill()

                only_show_top_window(self.mgr)


    def __ask_cargo_cnt_to_sell(self, cargo_id, ship_id):

        # ask user to enter cnt
        parcket = SellCargoInShip()
        parcket.cargo_id = cargo_id
        parcket.ship_id = ship_id

        PacketParamsDialog(self.mgr, self.client, ['cnt'], parcket)

    def show_cargo_to_sell_in_ship_menu(self, cargo_to_sell_in_ship):
        cargo_id = cargo_to_sell_in_ship.cargo_id
        cargo_name = cargo_to_sell_in_ship.cargo_name
        cnt = cargo_to_sell_in_ship.cnt
        sell_price = cargo_to_sell_in_ship.sell_price
        modified_sell_price = cargo_to_sell_in_ship.modified_sell_price
        ship_id = cargo_to_sell_in_ship.ship_id

        option_2_callback = {
            f'{tr(cargo_name)} [{cnt}] {sell_price}->{modified_sell_price}': partial(self.__ask_cargo_cnt_to_sell, cargo_id, ship_id),
        }

        self.__make_menu(option_2_callback)


    def __get_graphics(self):
        return self.client.game.graphics

    def __add_building_bg(self, building_name):
        self.__get_role().is_in_building = True
        self.__get_graphics().add_sp_building_bg(building_name)

    def show_market_menu(self):
        self.__add_building_bg('market')

        option_2_callback = {
            'Buy': partial(self.__send_get_available_cargos),
            'Sell': partial(self.__show_ships_with_cargo_to_sell),
            'Investment State': partial(self.__show_investment_state_menu),
            'Invest': partial(self.__show_invest_dialog),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def show_bar_menu(self):
        self.__add_building_bg('bar')

        option_2_callback = {
            'Treat Crew': partial(self.__confirm_treat_crew),
            'Recruit Crew': partial(self.show_ships_to_recruit_crew_menu),
            'Dismiss Crew': partial(self.show_ships_to_dismiss_crew_menu),
            'Meet': partial(self.__get_mate_in_port),
            'Fire Mate': partial(self.__show_mates_to_fire_menu),
            'Waitress': partial(self.__request_to_see_waitress),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def __sell_ship(self, id):
        self.client.send(SellShip(id=id))

    def __confirm_to_sell_ship(self, ship):


        option_2_callback = {
            'Yes': partial(self.__sell_ship, ship.id),
        }
        self.__make_menu(option_2_callback)

        self.__show_one_ship_states(ship)

        self.building_speak(f'{tr("You do want to sell")} {ship.name}?')


    def __show_ships_to_sell(self):
        option_2_callback = {
        }

        for id, ship in self.get_ship_mgr().id_2_ship.items():
            ship_template = sObjectMgr.get_ship_template(ship.ship_template_id)
            sell_price = int(ship_template.buy_price / 2)
            option_2_callback[f'{ship.name} {sell_price}'] = partial(self.__confirm_to_sell_ship, ship)

        self.__make_menu(option_2_callback)

    def __get_ships_to_buy(self):
        self.client.send(pb.GetShipsToBuy())

    def __repair_ship(self, id):
        self.client.send(pb.RepairShip(id=id))

    def __rename_ship(self, id):
        # ask user to enter cnt
        parcket = RenameShip()
        parcket.id = id

        PacketParamsDialog(self.mgr, self.client, ['name'], parcket)

    def __show_ships_to_rename_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__rename_ship, ship.id)

        self.__make_menu(option_2_callback)

    def __show_ships_to_repair_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__repair_ship, ship.id)

        self.__make_menu(option_2_callback)

    def __change_ship_capacity(self, id):
        # ask user to enter cnt
        parcket = pb.ChangeShipCapacity()
        parcket.id = id

        PacketParamsDialog(self.mgr, self.client, ['max_crew', 'max_guns'], parcket)

    def __change_ship_weapon(self, ship_id, cannon_id):
        self.client.send(pb.ChangeShipWeapon(ship_id=ship_id, cannon_id=cannon_id))

    def __show_weapons_menu(self, ship_id):
        option_2_callback = {}

        for cannon in sObjectMgr.get_cannons():
            option_2_callback[f'{tr(cannon.name)} {cannon.price}'] = partial(self.__change_ship_weapon, ship_id, cannon.id)

        self.__make_menu(option_2_callback)

    def __show_ships_to_change_weapon_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__show_weapons_menu, ship.id)

        self.__make_menu(option_2_callback)

    def __show_ships_to_change_capacity_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__change_ship_capacity, ship.id)

        self.__make_menu(option_2_callback)

    def __show_remodel_menu(self):
        option_2_callback = {
            'Name': partial(self.__show_ships_to_rename_menu),
            'Capacity': partial(self.__show_ships_to_change_capacity_menu),
            'Weapon': partial(self.__show_ships_to_change_weapon_menu),
        }

        self.__make_menu(option_2_callback)

    def __show_ships_to_remodel_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__remodel_ship, ship.id)



    def show_dry_dock_menu(self):
        self.__add_building_bg('dry_dock')

        option_2_callback = {
            'Buy Ship': partial(self.__get_ships_to_buy),
            'Repair': partial(self.__show_ships_to_repair_menu),
            'Sell': partial(self.__show_ships_to_sell),
            'Remodel': partial(self.__show_remodel_menu),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def __show_mate_template_panel(self, mate_template):
        if not self.__get_role().has_treated:
            self.building_speak("I suggest that you treat this guy first.")

            return

        dict = {
            'name': tr(mate_template.name),
            'nation': tr(c.Nation(mate_template.nation).name),
            '1': '',
            'navigation/accounting/battle': f'{mate_template.navigation}/{mate_template.accounting}/{mate_template.battle}',
            '2': '',
            'talent in navigation/accounting/battle': f'{mate_template.talent_in_navigation}/{mate_template.talent_in_accounting}/{mate_template.talent_in_battle}',
            'lv in nav/acc/bat': f'{mate_template.lv_in_nav}/{mate_template.lv_in_acc}/{mate_template.lv_in_bat}',
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get figure image
        # get mate image
        if mate_template.img_id.isdigit():
            img_x, img_y = self.__item_img_id_2_xy(int(mate_template.img_id))
        else:
            split_items = mate_template.img_id.split('_')
            img_x = int(split_items[0])
            img_y = int(split_items[1])

        mate_image = self.__figure_x_y_2_image(img_x, img_y)

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=text,
            image=mate_image,
        )

    def __hire_mate(self, mate_template):
        self.client.send(HireMate(mate_template_id=mate_template.id))

    def __get_port(self):
        return sObjectMgr.get_port(self.__get_role().map_id)

    def __treat(self, mate_template):
        port = self.__get_port()

        self.building_speak(
            f"{tr('We have the best')} {tr(port.wine)}. "
            f"{tr('Price is one gold ingot each. Want one?')}"
        )

        pack = pb.Treat()

        PacketParamsDialog(self.mgr, self.client, [], pack)

    def __chat(self, mate_template):
        max_stat_value = max(mate_template.navigation,
                             mate_template.accounting,
                             mate_template.battle
                             )

        if max_stat_value == mate_template.navigation:
            text = f"I'm good at navigation."
        elif max_stat_value == mate_template.accounting:
            text = f"I'm good at accounting."
        else:
            text = f"I'm good at battle."

        self.show_mate_speech(
            mate_template,
            f"{tr('Hello! I am')} {tr(mate_template.name)} {tr('from')} {tr(c.Nation(mate_template.nation).name)}. "
            f"{tr(text)}"
        )

    def __show_mate_menu(self, mate_template):
        option_2_callback = {
            'chat': partial(self.__chat, mate_template),
            'treat': partial(self.__treat, mate_template),
            'inspect': partial(self.__show_mate_template_panel, mate_template),
            'hire': partial(self.__hire_mate, mate_template),
        }

        self.__make_menu(option_2_callback)

    def __accept_trade_request(self, role_id):
        pack = pb.AcceptTradeRequest(role_id=role_id)
        self.client.send(pack)

    def __set_trade_money(self):
        pack = pb.SetTradeMoney()
        PacketParamsDialog(self.mgr, self.client, ['amount'], pack)

    def __set_trade_item(self):
        self.show_items(is_for_trade=True)

    def __confirm_trade(self):
        pack = pb.ConfirmTrade()
        self.client.send(pack)

    def show_trade_start(self, role_id, role_name):
        option_2_callback = {
            'Set Trade Money': partial(self.__set_trade_money),
            'Set Trade Item': partial(self.__set_trade_item),
            'Confirm': partial(self.__confirm_trade),
        }
        self.__make_menu(option_2_callback)

        my_role = self.__get_role()
        my_role.trade_role_id = role_id
        my_role_confired_text = 'Confirmed' if my_role.is_trade_confirmed else ''
        my_role_trade_item_name = sObjectMgr.get_item(my_role.trade_item_id).name \
            if my_role.trade_item_id else ''


        target_role = self.get_graphics().model.get_role_by_id(role_id)
        target_role.trade_role_id = my_role.id
        target_role_confired_text = 'Confirmed' if target_role.is_trade_confirmed else ''
        target_role_trade_item_name = sObjectMgr.get_item(target_role.trade_item_id).name \
            if target_role.trade_item_id else ''

        text = f'{tr("Trading with")} {role_name} \n' \
               f'{tr("You")}: {my_role.trade_money} {tr("coins")}  ' \
               f'{tr(my_role_trade_item_name)}  {tr(my_role_confired_text)} \n'\
               \
               f'{role_name}: {target_role.trade_money} {tr("coins")}   ' \
               f'{tr(target_role_trade_item_name)}  {tr(target_role_confired_text)}'

        MyPanelWindow(
            rect=pygame.Rect((248, 0), (264, 145)),
            ui_manager=self.mgr,
            text=text,
        )

    def show_trade_request(self, role_id,  role_name):
        option_2_callback = {
            f'{tr("Trade with")} {role_name} ?': '',
            'Yes': partial(self.__accept_trade_request, role_id),
        }

        self.__make_menu(option_2_callback)

    def building_speak(self, text):
        self.__building_speak(text)

    def show_mate_speech(self, mate, speech):
        # get image_x and y
        if mate.img_id.isdigit():
            x, y = self.__item_img_id_2_xy(int(mate.img_id))
        else:
            split_items = mate.img_id.split('_')
            x = int(split_items[0])
            y = int(split_items[1])

        # get figure image
        mate_image = self.__figure_x_y_2_image(x, y)

        # make window
        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=tr(speech),
            image=mate_image,
        )

    def show_mates_in_port_menu(self, mate_template=None):
        mates = self.get_mate_mgr().get_mates()
        role_name = self.__get_role().name
        option_2_callback = {
        }

        for mate in mates:
            if mate.name == role_name:
                continue
            speech = "Captain, how's life on land?"
            option_2_callback[f'{mate.name}'] = partial(self.show_mate_speech, mate, speech)
        
        if mate_template and not self.get_mate_mgr().is_mate_in_fleet(mate_template):
            option_2_callback[f'{mate_template.name}'] = partial(self.__show_mate_menu, mate_template)

        self.__make_menu(option_2_callback)

    def __get_mate_in_port(self):
        self.client.send(GetMateInPort())

    def __fire_mate(self, mate):
        self.client.send(FireMate(mate_id=mate.id))

    def __show_ensure_fire_mate_menu(self, mate):
        option_2_callback = {
            'Yes': partial(self.__fire_mate, mate),
        }

        self.__make_menu(option_2_callback)
        self.show_mate_speech(mate, 'You do want to fire me?')

    def __recruit_crew(self, ship_id):
        pack = pb.RecruitCrew()
        pack.ship_id = ship_id

        PacketParamsDialog(self.mgr, self.client, ['cnt'], pack)

    def __dismiss_crew(self, ship_id):
        pack = pb.DismissCrew()
        pack.ship_id = ship_id

        PacketParamsDialog(self.mgr, self.client, ['cnt'], pack)

    def show_ships_to_dismiss_crew_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name} [{ship.now_crew}]'] = partial(self.__dismiss_crew, ship.id)

        self.__make_menu(option_2_callback)

    def __confirm_treat_crew(self):
        pack = pb.TreatCrew()
        PacketParamsDialog(self.mgr, self.client, [], pack)

        self.building_speak(f'{tr("You want to treat the entire crew? Each beer costs")} {c.BEER_COST}.')

    def show_ships_to_recruit_crew_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name} [{ship.now_crew}]'] = partial(self.__recruit_crew, ship.id)

        self.__make_menu(option_2_callback)

    def __investigate_fleet(self, nation_id, fleet_id):
        self.client.send(pb.InvestigateFleet(nation_id=nation_id, fleet_id=fleet_id))

    def __show_fleet_types_to_investigate(self, nation_id, maid):
        option_2_callback = {}
        for fleet in c.Fleet:
            option_2_callback[f'{fleet.name}'] = partial(self.__investigate_fleet, nation_id, fleet.value)

        self.__make_menu(option_2_callback)

        self.show_mate_speech(maid, 'Which fleet?')

    def __tell_story(self, maid):
        self.pop_some_menus(7)
        self.show_mate_speech(maid, 'Wow! Interesting! I wish I could see it with my own eyes.')
        self.__get_role().has_told_story = True

    def __show_one_story_to_tell(self, village, maid):
        option_2_callback = {
            'OK': partial(self.__tell_story, maid),
        }
        self.__make_menu(option_2_callback)

        self.show_one_discovery(village)

    def __show_stories_to_tell(self, maid):
        option_2_callback = {}

        villages = self.__get_villages_in_order()

        for village in villages:
            option_2_callback[village.name] = partial(self.__show_one_story_to_tell, village, maid)

        self.__make_menu(option_2_callback)

    def __show_nations_to_investigate(self, maid):
        if not self.__get_role().has_told_story:
            self.pop_some_menus(4)
            self.show_mate_speech(maid, "Sorry. I'm rather busy right now. Maybe next time?")
        else:
            option_2_callback = {}
            for nation in c.Nation:
                option_2_callback[f'{nation.name}'] = partial(self.__show_fleet_types_to_investigate, nation.value, maid)

            self.__make_menu(option_2_callback)

            self.show_mate_speech(maid, 'Which nation?')

    def show_captain_info(self, pack):
        self.__show_weapon_and_armor_menu(pack)
        self.__show_captain_info_panel(pack)

    def __show_captain_info_panel(self, pack):
        # show captain info panel
        dict = {
            'name': tr(pack.name),
            'nation': tr(c.Nation(pack.nation).name),
            '1': '',
            'navigation/accounting/battle': f'{pack.navigation}/{pack.accounting}/{pack.battle}',
            '2': '',
            'lv in nav/acc/bat': f'{pack.lv_in_nav}/{pack.lv_in_acc}/{pack.lv_in_bat}',
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get figure image
        if pack.img_id.isdigit():
            x, y = self.__item_img_id_2_xy(int(pack.img_id))
        else:
            split_items = pack.img_id.split('_')
            x = int(split_items[0])
            y = int(split_items[1])
        mate_image = self.__figure_x_y_2_image(x, y)
        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=text,
            image=mate_image,
        )

    def __show_weapon_and_armor_menu(self, pack):
        # show weapon and armor menu
        option_2_callback = {}
        weapon_id = pack.weapon
        if weapon_id:
            weapon_item = sObjectMgr.get_item(weapon_id)
            option_2_callback[f'{tr("Weapon")}: {tr(weapon_item.name)}'] = partial(self.__show_one_item,
                                                                       weapon_item,
                                                                       is_for_view_captain=True)
        else:
            option_2_callback[f'{tr("Weapon")}: NA'] = ''
        armor_id = pack.armor
        if armor_id:
            armor_item = sObjectMgr.get_item(armor_id)
            option_2_callback[f'{tr("Armor")}: {tr(armor_item.name)}'] = partial(self.__show_one_item,
                                                                     armor_item,
                                                                     is_for_view_captain=True)
        else:
            option_2_callback[f'{tr("Armor")}: NA'] = ''
        self.__make_menu(option_2_callback)

    def show_waitress_menu(self):
        role = self.__get_role()
        port = sObjectMgr.get_port(role.map_id)
        if port.maid_id:
            maid = sObjectMgr.get_maid(port.maid_id)

            option_2_callback = {
                'Tell Story': partial(self.__show_stories_to_tell, maid),
                'Investigate': partial(self.__show_nations_to_investigate, maid),
            }

            self.__make_menu(option_2_callback)

            self.show_mate_speech(maid, f"How are you?")

        else:
            self.__building_speak('There is no waitress here.')

    def __request_to_see_waitress(self):
        port = self.__get_role().get_port()
        if port.maid_id:
            maid = sObjectMgr.get_maid(port.maid_id)
            self.building_speak(f"{tr('You want to see')} {tr(maid.name)}? "
                                f"{tr('We charge')} {c.WAITRESS_COST}.")

            pack = pb.SeeWaitress()
            PacketParamsDialog(self.mgr, self.client, [], pack)

        else:
            self.__building_speak('There is no waitress here.')

    def __show_mates_to_fire_menu(self):
        mates = self.get_mate_mgr().get_mates()
        option_2_callback = {}
        for mate in mates:

            if mate.name == self.__get_role().name:
                continue

            option_2_callback[f'{mate.name}'] = partial(self.__show_ensure_fire_mate_menu, mate)
        self.__make_menu(option_2_callback)

    def __get_port_info(self):
        self.client.send(pb.GetPortInfo())

    def __sleep(self):
        self.client.send(pb.Sleep())

    def __get_nation_info(self, nation_id):
        self.building_speak('I charge 1000 coins for this information. Is that OK?')

        pack = pb.GetNationInfo()
        pack.nation_id = nation_id
        PacketParamsDialog(self.mgr, self.client, [], pack)

    def __show_wanted_dialogue(self, fleet_type):
        self.building_speak(f"{tr('I know the primary threat for your country at the moment.')} "
                            f"{tr('If you pay')} {c.WANTED_COST}, "
                            f"{tr('I can share with you this information and notify your country that you are dealing with this.')}")

        pack = pb.BuyWanted()
        pack.fleet_type = fleet_type.value
        PacketParamsDialog(self.mgr, self.client, [], pack)

    def __show_wanted_menu(self):
        options = {
            'Merchant Fleet': partial(self.__show_wanted_dialogue, c.Fleet.MERCHANT),
            'Convoy Fleet': partial(self.__show_wanted_dialogue, c.Fleet.CONVOY),
            'Battle Fleet': partial(self.__show_wanted_dialogue, c.Fleet.BATTLE),
        }

        self.__make_menu(options)

    def __buy_treasure_map(self):
        self.building_speak(
            f"{tr('I bought this map from someone a while ago, but never had the time to check it out. I can transfer it to you for')} {c.TREASURE_MAP_COST}."
        )

        pack = pb.BuyTreasureMap()
        PacketParamsDialog(self.mgr, self.client, [], pack)

    def __show_nations_menu_to_get_info(self):
        option_2_callback = {}

        for nation in c.Nation:
            option_2_callback[f'{nation.name}'] = partial(self.__get_nation_info, nation.value)

        self.__make_menu(option_2_callback)

        self.building_speak('Which nation?')

    def __buy_item(self, item_id):
        self.client.send(BuyItem(item_id=item_id))

    def __show_item_to_buy(self, item):
        option_2_callback = {
            'OK': partial(self.__buy_item, item.id),
        }

        self.__make_menu(option_2_callback)

        self.__show_one_item(item, is_for_item_shop=True)

    def __sell_item(self, item_id):
        self.client.send(SellItem(item_id=item_id))

    def __calc_longitude_and_latitude(self, x, y):
        # transform to longitude
        longitude = None
        if x >= 900 and x <= 1980:
            longitude = int((x - 900) / 6)
            longitude = str(longitude) + 'e'
        elif x > 1980:
            longitude = int((900 + 2160 - x) / 6)
            longitude = str(longitude) + 'w'
        else:
            longitude = int((900 - x) / 6)
            longitude = str(longitude) + 'w'

        # transform to latitude
        latitude = None
        if y <= 640:
            latitude = int((640 - y) / 7.2)
            latitude = str(latitude) + 'N'
        else:
            latitude = int((y - 640) / 7.2)
            latitude = str(latitude) + 'S'

        return longitude, latitude

    def show_fleets_investigated(self, fleets_investigated):
        for fleet in fleets_investigated:
            # get maid
            port = sObjectMgr.get_port(self.__get_role().map_id)
            maid = sObjectMgr.get_maid(port.maid_id)

            longitude, latitude = self.__calc_longitude_and_latitude(fleet.now_x, fleet.now_y)
            port_name = sObjectMgr.get_port(fleet.dest_port_id).name
            cargo_name = sObjectMgr.get_cargo_template(fleet.cargo_id).name

            self.show_mate_speech(maid,
              f'{tr("I heard")} {tr(fleet.captain_name)} {tr("was at around")} '
              f'{longitude} {latitude}, {tr("heading to")} {tr(port_name)} '
              f'{tr("with")} {tr(cargo_name)}')

    def show_item_sell_price(self, item_id, price):
        item = sObjectMgr.get_item(item_id)

        option_2_callback = {
            'OK': partial(self.__sell_item, item_id),
        }

        self.__make_menu(option_2_callback)

        self.__show_one_item(item, is_for_item_shop=True)
        self.__building_speak(f"{tr('I can buy this for')} {price}.")

    def show_available_items(self, items_ids, prices):
        option_2_callback = {}

        for id, item_id in enumerate(items_ids):
            item = sObjectMgr.get_item(item_id)
            prcie = prices[id]
            option_2_callback[f'{tr(item.name)} {prcie}'] = partial(self.__show_item_to_buy, item)

        self.__make_menu(option_2_callback)

    def show_persons_investments(self, persons_investments):
        option_2_callback = {}

        for person in persons_investments:
            option_2_callback[f'{person.name} {person.investment}'] = ''

        self.__make_menu(option_2_callback)

    def show_nations_investments(self, nations_investments):
        option_2_callback = {}

        for id, nation in enumerate(c.Nation):
            option_2_callback[f'{tr(nation.name)} {nations_investments[id]}'] = ''

        self.__make_menu(option_2_callback)

    def show_nation_allied_ports(self, port_ids, price_indexes, nation_id):
        port_names = [sObjectMgr.get_port(port_id).name for port_id in port_ids]

        option_2_callback = {
        }

        for id, port_name in enumerate(port_names):
            option_2_callback[f'{tr(port_name)} {price_indexes[id]}'] = ''

        self.__make_menu(option_2_callback)

        # building speak number of allied ports
        self.__building_speak(f'{tr(c.Nation(nation_id).name)} {tr("has")} {len(port_names)} {tr("allied ports at the moment")}.')

    def show_port_info(self, price_index, economy_index, industry_index, allied_nation):

        nation_name = c.Nation(allied_nation).name

        option_2_callback = {
            f'{tr("Price Index")} {price_index}': '',
            f'{tr("Economy Index")} {economy_index}': '',
            f'{tr("Industry Index")} {industry_index}': '',
        }

        self.__make_menu(option_2_callback)

        self.__building_speak(f'{tr("We are currently allied to")} {tr(nation_name)}.')

    def __buy_letter_of_marque(self):
        self.client.send(BuyLetterOfMarque())

    def __buy_tax_free_permit(self):
        self.client.send(BuyTaxFreePermit())

    def __show_letter_of_marque_price(self):

        option_2_callback = {
            "OK": partial(self.__buy_letter_of_marque),
        }

        self.__make_menu(option_2_callback)

        self.__building_speak(f'{tr("Letter of Marque")}  50000. {tr("Is that OK?")}')

    def __show_tax_free_permit_price(self):

        option_2_callback = {
            "OK": partial(self.__buy_tax_free_permit),
        }

        self.__make_menu(option_2_callback)

        self.__building_speak(f'{tr("Tax Free Permit")} {tr("costs")} 50000. {tr("Is that OK?")}')

    def __get_item_sell_price(self, item_id):
        self.client.send(GetItemSellPrice(item_id=item_id))

    def __show_items_to_sell_menu(self):
        role = self.__get_role()
        items_ids = self.__get_role().items
        items = [sObjectMgr.get_item(item_id) for item_id in items_ids]
        option_2_callback = {}

        for item in items:
            count = items_ids.count(item.id)

            if item.id == role.weapon or item.id == role.armor:
                continue

            if count >= 2:
                option_2_callback[f'{tr(item.name)} x {count}'] = partial(self.__get_item_sell_price, item.id)
            else:
                option_2_callback[f'{tr(item.name)}'] = partial(self.__get_item_sell_price, item.id)

        # sort by name
        option_2_callback = dict(sorted(option_2_callback.items(), key=lambda x: x[0]))

        self.__make_menu(option_2_callback)

    def __get_available_items(self):
        self.client.send(GetAvailableItems())

    def __show_ruler_menu(self):
        option_2_callback = {
            'Buy Tax Free Permit': partial(self.__show_tax_free_permit_price),
            'Buy Letter of Marque': partial(self.__show_letter_of_marque_price),
        }

        self.__make_menu(option_2_callback)

        self.building_speak("I'm sorry, the King is busy at the moment. What do you want?")

    def __show_donate_dialog(self):
        self.__building_speak('How many ingots do you want to donate? '
                              'Any amount is appreciated.')

        pack = pb.Donate()
        PacketParamsDialog(self.mgr, self.client, ['ingots_cnt'], pack)

    def __pray(self):
        self.client.send(Pray())
        self.__building_speak('May God bless you in all your endeavors.')

    def __check_balance(self):
        self.client.send(pb.CheckBalance())

    def __show_withdraw_dialog(self):
        self.__building_speak('How much would you like to withdraw?')

        pack = pb.Withdraw()
        PacketParamsDialog(self.mgr, self.client, ['amount'], pack)

    def __show_deposit_dialog(self):
        self.__building_speak('How much would you like to deposit?')

        pack = pb.Deposit()
        PacketParamsDialog(self.mgr, self.client, ['amount'], pack)

    def exit_building(self):
        self.pop_some_menus(20)
        self.get_graphics().remove_sp_building_bg()

        role = self.__get_role()
        self.__get_graphics().change_background_sp_to_port(role.map_id, role.x, role.y)

        role.is_in_building = False

    def __send_sail_request(self):
        self.client.send(Sail())

    def show_msg_panel(self, msg):
        self.building_speak(msg)

    def __show_event_dialogs(self, event):
        name_2_xy = json.loads(event.figure_images)
        dialogues = json.loads(event.dialogues)

        for dialog in dialogues[::-1]:
            speaker = dialog[0]
            speach = dialog[1]

            x, y = name_2_xy[speaker]
            image = self.__figure_x_y_2_image(x, y)

            MyPanelWindow(
                rect=pygame.Rect((59, 12), (350, 400)),
                ui_manager=self.mgr,
                text=tr(speach),
                image=image,
            )

        self.client.send(pb.TriggerEvent())
        self.__get_role().event_id += 1

    def __trigger_event(self, now_building_name):
        # if role port and building matches event
        role = self.__get_role()
        port = role.get_port()
        now_port_name = port.name

        # get event
        event = sObjectMgr.get_event(role.event_id)
        if not event:
            return

        if event.lv > role.get_lv():
            return

        if event.building == 'any':
            if event.port == now_port_name:
                self.__show_event_dialogs(event)
        else:
            if event.building == now_building_name and event.port == now_port_name:
                self.__show_event_dialogs(event)

    def __building_speak(self, text):
        # make window
        MyPanelWindow(
            rect=pygame.Rect((248, -10), (264, 180)),
            ui_manager=self.mgr,
            text=tr(text),
        )

    def __show_confirm_sail_dialog(self):
        flag_ship = self.__get_role().get_flag_ship()
        if not flag_ship:
            self.__building_speak(tr(f"You don't have a flag ship."))
            return

        pack = pb.Sail()
        PacketParamsDialog(self.mgr, self.client, [], pack)

        days = self.__get_role().ship_mgr.calc_days_at_sea()

        self.__building_speak(f'{tr("You can sail for about")} {days} {tr("days")}. '
                              f'{tr("Are you sure you want to sail?")}')

    def __unload_supply(self, ship_id, supply_name):
        pack = pb.UnloadSupply()
        pack.ship_id = ship_id
        pack.supply_name = supply_name

        PacketParamsDialog(self.mgr, self.client, ['cnt'], pack)

    def __load_supply(self, ship_id, supply_name):
        pack = pb.LoadSupply()
        pack.ship_id = ship_id
        pack.supply_name = supply_name

        PacketParamsDialog(self.mgr, self.client, ['cnt'], pack)

    def show_ships_to_unload_supply(self, supply_name):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name} [{ship.food}, {ship.water}, {ship.material}, {ship.cannon}]'] = partial(self.__unload_supply, ship.id, supply_name)

        self.__make_menu(option_2_callback)

    def show_ships_to_load_supply(self, supply_name):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name} [{ship.food}, {ship.water}, {ship.material}, {ship.cannon}]'] = \
                partial(self.__load_supply, ship.id, supply_name)

        self.__make_menu(option_2_callback)

    def __show_unload_supply_menu(self):
        option_2_callback = {
            'Food': partial(self.show_ships_to_unload_supply, 'food'),
            'Water': partial(self.show_ships_to_unload_supply, 'water'),
            'Lumber': partial(self.show_ships_to_unload_supply, 'material'),
            'Shot': partial(self.show_ships_to_unload_supply, 'cannon'),
        }

        self.__make_menu(option_2_callback)

    def __show_load_supply_menu(self):
        option_2_callback = {
            f"{tr('Food')} {c.SUPPLY_2_COST['food']}": partial(self.show_ships_to_load_supply, 'food'),
            f"{tr('Water')} {c.SUPPLY_2_COST['water']}": partial(self.show_ships_to_load_supply, 'water'),
            f"{tr('Lumber')} {c.SUPPLY_2_COST['material']}": partial(self.show_ships_to_load_supply, 'material'),
            f"{tr('Shot')} {c.SUPPLY_2_COST['cannon']}": partial(self.show_ships_to_load_supply, 'cannon'),
        }

        self.__make_menu(option_2_callback)

        self.building_speak(tr('What do you want to load to your ship? Water is free.'))

    def show_harbor_menu(self):
        self.__add_building_bg('harbor')

        option_2_callback = {
            'Sail': partial(self.__show_confirm_sail_dialog),
            'Load Supply': partial(self.__show_load_supply_menu),
            'Unload Supply': partial(self.__show_unload_supply_menu),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def show_inn_menu(self):
        self.__add_building_bg('inn')

        option_2_callback = {
            'Check In': partial(self.__sleep),
            'Port Info': partial(self.__get_port_info),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def show_palace_menu(self):
        self.__add_building_bg('palace')

        option_2_callback = {
            'Meet Ruler': partial(self.__show_ruler_menu),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def show_job_house_menu(self):
        self.__add_building_bg('job_house')

        option_2_callback = {
            'Nation Info': partial(self.__show_nations_menu_to_get_info),
            'Treasure Map': partial(self.__buy_treasure_map),
            'Wanted': partial(self.__show_wanted_menu),
        }

        self.__make_menu(option_2_callback)

    def show_bank_menu(self):
        self.__add_building_bg('bank')

        option_2_callback = {
            'Check Balance': partial(self.__check_balance),
            'Deposit': partial(self.__show_deposit_dialog),
            'Withdraw': partial(self.__show_withdraw_dialog),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def show_item_shop_menu(self):
        self.__add_building_bg('item_shop')

        option_2_callback = {
            'Buy': partial(self.__get_available_items),
            'Sell': partial(self.__show_items_to_sell_menu),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def show_church_menu(self):
        self.__add_building_bg('church')

        option_2_callback = {
            'Pray': partial(self.__pray),
            'Donate': partial(self.__show_donate_dialog),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def show_fortune_house_menu(self):
        self.__add_building_bg('fortune_house')

        option_2_callback = {
            'Life': partial(self.__show_admiral_info),
            '': partial(self.exit_building),
        }

        self.__make_menu(option_2_callback)

    def __pause_effect(self):
        for sound in sAssetMgr.sounds.values():
            sound.set_volume(0)

    def __resume_effect(self):
        for sound in sAssetMgr.sounds.values():
            sound.set_volume(1)

    def __show_effect_menu(self):
        option_2_callback = {
            'Pause': partial(self.__pause_effect),
            'Resume': partial(self.__resume_effect),
        }

        self.__make_menu(option_2_callback)

    def __pause_music(self):
        pygame.mixer.music.set_volume(0)

    def __resume_music(self):
        pygame.mixer.music.set_volume(1)

    def __show_music_menu(self):
        option_2_callback = {
            'Pause': partial(self.__pause_music),
            'Resume': partial(self.__resume_music),
        }

        self.__make_menu(option_2_callback)

    def change_language(self, lan):
        sTr.set_to_language(lan)

        self.mgr.get_window_stack().clear()
        self.client.packet_handler.init_essential_windows()

    def __show_language_menu(self):
        option_2_callback = {
            'English': partial(self.change_language, Language.ENGLISH),
            'Chinese': partial(self.change_language, Language.CHINESE),
        }

        self.__make_menu(option_2_callback)

    def __show_sounds_menu(self):
        option_2_callback = {
            'Effect': partial(self.__show_effect_menu),
            'Music': partial(self.__show_music_menu),
            '': '',
        }

        self.__make_menu(option_2_callback)

    def __exit_game(self):
        self.client.send(Disconnect())

    def __show_one_enemy_ship_states(self, ship):
        ship_template = sObjectMgr.get_ship_template(ship.ship_template_id)

        # type_of_guns
        if ship.type_of_guns:
            gun_name = sObjectMgr.get_cannon(ship.type_of_guns).name
        else:
            gun_name = 'NA'

        dict = {
            'name/type': f'{ship.name}/{tr(ship_template.name)}',
            '1': '',
            'tacking/power': f'{ship.tacking}/{ship.power}',
            'durability': f'{ship.now_durability}/{ship.max_durability}',
            '2': '',
            'capacity': f'{ship.capacity}',
            'guns/max_guns/gun_type': f'{ship.now_guns}/{ship.max_guns}/{tr(gun_name)}',
            'min_crew/crew/max_crew': f'{ship.min_crew}/{ship.now_crew}/{ship.max_crew}',
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get ship image
        ship_image = sAssetMgr.images['ships'][ship_template.name.lower()]

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 430)),
            ui_manager=self.mgr,
            text=text,
            image=ship_image,
        )

    def __show_one_ship_states(self, ship):
        ship_template = sObjectMgr.get_ship_template(ship.ship_template_id)

        self.get_mate_mgr().get_mate(ship.captain)
        print(f'show states for {ship.id}')
        if ship.captain:
            mate = self.get_mate_mgr().get_mate(ship.captain)
            captain_name = mate.name
        else:
            captain_name = 'NA'

        # get chief_navigator
        if ship.chief_navigator:
            mate = self.get_mate_mgr().get_mate(ship.chief_navigator)
            chief_navigator_name = mate.name
        else:
            chief_navigator_name = 'NA'

        # get accountant
        if ship.accountant:
            mate = self.get_mate_mgr().get_mate(ship.accountant)
            accountant_name = mate.name
        else:
            accountant_name = 'NA'

        # get first mate
        if ship.first_mate:
            mate = self.get_mate_mgr().get_mate(ship.first_mate)
            first_mate_name = mate.name
        else:
            first_mate_name = 'NA'

        # get cargo name
        if ship.cargo_id:
            cargo_template = sObjectMgr.get_cargo_template(ship.cargo_id)
            cargo_name = cargo_template.name
        else:
            cargo_name = 'NA'

        # only show 3 aids for flagshi
        if captain_name == self.__get_role().name:
            aids = f'{tr(chief_navigator_name)}/{tr(accountant_name)}/{tr(first_mate_name)}'
        else:
            aids = ''

        # type_of_guns
        if ship.type_of_guns:
            gun_name = sObjectMgr.get_cannon(ship.type_of_guns).name
        else:
            gun_name = 'NA'


        dict = {
            ' ': f'{ship.name}    {tr(ship_template.name)}',
            'captain': f'{tr(captain_name)}',
            'nav/acc/first mate': f'{aids}',
            '1': '',
            'tacking/power/base_speed': f'{ship.tacking}/{ship.power}/{ship.get_base_speed_in_knots()}',
            'durability': f'{ship.now_durability}/{ship.max_durability}',
            '2': '',
            'capacity': f'{ship.capacity}',
            'guns/max_guns/gun_type': f'{ship.now_guns}/{ship.max_guns}/{tr(gun_name)}',
            'min_crew/crew/max_crew': f'{ship.min_crew}/{ship.now_crew}/{ship.max_crew}',
            '3': '',
            'max_cargo': f'{ship.get_max_cargo()}',
            'cargo/cnt': f'{tr(cargo_name)}/{ship.cargo_cnt}',
            'food/water/lumber/shot': f'{ship.food}/{ship.water}/{ship.material}/{ship.cannon}',

        }

        if captain_name != self.__get_role().name:
            del dict['nav/acc/first mate']

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get ship image
        ship_image = sAssetMgr.images['ships'][ship_template.name.lower()]

        # reszie
        # ship_image = pygame.transform.scale(ship_image, (260, 100))

        MyPanelWindow(
            rect=pygame.Rect((59, 0), (350, 500)),
            ui_manager=self.mgr,
            text=text,
            image=ship_image,
        )

    def __dict_2_txt(self, dict):
        text = ''
        for k, v in dict.items():
            if k.isdigit():
                text += f'<br>'
            else:
                if k.startswith(' ') and k.endswith(' '):
                    text += f'{v}<br>'
                else:
                    text += f'{tr(k)}: {v}<br>'
        return text

    def __get_enemy(self):
        return self.client.game.graphics.model.get_enemy()

    def __set_all_ships_target(self, ship_id):
        self.client.send(pb.SetAllShipsTarget(ship_id=ship_id))
        self.__get_role().set_all_ships_target(ship_id)

    def _set_all_ships_target(self):
        enemy = self.__get_enemy()

        option_2_callback = {
        }

        for ship in enemy.ship_mgr.get_ships():
            option_2_callback[f'{ship.name}'] = partial(self.__set_all_ships_target, ship.id)

        self.__make_menu(option_2_callback)

    def ___set_ship_target(self, ship_id, target_ship_id):
        self.client.send(
            pb.SetShipTarget(
                ship_id=ship_id,
                target_ship_id=target_ship_id
            )
        )

        self.__get_role().set_ship_target(ship_id, target_ship_id)

    def __set_ship_target(self, ship_id):
        enemy = self.__get_enemy()

        option_2_callback = {
        }

        for ship in enemy.ship_mgr.get_ships():
            option_2_callback[f'{ship.name}'] = partial(self.___set_ship_target, ship_id, ship.id)

        self.__make_menu(option_2_callback)

    def _set_ship_target(self):
        role = self.__get_role()

        option_2_callback = {
        }

        for ship in role.ship_mgr.get_ships():
            option_2_callback[f'{ship.name}'] = partial(self.__set_ship_target, ship.id)

        self.__make_menu(option_2_callback)

    def ___set_ship_strategy(self, ship_id, attack_method_type):
        self.client.send(
            pb.SetShipStrategy(
                ship_id=ship_id,
                attack_method_type=attack_method_type
            )
        )

        self.__get_role().set_ship_strategy(ship_id, attack_method_type)

    def __set_ship_strategy(self, ship_id):
        option_2_callback = {
            'shoot': partial(self.___set_ship_strategy, ship_id, pb.AttackMethodType.SHOOT),
            'engage': partial(self.___set_ship_strategy, ship_id, pb.AttackMethodType.ENGAGE),
            'flee': partial(self.___set_ship_strategy, ship_id, pb.AttackMethodType.FLEE),
            'hold': partial(self.___set_ship_strategy, ship_id, pb.AttackMethodType.HOLD),
        }

        self.__make_menu(option_2_callback)


    def _set_ship_strategy(self):
        role = self.__get_role()

        option_2_callback = {
        }

        for ship in role.ship_mgr.get_ships():
            option_2_callback[f'{ship.name}'] = partial(self.__set_ship_strategy, ship.id)

        self.__make_menu(option_2_callback)

    def __set_all_ships_strategy(self, strategy):
        self.client.send(pb.SetAllShipsStrategy(attack_method_type=strategy))
        self.__get_role().set_all_ships_strategy(strategy)

    def _set_all_ships_strategy(self):

        option_2_callback = {
            'shoot': partial(self.__set_all_ships_strategy, pb.AttackMethodType.SHOOT),
            'engage': partial(self.__set_all_ships_strategy, pb.AttackMethodType.ENGAGE),
            'flee': partial(self.__set_all_ships_strategy, pb.AttackMethodType.FLEE),
            'hold': partial(self.__set_all_ships_strategy, pb.AttackMethodType.HOLD),
        }

        self.__make_menu(option_2_callback)

    def show_fleet_info(self, ships_template_ids):
        # make window
        rect = pygame.Rect((-20, -20), (c.WINDOW_WIDTH + 40, c.WINDOW_HEIGHT + 40))
        ui_manager = self.mgr
        ui_window = pygame_gui.elements.UIWindow(rect, ui_manager)

        # add bg image to window
        bg_image = sAssetMgr.images['ships']['fleet_info']
        bg_image = pygame.transform.scale(bg_image, (c.WINDOW_WIDTH + 40, c.WINDOW_HEIGHT + 40))
        bg_rect = bg_image.get_rect()

        rect = pygame.Rect((0, 0), (bg_rect.width, bg_rect.height))
        pygame_gui.elements.UIImage(rect, bg_image, ui_manager, container=ui_window)

        # get ships_images
        ships_images = []
        for ship_template_id in ships_template_ids:
            ship_template = sObjectMgr.get_ship_template(ship_template_id)
            ship_img_name = ship_template.img_id.lower()
            ships_images.append(sAssetMgr.images['ships'][ship_img_name])

        # add ships images to window
        # display all ships in two rows
        # if ships cnt is odd, display the first ship to the left and in the middle of the two rows
        ships_cnt = len(ships_images)
        is_cnt_odd = ships_cnt % 2 == 1

        row = -1
        col = -1

        for index, image in enumerate(ships_images):
            image = pygame.transform.scale(image, (120, 90))
            image_width = image.get_rect().width
            image_height = image.get_rect().height

            # if odd, 1st ship placed at the front
            if is_cnt_odd and index == 0:
                my_col = 0
                my_row = 0
                x = my_col * image_width + image_width * ((10 - ships_cnt) // 4) + \
                    image_width // 2
                y = my_row * image_height + c.WINDOW_HEIGHT // 2 - image_height // 2
            else:
                if row == 1:
                    row = 0
                    col += 1
                else:
                    row += 1

                if col == -1:
                    col = 0

                x = col * image_width + image_width * ((10 - ships_cnt) // 4) + \
                    image_width + + image_width // 2
                y = row * image_height + c.WINDOW_HEIGHT // 2 - image_height

            if ships_cnt == 10:
                x -= image_width

            rect = pygame.Rect((x, y), (image_width, image_height))
            pygame_gui.elements.UIImage(rect, image, ui_manager, container=ui_window)

    def __show_fleet(self):
        ships = self.get_ship_mgr().get_ships()
        ships_template_ids = [ship.ship_template_id for ship in ships]
        self.show_fleet_info(ships_template_ids)

    def __view_enemy_captain(self):
        enemy = self.__get_enemy()
        self.__view_captain(enemy.id)

    def __show_fleet_info_menu(self):
        ships = self.get_ship_mgr().get_ships()

        MyFleetPanelWindow(
            rect=pygame.Rect((20, 0), (700, 500)),
            ui_manager=self.mgr,
            ships=list(ships),
        )

    def __show_ship_info_menu(self, is_enemy=False):
        if is_enemy:
            ship_mgr = self.client.game.graphics.model.get_enemy().ship_mgr
        else:
            ship_mgr = self.client.game.graphics.model.role.ship_mgr

        option_2_callback = {
        }

        for id, ship in ship_mgr.id_2_ship.items():
            if is_enemy:
                option_2_callback[f'{ship.name} '] = partial(self.__show_one_enemy_ship_states, ship_mgr.get_ship(id))
            else:

                ship_txt = f'{ship.name}     {ship.get_base_speed_in_knots()} {sTr.tr("knots")}'

                if ship_txt in option_2_callback:
                    print('ship name in dict !!!!!!!')
                    ship_txt += f'({id})'
                else:
                    pass

                option_2_callback[ship_txt] = \
                    partial(self.__show_one_ship_states, ship_mgr.get_ship(id))


        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __get_role(self):
        return self.client.game.graphics.model.role

    def __item_x_y_2_image(self, x, y):
        discoveries_and_items_images = sAssetMgr.images['discoveries_and_items']['discoveries_and_items']
        discovery_surface = pygame.Surface((c.ITEMS_IMAGE_SIZE, c.ITEMS_IMAGE_SIZE))
        x_coord = -c.ITEMS_IMAGE_SIZE * (x - 1)
        y_coord = -c.ITEMS_IMAGE_SIZE * (y - 1)
        rect = pygame.Rect(x_coord, y_coord, c.ITEMS_IMAGE_SIZE, c.ITEMS_IMAGE_SIZE)
        discovery_surface.blit(discoveries_and_items_images, rect)

        return discovery_surface

    def __use_item(self, item_id):
        self.client.send(UseItem(item_id=item_id))

    def __equip_item(self, item_id):
        self.client.send(EquipItem(item_id=item_id))

    def __unequip_item(self, item_id):
        self.client.send(UnequipItem(item_id=item_id))

    def __set_item_for_trade(self, item_id):
        self.client.send(SetTradeItem(item_id=item_id))

    def __item_img_id_2_xy(self, img_id):
        cols = 16

        img_x = (img_id % cols) + 1
        img_y = (img_id // cols) + 1

        return img_x, img_y

    def __show_one_item(self, item, is_equiped=False, is_for_item_shop=False, is_for_view_captain=False):
        # use or equip
        if not is_for_item_shop:
            if item.item_type == c.ItemType.CONSUMABLE.value:
                option_2_callback = {
                    'Use': partial(self.__use_item, item.id),
                }
                self.__make_menu(option_2_callback)
            elif item.item_type in [c.ItemType.WEAPON.value, c.ItemType.ARMOR.value]:
                if is_for_view_captain:
                    pass
                else:
                    if is_equiped:
                        option_2_callback = {
                            'Unequip': partial(self.__unequip_item, item.id),
                        }
                        self.__make_menu(option_2_callback)
                    else:
                        option_2_callback = {
                            'Equip': partial(self.__equip_item, item.id),
                        }
                        self.__make_menu(option_2_callback)

        if item.img_id.isdigit():
            img_x, img_y = self.__item_img_id_2_xy(int(item.img_id))
        else:
            split_items = item.img_id.split('_')
            img_x = int(split_items[0])
            img_y = int(split_items[1])

        # dict
        dict = {
            'name': tr(item.name),
            'description': tr(item.description),
        }

        if item.item_type == c.ItemType.WEAPON.value:
            dict['effect'] = f'{tr("For all ships, shoot and engage damage to targets increased by")} {item.effect}%.'
            dict['lv required'] = f'{tr("Lv required:")} {item.lv}'
        elif item.item_type == c.ItemType.ARMOR.value:
            dict['effect'] = f'{tr("For all ships, Shoot and engage damage from enemy ships reduced by")} {item.effect}%.'
            dict['lv required'] = f'{tr("Lv required:")} {item.lv}'

        # make text from dict
        text = ''
        for k, v in dict.items():
            text += f'{v}<br>'

        # get figure image
        item_img = self.__item_x_y_2_image(img_x, img_y)

        MyPanelWindow(
            rect=pygame.Rect((59, 50), (350, 400)),
            ui_manager=self.mgr,
            text=text,
            image=item_img,
        )

    def show_one_discovery(self, village):

        if village.img_id.isdigit():
            img_x, img_y = self.__item_img_id_2_xy(int(village.img_id))
        else:
            split_items = village.img_id.split('_')
            img_x = int(split_items[0])
            img_y = int(split_items[1])

        # dict
        dict = {
            'name': tr(village.name),
            'description': tr(village.description),
        }

        # make text from dict
        text = ''
        for k, v in dict.items():
            text += f'{v}<br>'

        # get figure image
        item_img = self.__item_x_y_2_image(img_x, img_y)


        MyPanelWindow(
            rect=pygame.Rect((59, -5), (400, 500)),
            ui_manager=self.mgr,
            text=text,
            image=item_img,
        )

    def show_items(self, is_for_trade=False):
        option_2_callback = {}
        items_ids = self.__get_role().items
        role = self.__get_role()

        items_cnt = len(items_ids)

        option_2_callback[f'{items_cnt}/{c.MAX_ITEMS_CNT}'] = ''

        for id in items_ids:
            item = sObjectMgr.get_item(id)

            count = items_ids.count(id)

            is_equiped = 'ON' if id == role.weapon or id == role.armor else ''

            if count >= 2:
                if is_for_trade:
                    option_2_callback[f'{tr(item.name)} x {count} {is_equiped}'] = partial(self.__set_item_for_trade, id)
                else:
                    option_2_callback[f'{tr(item.name)} x {count} {is_equiped}'] = partial(self.__show_one_item, item, is_equiped)
            else:
                if is_for_trade:
                    option_2_callback[f'{tr(item.name)} {is_equiped}'] = partial(self.__set_item_for_trade, id)
                else:
                    option_2_callback[f'{tr(item.name)} {is_equiped}'] = partial(self.__show_one_item, item, is_equiped)

        # sort by name
        option_2_callback = dict(sorted(option_2_callback.items(), key=lambda x: x[0]))

        self.__make_menu(option_2_callback)

    def __show_quest(self):
        event_id = self.__get_role().event_id
        event = sObjectMgr.get_event(event_id)

        if not event:
            self.show_msg_panel('You have completed the quests. Thank you.')
            return

        if event.building == 'any':
            building_name = ''
        else:
            building_name = event.building

        if event.lv > self.__get_role().get_lv():
            self.show_msg_panel(f'Requires lv {event.lv}')
        else:
            self.show_msg_panel(f'{tr("Go to")} {tr(event.port)} {tr(building_name)}.')

    def __get_villages_in_order(self):
        villages = []

        for id in self.__get_role().discovery_mgr.ids_set:
            village = sObjectMgr.get_village(id)
            villages.append(village)

        # sort villages by village.name
        villages = sorted(villages, key=lambda x: x.name)

        return villages

    def __show_discoveries_menu(self):

        option_2_callback = {}

        villages = self.__get_villages_in_order()

        for village in villages:
            option_2_callback[village.name] = partial(self.show_one_discovery, village)

        self.__make_menu(option_2_callback)

    def __rand_x_y_based_on_instrument(self, my_x, my_y):
        role = self.__get_role()
        if c.Item.THEODOLITE.value in role.items:
            distance = 0
        elif c.Item.SEXTANT.value in role.items:
            distance = 5
        elif c.Item.QUADRANT.value in role.items:
            distance = 10
        else:
            distance = 15

        my_x += random.randint(-distance, distance)
        my_y += random.randint(-distance, distance)

        return my_x, my_y

    def __show_wanted(self):
        role = self.__get_role()
        wanted_mate_template_id = role.wanted_mate_template_id

        if wanted_mate_template_id:
            mate_template = sObjectMgr.get_mate_template(wanted_mate_template_id)
            self.show_msg_panel(
                f'{tr(mate_template.name)} '
                f'from {tr(c.Nation(mate_template.nation).name)}!'
            )
        else:
            self.show_msg_panel("It's blank.")

    def __show_treasure_map(self):
        role = self.__get_role()
        if role.treasure_map_id:
            id = role.treasure_map_id
            village = sObjectMgr.get_village(id)
            self.show_msg_panel(f"{tr('There seems to be something around')} "
                                f"{village.latitude} {village.longitude}")
        else:
            self.show_msg_panel("It's blank.")

    def show_port_map(self):
        if not self.__get_role().is_in_port():
            return

        # show window
        graphics = self.__get_graphics()
        port_map_img = graphics.sp_background.image
        port_map = pygame.transform.scale(port_map_img, (c.PORT_MAP_SIZE, c.PORT_MAP_SIZE))
        text = ''

        MyPanelWindow(
            rect=pygame.Rect((10, 10), ((c.PORT_MAP_SIZE + 37), (c.PORT_MAP_SIZE + 37))),
            ui_manager=self.mgr,
            text=text,
            image=port_map,
        )

        # play sound
        sAssetMgr.sounds['map'].play()

    def show_world_map(self):
        # image
        world_map_image = sAssetMgr.images['world_map']['world_map_from_uw2']

        # shrink image
        world_map_image = pygame.transform.scale(world_map_image, (c.WINDOW_WIDTH, c.WINDOW_HEIGHT - 120))  # 720, 360
        world_map_image_rect = world_map_image.get_rect()

        strict_grid_size = world_map_image_rect.width / c.SEEN_GRIDS_COLS
        grid_size = int(strict_grid_size) + 1

        map_mosaic = sAssetMgr.images['world_map']['map_mosaic']
        map_mosaic = pygame.transform.scale(map_mosaic, (grid_size, grid_size))

        # my positiion
        my_position_img = sAssetMgr.images['world_map']['my_position_on_map']
        my_position_img = pygame.transform.scale(my_position_img, (3, 3))

        start_x = 0
        start_y = 0

        matrix = self.__get_role().seen_grids
        # iterate through matrix
        rows, cols = matrix.shape

        # hide unseen_grids
        for x in range(rows):
            for y in range(cols):
                if matrix[x][y] == 0:
                    # paste figure image onto img
                    start_x_y = (start_y + int(y * strict_grid_size), start_x + int(x * strict_grid_size))
                    world_map_image.blit(map_mosaic, start_x_y)

        # get my_x y based on location
        my_x, my_y = self.__get_my_world_xy()

        my_x = int(world_map_image_rect.width * (my_x / c.WORLD_MAP_COLUMNS))
        my_y = int(world_map_image_rect.height * (my_y / c.WORLD_MAP_ROWS))
        print(my_x, my_y)

        # rand x,y based on instrument
        my_x, my_y = self.__rand_x_y_based_on_instrument(my_x, my_y)

        world_map_image.blit(my_position_img, (my_x, my_y))

        MyPanelWindow(
            rect=pygame.Rect((-20, -20), (world_map_image_rect.width + 40, world_map_image_rect.height + 30)),
            ui_manager=self.mgr,
            text='',
            image=world_map_image,
        )

        # sound
        sAssetMgr.sounds['map'].play()

    def __get_my_world_xy(self):
        if self.__get_role().is_in_port():
            port = sObjectMgr.get_port(self.__get_role().map_id)
            my_x = port.x
            my_y = port.y
        else:
            my_x = self.__get_role().x
            my_y = self.__get_role().y
        return my_x, my_y

    def show_available_cargos_menu(self, get_available_cargos_res):
        option_2_callback = {
            f'{tr(cargo.name)} {cargo.price} -> {cargo.cut_price}':
                partial(self.__show_ships_to_load_cargo_menu, cargo.id)
               for cargo in get_available_cargos_res.available_cargos
        }

        self.__make_menu(option_2_callback)

        has_right_tax_free_permit = get_available_cargos_res.has_right_tax_free_permit

        if has_right_tax_free_permit:
            self.__building_speak(tr('Oh, you have a Tax Free Permit! OK. '
                                  'These are the best prices you can have.'))
        else:
            self.__building_speak(tr('Plus tax, these are the best prices you can have.'))

    def __figure_x_y_2_image(self, x=8, y=8):
        figure_width = c.FIGURE_WIDTH
        figure_height = c.FIGURE_HEIGHT

        figures_image = sAssetMgr.images['figures']['figures']
        figure_surface = pygame.Surface((figure_width, figure_height))
        x_coord = -figure_width * (x - 1)
        y_coord = -figure_height * (y - 1)
        rect = pygame.Rect(x_coord, y_coord, figure_width, figure_height)
        figure_surface.blit(figures_image, rect)

        return figure_surface

    def __show_one_mate_states(self, mate):
        if mate.ship_id:

            ship = self.get_ship_mgr().get_ship(mate.ship_id)
            if ship:
                ship_name = ship.name
            else:
                ship_name = 'NA'
        else:
            ship_name = 'NA'

        if mate.duty_type:
            duty_name = c.INT_2_DUTY_NAME[mate.duty_type]
        else:
            duty_name = 'NA'

        s = tr(str(c.Nation(mate.nation).name))
        print(f'xxxxx {s}')

        dict = {
            ' ': f"{tr(mate.name)}",
            '  ': f'{tr(str(c.Nation(mate.nation).name))}',
            '   ': f'{tr(duty_name)} on {ship_name}',
            '1': '',
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get mate image
        if mate.img_id.isdigit():
            img_x, img_y = self.__item_img_id_2_xy(int(mate.img_id))
        else:
            split_items = mate.img_id.split('_')
            img_x = int(split_items[0])
            img_y = int(split_items[1])

        mate_image = self.__figure_x_y_2_image(img_x, img_y)

        MyMatePanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            image=mate_image,
            mate=mate,
            text=text,
        )

    def __measure_coordinate(self):
        my_x, my_y = self.__get_my_world_xy()
        longitude, latitude = self.__calc_longitude_and_latitude(my_x, my_y)
        self.show_msg_panel(f'{longitude}, {latitude}')

    def land(self):
        # send land packet
        self.client.send(pb.Land())

    def try_to_discover(self):
        x = self.client.game.graphics.model.role.x
        y = self.client.game.graphics.model.role.y

        distance = 3

        village_id_in_range = None
        for id, village in sObjectMgr.id_2_village.items():
            if abs(village.x - x) <= distance and abs(village.y - y) <= distance:
                village_id_in_range = id

        print(f'village_id_in_range: {village_id_in_range}')

        if village_id_in_range:
            self.client.send(Discover(village_id=village_id_in_range))

    def __assign_duty(self, mate_id, ship_id, duty_type):
        print(f'mate_id: {mate_id}, ship_id: {ship_id}, duty_type: {duty_type}')

        self.client.send(AssignDuty(mate_id=mate_id, ship_id=ship_id, duty_type=duty_type))

    def __show_ships_to_assign_duty_menu(self, mate):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}
        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__assign_duty, mate.id, ship.id, pb.DutyType.CAPTAIN)

        self.__make_menu(option_2_callback)

    def __set_ration(self):
        # ask user to enter cnt
        pack = pb.SetRoleField()
        pack.key = 'ration'

        PacketParamsDialog(self.mgr, self.client, ['int_value'], pack)

    def __show_duty_types_menu(self, mate):
        option_2_callback = {
            'Captain': partial(self.__show_ships_to_assign_duty_menu, mate),
        }

        flag_ship = self.__get_role().get_flag_ship()
        if flag_ship:
            ship_id = flag_ship.id
            if mate.name != self.__get_role().name:
                option_2_callback['Chief Navigator'] = partial(self.__assign_duty, mate.id, ship_id, pb.DutyType.CHIEF_NAVIGATOR)
                option_2_callback['Accountant'] = partial(self.__assign_duty, mate.id, ship_id, pb.DutyType.ACCOUNTANT)
                option_2_callback['First Mate'] = partial(self.__assign_duty, mate.id, ship_id, pb.DutyType.FIRST_MATE)

        self.__make_menu(option_2_callback)

    def __show_mates_to_assign_duty_menu(self):
        mates = self.get_mate_mgr().get_mates()
        option_2_callback = {}
        for mate in mates:
            option_2_callback[f'{mate.name}'] = partial(self.__show_duty_types_menu, mate)

        self.__make_menu(option_2_callback)

    def __remove_friend(self, role_id):
        pack = pb.RemoveFriend(role_id=role_id)
        self.client.send(pack)

    def __show_friend_menu(self, role_id):
        option_2_callback = {
            'Remove': partial(self.__remove_friend, role_id),
        }
        self.__make_menu(option_2_callback)

    def __show_friends(self, is_enemy):
        option_2_callback = {}

        friends = self.get_friend_mgr().get_friends(is_enemy=is_enemy)
        for friend in friends:
            online_text = 'ON' if friend.is_online else 'OFF'
            option_2_callback[f'{friend.name} {online_text}'] = partial(self.__show_friend_menu, friend.role_id)

        self.__make_menu(option_2_callback)

    def __show_social(self):
        option_2_callback = {
            'Friends': partial(self.__show_friends, False),
            'Enemies': partial(self.__show_friends, True),
        }

        self.__make_menu(option_2_callback)

    def __show_crew_state_menu(self):
        role = self.__get_role()
        option_2_callback = {
            f'{tr("Ration")} {role.ration}': partial(self.__set_ration),
            f'{tr("Morale")} {role.morale}': '',
            f'{tr("Health")} {role.health}': '',
        }
        self.__make_menu(option_2_callback)

    def __show_admiral_info(self):
        role = self.__get_role()
        notorities = role.notorities

        option_2_callback = {
            'Notorities': '',
        }

        for id, notority in enumerate(notorities):
            option_2_callback[f'{tr(c.Nation(id+1).name)} {notority}'] = ''

        self.__make_menu(option_2_callback)


    def __show_mate_info_menu(self):
        mate_mgr = self.client.game.graphics.model.role.mate_mgr

        option_2_callback = {
        }

        for id, mate in mate_mgr.id_2_mate.items():
            option_2_callback[mate.name] = partial(self.__show_one_mate_states, mate_mgr.get_mate(id))

        self.__make_menu(option_2_callback)

    def __show_cargo_cnt_to_load_to_ship_dialog(self, cargo_id, ship_id):
        # ask user to enter cnt
        buy_cargo = BuyCargo()
        buy_cargo.cargo_id = cargo_id
        buy_cargo.ship_id = ship_id

        PacketParamsDialog(self.mgr, self.client, ['cnt'], buy_cargo)

    def __show_sell_prices(self, cargo_id):
        cargo_template = sObjectMgr.get_cargo_template(cargo_id)
        economy_id_2_sell_price = json.loads(cargo_template.sell_price)

        option_2_callback = {}
        for economy_id, sell_price in economy_id_2_sell_price.items():
            option_2_callback[f'{tr(c.MARKETS[int(economy_id)])} {sell_price}'] = ''

        self.__make_menu(option_2_callback)

    def __show_ships_to_load_cargo_menu(self, cargo_id):
        ship_mgr = self.client.game.graphics.model.role.ship_mgr

        option_2_callback = {
            'Sell Prices': partial(self.__show_sell_prices, cargo_id),
        }

        for ship_id, ship in ship_mgr.id_2_ship.items():
            option_2_callback[ship.name] = partial(self.__show_cargo_cnt_to_load_to_ship_dialog, cargo_id, ship_id)

        self.__make_menu(option_2_callback)

    def escape_battle(self):
        battle_npc_id = self.__get_role().battle_npc_id
        battle_role_id = self.__get_role().battle_role_id

        if battle_npc_id:
            self.client.send(EscapeNpcBattle(npc_id=battle_npc_id))
        elif battle_role_id:
            self.client.send(EscapeRoleBattle())

    def all_ships_attack(self):
        self.client.send(AllShipsAttack())

    def __buy_ship(self, template_id):
        self.client.send(BuyShip(template_id=template_id))

    def __show_ship_template(self, template_id):
        ship_template = sObjectMgr.get_ship_template(template_id)

        dict = {
            'type': f'{tr(ship_template.name)}',
            'tacking': f'{ship_template.tacking}',
            'power': f'{ship_template.power}',
            'durability': f'{ship_template.durability}',
            'capacity': f'{ship_template.capacity}',
            'max_guns': f'{ship_template.max_guns}',
            'min_crew/max_crew': f'{ship_template.min_crew}/{ship_template.max_crew}',
            'max_cargo': f'{ship_template.capacity - ship_template.max_crew - ship_template.max_guns}',
            'lv_required': f'{ship_template.lv}',
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get ship image
        ship_image = sAssetMgr.images['ships'][ship_template.name.lower()]

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 430)),
            ui_manager=self.mgr,
            text=text,
            image=ship_image,
        )

    def __show_ship_to_buy(self, template_id, price):
        option_2_callback = {
            'OK': partial(self.__buy_ship, template_id),
        }
        self.__make_menu(option_2_callback)

        self.__show_ship_template(template_id)

        self.__building_speak(f"{price}. {tr('No negotiation please.')}")

    def show_ships_to_buy_menu(self, ships_to_buy):
        option_2_callback = {
        }

        for ship_to_buy in ships_to_buy.ships_to_buy:
            template_id = ship_to_buy.template_id
            ship_template = sObjectMgr.get_ship_template(template_id)

            name = ship_template.name
            price = ship_to_buy.price

            option_2_callback[f'{name}'] = partial(self.__show_ship_to_buy, template_id, price)

        self.__make_menu(option_2_callback)

    def get_graphics(self):
        return self.client.game.graphics

    def __gossip(self, npc_id):
        """only with npc"""
        pack = pb.Gossip(npc_id=npc_id)
        self.client.send(pack)

    def __view_fleet(self, role_id):
        self.client.send(ViewFleet(role_id=role_id))

    def __view_captain(self, role_id):
        self.client.send(ViewCaptain(role_id=role_id))

    def fight_target(self, role):
        graphics = self.get_graphics()

        graphics.model.role.is_moving = False
        graphics.sp_background.start_time = None

        if role.is_npc():
            self.client.send(FightNpc(npc_id=role.id))
        else:
            self.client.send(FightRole(role_id=role.id))

    def enter_building(self):
        if self.__get_role().is_at_sea():
            return

        x = self.__get_role().x
        y = self.__get_role().y

        port_id = self.__get_role().map_id

        for building_id, building_name in c.ID_2_BUILDING_TYPE.items():

            b_x, b_y = sObjectMgr.get_building_xy_in_port(building_id, port_id)

            if building_id == 4:
                print(f'b_x: {b_x}, b_y: {b_y}')
                print(f'x: {x}, y: {y}')

            if x == b_x and y == b_y:
                if sMapMaker.get_time_of_day() == c.TimeType.NIGHT:
                    if building_name not in [c.Building.HARBOR.name.lower(),
                                             c.Building.BAR.name.lower(),
                                             c.Building.INN.name.lower(),
                                             c.Building.FORTUNE_HOUSE.name.lower(),]:
                        mate = self.__get_role().mate_mgr.get_random_mate()
                        self.show_mate_speech(mate, "It's closed!")
                        return

                if sMapMaker.get_time_of_day() != c.TimeType.NIGHT:
                    if building_name == c.Building.FORTUNE_HOUSE.name.lower():
                        mate = self.__get_role().mate_mgr.get_random_mate()
                        self.show_mate_speech(mate, "It's closed!")
                        return


                # enter building
                print(f'enter building: {building_name}')

                # change time if inn entered
                if building_name == c.Building.INN.name.lower():
                    sMapMaker.time_of_day = random.choice(list(c.TimeType))

                # self.__show_market_menu()
                self.get_graphics().sp_background.stop_moving()

                self.pop_some_menus(cnt=1)

                getattr(self, f'show_{building_name}_menu')()

                self.__get_role().is_in_building = True

                self.__building_speak(tr('Hello! How may I help you?'))

                self.__trigger_event(building_name)

                return

    def __request_trade(self, role_id):
        self.client.send(RequestTrade(role_id=role_id))

    def __add_friend(self, role, is_enemy):
        pack = pb.AddFriend(
            role_id=role.id,
            name=role.name,
            is_enemy=is_enemy,
        )
        self.client.send(pack)

    def show_role_menu(self, role):
        my_role = self.__get_role()
        if my_role.can_inspect(role):
            option_2_callback = {
                f'{role.name}': '',
                'View Fleet': partial(self.__view_fleet, role.id),
                'Gossip ': partial(self.__gossip, role.id),
                'View Captain': partial(self.__view_captain, role.id),
                'Fight': partial(self.fight_target, role),
            }

            if role.is_role():
                del option_2_callback['Gossip ']
                if my_role.is_in_port():
                    del option_2_callback['Fight']
                    option_2_callback['Request Trade'] = partial(self.__request_trade, role.id)

                option_2_callback['Add to Friends'] = partial(self.__add_friend, role, is_enemy=False)
                option_2_callback['Add to Enemies'] = partial(self.__add_friend, role, is_enemy=True)

            self.__make_menu(option_2_callback)
        else:
            mate = my_role.get_flag_ship().get_captain()
            self.show_mate_speech(mate, "It's too far away!")

    def enter_port(self):
        # get nearby port_id
        role = self.__get_role()
        role.stop_moving()

        nearby_port_id = None
        distance = 3
        for id, port in sObjectMgr.id_2_port.items():
            if abs(port.x - role.x) <= distance and abs(port.y - role.y) <= distance:
                nearby_port_id = id

        if nearby_port_id:
            self.client.send(EnterPort(id=nearby_port_id))
        else:
            print('no port to call!')

    def show_buildings_menu(self):
        option_2_callback = {
            'Market': partial(self.show_market_menu),
            'Bar': partial(self.show_bar_menu),
            'Dry Dock': partial(self.show_dry_dock_menu),
            'Harbor': partial(self.show_harbor_menu),
            'Inn': partial(self.show_inn_menu),
            'Palace': partial(self.show_palace_menu),
            'Job House': partial(self.show_job_house_menu),
            'Bank': partial(self.show_bank_menu),
            'Item Shop': partial(self.show_item_shop_menu),
            'Church': partial(self.show_church_menu),
            'Fortune House': partial(self.show_fortune_house_menu),
            'Misc': '',
        }

        self.__make_menu(option_2_callback)

    def show_options_menu(self):
        option_2_callback = {
            'Language(J)': partial(self.__show_language_menu),
            'Sounds': partial(self.__show_sounds_menu),
            'Exit': partial(self.__exit_game),
        }

        self.__make_menu(option_2_callback)

    def show_fight_menu(self):

        if not self.__get_role().is_in_battle():
            self.show_msg_panel(tr('You are not in battle.'))
            return

        option_2_callback = {
            'View Enemy Captain': partial(self.__view_enemy_captain),
            'View Enemy Ships': partial(self.__show_ship_info_menu, is_enemy=True),
            'All Ships Target': partial(self._set_all_ships_target),
            'All Ships Strategy': partial(self._set_all_ships_strategy),
            'Ship Target': partial(self._set_ship_target),
            'Ship Strategy': partial(self._set_ship_strategy),
            'Escape Battle': partial(self.escape_battle),
        }

        self.__make_menu(option_2_callback)

    def show_cmds_menu(self):
        option_2_callback = {
            'Enter/Exit Building (F)': partial(self.enter_building),
            'Enter Port (P)': partial(self.enter_port),
            'Search (G)': partial(self.try_to_discover),
            'Land (L)': partial(self.land),
            'Measure Cooridinate': partial(self.__measure_coordinate),
        }

        self.__make_menu(option_2_callback)

    def show_items_menu(self):
        option_2_callback = {
            'Items': partial(self.show_items),
            'Discoveries': partial(self.__show_discoveries_menu),
            'Quest': partial(self.__show_quest),
            'Treasure Map': partial(self.__show_treasure_map),
            'Wanted': partial(self.__show_wanted),
            'World Map(M)': partial(self.show_world_map),
            'Port Map(N)': partial(self.show_port_map),
        }

        self.__make_menu(option_2_callback)

    def show_mates_menu(self):
        option_2_callback = {
            'Mate Info': partial(self.__show_mate_info_menu),
            'Assign Duty': partial(self.__show_mates_to_assign_duty_menu),
            'Crew': partial(self.__show_crew_state_menu),
            'Social': partial(self.__show_social),
        }

        self.__make_menu(option_2_callback)

    def show_ships_menu(self):
        option_2_callback = {
            'Fleet': partial(self.__show_fleet),
            'Fleet Info': partial(self.__show_fleet_info_menu),
            'Ship Info': partial(self.__show_ship_info_menu),
        }

        self.__make_menu(option_2_callback)


