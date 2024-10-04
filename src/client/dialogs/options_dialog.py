import random
import pygame_gui
import pygame
from functools import partial

import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client\dialogs')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\client')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

from login_pb2 import *
import login_pb2 as pb
from my_ui_elements import MyButton, only_show_top_window
from create_account_dialog import CreateAccountDialog
from packet_params_dialog import PacketParamsDialog
from my_ui_elements import MyMenuWindow, MyPanelWindow
from asset_mgr import sAssetMgr
from map_maker import sMapMaker

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
        buttons_texts = ['Buildings', 'Options', 'Fight', 'Cmds', 'Items', 'Mates', 'Ships']

        for id, button_text in enumerate(buttons_texts):
            MyButton(
                relative_rect=pygame.Rect((0 + id * 100, 0), (120, 60)),
                text=button_text,
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
        MyMenuWindow(
            title='',
            option_2_callback=dict,
            mgr=self.mgr
        )


    def __send_get_available_cargos(self):
        self.client.send(GetAvailableCargos())

    def get_ship_mgr(self):
        return self.client.game.graphics.model.role.ship_mgr

    def get_mate_mgr(self):
        return self.client.game.graphics.model.role.mate_mgr

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

        self.building_speak("You want to invest?")

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
            self.__building_speak('You seem to have no cargo to sell.')

    def pop_some_menus(self, cnt):
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
            f'{cargo_name} [{cnt}] {sell_price}->{modified_sell_price}': partial(self.__ask_cargo_cnt_to_sell, cargo_id, ship_id),
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
            'Recruit Crew': partial(self.__show_ships_to_recruit_crew_menu),
            'Dismiss Crew': partial(self.__show_ships_to_dismiss_crew_menu),
            'Meet': partial(self.__get_mate_in_port),
            'Fire Mate': partial(self.__show_mates_to_fire_menu),
            'Waitress': partial(self.__show_waitress_menu),
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

        self.building_speak(f'Are you sure you want to sell {ship.name}?')


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
            option_2_callback[f'{cannon.name} {cannon.price}'] = partial(self.__change_ship_weapon, ship_id, cannon.id)

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

        self.__make_menu(option_2_callback)

    def show_dry_dock_menu(self):
        self.__add_building_bg('dry_dock')

        option_2_callback = {
            'Buy Ship': partial(self.__get_ships_to_buy),
            'Repair': partial(self.__show_ships_to_repair_menu),
            'Sell': partial(self.__show_ships_to_sell),
            'Remodel': partial(self.__show_remodel_menu),
            '': partial(self.exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_mate_template_panel(self, mate_template):
        if not self.__get_role().has_treated:
            self.building_speak("I suggest that you treat this guy first.")

            return

        dict = {
            'name': mate_template.name,
            'nation': mate_template.nation,
            '1': '',
            'navigation/accounting/battle': f'{mate_template.navigation}/{mate_template.accounting}/{mate_template.battle}',
            '2': '',
            'talent in navigation/accounting/battle': f'{mate_template.talent_in_navigation}/{mate_template.talent_in_accounting}/{mate_template.talent_in_battle}',
            'lv in nav/acc/bat': f'{mate_template.lv_in_nav}/{mate_template.lv_in_acc}/{mate_template.lv_in_bat}',
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get figure image
        split_items = mate_template.img_id.split('_')
        x = int(split_items[0])
        y = int(split_items[1])

        mate_image = self.__figure_x_y_2_image(x, y)

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=text,
            image=mate_image,
        )

    def __hire_mate(self, mate_template):
        self.client.send(HireMate(mate_template_id=mate_template.id))

    def __treat(self, mate_template):
        self.building_speak(
            f"We have the best brandy in the world. "
            f"Price is one gold ingot each. "
            f"Want one? ")

        pack = pb.Treat()

        PacketParamsDialog(self.mgr, self.client, [], pack)

    def __gossip(self, mate_template):
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
            f"How are you? I'm {mate_template.name} from {c.Nation(mate_template.nation).name}. "
            f"{text}"
        )

    def __show_mate_menu(self, mate_template):
        option_2_callback = {
            'gossip': partial(self.__gossip, mate_template),
            'treat': partial(self.__treat, mate_template),
            'inspect': partial(self.__show_mate_template_panel, mate_template),
            'hire': partial(self.__hire_mate, mate_template),
        }

        self.__make_menu(option_2_callback)

    def building_speak(self, text):
        self.__building_speak(text)

    def show_mate_speech(self, mate, speech):
        # get image_x and y
        split_items = mate.img_id.split('_')
        x = int(split_items[0])
        y = int(split_items[1])

        # get figure image
        mate_image = self.__figure_x_y_2_image(x, y)

        # make window
        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=speech,
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
            speech = "Captain, how's life in port? "
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
        self.show_mate_speech(mate, 'Are you sure you want to fire me?')

    def __recruit_crew(self, ship_id):
        pack = pb.RecruitCrew()
        pack.ship_id = ship_id

        PacketParamsDialog(self.mgr, self.client, ['cnt'], pack)

    def __dismiss_crew(self, ship_id):
        pack = pb.DismissCrew()
        pack.ship_id = ship_id

        PacketParamsDialog(self.mgr, self.client, ['cnt'], pack)

    def __show_ships_to_dismiss_crew_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__dismiss_crew, ship.id)

        self.__make_menu(option_2_callback)

    def __confirm_treat_crew(self):
        pack = pb.TreatCrew()
        PacketParamsDialog(self.mgr, self.client, [], pack)

        self.building_speak(f'You want to treat the entire crew? Our beer is {c.BEER_COST} each.')

    def __show_ships_to_recruit_crew_menu(self):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__recruit_crew, ship.id)

        self.__make_menu(option_2_callback)

    def __investigate_fleet(self, nation_id, fleet_id):
        self.client.send(pb.InvestigateFleet(nation_id=nation_id, fleet_id=fleet_id))

    def __show_fleet_types_to_investigate(self, nation_id, maid):
        option_2_callback = {}
        for fleet in c.Fleet:
            option_2_callback[f'{fleet.name}'] = partial(self.__investigate_fleet, nation_id, fleet.value)

        self.__make_menu(option_2_callback)

        self.show_mate_speech(maid, 'Which fleet?')

    def __show_nations_to_investigate(self, maid):
        option_2_callback = {}
        for nation in c.Nation:
            option_2_callback[f'{nation.name}'] = partial(self.__show_fleet_types_to_investigate, nation.value, maid)

        self.__make_menu(option_2_callback)

        self.show_mate_speech(maid, 'Which nation?')

    def __show_waitress_menu(self):
        role = self.__get_role()
        port = sObjectMgr.get_port(role.map_id)
        if port.maid_id:
            maid = sObjectMgr.get_maid(port.maid_id)

            option_2_callback = {
                'Ask Info': '',
                'Investigate': partial(self.__show_nations_to_investigate, maid),
                'Tell Story': '',
            }

            self.__make_menu(option_2_callback)

            self.show_mate_speech(maid, f"I'm {maid.name}. How are you?")

        else:
            self.__building_speak('There is no waitress in this port.')



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
              f'I heard {fleet.captain_name} was at around '
              f'{longitude} {latitude}, heading to {port_name} '
              f'with {cargo_name}')

    def show_item_sell_price(self, item_id, price):
        item = sObjectMgr.get_item(item_id)

        option_2_callback = {
            'OK': partial(self.__sell_item, item_id),
        }

        self.__make_menu(option_2_callback)

        self.__show_one_item(item, is_for_item_shop=True)
        self.__building_speak(f'I want to buy this for {price}.')

    def show_available_items(self, items_ids, prices):
        option_2_callback = {}

        for id, item_id in enumerate(items_ids):
            item = sObjectMgr.get_item(item_id)
            prcie = prices[id]
            option_2_callback[f'{item.name} {prcie}'] = partial(self.__show_item_to_buy, item)

        self.__make_menu(option_2_callback)

    def show_persons_investments(self, persons_investments):
        option_2_callback = {}

        for person in persons_investments:
            option_2_callback[f'{person.name} {person.investment}'] = ''

        self.__make_menu(option_2_callback)

    def show_nations_investments(self, nations_investments):
        option_2_callback = {}

        for id, nation in enumerate(c.Nation):
            option_2_callback[f'{nation.name} {nations_investments[id]}'] = ''

        self.__make_menu(option_2_callback)

    def show_nation_allied_ports(self, port_ids, price_indexes, nation_id):
        port_names = [sObjectMgr.get_port(port_id).name for port_id in port_ids]

        option_2_callback = {
        }

        for id, port_name in enumerate(port_names):
            option_2_callback[f'{port_name} {price_indexes[id]}'] = ''

        self.__make_menu(option_2_callback)

        # building speak number of allied ports
        self.__building_speak(f'{c.Nation(nation_id).name} has {len(port_names)} allied ports at the moment.')

    def show_port_info(self, price_index, economy_index, industry_index, allied_nation):

        nation_name = c.Nation(allied_nation).name

        option_2_callback = {
            f'Price Index {price_index}': '',
            f'Economy Index {economy_index}': '',
            f'Industry Index {industry_index}': '',
        }

        self.__make_menu(option_2_callback)

        self.__building_speak(f'We are allied to {nation_name} at the moment.')

    def __buy_letter_of_marque(self):
        self.client.send(BuyLetterOfMarque())

    def __buy_tax_free_permit(self):
        self.client.send(BuyTaxFreePermit())

    def __show_letter_of_marque_price(self):

        option_2_callback = {
            "OK": partial(self.__buy_letter_of_marque),
        }

        self.__make_menu(option_2_callback)

        self.__building_speak('Letter of Marque costs 50000 coins. Is that OK?')

    def __show_tax_free_permit_price(self):

        option_2_callback = {
            "OK": partial(self.__buy_tax_free_permit),
        }

        self.__make_menu(option_2_callback)

        self.__building_speak('Tax Free Permit costs 50000 coins. Is that OK?')

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
                option_2_callback[f'{item.name} x {count}'] = partial(self.__get_item_sell_price, item.id)
            else:
                option_2_callback[f'{item.name}'] = partial(self.__get_item_sell_price, item.id)

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

        self.building_speak("I'm sorry, but the King is busy at the moment. What do you want?")

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
        self.pop_some_menus(5)
        self.__get_graphics().add_port_npcs(self.__get_role().map_id)
        self.get_graphics().remove_sp_building_bg()

        role = self.__get_role()
        self.__get_graphics().change_background_sp_to_port(role.map_id, role.x, role.y)

        role.is_in_building = False

    def __send_sail_request(self):
        self.client.send(Sail())

    def __building_speak(self, text):
        # make window
        MyPanelWindow(
            rect=pygame.Rect((248, 0), (264, 124)),
            ui_manager=self.mgr,
            text=text,
        )

    def __show_confirm_sail_dialog(self):
        flag_ship = self.__get_role().get_flag_ship()
        if not flag_ship:
            self.__building_speak(f"You don't have a flag ship. ")
            return

        pack = pb.Sail()
        PacketParamsDialog(self.mgr, self.client, [], pack)

        days = self.__get_role().ship_mgr.calc_days_at_sea()

        self.__building_speak(f'You can sail for about {days} days. '
                              f'Are you sure you want to sail?')

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

    def __show_ships_to_unload_supply(self, supply_name):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__unload_supply, ship.id, supply_name)

        self.__make_menu(option_2_callback)

    def __show_ships_to_load_supply(self, supply_name):
        ships = self.get_ship_mgr().get_ships()
        option_2_callback = {}

        for ship in ships:
            option_2_callback[f'{ship.name}'] = partial(self.__load_supply, ship.id, supply_name)

        self.__make_menu(option_2_callback)

    def __show_unload_supply_menu(self):
        option_2_callback = {
            'Food': partial(self.__show_ships_to_unload_supply, 'food'),
            'Water': partial(self.__show_ships_to_unload_supply, 'water'),
            'Material': partial(self.__show_ships_to_unload_supply, 'material'),
            'Cannon': partial(self.__show_ships_to_unload_supply, 'cannon'),
        }

        self.__make_menu(option_2_callback)

    def __show_load_supply_menu(self):
        option_2_callback = {
            f"Food {c.SUPPLY_2_COST['food']}": partial(self.__show_ships_to_load_supply, 'food'),
            f"Water {c.SUPPLY_2_COST['water']}": partial(self.__show_ships_to_load_supply, 'water'),
            f"Material {c.SUPPLY_2_COST['material']}": partial(self.__show_ships_to_load_supply, 'material'),
            f"Cannon {c.SUPPLY_2_COST['cannon']}": partial(self.__show_ships_to_load_supply, 'cannon'),
        }

        self.__make_menu(option_2_callback)

        self.building_speak('What do you want to load to your ship? Water is free.')

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
            'Sleep': partial(self.__sleep),
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
            '': partial(self.exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

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

    def __exit_game(self):

        self.client.send(Disconnect())

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
            aids = f'{chief_navigator_name}/{accountant_name}/{first_mate_name}'
        else:
            aids = ''

        # type_of_guns
        if ship.type_of_guns:
            gun_name = sObjectMgr.get_cannon(ship.type_of_guns).name
        else:
            gun_name = 'NA'

        dict = {
            'name/type/captain': f'{ship.name}/{ship_template.name}/{captain_name}',
            'nav/acc/first mate': f'{aids}',
            '1': '',
            'tacking/power/speed': f'{ship.tacking}/{ship.power}',
            'durability': f'{ship.now_durability}/{ship.max_durability}',
            '2': '',
            'capacity': f'{ship.capacity}',
            'guns/max_guns/gun_type': f'{ship.now_guns}/{ship.max_guns}/{gun_name}',
            'min_crew/crew/max_crew': f'{ship.min_crew}/{ship.now_crew}/{ship.max_crew}',
            'max_cargo': f'{ship.get_max_cargo()}',
            'cargo/cnt': f'{cargo_name}/{ship.cargo_cnt}',
            'food/water/lumber/shot': f'{ship.food}/{ship.water}/{ship.material}/{ship.cannon}',

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

    def __dict_2_txt(self, dict):
        text = ''
        for k, v in dict.items():
            if k.isdigit():
                text += f'<br>'
            else:
                text += f'{k}: {v}<br>'
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

    def __show_battle_states(self):
        my_ships = self.get_ship_mgr().get_ships()
        enemy_ships = self.__get_enemy().ship_mgr.get_ships()

        text = 'num  durability  crew target strategy <br>'


        for ship in my_ships:
            target_name = ship.target_ship.name if ship.target_ship else ''
            strategy_name = c.STRATEGY_2_TEXT[ship.strategy] if ship.strategy is not None else ''

            text += f'<br>{ship.name}  {ship.now_durability}  ' \
                    f'{ship.now_crew}  {target_name}  {strategy_name} '

        text += '<br>'

        for ship in enemy_ships:
            text += f'<br>{ship.name}  {ship.now_durability}  ' \
                    f'{ship.now_crew}  '

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=text,
        )

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

            rect = pygame.Rect((x, y), (image_width, image_height))
            pygame_gui.elements.UIImage(rect, image, ui_manager, container=ui_window)

    def __show_fleet_info(self):
        ships = self.get_ship_mgr().get_ships()
        ships_template_ids = [ship.ship_template_id for ship in ships]
        self.show_fleet_info(ships_template_ids)

    def __show_ship_info_menu(self, is_enemy=False):
        if is_enemy:
            ship_mgr = self.client.game.graphics.model.get_enemy().ship_mgr
        else:
            ship_mgr = self.client.game.graphics.model.role.ship_mgr

        print('#' * 10)
        print(ship_mgr.id_2_ship)

        option_2_callback = {
        }

        for id, ship in ship_mgr.id_2_ship.items():
            print(f'ship name: {ship.name}')
            option_2_callback[f'{ship.name}'] = partial(self.__show_one_ship_states, ship_mgr.get_ship(id))


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

    def __show_one_item(self, item, is_equiped=False, is_for_item_shop=False):
        # use or equip
        if not is_for_item_shop:
            if item.item_type == c.ItemType.CONSUMABLE.value:
                option_2_callback = {
                    'Use': partial(self.__use_item, item.id),
                }
                self.__make_menu(option_2_callback)
            elif item.item_type in [c.ItemType.WEAPON.value, c.ItemType.ARMOR.value]:
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


        split_items = item.img_id.split('_')
        img_x = int(split_items[0])
        img_y = int(split_items[1])

        # dict
        dict = {
            'name': item.name,
            'description': item.description,
        }

        if item.item_type == c.ItemType.WEAPON.value:
            dict['effect'] = f'For all ships, shoot and engage damage to targets increased by {item.effect}%.'
        elif item.item_type == c.ItemType.ARMOR.value:
            dict['effect'] = f'For all ships, Shoot and engage damage from enemy ships reduced by {item.effect}%.'

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



    def __show_one_discovery(self, village):

        split_items = village.img_id.split('_')
        img_x = int(split_items[0])
        img_y = int(split_items[1])

        # dict
        dict = {
            'name': village.name,
            'description': village.description,
        }

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

    def show_items(self):
        option_2_callback = {}
        items_ids = self.__get_role().items
        role = self.__get_role()

        for id in items_ids:
            item = sObjectMgr.get_item(id)

            count = items_ids.count(id)

            is_equiped = 'ON' if id == role.weapon or id == role.armor else ''

            if count >= 2:
                option_2_callback[f'{item.name} x {count} {is_equiped}'] = partial(self.__show_one_item, item, is_equiped)
            else:
                option_2_callback[f'{item.name} {is_equiped}'] = partial(self.__show_one_item, item, is_equiped)

        # sort by name
        option_2_callback = dict(sorted(option_2_callback.items(), key=lambda x: x[0]))

        self.__make_menu(option_2_callback)

    def __show_discoveries_menu(self):

        option_2_callback = {}

        for id in self.__get_role().discovery_mgr.ids_set:
            village = sObjectMgr.get_village(id)
            option_2_callback[village.name] = partial(self.__show_one_discovery, village)

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

    def __show_world_map(self):
        # image
        world_map_image = sAssetMgr.images['world_map']['world_map_from_uw2']

        # shrink image
        world_map_image = pygame.transform.scale(world_map_image, (c.WINDOW_WIDTH, c.WINDOW_HEIGHT - 80))  # 800, 400

        grid_size = 13
        strict_grid_size = 12.5

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

        # for x in range(rows):
        #     for y in range(cols):
        #         if matrix[x][y] == 0:
        #             # paste figure image onto img
        #             start_x_y = (start_y + int(y * strict_grid_size), start_x + int(x * strict_grid_size))
        #             world_map_image.blit(map_mosaic, start_x_y)

        # get my_x y based on location
        if self.__get_role().is_in_port():
            port = sObjectMgr.get_port(self.__get_role().map_id)
            my_x = port.x
            my_y = port.y
        else:
            my_x = self.__get_role().x
            my_y = self.__get_role().y

        my_x = int(720 * (my_x / 2160))
        my_y = int(400 * (my_y / 1080))
        print(my_x, my_y)

        # rand x,y based on instrument
        my_x, my_y = self.__rand_x_y_based_on_instrument(my_x, my_y)

        world_map_image.blit(my_position_img, (my_x, my_y))


        image_rect = world_map_image.get_rect()
        text = ''

        MyPanelWindow(
            rect=pygame.Rect((-20, -20), (image_rect.width + 40, image_rect.height + 30)),
            ui_manager=self.mgr,
            text=text,
            image=world_map_image,
        )

        # sound
        sAssetMgr.sounds['map'].play()

    def show_available_cargos_menu(self, get_available_cargos_res):
        option_2_callback = {
            f'{cargo.name} {cargo.price} -> {cargo.cut_price}':
                partial(self.__show_ships_to_load_cargo_menu, cargo.id)
               for cargo in get_available_cargos_res.available_cargos
        }

        self.__make_menu(option_2_callback)

        #
        have_tax_free_permit = c.Item.TAX_FREE_PERMIT.value in self.__get_role().items

        if self.__get_role().has_tax_free_permit():
            self.__building_speak('Oh, you have a Tax Free Permit! OK. '
                                  'These are the best prices you can have.')
        else:
            self.__building_speak('Plus tax, these are the best prices you can have.')

    def __figure_x_y_2_image(self, x=8, y=8):
        figure_width = 65
        figure_height = 81

        figures_image = sAssetMgr.images['figures']['figures']
        figure_surface = pygame.Surface((figure_width, figure_height))
        x_coord = -figure_width * (x - 1) - 3
        y_coord = -figure_height * (y - 1) - 3
        rect = pygame.Rect(x_coord, y_coord, figure_width, figure_height)
        figure_surface.blit(figures_image, rect)

        return figure_surface

    def __show_one_mate_states(self, mate):
        if mate.ship_id:

            ship = self.get_ship_mgr().get_ship(mate.ship_id)
            ship_name = ship.name
        else:
            ship_name = 'NA'

        if mate.duty_type:
            duty_name = c.INT_2_DUTY_NAME[mate.duty_type]
        else:
            duty_name = 'NA'

        print(f'mate.duty_type: {mate.duty_type}')
        print(f'mate.ship_id: {mate.ship_id}')

        dict = {
            'name/nation': f"{mate.name}/{c.Nation(mate.nation).name}",
            'duty/ship': f'{duty_name}/{ship_name}',
            '1': '',
            'lv in nav/acc/bat': f"{mate.lv_in_nav}/{mate.lv_in_acc}/{mate.lv_in_bat}",
            '2': '',
            'xp in nav/acc/bat': f"{mate.xp_in_nav}/{mate.xp_in_acc}/{mate.xp_in_bat}",
            '3': '',
            'navigation/accounting/battle': f"{mate.navigation}/{mate.accounting}/{mate.battle}",
            '4': '',
            'talent in navigation/accounting/battle':
                f"{mate.talent_in_navigation}/{mate.talent_in_accounting}/{mate.talent_in_battle}",
        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get ship image
        split_items = mate.img_id.split('_')
        x = int(split_items[0])
        y = int(split_items[1])

        mate_image = self.__figure_x_y_2_image(x, y)

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
            ui_manager=self.mgr,
            text=text,
            image=mate_image,
        )

    def __try_to_discover(self):
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
        flag_ship = self.__get_role().get_flag_ship()
        ship_id = flag_ship.id
        option_2_callback = {
            'Captain': partial(self.__show_ships_to_assign_duty_menu, mate),
        }

        if mate.name != self.__get_role().name:
            option_2_callback['Navigator'] = partial(self.__assign_duty, mate.id, ship_id, pb.DutyType.CHIEF_NAVIGATOR)
            option_2_callback['Accountant'] = partial(self.__assign_duty, mate.id, ship_id, pb.DutyType.ACCOUNTANT)
            option_2_callback['First Mate'] = partial(self.__assign_duty, mate.id, ship_id, pb.DutyType.FIRST_MATE)

        self.__make_menu(option_2_callback)

    def __show_mates_to_assign_duty_menu(self):
        mates = self.get_mate_mgr().get_mates()
        option_2_callback = {}
        for mate in mates:
            option_2_callback[f'{mate.name}'] = partial(self.__show_duty_types_menu, mate)

        self.__make_menu(option_2_callback)

    def __show_crew_state_menu(self):
        role = self.__get_role()
        option_2_callback = {
            f'Ration {role.ration}': partial(self.__set_ration),
            f'Morale {role.morale}': '',
            f'Health {role.health}': '',
        }
        self.__make_menu(option_2_callback)

    def __show_admiral_info(self):
        role = self.__get_role()
        notorities = role.notorities

        option_2_callback = {
            'Notorities': '',
        }

        for id, notority in enumerate(notorities):
            option_2_callback[f'{c.Nation(id+1).name} {notority}'] = ''

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

    def __show_ships_to_load_cargo_menu(self, cargo_id):
        ship_mgr = self.client.game.graphics.model.role.ship_mgr

        option_2_callback = {
        }

        for ship_id, ship in ship_mgr.id_2_ship.items():
            option_2_callback[ship.name] = partial(self.__show_cargo_cnt_to_load_to_ship_dialog, cargo_id, ship_id)

        self.__make_menu(option_2_callback)

    def __fight_npc(self):
        PacketParamsDialog(
            mgr=self.mgr,
            client=self.client,
            params_names=['npc_id'],
            packet=FightNpc(),
        )

    def __fight_role(self):
        PacketParamsDialog(
            mgr=self.mgr,
            client=self.client,
            params_names=['role_id'],
            packet=FightRole(),
        )

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
            'type': f'{ship_template.name}',
            'tacking': f'{ship_template.tacking}',
            'power': f'{ship_template.power}',
            'durability': f'{ship_template.durability}',
            'capacity': f'{ship_template.capacity}',
            'max_guns': f'{ship_template.max_guns}',
            'min_crew/max_crew': f'{ship_template.min_crew}/{ship_template.max_crew}',
            'max_cargo': f'{ship_template.capacity - ship_template.max_crew - ship_template.max_guns}',
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

        self.__building_speak(f"I charge {price} for this ship. No negotiation please.")

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

    def __view_fleet(self, role_id):
        self.client.send(ViewFleet(role_id=role_id))

    def fight_target(self, role):
        graphics = self.get_graphics()

        graphics.model.role.is_moving = False
        graphics.sp_background.start_time = None

        if role.is_npc():
            self.client.send(FightNpc(npc_id=role.id))
        else:
            self.client.send(FightRole(role_id=role.id))

    def enter_building(self):
        x = self.__get_role().x
        y = self.__get_role().y

        port_id = self.__get_role().map_id

        for building_id, building_name in c.ID_2_BUILDING_TYPE.items():

            b_x, b_y = sObjectMgr.get_building_xy_in_port(building_id, port_id)

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

                self.__get_graphics().remove_port_npcs()

                self.pop_some_menus(cnt=1)

                getattr(self, f'show_{building_name}_menu')()

                self.__get_role().is_in_building = True

                self.__building_speak('Hello! How may I help you?')

                return


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
            'Language(L)': '',
            'Sounds': '',
            'Hot Keys': '',
            'Exit': partial(self.__exit_game),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_fight_menu(self):

        option_2_callback = {
            'View Battle States': partial(self.__show_battle_states),
            'View Enemy Ships': partial(self.__show_ship_info_menu, is_enemy=True),
            'Set All Ships Target': partial(self._set_all_ships_target),
            'Set All Ships Strategy': partial(self._set_all_ships_strategy),
            'Set Ship Target': partial(self._set_ship_target),
            'Set Ship Strategy': partial(self._set_ship_strategy),
            'Escape Battle': partial(self.escape_battle),
            'All Ships Attack': partial(self.all_ships_attack),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )


    def show_role_menu(self, role):
        my_role = self.__get_role()
        if my_role.can_inspect(role):
            option_2_callback = {
                f'{role.name}': '',
                'View Fleet': partial(self.__view_fleet, role.id),
                'View Captain': '',
                'Gossip': '',
                'Fight': partial(self.fight_target, role),
            }

            self.__make_menu(option_2_callback)
        else:
            mate = my_role.get_flag_ship().get_captain()
            self.show_mate_speech(mate, "It's too far away!")

    def show_cmds_menu(self):
        option_2_callback = {
            'Enter Building (F)': partial(self.enter_building),
            'Enter Port (M)': partial(self.enter_port),
            'Go Ashore (G)': partial(self.__try_to_discover),
            'Fight Npc (B)': partial(self.__fight_npc),
            'Fight Role (B)': partial(self.__fight_role),
            'Measure Cooridinate': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )


    def show_items_menu(self):
        option_2_callback = {
            'Items': partial(self.show_items),
            'Discoveries': partial(self.__show_discoveries_menu),
            'Diary': '',
            'World Map': partial(self.__show_world_map),
            'Port Map': ''
        }

        self.__make_menu(option_2_callback)

    def show_mates_menu(self):
        option_2_callback = {
            'Mate Info': partial(self.__show_mate_info_menu),
            'Assign Duty': partial(self.__show_mates_to_assign_duty_menu),
            'Crew': partial(self.__show_crew_state_menu),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )


    def show_ships_menu(self):
        option_2_callback = {
            'Fleet Info': partial(self.__show_fleet_info),
            'Ship Info': partial(self.__show_ship_info_menu),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )


