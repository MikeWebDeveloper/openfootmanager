**NOTE:** *THIS PROJECT IS STILL UNDER DEVELOPMENT, AND IS NOT READY FOR GAMEPLAY YET. AS SOON AS GAMEPLAY FEATURES ARE IMPLEMENTED, THIS NOTE WILL BE REMOVED AND NEW INFO WILL BE ADDED TO THIS REPOSITORY.*

![Openfoot logo](images/openfoot.png)

# OPENFOOT MANAGER PROJECT

**OpenFoot Manager** (temporary name) is a free and open source football/soccer manager game, licensed under the [GPLv3](LICENSE.md), inspired by the famous franchise Football Manager&trade;, and based on the source code of [Bygfoot](https://bygfoot.sourceforge.io/new/), an abandoned manager game.

The purpose of this project is to provide an interesting and fun game for simulating a manager's life in a simple way: managing a team, dealing with players, finances and many other features. Resembling the gameplay of Football Manager, FIFA Manager, Championship Manager, Elifoot, Bygfoot, Brasfoot etc. this game aims to become a complete alternative for these games.

## INSTALLATION

The game is still under development and it is not even close to ready for gameplay action. However, we already have a debug version of the game for testing purposes.

To run the debug build, ensure that you have Python 3.10 or higher.

Clone the repository using:

```
git clone https://github.com/openfootmanager/openfootmanager.git
```

We don't use external git repositories, so there's no need for a `--recursive` clone.

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/) or [Poetry](https://python-poetry.org/) to manage virtual environments and dependencies.

### Pipenv

To install Pipenv and install the project's dependencies, run the following commands:

```
pip install pipenv
```

After cloning the repository, install the virtualenv and its dependencies using:

```
pipenv install
```

For contributors, you might also need development dependencies (black, isort, flake8, pytest, pre-commit):

```
pipenv install --dev
```

If you want to commit to the repo, install pre-commit:

```
pipenv run python -m pre-commit install
```

To run the tests:

```
pipenv run pytest
```

To run the debug version of the project, use the `run.py` file at the root of this project folder:

```
pipenv run python run.py
```

### Poetry

Poetry is a standard in most Python projects. It uses the `pyproject.toml`, introduced in [PEP 518](https://peps.python.org/pep-0518/), to manage
the project's dependencies and virtualenvs. It's a little more convenient than Pipenv, so you can use it to run the project as well.

To install Poetry:

```
pip install poetry
```

Then you can just install the dependencies with:

```
poetry install
```

This will also install the development dependencies. If you only wish to run the project and do not want to contribute,
install it using the following command:

```
poetry install --without dev
```

Similar to Pipenv, you can run things inside poetry's virtualenv with the `poetry run` command. If you wish to contribute,
you must install the `pre-commit` package to allow pre-commit hooks:

```
poetry run pre-commit install
```

We use them to ensure code standards and formatting used throughout the project, so we don't need to nitpick on little
issues with formatting and following PEP8.

To run the tests, use `pytest`:

```
poetry run pytest
```

And to run the current version of the project, run:

```
poetry run python run.py
```

## CONTRIBUTING

Check the [CONTRIBUTING](CONTRIBUTING.md) file for more information on how to contribute.

## FEATURES

The game will have a number of features inspired by other established games on the market. The following features are planned:

### MAIN PLANNED FEATURES

- [ ] Choose any team and any league to manage
- [ ] Manage the team's finances
- [ ] Manage team's roster, being able to hire/fire players, choose team's formations and which players are going to play
- [ ] Organize practice sections, developing players even further
- [ ] Find new talents from Youth Academy
- [ ] Qualify for major leagues and championships, win important trophies
- [ ] Get the chance to become a national team's manager
- [ ] Simulation of games with Match Live Events (Descriptions of most important match events)
- [ ] Simulate results of other games
- [ ] Talk to the press
- [ ] Database of fictitious players

### ADDITIONAL FEATURES

- [ ] 3D simulation of matches
- [ ] Expand database
- [ ] Sponsorship with products that boost player's performances
- [ ] Mod support

## LICENSE

    OpenFoot Manager - A free and open source soccer management game
    Copyright (C) 2020-2025  Pedrenrique G. Guimarães

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Check [LICENSE](LICENSE.md) for more information.
