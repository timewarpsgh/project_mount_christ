from enum import Enum, auto


class OpCodeType(Enum):
    C_LOGIN = auto() # 1
    S_LOGIN_RES = auto()
    C_NEW_ACCOUNT = auto()


def main():
    print(OpCodeType.C_XX.value)


if __name__ == '__main__':
    main()