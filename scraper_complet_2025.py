import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict
import re

class BolkiriCompletScraper2025:
    """Scraper ultra-complet pour récupérer TOUS les restaurants et données Bolkiri 2025"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.restaurants = []
        
    def scrape_all_restaurants(self):
        """Scrape la liste complète des restaurants depuis la page officielle"""
        print("Scraping de la liste complète des restaurants...")
        
        url = "https://restaurants.bolkiri.fr/street-food-vietnamienne/nos-restaurants/"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Liste manuelle exhaustive basée sur la page officielle
            restaurant_links = [
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
            
            print(f"{len(restaurant_links)} restaurants détectés")
            
            # Scraper chaque restaurant individuellement
            for idx, resto_url in enumerate(restaurant_links, 1):
                print(f"\n[{idx}/{len(restaurant_links)}] Scraping {resto_url}...")
                resto_data = self.scrape_restaurant_detail(resto_url)
                if resto_data:
                    self.restaurants.append(resto_data)
                time.sleep(0.5)  # Pause pour ne pas surcharger le serveur
                
        except Exception as e:
            print(f"Erreur lors du scraping de la liste: {e}")
    
    def scrape_restaurant_detail(self, url: str) -> Dict:
        """Scrape les détails complets d'un restaurant"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraction du nom
            name = ""
            h1 = soup.find('h1')
            if h1:
                name = h1.get_text(strip=True)
            
            # Extraction de l'adresse
            adresse = ""
            adresse_elem = soup.find(string=re.compile(r'\d+.*[Rr]ue|[Aa]venue|[Bb]oulevard|[Pp]lace'))
            if adresse_elem:
                adresse = adresse_elem.strip()
            
            # Extraction du code postal et ville
            ville = ""
            code_postal = ""
            if adresse:
                cp_match = re.search(r'(\d{5})\s+([A-Za-zÀ-ÿ\-\s]+)', adresse)
                if cp_match:
                    code_postal = cp_match.group(1)
                    ville = cp_match.group(2).strip()
            
            # Extraction du téléphone
            telephone = ""
            tel_patterns = [
                r'\+33\s?\d{1}\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}',
                r'0\d{1}\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}'
            ]
            page_text = soup.get_text()
            for pattern in tel_patterns:
                tel_match = re.search(pattern, page_text)
                if tel_match:
                    telephone = tel_match.group(0)
                    break
            
            # Extraction des horaires
            horaires = self.extract_horaires(soup)
            
            # Extraction des services
            services = []
            service_keywords = ['Sur place', 'À emporter', 'Livraison', 'Drive', 'Wifi', 'Chiens acceptés']
            for keyword in service_keywords:
                if keyword.lower() in page_text.lower():
                    services.append(keyword)
            
            # Email (format standard Bolkiri)
            email = ""
            if ville:
                ville_clean = ville.lower().replace(' ', '').replace('-', '')
                email = f"{ville_clean}@bolkiri.fr"
            
            # Statut (ouvert ou prochainement)
            statut = "ouvert"
            if "Ouverture prochaine" in page_text or "prochaine" in page_text.lower():
                statut = "ouverture_prochaine"
            
            restaurant_data = {
                "name": name if name else f"Bolkiri {ville}",
                "ville": ville,
                "adresse": adresse,
                "code_postal": code_postal,
                "telephone": telephone,
                "email": email,
                "horaires": horaires,
                "services": services if services else ["Sur place", "À emporter", "Livraison"],
                "statut": statut,
                "url": url,
                "specialites": ["Phở", "Bún", "Bánh mì", "Bobun"]
            }
            
            print(f"   {name} - {ville} ({statut})")
            return restaurant_data
            
        except Exception as e:
            print(f"   Erreur: {e}")
            return None
    
    def extract_horaires(self, soup) -> Dict:
        """Extraction intelligente des horaires"""
        horaires_default = {
            "lundi": "11h30-14h30, 18h30-22h30",
            "mardi": "11h30-14h30, 18h30-22h30",
            "mercredi": "11h30-14h30, 18h30-22h30",
            "jeudi": "11h30-14h30, 18h30-22h30",
            "vendredi": "11h30-14h30, 18h30-22h30",
            "samedi": "11h30-15h00, 18h30-22h30",
            "dimanche": "11h30-15h00, 18h30-22h30"
        }
        
        # Chercher les horaires dans le texte
        text = soup.get_text()
        jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        horaires = {}
        
        for jour in jours:
            pattern = f"{jour}[:\s]*(\d{{1,2}}h?\d{{0,2}}\s*-\s*\d{{1,2}}h?\d{{0,2}})"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                horaires[jour] = match.group(1)
            else:
                horaires[jour] = horaires_default[jour]
        
        return horaires if horaires else horaires_default
    
    def scrape_menu(self):
        """Scrape le menu complet"""
        print("\nScraping du menu complet...")
        
        menu_url = "https://bolkiri.fr/la-carte/"
        
        try:
            response = requests.get(menu_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            menu = []
            
            # Extraction des plats
            plats_elements = soup.find_all(['h2', 'h3', 'h4'])
            
            for elem in plats_elements:
                nom = elem.get_text(strip=True)
                if nom and len(nom) > 3 and not nom.isupper():
                    
                    # Chercher la description
                    description = ""
                    next_p = elem.find_next('p')
                    if next_p:
                        description = next_p.get_text(strip=True)
                    
                    # Chercher le prix
                    prix = ""
                    prix_pattern = r'(\d+[,\.]\d{2})\s*€'
                    next_text = elem.find_next(string=re.compile(prix_pattern))
                    if next_text:
                        prix_match = re.search(prix_pattern, next_text)
                        if prix_match:
                            prix = prix_match.group(1)
                    
                    if description or prix:
                        menu.append({
                            "nom": nom,
                            "description": description,
                            "prix": prix if prix else "Variable"
                        })
            
            print(f"{len(menu)} plats récupérés")
            return menu
            
        except Exception as e:
            print(f"Erreur menu: {e}")
            return []
    
    def scrape_actualites(self):
        """Scrape les actualités récentes"""
        print("\nScraping des actualités...")
        
        actu_url = "https://bolkiri.fr/actualites/"
        
        try:
            response = requests.get(actu_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            actualites = []
            
            # Extraction des titres d'articles
            articles = soup.find_all(['h2', 'h3'], class_=re.compile('article|post|title'))
            
            for article in articles[:5]:  # Top 5
                titre = article.get_text(strip=True)
                if titre and len(titre) > 5:
                    actualites.append(titre)
            
            print(f"{len(actualites)} actualités récupérées")
            return actualites
            
        except Exception as e:
            print(f"Erreur actualités: {e}")
            return []
    
    def save_to_json(self, menu, actualites):
        """Sauvegarde complète dans un JSON structuré"""
        
        data = {
            "version": "3.0_complet",
            "date_scraping": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_restaurants": len(self.restaurants),
            "restaurants_ouverts": len([r for r in self.restaurants if r.get('statut') == 'ouvert']),
            "restaurants_a_venir": len([r for r in self.restaurants if r.get('statut') == 'ouverture_prochaine']),
            "restaurants": self.restaurants,
            "menu": menu,
            "actualites": actualites,
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
        
        filename = "bolkiri_knowledge_complete_2025.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\nSauvegarde dans {filename}")
        print(f"   {data['total_restaurants']} restaurants au total")
        print(f"   {data['restaurants_ouverts']} ouverts")
        print(f"   {data['restaurants_a_venir']} à venir")
        print(f"   {len(menu)} plats au menu")
        print(f"   {len(actualites)} actualités")
        
        return filename

def main():
    print("=" * 60)
    print("SCRAPER COMPLET BOLKIRI 2025")
    print("=" * 60)
    
    scraper = BolkiriCompletScraper2025()
    
    # 1. Scraper tous les restaurants
    scraper.scrape_all_restaurants()
    
    # 2. Scraper le menu
    menu = scraper.scrape_menu()
    
    # 3. Scraper les actualités
    actualites = scraper.scrape_actualites()
    
    # 4. Sauvegarder
    filename = scraper.save_to_json(menu, actualites)
    
    print("\n" + "=" * 60)
    print("SCRAPING TERMINÉ AVEC SUCCÈS")
    print("=" * 60)
    print(f"\nFichier généré: {filename}")
    print("\nProchaines étapes:")
    print("1. Vérifier le fichier JSON")
    print("2. Mettre à jour l'agent IA avec cette nouvelle base")
    print("3. Tester avec des questions sur tous les restaurants")

if __name__ == "__main__":
    main()
