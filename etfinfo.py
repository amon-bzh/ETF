#!/usr/bin/python3
# etfinfo.py - Script principal pour l'analyse des ETF

import sys
import argparse
from colorama import Fore, Style
import re

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

ticker_with_suffix = re.compile(r"^[A-Z0-9]{3,5}\.[A-Z]{1,2}$")

def resolve_ticker(ticker_symbol):
    is_complete = bool(ticker_with_suffix.match(ticker_symbol))

    # Ticker potentiellement incomplet (>=4 chars mais pas de suffixe)
    if not is_complete and len(ticker_symbol) >= 4:
        log_warning(f"Ticker '{ticker_symbol}' semble incomplet (manque suffixe).")
        print(f"\n{Fore.YELLOW}Le ticker '{ticker_symbol}' semble incomplet.{Style.RESET_ALL}")
        print("Souhaites-tu rechercher sur quelles places il est coté ? (o/n)")

        try:
            response = input().lower()
            if response not in ('o', 'y'):
                log_info("Recherche de variantes refusée")
                return None

            variants = search_ticker_variants(ticker_symbol)
            if not variants:
                log_warning(f"Aucune variante trouvée pour {ticker_symbol}")
                print(f"{Fore.RED}Aucune variante trouvée pour '{ticker_symbol}'.{Style.RESET_ALL}")
                return None

            selected = display_ticker_choices(variants)
            if not selected:
                log_info("Utilisateur a annulé la sélection")
                return None

            return selected

        except KeyboardInterrupt:
            log_info("Interruption utilisateur")
            print("\nAnnulation.")
            return None

    # Ticker mal formaté
    elif not is_complete:
        log_error(f"Ticker '{ticker_symbol}' mal formaté.")
        print(f"\n{Fore.RED}Le ticker '{ticker_symbol}' n'est pas au bon format.{Style.RESET_ALL}")
        print("Format attendu: XXXX.YY (ex: VWCE.DE)")
        return None

    # Ticker déjà complet
    return ticker_symbol

def main():
    """
    Point d'entrée principal.
    Étapes suivantes: déplacer progressivement la logique ici et
    remplacer les sys.exit() internes par des return codes.
    """
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
    
    # Résolution du ticker
    ticker_symbol = args.ticker
    resolved = resolve_ticker(ticker_symbol)
    if resolved is None:
        return None, None  # temporaire: signale un arrêt propre
    ticker_symbol = resolved
    
    log_info(f"Tentative de récupération des données pour {ticker_symbol}")
    result = get_ticker_data(ticker_symbol)

    if result is None:
        print(f"{Fore.RED}Impossible de récupérer '{ticker_symbol}'.{Style.RESET_ALL}")
        log_error(f"Impossible de récupérer les données pour {ticker_symbol}")
        return args, ticker_symbol, None, None, None

    fund, yqfund, info = result
    log_info(f"Données récupérées pour {ticker_symbol}")
    
    return args, ticker_symbol, fund, yqfund, info
    
args, ticker_symbol, fund, yqfund, info = main()

if args is None:
    sys.exit(1)

# Récupérer le ticker
ticker_symbol = args.ticker

# Vérifier le format du ticker
# Format avec suffixe: 4-5 lettres + point + 1-2 lettres (ex: VWCE.DE, IWDA.AS)
ticker_with_suffix = re.compile(r"^[A-Z0-9]{3,5}\.[A-Z]{1,2}$")

result = None

# Déterminer si le ticker semble complet
is_complete_ticker = ticker_with_suffix.match(ticker_symbol)

# Si le ticker semble incomplet (4+ lettres sans suffixe)
if not is_complete_ticker and len(ticker_symbol) >= 4:
    log_warning(f"Ticker '{ticker_symbol}' semble incomplet (manque le suffixe de place).")
    print(f"\n{Fore.YELLOW}Le ticker '{ticker_symbol}' semble incomplet.{Style.RESET_ALL}")
    print("Souhaitez-vous rechercher sur quelles places il est coté ? (o/n)")
    
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
                    log_info("Utilisateur a annulé la sélection")
                    sys.exit(0)
            else:
                log_warning(f"Aucune variante trouvée pour {ticker_symbol}")
                print(f"{Fore.RED}Aucune variante trouvée pour '{ticker_symbol}'.{Style.RESET_ALL}")
                sys.exit(1)
        else:
            log_info("Utilisateur a refusé la recherche de variantes")
            sys.exit(1)
    except KeyboardInterrupt:
        log_info("Interruption utilisateur (Ctrl+C)")
        print("\n\nAnnulation.")
        sys.exit(0)
