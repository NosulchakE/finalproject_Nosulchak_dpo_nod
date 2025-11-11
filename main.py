# main.py
"""
Главная точка входа проекта ValutaTrade.
Запускает CLI-интерфейс (valutatrade_hub/cli/interface.py)
"""

from valutatrade_hub.cli.interface import run_cli


def main():
    """Точка входа для poetry script (см. [tool.poetry.scripts])"""
    run_cli()


if __name__ == "__main__":
    main()


