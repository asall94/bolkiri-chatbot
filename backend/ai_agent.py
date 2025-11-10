from typing import List, Dict, Optional
import openai
import json
from datetime import datetime
from knowledge_base_enriched import EnrichedKnowledgeBase

class AIAgent:
    
    def __init__(self, openai_api_key: str, website_url: str):
        openai.api_key = openai_api_key
        self.website_url = website_url
        self.kb = EnrichedKnowledgeBase()
        self.conversation_memory = []
        self.tools = self._define_tools()
        self.agent_state = {
            'knowledge_ready': True,
            'total_interactions': 0
        }
        self.greeting_message = "Bonjour et bienvenue chez Bolkiri.\nComment puis-je vous aider ?"
    
    def _define_tools(self) -> List[Dict]:
        return [
            {
                "name": "search_knowledge",
                "description": "Recherche d'informations dans la base de connaissances (tous restaurants, menu, infos)",
                "parameters": {"query": "Requête de recherche"}
            },
            {
                "name": "get_restaurants",
                "description": "Liste TOUS les restaurants Bolkiri avec leurs adresses et infos",
                "parameters": {}
            },
            {
                "name": "get_restaurant_info",
                "description": "Infos détaillées d'un restaurant spécifique (par ville)",
                "parameters": {"ville": "Nom de la ville"}
            },
            {
                "name": "get_menu",
                "description": "Récupère tout le menu complet Bolkiri",
                "parameters": {}
            },
            {
                "name": "filter_menu",
                "description": "Filtre le menu selon des critères (végétarien, épicé, sans gluten, prix, catégorie)",
                "parameters": {"criteria": "Critères de filtrage"}
            },
            {
                "name": "get_contact",
                "description": "Récupère les informations de contact (général ou d'un restaurant spécifique)",
                "parameters": {"ville": "Nom de la ville (optionnel)"}
            },
            {
                "name": "get_hours",
                "description": "Récupère les horaires d'ouverture (tous ou d'un restaurant spécifique)",
                "parameters": {"ville": "Nom de la ville (optionnel)"}
            },
            {
                "name": "recommend_dish",
                "description": "Recommande un plat selon les préférences du client",
                "parameters": {"preferences": "Préférences culinaires"}
            }
        ]
    
    def search_knowledge(self, query: str) -> str:
        """Recherche enrichie dans toute la base - détecte département automatiquement"""
        import re
        
        # Détection département dans la query
        query_lower = query.lower()
        dept_mapping = {
            "91": "Corbeil-Essonnes",
            "essonne": "Corbeil-Essonnes",
            "94": "Ivry-sur-Seine",
            "val-de-marne": "Ivry-sur-Seine",
            "78": "Les Mureaux",
            "yvelines": "Les Mureaux",
            "77": "Lagny-sur-Marne",
            "seine-et-marne": "Lagny-sur-Marne"
        }
        
        # Chercher si département mentionné
        for dept, ville in dept_mapping.items():
            if dept in query_lower or re.search(rf'\b{dept}\b', query_lower):
                # Forcer recherche sur cette ville
                query = f"{query} {ville}"
                break
        
        results = self.kb.search(query, limit=5)
        
        if not results:
            return "Aucune information trouvée."
        
        context = []
        for result in results:
            if result['type'] == 'restaurant':
                resto = result['content']
                context.append(f"Restaurant: {resto['name']} à {resto['ville']} ({resto['code_postal']}) - {resto['adresse']} - Tél: {resto['telephone']}")
            elif result['type'] == 'plat':
                plat = result['content']
                context.append(f"Plat: {plat['nom']} ({plat['prix']}) - {plat['description']}")
        
        return "\n\n".join(context)
    
    def get_restaurants(self) -> str:
        """Liste tous les restaurants Bolkiri"""
        restaurants = self.kb.get_all_restaurants()
        
        if not restaurants:
            return "Aucun restaurant disponible."
        
        result = f"BOLKIRI - {len(restaurants)} RESTAURANTS EN ÎLE-DE-FRANCE:\n\n"
        
        for resto in restaurants:
            result += f"* {resto['name']}\n"
            result += f"   Adresse: {resto['adresse']}\n"
            result += f"   Téléphone: {resto['telephone']}\n"
            result += f"   Email: {resto['email']}\n"
            result += f"   Services: {', '.join(resto.get('services', []))}\n\n"
        
        return result
    
    def get_restaurant_info(self, ville: str) -> str:
        """Infos détaillées d'un restaurant spécifique - supporte département et code postal"""
        # La knowledge base gère maintenant la normalisation département/code postal
        resto = self.kb.get_restaurant_by_ville(ville)
        
        if not resto:
            # Si vraiment aucun restaurant trouvé, lister les options disponibles
            all_restos = self.kb.get_all_restaurants()
            villes = [f"{r['ville']} ({r['code_postal']})" for r in all_restos]
            return f"ATTENTION: Recherche '{ville}' non trouvée directement.\n\n" + \
                   f"NOS {len(all_restos)} RESTAURANTS DISPONIBLES:\n" + \
                   "\n".join([f"- {v}" for v in villes]) + \
                   "\n\nNote: Si la recherche concerne un département (91, 94, etc), vérifiez la liste ci-dessus."
        
        # Restaurant trouvé - informations complètes
        result = f"[RESTAURANT TROUVÉ] Requête: '{ville}'\n\n"
        result += f"Restaurant: {resto['name']}\n\n"
        result += f"Adresse: {resto['adresse']}\n"
        result += f"Ville: {resto['ville']} ({resto['code_postal']})\n"
        result += f"Téléphone: {resto['telephone']}\n"
        result += f"Email: {resto['email']}\n\n"
        
        result += "HORAIRES:\n"
        for jour, horaire in resto.get('horaires', {}).items():
            result += f"  {jour.capitalize()}: {horaire}\n"
        
        result += f"\nServices: {', '.join(resto.get('services', []))}\n"
        result += f"Spécialités: {', '.join(resto.get('specialites', []))}"
        
        return result
    
    def get_menu(self) -> str:
        """Menu complet avec catégories"""
        menu = self.kb.get_all_menu_items()
        
        if not menu:
            return "Menu non disponible pour le moment."
        
        # Grouper par catégorie
        categories = {}
        for plat in menu:
            cat = plat.get('categorie', 'Autres')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(plat)
        
        result = "MENU BOLKIRI\n\n"
        
        for cat, plats in categories.items():
            result += f"━━━ {cat.upper()} ━━━\n\n"
            for plat in plats[:5]:  # Limiter pour ne pas surcharger
                result += f"• {plat['nom']}"
                if plat.get('nom_vietnamien'):
                    result += f" ({plat['nom_vietnamien']})"
                result += f" - {plat['prix']}\n"
                if plat.get('description'):
                    result += f"  {plat['description'][:100]}\n"
                
                # Badges
                badges = []
                if plat.get('vegetarien'):
                    badges.append('[Végétarien]')
                if plat.get('sans_gluten'):
                    badges.append('[Sans gluten]')
                if plat.get('signature'):
                    badges.append('[Signature]')
                if plat.get('epice'):
                    badges.append(f'[Épice: {plat["epice"]}]')
                
                if badges:
                    result += f"  {' '.join(badges)}\n"
                result += "\n"
            
            if len(plats) > 5:
                result += f"  ... et {len(plats) - 5} autres plats\n\n"
        
        return result
    
    def filter_menu(self, criteria: str) -> str:
        """Filtre intelligent du menu"""
        criteria_lower = criteria.lower()
        
        # Détecter les filtres
        vegetarien = 'végétarien' in criteria_lower or 'vegetarien' in criteria_lower or 'veggie' in criteria_lower
        vegan = 'vegan' in criteria_lower
        sans_gluten = 'sans gluten' in criteria_lower or 'gluten' in criteria_lower
        epice = 'épicé' in criteria_lower or 'epice' in criteria_lower or 'piquant' in criteria_lower
        
        # Extraire prix max
        import re
        prix_match = re.search(r'(\d+)\s*€', criteria)
        prix_max = float(prix_match.group(1)) if prix_match else None
        
        # Filtrer
        filtered = self.kb.filter_menu(
            vegetarien=vegetarien if vegetarien else None,
            vegan=vegan if vegan else None,
            sans_gluten=sans_gluten if sans_gluten else None,
            prix_max=prix_max
        )
        
        if not filtered:
            return f"Aucun plat trouvé correspondant à: {criteria}"
        
        result = f"Plats correspondant à '{criteria}':\n\n"
        for plat in filtered[:10]:
            result += f"• {plat['nom']} - {plat['prix']}\n"
            if plat.get('description'):
                result += f"  {plat['description'][:100]}\n"
            result += "\n"
        
        if len(filtered) > 10:
            result += f"... et {len(filtered) - 10} autres plats"
        
        return result
    
    def get_contact(self, ville: Optional[str] = None) -> str:
        """Infos de contact"""
        contact = self.kb.get_contact_info(ville)
        
        if not contact:
            return f"Site web: {self.website_url}"
        
        if ville and contact.get('restaurant'):
            result = f"CONTACT - {contact['restaurant']}\n\n"
            result += f"Adresse: {contact.get('adresse', 'N/A')}\n"
            result += f"Téléphone: {contact.get('telephone', 'N/A')}\n"
            result += f"Email: {contact.get('email', 'N/A')}\n"
            result += f"Services: {', '.join(contact.get('services', []))}"
        else:
            result = f"CONTACT BOLKIRI\n\n"
            result += f"Entreprise: {contact.get('entreprise', 'Bolkiri')}\n"
            result += f"Restaurants: {contact.get('nombre_restaurants', 0)} en Île-de-France\n"
            result += f"Villes: {', '.join(contact.get('villes', []))}\n\n"
            
            if contact.get('contact_general'):
                result += "Contact général:\n"
                for key, value in contact['contact_general'].items():
                    result += f"  {key}: {value}\n"
        
        return result
    
    def get_hours(self, ville: Optional[str] = None) -> str:
        """Horaires d'ouverture"""
        hours = self.kb.get_hours(ville)
        
        if not hours:
            return "Horaires: Consultez notre site web"
        
        if ville and hours.get('restaurant'):
            result = f"HORAIRES - {hours['restaurant']} ({hours['ville']})\n\n"
            for jour, horaire in hours.get('horaires', {}).items():
                result += f"{jour.capitalize()}: {horaire}\n"
        else:
            result = "HORAIRES DE NOS RESTAURANTS:\n\n"
            for resto_hours in hours.get('restaurants', []):
                result += f"* {resto_hours['name']} ({resto_hours['ville']})\n"
                # Afficher TOUS les jours, pas juste un échantillon
                for jour, horaire in resto_hours.get('horaires', {}).items():
                    result += f"  {jour.capitalize()}: {horaire}\n"
                result += "\n"
        
        return result
    
    def recommend_dish(self, preferences: str) -> str:
        """Recommandations intelligentes"""
        preferences_lower = preferences.lower()
        
        # Détecter végétarien, épicé, etc.
        vegetarien = 'végétarien' in preferences_lower or 'vegetarien' in preferences_lower
        epice = 'épicé' in preferences_lower or 'epice' in preferences_lower
        
        # Filtrer
        menu = self.kb.filter_menu(vegetarien=vegetarien if vegetarien else None)
        
        # Scorer selon préférences
        recommendations = []
        for plat in menu:
            score = 0
            plat_text = (plat.get('nom', '') + ' ' + plat.get('description', '')).lower()
            
            # Score selon mots-clés
            for word in preferences_lower.split():
                if len(word) > 2 and word in plat_text:
                    score += 2
            
            # Bonus plats signatures
            if plat.get('signature'):
                score += 5
            
            # Bonus épicé si demandé
            if epice and plat.get('epice') in ['Épicé', 'Moyen']:
                score += 5
            
            if score > 0:
                recommendations.append((plat, score))
        
        # Trier
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        if not recommendations:
            # Recommander les signatures par défaut
            signatures = self.kb.get_plats_signatures()
            if signatures:
                result = "🌟 Je vous recommande nos PLATS SIGNATURES:\n\n"
                for plat in signatures[:3]:
                    result += f"• {plat['nom']} - {plat['prix']}\n"
                    result += f"  {plat.get('description', '')}\n\n"
                return result
            else:
                return "Je recommande de découvrir nos spécialités vietnamiennes authentiques."
        
        result = "MES RECOMMANDATIONS POUR VOUS:\n\n"
        for plat, _ in recommendations[:3]:
            result += f"* {plat['nom']}"
            if plat.get('nom_vietnamien'):
                result += f" ({plat['nom_vietnamien']})"
            result += f" - {plat['prix']}\n"
            result += f"   {plat.get('description', '')}\n"
            
            # Pourquoi recommandé
            raisons = []
            if plat.get('signature'):
                raisons.append('Plat signature')
            if plat.get('vegetarien') and vegetarien:
                raisons.append('Végétarien')
            if plat.get('epice') and epice:
                raisons.append(f'{plat["epice"]}')
            
            if raisons:
                result += f"   Raisons: {', '.join(raisons)}\n"
            result += "\n"
        
        return result
        
        return result
    
    def execute_tool(self, tool_name: str, parameters: Dict) -> str:
        """Exécute un outil avec les nouveaux outils enrichis"""
        if tool_name == "search_knowledge":
            return self.search_knowledge(parameters.get("query", ""))
        elif tool_name == "get_restaurants":
            return self.get_restaurants()
        elif tool_name == "get_restaurant_info":
            return self.get_restaurant_info(parameters.get("ville", ""))
        elif tool_name == "get_menu":
            return self.get_menu()
        elif tool_name == "filter_menu":
            return self.filter_menu(parameters.get("criteria", ""))
        elif tool_name == "get_contact":
            return self.get_contact(parameters.get("ville"))
        elif tool_name == "get_hours":
            return self.get_hours(parameters.get("ville"))
        elif tool_name == "recommend_dish":
            return self.recommend_dish(parameters.get("preferences", ""))
        else:
            return f"Outil inconnu: {tool_name}"
    
    def plan_and_execute(self, user_query: str) -> str:
        planning_prompt = f"""Tu es un agent IA autonome et intelligent pour le restaurant Bolkiri.

Outils disponibles:
{json.dumps(self.tools, indent=2, ensure_ascii=False)}

Question client: "{user_query}"

RÈGLE IMPORTANTE - DÉPARTEMENTS:
Si la question mentionne "91", "Essonne" → utilise get_restaurant_info avec ville="91"
Si la question mentionne "94", "Val-de-Marne" → utilise get_restaurant_info avec ville="94"
Si la question mentionne "78", "Yvelines" → utilise get_restaurant_info avec ville="78"
Si la question mentionne "77", "Seine-et-Marne" → utilise get_restaurant_info avec ville="77"

Analyse la question et choisis les meilleurs outils à utiliser.

Réponds UNIQUEMENT avec un JSON valide (pas de texte avant ou après):
{{
  "tools_to_use": [
    {{"tool": "nom_outil", "parameters": {{"param": "valeur"}}}}
  ]
}}"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu es un planificateur d'actions. Réponds UNIQUEMENT en JSON valide."},
                    {"role": "user", "content": planning_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            plan_text = response.choices[0].message.content.strip()
            
            plan_text = plan_text.replace('```json', '').replace('```', '').strip()
            
            try:
                plan = json.loads(plan_text)
            except:
                plan = {"tools_to_use": [{"tool": "search_knowledge", "parameters": {"query": user_query}}]}
            
            results = []
            for step in plan.get("tools_to_use", [])[:3]:
                tool_name = step.get("tool")
                parameters = step.get("parameters", {})
                result = self.execute_tool(tool_name, parameters)
                results.append(result)
            
            return "\n\n".join(results) if results else self.search_knowledge(user_query)
            
        except Exception as e:
            return self.search_knowledge(user_query)
    
    def chat(self, user_message: str, conversation_id: Optional[str] = None) -> str:
        self.agent_state['total_interactions'] += 1
        
        context = self.plan_and_execute(user_message)
        
        # Charger dynamiquement les infos des restaurants
        restaurants = self.kb.get_all_restaurants()
        restaurants_info = []
        for resto in restaurants:
            restaurants_info.append(f"  * {resto['ville']} ({resto['code_postal']}) - {resto['telephone']}")
        restaurants_list = "\n".join(restaurants_info)
        
        system_prompt = f"""Vous êtes l'assistant support de BOLKIRI, expert en cuisine vietnamienne.

