import calendar
import re

from us_birth_data.files import *


class Handlers:
    @staticmethod
    def integer(x):
        return int(x)

    @staticmethod
    def character(x):
        return x.decode('utf-8')


class Column:
    pd_type: str = None

    @classmethod
    def name(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()


class Year(Column):
    """ Birth Year """

    pd_type = 'uint16'


class OriginalColumn(Column):
    handler = None
    positions: dict = None
    na_value = None
    labels = {}

    @classmethod
    def position(cls, file: YearData):
        return cls.positions.get(file)

    @classmethod
    def prep(cls, value: str):
        return cls.handler(value)

    @classmethod
    def decode(cls, value):
        v = cls.labels.get(value, value)
        return None if v == cls.na_value else v

    @classmethod
    def parse_from_row(cls, file: YearData, row: list):
        pos = cls.position(file)
        value = row[pos[0] - 1:pos[1]]
        value = cls.prep(value)
        value = cls.decode(value)
        return value


class Births(OriginalColumn):
    """ Number of births """

    pd_type = 'uint32'
    handler = Handlers.integer
    positions = {
        x: (208, 208) for x in
        (Y1972, Y1973, Y1974, Y1975, Y1976, Y1977, Y1978, Y1979,
         Y1980, Y1981, Y1982, Y1983, Y1984)
    }


class State(OriginalColumn):
    """ State of Occurrence """

    pd_type = 'category'
    handler = Handlers.integer
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
        Y1968: (74, 75),
        **{
            x: (28, 29) for x in
            (Y1969, Y1970, Y1971, Y1972, Y1973, Y1974, Y1975, Y1976, Y1977,
             Y1978, Y1979, Y1980, Y1981, Y1982)
        },
        **{x: (28, 29) for x in (Y1983, Y1984, Y1985, Y1986, Y1987, Y1988)},
        **{
            x: (16, 17) for x in
            (Y1989, Y1990, Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997,
             Y1998, Y1999, Y2000, Y2001, Y2002)
        },
    }


class OccurrenceState(State):
    handler = Handlers.character
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
        Y2003: (30, 31),
        Y2004: (30, 31)
    }


class Month(OriginalColumn):
    """ Birth Month """

    handler = Handlers.integer
    labels = {ix: x for ix, x in enumerate(calendar.month_name) if x}
    pd_type = pd.api.types.CategoricalDtype(categories=list(labels.values()), ordered=True)
    positions = {
        Y1968: (32, 33),
        **{
            x: (84, 85) for x in
            (Y1969, Y1970, Y1971, Y1972, Y1973, Y1974, Y1975, Y1976, Y1977, Y1978, Y1979, Y1980,
             Y1981, Y1982, Y1983, Y1984, Y1985, Y1986, Y1987, Y1988)
        },
        **{
            x: (172, 173) for x in
            (Y1989, Y1990, Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997, Y1998,
             Y1999, Y2000, Y2001, Y2002)
        },
        **{
            x: (19, 20) for x in
            (Y2003, Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010, Y2011,
             Y2012, Y2013)
        },
        Y2014: (13, 14),
        Y2015: (13, 14)
    }


class Day(OriginalColumn):
    """ Birth Day of Month """

    handler = Handlers.integer
    na_value = 99
    positions = {
        x: (86, 87) for x in
        (
            Y1969, Y1970, Y1971, Y1972, Y1973, Y1974, Y1975, Y1976, Y1977, Y1978, Y1979, Y1980,
            Y1981, Y1982, Y1983, Y1984, Y1985, Y1986, Y1987, Y1988
        )
    }


class DayOfWeek(OriginalColumn):
    """ Date of Birth Weekday """

    labels = {
        1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday',
        6: 'Friday', 7: 'Saturday'
    }
    pd_type = pd.api.types.CategoricalDtype(categories=list(labels.values()), ordered=True)
    handler = Handlers.integer

    positions = {
        **{
            x: (180, 180) for x in
            (Y1989, Y1990, Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997, Y1998,
             Y1999, Y2000, Y2001, Y2002)
        },
        **{
            x: (29, 29) for x in
            (Y2003, Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010,
             Y2011, Y2012, Y2013)
        },
        Y2014: (23, 23),
        Y2015: (23, 23)
    }


class UmeColumn(OriginalColumn):
    handler = Handlers.integer
    labels = {
        1: "Yes", 2: "No", 8: "Not on Certificate", 9: "Unknown or Not Stated"
    }


class UmeVaginal(UmeColumn):
    """ Vaginal method of delivery """

    positions = {
        **{
            x: (217, 217) for x in
            (Y1989, Y1990, Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997,
             Y1998, Y1999, Y2000, Y2001, Y2002)
        },
        **{
            x: (395, 395) for x in
            (Y2003, Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010)
        }
    }


class UmeVBAC(UmeColumn):
    """ Vaginal birth after previous cesarean """

    positions = {
        **{
            x: (218, 218) for x in
            (Y1989, Y1990, Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997,
             Y1998, Y1999, Y2000, Y2001, Y2002)
        },
        **{
            x: (396, 396) for x in
            (Y2003, Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010)
        }
    }


class UmePrimaryCesarean(UmeColumn):
    """  Primary cesarean section """

    positions = {
        **{
            x: (219, 219) for x in
            (Y1989, Y1990, Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997,
             Y1998, Y1999, Y2000, Y2001, Y2002)
        },
        **{
            x: (397, 397) for x in
            (Y2003, Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010)
        }
    }


class UmeRepeatCesarean(UmeColumn):
    """ Repeat cesarean section """

    positions = {
        **{
            x: (220, 220) for x in
            (Y1989, Y1990, Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997,
             Y1998, Y1999, Y2000, Y2001, Y2002)
        },
        **{
            x: (398, 398) for x in
            (Y2003, Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010)
        }
    }


class FinalRouteMethod(OriginalColumn):
    """ Final Route & Method of Delivery """

    handler = Handlers.integer
    labels = {
        1: "Spontaneous", 2: "Forceps", 3: "Vacuum", 4: "Cesarean", 9: "Unknown or not stated"
    }

    positions = {
        **{
            x: (393, 393) for x in
            (Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010, Y2011, Y2012, Y2013)
        },
        **{
            x: (402, 402) for x in
            (Y2014, Y2015)
        }
    }
