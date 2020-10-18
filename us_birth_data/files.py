from pathlib import Path

import pandas as pd


class YearData:
    pub_file: str = None
    year: int = None

    @classmethod
    def read_parquet(cls, columns: list = None):
        return pd.read_parquet(
            Path('pq', f"{cls.__name__}.parquet"), columns=columns
        )


class Y1968(YearData):
    pub_file = 'Nat1968.PUB.gz'
    year = 1968


class Y1969(YearData):
    pub_file = 'Nat1969.PUB.gz'
    year = 1969


class Y1970(YearData):
    pub_file = 'Nat1970.PUB.gz'
    year = 1970


class Y1971(YearData):
    pub_file = 'Nat1971.pub.gz'
    year = 1971


class Y1972(YearData):
    pub_file = 'Nat1972.pub.gz'
    year = 1972


class Y1973(YearData):
    pub_file = 'Nat1973.pub.gz'
    year = 1973


class Y1974(YearData):
    pub_file = 'Nat1974.pb.gz'
    year = 1974


class Y1975(YearData):
    pub_file = 'Nat1975.pb.gz'
    year = 1975


class Y1976(YearData):
    pub_file = 'Nat1976.pb.gz'
    year = 1976


class Y1977(YearData):
    pub_file = 'Nat1977.pb.gz'
    year = 1977


class Y1978(YearData):
    pub_file = 'Nat1978.pb.gz'
    year = 1978


class Y1979(YearData):
    pub_file = 'Nat1979.gz'
    year = 1979


class Y1980(YearData):
    pub_file = 'Nat1980.PUB.gz'
    year = 1980


class Y1981(YearData):
    pub_file = 'Nat1981.txt.gz'
    year = 1981


class Y1982(YearData):
    pub_file = 'Nat1982.gz'
    year = 1982


class Y1983(YearData):
    pub_file = 'Nat1983.txt.gz'
    year = 1983


class Y1984(YearData):
    pub_file = 'Nat1984.txt.gz'
    year = 1984


class Y1985(YearData):
    pub_file = 'Nat1985.gz'
    year = 1985


class Y1986(YearData):
    pub_file = 'Nat1986.gz'
    year = 1986


class Y1987(YearData):
    pub_file = 'Nat1987.txt.gz'
    year = 1987


class Y1988(YearData):
    pub_file = 'Nat1988.txt.gz'
    year = 1988


class Y1989(YearData):
    pub_file = 'Nat1989.PUB.gz'
    year = 1989


class Y1990(YearData):
    pub_file = 'Nat1990.pub.gz'
    year = 1990


class Y1991(YearData):
    pub_file = 'Nat1991.pub.gz'
    year = 1991


class Y1992(YearData):
    pub_file = 'Nat1992.PUB.gz'
    year = 1992


class Y1993(YearData):
    pub_file = 'Nat1993.PUB.gz'
    year = 1993


class Y1994(YearData):
    pub_file = 'Nat1994us.us.gz'
    year = 1994


class Y1995(YearData):
    pub_file = 'Nat1995us.dat.gz'
    year = 1995


class Y1996(YearData):
    pub_file = 'Nat1996us.us.gz'
    year = 1996


class Y1997(YearData):
    pub_file = 'Nat1997us.us.gz'
    year = 1997


class Y1998(YearData):
    pub_file = 'Nat1998us.pb.gz'
    year = 1998


class Y1999(YearData):
    pub_file = 'Nat1999us.us.gz'
    year = 1999


class Y2000(YearData):
    pub_file = 'Nat2000us.pb.gz'
    year = 2000


class Y2001(YearData):
    pub_file = 'Nat2001us.US.gz'
    year = 2001


class Y2002(YearData):
    pub_file = 'Nat2002us.PB.gz'
    year = 2002


class Y2003(YearData):
    pub_file = 'Nat2003us.dat.gz'
    year = 2003


class Y2004(YearData):
    pub_file = 'Nat2004us.dat.gz'
    year = 2004


class Y2005(YearData):
    pub_file = 'Nat2005us.dat.gz'
    year = 2005


class Y2006(YearData):
    pub_file = 'Nat2006us.dat.gz'
    year = 2006


class Y2007(YearData):
    pub_file = 'Nat2007us.dat.gz'
    year = 2007


class Y2008(YearData):
    pub_file = 'Nat2008us.dat.gz'
    year = 2008


class Y2009(YearData):
    pub_file = 'Nat2009us.r20131202.gz'
    year = 2009


class Y2010(YearData):
    pub_file = 'Nat2010us.r20131202.gz'
    year = 2010


class Y2011(YearData):
    pub_file = 'Nat2011us.r20131211.gz'
    year = 2011


class Y2012(YearData):
    pub_file = 'Nat2012us.r20131217.gz'
    year = 2012


class Y2013(YearData):
    pub_file = 'Nat2013us.r20141016.gz'
    year = 2013


class Y2014(YearData):
    pub_file = 'Nat2014us.txt.gz'
    year = 2014


class Y2015(YearData):
    pub_file = 'Nat2015us.txt.gz'
    year = 2015


class Y2016(YearData):
    pub_file = 'Nat2016us.txt.gz'
    year = 2016


class Y2017(YearData):
    pub_file = 'Nat2017US.txt.gz'
    year = 2017


class Y2018(YearData):
    pub_file = 'Nat2018us.txt.gz'
    year = 2018


class Y2019(YearData):
    pub_file = 'Nat2019us.txt.gz'
    year = 2019
