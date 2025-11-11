import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Set
import re
from urllib.parse import urljoin, urlparse

class BolkiriIndustrialScraper:
    """Scraper industriel complet - Scrappe automatiquement TOUTES les pages pertinentes"""
    
    def __init__(self, base_url: str = "https://bolkiri.fr"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.visited_urls: Set[str] = set()
        self.all_pages_content = {}
        self.restaurants = []
        self.menu = []
        
        # Pages à scraper (prioritaires)
        self.priority_pages = [
            '/la-carte/',
            '/nos-restaurants/',
            '/fidelite/',
            '/service-client/',
            '/service-traiteur/',
            '/notre-concept/',
            '/nos-engagements/',
            '/actualites/',
            '/devenir-franchise/',
            '/nous-rejoindre/'
        ]
        
        # Pages à ignorer - AUCUNE (on scrappe tout)
        # Le RAG ne retournera que ce qui est pertinent
        self.ignored_patterns = []
    
    def should_scrape_url(self, url: str) -> bool:
        """Détermine si une URL doit être scrapée"""
        # Ignorer les URLs externes
        if not url.startswith(self.base_url):
            return False
        
        # Ignorer les fichiers
        if any(ext in url for ext in ['.pdf', '.jpg', '.png', '.zip', '.doc']):
            return False
        
        # Ignorer les pages blacklistées
        for pattern in self.ignored_patterns:
            if pattern in url:
                return False
        
        # Déjà visitée
        if url in self.visited_urls:
            return False
        
        return True
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte extrait"""
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        # Supprimer les lignes vides
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def scrape_page(self, url: str) -> Dict:
        """Scrape une page complète et extrait son contenu"""
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Nettoyer les éléments inutiles
            for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
                element.decompose()
            
            # Extraire le titre
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ""
            
            # Extraire les headings (structure)
            headings = []
            for tag in ['h1', 'h2', 'h3']:
                for heading in soup.find_all(tag):
                    text = heading.get_text(strip=True)
                    if text and len(text) > 2:
                        headings.append({
                            'level': tag,
                            'text': text
                        })
            
            # Extraire le contenu principal
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            text_content = main_content.get_text(separator='\n', strip=True) if main_content else ""
            text_content = self.clean_text(text_content)
            
            # Extraire les listes (FAQ, points clés)
            lists = []
            for ul in soup.find_all(['ul', 'ol']):
                items = [li.get_text(strip=True) for li in ul.find_all('li')]
                if items:
                    lists.append(items)
            
            self.visited_urls.add(url)
            
            return {
                'url': url,
                'title': title_text,
                'headings': headings,
                'content': text_content[:5000],  # Limiter à 5000 chars
                'lists': lists,
                'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"  Erreur: {e}")
            return None
    
    def discover_pages(self, start_url: str) -> List[str]:
        """Découvre automatiquement toutes les pages du site"""
        discovered_urls = set()
        
        try:
            response = requests.get(start_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les liens
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(self.base_url, href)
                
                # Normaliser l'URL
                parsed = urlparse(full_url)
                normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
                if self.should_scrape_url(normalized_url):
                    discovered_urls.add(normalized_url)
        
        except Exception as e:
            print(f"Erreur découverte pages: {e}")
        
        return list(discovered_urls)
    
    def scrape_all_content(self):
        """Scrape tout le contenu pertinent du site"""
        print("\n" + "=" * 60)
        print("SCRAPING INDUSTRIEL COMPLET")
        print("=" * 60)
        
        # 1. Scraper les pages prioritaires
        print("\n[1/3] Pages prioritaires...")
        for page_path in self.priority_pages:
            url = self.base_url + page_path
            page_data = self.scrape_page(url)
            if page_data:
                self.all_pages_content[url] = page_data
            time.sleep(0.5)
        
        # 2. Découvrir et scraper les autres pages
        print("\n[2/3] Découverte automatique...")
        discovered = self.discover_pages(self.base_url)
        print(f"  {len(discovered)} pages découvertes")
        
        for url in discovered[:20]:  # Limiter à 20 pages découvertes
            if url not in self.all_pages_content:
                page_data = self.scrape_page(url)
                if page_data:
                    self.all_pages_content[url] = page_data
                time.sleep(0.5)
        
        # 3. Scraper les restaurants (liste hardcodée pour fiabilité)
        print("\n[3/3] Restaurants détaillés...")
        self.scrape_restaurants()
    
    def scrape_restaurants(self):
        """Scrape tous les restaurants"""
        restaurant_urls = [
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/bondy/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/bry-sur-marne/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/corbeil-essonnes/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/ivry/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/saint-denis/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/lille-leon-gambetta/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/malakoff/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/montreuil/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/montrouge/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/nanterre/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/paris-11-republique/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/pierrefitte/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/les-mureaux/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/boulogne-billancourt/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/lagny-sur-marne/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/sucy-en-brie/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/saint-michel-sur-orge/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/versailles/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/saint-gratien/",
            "https://restaurants.bolkiri.fr/street-food-vietnamienne/lille-gare-flandres/"
        ]
        
        for idx, url in enumerate(restaurant_urls, 1):
            print(f"  [{idx}/{len(restaurant_urls)}] {url}")
            resto_data = self.extract_restaurant_data(url)
            if resto_data:
                self.restaurants.append(resto_data)
            time.sleep(0.5)
    
    def parse_menu_into_dishes(self, menu_content: str) -> List[Dict]:
        """Parse le contenu du menu pour extraire chaque plat individuellement"""
        dishes = []
        
        # Découper par "COMMANDER" qui sépare chaque plat
        dish_blocks = menu_content.split('COMMANDER')
        
        for block in dish_blocks:
            block = block.strip()
            if not block or len(block) < 20:
                continue
            
            # Ignorer les éléments de navigation/système dès le début
            skip_words = ['aller au contenu', 'gérer', 'accepter', 'refuser', 'cookies']
            if any(skip in block.lower() for skip in skip_words):
                continue
            
            # Nettoyer : garder jusqu'à "Plus" pour séparer nom du reste
            # Format: "NOM DU PLAT Plus description Plus traces..."
            parts = block.split('Plus')
            
            if not parts or len(parts[0].strip()) < 3:
                continue
            
            # Extraire le nom (première partie avant "Plus")
            dish_name = parts[0].strip()
            
            # Si le nom contient plusieurs lignes, prendre seulement la première ligne majuscule
            name_lines = [l.strip() for l in dish_name.split('\n') if l.strip()]
            if name_lines:
                # Garder la première ligne non-vide comme nom principal
                main_name = name_lines[0]
                
                # Si nom trop long (> 150 chars), c'est probablement une formule mal découpée
                if len(main_name) > 150:
                    # Prendre jusqu'au premier mot en minuscules ou ponctuation
                    words = main_name.split()
                    clean_name_parts = []
                    for word in words:
                        if word.isupper() or word[0].isupper():
                            clean_name_parts.append(word)
                        else:
                            break
                    main_name = ' '.join(clean_name_parts) if clean_name_parts else words[0]
                
                dish_name = main_name
            
            # Extraire la description (deuxième partie après premier "Plus")
            description = parts[1].strip() if len(parts) > 1 else ''
            
            # Chercher le prix (pattern €)
            price_match = re.search(r'(\d+[,.]?\d*)\s*€', block)
            price = price_match.group(0) if price_match else ''
            
            # Détecter les tags (végétarien, épicé, etc.)
            tags = []
            if 'végé' in block.lower() or 'végétarien' in block.lower():
                tags.append('vegetarien')
            if 'épicé' in block.lower() or '🌶' in block:
                tags.append('epice')
            if 'signature' in block.lower():
                tags.append('signature')
            if 'nem' in block.lower():
                tags.append('nems')
            
            dishes.append({
                'nom': dish_name,
                'description': description[:300],  # Limiter la longueur
                'prix': price,
                'tags': tags,
                'raw_content': block[:500]  # Garder le contenu brut pour RAG
            })
        
        return dishes
    
    def extract_restaurant_data(self, url: str) -> Dict:
        """Extrait les données structurées d'un restaurant depuis JSON-LD Schema.org"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire les données structurées JSON-LD
            json_ld_data = None
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if '@graph' in data:
                            for item in data['@graph']:
                                if item.get('@type') == 'Restaurant':
                                    json_ld_data = item
                                    break
                        elif data.get('@type') == 'Restaurant':
                            json_ld_data = data
                            
                    if json_ld_data:
                        break
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Si pas de JSON-LD, fallback sur extraction HTML
            if not json_ld_data:
                page_text = soup.get_text()
                h1 = soup.find('h1')
                
                # Extraire téléphone
                telephone = ""
                tel_pattern = r'\+33\s?\d{1}\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}'
                tel_match = re.search(tel_pattern, page_text)
                if tel_match:
                    telephone = tel_match.group(0)
                
                # Extraire adresse
                adresse = ""
                for string in soup.stripped_strings:
                    if re.search(r'\d+.*(?:Rue|Avenue|Boulevard|Place)', string):
                        adresse = string
                        break
                
                # Statut
                statut = "ouvert"
                if "prochaine" in page_text.lower():
                    statut = "ouverture_prochaine"
                
                return {
                    "name": h1.get_text(strip=True) if h1 else "",
                    "telephone": telephone,
                    "adresse": adresse,
                    "statut": statut,
                    "url": url
                }
            
            # Extraire depuis JSON-LD
            name = json_ld_data.get('name', '')
            telephone = json_ld_data.get('telephone', '')
            
            # Extraire l'adresse structurée
            address_data = json_ld_data.get('address', {})
            adresse = f"{address_data.get('streetAddress', '')}, {address_data.get('postalCode', '')} {address_data.get('addressLocality', '')}"
            
            # Extraire et parser les horaires depuis openingHoursSpecification
            horaires = {}
            if 'openingHoursSpecification' in json_ld_data:
                horaires = self.parse_opening_hours(json_ld_data['openingHoursSpecification'])
            
            # Statut
            page_text = soup.get_text()
            statut = "ouvert"
            if "prochaine" in page_text.lower():
                statut = "ouverture_prochaine"
            
            restaurant_data = {
                "name": name,
                "telephone": telephone,
                "adresse": adresse,
                "horaires": horaires,
                "statut": statut,
                "url": url
            }
            
            # Ajouter l'URL au contenu texte du restaurant
            if restaurant_data:
                restaurant_data['description'] = f"Restaurant {name}\nAdresse: {adresse}\nTéléphone: {telephone}\n\nPour réserver ou en savoir plus: {url}"
            
            return restaurant_data
            
        except Exception as e:
            print(f"    Erreur: {e}")
            return None
    
    def parse_opening_hours(self, specs: List[Dict]) -> Dict:
        """Parse les openingHoursSpecification de Schema.org
        
        Ce site utilise le format validFrom/validThrough sans dayOfWeek.
        On regroupe les plages horaires identiques.
        """
        if not specs:
            return {}
        
        # Collecter toutes les plages horaires uniques
        time_ranges = []
        for spec in specs:
            opens = spec.get('opens', '')
            closes = spec.get('closes', '')
            
            if opens and closes:
                time_range = f"{opens}-{closes}"
                if time_range not in time_ranges:
                    time_ranges.append(time_range)
        
        # Si on a des plages horaires, les appliquer à tous les jours
        # (le site ne spécifie pas les jours individuellement dans openingHoursSpecification)
        if time_ranges:
            combined = ", ".join(time_ranges)
            return {
                "lundi": combined,
                "mardi": combined,
                "mercredi": combined,
                "jeudi": combined,
                "vendredi": combined,
                "samedi": combined,
                "dimanche": combined
            }
        
        return {}
    
    def save_complete_knowledge_base(self):
        """Sauvegarde la base de connaissances complète"""
        
        # Organiser les pages par catégorie
        categorized_pages = {
            'menu': [],
            'restaurants': [],
            'fidelite': [],
            'service_client': [],
            'concept': [],
            'autres': []
        }
        
        for url, content in self.all_pages_content.items():
            if '/la-carte/' in url:
                # Parser le menu en plats individuels
                menu_dishes = self.parse_menu_into_dishes(content['content'])
                # Créer un document par plat
                for dish in menu_dishes:
                    categorized_pages['menu'].append({
                        'url': url,
                        'title': f"Plat: {dish['nom']}",
                        'content': f"{dish['nom']}\n{dish['description']}\nPrix: {dish['prix']}\nTags: {', '.join(dish['tags'])}\n\nPour commander ce plat: {url}\n\n{dish['raw_content']}",
                        'dish_data': dish
                    })
            elif '/fidelite/' in url or 'fidélité' in content['title'].lower():
                content['content'] = f"{content['content']}\n\nPour en savoir plus sur le programme de fidélité: {url}"
                categorized_pages['fidelite'].append(content)
            elif '/service-client/' in url or 'faq' in url.lower():
                content['content'] = f"{content['content']}\n\nPour contacter le service client: {url}"
                categorized_pages['service_client'].append(content)
            elif '/notre-concept/' in url or '/nos-engagements/' in url:
                content['content'] = f"{content['content']}\n\nPour découvrir notre concept: {url}"
                categorized_pages['concept'].append(content)
            else:
                content['content'] = f"{content['content']}\n\nPour plus d'informations: {url}"
                categorized_pages['autres'].append(content)
        
        data = {
            "version": "4.0_industrial",
            "date_scraping": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_pages_scrapees": len(self.all_pages_content),
            "total_restaurants": len(self.restaurants),
            "restaurants": self.restaurants,
            "pages_par_categorie": categorized_pages,
            "informations_generales": {
                "concept": "Street Food Vietnamienne Authentique",
                "programme_fidelite": "1€ dépensé = 1 grain de riz (point)",
                "reduction_premiere_commande": "-10% avec code BOLKIRI10",
                "services_disponibles": ["Sur place", "À emporter", "Livraison", "Drive"],
                "reseaux_sociaux": {
                    "instagram": "https://www.instagram.com/bolkiri/",
                    "facebook": "https://www.facebook.com/BolkiriParis/",
                    "tiktok": "https://www.tiktok.com/@bolkiri"
                }
            }
        }
        
        filename = "bolkiri_knowledge_industrial_2025.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("SCRAPING TERMINÉ")
        print("=" * 60)
        print(f"\nFichier: {filename}")
        print(f"  Pages scrapées: {len(self.all_pages_content)}")
        print(f"  Restaurants: {len(self.restaurants)}")
        print(f"  Menu: {len(categorized_pages['menu'])} pages")
        print(f"  Fidélité: {len(categorized_pages['fidelite'])} pages")
        print(f"  Service client: {len(categorized_pages['service_client'])} pages")
        print(f"  Concept: {len(categorized_pages['concept'])} pages")
        print(f"  Autres: {len(categorized_pages['autres'])} pages")
        
        return filename

def main():
    print("=" * 60)
    print("SCRAPER INDUSTRIEL BOLKIRI 2025")
    print("Scraping automatique de TOUTES les pages pertinentes")
    print("=" * 60)
    
    scraper = BolkiriIndustrialScraper()
    scraper.scrape_all_content()
    filename = scraper.save_complete_knowledge_base()
    
    print("\nBase de connaissances complète prête !")
    print(f"Fichier: {filename}")

if __name__ == "__main__":
    main()
