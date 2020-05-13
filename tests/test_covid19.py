from covid19 import __version__
import unittest

from covid19.covid import get_date_date_cases_greater_than
from covid19.scrap import get_covid_data, _read_datafile_from_disc

from datetime import datetime, date



class TestCovid19(unittest.TestCase):
    def test_version(self):
        assert __version__ == '0.1.0'

    def test_get_covid_data(self):
        data = get_covid_data()

    def test_get_date_date_cases_greater_than(self):
        data = _read_datafile_from_disc()

        first_case = get_date_date_cases_greater_than(data)
        correct_date = date(2020, 2, 26)
        self.assertEqual(first_case, correct_date)

        # Ao agrupar por data a coluna "data" passa a ser o index
        data_brasil = data.groupby("data").sum()
        first_case = get_date_date_cases_greater_than(data_brasil)
        self.assertEqual(first_case, correct_date)

    def test_get_state_data(self):
        pass


# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
if __name__ == '__main__':
    unittest.main()
