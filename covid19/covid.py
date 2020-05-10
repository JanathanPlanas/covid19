

import logging
from pathlib import Path

import pandas as pd

from .scrap import get_covid_data


def get_date_date_cases_greater_than(df, threshold=0):
    """
    Retorna a data a partir de quando o número de casos for maior que
    `threshold`.

    A coluna considerada para o número de casos é "casosAcumulados" e a data
    pode estar ou em uma coluna "data" ou no index (também de nome "data").

    Parameters
    ----------
    df : pd.Dataframe
        Os dados
    threshold : int
        Número de casos mínimo

    Returns
    -------
    datatime.date
        A data cujo número de casos ultrapassou o threshold.
    """
    result = df[df.casosAcumulados > threshold]

    assert(result.shape[0] > 0)

    if "data" in result:
        # O dataframe tem uma coluna "data"
        # Vamos fazer um "sort" pois como tem vários estados não necessariamente
        # a primeira data é a mais antiga
        return result.sort_values(by="data").iloc[0].data

    assert result.index.name == "data"
    return result.sort_index().index[0]


def get_state_data(df, state_abrv):
    """
    Retirna um dataframe com apenas os dados de um estado específico

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe com os dados do Brasil todo
    state_abrv : str
        Abreviatura do estado

    Returns
    -------
    pd.Dataframe
        Dataframe com dados apenas do estado especificado.
    """
    state_data = df.query(f"estado=='{state_abrv}'")
    return state_data

if __name__ == '__main__':
    data = get_covid_data()

    print(f"Data do primeiro caso: {get_date_date_cases_greater_than(data, 0)}")

    # print(file_is_current)
