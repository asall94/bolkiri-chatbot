import pytest
from knowledge_base_enriched import EnrichedKnowledgeBase

def test_haversine_distance():
    """Test haversine distance calculation"""
    kb = EnrichedKnowledgeBase()
    
    # Paris to Lyon (approx 391 km straight line distance)
    distance = kb.haversine_distance(48.8566, 2.3522, 45.7640, 4.8357)
    assert 385 < distance < 400, f"Expected ~391km, got {distance}km"
    
    # Same point should be 0 km
    distance = kb.haversine_distance(48.8566, 2.3522, 48.8566, 2.3522)
    assert distance < 0.01, f"Expected ~0km, got {distance}km"

def test_find_nearest_restaurant_meudon():
    """Test finding nearest restaurant to Meudon"""
    kb = EnrichedKnowledgeBase()
    
    # Meudon is in 92 (Hauts-de-Seine)
    # Closest should be Boulogne-Billancourt or Malakoff
    result = kb.find_nearest_restaurant("Meudon")
    
    assert 'error' not in result
    assert 'restaurant' in result
    assert 'distance_km' in result
    assert result['distance_km'] < 15  # Should be within 15km

def test_find_nearest_restaurant_versailles():
    """Test finding nearest restaurant to Versailles"""
    kb = EnrichedKnowledgeBase()
    
    # Versailles is in 78
    # Closest should be Les Mureaux (78) or Boulogne-Billancourt (92)
    result = kb.find_nearest_restaurant("Versailles")
    
    assert 'error' not in result
    assert 'restaurant' in result
    assert result['distance_km'] < 30  # Should be within 30km

def test_find_nearest_restaurant_invalid_city():
    """Test with non-existent city"""
    kb = EnrichedKnowledgeBase()
    
    result = kb.find_nearest_restaurant("Nonexistentville")
    
    assert 'error' in result

def test_find_nearest_restaurant_returns_required_fields():
    """Test that result contains all required fields"""
    kb = EnrichedKnowledgeBase()
    
    result = kb.find_nearest_restaurant("Paris")
    
    if 'error' not in result:
        assert 'restaurant' in result
        assert 'ville' in result
        assert 'adresse' in result
        assert 'distance_km' in result
        assert isinstance(result['distance_km'], (int, float))