elif not is_complete_ticker:
    # Ticker mal formaté (trop court ou caractères invalides)
    log_error(f"Ticker '{ticker_symbol}' mal formaté.")
    print(f"\n{Fore.RED}Le ticker '{ticker_symbol}' n'est pas au bon format.{Style.RESET_ALL}")
    print("Format attendu: XXXX.YY (ex: VWCE.DE)")
    sys.exit(1)
else:
    # Le ticker semble bien formaté, tenter de récupérer les données
    log_info(f"Tentative de récupération des données pour le ticker : {ticker_symbol}")
    result = get_ticker_data(ticker_symbol)
    
    # Si le ticker est bien formaté mais n'existe pas
    if result is None:
        log_warning(f"Ticker bien formaté mais introuvable: {ticker_symbol}")
        print(f"\n{Fore.YELLOW}Le ticker '{ticker_symbol}' n'a pas été trouvé.{Style.RESET_ALL}")
        print("Souhaitez-vous rechercher des variantes ? (o/n)")
        
        try:
            response = input().lower()
            if response == 'o' or response == 'y':
                log_debug(f"Recherche de variantes pour le ticker : {ticker_symbol}")
                variants = search_ticker_variants(ticker_symbol)
                
                if variants:
                    selected_ticker = display_ticker_choices(variants)
                    log_info(f"Utilisateur a sélectionné le ticker alternatif : {selected_ticker}")
                    
                    if selected_ticker:
                        ticker_symbol = selected_ticker
                        result = get_ticker_data(ticker_symbol)
                        
                        if result is None:
                            log_error(f"Erreur lors du chargement du ticker sélectionné : {selected_ticker}")
                            print(f"{Fore.RED}Erreur lors du chargement du ticker sélectionné.{Style.RESET_ALL}")
                            sys.exit(1)
                    else:
                        log_info("Utilisateur a annulé la sélection")
                        sys.exit(0)
                else:
                    log_warning(f"Aucune variante trouvée pour {ticker_symbol}")
                    print(f"{Fore.RED}Aucune variante trouvée pour '{ticker_symbol}'.{Style.RESET_ALL}")
                    sys.exit(1)
            else:
                log_info("Utilisateur a refusé la recherche de variantes")
                sys.exit(1)
        except KeyboardInterrupt:
            log_info("Interruption utilisateur (Ctrl+C)")
            print("\n\nAnnulation.")
            sys.exit(0)

# Si on arrive ici sans result valide, on quitte
if result is None:
    log_error("Aucun résultat valide après toutes les tentatives")
    sys.exit(1)

fund, yqfund, info = result
log_info(f"Données récupérées avec succès pour {ticker_symbol}")

# Programme principal avec traitement des options
log_debug(f"Traitement des options pour le ticker : {ticker_symbol}")

if args.raw:
    log_info("Option: --raw (affichage données brutes)")
    get_raw_info(info)
elif args.financials:
    log_info("Option: --financials")
    get_basic_info(info, ticker_symbol)
    get_financials(info)
elif args.summary:
    log_info("Option: --summary")
    get_basic_info(info, ticker_symbol)
    get_business_summary(info)
elif args.repartition:
    log_info("Option: --repartition")
    get_basic_info(info, ticker_symbol)
    get_repartition(yqfund, ticker_symbol)
elif args.top_holdings:
    log_info("Option: --top-holdings")
    get_basic_info(info, ticker_symbol)
    get_top_holdings(yqfund, ticker_symbol)
elif args.history:
    log_info("Option: --history")
    get_basic_info(info, ticker_symbol)
    get_history(fund)
elif args.rendement:
    log_info(f"Option: --rendement (période: {args.period}, dividendes: {not args.no_dividends})")
    if args.benchmark:
        log_debug(f"Benchmark spécifié: {args.benchmark}")
    get_basic_info(info, ticker_symbol)
    calculate_rendement(fund, 
                       period=args.period, 
                       include_dividends=not args.no_dividends,
                       benchmark_ticker=args.benchmark)
elif args.obsidian:
    log_info("Option: --obsidian")
    write_to_obsidian(fund, yqfund, info, ticker_symbol)
elif args.all:
    log_info("Option: --all")
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

# TODO: activer quand la migration vers main() sera finie
# if __name__ == "__main__":
#     sys.exit(main())