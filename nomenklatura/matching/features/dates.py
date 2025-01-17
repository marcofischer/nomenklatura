from typing import Iterable, Set
from prefixdate import Precision

from nomenklatura.entity import CompositeEntity as Entity
from nomenklatura.matching.features.util import props_pair, has_overlap

KEY_DATES = ["birthDate", "incorporationDate", "registrationDate", "startDate"]


def with_precision(values: Iterable[str], precision: Precision) -> Set[str]:
    dates = set()
    for value in values:
        if len(value) >= precision.value:
            dates.add(value[: precision.value])
    return dates


def key_day_matches(left: Entity, right: Entity) -> float:
    """The birth date or incorporation date of the two entities is the same."""
    left_dates, right_dates = props_pair(left, right, KEY_DATES)
    left_days = with_precision(left_dates, Precision.DAY)
    right_days = with_precision(right_dates, Precision.DAY)
    return has_overlap(left_days, right_days)


def key_year_matches(left: Entity, right: Entity) -> float:
    """The birth date or incorporation year of the two entities is the same."""
    left_dates, right_dates = props_pair(left, right, KEY_DATES)
    left_years = with_precision(left_dates, Precision.YEAR)
    right_years = with_precision(right_dates, Precision.YEAR)
    if len(left_years.intersection(right_dates)) > 0:
        return 1.0
    if len(right_years.intersection(left_dates)) > 0:
        return 1.0
    return 0.0
