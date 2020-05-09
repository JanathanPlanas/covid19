

import logging
from pathlib import Path

import pandas as pd

from scrap import get_covid_data


def get_date_first_case(df):
    """
    Retorna a primeira data com caso de covid
    """
    result = df[df.casosAcumulados>0]
    assert(result.shape[0] > 0)

    return result.data.iloc[0]


def get_state_cata(df, state_abrv):
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
    state_abrv = 'CE'
    state_data = data.query(f"estado=='{state_abrv}'")
    return state_data

if __name__ == '__main__':
    data = get_covid_data()

    print(f"Data do primeiro caso: {get_date_first_case(data)}")

    # print(file_is_current)
