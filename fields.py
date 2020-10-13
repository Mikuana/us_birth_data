from files import *
from raw_type import *


class Field:
    field_name: str = None  # used to combine subclassed columns across files
    raw_type: RawType = None
    positions: dict = None
    labels = {}

    @classmethod
    def position(cls, file: PubFile):
        return cls.positions.get(file)

    @classmethod
    def prep(cls, value: str):
        return cls.raw_type.handler(value)

    @classmethod
    def decode(cls, value):
        return cls.labels.get(value, value)

    @classmethod
    def parse_from_row(cls, file: PubFile, row: list):
        pos = cls.position(file)
        if not pos:
            return
        value = row[pos[0] - 1:pos[1]]
        value = cls.prep(value)
        value = cls.decode(value)
        return value


class RECWT(Field):
    """ Record Weight """

    field_name = 'record_weight'
    raw_type = Integer
    positions = {
        x: (208, 208) for x in
        (Nat1972, Nat1973, Nat1974, Nat1975, Nat1976, Nat1977, Nat1978, Nat1979,
         Nat1980, Nat1981, Nat1982, Nat1983, Nat1984)
    }


class STATE(Field):
    """ State of Occurrence """

    field_name = 'state'
    raw_type = Integer
    labels = {
        1: 'Alabama', 2: 'Alaska', 3: 'Arizona', 4: 'Arkansas', 5: 'California', 6: 'Colorado', 7: 'Connecticut',
        8: 'Delaware', 9: 'District of Columbia', 10: 'Florida', 11: 'Georgia', 12: 'Hawaii', 13: 'Idaho',
        14: 'Illinois', 15: 'Indiana', 16: 'Iowa', 17: 'Kansas', 18: 'Kentucky', 19: 'Louisiana', 20: 'Maine',
        21: 'Maryland', 22: 'Massachusetts', 23: 'Michigan', 24: 'Minnesota', 25: 'Mississippi', 26: 'Missouri',
        27: 'Montana', 28: 'Nebraska', 29: 'Nevada', 30: 'New Hampshire', 31: 'New Jersey', 32: 'New Mexico',
        33: 'New York', 34: 'North Carolina', 35: 'North Dakota', 36: 'Ohio', 37: 'Oklahoma', 38: 'Oregon',
        39: 'Pennsylvania', 40: 'Rhode Island', 41: 'South Carolina', 42: 'South Dakota', 43: 'Tennessee',
        44: 'Texas', 45: 'Utah', 46: 'Vermont', 47: 'Virginia', 48: 'Washington', 49: 'West Virginia',
        50: 'Wisconsin', 51: 'Wyoming', 52: 'Puerto Rico', 53: 'Virgin Islands', 54: 'Guam'
    }
    positions = {
        Nat1968: (74, 75),
        **{
            x: (28, 29) for x in
            (Nat1969, Nat1970, Nat1971, Nat1972, Nat1973, Nat1974, Nat1975, Nat1976, Nat1977,
             Nat1978, Nat1979, Nat1980, Nat1981, Nat1982)
        }
    }


class StateOfOccurrence(STATE):
    positions = {
        **{x: (28, 29) for x in (Nat1983, Nat1984, Nat1985, Nat1986, Nat1987, Nat1988)},
        **{x: (16, 17) for x in (Nat1989, Nat1990, Nat1991, Nat1992, Nat1993)}
    }


class STATENAT(STATE):
    positions = {
        x: (16, 17) for x in
        (Nat1994, Nat1995us, Nat1996us, Nat1997us, Nat1998us, Nat1999us, Nat2000us, Nat2001us, Nat2002us)
    }


class OSTATE(STATE):
    raw_type = Character
    labels = {
        'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado',
        'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine',
        'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MS': 'Mississippi', 'MT': 'Montana',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon',
        'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
        'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VT': 'Vermont', 'WA': 'Washington',
        'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming', 'AS': 'American Samoa', 'GU': 'Guam',
        'MP': 'Northern Marianas', 'PR': 'Puerto Rico', 'VI': 'Virgin Islands'
    }

    positions = {
        Nat2003us: (30, 31),
        Nat2004us: (30, 31)
    }
