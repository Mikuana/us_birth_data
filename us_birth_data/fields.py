import re
from typing import Tuple, Dict

from pandas.api.types import CategoricalDtype

from us_birth_data import data
from us_birth_data._utils import _recurse_subclasses
from us_birth_data.files import *


def _span(yf: YearData, yt: YearData, pf: int, pt: int = None) -> Dict[YearData, Tuple[int, int]]:
    """
    Map position across multiple years

    A wrapper to simplify te repeated task of mapping positions across multiple years.
    """
    years = (x for x in YearData.__subclasses__() if yf.year <= x.year <= yt.year)
    return {year: (pf, pt) if pt else (pf, pf) for year in years}


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
    """
    Source Column

    A column that exists in the source fixed-width-files. This class maps positions,
    NA value placeholders, and data labels if applicable. Source columns are not
    necessarily included in the final output, but are instead used to provide data
    for Target columns.
    """
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
            return None if value == cls.na_value else value

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
    """
    Target Column

    A column which is included in the final data output. This includes a pandas
    data type, and methods to combine multiple Source columns together when
    necessary.
    """
    pd_type: str = None

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return data_frame[cls.name()]

    @classmethod
    def load_data(cls) -> pd.DataFrame:
        """
        Load field data

        Read the longitudinal data provided with this package for this specific
        field.
        :return:
        """
        return pd.read_parquet(Path(data.folder, f"{cls.name()}.parquet"))


class Year(Target):
    """
    Birth Year

    An integer describing the year that the birth occurred. Although this is not
    explicitly included in the raw data sets, it is implied by the year that the
    data set represents.
    """

    pd_type = 'uint16'

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return kwargs.get('year')


class Month(Source, Target):
    """
    Birth Month

    The month of the year that the birth occurred, represented as a full English
    month name (e.g. February).
    """

    handler = Handlers.integer
    labels = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
        12: 'December'
    }
    pd_type = CategoricalDtype(categories=list(labels.values()), ordered=True)
    positions = {
        Y1968: (32, 33),
        **_span(Y1969, Y1988, 84, 85),
        **_span(Y1989, Y2002, 172, 173),
        **_span(Y2003, Y2013, 19, 20),
        **_span(Y2014, Y2019, 13, 14)
    }


class Day(Source):
    """
    Birth Day of Month

    The numeric day of month when the birth occurred. Eventually removed and
    replaced with day of week for privacy reasons.
    """

    handler = Handlers.integer
    na_value = 99
    positions = _span(Y1969, Y1988, 86, 87)


