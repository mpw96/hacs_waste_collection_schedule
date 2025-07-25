import datetime

import requests
from waste_collection_schedule import Collection  # type: ignore[attr-defined]
from waste_collection_schedule.service.ICS import ICS

TITLE = "Berliner Stadtreinigungsbetriebe"
DESCRIPTION = "Source for Berliner Stadtreinigungsbetriebe waste collection."
URL = "https://bsr.de"
TEST_CASES = {
    "Hufeland_45a": {
        "schedule_id": "04901100010300413840045A",
    },
    "Marktstr_1": {
        "schedule_id": "049011000105000297900010",
    },
}

ENDPOINT_ICS = "https://umnewforms.bsr.de/p/de.bsr.adressen.app//abfuhr/kalender/ics"

def download_monthly_ICS(sess, id, month, year):
    args = {
        "year": year,
        "month": month,
    }
    response = sess.get(
        f"{ENDPOINT_ICS}/{id}", params=args,
    )

    return response.text


ICONS = {
    "Hausmüll": "mdi:trash-can",
    "Biogut": "mdi:leaf",
    "Wertstoffe": "mdi:recycle",
}


def get_icon(text):
    for icon_key, icon_value in ICONS.items():
        if icon_key in text:
            return icon_value
    return None


class Source:
    def __init__(self, schedule_id):
        self._schedule_id = schedule_id
        self._ics = ICS()

    def fetch(self):

        # fetch monthly ics files for the next 12 months
        dates = []
        now = datetime.datetime.now()
        with requests.Session() as sess:
            for i in range(12):
                month, year = now.month + i, now.year
                if month > 12:
                    month = month % 12
                    year = year + 1

                ics = download_monthly_ICS(sess, self._schedule_id, month, year)
                dates.extend(self._ics.convert(ics))

        return [Collection(date=d[0], t=d[1], icon=get_icon(d[1])) for d in dates]
