#!/usr/bin/python3
# etf_obsidian.py - Génération des fiches Obsidian pour les ETF

import os
from datetime import datetime
from colorama import Fore, Style
from etf_utils import detect_indice, get_emetteur_url, get_ratio_emoji, format_date_fr
from etf_markdown import (
    write_header,
    write_general_section,
    write_financial_section,
    write_description_section,
    write_performance_section,
    write_dividends_section,
    write_sector_allocation_section,
    write_holdings_section,
    write_notes_section
)
from etf_data import compute_ytd_return, build_dividend_info, get_sector_weights, get_top_holdings, compute_performance_and_stats

def print_note_dates(created, modified):
    # Align labels so that the ':' are vertically aligned.
    created_text = "Fiche créée le"
    modified_text = "Dernière mise à jour"

    # Compute padding so that both labels have the colon at the same column
    colon_col = len(modified_text)
    pad = max(0, colon_col - len(created_text))

    created_label = (" " * pad) + created_text + ":"
    modified_label = modified_text + ":"

    # Print creation date
    print(f"{Fore.YELLOW}{created_label} {created}{Style.RESET_ALL}")

    # Print modification date, bold if different
    if created != modified:
        print(f"{Fore.YELLOW}{modified_label} {Style.BRIGHT}{modified}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{modified_label} {modified}{Style.RESET_ALL}")

def get_obsidian_paths(longName):
    """
    Construit les chemins Obsidian (dossier + fichier) pour la fiche ETF.
    Crée le dossier cible s'il n'existe pas.
    Returns: (directory_name, filename)
    """
    home_directory = os.path.expanduser("~")
    obsidian_directory = home_directory + "/Library/Mobile Documents/iCloud~md~obsidian/Documents/Invest"
    directory_name = obsidian_directory + "/8 ETF"
    os.makedirs(directory_name, exist_ok=True)
    filename = f"{directory_name}/{longName}.md"
    return directory_name, filename


def confirm_overwrite_if_exists(filename, date_creation):
    """
    Vérifie si un fichier existe déjà et demande confirmation d'écrasement.
    Affiche les dates (création / modif) si trouvées. 
    Returns: (proceed: bool, original_creation_date: str|None)
    """
    if os.path.exists(filename):
        # Lire le contenu pour extraire les dates
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            date_line = None
            mod_line = None
            for line in content.splitlines():
                if "**Fiche créée le" in line:
                    date_line = line.strip()
                if "**Dernière mise à jour" in line:
                    mod_line = line.strip()

        # Afficher le contexte à l'utilisateur
        if date_line and mod_line:
            print(f"{Fore.YELLOW}⚠️ Une fiche existe déjà pour cet ETF.{Style.RESET_ALL}")
            created = date_line.replace("**Fiche créée le :**", "").strip()
            modified = mod_line.replace("**Dernière mise à jour :**", "").strip()
            print_note_dates(created, modified)
        elif date_line:
            print(f"{Fore.YELLOW}⚠️ Une fiche existe déjà pour cet ETF.{Style.RESET_ALL}")
            created = date_line.replace("**Fiche créée le :**", "").strip()
            modified = created
            print_note_dates(created, modified)
        else:
            print(f"{Fore.YELLOW}⚠️ Une fiche existe déjà pour cet ETF, mais la date de création n'a pas été trouvée.{Style.RESET_ALL}")

        reponse = input("Souhaites tu l'écraser ? (o/n) ").strip().lower()
        if reponse != 'o':
            print(f"{Fore.CYAN}Opération annulée. Aucun fichier écrasé.{Style.RESET_ALL}")
            return False, None

        # Extraire la date de création existante si présente
        original_creation_date = None
        for line in content.splitlines():
            if "**Fiche créée le" in line:
                original_creation_date = line.replace("**Fiche créée le :**","").strip()
                break
        if not original_creation_date:
            original_creation_date = date_creation
        return True, original_creation_date

    # Fichier n'existe pas
    return True, date_creation

