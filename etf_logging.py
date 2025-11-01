#!/usr/bin/python3
# etf_logging.py - Système de logging pour etfinfo

import logging
import os
from datetime import datetime

# Variable globale pour savoir si le debug est activé
_debug_enabled = False
_logger = None

def setup_logging(debug=False):
    """
    Configure le système de logging
    
    Args:
        debug: Si True, active le mode debug avec logs dans fichier
    """
    global _debug_enabled, _logger
    _debug_enabled = debug
    
    if not debug:
        # Mode normal : pas de logs
        logging.disable(logging.CRITICAL)
        return
    
    # Mode debug : créer le logger
    _logger = logging.getLogger('etfinfo')
    _logger.setLevel(logging.DEBUG)
    
    # Nom du fichier de log avec date
    log_filename = f"etfinfo-{datetime.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(os.getcwd(), log_filename)
    
    # Handler pour écrire dans le fichier
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Éviter les doublons de handlers
    _logger.handlers.clear()
    _logger.addHandler(file_handler)
    
    # Message d'initialisation
    _logger.info("=" * 80)
    _logger.info("Démarrage d'une nouvelle session etfinfo")
    _logger.info("=" * 80)
    
    print(f"📝 Mode debug activé - Logs dans : {log_path}")

def log_debug(message):
    """Log un message de niveau DEBUG"""
    if _debug_enabled and _logger:
        _logger.debug(message)

def log_info(message):
    """Log un message de niveau INFO"""
    if _debug_enabled and _logger:
        _logger.info(message)

def log_warning(message):
    """Log un message de niveau WARNING"""
    if _debug_enabled and _logger:
        _logger.warning(message)

def log_error(message):
    """Log un message de niveau ERROR"""
    if _debug_enabled and _logger:
        _logger.error(message)

def log_exception(message):
    """Log une exception avec traceback complet"""
    if _debug_enabled and _logger:
        _logger.exception(message)

def is_debug_enabled():
    """Retourne True si le mode debug est activé"""
    return _debug_enabled
