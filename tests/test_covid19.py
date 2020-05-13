from covid19 import __version__
import unittest
import pandas as pd
from covid19.covid import get_date_date_cases_greater_than, get_dia_de_contaminacao_array
from covid19.scrap import get_covid_data, read_datafile_from_disc

from datetime import datetime, date

from pathlib import Path
import numpy as np


class TestCovid19(unittest.TestCase):
    def test_version(self):
        assert __version__ == '0.1.0'

    # def test_get_covid_data(self):
    #     data = get_covid_data()

    def test_get_date_date_cases_greater_than(self):
        # Brasil
        data = pd.read_excel("dados_test_Brasil.xlsx")
        first_case = get_date_date_cases_greater_than(data)
        correct_date = date(2020, 2, 26)
        self.assertEqual(first_case, correct_date)

        first_case = get_date_date_cases_greater_than(data, 50)
        correct_date = date(2020, 3, 11)
        self.assertEqual(first_case, correct_date)

        first_case = get_date_date_cases_greater_than(data, 100)
        correct_date = date(2020, 3, 14)
        self.assertEqual(first_case, correct_date)

        first_case = get_date_date_cases_greater_than(data, 1000)
        correct_date = date(2020, 3, 21)
        self.assertEqual(first_case, correct_date)

        first_case = get_date_date_cases_greater_than(data, 10000)
        correct_date = date(2020, 4, 4)
        self.assertEqual(first_case, correct_date)

        # Ceará
        data = pd.read_excel("dados_test_CE.xlsx")
        first_case = get_date_date_cases_greater_than(data)
        correct_date = date(2020, 3, 17)

        data = pd.read_excel("dados_test_CE.xlsx")
        first_case = get_date_date_cases_greater_than(data, 1000)
        correct_date = date(2020, 4, 6)
        self.assertEqual(first_case, correct_date)

    def test_get_dia_de_contaminacao_array(self):
        # Brasil
        data = pd.read_excel("dados_test_Brasil.xlsx")
        array = get_dia_de_contaminacao_array(data, 1)
        expected_array = np.arange(1, 78, dtype=int)
        np.testing.assert_array_equal(array, expected_array)

        array = get_dia_de_contaminacao_array(data, 100)
        expected_array = np.concatenate(
            [np.zeros(17, dtype=int),
             np.arange(1, 78 - 17, dtype=int)])
        np.testing.assert_array_equal(array, expected_array)

        array = get_dia_de_contaminacao_array(data, 1000)
        expected_array = np.concatenate(
            [np.zeros(24, dtype=int),
             np.arange(1, 78 - 24, dtype=int)])
        np.testing.assert_array_equal(array, expected_array)

        # Ceará
        data = pd.read_excel("dados_test_CE.xlsx")
        array = get_dia_de_contaminacao_array(data, 1)
        expected_array = np.arange(1, 58, dtype=int)
        np.testing.assert_array_equal(array, expected_array)

        array = get_dia_de_contaminacao_array(data, 100)
        expected_array = np.concatenate(
            [np.zeros(5, dtype=int),
             np.arange(1, 58 - 5, dtype=int)])
        np.testing.assert_array_equal(array, expected_array)

        array = get_dia_de_contaminacao_array(data, 1000)
        expected_array = np.concatenate(
            [np.zeros(20, dtype=int),
             np.arange(1, 58 - 20, dtype=int)])
        np.testing.assert_array_equal(array, expected_array)

    def test_get_state_data(self):
        pass


# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
if __name__ == '__main__':
    unittest.main()
