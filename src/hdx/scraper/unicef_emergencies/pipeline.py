#!/usr/bin/python
"""UNICEF Level of Emergencies scraper"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)

# open.unicef.org sits behind Cloudflare bot management, which returns a 403
# challenge page to requests that don't look like a real browser. These
# headers are the minimum needed to reliably get past it.
_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://open.unicef.org/flows-overview",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
}


class Pipeline:
    def __init__(self, configuration: Configuration, retriever: Retrieve, tempdir: str):
        self._configuration = configuration
        self._retriever = retriever
        self._tempdir = tempdir

    def get_latest_year(self) -> int:
        years_url = self._configuration["years_url"]
        years = self._retriever.download_json(
            years_url, "unicef_emergencies_years.json", headers=_HEADERS
        )
        return max(years)

    def get_emergency_levels(self, year: int) -> Dict[str, Dict]:
        url = self._configuration["base_url"].format(year=year)
        response = self._retriever.download_json(
            url, f"unicef_emergencies_{year}.json", headers=_HEADERS
        )

        rows = {}
        for country_data in response["data"].values():
            iso3 = country_data["isoalpha3"]
            emergency = country_data["emergency"]
            hac_flag = country_data["hacFlag"]

            if emergency == "Others" and hac_flag == 1:
                level = "Level 1"
            elif emergency in ("Level 2", "Level 3"):
                level = emergency
            else:
                logger.warning(
                    f"Unrecognised emergency/hacFlag combination for {iso3}: "
                    f"emergency={emergency!r}, hacFlag={hac_flag!r} - skipping"
                )
                continue

            rows[iso3] = {
                "Emergency Level": level,
                "Country": country_data["country"],
                "Country ISO 3": iso3,
                "Lat": country_data["lat"],
                "Lon": country_data["lon"],
            }
        return rows

    def generate_dataset(self) -> Optional[Dataset]:
        year = self.get_latest_year()
        rows = self.get_emergency_levels(year)
        if not rows:
            logger.error("No emergency level data retrieved, not updating dataset")
            return None

        dataset_name = self._configuration["dataset_name"]
        dataset_title = self._configuration["dataset_title"]
        dataset_tags = self._configuration["tags"]

        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
            }
        )
        dataset.set_time_period_year_range(year)
        dataset.add_tags(dataset_tags)

        for iso3 in rows:
            try:
                dataset.add_country_location(iso3)
            except HDXError:
                logger.error(f"Could not add country location for {iso3}")

        resource_name = self._configuration["resource_name"].format(year=year)
        resource_date = datetime.now(timezone.utc).strftime("%-d %B %Y")
        resource_description = self._configuration["resource_description"].format(
            date=resource_date
        )

        dataset.generate_resource_from_iterable(
            headers=list(next(iter(rows.values())).keys()),
            iterable=list(rows.values()),
            hxltags=self._configuration["hxl_tags"],
            folder=self._tempdir,
            filename=resource_name,
            resourcedata={
                "name": resource_name,
                "description": resource_description,
            },
            encoding="utf-8-sig",
        )

        return dataset