def write_to_obsidian(fund, yqfund, info, ticker_symbol):
    """
    Crée une fiche Markdown complète dans Obsidian pour un ETF
    
    Args:
        fund: objet yfinance.Ticker
        yqfund: objet yahooquery.Ticker
        info: dictionnaire des informations du ticker
        ticker_symbol: symbole du ticker
    """
    try:
        # Récupération des éléments nécessaires pour créer la fiche Obsidian        
        symbol = info.get('symbol', ticker_symbol)
        shortName = info.get('shortName', 'N/A')
        longName = info.get('longName', info.get('shortName', symbol))
        date_creation = datetime.now().strftime('%d/%m/%Y à %H:%M')
         
        # Création du fichier (chemins) puis confirmation d'écrasement éventuel
        directory_name, filename = get_obsidian_paths(longName)
        proceed, original_creation_date = confirm_overwrite_if_exists(filename, date_creation)
        if not proceed:
            return
                
        # Informations de base
        symbol_as_tag = symbol.replace('.', '_')
        exchange = info.get('exchange', '<non présent>')
        fundFamily = info.get('fundFamily', info.get('family', '<non présent>'))
        quoteType = info.get('quoteType', '<non présent>')
        currency = info.get('currency', '<non présent>')
        
        # Données financières
        currentPrice = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
        previousClose = info.get('previousClose', info.get('regularMarketPreviousClose', 'N/A'))
        fiftyTwoWeekLow = info.get('fiftyTwoWeekLow', 'N/A')
        fiftyTwoWeekHigh = info.get('fiftyTwoWeekHigh', 'N/A')
        fiftyDayAverage = info.get('fiftyDayAverage', 'N/A')
        twoHundredDayAverage = info.get('twoHundredDayAverage', 'N/A')
        volume = info.get('volume', info.get('regularMarketVolume', 'N/A'))
        totalAssets = info.get('totalAssets', 'N/A')
        expenseRatio = info.get('annualReportExpenseRatio', info.get('expenseRatio', None))
        
        # Type d'ETF (distribution/capitalisation)
        dividendYield = info.get('yield', info.get('trailingAnnualDividendYield', None))
        etf_type = "Distribuant" if dividendYield and dividendYield > 0 else "Capitalisant"
        
        # Détection de l'indice répliqué
        category = info.get('category', '')
        indice_replique = detect_indice(longName, category)
        
        # Date de création de l'ETF
        firstTrade = info.get('firstTradeDateEpochUtc', None)
        firstTradeDate = datetime.fromtimestamp(firstTrade).strftime('%d/%m/%Y') if firstTrade else 'N/A'
        
        # ISIN / codes
        isin = info.get('isin', 'N/A')
        
        # URL du site émetteur
        site_web = get_emetteur_url(fundFamily, longName)
        
        # Description
        businessSummary = info.get('longBusinessSummary', info.get('description', 'Non disponible'))
        
        # Répartition et holdings avec multiplication par 100
        repartition_fmt, rep_err = get_sector_weights(yqfund, ticker_symbol)
        if rep_err:
            print(f"{Fore.YELLOW}Attention: Répartition non disponible - {rep_err}{Style.RESET_ALL}")

        top_holdings_fmt, th_err = get_top_holdings(yqfund, ticker_symbol)
        if th_err:
            print(f"{Fore.YELLOW}Attention: Holdings non disponibles - {th_err}{Style.RESET_ALL}")

        # Calcul de rendement sur 1 an (version complète avec statistiques)
        rendement_data, stats_data = compute_performance_and_stats(fund)

        # YTD (rendement depuis le début de l'année)
        ytd_rendement = compute_ytd_return(fund)

        # Dividendes
        dividend_info = build_dividend_info(fund, dividendYield)
        
        with open(filename, "w", encoding='utf-8') as file:
            # En-tête
            write_header(file, symbol_as_tag, original_creation_date, date_creation)
            
            # 1. Généralités
            general_data = {
                "symbol": symbol,
                "longName": longName,
                "shortName": shortName,
                "fundFamily": fundFamily,
                "exchange": exchange,
                "currency": currency,
                "quoteType": quoteType,
                "etf_type": etf_type,
                "indice_replique": indice_replique,
                "isin": isin,
                "firstTradeDate": firstTradeDate,
                "site_web": site_web
            }

            write_general_section(file, general_data)
            
            # 2. Données financières
            financial_data = {
                "currentPrice": currentPrice,
                "previousClose": previousClose,
                "fiftyTwoWeekLow": fiftyTwoWeekLow,
                "fiftyTwoWeekHigh": fiftyTwoWeekHigh,
                "fiftyDayAverage": fiftyDayAverage,
                "twoHundredDayAverage": twoHundredDayAverage,
                "volume": volume,
                "totalAssets": totalAssets,
                "expenseRatio": expenseRatio,
                "currency": currency
            }

            write_financial_section(file, financial_data)
            
            # 3. Description
            write_description_section(file, businessSummary)
                            
            # 4. Performance
            write_performance_section(file, rendement_data, stats_data, ytd_rendement, currency)
            
            # 5. Dividendes
            if dividend_info:
                write_dividends_section(file, dividend_info)
            
            # 6. Répartition sectorielle
            write_sector_allocation_section(file, repartition_fmt)
            
            # 7. Principales positions
            write_holdings_section(file, top_holdings_fmt)
            
            # 8. Notes personnelles
            write_notes_section(file)
        
        print(f"{Fore.WHITE}✓ Fiche Obsidian créée : {Style.RESET_ALL}{Fore.GREEN}{longName}.md{Style.RESET_ALL}")
        print(f"{Fore.WHITE}📁 Emplacement : {Style.RESET_ALL}{Fore.GREEN}{directory_name}{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}✗ Erreur lors de la création de la fiche Obsidian: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
    
    return
