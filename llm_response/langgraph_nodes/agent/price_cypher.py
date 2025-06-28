from llm_response.langgraph_graph_state import GraphState
from prompt.cypher_tools.price import PRICE_CYPHER_PROMPT

def price_cypher(llm, state: GraphState) -> GraphState:
    if state.get("price_mentioned") != "yes":
        state.setdefault("field_conditions_summary", {})["price"] = "❌ not mentioned"
        return state

    query = state.get("rewritten_query") or state.get("query")
    prompt = PRICE_CYPHER_PROMPT.format(query=query)
    res = llm.invoke(prompt)
    cypher = res.content.replace("```cypher", "").replace("```", "").strip()

    if cypher:
        state.setdefault("field_cypher_parts", {})["price"] = cypher
        state.setdefault("field_conditions_summary", {})["price"] = "✅ price included"
    else:
        state.setdefault("field_conditions_summary", {})["price"] = "❌ not found"

    return state
