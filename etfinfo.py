#!/usr/bin/python3
# Objet: module pour aller chercher des informations sur les ETF
# Nom: etfinfo.py

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

# Pour les calculs de rendement
from datetime import datetime, timedelta
import numpy as np

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

def calculate_rendement(fund, period="1y", include_dividends=True, benchmark_ticker=None):
    """
    Calcule le rendement d'un ETF sur une période donnée
    
    Args:
        fund: objet yfinance.Ticker
        period: période (1mo, 3mo, 6mo, 1y, 2y, 5y, max) ou YYYY-MM-DD:YYYY-MM-DD
        include_dividends: inclure les dividendes dans le calcul
        benchmark_ticker: ticker du benchmark pour comparaison (optionnel)
    """
    
    print(f"\n{Style.BRIGHT}{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.CYAN}ANALYSE DE RENDEMENT{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")
    
    try:
        # Déterminer si c'est une période prédéfinie ou des dates personnalisées
        if ':' in period:
            # Dates personnalisées
            start_date, end_date = period.split(':')
            hist = fund.history(start=start_date, end=end_date)
            period_label = f"{start_date} → {end_date}"
        else:
            # Période prédéfinie
            hist = fund.history(period=period)
            period_label = period
        
        if hist.empty or len(hist) < 2:
            print(f"{Fore.RED}Pas assez de données pour la période demandée{Style.RESET_ALL}")
            return
        
        # Dates réelles
        date_debut = hist.index[0]
        date_fin = hist.index[-1]
        nb_jours = len(hist)
        
        # Prix
        prix_debut = hist['Close'].iloc[0]
        prix_fin = hist['Close'].iloc[-1]
        
        print(f"{Fore.YELLOW}PÉRIODE ANALYSÉE:{Style.RESET_ALL}")
        print(f"  Période demandée : {period_label}")
        print(f"  Date début       : {date_debut.strftime('%d/%m/%Y')}")
        print(f"  Date fin         : {date_fin.strftime('%d/%m/%Y')}")
        print(f"  Nombre de jours  : {nb_jours}")
        print(f"  Prix début       : {prix_debut:.2f}")
        print(f"  Prix fin         : {prix_fin:.2f}")
        
        # Calcul du nombre d'années pour annualisation
        nb_annees = (date_fin - date_debut).days / 365.25
        
        # Dividendes
        total_dividends = 0
        nb_dividends = 0
        if include_dividends:
            dividends = fund.dividends[date_debut:date_fin]
            if not dividends.empty:
                total_dividends = dividends.sum()
                nb_dividends = len(dividends)
                print(f"  Dividendes       : {total_dividends:.2f} ({nb_dividends} distributions)")
        
        print()
        
        # === RENDEMENTS ===
        print(f"{Fore.YELLOW}RENDEMENTS:{Style.RESET_ALL}")
        
        # Rendement simple (sans dividendes)
        rendement_simple = ((prix_fin - prix_debut) / prix_debut) * 100
        print(f"  Rendement prix   : {rendement_simple:+.2f}%")
        
        # Rendement total (avec dividendes)
        if include_dividends and total_dividends > 0:
            rendement_total = ((prix_fin + total_dividends - prix_debut) / prix_debut) * 100
            print(f"  Rendement total  : {Fore.GREEN}{rendement_total:+.2f}%{Style.RESET_ALL}")
            print(f"  Apport dividendes: {rendement_total - rendement_simple:+.2f}%")
        else:
            rendement_total = rendement_simple
            print(f"  Rendement total  : {Fore.GREEN}{rendement_total:+.2f}%{Style.RESET_ALL}")
        
        # Rendement annualisé (si période > 1 an)
        if nb_annees >= 1:
            rendement_annualise = (((prix_fin + total_dividends) / prix_debut) ** (1/nb_annees) - 1) * 100
            print(f"  Rendement annualisé: {rendement_annualise:+.2f}%")
        
        print()
        
        # === VOLATILITÉ ===
        print(f"{Fore.YELLOW}RISQUE:{Style.RESET_ALL}")
        
        # Calcul des rendements quotidiens
        returns = hist['Close'].pct_change().dropna()
        
        # Volatilité (écart-type des rendements quotidiens, annualisé)
        volatilite_quotidienne = returns.std()
        volatilite_annuelle = volatilite_quotidienne * np.sqrt(252) * 100  # 252 jours de trading
        print(f"  Volatilité annuelle: {volatilite_annuelle:.2f}%")
        
        # Drawdown maximum
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        print(f"  Drawdown maximum   : {max_drawdown:.2f}%")
        
        # Date du drawdown maximum
        max_dd_date = drawdown.idxmin()
        print(f"  Date du max DD     : {max_dd_date.strftime('%d/%m/%Y')}")
        
        print()
        
        # === RATIOS ===
        print(f"{Fore.YELLOW}RATIOS:{Style.RESET_ALL}")
        
        # Ratio de Sharpe (simplifié, taux sans risque = 0)
        if volatilite_annuelle > 0:
            if nb_annees >= 1:
                sharpe_ratio = rendement_annualise / volatilite_annuelle
            else:
                sharpe_ratio = rendement_total / volatilite_annuelle
            print(f"  Ratio de Sharpe    : {sharpe_ratio:.2f}")
        
        # Ratio de Sortino (volatilité des rendements négatifs uniquement)
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0:
            downside_vol = negative_returns.std() * np.sqrt(252) * 100
            if downside_vol > 0:
                if nb_annees >= 1:
                    sortino_ratio = rendement_annualise / downside_vol
                else:
                    sortino_ratio = rendement_total / downside_vol
                print(f"  Ratio de Sortino   : {sortino_ratio:.2f}")
        
        # Calmar ratio (rendement / max drawdown)
        if abs(max_drawdown) > 0:
            if nb_annees >= 1:
                calmar_ratio = rendement_annualise / abs(max_drawdown)
            else:
                calmar_ratio = rendement_total / abs(max_drawdown)
            print(f"  Ratio de Calmar    : {calmar_ratio:.2f}")
        
        print()
        
        # === STATISTIQUES ===
        print(f"{Fore.YELLOW}STATISTIQUES:{Style.RESET_ALL}")
        
        prix_min = hist['Close'].min()
        prix_max = hist['Close'].max()
        prix_moyen = hist['Close'].mean()
        
        print(f"  Prix minimum       : {prix_min:.2f}")
        print(f"  Prix maximum       : {prix_max:.2f}")
        print(f"  Prix moyen         : {prix_moyen:.2f}")
        print(f"  Amplitude          : {((prix_max - prix_min) / prix_min * 100):.2f}%")
        
        # Jours positifs vs négatifs
        jours_positifs = (returns > 0).sum()
        jours_negatifs = (returns < 0).sum()
        taux_reussite = jours_positifs / (jours_positifs + jours_negatifs) * 100
        print(f"  Jours positifs     : {jours_positifs} ({taux_reussite:.1f}%)")
        print(f"  Jours négatifs     : {jours_negatifs} ({100-taux_reussite:.1f}%)")
        
        # Meilleur et pire jour
        meilleur_jour = returns.max() * 100
        pire_jour = returns.min() * 100
        print(f"  Meilleur jour      : {meilleur_jour:+.2f}%")
        print(f"  Pire jour          : {pire_jour:+.2f}%")
        
        print()
        
        # === COMPARAISON AVEC BENCHMARK ===
        if benchmark_ticker:
            print(f"{Fore.YELLOW}COMPARAISON AVEC BENCHMARK ({benchmark_ticker}):{Style.RESET_ALL}")
            try:
                benchmark = yf.Ticker(benchmark_ticker)
                
                if ':' in period:
                    bench_hist = benchmark.history(start=start_date, end=end_date)
                else:
                    bench_hist = benchmark.history(period=period)
                
                if not bench_hist.empty:
                    bench_prix_debut = bench_hist['Close'].iloc[0]
                    bench_prix_fin = bench_hist['Close'].iloc[-1]
                    bench_rendement = ((bench_prix_fin - bench_prix_debut) / bench_prix_debut) * 100
                    
                    # Dividendes du benchmark si demandé
                    bench_dividends = 0
                    if include_dividends:
                        bench_divs = benchmark.dividends[bench_hist.index[0]:bench_hist.index[-1]]
                        if not bench_divs.empty:
                            bench_dividends = bench_divs.sum()
                    
                    bench_rendement_total = ((bench_prix_fin + bench_dividends - bench_prix_debut) / bench_prix_debut) * 100
                    
                    print(f"  Rendement benchmark: {bench_rendement_total:+.2f}%")
                    print(f"  Différence         : {rendement_total - bench_rendement_total:+.2f}%")
                    
                    if rendement_total > bench_rendement_total:
                        print(f"  {Fore.GREEN}✓ Surperformance de {rendement_total - bench_rendement_total:.2f}%{Style.RESET_ALL}")
                    else:
                        print(f"  {Fore.RED}✗ Sous-performance de {abs(rendement_total - bench_rendement_total):.2f}%{Style.RESET_ALL}")
                    
                    # Alpha et Beta (corrélation)
                    bench_returns = bench_hist['Close'].pct_change().dropna()
                    
                    # Aligner les dates
                    common_dates = returns.index.intersection(bench_returns.index)
                    if len(common_dates) > 2:
                        aligned_returns = returns.loc[common_dates]
                        aligned_bench = bench_returns.loc[common_dates]
                        
                        # Beta (sensibilité au marché)
                        covariance = np.cov(aligned_returns, aligned_bench)[0, 1]
                        benchmark_variance = np.var(aligned_bench)
                        if benchmark_variance > 0:
                            beta = covariance / benchmark_variance
                            print(f"  Beta               : {beta:.2f}")
                        
                        # Corrélation
                        correlation = np.corrcoef(aligned_returns, aligned_bench)[0, 1]
                        print(f"  Corrélation        : {correlation:.2f}")
                else:
                    print(f"  {Fore.RED}Données du benchmark non disponibles{Style.RESET_ALL}")
            except Exception as e:
                print(f"  {Fore.RED}Erreur lors de la comparaison: {e}{Style.RESET_ALL}")
            
            print()
        
        print(f"{Style.BRIGHT}{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"{Fore.RED}Erreur lors du calcul de rendement: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()

def write_to_obsidian(info, yqfund):
    try:
        # Date de création de la fiche
        date_creation = datetime.now().strftime('%d/%m/%Y à %H:%M')
        
        # Informations de base
        symbol = info.get('symbol', ticker_symbol)
        symbol_as_tag = symbol.replace('.', '_')
        longName = info.get('longName', info.get('shortName', symbol))
        shortName = info.get('shortName', 'N/A')
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
        
        # Détection de l'indice répliqué (depuis le nom ou category)
        indice_replique = "Non identifié"
        longNameLower = longName.lower()
        category = info.get('category', '').lower()
        
        # Patterns de détection d'indices
        if 'msci world' in longNameLower or 'msci world' in category:
            indice_replique = "MSCI World"
        elif 'msci acwi' in longNameLower or 'all-world' in longNameLower or 'ftse all-world' in longNameLower:
            indice_replique = "FTSE All-World / MSCI ACWI"
        elif 's&p 500' in longNameLower or 'sp500' in longNameLower or 'sp 500' in longNameLower:
            indice_replique = "S&P 500"
        elif 'stoxx 50' in longNameLower or 'euro stoxx 50' in longNameLower:
            indice_replique = "EURO STOXX 50"
        elif 'stoxx 600' in longNameLower or 'europe 600' in longNameLower:
            indice_replique = "STOXX Europe 600"
        elif 'nasdaq' in longNameLower:
            indice_replique = "NASDAQ"
        elif 'ftse 100' in longNameLower:
            indice_replique = "FTSE 100"
        elif 'dax' in longNameLower:
            indice_replique = "DAX"
        elif 'cac 40' in longNameLower:
            indice_replique = "CAC 40"
        elif 'emerging' in longNameLower or 'emergent' in longNameLower:
            indice_replique = "MSCI Emerging Markets"
        elif 'developed europe' in longNameLower:
            indice_replique = "FTSE Developed Europe"
        
        # URL du site émetteur
        site_web = "[A compléter]()"
        fundFamilyLower = fundFamily.lower() if fundFamily != '<non présent>' else ''
        
        if 'blackrock' in fundFamilyLower or 'ishares' in fundFamilyLower:
            # Essayer de construire l'URL BlackRock avec le nom de l'ETF
            etf_name_encoded = longName.replace(' ', '%20')
            site_web = f"[BlackRock iShares](https://www.blackrock.com/fr/particuliers/products/investment-funds#/?productView=all&search={etf_name_encoded})"
        elif 'vanguard' in fundFamilyLower:
            site_web = "[Vanguard](https://investor.vanguard.com)"
        elif 'amundi' in fundFamilyLower:
            site_web = "[Amundi ETF](https://www.amundietf.fr/fr/particuliers)"
        elif 'lyxor' in fundFamilyLower:
            site_web = "[Lyxor / Amundi](https://www.amundietf.fr/fr/particuliers)"
        elif 'spdr' in fundFamilyLower or 'state street' in fundFamilyLower:
            site_web = "[SPDR / State Street](https://www.ssga.com/fr/en_gb/institutional/etfs)"
        elif 'xtrackers' in fundFamilyLower or 'dws' in fundFamilyLower:
            site_web = "[Xtrackers / DWS](https://etf.dws.com)"
        elif 'wisdomtree' in fundFamilyLower:
            site_web = "[WisdomTree](https://www.wisdomtree.eu)"
        elif 'invesco' in fundFamilyLower:
            site_web = "[Invesco](https://www.invesco.com/us/financial-products/etfs)"
        else:
            site_web = "[A compléter - émetteur non reconnu]()"
        
        # Date de création de l'ETF
        firstTrade = info.get('firstTradeDateEpochUtc', None)
        firstTradeDate = datetime.fromtimestamp(firstTrade).strftime('%d/%m/%Y') if firstTrade else 'N/A'
        
        # ISIN / codes
        isin = info.get('isin', 'N/A')
        
        # Description
        businessSummary = info.get('longBusinessSummary', info.get('description', 'Non disponible'))
        
        # Répartition et holdings
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
        
        # Calcul de rendement sur 1 an (version complète avec statistiques)
        rendement_data = {}
        stats_data = {}
        try:
            hist_1y = fund.history(period='1y')
            if len(hist_1y) > 1:
                prix_debut = hist_1y['Close'].iloc[0]
                prix_fin = hist_1y['Close'].iloc[-1]
                rendement_simple = ((prix_fin - prix_debut) / prix_debut) * 100
                
                dividends_1y = fund.dividends[hist_1y.index[0]:hist_1y.index[-1]]
                total_dividends = dividends_1y.sum() if not dividends_1y.empty else 0
                rendement_total = ((prix_fin + total_dividends - prix_debut) / prix_debut) * 100
                
                # Calculs statistiques
                returns = hist_1y['Close'].pct_change().dropna()
                volatilite = returns.std() * np.sqrt(252) * 100
                
                # Drawdown
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                max_drawdown = drawdown.min() * 100
                max_dd_date = drawdown.idxmin().strftime('%d/%m/%Y')
                
                # Prix min/max/moyen
                prix_min = hist_1y['Close'].min()
                prix_max = hist_1y['Close'].max()
                prix_moyen = hist_1y['Close'].mean()
                
                # Jours positifs/négatifs
                jours_positifs = (returns > 0).sum()
                jours_negatifs = (returns < 0).sum()
                taux_reussite = jours_positifs / (jours_positifs + jours_negatifs) * 100
                
                # Meilleur et pire jour
                meilleur_jour = returns.max() * 100
                pire_jour = returns.min() * 100
                
                # Ratios
                sharpe_ratio = rendement_total / volatilite if volatilite > 0 else 0
                
                negative_returns = returns[returns < 0]
                sortino_ratio = 0
                if len(negative_returns) > 0:
                    downside_vol = negative_returns.std() * np.sqrt(252) * 100
                    if downside_vol > 0:
                        sortino_ratio = rendement_total / downside_vol
                
                calmar_ratio = rendement_total / abs(max_drawdown) if abs(max_drawdown) > 0 else 0
                
                rendement_data = {
                    'rendement_simple': rendement_simple,
                    'rendement_total': rendement_total,
                    'volatilite': volatilite,
                    'max_drawdown': max_drawdown,
                    'max_dd_date': max_dd_date,
                    'sharpe': sharpe_ratio,
                    'sortino': sortino_ratio,
                    'calmar': calmar_ratio,
                    'date_calcul': datetime.now().strftime('%d/%m/%Y'),
                    'periode_debut': hist_1y.index[0].strftime('%d/%m/%Y'),
                    'periode_fin': hist_1y.index[-1].strftime('%d/%m/%Y')
                }
                
                stats_data = {
                    'prix_min': prix_min,
                    'prix_max': prix_max,
                    'prix_moyen': prix_moyen,
                    'amplitude': ((prix_max - prix_min) / prix_min * 100),
                    'jours_positifs': jours_positifs,
                    'jours_negatifs': jours_negatifs,
                    'taux_reussite': taux_reussite,
                    'meilleur_jour': meilleur_jour,
                    'pire_jour': pire_jour
                }
        except Exception as e:
            print(f"{Fore.YELLOW}Attention: Calcul de rendement échoué - {e}{Style.RESET_ALL}")
            pass
        
        # YTD (rendement depuis le début de l'année)
        ytd_rendement = None
        try:
            start_of_year = datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')
            hist_ytd = fund.history(start=start_of_year)
            if len(hist_ytd) > 1:
                prix_debut_ytd = hist_ytd['Close'].iloc[0]
                prix_fin_ytd = hist_ytd['Close'].iloc[-1]
                ytd_rendement = ((prix_fin_ytd - prix_debut_ytd) / prix_debut_ytd) * 100
        except Exception:
            pass
        
        # Dividendes
        dividend_info = {}
        try:
            dividends = fund.dividends
            if not dividends.empty and len(dividends) > 0:
                dernier_dividende = dividends.iloc[-1]
                date_dernier_div = dividends.index[-1].strftime('%d/%m/%Y')
                dividend_info = {
                    'yield': dividendYield,
                    'dernier_montant': dernier_dividende,
                    'date_dernier': date_dernier_div,
                    'nb_distributions': len(dividends)
                }
        except Exception:
            pass
        
        # Création du fichier
        home_directory = os.path.expanduser("~")
        obsidian_directory = home_directory + "/Library/Mobile Documents/iCloud~md~obsidian/Documents/Invest"
        directory_name = obsidian_directory + "/8 ETF"
        os.makedirs(directory_name, exist_ok=True)
        filename = f"{directory_name}/{longName}.md"
        
        with open(filename, "w", encoding='utf-8') as file:
            # En-tête
            file.write(f"#ETF #{symbol_as_tag}\n\n")
            file.write(f"**Fiche créée le :** {date_creation}\n")
            file.write(f"**Dernière mise à jour :** {date_creation}\n\n")
            file.write("---\n\n")
            
            # 1. Généralités
            file.write(f"## Généralités\n\n")
            file.write(f"- **Symbole** : `{symbol}`\n")
            file.write(f"- **Nom complet** : {longName}\n")
            file.write(f"- **Nom court** : {shortName}\n")
            file.write(f"- **Fund family** : {fundFamily}\n")
            file.write(f"- **Exchange** : {exchange}\n")
            file.write(f"- **Devise** : {currency}\n")
            file.write(f"- **Quote type** : {quoteType}\n")
            file.write(f"- **Type** : {etf_type}\n")
            file.write(f"- **ISIN** : {isin}\n")
            file.write(f"- **Date de création ETF** : {firstTradeDate}\n")
            file.write(f"- **Site web** : {site_web}\n\n")
            
            # 2. Données financières
            file.write(f"## Données financières\n\n")
            if currentPrice != 'N/A':
                file.write(f"- **Prix actuel** : {currentPrice:.2f} {currency}\n".replace('.', ','))
            if previousClose != 'N/A':
                file.write(f"- **Clôture précédente** : {previousClose:.2f} {currency}\n".replace('.', ','))
            if fiftyTwoWeekLow != 'N/A' and fiftyTwoWeekHigh != 'N/A':
                file.write(f"- **Range 52 semaines** : {fiftyTwoWeekLow:.2f} - {fiftyTwoWeekHigh:.2f}\n".replace('.', ','))
            if fiftyDayAverage != 'N/A':
                file.write(f"- **Moyenne mobile 50j** : {fiftyDayAverage:.2f}\n".replace('.', ','))
            if twoHundredDayAverage != 'N/A':
                file.write(f"- **Moyenne mobile 200j** : {twoHundredDayAverage:.2f}\n".replace('.', ','))
            if volume != 'N/A':
                file.write(f"- **Volume** : {volume:,}\n".replace(',', ' '))
            if totalAssets != 'N/A':
                file.write(f"- **Actifs sous gestion** : {totalAssets:,.0f} {currency}\n".replace(',', ' '))
            if expenseRatio is not None:
                file.write(f"- **Frais de gestion (TER)** : {expenseRatio:.2%}\n".replace('.', ','))
            file.write("\n")
            
            # 3. Description
            file.write(f"## Description\n\n")
            file.write(f"{businessSummary}\n\n")
            
            # 4. Performance
            file.write(f"## Performance (sur 1 an)\n\n")
            if rendement_data:
                file.write(f"**Période analysée :** {rendement_data['periode_debut']} → {rendement_data['periode_fin']}\n\n")
                file.write(f"### Rendements\n\n")
                file.write(f"- **Rendement prix** : {rendement_data['rendement_simple']:+.2f}%\n".replace('.', ','))
                file.write(f"- **Rendement total (avec dividendes)** : {rendement_data['rendement_total']:+.2f}%\n".replace('.', ','))
                if ytd_rendement is not None:
                    file.write(f"- **YTD (année en cours)** : {ytd_rendement:+.2f}%\n".replace('.', ','))
                file.write(f"\n### Risque\n\n")
                file.write(f"- **Volatilité annuelle** : {rendement_data['volatilite']:.2f}%\n".replace('.', ','))
                file.write(f"- **Drawdown maximum** : {rendement_data['max_drawdown']:.2f}% (le {rendement_data['max_dd_date']})\n".replace('.', ','))
                file.write(f"\n### Ratios\n\n")
                file.write(f"- **Ratio de Sharpe** : {rendement_data['sharpe']:.2f}\n".replace('.', ','))
                file.write(f"- **Ratio de Sortino** : {rendement_data['sortino']:.2f}\n".replace('.', ','))
                file.write(f"- **Ratio de Calmar** : {rendement_data['calmar']:.2f}\n".replace('.', ','))
                
                if stats_data:
                    file.write(f"\n### Statistiques de prix\n\n")
                    file.write(f"- **Prix minimum** : {stats_data['prix_min']:.2f} {currency}\n".replace('.', ','))
                    file.write(f"- **Prix maximum** : {stats_data['prix_max']:.2f} {currency}\n".replace('.', ','))
                    file.write(f"- **Prix moyen** : {stats_data['prix_moyen']:.2f} {currency}\n".replace('.', ','))
                    file.write(f"- **Amplitude** : {stats_data['amplitude']:.2f}%\n".replace('.', ','))
                    file.write(f"\n### Analyse des mouvements\n\n")
                    file.write(f"- **Jours positifs** : {stats_data['jours_positifs']} ({stats_data['taux_reussite']:.1f}%)\n".replace('.', ','))
                    file.write(f"- **Jours négatifs** : {stats_data['jours_negatifs']} ({100-stats_data['taux_reussite']:.1f}%)\n".replace('.', ','))
                    file.write(f"- **Meilleur jour** : {stats_data['meilleur_jour']:+.2f}%\n".replace('.', ','))
                    file.write(f"- **Pire jour** : {stats_data['pire_jour']:+.2f}%\n".replace('.', ','))
                
                file.write(f"\n*Calcul effectué le {rendement_data['date_calcul']}*\n")
            else:
                file.write("Données de performance non disponibles.\n")
            file.write("\n")
            
            # 5. Dividendes
            if dividend_info:
                file.write(f"## Dividendes\n\n")
                if dividend_info.get('yield'):
                    file.write(f"- **Yield actuel** : {dividend_info['yield']:.2%}\n".replace('.', ','))
                file.write(f"- **Dernier dividende** : {dividend_info['dernier_montant']:.4f} le {dividend_info['date_dernier']}\n".replace('.', ','))
                file.write(f"- **Nombre de distributions** : {dividend_info['nb_distributions']}\n\n")
            
            # 6. Répartition sectorielle
            file.write(f"## Répartition sectorielle\n\n")
            if hasattr(repartition, 'to_string'):
                file.write("```\n")
                file.write(repartition.to_string(index=True))
                file.write("\n```\n\n")
            else:
                file.write(f"{repartition}\n\n")
            
            # 7. Principales positions
            file.write(f"## Principales positions\n\n")
            if hasattr(top_holdings, 'to_string'):
                file.write("```\n")
                file.write(top_holdings.to_string(index=True))
                file.write("\n```\n\n")
            else:
                file.write(f"{top_holdings}\n\n")
            
            # 8. Notes personnelles
            file.write(f"## Notes personnelles\n\n")
            file.write(f"*Ajoutez ici vos notes, analyses et réflexions sur cet ETF...*\n\n")
        
        print(f"{Fore.GREEN}✓ Fiche Obsidian créée: {filename}{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}✗ Erreur lors de la création de la fiche Obsidian: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
    
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
elif args.rendement:
    get_basic_info(info)
    calculate_rendement(fund, 
                       period=args.period, 
                       include_dividends=not args.no_dividends,
                       benchmark_ticker=args.benchmark)
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
