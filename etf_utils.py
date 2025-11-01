#!/usr/bin/python3
# etf_utils.py - Fonctions utilitaires pour etfinfo

from datetime import datetime
import yfinance as yf
from etf_logging import log_debug, log_info

def format_date_fr(date):
    """Formate une date au format français dd/mm/yyyy"""
    if isinstance(date, str):
        return date
    return date.strftime('%d/%m/%Y')

def format_number_fr(number, decimals=2):
    """Formate un nombre avec conventions françaises (virgule, espaces)"""
    if number == 'N/A' or number is None:
        return 'N/A'
    
    formatted = f"{number:,.{decimals}f}"
    # Remplacer séparateur de milliers par espace
    formatted = formatted.replace(',', ' ')
    # Remplacer point décimal par virgule
    formatted = formatted.replace('.', ',')
    return formatted

def format_percentage_fr(value, decimals=2):
    """Formate un pourcentage avec conventions françaises"""
    if value == 'N/A' or value is None:
        return 'N/A'
    
    formatted = f"{value:.{decimals}f}%"
    formatted = formatted.replace('.', ',')
    return formatted

def detect_indice(long_name, category=''):
    """
    Détecte l'indice répliqué par l'ETF depuis son nom ou sa catégorie
    
    Args:
        long_name: Nom complet de l'ETF
        category: Catégorie de l'ETF (optionnel)
    
    Returns:
        str: Nom de l'indice répliqué ou "Non identifié"
    """
    long_name_lower = long_name.lower()
    category_lower = category.lower() if category else ''
    
    # Patterns de détection d'indices
    indices = {
        'MSCI World': ['msci world'],
        'FTSE All-World / MSCI ACWI': ['msci acwi', 'all-world', 'ftse all-world'],
        'S&P 500': ['s&p 500', 'sp500', 'sp 500'],
        'EURO STOXX 50': ['stoxx 50', 'euro stoxx 50'],
        'STOXX Europe 600': ['stoxx 600', 'europe 600'],
        'NASDAQ': ['nasdaq'],
        'FTSE 100': ['ftse 100'],
        'DAX': ['dax'],
        'CAC 40': ['cac 40'],
        'MSCI Emerging Markets': ['emerging', 'emergent'],
        'FTSE Developed Europe': ['developed europe'],
        'MSCI USA': ['msci usa'],
        'MSCI Europe': ['msci europe'],
        'Russell 2000': ['russell 2000'],
        'MSCI Japan': ['msci japan'],
        'MSCI China': ['msci china'],
        'FTSE Developed Asia Pacific': ['developed asia pacific'],
    }
    
    for indice_name, patterns in indices.items():
        for pattern in patterns:
            if pattern in long_name_lower or pattern in category_lower:
                return indice_name
    
    return "Non identifié"

def get_emetteur_url(fund_family, long_name):
    """
    Génère l'URL du site de l'émetteur de l'ETF
    
    Args:
        fund_family: Famille de fonds (ex: Vanguard, BlackRock)
        long_name: Nom complet de l'ETF
    
    Returns:
        str: URL formatée en Markdown ou message à compléter
    """
    if not fund_family or fund_family == '<non présent>':
        return "[A compléter - émetteur non reconnu]()"
    
    fund_family_lower = fund_family.lower()
    
    # Mapping des émetteurs vers leurs URLs
    if 'blackrock' in fund_family_lower or 'ishares' in fund_family_lower:
        # Encoder le nom pour l'URL BlackRock
        etf_name_encoded = long_name.replace(' ', '%20')
        return f"[BlackRock iShares](https://www.blackrock.com/fr/particuliers/products/investment-funds#/?productView=all&search={etf_name_encoded})"
    
    elif 'vanguard' in fund_family_lower:
        return "[Vanguard](https://investor.vanguard.com)"
    
    elif 'amundi' in fund_family_lower:
        return "[Amundi ETF](https://www.amundietf.fr/fr/particuliers)"
    
    elif 'lyxor' in fund_family_lower:
        return "[Lyxor / Amundi](https://www.amundietf.fr/fr/particuliers)"
    
    elif 'spdr' in fund_family_lower or 'state street' in fund_family_lower:
        return "[SPDR / State Street](https://www.ssga.com/fr/en_gb/institutional/etfs)"
    
    elif 'xtrackers' in fund_family_lower or 'dws' in fund_family_lower:
        return "[Xtrackers / DWS](https://etf.dws.com)"
    
    elif 'wisdomtree' in fund_family_lower:
        return "[WisdomTree](https://www.wisdomtree.eu)"
    
    elif 'invesco' in fund_family_lower:
        return "[Invesco](https://www.invesco.com/us/financial-products/etfs)"
    
    elif 'hsbc' in fund_family_lower:
        return "[HSBC ETF](https://www.assetmanagement.hsbc.com/etf)"
    
    elif 'ubs' in fund_family_lower:
        return "[UBS ETF](https://www.ubs.com/etf)"
    
    else:
        return f"[A compléter - {fund_family}]()"

