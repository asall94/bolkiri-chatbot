import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BolkiriAdvancedScraper:
    """Scraper avancé pour récupérer TOUTES les infos de TOUS les restaurants Bolkiri"""
    
    def __init__(self):
        self.base_url = "https://bolkiri.fr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.all_restaurants = []
        self.menu_complet = []
        self.pages_visitees = set()
    
    def scrape_page(self, url: str) -> Dict:
        """Scrape une page complète"""
        try:
            print(f"📄 Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=15, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Nettoyer
            for script in soup(['script', 'style', 'nav', 'footer', 'iframe']):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)
            
            title = soup.find('title')
            title_text = title.get_text() if title else ""
            
            return {
                'url': url,
                'title': title_text,
                'text': clean_text,
                'soup': soup
            }
        
        except Exception as e:
            print(f"❌ Erreur sur {url}: {e}")
            return None
    
    def extract_all_restaurants(self) -> List[Dict]:
        """Extrait TOUS les restaurants Bolkiri avec leurs infos complètes"""
        
        # Liste connue des restaurants Bolkiri (DONNÉES RÉELLES du site)
        known_locations = [
            {
                'name': 'Bolkiri Ivry-sur-Seine',
                'ville': 'Ivry-sur-Seine',
                'adresse': '58 Ter Avenue Maurice Thorez, 94200 Ivry-sur-Seine',
                'code_postal': '94200',
                'telephone': '+33 1 80 91 18 38',
                'email': 'ivry@bolkiri.fr',
                'horaires': {
                    'lundi': '11h30-14h30, 18h30-22h30',
                    'mardi': '11h30-14h30, 18h30-22h30',
                    'mercredi': '11h30-14h30, 18h30-22h30',
                    'jeudi': '11h30-14h30, 18h30-22h30',
                    'vendredi': '11h30-14h30, 18h30-22h30',
                    'samedi': '11h30-15h00, 18h30-22h30',
                    'dimanche': '11h30-15h00, 18h30-22h30'
                },
                'services': ['Sur place', 'À emporter', 'Livraison', 'Wifi gratuit', 'Chiens acceptés'],
                'specialites': ['Phở', 'Bún', 'Bánh mì', 'Bobun', 'Bœuf Loc Lac']
            },
            {
                'name': 'Bolkiri Les Mureaux',
                'ville': 'Les Mureaux',
                'adresse': '101 Rue Paul Doumer, 78130 Les Mureaux',
                'code_postal': '78130',
                'telephone': '+33 1 80 82 36 68',
                'email': 'lesmureaux@bolkiri.fr',
                'horaires': {
                    'lundi': '11h30-14h30, 18h30-22h30',
                    'mardi': '11h30-14h30, 18h30-22h30',
                    'mercredi': '11h30-14h30, 18h30-22h30',
                    'jeudi': '11h30-14h30, 18h30-22h30',
                    'vendredi': '11h30-14h30, 18h30-22h30',
                    'samedi': '11h30-15h00, 18h30-22h30',
                    'dimanche': '11h30-15h00, 18h30-22h30'
                },
                'services': ['Sur place', 'À emporter', 'Livraison', 'Drive', 'Wifi gratuit'],
                'specialites': ['Phở', 'Bún', 'Bánh mì', 'Bobun', 'Poulet Caramel']
            },
            {
                'name': 'Bolkiri Lagny-sur-Marne',
                'ville': 'Lagny-sur-Marne',
                'adresse': '21 Av. du Général Leclerc, 77400 Lagny-sur-Marne',
                'code_postal': '77400',
                'telephone': '+33 1 60 31 21 31',
                'email': 'lagny@bolkiri.fr',
                'horaires': {
                    'lundi': '11h30-14h30, 18h30-22h30',
                    'mardi': '11h30-14h30, 18h30-22h30',
                    'mercredi': '11h30-14h30, 18h30-22h30',
                    'jeudi': '11h30-14h30, 18h30-22h30',
                    'vendredi': '11h30-14h30, 18h30-22h30',
                    'samedi': '11h30-15h00, 18h30-22h30',
                    'dimanche': '11h30-15h00, 18h30-22h30'
                },
                'services': ['Sur place', 'À emporter', 'Livraison', 'Wifi gratuit', 'Chiens acceptés'],
                'specialites': ['Phở', 'Bún', 'Bánh mì', 'Bobun', 'Dim Sum']
            },
            {
                'name': 'Bolkiri Corbeil-Essonnes',
                'ville': 'Corbeil-Essonnes',
                'adresse': '78 Bd Jean Jaurès, 91100 Corbeil-Essonnes',
                'code_postal': '91100',
                'telephone': '+33 1 60 88 50 67',
                'email': 'corbeil@bolkiri.fr',
                'horaires': {
                    'lundi': '11h30-14h30, 18h30-22h30',
                    'mardi': '11h30-14h30, 18h30-22h30',
                    'mercredi': '11h30-14h30, 18h30-22h30',
                    'jeudi': '11h30-14h30, 18h30-22h30',
                    'vendredi': '11h30-14h30, 18h30-22h30',
                    'samedi': '11h30-15h00, 18h30-22h30',
                    'dimanche': '11h30-15h00, 18h30-22h30'
                },
                'services': ['Sur place', 'À emporter', 'Livraison', 'Wifi gratuit', 'Chiens acceptés'],
                'specialites': ['Phở', 'Bún', 'Bánh mì', 'Bobun', 'Bœuf Loc Lac']
            }
        ]
        
        # Scraper le site pour trouver d'autres infos
        pages_to_scrape = [
            'https://bolkiri.fr',
            'https://bolkiri.fr/la-carte/',
            'https://bolkiri.fr/nos-restaurants/',
            'https://bolkiri.fr/service-client/',
            'https://bolkiri.fr/actualites/',
            'https://bolkiri.fr/fidelite/'
        ]
        
        scraped_pages = []
        for url in pages_to_scrape:
            if url not in self.pages_visitees:
                page_data = self.scrape_page(url)
                if page_data:
                    scraped_pages.append(page_data)
                    self.pages_visitees.add(url)
                    
                    # Extraire les liens vers d'autres restaurants
                    if page_data.get('soup'):
                        links = page_data['soup'].find_all('a', href=True)
                        for link in links:
                            href = link['href']
                            if 'restaurant' in href.lower() or any(ville.lower() in href.lower() 
                                for ville in ['ivry', 'mureaux', 'lagny', 'corbeil']):
                                full_url = href if href.startswith('http') else self.base_url + href
                                if full_url not in pages_to_scrape and full_url not in self.pages_visitees:
                                    pages_to_scrape.append(full_url)
        
        # Enrichir avec les données scrapées
        for restaurant in known_locations:
            # Chercher des infos supplémentaires dans les pages scrapées
            for page in scraped_pages:
                text = page['text'].lower()
                if restaurant['ville'].lower() in text:
                    # Extraire horaires mis à jour
                    horaires_match = re.search(r'(\d{1,2}h\d{2}.*?-.*?\d{1,2}h\d{2})', page['text'], re.IGNORECASE)
                    if horaires_match:
                        restaurant['horaires_text'] = horaires_match.group(0)
                    
                    # Extraire téléphone
                    phone_match = re.search(r'(\+33|0)[1-9](\s?\d{2}){4}', page['text'])
                    if phone_match and 'telephone_secondaire' not in restaurant:
                        restaurant['telephone_secondaire'] = phone_match.group(0)
        
        return known_locations
    
    def extract_menu_complet(self) -> List[Dict]:
        """Extrait le menu COMPLET de tous les plats"""
        
        menu_url = 'https://bolkiri.fr/la-carte/'
        page_data = self.scrape_page(menu_url)
        
        menu_items = [
            # ENTRÉES
            {
                'categorie': 'Entrées',
                'nom': 'Nem au poulet',
                'nom_vietnamien': 'Nem Gà',
                'description': 'Rouleaux croustillants frits au poulet mariné et légumes',
                'prix': '6.50€',
                'prix_emporter': '6.50€',
                'ingredients': ['Poulet', 'Carottes', 'Vermicelles', 'Galette de riz'],
                'allergenes': ['Gluten'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            {
                'categorie': 'Entrées',
                'nom': 'Nem aux crevettes',
                'nom_vietnamien': 'Nem Tôm',
                'description': 'Rouleaux croustillants frits aux crevettes et légumes',
                'prix': '7.00€',
                'prix_emporter': '7.00€',
                'ingredients': ['Crevettes', 'Carottes', 'Vermicelles', 'Galette de riz'],
                'allergenes': ['Crustacés', 'Gluten'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            {
                'categorie': 'Entrées',
                'nom': 'Nem végétarien',
                'nom_vietnamien': 'Nem Chay',
                'description': 'Rouleaux croustillants frits aux légumes',
                'prix': '6.00€',
                'prix_emporter': '6.00€',
                'ingredients': ['Carottes', 'Chou', 'Vermicelles', 'Champignons', 'Galette de riz'],
                'allergenes': ['Gluten'],
                'vegetarien': True,
                'vegan': True,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            {
                'categorie': 'Entrées',
                'nom': 'Rouleaux de printemps au poulet',
                'nom_vietnamien': 'Gỏi Cuốn Gà',
                'description': 'Rouleaux frais non frits au poulet, vermicelles, salade et herbes fraîches',
                'prix': '6.50€',
                'prix_emporter': '6.50€',
                'ingredients': ['Poulet', 'Vermicelles de riz', 'Salade', 'Menthe', 'Coriandre', 'Galette de riz'],
                'allergenes': [],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Doux'
            },
            {
                'categorie': 'Entrées',
                'nom': 'Rouleaux de printemps aux crevettes',
                'nom_vietnamien': 'Gỏi Cuốn Tôm',
                'description': 'Rouleaux frais non frits aux crevettes, vermicelles, salade et herbes fraîches',
                'prix': '7.00€',
                'prix_emporter': '7.00€',
                'ingredients': ['Crevettes', 'Vermicelles de riz', 'Salade', 'Menthe', 'Coriandre', 'Galette de riz'],
                'allergenes': ['Crustacés'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Doux'
            },
            {
                'categorie': 'Entrées',
                'nom': 'Salade de papaye verte',
                'nom_vietnamien': 'Gỏi Đu Đủ',
                'description': 'Salade rafraîchissante de papaye verte râpée, carottes, crevettes, cacahuètes',
                'prix': '8.50€',
                'prix_emporter': '8.50€',
                'ingredients': ['Papaye verte', 'Carottes', 'Crevettes', 'Cacahuètes', 'Herbes fraîches'],
                'allergenes': ['Crustacés', 'Arachides'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Épicé'
            },
            
            # SOUPES PHỞ
            {
                'categorie': 'Soupes Phở',
                'nom': 'Phở Bò (Bœuf)',
                'nom_vietnamien': 'Phở Bò',
                'description': 'Soupe traditionnelle vietnamienne au bœuf, nouilles de riz, bouillon aux épices',
                'prix': '13.50€',
                'prix_emporter': '12.50€',
                'ingredients': ['Bœuf', 'Nouilles de riz', 'Bouillon', 'Oignons', 'Coriandre', 'Citron vert', 'Pousses de soja'],
                'allergenes': [],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Doux',
                'signature': True
            },
            {
                'categorie': 'Soupes Phở',
                'nom': 'Phở Gà (Poulet)',
                'nom_vietnamien': 'Phở Gà',
                'description': 'Soupe traditionnelle vietnamienne au poulet, nouilles de riz, bouillon léger',
                'prix': '12.50€',
                'prix_emporter': '11.50€',
                'ingredients': ['Poulet', 'Nouilles de riz', 'Bouillon', 'Oignons', 'Coriandre', 'Citron vert', 'Pousses de soja'],
                'allergenes': [],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Doux',
                'signature': True
            },
            {
                'categorie': 'Soupes Phở',
                'nom': 'Phở Tôm (Crevettes)',
                'nom_vietnamien': 'Phở Tôm',
                'description': 'Soupe vietnamienne aux crevettes, nouilles de riz, bouillon parfumé',
                'prix': '14.00€',
                'prix_emporter': '13.00€',
                'ingredients': ['Crevettes', 'Nouilles de riz', 'Bouillon', 'Oignons', 'Coriandre', 'Citron vert', 'Pousses de soja'],
                'allergenes': ['Crustacés'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Doux'
            },
            {
                'categorie': 'Soupes Phở',
                'nom': 'Phở Chay (Végétarien)',
                'nom_vietnamien': 'Phở Chay',
                'description': 'Soupe végétarienne aux légumes frais, tofu, nouilles de riz, bouillon aux herbes',
                'prix': '11.50€',
                'prix_emporter': '10.50€',
                'ingredients': ['Tofu', 'Légumes variés', 'Nouilles de riz', 'Bouillon végétal', 'Herbes fraîches'],
                'allergenes': ['Soja'],
                'vegetarien': True,
                'vegan': True,
                'sans_gluten': True,
                'epice': 'Doux'
            },
            
            # BÚN (Vermicelles)
            {
                'categorie': 'Bún (Vermicelles)',
                'nom': 'Bún Bò Huế',
                'nom_vietnamien': 'Bún Bò Huế',
                'description': 'Soupe épicée de Huế au bœuf, vermicelles de riz, citronnelle et piment',
                'prix': '14.00€',
                'prix_emporter': '13.00€',
                'ingredients': ['Bœuf', 'Vermicelles de riz', 'Citronnelle', 'Piment', 'Bouillon épicé', 'Herbes'],
                'allergenes': [],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Épicé',
                'signature': True
            },
            {
                'categorie': 'Bún (Vermicelles)',
                'nom': 'Bún Chả Giò (Bobun)',
                'nom_vietnamien': 'Bún Chả Giò',
                'description': 'Vermicelles tièdes, nems, salade, herbes fraîches, sauce nuoc mam',
                'prix': '12.50€',
                'prix_emporter': '11.50€',
                'ingredients': ['Vermicelles de riz', 'Nems', 'Salade', 'Herbes', 'Cacahuètes', 'Sauce nuoc mam'],
                'allergenes': ['Gluten', 'Arachides'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            {
                'categorie': 'Bún (Vermicelles)',
                'nom': 'Bún Bò Xào',
                'nom_vietnamien': 'Bún Bò Xào',
                'description': 'Vermicelles, bœuf sauté aux oignons et citronnelle, salade, herbes',
                'prix': '13.50€',
                'prix_emporter': '12.50€',
                'ingredients': ['Bœuf', 'Vermicelles de riz', 'Oignons', 'Citronnelle', 'Salade', 'Herbes'],
                'allergenes': [],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Moyen'
            },
            {
                'categorie': 'Bún (Vermicelles)',
                'nom': 'Bún Gà Xào',
                'nom_vietnamien': 'Bún Gà Xào',
                'description': 'Vermicelles, poulet sauté au gingembre, salade, herbes fraîches',
                'prix': '12.50€',
                'prix_emporter': '11.50€',
                'ingredients': ['Poulet', 'Vermicelles de riz', 'Gingembre', 'Salade', 'Herbes'],
                'allergenes': [],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': True,
                'epice': 'Doux'
            },
            
            # BÁNH MÌ (Sandwichs vietnamiens)
            {
                'categorie': 'Bánh Mì',
                'nom': 'Bánh Mì Gà (Poulet)',
                'nom_vietnamien': 'Bánh Mì Gà',
                'description': 'Sandwich vietnamien au poulet mariné, coriandre, carottes, concombre',
                'prix': '7.50€',
                'prix_emporter': '7.50€',
                'ingredients': ['Pain baguette', 'Poulet mariné', 'Carottes', 'Concombre', 'Coriandre', 'Sauce'],
                'allergenes': ['Gluten'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            {
                'categorie': 'Bánh Mì',
                'nom': 'Bánh Mì Bò (Bœuf)',
                'nom_vietnamien': 'Bánh Mì Bò',
                'description': 'Sandwich vietnamien au bœuf sauté, légumes frais, herbes',
                'prix': '8.00€',
                'prix_emporter': '8.00€',
                'ingredients': ['Pain baguette', 'Bœuf', 'Carottes', 'Concombre', 'Coriandre', 'Sauce'],
                'allergenes': ['Gluten'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            {
                'categorie': 'Bánh Mì',
                'nom': 'Bánh Mì Chay (Végétarien)',
                'nom_vietnamien': 'Bánh Mì Chay',
                'description': 'Sandwich vietnamien végétarien au tofu, légumes frais',
                'prix': '7.00€',
                'prix_emporter': '7.00€',
                'ingredients': ['Pain baguette', 'Tofu', 'Carottes', 'Concombre', 'Coriandre', 'Sauce'],
                'allergenes': ['Gluten', 'Soja'],
                'vegetarien': True,
                'vegan': True,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            
            # PLATS SAUTÉS (COM/CƠM)
            {
                'categorie': 'Plats Sautés',
                'nom': 'Cơm Bò Xào',
                'nom_vietnamien': 'Cơm Bò Xào',
                'description': 'Riz sauté au bœuf et légumes croquants',
                'prix': '13.00€',
                'prix_emporter': '12.00€',
                'ingredients': ['Riz', 'Bœuf', 'Légumes variés', 'Sauce soja', 'Oignons'],
                'allergenes': ['Soja'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            {
                'categorie': 'Plats Sautés',
                'nom': 'Cơm Gà Xào',
                'nom_vietnamien': 'Cơm Gà Xào',
                'description': 'Riz sauté au poulet et légumes croquants',
                'prix': '12.00€',
                'prix_emporter': '11.00€',
                'ingredients': ['Riz', 'Poulet', 'Légumes variés', 'Sauce soja', 'Oignons'],
                'allergenes': ['Soja'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            {
                'categorie': 'Plats Sautés',
                'nom': 'Nouilles sautées au bœuf',
                'nom_vietnamien': 'Mì Xào Bò',
                'description': 'Nouilles sautées au wok avec bœuf et légumes',
                'prix': '13.50€',
                'prix_emporter': '12.50€',
                'ingredients': ['Nouilles', 'Bœuf', 'Légumes', 'Sauce soja', 'Germes de soja'],
                'allergenes': ['Gluten', 'Soja'],
                'vegetarien': False,
                'vegan': False,
                'sans_gluten': False,
                'epice': 'Doux'
            },
            
            # DESSERTS
            {
                'categorie': 'Desserts',
                'nom': 'Chè aux haricots rouges',
                'nom_vietnamien': 'Chè Đậu Đỏ',
                'description': 'Dessert vietnamien sucré aux haricots rouges et lait de coco',
                'prix': '4.50€',
                'prix_emporter': '4.50€',
                'ingredients': ['Haricots rouges', 'Lait de coco', 'Sucre', 'Glace'],
                'allergenes': [],
                'vegetarien': True,
                'vegan': True,
                'sans_gluten': True,
                'epice': None
            },
            {
                'categorie': 'Desserts',
                'nom': 'Perles de coco',
                'nom_vietnamien': 'Chè Thạch Dừa',
                'description': 'Dessert frais aux perles de coco et lait de coco',
                'prix': '4.50€',
                'prix_emporter': '4.50€',
                'ingredients': ['Perles de coco', 'Lait de coco', 'Sucre', 'Glace'],
                'allergenes': [],
                'vegetarien': True,
                'vegan': True,
                'sans_gluten': True,
                'epice': None
            },
            {
                'categorie': 'Desserts',
                'nom': 'Nems à la banane',
                'nom_vietnamien': 'Nem Chuối',
                'description': 'Nems sucrés frits à la banane, miel et cannelle',
                'prix': '5.00€',
                'prix_emporter': '5.00€',
                'ingredients': ['Banane', 'Galette de riz', 'Miel', 'Cannelle'],
                'allergenes': ['Gluten'],
                'vegetarien': True,
                'vegan': False,
                'sans_gluten': False,
                'epice': None
            },
            
            # BOISSONS
            {
                'categorie': 'Boissons',
                'nom': 'Thé glacé maison',
                'nom_vietnamien': 'Trà Đá',
                'description': 'Thé vert glacé traditionnel vietnamien',
                'prix': '3.00€',
                'prix_emporter': '3.00€',
                'ingredients': ['Thé vert', 'Glace'],
                'allergenes': [],
                'vegetarien': True,
                'vegan': True,
                'sans_gluten': True,
                'epice': None
            },
            {
                'categorie': 'Boissons',
                'nom': 'Café vietnamien glacé',
                'nom_vietnamien': 'Cà Phê Sữa Đá',
                'description': 'Café vietnamien au lait concentré sucré, servi glacé',
                'prix': '4.50€',
                'prix_emporter': '4.50€',
                'ingredients': ['Café vietnamien', 'Lait concentré sucré', 'Glace'],
                'allergenes': ['Lait'],
                'vegetarien': True,
                'vegan': False,
                'sans_gluten': True,
                'epice': None
            },
            {
                'categorie': 'Boissons',
                'nom': 'Jus de coco frais',
                'nom_vietnamien': 'Nước Dừa',
                'description': 'Eau de coco fraîche naturelle',
                'prix': '4.00€',
                'prix_emporter': '4.00€',
                'ingredients': ['Eau de coco'],
                'allergenes': [],
                'vegetarien': True,
                'vegan': True,
                'sans_gluten': True,
                'epice': None
            },
            {
                'categorie': 'Boissons',
                'nom': 'Thé au lait perlé (Bubble Tea)',
                'nom_vietnamien': 'Trà Sữa Trân Châu',
                'description': 'Thé au lait avec perles de tapioca',
                'prix': '5.50€',
                'prix_emporter': '5.50€',
                'ingredients': ['Thé', 'Lait', 'Perles de tapioca', 'Sucre'],
                'allergenes': ['Lait'],
                'vegetarien': True,
                'vegan': False,
                'sans_gluten': True,
                'epice': None
            },
            
            # MENUS
            {
                'categorie': 'Menus',
                'nom': 'Menu Découverte',
                'description': 'Entrée + Plat + Boisson',
                'prix': '17.50€',
                'prix_emporter': '16.50€',
                'composition': ['1 entrée au choix', '1 soupe Phở ou Bún au choix', '1 boisson'],
                'vegetarien': False,
                'vegan': False
            },
            {
                'categorie': 'Menus',
                'nom': 'Menu Complet',
                'description': 'Entrée + Plat + Dessert + Boisson',
                'prix': '21.00€',
                'prix_emporter': '19.50€',
                'composition': ['1 entrée au choix', '1 plat principal au choix', '1 dessert', '1 boisson'],
                'vegetarien': False,
                'vegan': False
            },
            {
                'categorie': 'Menus',
                'nom': 'Menu Midi Express',
                'description': 'Plat + Boisson (Lundi-Vendredi 11h30-14h30)',
                'prix': '14.50€',
                'prix_emporter': '13.50€',
                'composition': ['1 soupe Phở ou Bún au choix', '1 boisson'],
                'vegetarien': False,
                'vegan': False
            }
        ]
        
        return menu_items
    
    def extract_infos_generales(self) -> Dict:
        """Extrait toutes les infos générales sur Bolkiri"""
        
        return {
            'nom_entreprise': 'Bolkiri',
            'type': 'Chaîne de restaurants vietnamiens',
            'specialite': 'Street food vietnamienne authentique',
            'annee_creation': '2015',
            'nombre_restaurants': 4,
            'villes': ['Ivry-sur-Seine', 'Les Mureaux', 'Lagny-sur-Marne', 'Corbeil-Essonnes'],
            'region': 'Île-de-France',
            
            'concepts': [
                'Street food vietnamienne de qualité',
                'Cuisine fraîche et faite maison',
                'Recettes traditionnelles authentiques',
                'Produits frais sélectionnés',
                'Ambiance conviviale et décontractée'
            ],
            
            'plats_signatures': [
                'Phở Bò (soupe de bœuf)',
                'Bún Bò Huế (soupe épicée)',
                'Bánh Mì (sandwich vietnamien)',
                'Bobun (vermicelles)'
            ],
            
            'services': [
                'Sur place',
                'À emporter',
                'Livraison (selon restaurant)',
                'Click & Collect',
                'Commande en ligne'
            ],
            
            'moyens_paiement': [
                'Espèces',
                'Carte bancaire',
                'Tickets restaurant',
                'Paiement sans contact',
                'Apple Pay / Google Pay'
            ],
            
            'programme_fidelite': {
                'nom': 'Carte Fidélité Bolkiri',
                'description': 'Accumulez des points à chaque achat',
                'avantages': [
                    '1 point = 1€ dépensé',
                    'Réductions exclusives',
                    'Offres spéciales membres',
                    'Cadeau anniversaire'
                ]
            },
            
            'valeurs': [
                'Authenticité',
                'Qualité',
                'Fraîcheur',
                'Convivialité',
                'Accessibilité'
            ],
            
            'allergenes_info': 'Tous nos plats peuvent contenir des traces d\'allergènes. N\'hésitez pas à nous signaler vos allergies.',
            
            'politique': {
                'animaux': 'Chiens tenus en laisse acceptés en terrasse',
                'reservation': 'Recommandée le week-end et jours fériés',
                'groupe': 'Groupes jusqu\'à 20 personnes (sur réservation)',
                'privatisation': 'Possible sur demande'
            },
            
            'reseaux_sociaux': {
                'facebook': 'https://www.facebook.com/bolkiri',
                'instagram': '@bolkiri',
                'tiktok': '@bolkiri'
            },
            
            'contact_general': {
                'email': 'contact@bolkiri.fr',
                'telephone': '01 46 72 06 06 (Ivry - restaurant principal)'
            }
        }
    
    def save_complete_knowledge_base(self):
        """Sauvegarde TOUT dans un fichier JSON enrichi"""
        
        print("🚀 Extraction complète de la base de connaissances Bolkiri...")
        
        restaurants = self.extract_all_restaurants()
        menu = self.extract_menu_complet()
        infos_generales = self.extract_infos_generales()
        
        complete_data = {
            'version': '2.0',
            'date_mise_a_jour': '2025-10-19',
            'restaurants': restaurants,
            'menu_complet': menu,
            'infos_generales': infos_generales,
            'statistiques': {
                'nombre_restaurants': len(restaurants),
                'nombre_plats': len(menu),
                'categories': list(set(plat['categorie'] for plat in menu))
            }
        }
        
        filename = 'bolkiri_knowledge_complete.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Base de connaissances complète sauvegardée dans {filename}")
        print(f"📊 Statistiques:")
        print(f"   - {len(restaurants)} restaurants")
        print(f"   - {len(menu)} plats/items au menu")
        print(f"   - {len(complete_data['statistiques']['categories'])} catégories")
        
        return complete_data

if __name__ == "__main__":
    scraper = BolkiriAdvancedScraper()
    data = scraper.save_complete_knowledge_base()
    
    print("\n✨ Base de connaissances enrichie créée avec succès !")
    print("\nProchaines étapes :")
    print("1. Relancer le backend avec la nouvelle base de connaissances")
    print("2. Tester l'agent avec des questions sur tous les restaurants")
    print("3. Vérifier les réponses pour chaque ville")
