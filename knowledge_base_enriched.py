from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# Import RAG Engine (OBLIGATOIRE)
from rag_engine import RAGEngine

class EnrichedKnowledgeBase:
    """Enriched knowledge base for ALL Bolkiri restaurants"""
    
    def __init__(self):
        self.complete_file = "bolkiri_knowledge_industrial_2025.json"
        self.fallback_dir = "./data"
        self.data = self._load_complete_knowledge()
        
        # Adapt new structure
        self.restaurants = self.data.get('restaurants', [])
        self.menu_complet = self._extract_menu_from_pages()
        self.infos_generales = self.data.get('informations_generales', {})
        
        # For compatibility with old system
        self.documents = self._create_documents_from_pages()
        self.menu_items = self.menu_complet
        
        # Initialize RAG Engine (MANDATORY)
        print("Initialisation RAG Engine...")
        # force_rebuild from env variable (default: True in production)
        force_rebuild = os.getenv('REBUILD_EMBEDDINGS', 'true').lower() == 'true'
        self.rag_engine = RAGEngine(self.complete_file, force_rebuild=force_rebuild)
        print("RAG Engine active - Recherche semantique disponible")
        
        print(f"Base enrichie chargee: {len(self.restaurants)} restos, {len(self.menu_complet)} items menu")
    
    def _extract_menu_from_pages(self) -> List[Dict]:
        """Extract menu from scraped pages"""
        menu = []
        pages_categorie = self.data.get('pages_par_categorie', {})
        
        # Search in menu pages
        for page in pages_categorie.get('menu', []):
            content = page.get('content', '')
            # Parse content to extract dishes
            # For now, return basic structure
            if content:
                menu.append({
                    'nom': 'Menu Bolkiri',
                    'description': content[:500],
                    'prix': 'Variable'
                })
        
        return menu if menu else []
    
    def _create_documents_from_pages(self) -> List[Dict]:
        """Create documents from all scraped pages"""
        documents = []
        pages_categorie = self.data.get('pages_par_categorie', {})
        
        # Convert all pages to documents
        for category, pages in pages_categorie.items():
            for page in pages:
                if page.get('content'):
                    documents.append({
                        'url': page.get('url', ''),
                        'title': page.get('title', ''),
                        'text': page.get('content', ''),
                        'category': category
                    })
        
        return documents
    
    def _load_complete_knowledge(self) -> Dict:
        """Load complete knowledge base"""
        if os.path.exists(self.complete_file):
            try:
                with open(self.complete_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur chargement base complete: {e}")
        
        # Old system fallback
        return self._load_old_format()
    
    def _load_old_format(self) -> Dict:
        """Load old format for compatibility"""
        data = {'restaurants': [], 'menu_complet': [], 'infos_generales': {}}
        
        docs_file = os.path.join(self.fallback_dir, "documents.json")
        menu_file = os.path.join(self.fallback_dir, "menu.json")
        
        if os.path.exists(docs_file):
            with open(docs_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
        
        if os.path.exists(menu_file):
            with open(menu_file, 'r', encoding='utf-8') as f:
                data['menu_complet'] = json.load(f)
        
        return data
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Semantic search with RAG (mandatory)"""
        results = self.rag_engine.search(query, top_k=limit)
        
        # Format for compatibility with old format
        formatted_results = []
        for result in results:
            formatted_results.append({
                'type': result['type'],
                'content': result['content'],
                'score': result['score'],
                'metadata': result.get('metadata', {}),
                'data': result.get('data', {})
            })
        
        return formatted_results
    
    def get_all_restaurants(self) -> List[Dict]:
        """Return all restaurants"""
        return self.restaurants
    
    def _extract_ville_from_name(self, name: str) -> str:
        """Extract city from name 'BOLKIRI City Street Food Viêt'"""
        # Remove 'BOLKIRI' and 'Street Food Viêt'
        ville = name.replace('BOLKIRI', '').replace('Street Food Viêt', '').strip()
        return ville
    
    def get_restaurant_by_ville(self, ville: str) -> Optional[Dict]:
        """Find restaurant by city, department or postal code"""
        # Department → city mapping (normalized version)
        dept_mapping = {
            "91": "corbeil",  # Simplified for partial match
            "essonne": "corbeil",
            "94": "ivry",
            "val-de-marne": "ivry",
            "78": "mureaux",
            "yvelines": "mureaux",
            "77": "lagny",
            "seine-et-marne": "lagny"
        }
        
        ville_search = ville.lower().strip()
        
        # Search by department mapping
        if ville_search in dept_mapping:
            ville_search = dept_mapping[ville_search]
        
        # Search by postal code (91xxx → corbeil)
        if ville_search.startswith("91"):
            ville_search = "corbeil"
        elif ville_search.startswith("94"):
            ville_search = "ivry"
        elif ville_search.startswith("78"):
            ville_search = "mureaux"
        elif ville_search.startswith("77"):
            ville_search = "lagny"
        
        # Search restaurant (fuzzy matching with normalization)
        ville_lower = ville_search.lower()
        # Normalize for matching (remove hyphens and extra spaces)
        ville_normalized = ville_lower.replace('-', ' ').replace('  ', ' ').strip()
        # Also create version without spaces for partial word matching
        ville_compact = ville_normalized.replace(' ', '')
        
        for resto in self.restaurants:
            # Extract city from name and address
            resto_ville = self._extract_ville_from_name(resto.get('name', '')).lower()
            resto_adresse = resto.get('adresse', '').lower()
            
            # Normalize restaurant data
            resto_ville_normalized = resto_ville.replace('-', ' ').replace('  ', ' ').strip()
            resto_adresse_normalized = resto_adresse.replace('-', ' ')
            resto_ville_compact = resto_ville_normalized.replace(' ', '')
            
            # Multi-strategy matching:
            # 1. Exact or starts-with match (original)
            if ville_lower in resto_ville or resto_ville.startswith(ville_lower):
                return resto
            # 2. Normalized match (with spaces)
            if ville_normalized in resto_ville_normalized or resto_ville_normalized.startswith(ville_normalized):
                return resto
            # 3. Compact match (e.g., "ivrysurseine" matches "ivry")
            if resto_ville_compact in ville_compact or ville_compact.startswith(resto_ville_compact):
                return resto
            # 4. Address match
            if ville_lower in resto_adresse or ville_normalized in resto_adresse_normalized:
                return resto
        
        return None
    
    def get_all_menu_items(self, categorie: Optional[str] = None) -> List[Dict]:
        """Retourne tout le menu ou filtré par catégorie"""
        if categorie:
            return [p for p in self.menu_complet if p.get('categorie', '').lower() == categorie.lower()]
        return self.menu_complet
    
    def filter_menu(self, 
                    vegetarien: Optional[bool] = None,
                    vegan: Optional[bool] = None,
                    sans_gluten: Optional[bool] = None,
                    epice: Optional[str] = None,
                    prix_max: Optional[float] = None,
                    categorie: Optional[str] = None) -> List[Dict]:
        """Filtre le menu selon plusieurs critères"""
        results = self.menu_complet.copy()
        
        if vegetarien is not None:
            results = [p for p in results if p.get('vegetarien') == vegetarien]
        
        if vegan is not None:
            results = [p for p in results if p.get('vegan') == vegan]
        
        if sans_gluten is not None:
            results = [p for p in results if p.get('sans_gluten') == sans_gluten]
        
        if epice:
            results = [p for p in results if p.get('epice', '').lower() == epice.lower()]
        
        if prix_max:
            def extract_price(prix_str):
                try:
                    return float(prix_str.replace('€', '').replace(',', '.').strip())
                except:
                    return 999
            results = [p for p in results if extract_price(p.get('prix', '999€')) <= prix_max]
        
        if categorie:
            results = [p for p in results if p.get('categorie', '').lower() == categorie.lower()]
        
        return results
    
    def get_contact_info(self, ville: Optional[str] = None) -> Dict:
        """Return contact info (for restaurant or general)"""
        if ville:
            resto = self.get_restaurant_by_ville(ville)
            if resto:
                return {
                    'restaurant': resto['name'],
                    'ville': self._extract_ville_from_name(resto['name']),
                    'adresse': resto['adresse'],
                    'telephone': resto['telephone'],
                    'email': resto.get('email', 'N/A'),
                    'services': resto.get('services', []),
                    'url': resto.get('url', '')
                }
        
        # General info
        return {
            'entreprise': 'Bolkiri',
            'nombre_restaurants': len(self.restaurants),
            'villes': [self._extract_ville_from_name(r['name']) for r in self.restaurants],
            'contact_general': self.infos_generales.get('contact_general', {}),
            'restaurants': self.restaurants
        }
    
    def get_hours(self, ville: Optional[str] = None) -> Dict:
        """Return hours (for restaurant or all)"""
        if ville:
            resto = self.get_restaurant_by_ville(ville)
            if resto:
                return {
                    'restaurant': resto['name'],
                    'ville': self._extract_ville_from_name(resto['name']),
                    'horaires': resto.get('horaires', {})
                }
        
        # All hours
        return {
            'restaurants': [
                {
                    'name': r['name'],
                    'ville': self._extract_ville_from_name(r['name']),
                    'horaires': r.get('horaires', {})
                } for r in self.restaurants
            ]
        }
    
    def get_plats_signatures(self) -> List[Dict]:
        """Return signature dishes"""
        return [p for p in self.menu_complet if p.get('signature', False)]
    
    def get_info_generale(self, key: Optional[str] = None):
        """Return general info"""
        if key:
            return self.infos_generales.get(key)
        return self.infos_generales
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in km using Haversine formula"""
        R = 6371  # Earth radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def find_nearest_restaurant(self, ville_reference: str) -> Dict:
        """Find nearest restaurant to a reference city using geocoding
        
        Args:
            ville_reference: City name to find nearest restaurant from
            
        Returns:
            Dict with nearest restaurant info and distance
        """
        # First try to geocode the reference city
        import requests
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{ville_reference}, France",
                'format': 'json',
                'limit': 1
            }
            headers = {'User-Agent': 'BolkiriChatbot/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return {"error": f"Ville '{ville_reference}' non trouvée"}
            
            ref_lat = float(data[0]['lat'])
            ref_lon = float(data[0]['lon'])
            
        except Exception as e:
            return {"error": f"Erreur de géolocalisation: {str(e)}"}
        
        # Find nearest restaurant with coordinates
        nearest = None
        min_distance = float('inf')
        
        for resto in self.restaurants:
            coords = resto.get('coordinates')
            if not coords or not coords.get('lat') or not coords.get('lon'):
                continue
            
            distance = self.haversine_distance(
                ref_lat, ref_lon,
                coords['lat'], coords['lon']
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest = resto
        
        if not nearest:
            return {"error": "Aucun restaurant avec coordonnées GPS disponibles"}
        
        return {
            'restaurant': nearest['name'],
            'ville': self._extract_ville_from_name(nearest['name']),
            'adresse': nearest['adresse'],
            'distance_km': round(min_distance, 1),
            'telephone': nearest.get('telephone', ''),
            'url': nearest.get('url', '')
        }
    
    # Compatibility methods with old system
    def add_documents(self, documents: List[Dict]):
        """For compatibility - does nothing since enriched base is static"""
        pass
    
    def add_menu_items(self, menu_items: List[Dict]):
        """For compatibility - does nothing since enriched base is static"""
        pass
    
    def clear(self):
        """For compatibility - does nothing"""
        pass


# Alias for compatibility
KnowledgeBase = EnrichedKnowledgeBase
