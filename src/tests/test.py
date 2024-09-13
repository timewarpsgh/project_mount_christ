def calculate_crew_kill(ship1, ship2):
    # Get the current crew count and captain's battle skill for both ships
    crew1 = ship1.now_crew
    crew2 = ship2.now_crew
    battle_skill1 = ship1.get_captain().battle if ship1.get_captain() else 0
    battle_skill2 = ship2.get_captain().battle if ship2.get_captain() else 0

    # Calculate the crew kill for each ship
    kill_factor1 = (battle_skill1 + 1) / (battle_skill2 + 1)
    kill_factor2 = (battle_skill2 + 1) / (battle_skill1 + 1)

    crew_kill1 = int(crew2 * kill_factor1 * 0.1)
    crew_kill2 = int(crew1 * kill_factor2 * 0.1)

    # Ensure crew kill does not exceed the current crew count
    crew_kill1 = min(crew_kill1, crew1)
    crew_kill2 = min(crew_kill2, crew2)

    return crew_kill1, crew_kill2

# Example usage
class Captain:
    def __init__(self, battle):
        self.battle = battle

class Ship:
    def __init__(self, now_crew, captain):
        self.now_crew = now_crew
        self.captain = captain

    def get_captain(self):
        return self.captain

captain1 = Captain(battle=100)
captain2 = Captain(battle=100)
ship1 = Ship(now_crew=100, captain=captain1)
ship2 = Ship(now_crew=200, captain=captain2)

crew_kill1, crew_kill2 = calculate_crew_kill(ship1, ship2)
print(f"Ship 1 crew killed: {crew_kill1}")
print(f"Ship 2 crew killed: {crew_kill2}")