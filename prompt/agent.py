FIELD_DETECTION_PROMPT = """
You are analyzing a natural language restaurant query. 

Given the user query below, determine whether each of the following elements is mentioned or not:

Query: "{query}"

Answer in the following JSON format, using 'yes' or 'no' for each element:

{{
  "restaurant_name_mentioned": "...",
  "price_mentioned": "...",
  "location_mentioned": "...",
  "menu_mentioned": "...",
  "attraction_mentioned": "...",
  "age_mentioned": "...",
  "visit_with_mentioned": "..."
}}
"""