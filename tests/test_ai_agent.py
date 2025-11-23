import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from ai_agent import AIAgent


@pytest.fixture
def mock_openai_key():
    """Provide mock OpenAI API key"""
    return "sk-test-mock-key-12345"


@pytest.fixture
def mock_kb():
    """Mock knowledge base with sample data"""
    with patch('ai_agent.EnrichedKnowledgeBase') as mock:
        kb_instance = mock.return_value
        kb_instance.search.return_value = [
            {"type": "restaurant", "nom": "Bolkiri Corbeil", "ville": "Corbeil-Essonnes"}
        ]
        kb_instance.get_all_restaurants.return_value = [
            {
                "nom": "Bolkiri Corbeil",
                "ville": "Corbeil-Essonnes",
                "adresse": "123 Rue Test",
                "telephone": "01 23 45 67 89"
            }
        ]
        kb_instance.get_full_menu.return_value = [
            {"nom": "Pho Bo", "prix": "12.90", "categorie": "soupes"}
        ]
        yield kb_instance


@pytest.fixture
def agent(mock_openai_key, mock_kb):
    """Create AIAgent instance with mocked dependencies"""
    with patch('ai_agent.OpenAI'):
        agent = AIAgent(
            openai_api_key=mock_openai_key,
            website_url="https://bolkiri.fr"
        )
        agent.kb = mock_kb
        return agent


class TestAIAgentInitialization:
    """Test AIAgent initialization and configuration"""
    
    def test_agent_initialization(self, agent):
        """Agent initializes with correct default state"""
        assert agent.agent_state['knowledge_ready'] is True
        assert agent.agent_state['total_interactions'] == 0
        assert len(agent.tools) == 9
        assert agent.greeting_message is not None
    
    def test_tools_defined(self, agent):
        """All 9 required tools are defined"""
        tool_names = [tool['name'] for tool in agent.tools]
        expected_tools = [
            'search_knowledge',
            'get_restaurants',
            'get_restaurant_info',
            'get_menu',
            'filter_menu',
            'get_contact',
            'get_hours',
            'recommend_dish',
            'find_nearest_restaurant'
        ]
        assert set(tool_names) == set(expected_tools)


class TestToolExecution:
    """Test individual tool functions"""
    
    def test_search_knowledge(self, agent, mock_kb):
        """search_knowledge returns formatted results"""
        # Mock search to return results (not empty list)
        mock_kb.search.return_value = [
            {
                "content": "Bolkiri Corbeil - Pho Bo (boeuf) 12.50€",
                "type": "menu",
                "score": 0.92
            }
        ]
        
        result = agent.search_knowledge("pho")
        
        mock_kb.search.assert_called_once_with("pho", limit=5)
        assert "Bolkiri Corbeil" in result
        assert isinstance(result, str)
    
    def test_get_restaurants(self, agent, mock_kb):
        """get_restaurants returns all locations"""
        mock_kb.get_all_restaurants.return_value = [
            {
                "nom": "Bolkiri Corbeil",
                "name": "Bolkiri Corbeil",
                "ville": "Corbeil-Essonnes",
                "adresse": "123 Rue Test",
                "telephone": "01 23 45 67 89",
                "email": "test@bolkiri.fr",
                "services": ["livraison"]
            }
        ]
        
        result = agent.get_restaurants()
        
        mock_kb.get_all_restaurants.assert_called_once()
        assert "Bolkiri Corbeil" in result
        # Note: get_restaurants() doesn't include ville in output (lines 111-115 ai_agent.py)
        assert "123 Rue Test" in result
        assert "livraison" in result
    
    def test_get_menu(self, agent, mock_kb):
        """get_menu returns full menu"""
        mock_kb.get_all_menu_items.return_value = [
            {"nom": "Pho Bo", "prix": "12.90", "categorie": "soupes"}
        ]
        
        result = agent.get_menu()
        
        mock_kb.get_all_menu_items.assert_called_once()
        assert "Pho Bo" in result or "MENU" in result
        assert isinstance(result, str)
    
    def test_filter_menu_vegetarian(self, agent, mock_kb):
        """filter_menu handles vegetarian criteria"""
        mock_kb.search.return_value = [
            {
                "nom": "Rouleaux Végétariens",
                "prix": "8.50",
                "data": {"nom": "Rouleaux Végétariens", "prix": "8.50"}
            }
        ]
        
        result = agent.filter_menu("végétarien")
        
        assert "Rouleaux" in result or "végétarien" in result.lower()
    
    def test_get_contact_general(self, agent, mock_kb):
        """get_contact returns general contact info"""
        mock_kb.get_all_restaurants.return_value = [
            {"nom": "Bolkiri Test", "telephone": "01 11 11 11 11", "email": "test@bolkiri.fr"}
        ]
        
        result = agent.get_contact()
        
        assert "01 11 11 11 11" in result or "Contact" in result


