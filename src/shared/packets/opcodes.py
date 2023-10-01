from enum import Enum, auto


class OpCodeType(Enum):
    C_LOGIN = 0x000
    C_NEW_ACCOUNT = 0X001



def main():
    print(OpCodeType.C_NEW_ACCOUNT.value)


if __name__ == '__main__':
    main()