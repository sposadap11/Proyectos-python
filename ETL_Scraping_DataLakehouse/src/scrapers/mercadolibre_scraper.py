"""
MercadoLibre Scraper Module - Competitive Price Intelligence Platform
Scraper específico para MercadoLibre
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

from .base_scraper import BaseScraper


class MercadoLibreScraper(BaseScraper):
    """Scraper específico para MercadoLibre."""
    
    def __init__(self, config: Dict[str, Any], competitor_name: str = "mercadolibre"):
        """Inicializar scraper de MercadoLibre."""
        super().__init__(config, competitor_name)
        
        # Configuración específica de MercadoLibre
        self.selectors = {
            'product_container': 'li.ui-search-layout__item',
            'product_title': 'h2.ui-search-item__title',
            'product_price': 'span.andes-money-amount__fraction',
            'product_original_price': 'span.andes-money-amount--previous',
            'product_rating': 'span.ui-search-reviews__rating-number',
            'product_reviews': 'span.ui-search-reviews__amount',
            'product_image': 'img.ui-search-result-image__element',
            'product_url': 'a.ui-search-item__group__element',
            'product_availability': 'span.ui-search-item__stock',
            'product_brand': 'span.ui-search-item__brand-discoverability',
            'product_category': 'span.ui-search-breadcrumb__title',
            'next_page': 'a.andes-pagination__link--next',
            'product_condition': 'span.ui-search-item__condition',
            'product_shipping': 'span.ui-search-item__shipping'
        }
        
        # Headers específicos para MercadoLibre
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _scrape_category(self, category: str) -> List[Dict[str, Any]]:
        """Scraping específico de una categoría en MercadoLibre."""
        self.logger.info(f"📂 Scraping categoría MercadoLibre: {category}")
        
        all_products = []
        page = 1
        
        while page <= self.max_pages:
            try:
                # Construir URL de búsqueda
                search_url = self._build_search_url(category, page)
                self.logger.info(f"🔍 Página {page}: {search_url}")
                
                # Realizar request
                response = self._make_request(search_url)
                if not response:
                    self.logger.warning(f"Error obteniendo página {page}")
                    break
                
                # Extraer productos de la página
                products = self._extract_products_from_page(response.text)
                
                if not products:
                    self.logger.info(f"No se encontraron productos en página {page}")
                    break
                
                all_products.extend(products)
                self.logger.info(f"✅ Página {page}: {len(products)} productos extraídos")
                
                # Verificar si hay siguiente página
                if not self._has_next_page(response.text):
                    self.logger.info("Última página alcanzada")
                    break
                
                page += 1
                
            except Exception as e:
                self.logger.error(f"Error en página {page}: {e}")
                break
        
        self.logger.info(f"🎯 Categoría {category}: {len(all_products)} productos totales")
        return all_products
    
    def _build_search_url(self, category: str, page: int) -> str:
        """Construir URL de búsqueda para MercadoLibre."""
        # Mapeo de categorías a categorías de MercadoLibre
        category_mapping = {
            'computacion': 'computacion',
            'libros': 'libros-revistas-comics',
            'hogar': 'hogar-muebles-jardin',
            'electronics': 'computacion',
            'books': 'libros-revistas-comics',
            'home': 'hogar-muebles-jardin'
        }
        
        mapped_category = category_mapping.get(category, category)
        
        # Construir URL base
        if page == 1:
            base_url = f"{self.base_url}/{mapped_category}"
        else:
            base_url = f"{self.base_url}/{mapped_category}/_Desde_{(page-1)*50+1}"
        
        return base_url
    
    def _extract_products_from_page(self, html_content: str) -> List[Dict[str, Any]]:
        """Extraer productos de una página HTML."""
        from bs4 import BeautifulSoup
        
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Encontrar contenedores de productos
        product_containers = soup.select(self.selectors['product_container'])
        
        for container in product_containers:
            try:
                product_data = self._extract_product_data(container)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                self.logger.warning(f"Error extrayendo producto: {e}")
                continue
        
        return products
    
    def _extract_product_data(self, product_element) -> Optional[Dict[str, Any]]:
        """Extraer datos de un producto específico de MercadoLibre."""
        try:
            # Extraer título
            title_elem = product_element.select_one(self.selectors['product_title'])
            title = self._clean_text(title_elem.get_text()) if title_elem else ""
            
            if not title:
                return None
            
            # Extraer precio
            price_elem = product_element.select_one(self.selectors['product_price'])
            price = self._extract_price(price_elem.get_text()) if price_elem else None
            
            # Extraer precio original
            original_price_elem = product_element.select_one(self.selectors['product_original_price'])
            original_price = self._extract_price(original_price_elem.get_text()) if original_price_elem else None
            
            # Extraer rating
            rating_elem = product_element.select_one(self.selectors['product_rating'])
            rating = self._extract_rating(rating_elem.get_text()) if rating_elem else None
            
            # Extraer número de reviews
            reviews_elem = product_element.select_one(self.selectors['product_reviews'])
            reviews_count = self._extract_reviews_count(reviews_elem.get_text()) if reviews_elem else 0
            
            # Extraer URL del producto
            url_elem = product_element.select_one(self.selectors['product_url'])
            product_url = urljoin(self.base_url, url_elem.get('href')) if url_elem else ""
            
            # Extraer imagen
            image_elem = product_element.select_one(self.selectors['product_image'])
            image_url = image_elem.get('src') if image_elem else ""
            
            # Extraer disponibilidad
            availability_elem = product_element.select_one(self.selectors['product_availability'])
            availability = self._extract_availability(availability_elem.get_text()) if availability_elem else True
            
            # Extraer marca
            brand_elem = product_element.select_one(self.selectors['product_brand'])
            brand = self._clean_text(brand_elem.get_text()) if brand_elem else ""
            
            # Extraer condición del producto
            condition_elem = product_element.select_one(self.selectors['product_condition'])
            condition = self._clean_text(condition_elem.get_text()) if condition_elem else ""
            
            # Extraer información de envío
            shipping_elem = product_element.select_one(self.selectors['product_shipping'])
            shipping_info = self._clean_text(shipping_elem.get_text()) if shipping_elem else ""
            
            # Extraer ML ID (MercadoLibre ID)
            ml_id = self._extract_ml_id(product_url)
            
            # Construir datos del producto
            product_data = {
                'id': ml_id or f"ml_{hash(title)}",
                'name': title,
                'price': price,
                'original_price': original_price,
                'currency': 'ARS',  # Peso argentino
                'rating': rating,
                'reviews_count': reviews_count,
                'brand': brand,
                'condition': condition,
                'shipping_info': shipping_info,
                'url': product_url,
                'image_url': image_url,
                'availability': availability,
                'competitor': self.competitor_name,
                'scraped_at': datetime.now().isoformat(),
                'raw_data': {
                    'title': title,
                    'price_text': price_elem.get_text() if price_elem else "",
                    'original_price_text': original_price_elem.get_text() if original_price_elem else "",
                    'rating_text': rating_elem.get_text() if rating_elem else "",
                    'reviews_text': reviews_elem.get_text() if reviews_elem else "",
                    'condition_text': condition_elem.get_text() if condition_elem else "",
                    'shipping_text': shipping_elem.get_text() if shipping_elem else ""
                }
            }
            
            return product_data
            
        except Exception as e:
            self.logger.warning(f"Error extrayendo datos de producto: {e}")
            return None
    
    def _extract_rating(self, rating_text: str) -> Optional[float]:
        """Extraer rating numérico del texto de MercadoLibre."""
        if not rating_text:
            return None
        
        try:
            # Buscar patrón de rating (ej: "4.5")
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                rating = float(match.group(1))
                return rating if 0 <= rating <= 5 else None
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _extract_reviews_count(self, reviews_text: str) -> int:
        """Extraer número de reviews del texto de MercadoLibre."""
        if not reviews_text:
            return 0
        
        try:
            # Buscar números en el texto
            numbers = re.findall(r'[\d,]+', reviews_text)
            if numbers:
                # Tomar el primer número encontrado
                count_str = numbers[0].replace(',', '').replace('.', '')
                return int(count_str)
            
            return 0
            
        except (ValueError, AttributeError):
            return 0
    
    def _extract_ml_id(self, product_url: str) -> Optional[str]:
        """Extraer ML ID de la URL del producto."""
        if not product_url:
            return None
        
        try:
            # Buscar ML ID en la URL (formato: MLM-XXXXXXXXX)
            match = re.search(r'MLM-(\d+)', product_url)
            if match:
                return f"MLM-{match.group(1)}"
            
            # Buscar otros formatos de ID
            match = re.search(r'/([A-Z]{2,3}-\d+)/', product_url)
            if match:
                return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    def _extract_availability(self, availability_text: str) -> bool:
        """Extraer información de disponibilidad."""
        if not availability_text:
            return True
        
        # Palabras que indican disponibilidad
        available_keywords = ['disponible', 'en stock', 'disponible', 'hay stock']
        unavailable_keywords = ['agotado', 'sin stock', 'no disponible', 'agotado']
        
        text_lower = availability_text.lower()
        
        for keyword in unavailable_keywords:
            if keyword in text_lower:
                return False
        
        return True
    
    def _has_next_page(self, html_content: str) -> bool:
        """Verificar si hay siguiente página."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        next_button = soup.select_one(self.selectors['next_page'])
        
        return next_button is not None and 'disabled' not in next_button.get('class', [])
    
    def _clean_text(self, text: str) -> str:
        """Limpieza específica para texto de MercadoLibre."""
        if not text:
            return ""
        
        # Limpieza básica
        text = super()._clean_text(text)
        
        # Remover caracteres específicos de MercadoLibre
        text = re.sub(r'\s+', ' ', text)  # Normalizar espacios
        text = text.replace('\n', ' ').replace('\r', ' ')  # Remover saltos de línea
        
        return text.strip()
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extracción específica de precios de MercadoLibre."""
        if not price_text:
            return None
        
        try:
            # Limpiar texto de precio
            price_text = price_text.replace('$', '').replace(',', '').replace('.', '').strip()
            
            # Buscar patrón de precio
            match = re.search(r'(\d+)', price_text)
            if match:
                return float(match.group(1))
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado específico del scraper de MercadoLibre."""
        status = super().get_status()
        status.update({
            'mercadolibre_specific': {
                'selectors_configured': len(self.selectors),
                'category_mapping': {
                    'computacion': 'computacion',
                    'libros': 'libros-revistas-comics',
                    'hogar': 'hogar-muebles-jardin'
                },
                'currency': 'ARS'
            }
        })
        return status 