#!/usr/bin/python3
# etf_core.py - Fonctions de récupération et affichage des données ETF

import sys
import yfinance as yf
from yahooquery import Ticker
from colorama import Fore, Style

def get_ticker_data(ticker_symbol):
    """
    Récupère les données d'un ticker depuis Yahoo Finance
    
    Args:
        ticker_symbol: Symbole du ticker (ex: VWCE.DE)
    
    Returns:
        tuple: (fund, yqfund, info) ou None si erreur
    """
    try:
        fund = yf.Ticker(ticker_symbol)
        yqfund = Ticker(ticker_symbol)

        # Lire les infos générales - utiliser fast_info comme fallback
        try:
            info = fund.info
        except Exception:
            # Fallback sur fast_info si info échoue
            info = fund.fast_info.__dict__ if hasattr(fund, 'fast_info') else {}
            print(f"{Fore.YELLOW}Attention: utilisation de données limitées (fast_info){Style.RESET_ALL}\n")
        
        return fund, yqfund, info

    except Exception as e:
        print(f"{Fore.RED}Le ticker n'est pas reconnu:{Style.RESET_ALL}")
        print(str(e))
        return None

def get_raw_info(info):
    """Affiche toutes les données brutes du ticker"""
    print(f"{Fore.YELLOW}RAW INFO:{Style.RESET_ALL}")
    for key, value in sorted(info.items()):
        print(f"{key}: {value}")
    return

def get_basic_info(info, ticker_symbol):
    """
    Affiche les informations de base de l'ETF
    
    Args:
        info: Dictionnaire des informations du ticker
        ticker_symbol: Symbole du ticker
    """
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
    """Affiche les données financières de l'ETF"""
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
    """Affiche le résumé business de l'ETF"""
    print(f"{Fore.YELLOW}BUSINESS SUMMARY:{Style.RESET_ALL}")
    summary = str(info.get('longBusinessSummary', info.get('description', '<Business summary non présent>')))
    print(summary)
    print()
    return

def get_history(fund):
    """Affiche l'historique sur 1 mois"""
    print(f"{Fore.YELLOW}HISTORY (1 month):{Style.RESET_ALL}")
    try:
        history = fund.history(period="1mo")
        print(history)
    except Exception as e:
        print(f"{Fore.RED}Erreur lors de la récupération de l'historique: {e}{Style.RESET_ALL}")
    print()
    return

def get_repartition(yqfund, ticker_symbol):
    """Affiche la répartition sectorielle de l'ETF"""
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

def get_top_holdings(yqfund, ticker_symbol):
    """Affiche les principales positions de l'ETF"""
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
