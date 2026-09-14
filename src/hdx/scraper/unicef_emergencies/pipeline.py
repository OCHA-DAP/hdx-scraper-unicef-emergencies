#!/usr/bin/python
"""UNICEF Level of Emergencies scraper"""

import logging
from datetime import datetime

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, configuration: Configuration, retriever: Retrieve, tempdir: str):
        self._configuration = configuration
        self._retriever = retriever
        self._tempdir = tempdir

    def get_latest_year(self) -> int:
        years_url = self._configuration["years_url"]
        years = self._retriever.download_json(years_url)
        return max(years)

    def get_emergency_levels(self, year: int) -> list[dict[str, dict]]:
        url = self._configuration["base_url"].format(year=year)
        response = self._retriever.download_json(url)

        rows = []
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

            rows.append(
                {
                    "Emergency Level": level,
                    "Country": country_data["country"],
                    "Country ISO 3": iso3,
                    "Lat": country_data["lat"],
                    "Lon": country_data["lon"],
                }
            )
        return rows

    def generate_dataset(self, today: datetime) -> Dataset | None:
        year = self.get_latest_year()
        rows = self.get_emergency_levels(year)
        if not rows:
            logger.error("No emergency level data retrieved, not updating dataset")
            return None

        dataset_name = self._configuration["dataset_name"]
        dataset_title = self._configuration["dataset_title"]

        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
            }
        )
        dataset.set_time_period(today, today)
        dataset.add_tags(self._configuration["tags"])
        dataset.add_other_location("world")

        resource_name = self._configuration["resource_name"].format(year=year)
        resource_date = today.strftime("%-d %B %Y")
        resource_description = self._configuration["resource_description"].format(
            date=resource_date
        )

        dataset.generate_resource(
            folder=self._tempdir,
            filename=resource_name,
            rows=rows,
            headers=list(rows[0].keys()),
            resourcedata={
                "name": resource_name,
                "description": resource_description,
            },
            encoding="utf-8-sig",
        )

        return dataset
