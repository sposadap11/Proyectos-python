#!/usr/bin/env python3
"""
Script de ejemplo para ejecutar el pipeline ETL completo.
Este script demuestra cómo usar el proyecto ETL paso a paso.
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.extractors.data_extractor import DataExtractor
from src.transformers.data_transformer import DataTransformer
from src.loaders.data_loader import DataLoader
from src.utils.report_generator import ReportGenerator


def main():
    """Función principal del script de ejemplo."""
    print("🚀 Iniciando Pipeline ETL de Ejemplo")
    print("=" * 50)
    
    # Configurar logging
    logger = setup_logger()
    
    try:
        # 1. Cargar configuración
        print("📋 Paso 1: Cargando configuración...")
        config = ConfigLoader("config/config.yaml")
        print(f"✅ Configuración cargada: {config.get('project.name')}")
        
        # 2. Extraer datos
        print("\n📥 Paso 2: Extrayendo datos...")
        extractor = DataExtractor(config)
        raw_data = extractor.extract_all()
        print(f"✅ Datos extraídos de {len(raw_data)} fuentes")
        
        for source, df in raw_data.items():
            print(f"   - {source}: {len(df)} registros")
        
        # 3. Transformar datos
        print("\n🔄 Paso 3: Transformando datos...")
        transformer = DataTransformer(config)
        transformed_data = transformer.transform_all(raw_data)
        print(f"✅ Datos transformados: {len(transformed_data)} tablas")
        
        # Mostrar algunas transformaciones
        if 'ventas' in transformed_data:
            ventas_df = transformed_data['ventas']
            print(f"   - Ventas: {len(ventas_df)} registros")
            if 'mes' in ventas_df.columns:
                print(f"   - Columnas agregadas: mes, año, dia_semana")
        
        # 4. Cargar datos
        print("\n📤 Paso 4: Cargando datos en base de datos...")
        loader = DataLoader(config)
        success = loader.load_all(transformed_data)
        
        if success:
            print("✅ Datos cargados exitosamente en la base de datos")
            
            # Mostrar información de las tablas
            for table_name in ['ventas', 'productos', 'clientes']:
                table_info = loader.get_table_info(table_name)
                if table_info:
                    print(f"   - Tabla {table_name}: {table_info['registros']} registros")
        else:
            print("❌ Error al cargar datos")
            return
        
        # 5. Generar reportes
        print("\n📊 Paso 5: Generando reportes...")
        report_generator = ReportGenerator(config)
        report_success = report_generator.generate_all_reports()
        
        if report_success:
            print("✅ Reportes generados exitosamente")
            print("   - Gráficos guardados en data/reports/")
            print("   - Reporte HTML: data/reports/reporte_completo.html")
        else:
            print("❌ Error al generar reportes")
        
        # 6. Ejecutar consultas de ejemplo
        print("\n🔍 Paso 6: Ejecutando consultas de ejemplo...")
        
        # Consulta 1: Top 5 productos más vendidos
        query1 = """
        SELECT vpp.nombre_producto, vpp.total_ventas, vpp.num_ventas
        FROM ventas_por_producto vpp
        ORDER BY vpp.total_ventas DESC
        LIMIT 5
        """
        result1 = loader.execute_query(query1)
        if result1 is not None and not result1.empty:
            print("   Top 5 productos más vendidos:")
            for _, row in result1.iterrows():
                print(f"     - {row['nombre_producto']}: {row['total_ventas']:.2f}€ ({row['num_ventas']} ventas)")
        
        # Consulta 2: Ventas totales por categoría
        query2 = """
        SELECT categoria, total_ventas, num_ventas
        FROM ventas_por_categoria
        ORDER BY total_ventas DESC
        """
        result2 = loader.execute_query(query2)
        if result2 is not None and not result2.empty:
            print("   Ventas por categoría:")
            for _, row in result2.iterrows():
                print(f"     - {row['categoria']}: {row['total_ventas']:.2f}€ ({row['num_ventas']} ventas)")
        
        # Consulta 3: Ticket promedio
        query3 = "SELECT AVG(total) as ticket_promedio FROM ventas"
        result3 = loader.execute_query(query3)
        if result3 is not None and not result3.empty:
            ticket_promedio = result3['ticket_promedio'].iloc[0]
            print(f"   Ticket promedio: {ticket_promedio:.2f}€")
        
        print("\n" + "=" * 50)
        print("🎉 Pipeline ETL completado exitosamente!")
        print("\n📁 Archivos generados:")
        print(f"   - Base de datos: {config.get('database.path')}")
        print(f"   - Reportes: {config.get('paths.data_reports')}")
        print(f"   - Logs: {config.get('paths.logs')}")
        
        print("\n📖 Próximos pasos:")
        print("   1. Revisar los reportes generados en data/reports/")
        print("   2. Explorar la base de datos con herramientas como DB Browser for SQLite")
        print("   3. Personalizar la configuración en config/config.yaml")
        print("   4. Agregar más fuentes de datos según tus necesidades")
        
    except Exception as e:
        logger.error(f"Error en el pipeline: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 