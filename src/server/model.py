from dataclasses import dataclass


@dataclass
class Role:
    session: any
    id: int
    name: str
    x: int
    y: int
    map_id: int

class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {}
