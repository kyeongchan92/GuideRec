from llm_response.langgraph_graph_state import GraphState
from prompt.cypher_tools.final_cypher_gen import FINAL_CYPHER_GENERATION_PROMPT


def build_final_cypher_from_parts(llm, state: GraphState) -> GraphState:
    parts = state.get("field_cypher_parts", {})
    rewritten_query = state.get("rewritten_query") or state["query"]

    print("\n" + "=" * 100)
    print("FINAL CYPHER GENERATION".center(100))
    print("=" * 100)
    print(f"Query             : {rewritten_query}")
    print(f"Detected Fields   : {', '.join(parts.keys()) if parts else 'None'}")
    print("-" * 100)

    print("Individual Field Conditions:")
    if parts:
        for k, v in parts.items():
            print(f"[{k.upper()}]".ljust(15) + "=> " + v.strip().replace("\n", " "))
    else:
        print("❌ No field-level Cypher conditions detected.")
    print("=" * 100)

    prompt = FINAL_CYPHER_GENERATION_PROMPT.format(
        query=rewritten_query,
        parts="\n".join(parts.values())
    )

    res = llm.invoke(prompt)
    final_cypher = res.content.strip().replace("```", "").replace("cypher", "")

    print("FINAL CYPHER QUERY".center(100))
    print("-" * 100)
    print(final_cypher)
    print("=" * 100 + "\n")

    state["t2c_for_recomm"] = final_cypher
    return state
