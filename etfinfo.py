#!/usr/bin/python3
# etfinfo.py - Script principal pour l'analyse des ETF

import sys
import argparse
from colorama import Fore, Style

# Imports des modules locaux
from etf_core import (
    get_ticker_data,
    get_raw_info,
    get_basic_info,
    get_financials,
    get_business_summary,
    get_history,
    get_repartition,
    get_top_holdings
)
from etf_analysis import calculate_rendement
from etf_obsidian import write_to_obsidian
from etf_utils import search_ticker_variants, display_ticker_choices
from etf_logging import setup_logging, log_info, log_warning, log_debug, log_error

# Créer le parser d'argument
parser = argparse.ArgumentParser(
    prog='etfinfo',
    description='Outil d\'analyse et d\'information sur les ETF'
)
parser.add_argument("ticker", help="Ticker de l'ETF (ex: VWCE.DE)")
parser.add_argument("--raw", action="store_true", help="Afficher le contenu de Ticker.info.")
parser.add_argument("--summary", action="store_true", help="Afficher le business summary.")
parser.add_argument("--financials", action="store_true", help="Afficher les données financières.")
parser.add_argument("--repartition", action="store_true", help="Afficher la répartition par secteurs de l'ETF.")
parser.add_argument("--top-holdings", action="store_true", help="Retrieves Top 10 holdings for a given symbol(s).")
parser.add_argument("--obsidian", action="store_true", help="Créé une fiche dans Obsidian pour l'ETF sélectionné.")
parser.add_argument("--all", action="store_true", help="Afficher toutes les informations disponibles.")
parser.add_argument("--history", action="store_true", help="Afficher l'historique sur 1 mois.")
parser.add_argument("--rendement", action="store_true", help="Calculer le rendement sur une période.")
parser.add_argument("--period", type=str, default="1y", 
                    help="Période pour le calcul de rendement (1mo, 3mo, 6mo, 1y, 2y, 5y, max) ou dates YYYY-MM-DD:YYYY-MM-DD")
parser.add_argument("--no-dividends", action="store_true", help="Exclure les dividendes du calcul de rendement.")
parser.add_argument("--benchmark", type=str, help="Comparer avec un benchmark (ex: ^GSPC pour S&P500)")
parser.add_argument("--debug", action="store_true", help="Activer le mode debug avec logs dans fichier")

# Analyser les arguments en ligne de commande
args = parser.parse_args()
setup_logging(debug=args.debug)
log_debug(f"Arguments: {args}")
log_info(f"Démarrage etfinfo avec ticker: {args.ticker}")
log_info(f"Lancement de etfinfo.py avec arguments : {sys.argv}")

# Récupérer le ticker
ticker_symbol = args.ticker
log_info(f"Tentative de récupération des données pour le ticker : {ticker_symbol}")
result = get_ticker_data(ticker_symbol)

# Si le ticker n'est pas trouvé, proposer une recherche interactive
if result is None:
    log_info(f"Ticker {ticker_symbol} introuvable — proposition de recherche de variantes.")
    print(f"\n{Fore.YELLOW}Le ticker '{ticker_symbol}' n'a pas été trouvé.{Style.RESET_ALL}")
    print(f"Souhaitez-vous rechercher des variantes ? (o/n)")
    
    try:
        response = input().lower()
        if response == 'o' or response == 'y':
            # Rechercher les variantes
            log_debug(f"Recherche de variantes pour le ticker : {ticker_symbol}")
            variants = search_ticker_variants(ticker_symbol)
            
            if variants:
                # Proposer le choix
                selected_ticker = display_ticker_choices(variants)
                log_info(f"Utilisateur a sélectionné le ticker alternatif : {selected_ticker}")
                
                if selected_ticker:
                    # Réessayer avec le ticker sélectionné
                    ticker_symbol = selected_ticker
                    result = get_ticker_data(ticker_symbol)
                    
                    if result is None:
                        log_error(f"Erreur lors du chargement du ticker sélectionné : {selected_ticker}")
                        print(f"{Fore.RED}Erreur lors du chargement du ticker sélectionné.{Style.RESET_ALL}")
                        sys.exit(1)
                else:
                    sys.exit(0)
            else:
                log_info(f"Aucune variante trouvée pour {ticker_symbol}")
                print(f"{Fore.RED}Aucune variante trouvée pour '{ticker_symbol}'.{Style.RESET_ALL}")
                sys.exit(1)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nAnnulation.")
        sys.exit(0)
else:
    # Le ticker existe, on continue normalement
    pass

# Si on arrive ici sans result valide, on quitte
if result is None:
    sys.exit(1)

fund, yqfund, info = result

# Programme principal avec traitement des options
log_info(f"Traitement des options pour le ticker : {ticker_symbol}")
if args.raw:
    get_raw_info(info)
elif args.financials:
    get_basic_info(info, ticker_symbol)
    get_financials(info)
elif args.summary:
    get_basic_info(info, ticker_symbol)
    get_business_summary(info)
elif args.repartition: 
    get_basic_info(info, ticker_symbol)
    get_repartition(yqfund, ticker_symbol)
elif args.top_holdings: 
    get_basic_info(info, ticker_symbol)
    get_top_holdings(yqfund, ticker_symbol)
elif args.history:
    get_basic_info(info, ticker_symbol)
    get_history(fund)
elif args.rendement:
    get_basic_info(info, ticker_symbol)
    calculate_rendement(fund, 
                       period=args.period, 
                       include_dividends=not args.no_dividends,
                       benchmark_ticker=args.benchmark)
elif args.obsidian:
    write_to_obsidian(fund, yqfund, info, ticker_symbol)
elif args.all:
    get_basic_info(info, ticker_symbol)
    get_financials(info)
    get_business_summary(info)
    get_repartition(yqfund, ticker_symbol)
    get_top_holdings(yqfund, ticker_symbol)
    get_history(fund)
else:
    log_info("Aucune option spécifique fournie, affichage des informations de base")
    get_basic_info(info, ticker_symbol)
    
log_info(f"Exécution terminée pour {ticker_symbol}")
