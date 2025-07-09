#!/usr/bin/env python3
"""
Competitive Price Intelligence Platform - Example Script
Script de ejemplo para demostrar el uso del sistema
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Función principal del script de ejemplo."""
    print("🚀 Competitive Price Intelligence Platform - Ejemplo de Uso")
    print("=" * 60)
    
    try:
        # Importar componentes principales
        from src.utils.config_loader import ConfigLoader
        from src.scrapers.scraper_manager import ScraperManager
        from src.utils.logger import setup_logger
        
        print("📋 Paso 1: Cargando configuración...")
        
        # Cargar configuración
        config = ConfigLoader("config/config.yaml")
        logger = setup_logger()
        
        print("✅ Configuración cargada exitosamente")
        print(f"   - Competidores habilitados: {config.get_enabled_competitors()}")
        print(f"   - Categorías configuradas: {config.get('scraping.competitors.amazon.categories', [])}")
        
        print("\n📥 Paso 2: Inicializando gestor de scrapers...")
        
        # Inicializar gestor de scrapers
        scraper_manager = ScraperManager(config)
        
        print("✅ Gestor de scrapers inicializado")
        print(f"   - Scrapers disponibles: {scraper_manager.get_available_competitors()}")
        print(f"   - Scrapers habilitados: {scraper_manager.get_enabled_competitors()}")
        
        print("\n🔍 Paso 3: Ejecutando scraping de prueba...")
        
        # Ejecutar scraping de prueba
        print("   Ejecutando scraping con datos de prueba...")
        
        # Usar scraper de prueba si está disponible
        if 'mock' in scraper_manager.get_available_competitors():
            print("   Usando scraper de prueba (mock)...")
            results = scraper_manager.run_test_scraping('mock')
            
            if results.get('success'):
                print(f"   ✅ Scraping de prueba exitoso: {results.get('products_count', 0)} productos")
            else:
                print(f"   ❌ Error en scraping de prueba: {results.get('error', 'Error desconocido')}")
        else:
            print("   No hay scraper de prueba disponible")
            print("   Para usar scrapers reales, configura las credenciales necesarias")
        
        print("\n📊 Paso 4: Mostrando métricas del sistema...")
        
        # Obtener métricas
        metrics = scraper_manager.get_scraping_metrics()
        
        print("   Métricas del sistema:")
        print(f"   - Total de scrapers: {metrics.get('total_scrapers', 0)}")
        print(f"   - Scrapers habilitados: {metrics.get('enabled_scrapers', 0)}")
        
        last_scraping = metrics.get('last_scraping', {})
        if 'status' in last_scraping:
            print(f"   - Último scraping: {last_scraping['status']}")
        else:
            print(f"   - Último scraping: {last_scraping.get('total_products', 0)} productos")
        
        print("\n🎯 Paso 5: Demostrando funcionalidades...")
        
        # Mostrar estado de scrapers
        print("   Estado de scrapers:")
        scrapers_status = scraper_manager.get_all_scrapers_status()
        
        for competitor, status in scrapers_status.items():
            print(f"   - {competitor}: {status.get('status', 'unknown')}")
        
        print("\n📋 Paso 6: Información de configuración...")
        
        # Mostrar información de configuración
        print("   Configuración del sistema:")
        print(f"   - Base de datos: {config.get('database.type', 'N/A')}")
        print(f"   - Almacenamiento: {config.get('storage.type', 'N/A')}")
        print(f"   - Delay de scraping: {config.get('scraping.delay', 'N/A')} segundos")
        print(f"   - Timeout: {config.get('scraping.timeout', 'N/A')} segundos")
        
        print("\n🔧 Paso 7: Comandos disponibles...")
        
        print("   Comandos principales:")
        print("   python main.py --full-pipeline                    # Pipeline completo")
        print("   python main.py --scrape-only                      # Solo scraping")
        print("   python main.py --analysis-only                    # Solo análisis")
        print("   python main.py --reporting-only                   # Solo reportes")
        print("   python main.py --competitor amazon                # Análisis específico")
        print("   python main.py --monitoring                       # Monitoreo continuo")
        print("   python main.py --quality-check                    # Verificación de calidad")
        print("   python main.py --optimize                         # Optimización")
        print("   python main.py --status                           # Estado del sistema")
        
        print("\n🐳 Paso 8: Información de Docker...")
        
        print("   Para ejecutar con Docker:")
        print("   docker-compose up -d                              # Levantar servicios")
        print("   docker-compose logs -f                            # Ver logs")
        print("   docker-compose down                               # Detener servicios")
        
        print("\n📚 Paso 9: Documentación...")
        
        print("   Recursos disponibles:")
        print("   - README.md: Documentación principal")
        print("   - DOCUMENTACION.md: Documentación técnica detallada")
        print("   - config/config.yaml: Configuración del sistema")
        print("   - env.example: Variables de entorno de ejemplo")
        
        print("\n🎉 ¡Ejemplo completado exitosamente!")
        print("\n💡 Próximos pasos:")
        print("   1. Configura las variables de entorno (copia env.example a .env)")
        print("   2. Instala las dependencias: pip install -r requirements.txt")
        print("   3. Ejecuta el pipeline completo: python main.py --full-pipeline")
        print("   4. Accede a los dashboards:")
        print("      - Airflow: http://localhost:8080")
        print("      - Grafana: http://localhost:3000")
        print("      - MinIO: http://localhost:9001")
        print("      - API: http://localhost:8000")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("   Asegúrate de haber instalado las dependencias:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("   Revisa la configuración y los logs para más detalles")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 