class DayOfWeek(Source, Target):
    """
    Date of Birth Weekday

    The day of the week that the birth occurred. Represented by the full English
    name for the day (e.g. Monday).
    """

    labels = {
        1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday',
        6: 'Friday', 7: 'Saturday'
    }
    pd_type = CategoricalDtype(categories=list(labels.values()), ordered=True)
    handler = Handlers.integer

    positions = {
        **_span(Y1989, Y2002, 180),
        **_span(Y2003, Y2013, 29),
        **_span(Y2014, Y2019, 23)
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
    field includes all 50 states, the District of Columbia (i.e. Washington D.C.),
    and also allows for territories, but currently territories are not included in
    the data set.
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
        **_span(Y1969, Y1988, 28, 29),
        **_span(Y1989, Y2002, 16, 17)
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


class _UmeColumn(Source):
    handler = Handlers.integer
    labels = {1: "Yes", 2: "No", 8: "Not on Certificate"}
    pd_type = CategoricalDtype(categories=list(labels.values()), ordered=True)


class UmeVaginal(_UmeColumn):
    """ Vaginal method of delivery """

    positions = {
        **_span(Y1989, Y2002, 217),
        **_span(Y2003, Y2010, 395)
    }


class UmeVBAC(_UmeColumn):
    """ Vaginal birth after previous cesarean """

    positions = {
        **_span(Y1989, Y2002, 218),
        **_span(Y2003, Y2010, 396)
    }


class UmePrimaryCesarean(_UmeColumn):
    """  Primary cesarean section """

    positions = {
        **_span(Y1989, Y2002, 219),
        **_span(Y2003, Y2010, 397)
    }


class UmeRepeatCesarean(_UmeColumn):
    """ Repeat cesarean section """

    positions = {
        **_span(Y1989, Y2002, 220),
        **_span(Y2003, Y2010, 398)
    }


class FinalRouteMethod(Source):
    """ Final Route & Method of Delivery """

    handler = Handlers.integer
    labels = {
        1: "Spontaneous", 2: "Forceps", 3: "Vacuum", 4: "Cesarean", 9: "Unknown or not stated"
    }

    positions = {
        **_span(Y2004, Y2013, 393),
        **_span(Y2014, Y2019, 402)
    }


class DeliveryMethod(Source, Target):
    """
    Delivery method

    A broad categorization of final delivery method, either Vaginal or Cesarean.
    Attempts at Vaginal birth would be counted as Cesarean if that was the
    ultimate result.
    """
    handler = Handlers.integer
    labels = {1: 'Vaginal', 2: 'Cesarean'}
    pd_type = CategoricalDtype(categories=list(labels.values()), ordered=True)
    positions = {
        **_span(Y2005, Y2013, 403),
        **_span(Y2014, Y2019, 408)
    }

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return data_frame[cls.name()]. \
            combine_first(cls.remap_final_route_method(data_frame)). \
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
    """
    Sex of child

    The binary sex of the child, represented as either Male or Female.
    """
    handler = Handlers.integer
    labels = {1: 'Male', 2: 'Female'}
    pd_type = 'category'
    positions = {
        Y1968: (31, 31),
        **_span(Y1969, Y1988, 35),
        **_span(Y1989, Y2002, 189)
    }

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return data_frame[cls.name()].combine_first(data_frame[Sex.name()])


class Sex(SexOfChild):
    """ Sex of child """
    handler = Handlers.character
    labels = {'M': 'Male', 'F': 'Female'}
    positions = {
        **_span(Y2003, Y2013, 436),
        **_span(Y2014, Y2019, 475)
    }


class BirthFacility(Source, Target):
    """
    Birth Facility

    Indicates whether the birth was an in or out of hospital birth.
    """
    handler = Handlers.integer
    labels = {1: "In Hospital", 2: "Not in Hospital"}
    pd_type = 'category'
    positions = {
        **_span(Y1989, Y2002, 9),
        **_span(Y2003, Y2013, 59),
        **_span(Y2014, Y2019, 50)
    }

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        pod = {
            "Hospital Births": "In Hospital", "Nonhospital Births": "Not in Hospital",
            "En route or born on arrival (BOA)": "Not in Hospital", "Not classifiable": None
        }
        pod75 = {
            "Hospital or Institution": "In Hospital", "Clinic, Center, or a Home": "Not in Hospital",
            "Names places (Drs. Offices)": "Not in Hospital", "Street Address": "Not in Hospital",
            "Not classifiable": None
        }
        aab = {
            "Births in hospitals or institutions": "In Hospital",
            "Births not in hospitals; Attended by physician": "Not in Hospital",
            "Births not in hospitals; Attended by midwife": "Not in Hospital",
            "Other and not specified": None
        }

        return data_frame[cls.name()].combine_first(
            data_frame[PlaceOfDelivery.name()].replace(pod)
        ).combine_first(
            data_frame[PlaceOfDelivery1975.name()].replace(pod75)
        ).combine_first(
            data_frame[AttendantAtBirth.name()].replace(aab)
        )


class PlaceOfDelivery(Source):
    handler = Handlers.integer
    labels = {
        1: "Hospital Births", 2: "Nonhospital Births",
        3: "En route or born on arrival (BOA)", 9: "Not classifiable"
    }
    positions = _span(Y1978, Y1988, 80)


class PlaceOfDelivery1975(Source):
    handler = Handlers.integer
    labels = {
        1: "Hospital or Institution", 2: "Clinic, Center, or a Home",
        3: "Names places (Drs. Offices)", 4: "Street Address", 9: "Not classifiable"
    }
    positions = _span(Y1975, Y1977, 80)


class AttendantAtBirth(Source):
    handler = Handlers.integer
    labels = {
        1: "Births in hospitals or institutions", 2: "Births not in hospitals; Attended by physician",
        3: "Births not in hospitals; Attended by midwife", 4: "Other and not specified"
    }
    positions = {
        Y1968: (58, 58),
        **_span(Y1969, Y1977, 36)
    }


class AgeOfMother(Source, Target):
    """
    Age of Mother

    The age of the mother at time of delivery in single digit years. After 2004,
    births to mothers aged 12 and under, or 50 and over were grouped, resulting
    in uncertainty of the actual age, and in this data set the birth is handled
    as missing for those cases.
    """
    handler = Handlers.integer
    na_value = 99
    pd_type = float
    positions = {
        Y1968: (38, 39),
        **_span(Y1969, Y1988, 41, 42),
        **_span(Y1989, Y1990, 70, 71),
        **_span(Y1991, Y2002, 91, 92),
        Y2003: (77, 78)
    }

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        recodes = {x: None for x in ('10-12 years', '50-54 years')}
        return data_frame[cls.name()].combine_first(
            data_frame[AgeOfMother50.name()].replace(recodes)
        ).combine_first(
            data_frame[AgeOfMother41.name()].replace({'Under 15 years': None})
        )


class AgeOfMother41(Source):
    handler = Handlers.integer
    na_value = None
    labels = {
        1: 'Under 15 years', 2: '15', 3: '16', 4: '17', 5: '18', 6: '19', 7: '20',
        8: '21', 9: '22', 10: '23', 11: '24', 12: '25', 13: '26', 14: '27', 15: '28',
        16: '29', 17: '30', 18: '31', 19: '32', 20: '33', 21: '34', 22: '35',
        23: '36', 24: '37', 25: '38', 26: '39', 27: '40', 28: '41', 29: '42',
        30: '43', 31: '44', 32: '45', 33: '46', 34: '47', 35: '48', 36: '49',
        37: '50', 38: '51', 39: '52', 40: '53', 41: '54'
    }

    positions = {
        **_span(Y1991, Y2002, 72, 73),
        Y2003: (89, 90)
    }


class AgeOfMother50(Source):
    handler = Handlers.integer
    labels = {
        12: '10-12 years', 13: '13', 14: '14', 15: '15', 16: '16', 17: '17',
        18: '18', 19: '19', 20: '20', 21: '21', 22: '22', 23: '23', 24: '24',
        25: '25', 26: '26', 27: '27', 28: '28', 29: '29', 30: '30', 31: '31',
        32: '32', 33: '33', 34: '34', 35: '35', 36: '36', 37: '37', 38: '38',
        39: '39', 40: '40', 41: '41', 42: '42', 43: '43', 44: '44', 45: '45',
        46: '46', 47: '47', 48: '48', 49: '49', 50: '50-54 years'
    }

    positions = {
        **_span(Y2004, Y2013, 89, 90),
        **_span(Y2014, Y2019, 75, 76)
    }


class Parity(Target):
    """
    Parity

    The number of times that the mother has been pregnant and carried the
    the pregnancy to a viable gestational age (including this one).
    """
    pd_type = float

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        return data_frame[BirthOrderDetail.name()].combine_first(
            data_frame[BirthOrderRecode.name()].replace({8: None, 9: None})
        )


class ChildrenBornAlive(Source):
    """
    Number of children born alive, now living

    Sum of all previous live births (now living and now dead) plus this one.
    """
    handler = Handlers.integer
    na_value = 99
    positions = {
        Y1968: (47, 48),
        **_span(Y1969, Y1988, 52, 53),
        **_span(Y1989, Y2002, 100, 101),
        **_span(Y2003, Y2005, 210, 211)
    }


class ChildrenBornAlive06(ChildrenBornAlive):
    """
    Number of children born alive, now living recode

    A recode of detail values.

    1-7 Live birth order
    8 Live birth order of 8 or more
    9 Unknown or not stated
    """
    na_value = 9
    positions = {
        **_span(Y2006, Y2013, 212),
        **_span(Y2014, Y2019, 179)
    }


class BirthOrderDetail(Source):
    """
    Total Birth Order

    Sum of all previous pregnancies plus this one
    """
    handler = Handlers.integer
    na_value = 99
    positions = {
        **_span(Y1969, Y1988, 58, 59),
        **_span(Y1989, Y2002, 103, 104),
        **_span(Y2003, Y2005, 215, 216)
    }


class BirthOrderRecode(BirthOrderDetail):
    """
    Total Birth Order recode

    Sum of all previous pregnancies plus this one

    1-7 Total birth order
    8 Total birth order of 8 or more
    9 Unknown or not stated
    """
    handler = Handlers.integer
    na_value = 9
    positions = {
        **_span(Y2006, Y2013, 217),
        **_span(Y2014, Y2019, 182)
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
    positions = _span(Y1972, Y1984, 208)

    @classmethod
    def remap(cls, data_frame: pd.DataFrame, **kwargs):
        if kwargs.get('year') < 1972:
            return 2
        else:
            return data_frame[cls.name()].fillna(1)


sources = _recurse_subclasses(Source)
targets = [
    t for t in _recurse_subclasses(Target)
    if not any([t in _recurse_subclasses(x) for x in _recurse_subclasses(Target)])
]
