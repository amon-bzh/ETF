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
