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

    def __show_ships_with_cargo_to_sell(self):
        ship_mgr = self.get_ship_mgr()

        option_2_callback = {
        }

        for ship_id, ship in ship_mgr.id_2_ship.items():
            option_2_callback[ship.name] = partial(self.__send_packet_to_get_cargo_cnt_and_sell_price, ship_id)


        self.__make_menu(option_2_callback)


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
        ship_id = cargo_to_sell_in_ship.ship_id

        option_2_callback = {
            f'{cargo_name} [{cnt}] {sell_price}': partial(self.__ask_cargo_cnt_to_sell, cargo_id, ship_id),
        }

        self.__make_menu(option_2_callback)


    def __get_graphics(self):
        return self.client.game.graphics

    def __change_building_bg(self, building_name):
        self.__get_graphics().change_background_sp_to_building(building_name)

    def show_market_menu(self):
        # hide role sp
        self.__get_graphics().hide_role_sprite()

        self.__change_building_bg('market')

        option_2_callback = {
            'Buy': partial(self.__send_get_available_cargos),
            'Sell': partial(self.__show_ships_with_cargo_to_sell),
            'Price Index': '',
            'Investment State': '',
            'Invest': '',
            'Defeat Administrator': '',
            'Manage': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_bar_menu(self):
        self.__change_building_bg('bar')

        option_2_callback = {
            'Recruit Crew': '',
            'Dismiss Crew': '',
            'Meet': partial(self.__get_mate_in_port),
            'Fire Mate': partial(self.__show_mates_to_fire_menu),
            'Waitress': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )


    def __sell_ship(self, id):
        self.client.send(SellShip(id=id))

    def __show_ships_to_sell(self):
        option_2_callback = {
        }

        for id, ship in self.get_ship_mgr().id_2_ship.items():
            ship_template = sObjectMgr.get_ship_template(ship.ship_template_id)
            sell_price = int(ship_template.buy_price / 2)
            option_2_callback[f'{ship.name} {sell_price}'] = partial(self.__sell_ship, id)

        self.__make_menu(option_2_callback)

    def __get_ships_to_buy(self):
        self.client.send(GetShipsToBuy())

    def show_dry_dock_menu(self):
        self.__change_building_bg('dry_dock')

        option_2_callback = {
            'New Ship': '',
            'Used Ship': partial(self.__get_ships_to_buy),
            'Repair': '',
            'Sell': partial(self.__show_ships_to_sell),
            'Remodel': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __show_mate_template_panel(self, mate_template):
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

    def __show_mate_menu(self, mate_template):
        option_2_callback = {
            'inspect': partial(self.__show_mate_template_panel, mate_template),
            'treat': '',
            'gossip': '',
            'hire': partial(self.__hire_mate, mate_template),
        }

        self.__make_menu(option_2_callback)

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

    def __show_mates_to_fire_menu(self):
        mates = self.get_mate_mgr().get_mates()
        option_2_callback = {}
        for mate in mates:
            option_2_callback[f'{mate.name}'] = partial(self.__show_ensure_fire_mate_menu, mate)
        self.__make_menu(option_2_callback)

    def __exit_building(self):
        self.pop_some_menus(1)
        self.__get_graphics().unhide_role_sprite()

        role = self.__get_role()
        self.__get_graphics().change_background_sp_to_port(role.map_id, role.x, role.y)

    def __send_sail_request(self):
        self.client.send(Sail())

    def show_harbor_menu(self):
        self.__change_building_bg('harbor')

        option_2_callback = {
            'Sail': partial(self.__send_sail_request),
            'Load Supply': '',
            'Unload Supply': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_inn_menu(self):
        self.__change_building_bg('inn')

        option_2_callback = {
            'Check In': '',
            'Gossip': '',
            'Port Info': '',
            'Walk Around': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_palace_menu(self):
        self.__change_building_bg('palace')

        option_2_callback = {
            'Meet Ruler': '',
            'Defect': '',
            'Gold Aid': '',
            'Ship Aid': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_job_house_menu(self):
        self.__change_building_bg('job_house')

        option_2_callback = {
            'Job Assignment': '',
            'Country Info': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_bank_menu(self):
        self.__change_building_bg('bank')

        option_2_callback = {
            'Check Balance': '',
            'Deposit': '',
            'Withdraw': '',
            'Borrow': '',
            'Repay': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_item_shop_menu(self):
        self.__change_building_bg('item_shop')

        option_2_callback = {
            'Buy': '',
            'Sell': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_church_menu(self):
        self.__change_building_bg('church')

        option_2_callback = {
            'Pray': '',
            'Donate': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_fortune_house_menu(self):
        self.__change_building_bg('fortune_house')

        option_2_callback = {
            'Life': '',
            'Career': '',
            'Love': '',
            'Mates': '',
            'Exit': partial(self.__exit_building),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def __exit_game(self):

        self.client.send(Disconnect())

    def __show_one_ship_states(self, ship):
        ship_template = sObjectMgr.get_ship_template(ship.ship_template_id)

        print(f'show states for {ship.id}')
        dict = {
            'name/type/captain': f'{ship.name}/{ship_template.name}/{ship.captain}',
            '1': '',
            'tacking/power/speed': f'{ship.tacking}/{ship.power}',
            'durability': f'{ship.now_durability}/{ship.max_durability}',
            '2': '',
            'capacity': f'{ship.capacity}',
            'guns/max_guns': f'{ship.now_guns}/{ship.max_guns}',
            'min_crew/crew/max_crew': f'{ship.min_crew}/{ship.now_crew}/{ship.max_crew}',
            'useful_capacity': f'{ship.capacity}',
            'cargo_id/cnt': f'{ship.cargo_id}/{ship.cargo_cnt}'

        }

        # make text from dict
        text = self.__dict_2_txt(dict)

        # get ship image
        ship_image = sAssetMgr.images['ships'][ship_template.name.lower()]

        MyPanelWindow(
            rect=pygame.Rect((59, 12), (350, 400)),
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


    def __show_discoveries_menu(self):

        option_2_callback = {}

        for id in self.__get_role().discovery_mgr.ids_set:
            village = sObjectMgr.get_village(id)
            option_2_callback[village.name] = partial(self.__show_one_discovery, village)

        self.__make_menu(option_2_callback)


    def __show_world_map(self):
        # image
        world_map_image = sAssetMgr.images['world_map']['world_map_from_uw2']

        # shrink image
        world_map_image = pygame.transform.scale(world_map_image, (800, 400))  # 800, 400

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

        for x in range(rows):
            for y in range(cols):
                if matrix[x][y] == 0:
                    # paste figure image onto img
                    start_x_y = (start_y + int(y * strict_grid_size), start_x + int(x * strict_grid_size))
                    world_map_image.blit(map_mosaic, start_x_y)

        # get my_x y based on location
        if self.__get_role().is_in_port():
            port = sObjectMgr.get_port(self.__get_role().map_id)
            my_x = port.x
            my_y = port.y
        else:
            my_x = self.__get_role().x
            my_y = self.__get_role().y

        my_x = int(800 * (my_x / 2160))
        my_y = int(400 * (my_y / 1080))
        print(my_x, my_y)

        world_map_image.blit(my_position_img, (my_x, my_y))


        image_rect = world_map_image.get_rect()
        text = ''

        MyPanelWindow(
            rect=pygame.Rect((10, 10), (image_rect.width, (image_rect.height + 60))),
            ui_manager=self.mgr,
            text=text,
            image=world_map_image,
        )

        # sound
        sAssetMgr.sounds['map'].play()

    def show_available_cargos_menu(self, get_available_cargos_res):
        option_2_callback = {f'{cargo.name} {cargo.price}': partial(self.__show_ships_to_load_cargo_menu, cargo.id)
                             for cargo in get_available_cargos_res.available_cargos}

        self.__make_menu(option_2_callback)

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

        dict = {
            'name/nation': f"{mate.name}/{mate.nation}",
            'duty': mate.assigned_duty,
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

    def show_ships_to_buy_menu(self, ships_to_buy):
        option_2_callback = {
        }

        for ship_to_buy in ships_to_buy.ships_to_buy:
            template_id = ship_to_buy.template_id
            ship_template = sObjectMgr.get_ship_template(template_id)

            name = ship_template.name
            price = ship_to_buy.price

            option_2_callback[f'{name} {price}'] = partial(self.__buy_ship, template_id)

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

    def __enter_building(self):
        x = self.__get_role().x
        y = self.__get_role().y

        port_id = self.__get_role().map_id

        for building_id, building_name in c.ID_2_BUILDING_TYPE.items():

            b_x, b_y = sObjectMgr.get_building_xy_in_port(building_id, port_id)

            if x == b_x and y == b_y:
                # enter building
                print(f'enter building: {building_name}')
                # self.__show_market_menu()

                self.__get_graphics().hide_role_sprite()

                self.pop_some_menus(cnt=1)

                getattr(self, f'show_{building_name}_menu')()



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
            'Misc': 'test',
            'Bank': partial(self.show_bank_menu),
            'Item Shop': partial(self.show_item_shop_menu),
            'Church': partial(self.show_church_menu),
            'Fortune House': partial(self.show_fortune_house_menu),
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

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
        option_2_callback = {
            f'{role.name}': '',
            'View Fleet': partial(self.__view_fleet, role.id),
            'View Captain': '',
            'Gossip': '',
            'Fight': partial(self.fight_target, role),
        }

        self.__make_menu(option_2_callback)

    def show_cmds_menu(self):
        option_2_callback = {
            'Enter Building (F)': partial(self.__enter_building),
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
            'Equipments': '',
            'Items': '',
            'Discoveries': partial(self.__show_discoveries_menu),
            'Diary': '',
            'World Map': partial(self.__show_world_map),
            'Port Map': ''
        }

        option_2_callback[f'Gold Coins {self.client.game.graphics.model.role.money}'] = ''

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )

    def show_mates_menu(self):
        option_2_callback = {
            'Admiral Info': '',
            'Mate Info': partial(self.__show_mate_info_menu),
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
            'Swap Ships': '',
        }

        MyMenuWindow(
            title='',
            option_2_callback=option_2_callback,
            mgr=self.mgr
        )


