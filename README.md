# etfinfo.py

Outil d'analyse et d'information sur les ETF en ligne de commande.

## Installation

### Prérequis
- Python 3.10 ou supérieur
- Environnement virtuel recommandé

### Configuration de l'environnement

```bash
# Se placer dans le répertoire du projet
cd ~/Developer/ETF

# Créer l'environnement virtuel
python3 -m venv venv-etf

# Activer l'environnement virtuel
source venv-etf/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install yfinance yahooquery colorama pandas numpy
```

## Utilisation

### Activation de l'environnement

Avant chaque utilisation, activer l'environnement virtuel :

```bash
cd ~/Developer/ETF
source venv-etf/bin/activate
```

### Commandes disponibles

#### Informations de base
```bash
python etfinfo.py VWCE.DE
```
Affiche : symbole, nom, marché, devise, fund family

#### Données financières
```bash
python etfinfo.py VWCE.DE --financials
```
Affiche : prix actuel, clôture précédente, range 52 semaines, moyennes mobiles, volume, actifs sous gestion, frais de gestion

#### Description / Business Summary
```bash
python etfinfo.py VWCE.DE --summary
```
Affiche : objectif et stratégie d'investissement de l'ETF

#### Répartition sectorielle
```bash
python etfinfo.py VWCE.DE --repartition
```
Affiche : répartition par secteurs d'activité

#### Principales positions (Top Holdings)
```bash
python etfinfo.py VWCE.DE --top-holdings
```
Affiche : top 10 des positions de l'ETF

#### Historique
```bash
python etfinfo.py VWCE.DE --history
```
Affiche : historique des prix sur 1 mois

#### Analyse de rendement
```bash
# Rendement sur 1 an (par défaut)
python etfinfo.py VWCE.DE --rendement

# Périodes disponibles
python etfinfo.py VWCE.DE --rendement --period 1mo   # 1 mois
python etfinfo.py VWCE.DE --rendement --period 3mo   # 3 mois
python etfinfo.py VWCE.DE --rendement --period 6mo   # 6 mois
python etfinfo.py VWCE.DE --rendement --period 1y    # 1 an
python etfinfo.py VWCE.DE --rendement --period 2y    # 2 ans
python etfinfo.py VWCE.DE --rendement --period 5y    # 5 ans
python etfinfo.py VWCE.DE --rendement --period max   # Depuis création

# Période personnalisée
python etfinfo.py VWCE.DE --rendement --period 2020-01-01:2023-12-31

# Sans dividendes
python etfinfo.py VWCE.DE --rendement --no-dividends

# Comparaison avec benchmark
python etfinfo.py VWCE.DE --rendement --benchmark ^GSPC  # S&P 500
python etfinfo.py VWCE.DE --rendement --benchmark URTH   # MSCI World
```

L'analyse de rendement affiche :
- **Rendements** : prix, total (avec dividendes), YTD
- **Risque** : volatilité annuelle, drawdown maximum
- **Ratios** : Sharpe, Sortino, Calmar
- **Statistiques** : prix min/max/moyen, amplitude, jours positifs/négatifs
- **Comparaison** : performance vs benchmark, beta, corrélation

#### Toutes les informations
```bash
python etfinfo.py VWCE.DE --all
```
Affiche toutes les données disponibles (sauf rendement et Obsidian)

#### Données brutes
```bash
python etfinfo.py VWCE.DE --raw
```
Affiche toutes les données brutes du ticker (format JSON)

#### Créer une fiche Obsidian
```bash
python etfinfo.py VWCE.DE --obsidian
```
Crée une fiche Markdown complète dans Obsidian avec :
- Généralités (identification, ISIN, dates)
- Données financières
- Description
- Performance détaillée (1 an)
- Dividendes (si applicable)
- Répartition sectorielle
- Principales positions
- Section notes personnelles

**Emplacement** : `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Invest/8 ETF/`

## Exemples d'ETF

```bash
# ETF Monde
python etfinfo.py VWCE.DE --rendement          # Vanguard FTSE All-World (EUR)
python etfinfo.py IWDA.AS --rendement          # iShares Core MSCI World (EUR)

# ETF S&P 500
python etfinfo.py VOO --rendement              # Vanguard S&P 500 (USD)
python etfinfo.py SPY --rendement              # SPDR S&P 500 (USD)

# ETF Emerging Markets
python etfinfo.py VFEM.AS --rendement          # Vanguard FTSE Emerging Markets

# ETF Europe
python etfinfo.py VEUR.AS --rendement          # Vanguard FTSE Developed Europe
```

## Formats et conventions

### Dates
Format français : `dd/mm/yyyy` (ex: 28/10/2025)

### Nombres
- Séparateur décimal : virgule `,` (ex: 12,34)
- Séparateur de milliers : espace (ex: 1 234 567)

### Pourcentages
Affichage explicite avec symbole `%` (ex: 15,23%)

## Astuces

### Alias pour aller plus vite

Ajoutez dans votre `~/.zshrc` :

```bash
# Accès rapide au projet ETF
alias etf='cd ~/Developer/ETF && source venv-etf/bin/activate'

# Commande directe (après avoir ajouté le script au PATH)
alias etfinfo='python ~/Developer/ETF/etfinfo.py'
```

Puis rechargez : `source ~/.zshrc`

Utilisation :
```bash
etf                              # Active l'environnement
etfinfo VWCE.DE --rendement      # Lance l'analyse
```

### Désactivation de l'environnement

```bash
deactivate
```

## Notes

- Les données proviennent de Yahoo Finance
- Certaines données peuvent ne pas être disponibles pour tous les ETF
- Les calculs de rendement incluent les dividendes par défaut
- La répartition sectorielle et les holdings utilisent le format anglo-saxon (limitation technique)

## Auteur

Antoine - 2023-2025
