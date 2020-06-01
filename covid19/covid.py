import logging

import numpy as np
import pandas as pd


def get_date_date_cases_greater_than(df: pd.DataFrame, threshold: int = 0):
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

    assert (result.shape[0] > 0)

    if "data" in result:
        # O dataframe tem uma coluna "data"
        # Vamos fazer um "sort" pois como tem vários estados não necessariamente
        # a primeira data é a mais antiga
        return result.sort_values(by="data").iloc[0].data

    assert result.index.name == "data"
    return result.sort_index().index[0]


def get_dia_de_contaminacao_array(df: pd.DataFrame, min_casos: int = 1):
    """
    Retorna um array contendo o dias de contaminação.

    Isso corresponde a uma sequência de zeros até o primeiro caso de
    contaminação. Então o primeiro caso de contaminação tem valor 1, o dia
    seguinte valor 2 e assim por diante.

    Parameters
    -----------
    df : pd.Dataframe
        Um Dataframe contendo datas únicas e em sequência
    min_casos : int
        Número mínimo de casos para iniciar a contagem de "dias de contaminação"

    Returns
    -------
    np.ndarray
        Um array de inteiros.
    """
    primeiro_dia_de_contaminacao = get_date_date_cases_greater_than(
        df, threshold=min_casos - 1)
    bool_array = df.data >= primeiro_dia_de_contaminacao

    num_dates = df.shape[0]

    # Number of dates with contamination
    num_contamination_dates = sum(bool_array)

    return np.concatenate([
        np.zeros(num_dates - num_contamination_dates, dtype=int),
        np.arange(1, num_contamination_dates + 1, dtype=int)
    ])


def get_brazil_data(df: pd.DataFrame):
    """
    Retorna um DataFrame com os dados do Brasil.

    A planilha disponibilizada no site tem todos os dados juntos: Brasil todo,
    mais cada estado todo, mais dados por cidades.

    Além de pegar apenas os dados do Brasil, o DataFrame retornado possui quatro
    colunas extras: "casosNovos", "obitosNovos", "diasDeContaminacao_1" e
    "diasDeContaminacao_100".

    Colunas que não importam para os dados do Brasil foram removidas. Elas são:
    "estado", "municipio", "codmun", "codRegiaoSaude" e "nomeRegiaoSaude".

    Parameters
    ----------
    df : pd.DataFrame
        O DataFrame obtido ao ler o arquivo de dados disponibilizado pelo
        ministério da saúde. Esse DataFrame possui dados do Brasil, de cada
        estado, e de cada município.

    Returns
    -------
    pd.DataFrame
        Um DataFrame contendo os dados apenas do Brasil.
    """
    data_brasil = df.query("regiao=='Brasil'").copy()

    # xxxxxxxxxx Cleaning xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # In case of multiple rows with the same date, drop all except the first
    duplicated_bool_mask = data_brasil.duplicated("data")
    if sum(duplicated_bool_mask) > 0:
        logging.warning(
            "There are duplicated dates in Brazil data -> dropping all except the first one"
        )
        data_brasil = data_brasil[~duplicated_bool_mask]
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    data_brasil["casosNovos"] = np.diff(data_brasil.casosAcumulado, prepend=0)
    data_brasil["obitosNovos"] = np.diff(data_brasil.obitosAcumulado,
                                         prepend=0)

    data_brasil["diasDeContaminacao_1"] = get_dia_de_contaminacao_array(
        data_brasil, min_casos=1)
    data_brasil["diasDeContaminacao_100"] = get_dia_de_contaminacao_array(
        data_brasil, min_casos=100)

    return data_brasil.drop(labels=[
        "regiao", "coduf", "estado", "municipio", "codmun", "codRegiaoSaude",
        "nomeRegiaoSaude"
    ],
                            axis=1)


def get_all_states_data(df: pd.DataFrame):
    """
    Retorna um Dataframe com apenas os dados dos estados.

    A planilha disponibilizada no site tem todos os dados juntos: Brasil todo,
    mais cada estado todo, mais dados por cidades.

    Para pegar os dados por estado basta pegar linhas que possuem valor na
    coluna 'estado' (caso contrário são dados do Brasil todo) e que NÃO possuem
    valor na coluna "municipio".

    Além de pegar apenas os dados dos estados, o DataFrame retornado possui
    quatro colunas extras: "casosNovos", "obitosNovos", "diasDeContaminacao_1" e
    "diasDeContaminacao_100".

    Colunas que não importam para os dados dos estados foram removidas. Elas
    são: "municipio", "codmun", "codRegiaoSaude" e "nomeRegiaoSaude".

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe com os dados do Brasil todo

    Returns
    -------
    pd.Dataframe
        Dataframe com dados apenas dos estados
    """
    data_estados = df[df.codmun.isna()
                      & np.logical_not(df.estado.isna())].copy()

    # xxxxxxxxxx Cleaning xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # In case of multiple rows with the same date, drop all except the first
    duplicated_bool_mask = data_estados.duplicated(["estado", "data"])
    if sum(duplicated_bool_mask) > 0:
        logging.warning(
            "There are duplicated dates in All States data -> dropping all except the first one"
        )
        data_estados = data_estados[~duplicated_bool_mask]
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    estados = data_estados.estado.unique()

    # Calcula novos casos a partir dos casos acumulados. Note que o primeiro
    # valor na coluna "casosNovos" corresponde ao total de casos acumulados na
    # primeira entrada
    data_estados["casosNovos"] = np.zeros(data_estados.shape[0], dtype=int)
    data_estados["diasDeContaminacao_1"] = np.zeros(data_estados.shape[0],
                                                    dtype=int)
    data_estados["diasDeContaminacao_100"] = np.zeros(data_estados.shape[0],
                                                      dtype=int)
    for sigla in estados:
        data_esse_estado = data_estados[data_estados.estado == sigla]
        data_estados.loc[data_estados.estado == sigla, "casosNovos"] = np.diff(
            data_esse_estado.casosAcumulado, prepend=0)
        data_estados.loc[data_estados.estado == sigla,
                         "obitosNovos"] = np.diff(
                             data_esse_estado.obitosAcumulado, prepend=0)
        data_estados.loc[
            data_estados.estado == sigla,
            "diasDeContaminacao_1"] = get_dia_de_contaminacao_array(
                data_estados[data_estados.estado == sigla])
        data_estados.loc[
            data_estados.estado == sigla,
            "diasDeContaminacao_100"] = get_dia_de_contaminacao_array(
                data_estados[data_estados.estado == sigla], 100)

    return data_estados.drop(
        labels=["municipio", "codmun", "codRegiaoSaude", "nomeRegiaoSaude"],
        axis=1)


# def get_state_data(df: pd.DataFrame, state_abrv: str):
#     """
#     Retorna um dataframe com apenas os dados de um estado específico.

#     A planilha disponibilizada no site tem todos os dados juntos: Brasil todo,
#     mais cada estado todo, mais dados por cidades.

#     Para pegar os dados por estado basta pegar linhas cujo valor na coluna
#     "estado" seja a singla do estado desejado e cuja coluna "municipio" NÃO
#     possui valor.

#     Parameters
#     ----------
#     df : pd.DataFrame
#         Dataframe com os dados do Brasil todo
#     state_abrv : str
#         Abreviatura do estado

#     Returns
#     -------
#     pd.Dataframe
#         Dataframe com dados apenas do estado especificado.
#     """
#     # state_data = df.query(f"estado=='{state_abrv}'")
#     return df[(df.estado == state_abrv) & (df.codmun.isna())].copy()
