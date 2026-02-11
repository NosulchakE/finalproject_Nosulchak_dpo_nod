# main.py
from valutatrade_hub.logging_config import setup_logging
from valutatrade_hub.cli.interface import run_interactive_cli

def main():
    setup_logging() 
    run_interactive_cli()

if __name__ == "__main__":
    main()











