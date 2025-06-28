from llm_response.langgraph_graph_state import GraphState
from prompt.cypher_tools.location import LOCATION_CYPHER_PROMPT

def location_cypher(llm, state: GraphState) -> GraphState:
    if state.get("location_mentioned") != "yes":
        state.setdefault("field_conditions_summary", {})["location"] = "❌ not mentioned"
        return state

    query = state.get("rewritten_query") or state.get("query")
    prompt = LOCATION_CYPHER_PROMPT.format(query=query)
    res = llm.invoke(prompt)
    cypher = res.content.replace("```cypher", "").replace("```", "").strip()

    if cypher:
        state.setdefault("field_cypher_parts", {})["location"] = cypher
        state.setdefault("field_conditions_summary", {})["location"] = "✅ location included"
    else:
        state.setdefault("field_conditions_summary", {})["location"] = "❌ not found"

    return state
