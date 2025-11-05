# etf_data.py - Fonctions de récupération et calcul de données ETF
from datetime import datetime
import numpy as np
from datetime import datetime
from etf_utils import get_ratio_emoji
from etf_logging import log_info, log_warning, log_error, is_debug_enabled

def compute_ytd_return(fund):
    """
    Calcule le rendement depuis le début de l'année (YTD)
    Args:
        fund: objet yfinance.Ticker
    Returns:
        float ou None
    """
    if is_debug_enabled():
        log_info("compute_ytd_return: start")
    try:
        start_of_year = datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')
        hist_ytd = fund.history(start=start_of_year)
        if len(hist_ytd) > 1:
            prix_debut_ytd = hist_ytd['Close'].iloc[0]
            prix_fin_ytd = hist_ytd['Close'].iloc[-1]
            if is_debug_enabled():
                log_info(f"compute_ytd_return: computed YTD = {((prix_fin_ytd - prix_debut_ytd) / prix_debut_ytd) * 100:.2f}%")
            return ((prix_fin_ytd - prix_debut_ytd) / prix_debut_ytd) * 100
    except Exception as e:
        if is_debug_enabled():
            log_warning(f"compute_ytd_return: error {e}")
    if is_debug_enabled():
        log_info("compute_ytd_return: no data or error, returning None")
    return None

def build_dividend_info(fund, dividendYield):
    """
    Construit les informations de dividendes pour l'ETF

    Args:
        fund: objet yfinance.Ticker
        dividendYield: rendement du dividende (float ou None)

    Returns:
        dict contenant yield, dernier montant, date dernier dividende, nb distributions
    """
    if is_debug_enabled():
        log_info("build_dividend_info: start")
    try:
        dividends = fund.dividends
        if hasattr(dividends, 'empty') and not dividends.empty and len(dividends) > 0:
            dernier_dividende = dividends.iloc[-1]
            date_dernier_div = dividends.index[-1].strftime('%d/%m/%Y')
            if is_debug_enabled():
                log_info(f"build_dividend_info: last dividend {dernier_dividende} on {date_dernier_div}")
            return {
                'yield': dividendYield,
                'dernier_montant': dernier_dividende,
                'date_dernier': date_dernier_div,
                'nb_distributions': len(dividends)
            }
    except Exception as e:
        if is_debug_enabled():
            log_warning(f"build_dividend_info: error {e}")

    if is_debug_enabled():
        log_info("build_dividend_info: no dividend data, returning empty dict")
    return {}

def compute_performance_and_stats(fund):
    """
    Calcule les performances sur 1 an + stats prix et drawdown
    Args:
        fund: objet yfinance.Ticker
    Returns:
        rendement_data (dict), stats_data (dict)
    """
    if is_debug_enabled():
        log_info("compute_performance_and_stats: start")
    rendement_data = {}
    stats_data = {}
    try:
        hist_1y = fund.history(period='1y')
        if len(hist_1y) <= 1:
            if is_debug_enabled():
                log_warning("compute_performance_and_stats: insufficient price history")
            return {}, {}

        prix_debut = hist_1y['Close'].iloc[0]
        prix_fin = hist_1y['Close'].iloc[-1]
        rendement_simple = ((prix_fin - prix_debut) / prix_debut) * 100

        dividends_1y = fund.dividends[hist_1y.index[0]:hist_1y.index[-1]]
        total_dividends = dividends_1y.sum() if hasattr(dividends_1y, 'empty') and not dividends_1y.empty else 0
        rendement_total = ((prix_fin + total_dividends - prix_debut) / prix_debut) * 100

        returns = hist_1y['Close'].pct_change().dropna()
        volatilite = returns.std() * np.sqrt(252) * 100

        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        max_dd_date = drawdown.idxmin().strftime('%d/%m/%Y')

        prix_min = hist_1y['Close'].min()
        prix_max = hist_1y['Close'].max()
        prix_moyen = hist_1y['Close'].mean()

        jours_positifs = (returns > 0).sum()
        jours_negatifs = (returns < 0).sum()
        taux_reussite = jours_positifs / (jours_positifs + jours_negatifs) * 100 if (jours_positifs + jours_negatifs) > 0 else 0

        meilleur_jour = returns.max() * 100
        pire_jour = returns.min() * 100

        sharpe_ratio = rendement_total / volatilite if volatilite > 0 else 0

        negative_returns = returns[returns < 0]
        sortino_ratio = 0
        if len(negative_returns) > 0:
            downside_vol = negative_returns.std() * np.sqrt(252) * 100
            if downside_vol > 0:
                sortino_ratio = rendement_total / downside_vol

        calmar_ratio = rendement_total / abs(max_drawdown) if abs(max_drawdown) > 0 else 0

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
            'amplitude': ((prix_max - prix_min) / prix_min * 100) if prix_min else 0,
            'jours_positifs': jours_positifs,
            'jours_negatifs': jours_negatifs,
            'taux_reussite': taux_reussite,
            'meilleur_jour': meilleur_jour,
            'pire_jour': pire_jour
        }

        if is_debug_enabled():
            log_info("compute_performance_and_stats: metrics computed successfully")
        return rendement_data, stats_data
    except Exception as e:
        if is_debug_enabled():
            log_error(f"compute_performance_and_stats: error {e}")
        return {}, {}

def get_sector_weights(yqfund, ticker_symbol):
    """
    Récupère la répartition sectorielle d'un ETF
    Args:
        yqfund: objet yahooquery.Ticker
        ticker_symbol: symbole du ticker

    Returns:
        (repartition_fmt, erreur) tuple
    """
    if is_debug_enabled():
        log_info("get_sector_weights: start")
    try:
        repartition = yqfund.fund_sector_weightings
        if isinstance(repartition, dict) and ticker_symbol in repartition:
            repartition = repartition[ticker_symbol]
        if hasattr(repartition, 'map'):
            repartition_fmt = repartition.map(
                lambda x: x * 100 if isinstance(x, (int, float)) and 0 <= x <= 1 else x
            )
        else:
            repartition_fmt = repartition
        if is_debug_enabled():
            log_info("get_sector_weights: sector weights retrieved")
        return repartition_fmt, None
    except Exception as e:
        if is_debug_enabled():
            log_warning(f"get_sector_weights: error {e}")
        return "Non disponible", str(e)

def get_top_holdings(yqfund, ticker_symbol):
    """
    Récupère les principales positions d'un ETF
    Args:
        yqfund: objet yahooquery.Ticker
        ticker_symbol: symbole du ticker

    Returns:
        (top_holdings_fmt, erreur) tuple
    """
    if is_debug_enabled():
        log_info("get_top_holdings: start")
    try:
        top_holdings = yqfund.fund_top_holdings
        if isinstance(top_holdings, dict) and ticker_symbol in top_holdings:
            top_holdings = top_holdings[ticker_symbol]
        if hasattr(top_holdings, 'map'):
            top_holdings_fmt = top_holdings.map(
                lambda x: x * 100 if isinstance(x, (int, float)) and 0 <= x <= 1 else x
            )
        else:
            top_holdings_fmt = top_holdings
        if is_debug_enabled():
            log_info("get_top_holdings: top holdings retrieved")
        return top_holdings_fmt, None
    except Exception as e:
        if is_debug_enabled():
            log_warning(f"get_top_holdings: error {e}")
        return "Non disponible", str(e)