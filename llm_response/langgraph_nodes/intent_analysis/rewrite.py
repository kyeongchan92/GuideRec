from llm_response.langgraph_graph_state import GraphState
from prompt.routing_and_intent_analysis import REWRITE_PROMPT
import streamlit as st

def rewrite(llm, state: GraphState):
    st.markdown("### 🛠️ **Query Rewriting**")
    st.code(f"Original Query = {state['query']}", language="text")

    with st.spinner("Rewriting in progress..."):
        res = llm.invoke(REWRITE_PROMPT.format(query=state["query"]))
    
    # 토큰 수
    # token_info = res.usage_metadata.get("input_tokens", "N/A")
    # st.markdown(f"`🔢 Token Count:` {token_info}")

    try:
        res_json = eval(res.content.replace("```", "").replace("json", ""))
    except Exception as e:
        st.error(f"⚠️ Failed to parse rewritten response: {e}")
        res_json = {}

    rewritten = res_json.get("rewritten_query", state["query"])
    state["rewritten_query"] = rewritten

    st.success(f"✅ Rewritten Query = {rewritten}")
    return state
