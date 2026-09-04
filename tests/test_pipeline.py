import csv
from os.path import join

from hdx.scraper.unicef_emergencies.pipeline import Pipeline
from hdx.utilities.downloader import Download
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve


class TestPipeline:
    def test_generate_dataset(self, configuration, fixtures_dir, input_dir, config_dir):
        with temp_dir(
            "TestUnicefEmergencies",
            delete_on_success=True,
            delete_on_failure=False,
        ) as tempdir:
            with Download(user_agent="test") as downloader:
                retriever = Retrieve(
                    downloader=downloader,
                    fallback_dir=tempdir,
                    saved_dir=input_dir,
                    temp_dir=tempdir,
                    save=False,
                    use_saved=True,
                )
                pipeline = Pipeline(configuration, retriever, tempdir)
                dataset = pipeline.generate_dataset()
                dataset.update_from_yaml(
                    path=join(config_dir, "hdx_dataset_static.yaml")
                )

                assert dataset["name"] == "unicef-level-of-emergencies"
                assert (
                    dataset["title"]
                    == "UNICEF Humanitarian Response: Countries and Emergency Levels"
                )
                assert dataset.get_tags() == ["affected area"]
                assert dataset.get_time_period()["startdate_str"] == "2026-01-01T00:00:00"

                resources = dataset.get_resources()
                assert len(resources) == 1
                resource = resources[0]
                assert resource["name"] == "UNICEF_Level_of_Emergencies_2026.csv"

                with open(
                    join(tempdir, "UNICEF_Level_of_Emergencies_2026.csv"),
                    encoding="utf-8-sig",
                ) as f:
                    rows = list(csv.DictReader(f))

                # HXL hashtag row plus one row per of the 59 countries in the fixture
                assert rows[0] == {
                    "Emergency Level": "#severity",
                    "Country": "#country+name",
                    "Country ISO 3": "#country+code",
                    "Lat": "#geo+lat",
                    "Lon": "#geo+lon",
                }
                assert len(rows) == 60

                by_iso3 = {row["Country ISO 3"]: row for row in rows[1:]}
                # hacFlag=1 + emergency="Others" -> Level 1
                assert by_iso3["ETH"]["Emergency Level"] == "Level 1"
                # emergency="Level 2" passes through directly
                assert by_iso3["HTI"]["Emergency Level"] == "Level 2"
                # emergency="Level 3" passes through directly
                assert by_iso3["SDN"]["Emergency Level"] == "Level 3"
                assert by_iso3["UGA"]["Emergency Level"] == "Level 3"

    def test_get_latest_year(self, configuration, input_dir):
        with temp_dir(
            "TestUnicefEmergenciesYear",
            delete_on_success=True,
            delete_on_failure=False,
        ) as tempdir:
            with Download(user_agent="test") as downloader:
                retriever = Retrieve(
                    downloader=downloader,
                    fallback_dir=tempdir,
                    saved_dir=input_dir,
                    temp_dir=tempdir,
                    save=False,
                    use_saved=True,
                )
                pipeline = Pipeline(configuration, retriever, tempdir)
                assert pipeline.get_latest_year() == 2026
