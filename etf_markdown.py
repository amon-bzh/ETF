# etf_markdown.py — génération du contenu Markdown pour les fiches Obsidian

def write_header(file, symbol_as_tag, original_creation_date, date_creation):
    """
    Écrit l'en-tête Markdown d'une fiche ETF dans Obsidian.
    Déplacé depuis etf_obsidian.py dans le cadre du refactoring.
    """
    file.write(f"#ETF #{symbol_as_tag}\n\n")
    file.write(f"**Fiche créée le :** {original_creation_date}\n")
    file.write(f"**Dernière mise à jour :** {date_creation}\n\n")
    file.write("---\n\n")

def write_general_section(file, data):
    """
    Écrit la section 'Généralités' dans la fiche Obsidian.
    Déplacé depuis etf_obsidian.py dans le cadre du refactoring.
    """
    file.write(f"## Généralités\n\n")
    file.write(f"- **Symbole** : {data['symbol']}\n")
    file.write(f"- **Nom complet** : {data['longName']}\n")
    file.write(f"- **Nom court** : {data['shortName']}\n")
    file.write(f"- **Fund family** : {data['fundFamily']}\n")
    file.write(f"- **Exchange** : {data['exchange']}\n")
    file.write(f"- **Devise** : {data['currency']}\n")
    file.write(f"- **Quote type** : {data['quoteType']}\n")
    file.write(f"- **Type** : {data['etf_type']}\n")
    file.write(f"- **Indice répliqué** : {data['indice_replique']}\n")
    file.write(f"- **ISIN** : {data['isin']}\n")
    file.write(f"- **Date de création ETF** : {data['firstTradeDate']}\n")
    file.write(f"- **Site web** : {data['site_web']}\n\n")

def write_financial_section(file, data):
    """
    Écrit la section 'Données financières' dans la fiche Obsidian.
    Déplacé depuis etf_obsidian.py dans le cadre du refactoring.
    """
    file.write("## Données financières\n\n")
    if data['currentPrice'] != 'N/A':
        file.write(f"- **Prix actuel** : {data['currentPrice']:.2f} {data['currency']}\n".replace('.', ','))
    if data['previousClose'] != 'N/A':
        file.write(f"- **Clôture précédente** : {data['previousClose']:.2f} {data['currency']}\n".replace('.', ','))
    if data['fiftyTwoWeekLow'] != 'N/A' and data['fiftyTwoWeekHigh'] != 'N/A':
        file.write(f"- **Range 52 semaines** : {data['fiftyTwoWeekLow']:.2f} - {data['fiftyTwoWeekHigh']:.2f}\n".replace('.', ','))
    if data['fiftyDayAverage'] != 'N/A':
        file.write(f"- **Moyenne mobile 50j** : {data['fiftyDayAverage']:.2f}\n".replace('.', ','))
    if data['twoHundredDayAverage'] != 'N/A':
        file.write(f"- **Moyenne mobile 200j** : {data['twoHundredDayAverage']:.2f}\n".replace('.', ','))
    if data['volume'] != 'N/A':
        file.write(f"- **Volume** : {data['volume']:,}\n".replace(',', ' '))
    if data['totalAssets'] != 'N/A':
        file.write(f"- **Actifs sous gestion** : {data['totalAssets']:,.0f} {data['currency']}\n".replace(',', ' '))
    if data['expenseRatio'] is not None:
        file.write(f"- **Frais de gestion (TER)** : {data['expenseRatio']:.2%}\n".replace('.', ','))
    file.write("\n")
    
def write_description_section(file, businessSummary):
    """
    Écrit la section 'Description' dans la fiche Obsidian.
    Déplacé depuis etf_obsidian.py dans le cadre du refactoring.
    """
    file.write("## Description\n\n")
    file.write(f"{businessSummary}\n\n")
    
