from enum import Enum, auto


class OpCodeType(Enum):
    NewAccount = auto()
    NewAccountRes = auto()

    Login = auto() # 1
    LoginRes = auto()

    GetWorlds = auto()
    GetWorldsRes = auto()

    GetRolesInWorld = auto()
    GetRolesInWorldRes = auto()

    NewRole = auto()
    NewRoleRes = auto()

    EnterWorld = auto()
    EnterWorldRes = auto()

    RoleAppeared = auto()
    RoleDisappeared = auto()

    GetAvailableCargos = auto()
    GetAvailableCargosRes = auto()

    Move = auto()
    RoleMoved = auto()

    Disconnect = auto()

    BuyCargo = auto()
    MoneyChanged = auto()
    ShipCargoChanged = auto()

    GetCargoCntAndSellPrice = auto()
    CargoToSellInShip = auto()
    SellCargoInShip = auto()
    PopSomeMenus = auto()

    Chat = auto()
    GotChat = auto()

    Discover = auto()
    Discovered = auto()

    Sail = auto()
    MapChanged = auto()
    EnterPort = auto()

    OpenedGrid = auto()

    FightNpc = auto()
    EnteredBattleWithNpc = auto()

    EscapeNpcBattle = auto()
    EscapedNpcBattle = auto()

    YouWonNpcBattle = auto()

    SellShip = auto()
    ShipRemoved = auto()

    GetShipsToBuy = auto()
    ShipsToBuy = auto()

    BuyShip = auto()
    GotNewShip = auto()

    FightRole = auto()
    EnteredBattleWithRole = auto()

    EscapeRoleBattle = auto()
    EscapedRoleBattle = auto()

    BattleTimerStarted = auto()
    AllShipsAttack = auto()
    ShipAttacked = auto()

def gen_opcode_2_value():
    d = {}
    for type in OpCodeType:
        d[str(type)[11:]] = type.value
    return d


OPCODE_2_VALUE = gen_opcode_2_value()
VALUE_2_OPCODE = {v: k for k, v in OPCODE_2_VALUE.items()}


def main():
    print(OPCODE_2_VALUE)
    print(VALUE_2_OPCODE)


if __name__ == '__main__':
    main()