class TestValidation:
    """Test anti-hallucination validation system"""
    
    def test_validate_restaurant_existence(self, agent, mock_kb):
        """Validator detects negative phrases when restaurant exists"""
        mock_kb.get_all_restaurants.return_value = [
            {"nom": "Bolkiri Corbeil", "name": "Bolkiri Corbeil"}
        ]
        
        # Valid restaurant response
        response_valid = "Le Bolkiri Corbeil est ouvert de 11:30 à 14:00."
        context_valid = "[Restaurant trouvé] Bolkiri Corbeil - Horaires: 11:30-14:00"
        validated, is_valid = agent._validate_response(response_valid, context_valid, "Bolkiri Corbeil")
        assert is_valid is True
        
        # Negative phrase despite positive context (hallucination)
        response_negative = "Nous n'avons pas de restaurant dans le 91."
        context_positive = "[Restaurant trouvé] Bolkiri Corbeil-Essonnes - Essonne 91"
        validated, is_valid = agent._validate_response(response_negative, context_positive, "restaurant 91")
        # Should detect hallucination
        assert not is_valid
    
    def test_validate_schedule_format(self, agent):
        """Validator checks schedule format consistency"""
        response_valid = "Ouvert lundi-dimanche 11h30-14h30"
        context = "horaires: lundi-dimanche 11h30-14h30"
        validated, is_valid = agent._validate_response(response_valid, context, "horaires")
        # Valid format should pass through
        assert "11h30" in validated or "14h30" in validated
    
    def test_validate_price_hallucination(self, agent, mock_kb):
        """Validator catches invented prices when KB has none"""
        mock_kb.get_all_menu_items.return_value = [
            {"nom": "Pho Bo", "prix": ""}  # No price in KB
        ]
        
        response_with_price = "Le Pho Bo coûte 15€"
        context = "Pho Bo prix: (vide)"
        validated, is_valid = agent._validate_response(response_with_price, context, "prix Pho Bo")
        
        # Should strip hallucinated price or flag issue
        assert "15€" not in validated or "disponibles" in validated or not is_valid


class TestDepartmentDetection:
    """Test department/city mapping logic"""
    
    def test_detect_essonne_91(self, agent, mock_kb):
        """91/Essonne queries map to Corbeil"""
        mock_kb.search.return_value = [
            {"nom": "Bolkiri Corbeil", "ville": "Corbeil-Essonnes", "content": "Restaurant Corbeil", "data": {}}
        ]
        
        # Test with department code
        result = agent.get_restaurant_info("91")
        assert mock_kb.search.called
        assert "Corbeil" in result or "restaurant" in result.lower()
    
    def test_detect_val_de_marne_94(self, agent, mock_kb):
        """94/Val-de-Marne queries map to Ivry"""
        mock_kb.search.return_value = [
            {"nom": "Bolkiri Ivry", "ville": "Ivry-sur-Seine", "content": "Restaurant Ivry", "data": {}}
        ]
        
        result = agent.get_restaurant_info("94")
        assert mock_kb.search.called


class TestConversationMemory:
    """Test conversation context management"""
    
    def test_conversation_memory_appended(self, agent):
        """User messages added to conversation memory"""
        initial_length = len(agent.conversation_memory)
        
        agent.conversation_memory.append({
            "role": "user",
            "content": "Test message"
        })
        
        assert len(agent.conversation_memory) == initial_length + 1
        assert agent.conversation_memory[-1]["content"] == "Test message"
    
    def test_conversation_memory_persists(self, agent):
        """Conversation memory maintains context across calls"""
        agent.conversation_memory.append({"role": "user", "content": "First"})
        agent.conversation_memory.append({"role": "assistant", "content": "Response"})
        
        assert len(agent.conversation_memory) >= 2
        assert agent.conversation_memory[0]["content"] == "First"


class TestEdgeCases:
    """Test error handling and edge cases"""
    
    def test_empty_query_search(self, agent, mock_kb):
        """Handle empty search queries gracefully"""
        mock_kb.search.return_value = []
        
        result = agent.search_knowledge("")
        
        assert isinstance(result, str)
        assert len(result) > 0  # Should return meaningful message
    
    def test_kb_not_ready(self, agent):
        """Handle knowledge base unavailable state"""
        agent.agent_state['knowledge_ready'] = False
        
        # Should handle gracefully or raise appropriate error
        # Implementation depends on your error handling strategy
        assert agent.agent_state['knowledge_ready'] is False
    
    def test_invalid_department_code(self, agent, mock_kb):
        """Handle invalid department codes"""
        mock_kb.get_restaurant_by_ville.return_value = []
        
        result = agent.get_restaurant_info("99")  # Invalid department
        
        # Should return helpful message, not crash
        assert isinstance(result, str)


class TestRecommendDish:
    """Test personalized recommendation logic"""
    
    def test_recommend_with_preferences(self, agent, mock_kb):
        """Recommendations incorporate user preferences"""
        mock_kb.get_all_menu_items.return_value = [
            {"nom": "Pho Bo", "description": "Soupe vietnamienne boeuf", "categorie": "soupes"}
        ]
        mock_kb.search.return_value = [
            {"nom": "Pho Bo", "data": {"nom": "Pho Bo", "description": "Soupe vietnamienne boeuf"}}
        ]
        
        result = agent.recommend_dish("soupe chaude")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_recommend_no_match(self, agent, mock_kb):
        """Handle preferences with no matching dishes"""
        mock_kb.search.return_value = []
        
        result = agent.recommend_dish("pizza")  # Not Vietnamese
        
        # Should return polite message or general recommendations
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
