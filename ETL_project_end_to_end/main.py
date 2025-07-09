#!/usr/bin/env python3
"""
Script principal del Pipeline ETL para Análisis de E-commerce
Autor: Tu Nombre
Fecha: 2024
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.extractors.data_extractor import DataExtractor
from src.transformers.data_transformer import DataTransformer
from src.loaders.data_loader import DataLoader
from src.utils.report_generator import ReportGenerator


class ETLPipeline:
    """Clase principal que orquesta el pipeline ETL completo."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Inicializar el pipeline ETL."""
        self.config = ConfigLoader(config_path)
        self.logger = setup_logger()
        self.extractor = DataExtractor(self.config)
        self.transformer = DataTransformer(self.config)
        self.loader = DataLoader(self.config)
        self.report_generator = ReportGenerator(self.config)
        
    def run_full_pipeline(self):
        """Ejecutar el pipeline ETL completo."""
        self.logger.info("🚀 Iniciando Pipeline ETL Completo")
        
        try:
            # Etapa 1: Extracción
            self.logger.info("📥 Etapa 1: Extracción de datos")
            raw_data = self.extractor.extract_all()
            
            # Etapa 2: Transformación
            self.logger.info("🔄 Etapa 2: Transformación de datos")
            processed_data = self.transformer.transform_all(raw_data)
            
            # Etapa 3: Carga
            self.logger.info("📤 Etapa 3: Carga de datos")
            self.loader.load_all(processed_data)
            
            # Etapa 4: Generación de reportes
            self.logger.info("📊 Etapa 4: Generación de reportes")
            self.report_generator.generate_all_reports()
            
            self.logger.info("✅ Pipeline ETL completado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en el pipeline ETL: {str(e)}")
            return False
    
    def run_extract_only(self):
        """Ejecutar solo la etapa de extracción."""
        self.logger.info("📥 Ejecutando solo extracción de datos")
        try:
            raw_data = self.extractor.extract_all()
            self.logger.info("✅ Extracción completada exitosamente")
            return raw_data
        except Exception as e:
            self.logger.error(f"❌ Error en extracción: {str(e)}")
            return None
    
    def run_transform_only(self):
        """Ejecutar solo la etapa de transformación."""
        self.logger.info("🔄 Ejecutando solo transformación de datos")
        try:
            # Primero extraer datos
            raw_data = self.extractor.extract_all()
            processed_data = self.transformer.transform_all(raw_data)
            self.logger.info("✅ Transformación completada exitosamente")
            return processed_data
        except Exception as e:
            self.logger.error(f"❌ Error en transformación: {str(e)}")
            return None
    
    def run_load_only(self):
        """Ejecutar solo la etapa de carga."""
        self.logger.info("📤 Ejecutando solo carga de datos")
        try:
            # Primero extraer y transformar datos
            raw_data = self.extractor.extract_all()
            processed_data = self.transformer.transform_all(raw_data)
            self.loader.load_all(processed_data)
            self.logger.info("✅ Carga completada exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error en carga: {str(e)}")
            return False


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Pipeline ETL para Análisis de E-commerce",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                    # Ejecutar pipeline completo
  python main.py --stage extract    # Solo extracción
  python main.py --stage transform  # Solo transformación
  python main.py --stage load       # Solo carga
  python main.py --config custom_config.yaml  # Usar configuración personalizada
        """
    )
    
    parser.add_argument(
        "--stage",
        choices=["extract", "transform", "load", "full"],
        default="full",
        help="Etapa del pipeline a ejecutar (default: full)"
    )
    
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Ruta al archivo de configuración (default: config/config.yaml)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Modo verbose para más información"
    )
    
    args = parser.parse_args()
    
    # Configurar logging según nivel de verbosidad
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Crear instancia del pipeline
    pipeline = ETLPipeline(args.config)
    
    # Ejecutar según la etapa especificada
    success = False
    
    if args.stage == "extract":
        success = pipeline.run_extract_only() is not None
    elif args.stage == "transform":
        success = pipeline.run_transform_only() is not None
    elif args.stage == "load":
        success = pipeline.run_load_only()
    else:  # full
        success = pipeline.run_full_pipeline()
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 