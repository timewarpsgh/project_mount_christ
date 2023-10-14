from dataclasses import dataclass


@dataclass
class Role:
    session: any
    id: int
    name: str
    x: int
    y: int


class Model:

    def __init__(self):
        self.role = None
        self.id_2_role = {}
