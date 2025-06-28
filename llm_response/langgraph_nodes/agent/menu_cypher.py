from llm_response.langgraph_graph_state import GraphState
from prompt.cypher_tools.menu import MENU_CYPHER_PROMPT

def menu_cypher(llm, state: GraphState) -> GraphState:
    if state.get("menu_mentioned") != "yes":
        state.setdefault("field_conditions_summary", {})["menu"] = "❌ not mentioned"
        return state

    query = state.get("rewritten_query") or state.get("query")
    prompt = MENU_CYPHER_PROMPT.format(query=query)
    res = llm.invoke(prompt)
    cypher = res.content.replace("```cypher", "").replace("```", "").strip()

    if cypher:
        state.setdefault("field_cypher_parts", {})["menu"] = cypher
        state.setdefault("field_conditions_summary", {})["menu"] = "✅ menu included"
    else:
        state.setdefault("field_conditions_summary", {})["menu"] = "❌ not found"

    return state
