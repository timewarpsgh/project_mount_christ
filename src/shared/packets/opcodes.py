from enum import Enum, auto


class OpCodeType(Enum):
    C_LOGIN = auto() # 1
    C_NEW_ACCOUNT = auto() # 2


def main():
    print(OpCodeType.C_XX.value)


if __name__ == '__main__':
    main()