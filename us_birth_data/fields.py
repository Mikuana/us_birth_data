import re

from pandas.api.types import CategoricalDtype

from us_birth_data._utils import _recurse_subclasses
from us_birth_data.files import *


class Handlers:
    """ Raw value handlers """

    @staticmethod
    def integer(x):
        return int(x) if x.strip() else None

    @staticmethod
    def character(x):
        return x.decode('utf-8')


class Column:
    """ Base Column class """

    @classmethod
    def name(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()


class Source(Column):
    handler = None
    na_value = None
    positions: dict = {}
    labels = {}

    @classmethod
    def position(cls, file: YearData):
        return cls.positions.get(file)

    @classmethod
    def prep(cls, value: str):
        return cls.handler(value)

    @classmethod
    def decode(cls, value):
        if cls.labels:
            return cls.labels.get(value)
        else:
            return value

    @classmethod
    def parse_from_row(cls, file: YearData, row: list):
        pos = cls.position(file)
        if pos:
            value = row[pos[0] - 1:pos[1]]
            value = cls.prep(value)
            value = cls.decode(value)
            return value
        else:
            return


class Target(Column):
    pd_type: str = None

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return data_frame[cls.name()]


class Year(Target):
    """
    Birth Year

    And integer describing the year that the birth occurred. Although this is not
    explicitly included in the raw data sets, it is implied by the year that the
    data set represents.
    """

    pd_type = 'uint16'

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return kwargs.get('year')


class Month(Source, Target):
    """ Birth Month """

    handler = Handlers.integer
    labels = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
        12: 'December'
    }
    pd_type = CategoricalDtype(categories=list(labels.values()), ordered=True)
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
        **{
            x: (13, 14) for x in
            (Y2014, Y2015, Y2016, Y2017, Y2018, Y2019)
        }
    }


class Day(Source):
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


class DayOfWeek(Source, Target):
    """ Date of Birth Weekday """

    labels = {
        1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday',
        6: 'Friday', 7: 'Saturday'
    }
    pd_type = CategoricalDtype(categories=list(labels.values()), ordered=True)
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
        **{
            x: (23, 23) for x in
            (Y2014, Y2015, Y2016, Y2017, Y2018, Y2019)
        }
    }

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        rd = data_frame[[Year.name(), Month.name(), Day.name()]].copy()
        lkp = dict(zip(Month.labels.values(), Month.labels.keys()))
        rd[Month.name()] = rd[Month.name()].replace(lkp)
        return data_frame[DayOfWeek.name()].combine_first(
            pd.to_datetime(rd, errors='coerce').dt.strftime('%A')
        )


class State(Source, Target):
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

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return data_frame[cls.name()].combine_first(data_frame[OccurrenceState.name()])


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


class UmeColumn(Source):
    handler = Handlers.integer
    labels = {1: "Yes", 2: "No", 8: "Not on Certificate"}
    pd_type = CategoricalDtype(categories=list(labels.values()), ordered=True)


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


class FinalRouteMethod(Source):
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
            (Y2014, Y2015, Y2016, Y2017, Y2018, Y2019)
        }
    }


class DeliveryMethod(Source, Target):
    """ Delivery method recode """
    handler = Handlers.integer
    labels = {1: 'Vaginal', 2: 'Cesarean'}
    pd_type = CategoricalDtype(categories=list(labels.values()), ordered=True)
    positions = {
        **{
            x: (403, 403) for x in
            (Y2005, Y2006, Y2007, Y2008, Y2009, Y2010, Y2011, Y2012, Y2013)
        },
        **{
            x: (408, 408) for x in
            (Y2014, Y2015, Y2016, Y2017, Y2018, Y2019)
        },
    }

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return data_frame[cls.name()].\
            combine_first(cls.remap_final_route_method(data_frame)).\
            combine_first(cls.remap_ume(data_frame))

    @classmethod
    def remap_final_route_method(cls, df: pd.DataFrame) -> pd.Series:
        lkp = {
            'Spontaneous': 'Vaginal',
            'Forceps': 'Vaginal',
            'Vacuum': 'Vaginal',
            'Cesarean': 'Cesarean',
            'Unknown or not stated': None,
        }
        return df[FinalRouteMethod.name()].replace(lkp)

    @classmethod
    def remap_ume(cls, df: pd.DataFrame) -> pd.Series:
        v_lkp = {'Yes': 'Vaginal', 'No': None}
        vag = df[UmeVaginal.name()].replace(v_lkp)
        vbac = df[UmeVBAC.name()].replace(v_lkp)

        c_lkp = {'Yes': 'Cesarean', 'No': None}
        prime = df[UmePrimaryCesarean.name()].replace(c_lkp)
        repeat = df[UmeRepeatCesarean.name()].replace(c_lkp)
        return vag.combine_first(vbac).combine_first(prime).combine_first(repeat)


