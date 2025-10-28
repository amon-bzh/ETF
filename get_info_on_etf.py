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

# Pour les calculs de rendement
from datetime import datetime, timedelta
import numpy as np

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
