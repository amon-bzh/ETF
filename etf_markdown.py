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