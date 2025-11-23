from typing import List, Dict, Optional, Tuple
from openai import OpenAI
import json
from datetime import datetime
from knowledge_base_enriched import EnrichedKnowledgeBase
from logger_config import setup_logger

# Setup structured JSON logging
logger = setup_logger(__name__)

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
            },
            {
                "name": "find_nearest_restaurant",
                "description": "Trouve le restaurant Bolkiri le plus proche d'une ville donnée en utilisant les coordonnées GPS",
                "parameters": {"ville_reference": "Nom de la ville de référence"}
            }
        ]
    
    def search_knowledge(self, query: str) -> str:
        """Enriched search across entire knowledge base - auto-detects department"""
        import re
        
        # Department detection in query
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
        
        # Check if department mentioned
        for dept, ville in dept_mapping.items():
            if dept in query_lower or re.search(rf'\b{dept}\b', query_lower):
                # Force search on this city
                query = f"{query} {ville}"
                break
        
        results = self.kb.search(query, limit=5)
        
        if not results:
            return "[HORS_PERIMETRE] Cette information n'est pas disponible sur notre site web. Pour des questions spécifiques (parking, événements, réservations privées...), contactez directement le restaurant concerné."
        
        context = []
        for result in results:
            # RAG already returns formatted content as string
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
        """Detailed info for specific restaurant - supports department and postal code"""
        # Use RAG for intelligent search
        results = self.kb.search(f"restaurant {ville}", limit=3)
        
        if not results:
            # List all available restaurants
            all_restos = self.kb.get_all_restaurants()
            return f"Restaurant non trouvé pour '{ville}'.\n\n" + \
                   f"NOS {len(all_restos)} RESTAURANTS DISPONIBLES:\n" + \
                   "\n".join([f"- {r.get('name', 'N/A')}" for r in all_restos[:10]]) + \
                   "\n\n(10 premiers restaurants affichés)"
        
        # Take best result
        best_result = results[0]
        return f"[RESTAURANT TROUVE]\n\n{best_result.get('content', 'Information non disponible')}"
    
    def get_menu(self) -> str:
        """Complete menu with categories"""
        menu = self.kb.get_all_menu_items()
        
        if not menu:
            return "Menu non disponible pour le moment."
        
        # Group by category
        categories = {}
        for plat in menu:
            cat = plat.get('categorie', 'Autres')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(plat)
        
        result = "MENU BOLKIRI\n\n"
        
        for cat, plats in categories.items():
            result += f"━━━ {cat.upper()} ━━━\n\n"
            for plat in plats[:5]:  # Limit to avoid overload
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
        """Intelligent menu filtering"""
        criteria_lower = criteria.lower()
        
        # Detect filters
        vegetarien = 'végétarien' in criteria_lower or 'vegetarien' in criteria_lower or 'veggie' in criteria_lower
        vegan = 'vegan' in criteria_lower
        sans_gluten = 'sans gluten' in criteria_lower or 'gluten' in criteria_lower
        epice = 'épicé' in criteria_lower or 'epice' in criteria_lower or 'piquant' in criteria_lower
        
        # Extract max price
        import re
        prix_match = re.search(r'(\d+)\s*€', criteria)
        prix_max = float(prix_match.group(1)) if prix_match else None
        
        # For vegetarian/vegan, use RAG search (KB has tags, not structured fields)
        if vegetarien or vegan:
            search_term = "végétarien" if vegetarien else "vegan"
            results = self.kb.search(f"plat {search_term} menu", limit=10)
            
            if not results:
                return f"Aucun plat trouvé correspondant à: {criteria}"
            
            result = f"Plats correspondant à '{criteria}':\n\n"
            for item in results[:10]:
                content = item.get('content', '')
                # Extract dish name from content (first line usually)
                lines = content.split('\n')
                dish_name = lines[0] if lines else content[:50]
                result += f"• {dish_name}\n"
                if len(content) > 100:
                    result += f"  {content[50:150]}...\n"
                result += "\n"
            
            return result
        
        # For other filters, use structured filtering
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
            
            # Handle missing contact info explicitly
            tel = contact.get('telephone', '').strip()
            email = contact.get('email', '').strip()
            result += f"Téléphone: {tel if tel else 'Non renseigné sur le site'}\n"
            result += f"Email: {email if email else 'Non renseigné sur le site'}\n"
            result += f"Services: {', '.join(contact.get('services', []))}\n\n"
            
            # Add link if available
            if contact.get('url'):
                result += f"Plus d'infos: {contact['url']}"
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
    
    def find_nearest_restaurant(self, ville_reference: str) -> str:
        """Find nearest Bolkiri restaurant from a reference city"""
        result = self.kb.find_nearest_restaurant(ville_reference)
        
        if result.get('error'):
            return f"[ERREUR] {result['error']}\n\nVoici la liste de tous nos restaurants:\n{self.get_restaurants()}"
        
        output = f"RESTAURANT LE PLUS PROCHE DE {ville_reference.upper()}\n\n"
        output += f"Restaurant: {result['restaurant']}\n"
        output += f"Ville: {result['ville']}\n"
        output += f"Distance: {result['distance_km']} km\n"
        output += f"Adresse: {result['adresse']}\n"
        
        if result.get('telephone'):
            output += f"Téléphone: {result['telephone']}\n"
        if result.get('url'):
            output += f"Plus d'infos: {result['url']}\n"
        
        return output
    
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
                # Display ALL days, not just a sample
                for jour, horaire in resto_hours.get('horaires', {}).items():
                    result += f"  {jour.capitalize()} : {horaire}\n"
                result += "\n"
        
        return result
    
    def recommend_dish(self, preferences: str) -> str:
        """Intelligent recommendations"""
        preferences_lower = preferences.lower()
        
        # Detect vegetarian, spicy, etc.
        vegetarien = 'végétarien' in preferences_lower or 'vegetarien' in preferences_lower
        epice = 'épicé' in preferences_lower or 'epice' in preferences_lower
        
        # Filter
        menu = self.kb.filter_menu(vegetarien=vegetarien if vegetarien else None)
        
        # Score according to preferences
        recommendations = []
        for plat in menu:
            score = 0
            plat_text = (plat.get('nom', '') + ' ' + plat.get('description', '')).lower()
            
            # Score based on keywords
            for word in preferences_lower.split():
                if len(word) > 2 and word in plat_text:
                    score += 2
            
            # Bonus for signature dishes
            if plat.get('signature'):
                score += 5
            
            # Bonus if spicy requested
            if epice and plat.get('epice') in ['Épicé', 'Moyen']:
                score += 5
            
            if score > 0:
                recommendations.append((plat, score))
        
        # Sort
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        if not recommendations:
            # Recommend signatures by default - return context for LLM
            signatures = self.kb.get_plats_signatures()
            if signatures:
                result = "SIGNATURE DISHES:\n\n"
                for plat in signatures[:3]:
                    result += f"• {plat['nom']} - {plat['prix']}\n"
                    result += f"  {plat.get('description', '')}\n\n"
                return result
            else:
                return "Authentic Vietnamese specialties available."
        
        result = "RECOMMENDED DISHES:\n\n"
        for plat, _ in recommendations[:3]:
            result += f"• {plat['nom']}"
            if plat.get('nom_vietnamien'):
                result += f" ({plat['nom_vietnamien']})"
            result += f" - {plat['prix']}\n"
            result += f"   {plat.get('description', '')}\n"
            
            # Why recommended
            raisons = []
            if plat.get('signature'):
                raisons.append('Signature dish')
            if plat.get('vegetarien') and vegetarien:
                raisons.append('Vegetarian')
            if plat.get('epice') and epice:
                raisons.append(f'{plat["epice"]}')
            
            if raisons:
                result += f"   Reasons: {', '.join(raisons)}\n"
            result += "\n"
        
        return result
        
        return result
    
    def execute_tool(self, tool_name: str, parameters: Dict) -> str:
        """Execute tool with enriched tool set"""
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
        elif tool_name == "find_nearest_restaurant":
            return self.find_nearest_restaurant(parameters.get("ville_reference", ""))
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
        """Validate generated response against context and detect hallucinations
        
        Returns:
            (corrected_response, is_valid)
        """
        response_lower = response.lower()
        context_lower = context.lower()
        
        # 1. Check restaurant contradictions
        if "[restaurant trouvé]" in context_lower or "restaurant" in context_lower:
            # Detect negative phrases when restaurant exists
            negative_phrases = [
                "n'avons pas de restaurant",
                "pas de restaurant dans",
                "aucun restaurant dans",
                "malheureusement pas",
                "ne disposons pas"
            ]
            
            for phrase in negative_phrases:
                if phrase in response_lower:
                    logger.warning("Restaurant hallucination detected", extra={"phrase": phrase, "validation_result": "negative_phrase_despite_positive_context"})
                    # Return simple and direct corrected response
                    # Extract city/department from query
                    import re
                    dept_match = re.search(r'\b(91|94|78|77)\b', user_query)
                    if dept_match or any(d in user_query.lower() for d in ['91', '94', '78', '77', 'essonne', 'val-de-marne', 'yvelines', 'seine-et-marne']):
                        # Use get_restaurant_info for structured response
                        dept = dept_match.group(1) if dept_match else user_query
                        corrected = self.get_restaurant_info(dept)
                        return corrected, False
                    # Otherwise return generic message based on context
                    return "Oui, nous avons plusieurs restaurants en Île-de-France. Pour plus de détails sur un restaurant spécifique, précisez la ville ou le département.", False
        
        # 2. Check schedule inconsistencies
        import re
        # Extract hours from context (format HH:MM-HH:MM)
        context_hours = re.findall(r'\d{1,2}:\d{2}-\d{1,2}:\d{2}', context)
        # Extract hours from response (format HH:MM-HH:MM or HHhMM-HHhMM)
        response_hours = re.findall(r'\d{1,2}[h:]?\d{2}\s?-\s?\d{1,2}[h:]?\d{2}', response)
        
        if context_hours and response_hours:
            # Normalize for comparison
            def normalize_hour(h):
                # "11:30" or "11h30" → "1130"
                return re.sub(r'[:\sh-]', '', h)
            
            context_normalized = set(normalize_hour(h) for h in context_hours)
            response_normalized = set(normalize_hour(h) for h in response_hours)
            
            # If completely different hours
            if context_normalized and not any(rh in ' '.join(context_normalized) for rh in response_normalized):
                logger.warning("Schedule hallucination detected", extra={"context_hours": context_hours, "response_hours": response_hours})
                # Replace hours in response with context hours
                corrected = response
                for wrong_hour in response_hours:
                    # Replace with real context hours
                    if context_hours:
                        corrected = corrected.replace(wrong_hour, context_hours[0])
                return corrected, False
        
        # 3. Check department/city coherence
        dept_ville = {
            "91": "corbeil",
            "94": "ivry", 
            "78": "mureaux",
            "77": "lagny"
        }
        
        for dept, ville in dept_ville.items():
            # If question mentions department
            if dept in user_query.lower():
                # But response says "no restaurant" AND context mentions the city
                if ville in context_lower and any(neg in response_lower for neg in ["pas de restaurant", "aucun restaurant"]):
                    logger.warning("Department contradiction detected", extra={"department": dept, "ville": ville})
                    # Use get_restaurant_info for clean response
                    corrected = self.get_restaurant_info(dept)
                    return corrected, False
        
        # 4. Check aberrant or hallucinated prices
        context_prices = re.findall(r'(\d+[,.]?\d*)\s*€', context)
        response_prices = re.findall(r'(\d+[,.]?\d*)\s*€', response)
        
        # If response mentions prices BUT context has NONE → Hallucination
        if response_prices and not context_prices:
            logger.warning("Price hallucination detected", extra={"response_prices": response_prices, "context_empty": True})
            # Replace all prices with generic message
            corrected = re.sub(r'\d+[,.]?\d*\s*€', '', response)
            corrected += "\n\nPrix disponibles sur la carte en restaurant. Contactez-nous pour plus d'informations."
            return corrected.strip(), False
        
        if context_prices and response_prices:
            context_nums = [float(p.replace(',', '.')) for p in context_prices]
            response_nums = [float(p.replace(',', '.')) for p in response_prices]
            
            # If price in response > 2x max of context
            if max(response_nums) > max(context_nums) * 2:
                logger.warning("Aberrant price detected", extra={"context_max": max(context_nums), "response_max": max(response_nums)})
                # Correct by replacing aberrant prices
                corrected = response
                for i, wrong_price in enumerate(response_prices):
                    if i < len(context_prices):
                        corrected = corrected.replace(f"{wrong_price}€", f"{context_prices[i]}€")
                return corrected, False
        
        # Valid response
        return response, True
    
    def chat(self, user_message: str, conversation_id: Optional[str] = None) -> str:
        self.agent_state['total_interactions'] += 1
        
        context = self.plan_and_execute(user_message)
        
        # Dynamically load restaurant info
        restaurants = self.kb.get_all_restaurants()
        restaurants_info = []
        for resto in restaurants:
            # Extract city from name "BOLKIRI {city} Street Food Viêt"
            name = resto.get('name', '')
            ville = name.replace('BOLKIRI', '').replace('Street Food Viêt', '').strip()
            telephone = resto.get('telephone', 'N/A')
            adresse = resto.get('adresse', 'N/A')
            restaurants_info.append(f"  * {ville} - {adresse} - Tel: {telephone}")
        restaurants_list = "\n".join(restaurants_info)
        
        system_prompt = f"""AGENTIC AI SYSTEM - Tool-First RAG Architecture

CRITICAL: You are a TOOL-CALLING agent. Always use tools to retrieve context before responding. Never answer from memory.

LANGUAGE: Auto-detect query language (French/English/Vietnamese). Respond in SAME language detected.

AVAILABLE TOOLS (use these first):
1. search_knowledge(query) - Semantic search across all KB
2. get_restaurants() - List all 20 restaurant locations
3. get_menu() - Full menu with prices
4. filter_menu(vegetarian=True/False, vegan=True/False) - Filtered dishes
5. get_restaurant_info(city_or_dept) - Specific location details
6. recommend_dish(preferences) - Personalized suggestions
7. get_contact() - Contact information
8. detect_department(query) - Extract department code from query

AGENTIC WORKFLOW:
Step 1: Analyze query intent
Step 2: Select 1-3 relevant tools
Step 3: Execute tools to retrieve RAG context
Step 4: Synthesize response from retrieved context ONLY
Step 5: Automatic validation (restaurants/schedules/prices/departments)

RETRIEVED CONTEXT FROM TOOLS:
{context}

GENERATION CONSTRAINTS:
- Context is absolute source of truth. Never contradict retrieved data.
- If context empty or contains [HORS_PERIMETRE]: Inform user information not available on website, suggest direct contact.
- Schedules: Use exact format from context (11:30-14:30). If missing: "Horaires disponibles directement en restaurant."
- Prices: Only mention if present in context. If missing: "Prix disponibles sur la carte en restaurant."
- Links: If context has HTML tags <a href>, copy EXACTLY as-is (preserve HTML).
- Format: Plain text only. NO markdown syntax (no bold/italic/underline markers).

MULTI-STEP REASONING EXAMPLES:
Query "vegetarian menu in Essonne" → detect_department("Essonne") → filter_menu(vegetarian=True) + get_restaurant_info("91") → synthesize
Query "do you have spring rolls" → search_knowledge("spring rolls") → extract dishes → respond with HTML links from context
Query "yes" (after confirmation request) → execute previously suggested action (get_menu or filter_menu)

RESPONSE STYLE: First-person plural, concise, conversational. Respect detected language.
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
                temperature=0.1,  # Minimal for consistency while keeping some naturalness
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # AUTOMATIC RESPONSE VALIDATION
            try:
                validated_message, is_valid = self._validate_response(assistant_message, context, user_message)
                
                if not is_valid:
                    logger.info("Response corrected by validator", extra={"validation_result": "invalid_corrected"})
                    assistant_message = validated_message
                else:
                    logger.info("Response validated successfully", extra={"validation_result": "valid"})
            except Exception as e:
                logger.error("Validation error", extra={"error_type": type(e).__name__}, exc_info=True)
                # In case of validation error, keep original response
            
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
            logger.error("OpenAI API error", extra={"error_type": type(e).__name__, "error_message": str(e)}, exc_info=True)
            return f"Désolé, une erreur est survenue. Veuillez réessayer."
    
    def refresh_knowledge_from_web(self):
        """Rescrape website and update KB"""
        try:
            logger.info("Refreshing knowledge base...")
            
            # Scraper already has hardcoded data in extract_all_restaurants()
            # and extract_menu_complet() - no need to scrape real site
            
            # Could add real scraping here if necessary
            # For now, just reload enriched KB
            
            self.kb = EnrichedKnowledgeBase()
            self.agent_state['last_update'] = datetime.now().isoformat()
            
            restaurant_count = len(self.kb.get_all_restaurants())
            menu_count = len(self.kb.get_all_menu_items())
            logger.info("Knowledge base refreshed successfully", extra={"restaurant_count": restaurant_count, "menu_count": menu_count})
            return True
            
        except Exception as e:
            logger.error("KB refresh failed", extra={"error_type": type(e).__name__}, exc_info=True)
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