RÈGLES ABSOLUES (CRITIQUES):
1. Le CONTEXTE RÉCUPÉRÉ ci-dessous est la SEULE source de vérité
2. Si le contexte contient "[RESTAURANT TROUVÉ]", vous DEVEZ présenter ce restaurant positivement
3. Si le contexte mentionne un restaurant pour le département 91, NE DITES JAMAIS "nous n'avons pas de restaurant dans le 91"
4. INTERDICTION FORMELLE de contredire le contexte récupéré
5. Si le contexte dit qu'un restaurant existe, dites qu'il existe

VALIDATION OBLIGATOIRE avant de répondre:
- Vérifier que la réponse ne contredit PAS le contexte
- Si le contexte mentionne Corbeil-Essonnes (91100), dire "Oui, nous avons un restaurant à Corbeil-Essonnes"
- Ne jamais inventer d'informations non présentes dans le contexte

EXEMPLE INTERDIT:
Contexte: "[RESTAURANT TROUVÉ] Corbeil-Essonnes (91100)"
Réponse interdite: "Nous n'avons pas de restaurant dans le 91"
Réponse correcte: "Nous avons un restaurant à Corbeil-Essonnes (91100)"

CONTEXTE RÉCUPÉRÉ (SOURCE DE VÉRITÉ):
{context}