class SexOfChild(Source, Target):
    """ Sex of child """
    handler = Handlers.integer
    labels = {1: 'Male', 2: 'Female'}
    pd_type = 'category'
    positions = {
        Y1968: (31, 31),
        **{
            x: (35, 35) for x in
            (Y1969, Y1970, Y1971, Y1972, Y1973, Y1974, Y1975, Y1976, Y1977, Y1978,
             Y1979, Y1980, Y1981, Y1982, Y1983, Y1984, Y1985, Y1986, Y1987, Y1988)
        },
        **{
            x: (189, 189) for x in
            (Y1989, Y1990, Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997, Y1998,
             Y1999, Y2000, Y2001, Y2002)
        }
    }

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return data_frame[cls.name()].combine_first(data_frame[Sex.name()])


class Sex(SexOfChild):
    """ Sex of child """
    handler = Handlers.character
    labels = {'M': 'Male', 'F': 'Female'}
    positions = {
        **{
            x: (436, 436) for x in
            (Y2003, Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010, Y2011,
             Y2012, Y2013)
        },
        **{
            x: (475, 475) for x in
            (Y2014, Y2015, Y2016, Y2017, Y2018, Y2019)
        },
    }


class AgeOfMother(Source, Target):
    """ Age of Mother """
    handler = Handlers.integer
    na_value = 99
    pd_type = float
    positions = {
        Y1968: (38, 39),
        **{
            x: (41, 42) for x in
            (Y1969, Y1970, Y1971, Y1972, Y1973, Y1974, Y1975, Y1976, Y1977, Y1978,
             Y1979, Y1980, Y1981, Y1982, Y1983, Y1984, Y1985, Y1986, Y1987, Y1988)
        },
        **{
            x: (70, 71) for x in
            (Y1989, Y1990, Y1991)
        },
        **{
            x: (91, 92) for x in
            (Y1991, Y1992, Y1993, Y1994, Y1995, Y1996, Y1997, Y1998, Y1999,
             Y2000, Y2001, Y2002)
        },
        Y2003: (77, 78)
    }

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        recodes = {x: None for x in ('10-12 years', '50-54 years')}
        return data_frame[cls.name()].combine_first(
            data_frame[AgeOfMotherSuppressed.name()].replace(recodes)
        )


class AgeOfMotherSuppressed(AgeOfMother):
    pd_type = str
    labels = {
        12: '10-12 years', 13: '13', 14: '14', 15: '15', 16: '16', 17: '17',
        18: '18', 19: '19', 20: '20', 21: '21', 22: '22', 23: '23', 24: '24',
        25: '25', 26: '26', 27: '27', 28: '28', 29: '29', 30: '30', 31: '31',
        32: '32', 33: '33', 34: '34', 35: '35', 36: '36', 37: '37', 38: '38',
        39: '39', 40: '40', 41: '41', 42: '42', 43: '43', 44: '44', 45: '45',
        46: '46', 47: '47', 48: '48', 49: '49', 50: '50-54 years'
    }

    positions = {
        **{
            x: (89, 90) for x in
            (Y2004, Y2005, Y2006, Y2007, Y2008, Y2009, Y2010, Y2011, Y2012, Y2013)
        },
        **{
            x: (75, 76) for x in
            (Y2014, Y2015, Y2016, Y2017, Y2018, Y2019)
        }
    }


class Births(Source, Target):
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

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        if kwargs.get('year') < 1972:
            return 2
        else:
            return data_frame[cls.name()].fillna(1)

    # df = df.groupby([x for x in df.columns.tolist() if x != n], as_index=False)[n].sum()


sources = _recurse_subclasses(Source)
targets = _recurse_subclasses(Target)
# restrict to direct Target assignment only, not inherited
targets = [
    t for t in targets
    if not any([t in _recurse_subclasses(x) for x in targets])
]
# print(targets)
targets = [
    Year, Month, DayOfWeek, State, SexOfChild, DeliveryMethod, AgeOfMother, Births
]
