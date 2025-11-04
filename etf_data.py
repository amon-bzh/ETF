# etf_data.py - Fonctions de récupération et calcul de données ETF
from datetime import datetime

def compute_ytd_return(fund):
    """
    Calcule le rendement depuis le début de l'année (YTD)
    Args:
        fund: objet yfinance.Ticker
    Returns:
        float ou None
    """
    try:
        start_of_year = datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')
        hist_ytd = fund.history(start=start_of_year)
        if len(hist_ytd) > 1:
            prix_debut_ytd = hist_ytd['Close'].iloc[0]
            prix_fin_ytd = hist_ytd['Close'].iloc[-1]
            return ((prix_fin_ytd - prix_debut_ytd) / prix_debut_ytd) * 100
    except Exception:
        pass
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
    try:
        dividends = fund.dividends
        if hasattr(dividends, 'empty') and not dividends.empty and len(dividends) > 0:
            dernier_dividende = dividends.iloc[-1]
            date_dernier_div = dividends.index[-1].strftime('%d/%m/%Y')
            return {
                'yield': dividendYield,
                'dernier_montant': dernier_dividende,
                'date_dernier': date_dernier_div,
                'nb_distributions': len(dividends)
            }
    except Exception:
        pass

    return {}

def get_sector_weights(yqfund, ticker_symbol):
    """
    Récupère la répartition sectorielle d'un ETF
    Args:
        yqfund: objet yahooquery.Ticker
        ticker_symbol: symbole du ticker

    Returns:
        (repartition_fmt, erreur) tuple
    """
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
        return repartition_fmt, None
    except Exception as e:
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
        return top_holdings_fmt, None
    except Exception as e:
        return "Non disponible", str(e)