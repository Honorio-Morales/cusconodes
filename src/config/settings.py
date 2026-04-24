"""
Settings - Configuración global del proyecto CuscoNodes
"""

import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()


class Settings:
    """Configuración centralizada del proyecto"""

    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # URLs Base
    RPP_URL = os.getenv('RPP_URL', 'https://rpp.pe/cusco')
    PERURAIL_URL = os.getenv('PERURAIL_URL', 'https://www.perurail.com')

    # Configuración de Base de Datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./cusconodes.db')

    # Configuración de Email
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')

    # Configuración de Almacenamiento
    DATA_STORAGE_PATH = os.getenv('DATA_STORAGE_PATH', './data')
    RAW_DATA_PATH = os.path.join(DATA_STORAGE_PATH, 'raw')
    PROCESSED_DATA_PATH = os.path.join(DATA_STORAGE_PATH, 'processed')

    # Configuración del Proyecto
    PROJECT_ENV = os.getenv('PROJECT_ENV', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

    # Timeouts y Reintentos
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3

    @classmethod
    def configure_logging(cls):
        """Configura el sistema de logging del proyecto"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

