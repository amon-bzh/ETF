# etfinfo.py

Outil avancé d’analyse et d’information sur les ETF en ligne de commande.

## 🚀 Installation

### Prérequis
- Python **3.12+**
- Un environnement virtuel est vivement recommandé

### Création et configuration de l’environnement

```bash
cd ~/Developer/ETF

# Création de l'environnement virtuel
python3 -m venv venv-etf

# Activation
source venv-etf/bin/activate

# Mise à jour de pip
pip install --upgrade pip

# Installation des dépendances
pip install -r requirements.txt
```

📌 Toutes les dépendances nécessaires sont centralisées dans `requirements.txt`.

## 🧭 Utilisation

### Activation de l’environnement

```bash
cd ~/Developer/ETF
source venv-etf/bin/activate
```

## 📘 Commandes principales

### Informations générales
```bash
python etfinfo.py VWCE.DE
```

### Données financières
```bash
python etfinfo.py VWCE.DE --financials
```

### Description / Business Summary
```bash
python etfinfo.py VWCE.DE --summary
```

### Répartition sectorielle
```bash
python etfinfo.py VWCE.DE --repartition
```

### Top holdings
```bash
python etfinfo.py VWCE.DE --top-holdings
```

### Historique (1 mois)
```bash
python etfinfo.py VWCE.DE --history
```

## 📈 Analyse de rendement

### Rendement 1 an (défaut)
```bash
python etfinfo.py VWCE.DE --rendement
```

### Périodes disponibles
```bash
python etfinfo.py VWCE.DE --rendement --period 1mo
python etfinfo.py VWCE.DE --rendement --period 1y
python etfinfo.py VWCE.DE --rendement --period max
```

### Période personnalisée
```bash
python etfinfo.py VWCE.DE --rendement --period 2020-01-01:2023-12-31
```

### Sans dividendes
```bash
python etfinfo.py VWCE.DE --rendement --no-dividends
```

### Comparaison benchmark
```bash
python etfinfo.py VWCE.DE --rendement --benchmark ^GSPC
```

### Le rapport présente :
- Rendements (simple, total, YTD)
- Risque (volatilité, drawdown)
- Ratios (Sharpe, Sortino, Calmar)
- Statistiques (min/max/moyen, jours positifs/négatifs)
- Comparaison (beta, corrélation, sur/sous-performance)

## 🌐 Fiches Obsidian

Créer une fiche complète :
```bash
python etfinfo.py VWCE.DE --obsidian
```

La fiche contient :
- Généralités  
- Données financières  
- Description  
- Performances  
- Dividendes  
- Répartition sectorielle  
- Top holdings  
- Notes personnelles  

📁 Répertoire par défaut :  
`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Invest/8 ETF/`

## 📚 Exemples d’ETF

```bash
python etfinfo.py VWCE.DE --rendement      # Monde
python etfinfo.py IWDA.AS --rendement      # MSCI World
python etfinfo.py VOO --rendement          # S&P 500
python etfinfo.py VFEM.AS --rendement      # Emerging Markets
python etfinfo.py VEUR.AS --rendement      # Europe
```

## 🔢 Formats et conventions

### Dates
Format français : `dd/mm/yyyy`

### Nombres
- Décimale : `,`
- Milliers : espace

### Pourcentages
Exemple : `15,23 %`

## ⚡ Astuces

### Alias utiles (`~/.zshrc`)
```bash
alias etf='cd ~/Developer/ETF && source venv-etf/bin/activate'
alias etfinfo='python ~/Developer/ETF/etfinfo.py'
```

Recharge :
```bash
source ~/.zshrc
```

## 🧹 Désactivation de l’environnement

```bash
deactivate
```

## ⚠️ Notes importantes

- Les données proviennent de Yahoo Finance  
- Certaines informations peuvent être absentes selon l’ETF  
- Les dividendes sont inclus par défaut  
- Les répartitions sectorielles suivent le format anglo-saxon  

## 👤 Auteur

Antoine — 2023–2025
