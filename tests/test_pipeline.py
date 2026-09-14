from datetime import datetime
from os.path import join

from hdx.utilities.compare import assert_files_same
from hdx.utilities.downloader import Download
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve

from hdx.scraper.unicef_emergencies.pipeline import Pipeline


class TestPipeline:
    def test_generate_dataset(self, configuration, fixtures_dir, input_dir, config_dir):
        with temp_dir("TestUnicefEmergencies") as tempdir:
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
                dataset = pipeline.generate_dataset(datetime(2026, 10, 1))
                dataset.update_from_yaml(
                    path=join(config_dir, "hdx_dataset_static.yaml")
                )

                assert dataset == {
                    "name": "unicef-level-of-emergencies",
                    "title": "UNICEF Humanitarian Response: Countries and Emergency Levels",
                    "dataset_date": "[2026-10-01T00:00:00 TO 2026-10-01T23:59:59]",
                    "tags": [
                        {
                            "name": "affected area",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        }
                    ],
                    "groups": [
                        {"name": "world"},
                    ],
                    "license_id": "cc-by",
                    "methodology": "Registry",
                    "dataset_source": "UNICEF",
                    "package_creator": "HDX Data Systems Team",
                    "private": False,
                    "maintainer": "4c4492ca-9b78-438a-b66a-587e2bb017b1",
                    "owner_org": "3ab17ac1-1196-4501-a4dc-a01d2e52ff7c",
                    "data_update_frequency": -2,
                    "notes": "The Core Commitments for Children (CCCs) in Humanitarian Action 2020 set out a policy and framework to equip UNICEF and its partners to deliver a principled, timely, quality and child-centred humanitarian response and advocacy in any crises with humanitarian consequences. The determination of a Unicef Level 3 or Level 2 emergency is made based on scale; urgency; complexity; and capacity of RO and COs affected by the crisis.  \\n  \\nData extracted from https://open.unicef.org/flows-overview",
                }

                resources = dataset.get_resources()
                assert resources == [
                    {
                        "name": "UNICEF_Level_of_Emergencies_2026.csv",
                        "description": "List of countries in L1, L2, L3 emergencies as of 1 October 2026.",
                        "format": "csv",
                    },
                ]

                assert_files_same(
                    join(fixtures_dir, "UNICEF_Level_of_Emergencies_2026.csv"),
                    join(tempdir, "UNICEF_Level_of_Emergencies_2026.csv"),
                )
