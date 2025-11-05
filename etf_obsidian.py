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
from etf_logging import log_info, log_warning, log_error, log_exception, is_debug_enabled

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
    # Mode test : si le flag existe, on isole l’écriture
    repo_root = os.path.dirname(os.path.abspath(__file__))
    test_flag = os.path.join(repo_root, ".obsidian_test_mode")

    if os.path.exists(test_flag):
        test_dir = os.path.expanduser("~/ObsidianTest/ETF")
        os.makedirs(test_dir, exist_ok=True)
        filename = f"{test_dir}/{longName}.md"
        return test_dir, filename
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
        if is_debug_enabled(): log_info(f"Fiche existante détectée: {filename}")
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
            if is_debug_enabled(): log_info("Écrasement refusé par l'utilisateur")
            print(f"{Fore.CYAN}Opération annulée. Aucun fichier écrasé.{Style.RESET_ALL}")
            return False, None

        # Extraire la date de création existante si présente
        original_creation_date = None
        for line in content.splitlines():
            if "Fiche créée le" in line:
                original_creation_date = (
                    line.replace("**Fiche créée le :**", "")
                        .replace("Fiche créée le :", "")
                        .strip()
                )
                break
        if not original_creation_date:
            original_creation_date = date_creation
        if is_debug_enabled(): log_info("Écrasement confirmé, poursuite du traitement")
        return True, original_creation_date

    # Fichier n'existe pas
    if is_debug_enabled(): log_info("Aucune fiche existante, création nouvelle")
    return True, date_creation

