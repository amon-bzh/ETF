#!/usr/bin/python3
# etf_obsidian.py - Génération des fiches Obsidian pour les ETF

import os
import numpy as np
from datetime import datetime
from colorama import Fore, Style
from etf_utils import detect_indice, get_emetteur_url, get_ratio_emoji, format_date_fr
from etf_markdown import (
    write_header,
    write_general_section,
    write_financial_section,
    write_description_section,
    write_performance_section
)

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
        try:
            repartition = yqfund.fund_sector_weightings
            if isinstance(repartition, dict) and ticker_symbol in repartition:
                repartition = repartition[ticker_symbol]
            
            # Multiplier par 100 si les valeurs sont des décimaux (entre 0 et 1)
            if hasattr(repartition, 'map'):
                repartition_fmt = repartition.map(
                    lambda x: x * 100 if isinstance(x, (int, float)) and 0 <= x <= 1 else x
                )
            else:
                repartition_fmt = repartition
        except Exception as e:
            print(f"{Fore.YELLOW}Attention: Répartition non disponible - {e}{Style.RESET_ALL}")
            repartition = "Non disponible"
            repartition_fmt = "Non disponible"
        
        try:
            top_holdings = yqfund.fund_top_holdings
            if isinstance(top_holdings, dict) and ticker_symbol in top_holdings:
                top_holdings = top_holdings[ticker_symbol]
            
            # Multiplier par 100 si les valeurs sont des décimaux
            if hasattr(top_holdings, 'map'):
                top_holdings_fmt = top_holdings.map(
                    lambda x: x * 100 if isinstance(x, (int, float)) and 0 <= x <= 1 else x
                )
            else:
                top_holdings_fmt = top_holdings
        except Exception as e:
            print(f"{Fore.YELLOW}Attention: Holdings non disponibles - {e}{Style.RESET_ALL}")
            top_holdings = "Non disponible"
            top_holdings_fmt = "Non disponible"
        
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
                
                # Emojis pour les ratios
                sharpe_emoji, sharpe_alert = get_ratio_emoji(sharpe_ratio, 'sharpe')
                sortino_emoji, sortino_alert = get_ratio_emoji(sortino_ratio, 'sortino')
                
                rendement_data = {
                    'rendement_simple': rendement_simple,
                    'rendement_total': rendement_total,
                    'volatilite': volatilite,
                    'max_drawdown': max_drawdown,
                    'max_dd_date': max_dd_date,
                    'sharpe': sharpe_ratio,
                    'sharpe_emoji': sharpe_emoji,
                    'sharpe_alert': sharpe_alert,
                    'sortino': sortino_ratio,
                    'sortino_emoji': sortino_emoji,
                    'sortino_alert': sortino_alert,
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

        # Vérification si le fichier existe déjà
        if os.path.exists(filename):
            # Lire la première ligne contenant la date
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                date_line = None
                mod_line = None
                for line in content.splitlines():
                    if "**Fiche créée le" in line:
                        date_line = line.strip()
                    if "**Dernière mise à jour" in line:
                        mod_line = line.strip()
                # Affichage avec print_note_dates
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
                return
            # Extraire la date de création existante si présente
            original_creation_date = None
            for line in content.splitlines():
                if "**Fiche créée le" in line:
                    original_creation_date = line.replace("**Fiche créée le :**","").strip()
                    break
            if not original_creation_date:
                original_creation_date = date_creation
        else:
            original_creation_date = date_creation

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
                file.write(f"## Dividendes\n\n")
                if dividend_info.get('yield'):
                    file.write(f"- **Yield actuel** : {dividend_info['yield']:.2%}\n".replace('.', ','))
                file.write(f"- **Dernier dividende** : {dividend_info['dernier_montant']:.4f} le {dividend_info['date_dernier']}\n".replace('.', ','))
                file.write(f"- **Nombre de distributions** : {dividend_info['nb_distributions']}\n\n")
            
            # 6. Répartition sectorielle
            file.write(f"## Répartition sectorielle\n\n")
            if hasattr(repartition_fmt, 'to_string'):
                file.write("```\n")
                file.write(repartition_fmt.to_string(index=True))
                file.write("\n```\n\n")
            elif repartition_fmt != "Non disponible":
                file.write(f"{repartition_fmt}\n\n")
            else:
                file.write(f"{repartition_fmt}\n\n")
            
            # 7. Principales positions
            file.write(f"## Principales positions\n\n")
            if hasattr(top_holdings_fmt, 'to_string'):
                file.write("```\n")
                file.write(top_holdings_fmt.to_string(index=True))
                file.write("\n```\n\n")
            elif top_holdings_fmt != "Non disponible":
                file.write(f"{top_holdings_fmt}\n\n")
            else:
                file.write(f"{top_holdings_fmt}\n\n")
            
            # 8. Notes personnelles
            file.write(f"## Notes personnelles\n\n")
            file.write(f"*Ajoutez ici vos notes, analyses et réflexions sur cet ETF...*\n\n")
        
        print(f"{Fore.WHITE}✓ Fiche Obsidian créée : {Style.RESET_ALL}{Fore.GREEN}{longName}.md{Style.RESET_ALL}")
        print(f"{Fore.WHITE}📁 Emplacement : {Style.RESET_ALL}{Fore.GREEN}{directory_name}{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}✗ Erreur lors de la création de la fiche Obsidian: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
    
    return
