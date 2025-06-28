from typing import Dict, List, TypedDict


class GraphState(TypedDict):
    query: str
    # query_type: str
    # subtype: str
    rewritten_query: List[str]
    # similar_query: List[str]
    # t2c_for_search: str
    record_dict_lst: List[Dict]
    messages: List[Dict]
    t2c_for_recomm: str
    candidate_str: str
    selected_recommendations: Dict
    final_answer: str

    # Field detection 결과
    restaurant_name_mentioned: str  # "yes" or "no"
    price_mentioned: str
    location_mentioned: str
    menu_mentioned: str
    attraction_mentioned: str
    age_mentioned: str
    visit_with_mentioned: str
    
    field_cypher_parts: Dict[str, str]  # 각 필드별 Cypher
    field_conditions_summary: Dict[str, str]  # UI용 상태 메시지
