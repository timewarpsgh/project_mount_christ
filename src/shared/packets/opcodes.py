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
    StartMoving = auto()
    StartedMoving = auto()
    StopMoving = auto()
    StoppedMoving = auto()
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
    ShipMoved = auto()

    SetAllShipsTarget = auto()
    AllShipsTargetSet = auto()
    SetAllShipsStrategy = auto()
    AllShipsStrategySet = auto()
    SetShipTarget = auto()
    SetShipStrategy = auto()

    FlagShipMove = auto()
    FlagShipAttack = auto()

    ViewFleet = auto()
    FleetInfo = auto()

    GetMateInPort = auto()
    MateInPort = auto()

    HireMate = auto()
    HireMateRes = auto()
    MateAdded = auto()

    FireMate = auto()
    MateFired = auto()

    AssignDuty = auto()
    DutyAssigned = auto()
    DutyCleared = auto()

    XpEarned = auto()
    LvUped = auto()

    SeasonChanged = auto()

    RepairShip = auto()
    ShipRepaired = auto()

    RenameShip = auto()
    ShipRenamed = auto()

    ChangeShipCapacity = auto()
    ShipCapacityChanged = auto()

    ChangeShipWeapon = auto()
    ShipWeaponChanged = auto()

    RecruitCrew = auto()
    CrewRecruited = auto()

    DismissCrew = auto()
    CrewDismissed = auto()

    LoadSupply = auto()
    SupplyChanged = auto()
    UnloadSupply = auto()

    OneDayPassedAtSea = auto()
    SupplyConsumed = auto()

    YouDied = auto()
    ShipFieldChanged = auto()

    SetRoleField = auto()
    RoleFieldSet = auto()

    GetPortInfo = auto()
    PortInfo = auto()

    GetNationInfo = auto()
    NationAlliedPorts = auto()

    GetNationsInvestments = auto()
    NationsInvestments = auto()

    Invest = auto()
    GetPersonsInvestments = auto()
    PersonsInvestments = auto()

    GetAvailableItems = auto()
    AvailableItems = auto()

    BuyItem = auto()
    ItemAdded = auto()

    GetItemSellPrice = auto()
    ItemSellPrice = auto()

    SellItem = auto()
    ItemRemoved = auto()

    BuyTaxFreePermit = auto()
    BuyLetterOfMarque = auto()

    InvestigateFleet = auto()
    FleetsInvestigated = auto()

    EquipItem = auto()
    ItemEquipped = auto()

    UnequipItem = auto()
    ItemUnequipped = auto()

    UseItem = auto()
    ItemUsed = auto()

    AuraAdded = auto()
    AuraRemoved = auto()

    AuraCleared = auto()
    NotorityChanged = auto()
    CannotEnterPort = auto()

    Pray = auto()
    Donate = auto()
    DonationMade = auto()

    CheckBalance = auto()
    YourBalance = auto()

    Deposit = auto()
    Deposited = auto()

    Withdraw = auto()
    Withdrawn = auto()

    Invested = auto()

    TreatCrew = auto()
    CrewTreated = auto()

    Sleep = auto()
    Slept = auto()

    BuildingSpeak = auto()

    Treat = auto()
    Treated = auto()
    MateSpeak = auto()

    SeeWaitress = auto()
    WaitressSeen = auto()

    Gossip = auto()
    ViewCaptain = auto()
    CaptainInfo = auto()
    RandMateSpeak = auto()

    TreasureMapCleared = auto()
    BuyTreasureMap = auto()
    TreasureMapBought = auto()

    TriggerEvent = auto()
    RequestTrade = auto()
    TradeRequested = auto()
    AcceptTradeRequest = auto()
    TradeStart = auto()
    SetTradeMoney = auto()
    TradeMoneySet = auto()
    ConfirmTrade = auto()
    TradeConfirmed = auto()
    TradeCompleted = auto()
    SetTradeItem = auto()
    TradeItemSet = auto()
    TradeUnconfirmed = auto()
    FriendOnlineStateChanged = auto()

    AddFriend = auto()
    FriendAdded = auto()
    RemoveFriend = auto()
    FriendRemoved = auto()

    ShowWinImg = auto()
    ShowLoseImg = auto()

    Land = auto()

    BuyWanted = auto()
    WantedBought = auto()
    WantedCleared = auto()

    GossipResult = auto()
    NpcLootInfo = auto()
    RoleLootInfo = auto()
    OnlyThisManyCrew = auto()
    FoundItem = auto()
    PaidWage = auto()
    ManagePort = auto()
    ShowGovernorOptions = auto()
    SetPortStates = auto()
    GotTax = auto()

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