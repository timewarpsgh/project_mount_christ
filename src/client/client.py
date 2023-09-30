from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str


def test():
    user = User(1, 'Alex')
    print(user)


def main():
    test()


if __name__ == '__main__':
    main()

