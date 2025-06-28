from llm_response.langgraph_graph_state import GraphState
from prompt.cypher_tools.restaurant_name import RESTAURANT_NAME_CYPHER_PROMPT

def restaurant_name_cypher(llm, state: GraphState) -> GraphState:
    if state.get("restaurant_name_mentioned") != "yes":
        state.setdefault("field_conditions_summary", {})["restaurant_name"] = "❌ not mentioned"
        return state

    query = state.get("rewritten_query") or state.get("query")
    prompt = RESTAURANT_NAME_CYPHER_PROMPT.format(query=query)
    res = llm.invoke(prompt)
    cypher = res.content.replace("```cypher", "").replace("```", "").strip()

    if cypher:
        state.setdefault("field_cypher_parts", {})["restaurant_name"] = cypher
        state.setdefault("field_conditions_summary", {})["restaurant_name"] = "✅ restaurant_name included"
    else:
        state.setdefault("field_conditions_summary", {})["restaurant_name"] = "❌ not found"

    return state
