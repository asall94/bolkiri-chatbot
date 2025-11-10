from typing import List, Dict, Optional
import json
import os
from datetime import datetime

# Import RAG Engine
try:
    from rag_engine import RAGEngine
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG Engine non disponible, utilisation du mode recherche classique")

class EnrichedKnowledgeBase:
    """Base de connaissances enrichie pour TOUS les restaurants Bolkiri"""
    
    def __init__(self):
        self.complete_file = "bolkiri_knowledge_industrial_2025.json"
        self.fallback_dir = "./data"
        self.data = self._load_complete_knowledge()
        
        # Adapter la nouvelle structure
        self.restaurants = self.data.get('restaurants', [])
        self.menu_complet = self._extract_menu_from_pages()
        self.infos_generales = self.data.get('informations_generales', {})
        
        # Pour compatibilité avec l'ancien système
        self.documents = self._create_documents_from_pages()
        self.menu_items = self.menu_complet
        
        # Initialiser RAG Engine si disponible
        self.rag_engine = None
        if RAG_AVAILABLE:
            try:
                print("🚀 Initialisation RAG Engine...")
                self.rag_engine = RAGEngine(self.complete_file)
                print("✅ RAG Engine activé - Recherche sémantique disponible")
            except Exception as e:
                print(f"⚠️ Erreur initialisation RAG: {e}")
                print("Utilisation du mode recherche classique")
        
        print(f"Base enrichie chargée: {len(self.restaurants)} restos, {len(self.menu_complet)} items menu")
    
    def _extract_menu_from_pages(self) -> List[Dict]:
        """Extrait le menu depuis les pages scrapées"""
        menu = []
        pages_categorie = self.data.get('pages_par_categorie', {})
        
        # Chercher dans les pages menu
        for page in pages_categorie.get('menu', []):
            content = page.get('content', '')
            # Parser le contenu pour extraire les plats
            # Pour l'instant, retourner une structure basique
            if content:
                menu.append({
                    'nom': 'Menu Bolkiri',
                    'description': content[:500],
                    'prix': 'Variable'
                })
        
        return menu if menu else []
    
    def _create_documents_from_pages(self) -> List[Dict]:
        """Crée des documents depuis toutes les pages scrapées"""
        documents = []
        pages_categorie = self.data.get('pages_par_categorie', {})
        
        # Convertir toutes les pages en documents
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
        """Charge la base de connaissances complète"""
        if os.path.exists(self.complete_file):
            try:
                with open(self.complete_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Erreur chargement base complète: {e}")
        
        # Fallback ancien système
        return self._load_old_format()
    
    def _load_old_format(self) -> Dict:
        """Charge l'ancien format pour compatibilité"""
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
        """Recherche enrichie dans toute la base (RAG si disponible, sinon classique)"""
        
        # Utiliser RAG si disponible
        if self.rag_engine:
            return self._search_rag(query, limit)
        
        # Sinon fallback sur recherche classique
        return self._search_classic(query, limit)
    
    def _search_rag(self, query: str, limit: int = 5) -> List[Dict]:
        """Recherche sémantique avec RAG"""
        try:
            results = self.rag_engine.search(query, top_k=limit)
            
            # Formater pour compatibilité avec l'ancien format
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
        except Exception as e:
            print(f"⚠️ Erreur RAG search: {e}")
            return self._search_classic(query, limit)
    
    def _search_classic(self, query: str, limit: int = 5) -> List[Dict]:
        """Recherche classique par mots-clés (fallback)"""
        query_lower = query.lower()
        results = []
        
        # Si question sur les villes/localisations, augmenter limit pour montrer tous les restos
        location_keywords = ['ville', 'où', 'localise', 'situe', 'adresse', 'implanté', 'trouvez-vous', 'présent']
        is_location_query = any(word in query_lower for word in location_keywords)
        
        # Recherche dans les restaurants
        for resto in self.restaurants:
            score = 0
            name = resto.get('name', '')
            adresse = resto.get('adresse', '')
            
            # Extraire la ville depuis l'adresse ou le nom
            ville = ''
            if 'name' in resto and resto['name']:
                # Extraire après "BOLKIRI"
                parts = name.split()
                if len(parts) > 1:
                    ville = ' '.join(parts[1:]).replace('Street Food Viêt', '').strip()
            
            if query_lower in ville.lower():
                score += 10
            if query_lower in name.lower():
                score += 10
            if query_lower in adresse.lower():
                score += 5
            
            # Mots-clés recherche de villes
            if is_location_query:
                if ville or adresse:
                    score += 5
            
            if score > 0:
                results.append({
                    'type': 'restaurant',
                    'content': f"Restaurant {name} situé à {adresse}. Tél: {resto.get('telephone', 'N/A')}",
                    'score': score,
                    'data': resto
                })
        
        # Recherche dans les documents (pages scrapées)
        for doc in self.documents:
            score = 0
            if query_lower in doc.get('text', '').lower():
                score += 5
            if query_lower in doc.get('title', '').lower():
                score += 3
            
            if score > 0:
                results.append({
                    'type': 'document',
                    'content': doc.get('text', '')[:500],
                    'score': score,
                    'data': doc
                })
        
        # Trier par score et limiter
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Si question sur les villes, retourner tous les restaurants trouvés
        if is_location_query:
            return results
        
        return results[:limit]
    
    def get_all_restaurants(self) -> List[Dict]:
        """Retourne tous les restaurants"""
        return self.restaurants
    
    def get_restaurant_by_ville(self, ville: str) -> Optional[Dict]:
        """Trouve un restaurant par ville, département ou code postal"""
        # Mapping département → ville (version normalisée)
        dept_mapping = {
            "91": "corbeil",  # Simplifié pour match partiel
            "essonne": "corbeil",
            "94": "ivry",
            "val-de-marne": "ivry",
            "78": "mureaux",
            "yvelines": "mureaux",
            "77": "lagny",
            "seine-et-marne": "lagny"
        }
        
        ville_search = ville.lower().strip()
        
        # Chercher par mapping département
        if ville_search in dept_mapping:
            ville_search = dept_mapping[ville_search]
        
        # Chercher par code postal (91xxx → corbeil)
        if ville_search.startswith("91"):
            ville_search = "corbeil"
        elif ville_search.startswith("94"):
            ville_search = "ivry"
        elif ville_search.startswith("78"):
            ville_search = "mureaux"
        elif ville_search.startswith("77"):
            ville_search = "lagny"
        
        # Chercher le restaurant (match partiel plus permissif)
        ville_lower = ville_search.lower()
        for resto in self.restaurants:
            resto_ville = resto.get('ville', '').lower()
            resto_cp = resto.get('code_postal', '').lower()
            
            # Match partiel sur ville ou code postal
            if ville_lower in resto_ville or resto_ville.startswith(ville_lower):
                return resto
            if ville_lower in resto_cp or resto_cp.startswith(ville_lower):
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
        """Retourne les infos de contact (d'un restaurant ou général)"""
        if ville:
            resto = self.get_restaurant_by_ville(ville)
            if resto:
                return {
                    'restaurant': resto['name'],
                    'adresse': resto['adresse'],
                    'telephone': resto['telephone'],
                    'email': resto['email'],
                    'services': resto.get('services', [])
                }
        
        # Info générale
        return {
            'entreprise': 'Bolkiri',
            'nombre_restaurants': len(self.restaurants),
            'villes': [r['ville'] for r in self.restaurants],
            'contact_general': self.infos_generales.get('contact_general', {}),
            'restaurants': self.restaurants
        }
    
    def get_hours(self, ville: Optional[str] = None) -> Dict:
        """Retourne les horaires (d'un restaurant ou tous)"""
        if ville:
            resto = self.get_restaurant_by_ville(ville)
            if resto:
                return {
                    'restaurant': resto['name'],
                    'ville': resto['ville'],
                    'horaires': resto.get('horaires', {})
                }
        
        # Tous les horaires
        return {
            'restaurants': [
                {
                    'name': r['name'],
                    'ville': r['ville'],
                    'horaires': r.get('horaires', {})
                } for r in self.restaurants
            ]
        }
    
    def get_plats_signatures(self) -> List[Dict]:
        """Retourne les plats signatures"""
        return [p for p in self.menu_complet if p.get('signature', False)]
    
    def get_info_generale(self, key: Optional[str] = None):
        """Retourne les infos générales"""
        if key:
            return self.infos_generales.get(key)
        return self.infos_generales
    
    # Méthodes de compatibilité avec l'ancien système
    def add_documents(self, documents: List[Dict]):
        """Pour compatibilité - ne fait rien car base enrichie statique"""
        pass
    
    def add_menu_items(self, menu_items: List[Dict]):
        """Pour compatibilité - ne fait rien car base enrichie statique"""
        pass
    
    def clear(self):
        """Pour compatibilité - ne fait rien"""
        pass


# Alias pour compatibilité
KnowledgeBase = EnrichedKnowledgeBase
