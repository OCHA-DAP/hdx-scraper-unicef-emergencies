from os.path import join

import pytest
from hdx.api.configuration import Configuration
from hdx.api.locations import Locations
from hdx.data.vocabulary import Vocabulary
from hdx.location.country import Country
from hdx.utilities.useragent import UserAgent


@pytest.fixture(scope="session")
def fixtures_dir():
    return join("tests", "fixtures")


@pytest.fixture(scope="session")
def input_dir(fixtures_dir):
    return join(fixtures_dir, "input")


@pytest.fixture(scope="session")
def config_dir(fixtures_dir):
    return join("src", "hdx", "scraper", "unicef_emergencies", "config")


@pytest.fixture(scope="session")
def configuration(config_dir):
    UserAgent.set_global("test")
    Configuration._create(
        hdx_read_only=True,
        hdx_site="prod",
        project_config_yaml=join(config_dir, "project_configuration.yaml"),
    )
    # All 59 countries present in the tests/fixtures/input/unicef_emergencies_2026.json fixture
    Locations.set_validlocations(
        [
            {"name": "afg", "title": "Afghanistan"},
            {"name": "arm", "title": "Armenia"},
            {"name": "aze", "title": "Azerbaijan"},
            {"name": "bdi", "title": "Burundi"},
            {"name": "bfa", "title": "Burkina Faso"},
            {"name": "bgd", "title": "Bangladesh"},
            {"name": "bgr", "title": "Bulgaria"},
            {"name": "blr", "title": "Belarus"},
            {"name": "blz", "title": "Belize"},
            {"name": "bra", "title": "Brazil"},
            {"name": "caf", "title": "Central African Republic"},
            {"name": "chl", "title": "Chile"},
            {"name": "cmr", "title": "Republic of Cameroon"},
            {"name": "cod", "title": "Democratic Republic of Congo"},
            {"name": "col", "title": "Colombia"},
            {"name": "cri", "title": "Costa Rica"},
            {"name": "dom", "title": "Dominican Republic"},
            {"name": "ecu", "title": "Ecuador"},
            {"name": "egy", "title": "Egypt"},
            {"name": "eth", "title": "Ethiopia"},
            {"name": "gha", "title": "Ghana"},
            {"name": "gin", "title": "Guinea"},
            {"name": "gtm", "title": "Guatemala"},
            {"name": "guy", "title": "Guyana"},
            {"name": "hnd", "title": "Honduras"},
            {"name": "hti", "title": "Haiti"},
            {"name": "irn", "title": "Iran"},
            {"name": "irq", "title": "Iraq"},
            {"name": "jor", "title": "Jordan"},
            {"name": "lbn", "title": "Lebanon"},
            {"name": "lby", "title": "Libya"},
            {"name": "lka", "title": "Sri Lanka"},
            {"name": "mda", "title": "Moldova"},
            {"name": "mex", "title": "Mexico"},
            {"name": "mli", "title": "Mali"},
            {"name": "mmr", "title": "Myanmar"},
            {"name": "moz", "title": "Republic of Mozambique"},
            {"name": "ner", "title": "Niger"},
            {"name": "nga", "title": "Nigeria"},
            {"name": "pak", "title": "Pakistan"},
            {"name": "pan", "title": "Panama"},
            {"name": "per", "title": "Peru"},
            {"name": "pol", "title": "Poland"},
            {"name": "pse", "title": "Palestine, State of"},
            {"name": "rou", "title": "Romania"},
            {"name": "rwa", "title": "Rwanda"},
            {"name": "sdn", "title": "Sudan"},
            {"name": "slv", "title": "El Salvador"},
            {"name": "som", "title": "Somalia"},
            {"name": "ssd", "title": "South Sudan"},
            {"name": "syr", "title": "Syria"},
            {"name": "tcd", "title": "Chad"},
            {"name": "tkm", "title": "Turkmenistan"},
            {"name": "tur", "title": "Turkiye"},
            {"name": "tza", "title": "United Rep. of Tanzania"},
            {"name": "uga", "title": "Uganda"},
            {"name": "ukr", "title": "Ukraine"},
            {"name": "ven", "title": "Venezuela"},
            {"name": "yem", "title": "Yemen"},
            {"name": "world", "title": "World"},
        ]
    )
    Country.countriesdata(False)
    Vocabulary._approved_vocabulary = {
        "tags": [{"name": tag} for tag in ("affected area",)],
        "id": "b891512e-9516-4bf5-962a-7a289772a2a1",
        "name": "approved",
    }
    return Configuration.read()
