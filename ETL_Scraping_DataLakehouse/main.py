#!/usr/bin/env python3
"""
Competitive Price Intelligence Platform - Main Script
Sistema completo de scraping, procesamiento y análisis de precios de competencia
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.scrapers.scraper_manager import ScraperManager
from src.transformers.data_transformer import DataTransformer
from src.loaders.data_loader import DataLoader
from src.analytics.price_analyzer import PriceAnalyzer
from src.utils.report_generator import ReportGenerator
from src.orchestration.workflow_manager import WorkflowManager


class CompetitivePriceIntelligence:
    """Clase principal del sistema de inteligencia de precios competitivos."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Inicializar el sistema de inteligencia de precios."""
        self.config = ConfigLoader(config_path)
        self.logger = setup_logger()
        
        # Inicializar componentes
        self.scraper_manager = ScraperManager(self.config)
        self.transformer = DataTransformer(self.config)
        self.loader = DataLoader(self.config)
        self.analyzer = PriceAnalyzer(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.workflow_manager = WorkflowManager(self.config)
        
        self.logger.info("🚀 Sistema de Inteligencia de Precios Competitivos inicializado")
    
    def run_full_pipeline(self) -> bool:
        """Ejecutar el pipeline completo de inteligencia de precios."""
        self.logger.info("🎯 Iniciando Pipeline Completo de Inteligencia de Precios")
        
        try:
            # Etapa 1: Scraping de datos
            self.logger.info("📥 Etapa 1: Scraping de datos de competidores")
            scraped_data = self.scraper_manager.scrape_all_competitors()
            
            if not scraped_data:
                self.logger.error("❌ No se pudieron extraer datos de competidores")
                return False
            
            # Etapa 2: Transformación de datos
            self.logger.info("🔄 Etapa 2: Transformación y limpieza de datos")
            transformed_data = self.transformer.transform_all(scraped_data)
            
            # Etapa 3: Carga en data lakehouse
            self.logger.info("📤 Etapa 3: Carga en data lakehouse")
            load_success = self.loader.load_all(transformed_data)
            
            if not load_success:
                self.logger.error("❌ Error al cargar datos en data lakehouse")
                return False
            
            # Etapa 4: Análisis de precios
            self.logger.info("📊 Etapa 4: Análisis de precios y competitividad")
            analysis_results = self.analyzer.analyze_competitiveness()
            
            # Etapa 5: Generación de reportes
            self.logger.info("📋 Etapa 5: Generación de reportes y alertas")
            self.report_generator.generate_all_reports(analysis_results)
            
            # Etapa 6: Envío de alertas
            self.logger.info("🔔 Etapa 6: Envío de alertas y notificaciones")
            self._send_alerts(analysis_results)
            
            self.logger.info("✅ Pipeline completo ejecutado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en el pipeline completo: {str(e)}")
            return False
    
    def run_scraping_only(self) -> Optional[Dict[str, Any]]:
        """Ejecutar solo el scraping de datos."""
        self.logger.info("📥 Ejecutando solo scraping de datos")
        try:
            scraped_data = self.scraper_manager.scrape_all_competitors()
            self.logger.info(f"✅ Scraping completado: {len(scraped_data)} fuentes procesadas")
            return scraped_data
        except Exception as e:
            self.logger.error(f"❌ Error en scraping: {str(e)}")
            return None
    
    def run_analysis_only(self) -> Optional[Dict[str, Any]]:
        """Ejecutar solo el análisis de precios."""
        self.logger.info("📊 Ejecutando solo análisis de precios")
        try:
            analysis_results = self.analyzer.analyze_competitiveness()
            self.logger.info("✅ Análisis de precios completado")
            return analysis_results
        except Exception as e:
            self.logger.error(f"❌ Error en análisis: {str(e)}")
            return None
    
    def run_reporting_only(self) -> bool:
        """Ejecutar solo la generación de reportes."""
        self.logger.info("📋 Ejecutando solo generación de reportes")
        try:
            # Obtener análisis reciente
            analysis_results = self.analyzer.analyze_competitiveness()
            self.report_generator.generate_all_reports(analysis_results)
            self.logger.info("✅ Reportes generados exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error en generación de reportes: {str(e)}")
            return False
    
    def run_competitor_analysis(self, competitor: str) -> bool:
        """Ejecutar análisis específico de un competidor."""
        self.logger.info(f"🎯 Ejecutando análisis específico para: {competitor}")
        try:
            # Scraping específico
            competitor_data = self.scraper_manager.scrape_competitor(competitor)
            
            if not competitor_data:
                self.logger.error(f"❌ No se pudieron extraer datos de {competitor}")
                return False
            
            # Transformación
            transformed_data = self.transformer.transform_competitor_data(competitor_data)
            
            # Carga
            self.loader.load_competitor_data(transformed_data)
            
            # Análisis específico
            analysis = self.analyzer.analyze_competitor(competitor)
            
            # Reporte específico
            self.report_generator.generate_competitor_report(competitor, analysis)
            
            self.logger.info(f"✅ Análisis de {competitor} completado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en análisis de {competitor}: {str(e)}")
            return False
    
    def run_price_monitoring(self) -> bool:
        """Ejecutar monitoreo continuo de precios."""
        self.logger.info("👀 Iniciando monitoreo continuo de precios")
        try:
            # Configurar monitoreo
            monitoring_config = self.config.get('monitoring', {})
            check_interval = monitoring_config.get('check_interval_minutes', 30)
            
            self.logger.info(f"⏰ Monitoreo configurado para verificar cada {check_interval} minutos")
            
            # Iniciar monitoreo
            self.workflow_manager.start_price_monitoring(
                interval_minutes=check_interval,
                callback=self._price_change_callback
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en monitoreo de precios: {str(e)}")
            return False
    
    def run_data_quality_check(self) -> bool:
        """Ejecutar verificación de calidad de datos."""
        self.logger.info("🔍 Ejecutando verificación de calidad de datos")
        try:
            # Verificar datos raw
            raw_quality = self.transformer.validate_raw_data()
            
            # Verificar datos procesados
            processed_quality = self.transformer.validate_processed_data()
            
            # Verificar datos analíticos
            analytics_quality = self.analyzer.validate_analytics_data()
            
            # Generar reporte de calidad
            quality_report = {
                'raw_data': raw_quality,
                'processed_data': processed_quality,
                'analytics_data': analytics_quality,
                'timestamp': datetime.now().isoformat()
            }
            
            self.report_generator.generate_quality_report(quality_report)
            
            self.logger.info("✅ Verificación de calidad completada")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en verificación de calidad: {str(e)}")
            return False
    
    def run_performance_optimization(self) -> bool:
        """Ejecutar optimización de rendimiento."""
        self.logger.info("⚡ Ejecutando optimización de rendimiento")
        try:
            # Optimizar base de datos
            self.loader.optimize_database()
            
            # Optimizar índices
            self.loader.optimize_indexes()
            
            # Limpiar datos antiguos
            self.loader.cleanup_old_data()
            
            # Optimizar cache
            self.analyzer.optimize_cache()
            
            self.logger.info("✅ Optimización de rendimiento completada")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en optimización: {str(e)}")
            return False
    
    def _send_alerts(self, analysis_results: Dict[str, Any]) -> None:
        """Enviar alertas basadas en el análisis."""
        try:
            # Detectar cambios significativos
            significant_changes = self.analyzer.detect_significant_changes(analysis_results)
            
            if significant_changes:
                self.logger.info(f"🔔 Enviando {len(significant_changes)} alertas")
                
                for alert in significant_changes:
                    self.workflow_manager.send_alert(alert)
            else:
                self.logger.info("✅ No se detectaron cambios significativos")
                
        except Exception as e:
            self.logger.error(f"❌ Error al enviar alertas: {str(e)}")
    
    def _price_change_callback(self, price_change: Dict[str, Any]) -> None:
        """Callback para cambios de precios detectados."""
        try:
            self.logger.info(f"💰 Cambio de precio detectado: {price_change}")
            
            # Enviar alerta inmediata
            self.workflow_manager.send_immediate_alert(price_change)
            
            # Actualizar análisis
            self.analyzer.update_analysis_with_change(price_change)
            
        except Exception as e:
            self.logger.error(f"❌ Error en callback de cambio de precio: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema."""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'scrapers': self.scraper_manager.get_status(),
                'database': self.loader.get_database_status(),
                'analysis': self.analyzer.get_analysis_status(),
                'monitoring': self.workflow_manager.get_monitoring_status(),
                'last_run': self._get_last_run_info()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Error al obtener estado del sistema: {str(e)}")
            return {'error': str(e)}
    
    def _get_last_run_info(self) -> Dict[str, Any]:
        """Obtener información de la última ejecución."""
        try:
            # Leer archivo de estado
            status_file = Path("logs/last_run.json")
            if status_file.exists():
                import json
                with open(status_file, 'r') as f:
                    return json.load(f)
            else:
                return {'status': 'No previous runs found'}
                
        except Exception as e:
            return {'error': str(e)}


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Competitive Price Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --full-pipeline                    # Pipeline completo
  python main.py --scrape-only                      # Solo scraping
  python main.py --analysis-only                    # Solo análisis
  python main.py --reporting-only                   # Solo reportes
  python main.py --competitor amazon                # Análisis específico
  python main.py --monitoring                       # Monitoreo continuo
  python main.py --quality-check                    # Verificación de calidad
  python main.py --optimize                         # Optimización
  python main.py --status                           # Estado del sistema
  python main.py --config custom_config.yaml        # Configuración personalizada
        """
    )
    
    parser.add_argument(
        "--full-pipeline",
        action="store_true",
        help="Ejecutar pipeline completo"
    )
    
    parser.add_argument(
        "--scrape-only",
        action="store_true",
        help="Ejecutar solo scraping de datos"
    )
    
    parser.add_argument(
        "--analysis-only",
        action="store_true",
        help="Ejecutar solo análisis de precios"
    )
    
    parser.add_argument(
        "--reporting-only",
        action="store_true",
        help="Ejecutar solo generación de reportes"
    )
    
    parser.add_argument(
        "--competitor",
        type=str,
        help="Ejecutar análisis específico de competidor (amazon, mercadolibre, ebay)"
    )
    
    parser.add_argument(
        "--monitoring",
        action="store_true",
        help="Iniciar monitoreo continuo de precios"
    )
    
    parser.add_argument(
        "--quality-check",
        action="store_true",
        help="Ejecutar verificación de calidad de datos"
    )
    
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Ejecutar optimización de rendimiento"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Mostrar estado del sistema"
    )
    
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Ruta al archivo de configuración"
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
    
    # Crear instancia del sistema
    system = CompetitivePriceIntelligence(args.config)
    
    # Ejecutar según argumentos
    success = False
    
    if args.full_pipeline:
        success = system.run_full_pipeline()
    elif args.scrape_only:
        success = system.run_scraping_only() is not None
    elif args.analysis_only:
        success = system.run_analysis_only() is not None
    elif args.reporting_only:
        success = system.run_reporting_only()
    elif args.competitor:
        success = system.run_competitor_analysis(args.competitor)
    elif args.monitoring:
        success = system.run_price_monitoring()
    elif args.quality_check:
        success = system.run_data_quality_check()
    elif args.optimize:
        success = system.run_performance_optimization()
    elif args.status:
        status = system.get_system_status()
        import json
        print(json.dumps(status, indent=2))
        success = True
    else:
        # Por defecto, ejecutar pipeline completo
        success = system.run_full_pipeline()
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 