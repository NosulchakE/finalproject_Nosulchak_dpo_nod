# main.py
from valutatrade_hub.cli.interface import run_interactive_cli


def print_banner():
    print("CLI для управления валютным портфелем.\n")

def main():
    print_banner()
    run_interactive_cli()

if __name__ == "__main__":
    main()










