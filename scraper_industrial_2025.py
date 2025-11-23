import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Set
import re
from urllib.parse import urljoin, urlparse

class BolkiriIndustrialScraper:
    """Complete industrial scraper - Automatically scrapes ALL relevant pages"""
    
    def __init__(self, base_url: str = "https://bolkiri.fr"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'BolkiriChatbot/1.0 (https://github.com/asall94/bolkiri-chatbot)'
        }
        self.visited_urls: Set[str] = set()
        self.all_pages_content = {}
        self.restaurants = []
        self.menu = []
        self.geocoding_cache = {}  # Cache for Nominatim API calls
        
        # Priority pages to scrape
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
        
        # Pages to ignore - NONE (we scrape everything)
        # RAG will only return what's relevant
        self.ignored_patterns = []
    
    def should_scrape_url(self, url: str) -> bool:
        """Determine if URL should be scraped"""
        # Ignore external URLs
        if not url.startswith(self.base_url):
            return False
        
        # Ignore files
        if any(ext in url for ext in ['.pdf', '.jpg', '.png', '.zip', '.doc']):
            return False
        
        # Ignore blacklisted pages
        for pattern in self.ignored_patterns:
            if pattern in url:
                return False
        
        # Already visited
        if url in self.visited_urls:
            return False
        
        return True
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def scrape_page(self, url: str) -> Dict:
        """Scrape complete page and extract content"""
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unnecessary elements
            for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ""
            
            # Extract headings (structure)
            headings = []
            for tag in ['h1', 'h2', 'h3']:
                for heading in soup.find_all(tag):
                    text = heading.get_text(strip=True)
                    if text and len(text) > 2:
                        headings.append({
                            'level': tag,
                            'text': text
                        })
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            text_content = main_content.get_text(separator='\n', strip=True) if main_content else ""
            text_content = self.clean_text(text_content)
            
            # Extract lists (FAQ, key points)
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
                'content': text_content[:5000],  # Limit to 5000 chars
                'lists': lists,
                'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"  Erreur: {e}")
            return None
    
    def discover_pages(self, start_url: str) -> List[str]:
        """Automatically discover all site pages"""
        discovered_urls = set()
        
        try:
            response = requests.get(start_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(self.base_url, href)
                
                # Normalize URL
                parsed = urlparse(full_url)
                normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
                if self.should_scrape_url(normalized_url):
                    discovered_urls.add(normalized_url)
        
        except Exception as e:
            print(f"Erreur découverte pages: {e}")
        
        return list(discovered_urls)
    
    def scrape_all_content(self):
        """Scrape all relevant site content"""
        print("\n" + "=" * 60)
        print("COMPLETE INDUSTRIAL SCRAPING")
        print("=" * 60)
        
        # 1. Scrape priority pages
        print("\n[1/3] Priority pages...")
        for page_path in self.priority_pages:
            url = self.base_url + page_path
            page_data = self.scrape_page(url)
            if page_data:
                self.all_pages_content[url] = page_data
            time.sleep(0.5)
        
        # 2. Discover and scrape other pages
        print("\n[2/3] Automatic discovery...")
        discovered = self.discover_pages(self.base_url)
        print(f"  {len(discovered)} pages discovered")
        
        for url in discovered[:20]:  # Limit to 20 discovered pages
            if url not in self.all_pages_content:
                page_data = self.scrape_page(url)
                if page_data:
                    self.all_pages_content[url] = page_data
                time.sleep(0.5)
        
        # 3. Scrape restaurants (hardcoded list for reliability)
        print("\n[3/3] Detailed restaurants...")
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
        """Parse menu content to extract each dish individually"""
        dishes = []
        
        # Split by "COMMANDER" which separates each dish
        dish_blocks = menu_content.split('COMMANDER')
        
        for block in dish_blocks:
            block = block.strip()
            if not block or len(block) < 20:
                continue
            
            # Ignore navigation/system elements from the start
            skip_words = ['aller au contenu', 'gérer', 'accepter', 'refuser', 'cookies']
            if any(skip in block.lower() for skip in skip_words):
                continue
            
            # Clean: keep until "Plus" to separate name from rest
            # Format: "DISH NAME Plus description Plus traces..."
            parts = block.split('Plus')
            
            if not parts or len(parts[0].strip()) < 3:
                continue
            
            # Extract name (first part before "Plus")
            dish_name = parts[0].strip()
            
            # If name contains multiple lines, take only first uppercase line
            name_lines = [l.strip() for l in dish_name.split('\n') if l.strip()]
            if name_lines:
                # Keep first non-empty line as main name
                main_name = name_lines[0]
                
                # If name too long (> 150 chars), it's probably a badly split formula
                if len(main_name) > 150:
                    # Take until first lowercase word or punctuation
                    words = main_name.split()
                    clean_name_parts = []
                    for word in words:
                        if word.isupper() or word[0].isupper():
                            clean_name_parts.append(word)
                        else:
                            break
                    main_name = ' '.join(clean_name_parts) if clean_name_parts else words[0]
                
                dish_name = main_name
            
            # Extract description (second part after first "Plus")
            description = parts[1].strip() if len(parts) > 1 else ''
            
            # Find price (€ pattern)
            price_match = re.search(r'(\d+[,.]?\d*)\s*€', block)
            price = price_match.group(0) if price_match else ''
            
            # Detect tags (vegetarian, spicy, etc.)
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
                'description': description[:300],  # Limit length
                'prix': price,
                'tags': tags,
                'raw_content': block[:500]  # Keep raw content for RAG
            })
        
        return dishes
    
    def extract_restaurant_data(self, url: str) -> Dict:
        """Extract structured restaurant data from JSON-LD Schema.org"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract JSON-LD structured data
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
            
            # If no JSON-LD, fallback on HTML extraction
            if not json_ld_data:
                page_text = soup.get_text()
                h1 = soup.find('h1')
                
                # Extract phone
                telephone = ""
                tel_pattern = r'\+33\s?\d{1}\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}'
                tel_match = re.search(tel_pattern, page_text)
                if tel_match:
                    telephone = tel_match.group(0)
                
                # Extract address
                adresse = ""
                for string in soup.stripped_strings:
                    if re.search(r'\d+.*(?:Rue|Avenue|Boulevard|Place)', string):
                        adresse = string
                        break
                
                # Status
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
            
            # Extract from JSON-LD
            name = json_ld_data.get('name', '')
            telephone = json_ld_data.get('telephone', '')
            
            # Extract structured address
            address_data = json_ld_data.get('address', {})
            adresse = f"{address_data.get('streetAddress', '')}, {address_data.get('postalCode', '')} {address_data.get('addressLocality', '')}"
            
            # Extract and parse hours from openingHoursSpecification
            horaires = {}
            if 'openingHoursSpecification' in json_ld_data:
                horaires = self.parse_opening_hours(json_ld_data['openingHoursSpecification'])
            
            # Status
            page_text = soup.get_text()
            statut = "ouvert"
            if "prochaine" in page_text.lower():
                statut = "ouverture_prochaine"
            
            # Get coordinates
            coordinates = self.geocode_address(adresse)
            
            restaurant_data = {
                "name": name,
                "telephone": telephone,
                "adresse": adresse,
                "horaires": horaires,
                "statut": statut,
                "url": url,
                "coordinates": coordinates,
                "description": f"Restaurant {name}\nAdresse: {adresse}\nTéléphone: {telephone}\n\nPour réserver ou commander: <a href=\"{url}\" target=\"_blank\">Page du restaurant</a>"
            }
            
            return restaurant_data
            
        except Exception as e:
            print(f"    Erreur: {e}")
            return None
    
    def geocode_address(self, address: str) -> Dict:
        """Get coordinates from address using Nominatim (OpenStreetMap)"""
        if address in self.geocoding_cache:
            return self.geocoding_cache[address]
        
        try:
            # Clean address for better results
            clean_address = address.replace('\n', ', ').strip()
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': clean_address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'fr'  # France only
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data:
                coords = {
                    'lat': float(data[0]['lat']),
                    'lon': float(data[0]['lon'])
                }
                self.geocoding_cache[address] = coords
                time.sleep(1)  # Nominatim rate limit: 1 req/sec
                return coords
            
        except Exception as e:
            print(f"    Geocoding error: {e}")
        
        return None
    
    def parse_opening_hours(self, specs: List[Dict]) -> Dict:
        """Parse openingHoursSpecification from Schema.org
        
        This site uses validFrom/validThrough format without dayOfWeek.
        We group identical time ranges.
        """
        if not specs:
            return {}
        
        # Collect all unique time ranges
        time_ranges = []
        for spec in specs:
            opens = spec.get('opens', '')
            closes = spec.get('closes', '')
            
            if opens and closes:
                time_range = f"{opens}-{closes}"
                if time_range not in time_ranges:
                    time_ranges.append(time_range)
        
        # If we have time ranges, apply to all days
        # (site doesn't specify individual days in openingHoursSpecification)
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
        """Save complete knowledge base"""
        
        # Organize pages by category
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
                # Parse menu into individual dishes
                menu_dishes = self.parse_menu_into_dishes(content['content'])
                # Create document per dish
                for dish in menu_dishes:
                    categorized_pages['menu'].append({
                        'url': url,
                        'title': f"Plat: {dish['nom']}",
                        'content': f"{dish['nom']}\n{dish['description']}\nPrix: {dish['prix']}\nTags: {', '.join(dish['tags'])}\n\nPour commander ce plat, cliquez ici: <a href=\"{url}\" target=\"_blank\">Menu Bolkiri</a>\n\n{dish['raw_content']}",
                        'dish_data': dish
                    })
            elif '/fidelite/' in url or 'fidélité' in content['title'].lower():
                content['content'] = f"{content['content']}\n\nPour en savoir plus: <a href=\"{url}\" target=\"_blank\">Programme de fidélité</a>"
                categorized_pages['fidelite'].append(content)
            elif '/service-client/' in url or 'faq' in url.lower():
                content['content'] = f"{content['content']}\n\nContactez-nous: <a href=\"{url}\" target=\"_blank\">Service client</a>"
                categorized_pages['service_client'].append(content)
            elif '/notre-concept/' in url or '/nos-engagements/' in url:
                content['content'] = f"{content['content']}\n\nDécouvrez-en plus: <a href=\"{url}\" target=\"_blank\">Notre concept</a>"
                categorized_pages['concept'].append(content)
            elif '/devenir-franchise/' in url:
                content['content'] = f"{content['content']}\n\nRejoignez notre réseau: <a href=\"{url}\" target=\"_blank\">Devenir franchisé</a>"
                categorized_pages['autres'].append(content)
            elif '/nous-rejoindre/' in url:
                content['content'] = f"{content['content']}\n\nPostulez maintenant: <a href=\"{url}\" target=\"_blank\">Nous rejoindre</a>"
                categorized_pages['autres'].append(content)
            elif '/service-traiteur/' in url:
                content['content'] = f"{content['content']}\n\nDemandez un devis: <a href=\"{url}\" target=\"_blank\">Service traiteur</a>"
                categorized_pages['autres'].append(content)
            elif '/nos-restaurants/' in url:
                content['content'] = f"{content['content']}\n\nTrouvez votre restaurant: <a href=\"{url}\" target=\"_blank\">Nos restaurants</a>"
                categorized_pages['autres'].append(content)
            else:
                content['content'] = f"{content['content']}\n\nPlus d'infos: <a href=\"{url}\" target=\"_blank\">En savoir plus</a>"
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
        print("SCRAPING COMPLETE")
        print("=" * 60)
        print(f"\nFile: {filename}")
        print(f"  Scraped pages: {len(self.all_pages_content)}")
        print(f"  Restaurants: {len(self.restaurants)}")
        print(f"  Menu: {len(categorized_pages['menu'])} pages")
        print(f"  Fidelity: {len(categorized_pages['fidelite'])} pages")
        print(f"  Customer service: {len(categorized_pages['service_client'])} pages")
        print(f"  Concept: {len(categorized_pages['concept'])} pages")
        print(f"  Other: {len(categorized_pages['autres'])} pages")
        
        return filename

def main():
    print("=" * 60)
    print("BOLKIRI INDUSTRIAL SCRAPER 2025")
    print("Automatic scraping of ALL relevant pages")
    print("=" * 60)
    
    scraper = BolkiriIndustrialScraper()
    scraper.scrape_all_content()
    filename = scraper.save_complete_knowledge_base()
    
    print("\nComplete knowledge base ready!")
    print(f"File: {filename}")

if __name__ == "__main__":
    main()