def extract_creation_date(content):
    """
    Extrait la date de création depuis le contenu Markdown existant.
    Retourne None si absente.
    """
    for line in content.splitlines():
        if "Fiche créée le" in line:
            return (
                line.replace("**Fiche créée le :**", "")
                    .replace("Fiche créée le :", "")
                    .strip()
            )
    return None

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
        if is_debug_enabled(): log_info(f"Début génération fiche Obsidian pour {symbol} / {longName}")
         
        # Création du fichier (chemins) puis confirmation d'écrasement éventuel
        directory_name, filename = get_obsidian_paths(longName)
        if is_debug_enabled(): log_info(f"Chemins Obsidian: dir={directory_name}, file={filename}")

        # Préparer les valeurs par défaut issues des données Yahoo avant enrichissement
        category = info.get('category', '')
        indice_replique = detect_indice(longName, category)
        firstTrade = info.get('firstTradeDateEpochUtc', None)
        firstTradeDate = datetime.fromtimestamp(firstTrade).strftime('%d/%m/%Y') if firstTrade else 'N/A'
        isin = info.get('isin', 'N/A')
        
        # --- Gestion mise à jour inline de champs existants ---
        file_exists = os.path.exists(filename)
        user_modified = False

        if file_exists:
            with open(filename, "r", encoding="utf-8") as f:
                old_content = f.read()
            lines = old_content.splitlines()

            fields_to_check = {
                "Indice répliqué": "indice_replique",
                "ISIN": "isin",
                "Date de création ETF": "firstTradeDate"
            }

            original_values = {}
            for label, var_name in fields_to_check.items():
                search = f"- **{label}** :"
                for line in lines:
                    if search in line:
                        current_val = line.split(":", 1)[1].strip()
                        original_values[var_name] = current_val
                        break

            import sys
            edit_mode = ("--edit" in sys.argv)

            def maybe_replace(field_label, var_name, current):
                nonlocal user_modified
                if var_name not in original_values:
                    return current

                prev = original_values[var_name].replace("*", "").strip()

                # Pas de valeur → demande auto
                if prev in ("N/A", "Non renseigné"):
                    print(f"\nChamp détecté : {field_label}")
                    print(f"Valeur actuelle : {prev}")
                    rep = input("Souhaites tu la compléter ? (o/n) ").strip().lower()
                    if rep == "o":
                        new_val = input(f"Nouvelle valeur pour {field_label} : ").strip()
                        if new_val and new_val != prev:
                            user_modified = True
                            return new_val
                    return prev

                # Valeur existante → modifiable seulement en mode --edit
                if not edit_mode:
                    return prev

                print(f"\nChamp détecté : {field_label}")
                print(f"Valeur actuelle : {prev}")
                rep = input("Souhaites tu la remplacer ? (o/n) ").strip().lower()
                if rep == "o":
                    new_val = input(f"Nouvelle valeur pour {field_label} : ").strip()
                    if new_val and new_val != prev:
                        user_modified = True
                        return new_val

                return prev

            # --- Récupérer valeurs actuelles du script avant modification ---
            current_indice = locals().get("indice_replique", "N/A")
            current_isin = locals().get("isin", "N/A")
            current_firstTradeDate = locals().get("firstTradeDate", "N/A")

            # --- Appliquer les remplacements sécurisés ---
            indice_replique = maybe_replace("Indice répliqué", "indice_replique", current_indice)
            isin = maybe_replace("ISIN", "isin", current_isin)
            firstTradeDate = maybe_replace("Date de création ETF", "firstTradeDate", current_firstTradeDate)

        # --- Fin enrichissement inline ---
        
        # Si l'utilisateur a modifié au moins un champ → pas d'alerte "écraser ?"
        if file_exists and user_modified:
            proceed = True
            original_creation_date = extract_creation_date(old_content)
            print("✅ Mise à jour des champs existants, sans écraser toute la fiche.")
        else:
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
        
        # Détection de l'indice / ISIN / date déjà préparées en amont (et potentiellement éditées par l'utilisateur)
        # category, indice_replique, firstTradeDate, isin : conservés
        
        # URL du site émetteur
        site_web = get_emetteur_url(fundFamily, longName)
        
        # Description
        businessSummary = info.get('longBusinessSummary', info.get('description', 'Non disponible'))
        
        # Répartition sectorielle
        try:
            repartition_fmt, rep_err = get_sector_weights(yqfund, ticker_symbol)
            if rep_err:
                print(f"{Fore.YELLOW}Attention: Répartition non disponible - {rep_err}{Style.RESET_ALL}")
                if is_debug_enabled(): log_warning(f"Répartition non disponible - {rep_err}")
        except Exception as e:
            print(f"{Fore.RED}Erreur lors de la récupération de la répartition sectorielle: {e}{Style.RESET_ALL}")
            if is_debug_enabled(): log_error(f"Erreur répartition sectorielle: {e}")
            repartition_fmt = "Non disponible"

        # Principales positions
        try:
            top_holdings_fmt, th_err = get_top_holdings(yqfund, ticker_symbol)
            if th_err:
                print(f"{Fore.YELLOW}Attention: Holdings non disponibles - {th_err}{Style.RESET_ALL}")
                if is_debug_enabled(): log_warning(f"Holdings non disponibles - {th_err}")
        except Exception as e:
            print(f"{Fore.RED}Erreur lors de la récupération des principales positions: {e}{Style.RESET_ALL}")
            if is_debug_enabled(): log_error(f"Erreur principales positions: {e}")
            top_holdings_fmt = "Non disponible"

        # Calcul de rendement sur 1 an (version complète avec statistiques)
        try:
            rendement_data, stats_data = compute_performance_and_stats(fund)
        except Exception as e:
            print(f"{Fore.RED}Erreur lors du calcul des performances: {e}{Style.RESET_ALL}")
            if is_debug_enabled(): log_error(f"Erreur calcul performances: {e}")
            rendement_data, stats_data = {}, {}

        # YTD (rendement depuis le début de l'année)
        try:
            ytd_rendement = compute_ytd_return(fund)
        except Exception as e:
            print(f"{Fore.RED}Erreur lors du calcul YTD: {e}{Style.RESET_ALL}")
            if is_debug_enabled(): log_error(f"Erreur calcul YTD: {e}")
            ytd_rendement = None

        # Dividendes
        try:
            dividend_info = build_dividend_info(fund, dividendYield)
        except Exception as e:
            print(f"{Fore.RED}Erreur lors de la récupération des dividendes: {e}{Style.RESET_ALL}")
            if is_debug_enabled(): log_error(f"Erreur récupération dividendes: {e}")
            dividend_info = {}
        
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
        if is_debug_enabled(): log_info(f"Fiche créée: {filename}")
    
    except Exception as e:
        print(f"{Fore.RED}✗ Erreur lors de la création de la fiche Obsidian: {e}{Style.RESET_ALL}")
        if is_debug_enabled(): log_exception("Erreur lors de la création de la fiche Obsidian")
        import traceback
        traceback.print_exc()
    
    return