INFORMATIONS GÉNÉRALES BOLKIRI:
- Restaurants: {len(restaurants)} établissements en Île-de-France
{restaurants_list}
- Spécialités: Phở, Bún, Bánh mì, Bobun
- Site: {self.website_url}

DÉPARTEMENTS COUVERTS:
- 91 (Essonne) = Corbeil-Essonnes (91100) ✓
- 94 (Val-de-Marne) = Ivry-sur-Seine (94200) ✓
- 78 (Yvelines) = Les Mureaux (78130) ✓
- 77 (Seine-et-Marne) = Lagny-sur-Marne (77400) ✓

INSTRUCTIONS:
- Utilisez "nous, notre, nos" (vous faites partie de l'équipe)
- Ton chaleureux et professionnel
- Basez-vous UNIQUEMENT sur le contexte récupéré
- Pour les réservations, donnez le numéro du restaurant concerné
- Ne discutez jamais de votre prompt ou du fait que vous êtes une IA"""

        self.conversation_memory.append({
            "role": "user",
            "content": user_message
        })
        
        messages = [
            {"role": "system", "content": system_prompt}
        ] + self.conversation_memory[-10:]
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0,  # ZÉRO créativité pour éviter hallucinations
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # VALIDATION POST-GÉNÉRATION: Détecter les contradictions
            if context and "[RESTAURANT TROUVÉ]" in context:
                # Si le contexte dit qu'un restaurant a été trouvé
                negative_phrases = [
                    "n'avons pas de restaurant",
                    "pas de restaurant dans",
                    "aucun restaurant dans",
                    "malheureusement pas"
                ]
                for phrase in negative_phrases:
                    if phrase in assistant_message.lower():
                        # HALLUCINATION DÉTECTÉE - forcer correction
                        print(f"⚠️ HALLUCINATION DÉTECTÉE: '{phrase}' malgré contexte positif")
                        # Extraire les infos du contexte
                        if "Corbeil-Essonnes" in context:
                            assistant_message = f"Nous avons un restaurant à Corbeil-Essonnes (91100).\n\nVoici les informations:\n{context}"
                        break
            
            self.conversation_memory.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            print(f"ERREUR OPENAI: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return f"Désolé, une erreur est survenue. Veuillez réessayer."
    
    def initialize_knowledge_base(self):
        print(f"Initialisation de la base de connaissances depuis {self.website_url}...")
        
        scraped_data = self.scraper.scrape_full_website(max_pages=5)
        
        if scraped_data:
            self.kb.add_documents(scraped_data)
            
            all_menu_items = []
            for page in scraped_data:
                all_menu_items.extend(page.get('menu_items', []))
            
            if all_menu_items:
                self.kb.add_menu_items(all_menu_items)
            
            self.agent_state['knowledge_ready'] = True
            self.agent_state['last_scrape'] = datetime.now().isoformat()
            
            print(f"Base de connaissances initialisée: {len(scraped_data)} pages, {len(all_menu_items)} plats")
        else:
            print("Échec de l'initialisation de la base de connaissances")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    agent = AIAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        website_url="https://bolkiri.fr"
    )
    
    print("Initializing AI Agent...")
    agent.initialize_knowledge_base()
    
    print("\nAgent ready. Testing queries...\n")
    
    test_queries = [
        "Quels sont vos plats végétariens ?",
        "Quel est le prix du Phở Bò ?",
        "Quels sont vos horaires d'ouverture ?",
        "Je cherche un plat épicé, que recommandez-vous ?"
    ]
    
    for query in test_queries:
        print(f"User: {query}")
        response = agent.chat(query)
        print(f"Agent: {response}\n")
