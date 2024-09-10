from enum import Enum


class DutyType(Enum):
    DUTY = 1
    REST = 2
    OFF = 3


print(DutyType.DUTY.value)

# int to dutytype
print(DutyType(1))