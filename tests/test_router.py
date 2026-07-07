from app.router import route_intent


def test_router_maps_intent_to_tool():
    result = route_intent("search")
    assert result["route_to"] == "web_search"
    assert result["reason"]
