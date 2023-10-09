import re
from typing import Optional, Self

DAYS_KEY = "days"
HOURS_KEY = "hours"
MINUTES_KEY = "minutes"
TIME_REGEX = re.compile(
    f"^((?P<{DAYS_KEY}>[0-9]+)[dD])?((?P<{HOURS_KEY}>[0-9]+)[hH])?((?P<{MINUTES_KEY}>[0-9]+)[mM])?$"
)
M_IN_H = 60
M_IN_D = 24 * M_IN_H



class TimeAccumulator:
    def __init__(self, time: Optional[str] = None):
        self.__minutes__ = 0
        if time is not None:
            self.add(time)

    def add(self, time: str):
        matches = TIME_REGEX.search(time)
        if matches is not None:
            if (m := matches.group(MINUTES_KEY)) is not None:
                self.__minutes__ += int(m)
            if (h := matches.group(HOURS_KEY)) is not None:
                self.__minutes__ += M_IN_H * int(h)
            if (d := matches.group(DAYS_KEY)) is not None:
                self.__minutes__ += M_IN_D * int(d)

    def days(self) -> int:
        return self.__minutes__ // M_IN_D
    
    def hours(self) -> int:
        return (self.__minutes__ % M_IN_D) // M_IN_H

    def minutes(self) -> int:
        return self.__minutes__ % M_IN_H

    def __str__(self):
        time = ""
        if (d := self.days()) != 0:
            time += f"{d}d"
        if (h := self.hours()) != 0:
            time += f"{h}h"
        if (m := self.minutes()) != 0:
            time += f"{m}m"
        return time

    def __add__(self, other: Self):
        ta = TimeAccumulator()
        ta.__minutes__ = self.__minutes__ + other.__minutes__
        return ta