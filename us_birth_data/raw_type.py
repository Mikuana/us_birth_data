class RawType:
    @staticmethod
    def handler(x):
        return x


class Integer(RawType):
    @staticmethod
    def handler(x):
        return int(x)


class Boolean(RawType):
    @staticmethod
    def handler(x):
        return '' if x == ' ' else str(x)


class Character(RawType):
    @staticmethod
    def handler(x):
        return x.decode('utf-8')


class Numeric(RawType):
    @staticmethod
    def handler(x):
        return '' if x[0] == ' ' else str(round(float(x), ndigits=1))


class Ignore(RawType):
    @staticmethod
    def handler(x):
        return ''
