from dataclasses import dataclass

@dataclass
class Role:
    id: int=None
    name: str=None
    x: int=None
    y: int=None


class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {}
