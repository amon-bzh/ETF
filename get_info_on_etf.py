#!/usr/bin/python3
# Objet: module pour aller chercher des informations sur les ETF

import sys
import os

# Module parser d'arguments
import argparse

# Yahoo Finance
import yfinance as yf

# Yahoo Query
from yahooquery import Ticker

# Colorama pour la gestion des couleurs
from colorama import Fore, Style

# Créer le parser d'argument
parser = argparse.ArgumentParser()
parser.add_argument("ticker", help="get_info_on_etf <ticker>")
parser.add_argument("--raw", action="store_true", help="Afficher le contenu de Ticker.info.")
parser.add_argument("--summary", action="store_true", help="Afficher le business summary.")
parser.add_argument("--financials", action="store_true", help="Afficher les données financières.")
parser.add_argument("--repartition", action="store_true", help="Afficher la répartition par secteurs de l'ETF.")
parser.add_argument("--top-holdings", action="store_true", help="Retrieves Top 10 holdings for a given symbol(s).")
parser.add_argument("--obsidian", action="store_true", help="Créé une fiche dans Obsidian pour l'ETF sélectionné.")
parser.add_argument("--all", action="store_true", help="Afficher toutes les informations disponibles.")
parser.add_argument("--history", action="store_true", help="Afficher l'historique sur 1 mois.")

# Analyser les arguments en ligne de commande
args = parser.parse_args()

# Récupérer le ticker
try:
    ticker_symbol = args.ticker 
    fund = yf.Ticker(ticker_symbol)
    yqfund = Ticker(ticker_symbol)

    # Lire les infos générales - utiliser fast_info comme fallback
    try:
        info = fund.info
    except Exception:
        # Fallback sur fast_info si info échoue
        info = fund.fast_info.__dict__ if hasattr(fund, 'fast_info') else {}
        print(f"{Fore.YELLOW}Attention: utilisation de données limitées (fast_info){Style.RESET_ALL}\n")

except Exception as e:
    print(f"{Fore.RED}Le ticker n'est pas reconnu:{Style.RESET_ALL}")
    print(str(e))
    sys.exit(1)

# Fonction pour lire les données JSON récupérées par ticker.info.
def get_raw_info(info):
    print(f"{Fore.YELLOW}RAW INFO:{Style.RESET_ALL}")
    for key, value in sorted(info.items()):
        print(f"{key}: {value}")
    return

# Fonction qui affiche les données de base de l'ETF
def get_basic_info(info):
    print()
    # Identification avec gestion des clés manquantes
    symbol = info.get('symbol', ticker_symbol)
    shortName = info.get('shortName', 'N/A')
    longName = info.get('longName', shortName)
    name = f"{symbol} / {shortName} / {longName}"
    
    print(f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}{'-' * len(name)}\n{name}\n{'-' * len(name)}{Style.RESET_ALL}")
    print()

    # Lecture sur clef dans les données JSON
    fundFamily = info.get('fundFamily', info.get('family', '<non présent>'))
    print(f"fundFamily : {fundFamily}")

    # Marché
    exchange = info.get('exchange', '<non présent>')
    print(f"exchange : {exchange}")

    quoteType = info.get('quoteType', '<non présent>')
    print(f"quoteType : {quoteType}")

    currency = str(info.get('currency', "<absent>"))
    if currency == 'EUR':
        currency = f"{Fore.GREEN}{currency}{Style.RESET_ALL}"
    else:
        currency = f"{Style.BRIGHT}{Fore.RED}{currency}{Style.RESET_ALL}"
    print(f"currency : {currency}")
    print()

    return

def get_financials(info):
    print(f"{Fore.YELLOW}FINANCIALS:{Style.RESET_ALL}")
    
    # Prix actuel et précédent
    currentPrice = str(info.get('currentPrice', info.get('regularMarketPrice', '<absent>')))
    print(f"currentPrice: {currentPrice}")
    
    previousClose = str(info.get('previousClose', info.get('regularMarketPreviousClose', '<absent>')))
    print(f"previousClose: {previousClose}")
    
    # Range 52 semaines
    fiftyTwoWeekLow = str(info.get('fiftyTwoWeekLow', '<absent>'))
    fiftyTwoWeekHigh = str(info.get('fiftyTwoWeekHigh', '<absent>'))
    print(f"52 Week range: {fiftyTwoWeekLow} - {fiftyTwoWeekHigh}\n")
    
    # Moyennes mobiles
    fiftyDayAverage = str(info.get('fiftyDayAverage', '<absent>'))
    print(f"50 days average: {fiftyDayAverage}")
    
    twoHundredDayAverage = str(info.get('twoHundredDayAverage', '<absent>'))
    print(f"200 days average: {twoHundredDayAverage}\n")
    
    # Volume
    volume = str(info.get('volume', info.get('regularMarketVolume', '<absent>')))
    print(f"Volume: {volume}")
    
    # Total des actifs (pour les ETF)
    totalAssets = info.get('totalAssets', '<absent>')
    if totalAssets != '<absent>':
        print(f"Total Assets: {totalAssets:,.0f}")
    
    # Frais de gestion
    expenseRatio = info.get('annualReportExpenseRatio', info.get('expenseRatio', '<absent>'))
    if expenseRatio != '<absent>' and expenseRatio is not None:
        print(f"Expense Ratio: {expenseRatio:.2%}")
    
    print()
    return

