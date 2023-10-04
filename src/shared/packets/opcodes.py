from enum import Enum, auto


class OpCodeType(Enum):
    Login = auto() # 1
    LoginRes = auto()
    NewAccount = auto()
    NewAccountRes = auto()


def main():
    print(OpCodeType.C_XX.value)


if __name__ == '__main__':
    main()