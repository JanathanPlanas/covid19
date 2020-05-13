# Covid 19 Brazil

Some code to parse and visualize covid-19 data for Brazil [official
sources](https://covid.saude.gov.br/).

In order to run this code, install [poetry](https://python-poetry.org/) and then
run the `poetry install` command to create a virtual environment and install all
dependencies.

After that activate the environment with the `poetry shell` command.

The visualizations are in the `notebooks/visualizations.ipynb` file.

## Jupyterlab extensions ##

These are some useful jupyterlab extensions that you might want to install
through jupyterlab. The "server part" of the extensions that have a server part
are listed as dependencies in `pyproject.toml` and should already be installed
if you run the `poetry install` command. Thus, you only need to install the
client part and client-only extensions.

- @jupyterlab/toc
- @jupyter-widgets/jupyterlab-manager
- @jupyterlab/debugger
- @ryantam626/jupyterlab_code_formatter  ->  Also with server extension
- jupyterlab-jupytext                    ->  Also with server extension
- @bokeh/jupyter_bokeh
- jupyterlab-lsp                         ->  Also with server extension (jupyterlab-lsp and python-language-server[all])