def get_business_summary(info):
    print(f"{Fore.YELLOW}BUSINESS SUMMARY:{Style.RESET_ALL}")
    summary = str(info.get('longBusinessSummary', info.get('description', '<Business summary non présent>')))
    print(summary)
    print()
    return

def get_history(fund):
    print(f"{Fore.YELLOW}HISTORY (1 month):{Style.RESET_ALL}")
    try:
        history = fund.history(period="1mo")
        print(history)
    except Exception as e:
        print(f"{Fore.RED}Erreur lors de la récupération de l'historique: {e}{Style.RESET_ALL}")
    print()
    return

def get_repartition(yqfund):
    print(f"{Fore.YELLOW}REPARTITION ETF:{Style.RESET_ALL}")
    try:
        repartition = yqfund.fund_sector_weightings
        if isinstance(repartition, dict) and ticker_symbol in repartition:
            print(repartition[ticker_symbol])
        else:
            print(repartition)
    except Exception as e:
        print(f"{Fore.RED}Erreur: {e}{Style.RESET_ALL}")
        print("La répartition sectorielle n'est pas disponible pour ce ticker.")
    print()
    return

def get_topHoldings(yqfund):
    print(f"{Fore.YELLOW}TOP HOLDINGS ETF:{Style.RESET_ALL}")
    print(f"{Style.DIM}Retrieves Top 10 holdings for a given symbol(s){Style.RESET_ALL}")
    try:
        holdings = yqfund.fund_top_holdings
        if isinstance(holdings, dict) and ticker_symbol in holdings:
            print(holdings[ticker_symbol])
        else:
            print(holdings)
    except Exception as e:
        print(f"{Fore.RED}Erreur: {e}{Style.RESET_ALL}")
        print("Les holdings ne sont pas disponibles pour ce ticker.")
    print()
    return

def write_to_obsidian(info, yqfund):
    try:
        symbol = info.get('symbol', ticker_symbol)
        symbol_as_tag = symbol.replace('.', '_')
        longName = info.get('longName', info.get('shortName', symbol))
        exchange = info.get('exchange', '<non présent>')
        fundFamily = info.get('fundFamily', info.get('family', '<non présent>'))
        quoteType = info.get('quoteType', '<non présent>')
        currency = info.get('currency', '<non présent>')
        
        # Récupérer repartition et holdings avec gestion d'erreur
        try:
            repartition = yqfund.fund_sector_weightings
            if isinstance(repartition, dict) and ticker_symbol in repartition:
                repartition = repartition[ticker_symbol]
        except Exception:
            repartition = "Non disponible"
        
        try:
            top_holdings = yqfund.fund_top_holdings
            if isinstance(top_holdings, dict) and ticker_symbol in top_holdings:
                top_holdings = top_holdings[ticker_symbol]
        except Exception:
            top_holdings = "Non disponible"
        
        home_directory = os.path.expanduser("~")
        obsidian_directory = home_directory + "/documents/obsidian/invest/"
        directory_name = obsidian_directory + "/4 ETF"
        os.makedirs(directory_name, exist_ok=True)
        filename = f"{directory_name}/{longName}.md"
        
        with open(filename, "w", encoding='utf-8') as file:
            file.write(f"#ETF #{symbol_as_tag}")
            file.write("\n\n")
            file.write(f"# In a nutshell\n\n")
            file.write(f"- symbole: *{symbol}*\n")
            file.write(f"- fund family: *{fundFamily}*\n")
            file.write(f"- quote type: *{quoteType}*\n")
            file.write(f"- exchange: *{exchange}*\n")
            file.write(f"- currency: *{currency}*\n")
            file.write(f"- site web: [A compléter]()\n")
            file.write(f"\n# Répartition\n\n")
            if hasattr(repartition, 'to_string'):
                file.write(repartition.to_string(index=True))
            else:
                file.write(str(repartition))
            file.write("\n\n# Principales positions\n\n")
            if hasattr(top_holdings, 'to_string'):
                file.write(top_holdings.to_string(index=True))
            else:
                file.write(str(top_holdings))
            file.write("\n")
        
        print(f"{Fore.GREEN}Fiche Obsidian créée: {filename}{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}Erreur lors de la création de la fiche Obsidian: {e}{Style.RESET_ALL}")
    
    return

# Programme principal avec traitement des options
if args.raw:
    get_raw_info(info)
elif args.financials:
    get_basic_info(info)
    get_financials(info)
elif args.summary:
    get_basic_info(info)
    get_business_summary(info)
elif args.repartition: 
    get_basic_info(info)
    get_repartition(yqfund)
elif args.top_holdings: 
    get_basic_info(info)
    get_topHoldings(yqfund)
elif args.history:
    get_basic_info(info)
    get_history(fund)
elif args.obsidian:
    write_to_obsidian(info, yqfund)
elif args.all:
    get_basic_info(info)
    get_financials(info)
    get_business_summary(info)
    get_repartition(yqfund)
    get_topHoldings(yqfund)
    get_history(fund)
else:
    get_basic_info(info)
