"""Red-green tests for company → country assignment.

Regression net for the patch-1.13.1 ep2 DLC bug: ep2 company files use the new
syntax `s:STATE_X = { ... }` directly inside `possible = {}`, instead of the
old `any_scope_state = { state_region = s:STATE_X ... }`. Before the fix, the
parser's regex only matched the old form and these companies fell through to
country = None.
"""
import unittest

from victoria3_company_parser import Victoria3CompanyParserV6Final


class CompanyCountryAssignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parser = Victoria3CompanyParserV6Final(game_directory="game")
        parser.parse_state_to_country_mappings()
        parser.parse_company_history()
        parser.parse_wiki_data()
        parser.parse_prestige_goods()
        parser.parse_all_companies()
        cls.companies = parser.companies

    def assert_country(self, company_key, expected_country):
        if company_key not in self.companies:
            self.fail("{} not parsed".format(company_key))
        actual = self.companies[company_key].get("country")
        self.assertEqual(
            expected_country,
            actual,
            "{}: expected country {!r}, got {!r}".format(company_key, expected_country, actual),
        )

    # New ep2 (1.13.1) DLC syntax — uses `s:STATE_X = { ... }` directly.
    def test_sumitomo_is_japan(self):
        self.assert_country("company_sumitomo", "JAP")

    def test_yasuda_is_japan(self):
        self.assert_country("company_yasuda", "JAP")

    def test_tokyo_electric_light_is_japan(self):
        self.assert_country("company_tokyo_electric_light_company", "JAP")

    def test_noda_shoyu_is_japan(self):
        self.assert_country("company_noda_shoyu", "JAP")

    # Pre-1.13.1 syntax — uses `any_scope_state = { state_region = s:STATE_X }`.
    # Guards against regressions from the regex change.
    def test_us_steel_is_usa(self):
        self.assert_country("company_us_steel", "USA")


if __name__ == "__main__":
    unittest.main()
