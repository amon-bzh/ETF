#!/usr/bin/python3
# etf_analysis.py - Calculs de rendement et analyse de performance

import numpy as np
import yfinance as yf
from colorama import Fore, Style
from datetime import datetime

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
