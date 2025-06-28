import json
from llm_response.langgraph_graph_state import GraphState
from prompt.agent import FIELD_DETECTION_PROMPT
import streamlit as st

def field_detection(llm, state: GraphState) -> GraphState:
    st.markdown("## 🧠 Field Detection")
    
    query = state.get("rewritten_query") or state["query"]
    st.markdown(f"**Query**: `{query}`")

    prompt = FIELD_DETECTION_PROMPT.format(query=query)
    res = llm.invoke(prompt)

    try:
        res_json = eval(res.content.replace("```", "").replace("json", ""))
    except Exception as e:
        st.error(f"❌ Failed to parse field detection response: {e}")
        res_json = {}

    field_keys = [
        "restaurant_name_mentioned", "price_mentioned",
        "location_mentioned", "menu_mentioned",
        "attraction_mentioned", "age_mentioned",
        "visit_with_mentioned"
    ]
    for key in field_keys:
        state[key] = res_json.get(key, "no")

    display_detected_fields(state)

    return state




def display_detected_fields(state: GraphState):
    st.markdown("### 🧠 **Field Detection Result**")
    field_keys = [
        "restaurant_name_mentioned", "price_mentioned",
        "location_mentioned", "menu_mentioned",
        "attraction_mentioned", "age_mentioned",
        "visit_with_mentioned"
    ]
    for key in field_keys:
        value = state.get(key, "no")
        emoji = "✅" if value == "yes" else "❌"
        st.markdown(f"- **{key.replace('_', ' ').title()}**: {emoji} `{value}`")