def get_ratio_emoji(ratio_value, ratio_type='sharpe'):
    """
    Retourne un emoji et une alerte selon la valeur du ratio
    
    Args:
        ratio_value: Valeur du ratio
        ratio_type: Type de ratio ('sharpe' ou 'sortino')
    
    Returns:
        tuple: (emoji, alerte_text ou None)
    """
    if ratio_type == 'sharpe':
        if ratio_value < 0:
            return '🔴', None
        elif ratio_value < 1:
            return '🟡', None
        elif ratio_value < 2:
            return '🟢', None
        elif ratio_value < 3:
            return '🟢⭐', None
        else:
            return '🔴⚠️', 'Risque de bulle'
    
    elif ratio_type == 'sortino':
        if ratio_value < 0:
            return '🔴', None
        elif ratio_value < 1:
            return '🟡', None
        elif ratio_value < 2:
            return '🟢', None
        else:
            return '🟢⭐', None
    
    return '', None

def search_ticker_variants(base_ticker):
    """
    Recherche les variantes d'un ticker sur différentes places boursières
    
    Args:
        base_ticker: Ticker de base sans suffixe (ex: VWCE)
    
    Returns:
        list: Liste de tuples (ticker_complet, nom, exchange, devise) ou None si aucun
    """
    import os
    from contextlib import redirect_stderr
    
    # Suffixes des principales places boursières européennes et US
    suffixes = {
        '.DE': 'XETRA (Allemagne)',
        '.F': 'Frankfurt (Allemagne)', 
        '.L': 'London Stock Exchange (UK)',
        '.AS': 'Euronext Amsterdam (Pays-Bas)',
        '.PA': 'Euronext Paris (France)',
        '.MI': 'Borsa Italiana (Italie)',
        '.SW': 'SIX Swiss Exchange (Suisse)',
        '': 'US Markets (NYSE/NASDAQ)'
    }
    
    results = []
    
    print(f"🔍 Recherche de variantes pour '{base_ticker}'...\n")
    
    for suffix, exchange_name in suffixes.items():
        ticker = base_ticker + suffix if suffix else base_ticker
        
        try:
            # Supprimer les messages d'erreur HTTP
            with open(os.devnull, 'w') as devnull:
                with redirect_stderr(devnull):
                    fund = yf.Ticker(ticker)
                    info = fund.info
            
            # Vérifier si le ticker existe vraiment
            if info and 'symbol' in info and info.get('regularMarketPrice'):
                name = info.get('shortName', info.get('longName', 'N/A'))
                exchange = info.get('exchange', 'N/A')
                currency = info.get('currency', 'N/A')
                price = info.get('regularMarketPrice', 'N/A')
                
                results.append({
                    'ticker': ticker,
                    'name': name,
                    'exchange': exchange,
                    'exchange_name': exchange_name,
                    'currency': currency,
                    'price': price
                })
        except Exception:
            # Le ticker n'existe pas sur cette place, on continue silencieusement
            pass
    
    return results if results else None

def display_ticker_choices(results):
    """
    Affiche les choix de tickers trouvés et demande à l'utilisateur de choisir
    
    Args:
        results: Liste des résultats de search_ticker_variants
    
    Returns:
        str: Ticker choisi ou None si annulation
    """
    from colorama import Fore, Style
    
    if not results:
        return None
    
    print(f"{Fore.GREEN}✓ {len(results)} variante(s) trouvée(s):{Style.RESET_ALL}\n")
    
    # Afficher les options
    for i, result in enumerate(results, 1):
        price_str = f"{result['price']:.2f}" if isinstance(result['price'], (int, float)) else str(result['price'])
        
        print(f"{Fore.CYAN}[{i}]{Style.RESET_ALL} {Style.BRIGHT}{result['ticker']}{Style.RESET_ALL}")
        print(f"    Nom       : {result['name']}")
        print(f"    Place     : {result['exchange_name']}")
        print(f"    Exchange  : {result['exchange']}")
        print(f"    Devise    : {result['currency']}")
        print(f"    Prix      : {price_str} {result['currency']}")
        print()
    
    # Demander le choix
    while True:
        try:
            choice = input(f"{Fore.YELLOW}Choisissez un ticker [1-{len(results)}] ou 'q' pour annuler: {Style.RESET_ALL}")
            
            if choice.lower() == 'q':
                print("Annulation.")
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(results):
                selected = results[choice_num - 1]['ticker']
                print(f"\n{Fore.GREEN}✓ Ticker sélectionné: {selected}{Style.RESET_ALL}\n")
                return selected
            else:
                print(f"{Fore.RED}Choix invalide. Entrez un nombre entre 1 et {len(results)}.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Choix invalide. Entrez un nombre ou 'q'.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print("\n\nAnnulation.")
            return None