def write_performance_section(file, rendement_data, stats_data, ytd_rendement, currency):
    """
    Écrit la section 'Performance (sur 1 an)' dans la fiche Obsidian.
    Déplacé depuis etf_obsidian.py dans le cadre du refactoring.
    """
    file.write("## Performance (sur 1 an)\n\n")
    if rendement_data:
        file.write(f"**Période analysée :** {rendement_data['periode_debut']} → {rendement_data['periode_fin']}\n\n")
        file.write("### Rendements\n\n")
        file.write(f"- **Rendement prix** : {rendement_data['rendement_simple']:+.2f}%\n".replace('.', ','))
        file.write(f"- **Rendement total (avec dividendes)** : {rendement_data['rendement_total']:+.2f}%\n".replace('.', ','))
        if ytd_rendement is not None:
            file.write(f"- **YTD (année en cours)** : {ytd_rendement:+.2f}%\n".replace('.', ','))

        file.write("\n### Risque\n\n")
        file.write(f"- **Volatilité annuelle** : {rendement_data['volatilite']:.2f}%\n".replace('.', ','))
        file.write(f"- **Drawdown maximum** : {rendement_data['max_drawdown']:.2f}% (le {rendement_data['max_dd_date']})\n".replace('.', ','))

        file.write("\n### Ratios (calculés sur 1 an)\n\n")

        sharpe_line = f"- **Ratio de Sharpe** : {rendement_data['sharpe']:.2f}".replace('.', ',')
        sharpe_line += f" {rendement_data['sharpe_emoji']}"
        if rendement_data['sharpe_alert']:
            sharpe_line += f" *{rendement_data['sharpe_alert']}*"
        file.write(sharpe_line + "\n")

        sortino_line = f"- **Ratio de Sortino** : {rendement_data['sortino']:.2f}".replace('.', ',')
        sortino_line += f" {rendement_data['sortino_emoji']}"
        if rendement_data['sortino_alert']:
            sortino_line += f" *{rendement_data['sortino_alert']}*"
        file.write(sortino_line + "\n")

        file.write(f"- **Ratio de Calmar** : {rendement_data['calmar']:.2f}\n".replace('.', ','))

        if stats_data:
            file.write("\n### Statistiques de prix\n\n")
            file.write(f"- **Prix minimum** : {stats_data['prix_min']:.2f} {currency}\n".replace('.', ','))
            file.write(f"- **Prix maximum** : {stats_data['prix_max']:.2f} {currency}\n".replace('.', ','))
            file.write(f"- **Prix moyen** : {stats_data['prix_moyen']:.2f} {currency}\n".replace('.', ','))
            file.write(f"- **Amplitude** : {stats_data['amplitude']:.2f}%\n".replace('.', ','))

            file.write("\n### Analyse des mouvements\n\n")
            file.write(f"- **Jours positifs** : {stats_data['jours_positifs']} ({stats_data['taux_reussite']:.1f}%)\n".replace('.', ','))
            file.write(f"- **Jours négatifs** : {stats_data['jours_negatifs']} ({100-stats_data['taux_reussite']:.1f}%)\n".replace('.', ','))
            file.write(f"- **Meilleur jour** : {stats_data['meilleur_jour']:+.2f}%\n".replace('.', ','))
            file.write(f"- **Pire jour** : {stats_data['pire_jour']:+.2f}%\n".replace('.', ','))

        file.write(f"\n*Calcul effectué le {rendement_data['date_calcul']}*\n\n")
    else:
        file.write("Données de performance non disponibles.\n\n")
        
def write_dividends_section(file, dividend_info):
    """
    Écrit la section 'Dividendes' dans la fiche Obsidian.
    Déplacé depuis etf_obsidian.py dans le cadre du refactoring.
    """
    file.write("## Dividendes\n\n")
    if dividend_info.get('yield'):
        file.write(f"- **Yield actuel** : {dividend_info['yield']:.2%}\n".replace('.', ','))
    file.write(f"- **Dernier dividende** : {dividend_info['dernier_montant']:.4f} le {dividend_info['date_dernier']}\n".replace('.', ','))
    file.write(f"- **Nombre de distributions** : {dividend_info['nb_distributions']}\n\n")

def write_sector_allocation_section(file, repartition_fmt):
    """
    Écrit la section 'Répartition sectorielle' dans la fiche Obsidian.
    Déplacé depuis etf_obsidian.py dans le cadre du refactoring.
    """
    file.write("## Répartition sectorielle\n\n")
    if hasattr(repartition_fmt, 'to_string'):
        file.write("```\n")
        file.write(repartition_fmt.to_string(index=True))
        file.write("\n```\n\n")
    elif repartition_fmt != "Non disponible":
        file.write(f"{repartition_fmt}\n\n")
    else:
        file.write(f"{repartition_fmt}\n\n")