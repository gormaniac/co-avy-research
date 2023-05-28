"""Enumerate all classic IDs and tie them to their new CAIC UUIDs."""

import asyncio
import json
import logging
import functools
import string
import time

from caicpy import LOGGER
import caicpy.client


LOGGER.setLevel(logging.DEBUG)

YearStart = string.Template("$year-01-01 00:00:00")
YearEnd = string.Template("$year-12-31 23:39:59")

# CAIC API data only goes back to 2010
def gen_years(start_year=10, end_year=23, year_prefix=20):
    """
    Generates the years from start year until end year using year_prefix.

    Parameters
    ----------
    end_year : int, optional
        The last year (YY) this generator returns, by default 23.

    Yields
    ------
    str
        A single year generated by this function.
    """

    for num in iter(range(start_year, end_year + 1)):
        suffix = str(num)
        if len(suffix) == 1:
            prefix = f"{year_prefix}0"
        else:
            prefix = f"{year_prefix}"

        yield prefix + suffix


async def main():
    client = caicpy.client.CaicClient()

    field_report_requests = []
    for year in gen_years(start_year=21, end_year=21):
        field_report_requests.append(
            functools.partial(
                client.field_reports,
                start=YearStart.substitute(year=year),
                end=YearEnd.substitute(year=year),
                page_limit=1000,
            )
        )
    
    _field_reports = await asyncio.gather(*[func() for func in field_report_requests], return_exceptions=True)

    field_reports = []
    for reports in _field_reports:
        if isinstance(reports, Exception):
            LOGGER.warning("Error from CAIC: %s", str(reports))
            continue
        for report in reports:
            field_reports.append(report)

    now = int(time.time())
    with open(f"data/field_reports/{now}.json", "w") as fd:
        json.dump([r.model_dump(mode="json") for r in field_reports], fd)

    id_map = {}
    for report in field_reports:
        if (_id := report.avalanche_detail.classic_id):
            if _id not in id_map.keys():
                id_map[_id] = report.id

    with open(f"data/classic_ids/{now}_clsc_ids.json", "w") as fd:
        json.dump(id_map, fd)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
