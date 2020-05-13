

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from .scrap import get_covid_data


def get_dia_de_contaminacao_array(df):
    """
    Retorna um array contendo o dias de contaminação.

    Isso corresponde a uma sequência de zeros até o primeiro caso de
    contaminação. Então o primeiro caso de contaminação tem valor 1, o dia
    seguinte valor 2 e assim por diante.

    Parameters
    -----------
    df : pd.Dataframe
        Um Dataframe contendo datas únicas e em sequência

    Returns
    -------
    np.ndarray
        Um array de inteiros.
    """
    primeiro_dia_de_contaminacao = get_date_date_cases_greater_than(df)
    bool_array = df.data >= primeiro_dia_de_contaminacao

    num_dates = df.shape[0]

    # Number of dates with contamination
    num_contamination_dates = sum(bool_array)

    return np.concatenate([np.zeros(num_dates - num_contamination_dates, dtype=int), np.arange(1, num_contamination_dates+1, dtype=int)])


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
    result = df[df.casosAcumulado > threshold]

    assert(result.shape[0] > 0)

    if "data" in result:
        # O dataframe tem uma coluna "data"
        # Vamos fazer um "sort" pois como tem vários estados não necessariamente
        # a primeira data é a mais antiga
        return result.sort_values(by="data").iloc[0].data

    assert result.index.name == "data"
    return result.sort_index().index[0]


def get_all_states_data(df):
    """
    Retorna um Dataframe com apenas os dados dos estados.

    A planilha disponibilizada no site tem todos os dados juntos: Brasil todo,
    mais cada estado todo, mais dados por cidades.

    Para pegar os dados por estado basta pegar linhas que possuem valor na
    coluna 'estado' (caso contrário são dados do Brasil todo) e que NÃO possuem
    valor na coluna "municipio".

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe com os dados do Brasil todo

    Returns
    -------
    pd.Dataframe
        Dataframe com dados apenas dos estados
    """
    return df[df.codmun.isna() & np.logical_not(df.estado.isna())].copy()


def get_state_data(df, state_abrv):
    """
    Retorna um dataframe com apenas os dados de um estado específico.

    A planilha disponibilizada no site tem todos os dados juntos: Brasil todo,
    mais cada estado todo, mais dados por cidades.

    Para pegar os dados por estado basta pegar linhas cujo valor na coluna
    "estado" seja a singla do estado desejado e cuja coluna "municipio" NÃO
    possui valor.

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
    # state_data = df.query(f"estado=='{state_abrv}'")
    return df[(df.estado == state_abrv) & (df.codmun.isna())].copy()

# if __name__ == '__main__':
#     data = get_covid_data()

#     print(f"Data do primeiro caso: {get_date_date_cases_greater_than(data, 0)}")

#     # print(file_is_current)
