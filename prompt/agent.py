FIELD_DETECTION_PROMPT = """
You are analyzing a natural language restaurant query. 

Given the user query below, determine whether each of the following elements is mentioned or not:

Answer in the following JSON format, mentioning words that you found as values:

Query: "한라산 등반 후 40대 부모님과 10대 아이의 가족이 함께 먹을 수 있는 중문 근처 5~6만원대 삼겹살집 추천해줘. 모수라는 식당도 있던데"
Answer:
{{
  "restaurant_name_mentioned": "모수",
  "price_mentioned": "5~6만원대",
  "location_mentioned": "중문",
  "menu_mentioned": "삼겹살",
  "attraction_mentioned": "한라산",
  "age_mentioned": "40대 부모님, 10대 아이",
  "visit_with_mentioned": "가족 (부모님과 아이)"
}}

Query: "60대 부모님과 갈만한 애월읍 식당"
Answer:
{{
  "restaurant_name_mentioned": "",
  "price_mentioned": "",
  "location_mentioned": "애월읍",
  "menu_mentioned": "",
  "attraction_mentioned": "한라산",
  "age_mentioned": "60대 부모님",
  "visit_with_mentioned": ""
}}

Query: "{query}"
Answer:
"""