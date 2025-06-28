from llm_response.langgraph_graph_state import GraphState
from prompt.cypher_tools.attraction import ATTRACTION_CYPHER_PROMPT

def attraction_cypher(llm, state: GraphState) -> GraphState:
    if state.get("attraction_mentioned") != "yes":
        state.setdefault("field_conditions_summary", {})["attraction"] = "❌ not mentioned"
        return state

    query = state.get("rewritten_query") or state.get("query")
    prompt = ATTRACTION_CYPHER_PROMPT.format(query=query)
    res = llm.invoke(prompt)
    cypher = res.content.replace("```cypher", "").replace("```", "").strip()

    if cypher:
        state.setdefault("field_cypher_parts", {})["attraction"] = cypher
        state.setdefault("field_conditions_summary", {})["attraction"] = "✅ attraction included"
    else:
        state.setdefault("field_conditions_summary", {})["attraction"] = "❌ not found"

    return state
