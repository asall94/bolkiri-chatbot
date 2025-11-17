from typing import List, Dict, Optional, Tuple
from openai import OpenAI
import json
from datetime import datetime
from knowledge_base_enriched import EnrichedKnowledgeBase

class AIAgent:
    
    def __init__(self, openai_api_key: str, website_url: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.website_url = website_url
        self.kb = EnrichedKnowledgeBase()
        self.conversation_memory = []
        self.tools = self._define_tools()
        self.agent_state = {
            'knowledge_ready': True,
            'total_interactions': 0,
            'last_update': None
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
            return "[HORS_PERIMETRE] Cette information n'est pas disponible sur notre site web. Pour des questions spécifiques (parking, événements, réservations privées...), contactez directement le restaurant concerné."
        
        context = []
        for result in results:
            # RAG retourne déjà du contenu formaté en string
            content = result.get('content', '')
            if content:
                context.append(content)
        
        return "\n\n".join(context)
    
    def get_restaurants(self) -> str:
        """Liste tous les restaurants Bolkiri"""
        restaurants = self.kb.get_all_restaurants()
        
        if not restaurants:
            return "Aucun restaurant disponible."
        
        result = f"BOLKIRI - {len(restaurants)} RESTAURANTS EN ÎLE-DE-FRANCE:\n\n"
        
        for resto in restaurants:
            result += f"• {resto['name']}\n"
            result += f"   Adresse : {resto['adresse']}\n"
            result += f"   Téléphone : {resto['telephone']}\n"
            result += f"   Email : {resto['email']}\n"
            result += f"   Services : {', '.join(resto.get('services', []))}\n\n"
        
        return result
    
    def get_restaurant_info(self, ville: str) -> str:
        """Infos détaillées d'un restaurant spécifique - supporte département et code postal"""
        # Utiliser RAG pour recherche intelligente
        results = self.kb.search(f"restaurant {ville}", limit=3)
        
        if not results:
            # Lister tous les restaurants disponibles
            all_restos = self.kb.get_all_restaurants()
            return f"Restaurant non trouvé pour '{ville}'.\n\n" + \
                   f"NOS {len(all_restos)} RESTAURANTS DISPONIBLES:\n" + \
                   "\n".join([f"- {r.get('name', 'N/A')}" for r in all_restos[:10]]) + \
                   "\n\n(10 premiers restaurants affichés)"
        
        # Prendre le meilleur résultat
        best_result = results[0]
        return f"[RESTAURANT TROUVE]\n\n{best_result.get('content', 'Information non disponible')}"
    
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
                result += f"{jour.capitalize()} : {horaire}\n"
        else:
            result = "HORAIRES DE NOS RESTAURANTS :\n\n"
            for resto_hours in hours.get('restaurants', []):
                result += f"• {resto_hours['name']} ({resto_hours['ville']})\n"
                # Afficher TOUS les jours, pas juste un échantillon
                for jour, horaire in resto_hours.get('horaires', {}).items():
                    result += f"  {jour.capitalize()} : {horaire}\n"
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
        
        result = "MES RECOMMANDATIONS POUR VOUS :\n\n"
        for plat, _ in recommendations[:3]:
            result += f"• {plat['nom']}"
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
                result += f"   Raisons : {', '.join(raisons)}\n"
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
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Agent de planning multi-tool. Analyse query → Sélection outils optimaux → Output JSON strict (pas texte). Capacité: décomposition requêtes complexes en étapes parallèles."},
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
    
    def _validate_response(self, response: str, context: str, user_query: str) -> Tuple[str, bool]:
        """Valide la réponse générée contre le contexte et détecte les hallucinations
        
        Returns:
            (response_corrigee, is_valid)
        """
        response_lower = response.lower()
        context_lower = context.lower()
        
        # 1. Vérifier contradictions restaurants
        if "[restaurant trouvé]" in context_lower or "restaurant" in context_lower:
            # Détecter phrases négatives alors que restaurant existe
            negative_phrases = [
                "n'avons pas de restaurant",
                "pas de restaurant dans",
                "aucun restaurant dans",
                "malheureusement pas",
                "ne disposons pas"
            ]
            
            for phrase in negative_phrases:
                if phrase in response_lower:
                    print(f"[WARN] HALLUCINATION: '{phrase}' malgre contexte positif")
                    # Retourner réponse corrigée simple et directe
                    # Extraire ville/département de la query
                    import re
                    dept_match = re.search(r'\b(91|94|78|77)\b', user_query)
                    if dept_match or any(d in user_query.lower() for d in ['91', '94', '78', '77', 'essonne', 'val-de-marne', 'yvelines', 'seine-et-marne']):
                        # Utiliser get_restaurant_info pour réponse structurée
                        dept = dept_match.group(1) if dept_match else user_query
                        corrected = self.get_restaurant_info(dept)
                        return corrected, False
                    # Sinon retourner message générique basé sur contexte
                    return "Oui, nous avons plusieurs restaurants en Île-de-France. Pour plus de détails sur un restaurant spécifique, précisez la ville ou le département.", False
        
        # 2. Vérifier incohérences horaires
        import re
        # Extraire horaires du contexte (format HH:MM-HH:MM)
        context_hours = re.findall(r'\d{1,2}:\d{2}-\d{1,2}:\d{2}', context)
        # Extraire horaires de la réponse (format HH:MM-HH:MM ou HHhMM-HHhMM)
        response_hours = re.findall(r'\d{1,2}[h:]?\d{2}\s?-\s?\d{1,2}[h:]?\d{2}', response)
        
        if context_hours and response_hours:
            # Normaliser pour comparaison
            def normalize_hour(h):
                # "11:30" ou "11h30" → "1130"
                return re.sub(r'[:\sh-]', '', h)
            
            context_normalized = set(normalize_hour(h) for h in context_hours)
            response_normalized = set(normalize_hour(h) for h in response_hours)
            
            # Si horaires complètement différents
            if context_normalized and not any(rh in ' '.join(context_normalized) for rh in response_normalized):
                print(f"[WARN] HALLUCINATION HORAIRES: Contexte={context_hours} vs Reponse={response_hours}")
                # Remplacer les horaires dans la réponse par ceux du contexte
                corrected = response
                for wrong_hour in response_hours:
                    # Remplacer par les vrais horaires du contexte
                    if context_hours:
                        corrected = corrected.replace(wrong_hour, context_hours[0])
                return corrected, False
        
        # 3. Vérifier cohérence département/ville
        dept_ville = {
            "91": "corbeil",
            "94": "ivry", 
            "78": "mureaux",
            "77": "lagny"
        }
        
        for dept, ville in dept_ville.items():
            # Si question mentionne département
            if dept in user_query.lower():
                # Mais réponse dit "pas de restaurant" ET contexte mentionne la ville
                if ville in context_lower and any(neg in response_lower for neg in ["pas de restaurant", "aucun restaurant"]):
                    print(f"[WARN] CONTRADICTION: Dit 'pas de resto' pour {dept} mais contexte contient {ville}")
                    # Utiliser get_restaurant_info pour réponse propre
                    corrected = self.get_restaurant_info(dept)
                    return corrected, False
        
        # 4. Vérifier prix aberrants
        context_prices = re.findall(r'(\d+[,.]?\d*)\s*€', context)
        response_prices = re.findall(r'(\d+[,.]?\d*)\s*€', response)
        
        if context_prices and response_prices:
            context_nums = [float(p.replace(',', '.')) for p in context_prices]
            response_nums = [float(p.replace(',', '.')) for p in response_prices]
            
            # Si prix dans réponse > 2x max du contexte
            if max(response_nums) > max(context_nums) * 2:
                print(f"[WARN] PRIX ABERRANT: Contexte max={max(context_nums)}€ vs Reponse max={max(response_nums)}€")
                # Corriger en remplaçant les prix aberrants
                corrected = response
                for i, wrong_price in enumerate(response_prices):
                    if i < len(context_prices):
                        corrected = corrected.replace(f"{wrong_price}€", f"{context_prices[i]}€")
                return corrected, False
        
        # Réponse valide
        return response, True
    
    def chat(self, user_message: str, conversation_id: Optional[str] = None) -> str:
        self.agent_state['total_interactions'] += 1
        
        context = self.plan_and_execute(user_message)
        
        # Charger dynamiquement les infos des restaurants
        restaurants = self.kb.get_all_restaurants()
        restaurants_info = []
        for resto in restaurants:
            # Extraire ville du nom "BOLKIRI {ville} Street Food Viêt"
            name = resto.get('name', '')
            ville = name.replace('BOLKIRI', '').replace('Street Food Viêt', '').strip()
            telephone = resto.get('telephone', 'N/A')
            adresse = resto.get('adresse', 'N/A')
            restaurants_info.append(f"  * {ville} - {adresse} - Tel: {telephone}")
        restaurants_list = "\n".join(restaurants_info)
        
        system_prompt = f"""Bolkiri Agentic AI Agent - RAG Architecture

LANGUAGE DETECTION: Detect query language → Respond in SAME language (French/English/Vietnamese/Spanish/any language).

AGENT CAPABILITIES:
- Tool calling: 8 available tools (search_knowledge, get_restaurants, get_menu, filter_menu, etc.)
- Multi-step reasoning: query decomposition → planning → tool execution → synthesis
- Conversational state: context memory (last 10 exchanges) - USE PREVIOUS CONTEXT FOR FOLLOW-UP QUERIES

EXECUTION PIPELINE:
1. Query analysis → Tool selection
2. Tool execution (max 3 parallel) → RAG context retrieval
3. Multi-source context aggregation
4. Context-based response generation
5. Anti-hallucination validation (4 types: restaurants/schedules/prices/departments)

CONVERSATIONAL RULES:
- If user says "yes"/"oui"/"okay" after a question → Execute the action they confirmed
- If previous message asked "would you like details?" and user says "yes" → Provide full details with tool execution
- Track conversation flow: user confirmation = execute promised action

RETRIEVED CONTEXT (RAG via tools)
{context}

GENERATION RULES:
- Context = absolute truth (never contradict)
- Schedules: exact format (11:30-14:30)
- LINKS: If context contains <a href="URL">text</a> → COPY EXACTLY (keep HTML tags)
- FORMAT: Plain text ONLY. NEVER use markdown syntax (**bold**, *italic*, __underline__). Write text directly without any formatting markers.
- OUT OF SCOPE: If context contains [HORS_PERIMETRE] → Inform user politely that info is not on website, suggest contacting restaurant directly

AGENTIC EXAMPLES:
Query "menu végé restaurant 91" → Tool 1: filter_menu(végétarien=True) + Tool 2: get_restaurant_info("91")
Query "do you have nems?" → English response + include HTML links from context
Query "yes" after asking "would you like details?" → Execute filter_menu or get_menu to list specific dishes

STYLE: First person plural, concise, LANGUAGE = detected query language.
"""

        self.conversation_memory.append({
            "role": "user",
            "content": user_message
        })
        
        messages = [
            {"role": "system", "content": system_prompt}
        ] + self.conversation_memory[-10:]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.1,  # Minimal pour cohérence tout en gardant un peu de naturel
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # VALIDATION AUTOMATIQUE de la réponse
            try:
                validated_message, is_valid = self._validate_response(assistant_message, context, user_message)
                
                if not is_valid:
                    print(f"[INVALID] Reponse invalidee, correction appliquee")
                    assistant_message = validated_message
                else:
                    print(f"[OK] Reponse validee")
            except Exception as e:
                print(f"[ERROR] Erreur validation: {e}")
                # En cas d'erreur validation, garder la réponse originale
            
            # POST-PROCESSING: Strip markdown syntax (bold, italic, underline)
            import re
            # Remove **bold**, __bold__
            assistant_message = re.sub(r'\*\*([^*]+)\*\*', r'\1', assistant_message)
            assistant_message = re.sub(r'__([^_]+)__', r'\1', assistant_message)
            # Remove *italic*, _italic_
            assistant_message = re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'\1', assistant_message)
            assistant_message = re.sub(r'(?<!_)_(?!_)([^_]+)(?<!_)_(?!_)', r'\1', assistant_message)
            
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
    
    def refresh_knowledge_from_web(self):
        """Rescrape le site et met à jour la KB"""
        try:
            print("[INFO] Rafraichissement base connaissances...")
            
            # Le scraper a déjà les données hardcodées dans extract_all_restaurants()
            # et extract_menu_complet() - pas besoin de scraper le site réel
            
            # On pourrait ajouter un vrai scraping ici si nécessaire
            # Pour l'instant, on recharge juste la KB enrichie
            
            self.kb = EnrichedKnowledgeBase()
            self.agent_state['last_update'] = datetime.now().isoformat()
            
            print(f"KB rafraichie: {len(self.kb.get_all_restaurants())} restaurants, {len(self.kb.get_all_menu_items())} plats")
            return True
            
        except Exception as e:
            print(f"Erreur refresh KB: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    agent = AIAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        website_url="https://bolkiri.fr"
    )
    
    print(f"\nAgent ready with {len(agent.kb.get_all_restaurants())} restaurants!\n")
    
    test_queries = [
        "Où êtes-vous situés dans le 91 ?",
        "Quels sont vos plats végétariens ?",
        "Quel est le prix du Phở Bò ?",
        "Quels sont vos horaires d'ouverture ?"
    ]
    
    for query in test_queries:
        print(f"User: {query}")
        response = agent.chat(query)
        print(f"Agent: {response}\n")
