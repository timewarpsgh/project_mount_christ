from enum import Enum, auto
from languages import chinese


class Language(Enum):
    ENGLISH = auto()
    CHINESE = auto()


class Translator():

    def __init__(self):
        self.to_language = Language.CHINESE

    def tr(self, content):
        if self.to_language == Language.CHINESE:
            if content.lower() in chinese.dic:
                return  chinese.dic[content.lower()]
            elif content in chinese.dic:
                return chinese.dic[content]
            else:
                return content
        elif self.to_language == Language.ENGLISH:
            return content

    def set_to_language(self, language):
        self.to_language = language


def main():
    translator = Translator()
    print(translator.translate("ships"))


# singleton
sTr = Translator()

def tr(content):
    return sTr.tr(content)

if __name__ == '__main__':
    main()