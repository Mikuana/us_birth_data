import re

from us_birth_data.files import *


class Handlers:
    """ Raw value handlers """

    @staticmethod
    def integer(x):
        return int(x)

    @staticmethod
    def character(x):
        return x


class Column:
    """ Base Column class """
    pd_type: str = None

    @classmethod
    def name(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()


class Year(Column):
    """
    Birth Year

    And integer describing the year that the birth occurred. Although this is not
    explicitly included in the raw data sets, it is implied by the year that the
    data set represents.
    """

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
        v = None if v == cls.na_value else v
        if not v and 'Unknown' in cls.labels.values():
            v = 'Unknown'
        return v

    @classmethod
    def parse_from_row(cls, file: YearData, row: list):
        pos = cls.position(file)
        value = row[pos[0] - 1:pos[1]]
        value = cls.prep(value)
        value = cls.decode(value)
        return value


class Births(OriginalColumn):
    """
    Number of births

    An integer representing the number of birth records that are represented by
    the combination of dimensions that are present in a particular record of the
    births data set. All math that is performed on this data set should be weighted
    by this value.

    From 1968 to 1971, the number of records is calculated assuming a 50% sample
    rate (i.e. each record counts for 2 births), per the documentation. From 1972
    to 1984, and explicit record weight column was introduced, which indicates the
    appropriate weighting of records; some states used a 50% sample, and some
    reported all records. After 1984, the data are reported without weighting, and
    each record is counted as a single birth.
    """

    pd_type = 'uint32'
    handler = Handlers.integer
    positions = {
        x: (208, 208) for x in
        (Y1972, Y1973, Y1974, Y1975, Y1976, Y1977, Y1978, Y1979,
         Y1980, Y1981, Y1982, Y1983, Y1984)
    }


class State(OriginalColumn):
    """
    State of Occurrence

    From 1968 to 2004 the data sets included the state (or territory) where
    the birth occurred. After 2004, state of occurrence is no longer included. This
    field includes all 50 states, and the District of Columbia (i.e. Washington D.C.).
    """

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
        50: 'Wisconsin', 51: 'Wyoming', 52: 'Puerto Rico', 53: 'Virgin Islands', 54: 'Guam',
        99: 'Unknown'
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
        'MP': 'Northern Marianas', 'PR': 'Puerto Rico', 'VI': 'Virgin Islands',
        'XX': 'Unknown'
    }

    positions = {
        Y2003: (30, 31),
        Y2004: (30, 31)
    }


class Month(OriginalColumn):
    """ Birth Month """

    handler = Handlers.integer
    labels = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
        12: 'December', 99: 'Unknown'
    }
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
    """
    Date of Birth Weekday

    TODO: 'Unknowns'
    """

    labels = {
        1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday',
        6: 'Friday', 7: 'Saturday', 99: 'Unknown'
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
        1: "Yes", 2: "No", 8: "Not on Certificate", 9: "Unknown or Not Stated",
        99: 'Unknown'
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
        1: "Spontaneous", 2: "Forceps", 3: "Vacuum", 4: "Cesarean", 9: "Unknown or not stated",
        99: 'Unknown'
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
