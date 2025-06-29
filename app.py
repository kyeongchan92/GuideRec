import os
import streamlit as st
import pandas as pd
import numpy as np
from graphrag.retriever import get_neo4j_vector, retrieve_store_nodes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from llm_response.make_response import get_llm_response
from llm_response.langgraph_app import app, GraphState
from langchain_core.runnables import RunnableConfig
from utils import add_recomm_query, get_init_recomm_query
    

print("APP START!")


st.title("혼저 옵서예!👋")
st.subheader("\"잘도 맛있수다!\"가 절로 나오는 제주도 맛집 추천 🍊")
st.write("")
st.write("여행 구성원 유형(가족, 친구 등) 및 연령대에 맞춘 제주도 맛집 추천해드려요")
st.write("")
with st.sidebar:
    st.title("🍊참신한! 제주 맛집")

print(f"{st.session_state.keys()}")

if 'query' not in st.session_state:
    st.session_state.query = None

if 'similar_query' not in st.session_state:
    st.session_state.similar_query = get_init_recomm_query()

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}]


# Display or clear chat messages
messages_len = len(st.session_state.messages)
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
        # if i == (messages_len-1):
        #     col1, col2 = st.columns(2)
        #     query1, query2 = st.session_state.similar_query
        #     with col1:
        #         if st.button(query1):
        #             st.session_state.messages.append({"role": "user", "content": query1})
        #             st.session_state.query = query1
        #     with col2:
        #         if st.button(query2):
        #             st.session_state.messages.append({"role": "user", "content": query2})
        #             st.session_state.query = query2
        

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    
if query := st.chat_input("Say something"):
    st.session_state.query = query
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)


config = RunnableConfig(recursion_limit=20, configurable={"thread_id": "movie"})
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # LangGraph 실행
            gs = GraphState(query=st.session_state.query, messages=st.session_state.messages)
            result_gs = app.invoke(gs, config=config)

        # 결과 메시지 출력
        if result_gs['final_answer']:
            st.markdown(result_gs['final_answer'], unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": result_gs['final_answer']})

        # ===== 🔍 Cypher 쿼리 & 그래프 시각화 =====
        if 't2c_for_recomm' in result_gs:
            st.markdown("## 🧠 생성된 Cypher 쿼리")
            st.code(result_gs['t2c_for_recomm'], language="cypher")

            from neo4j.graph import Node, Relationship
            from pyvis.network import Network
            import streamlit.components.v1 as components
            from utils import graphdb_driver

            def run_cypher_and_extract_elements(graphdb_driver, cypher: str):
                result = graphdb_driver.execute_query(cypher)
                nodes = set()
                edges = []
                for record in result.records:
                    for value in record.values():
                        if isinstance(value, Node):
                            nodes.add(value)
                        elif isinstance(value, Relationship):
                            edges.append((value.start_node.id, value.end_node.id, value.type))
                return list(nodes), edges

            def draw_graph_pyvis(nodes, edges):
                net = Network(height="600px", width="100%", notebook=False)
                for node in nodes:
                    net.add_node(node.id, label=node.get("MCT_NM") or node.get("name") or str(node.id), title=str(dict(node)))
                for start, end, rel in edges:
                    net.add_edge(start, end, label=rel)
                net.save_graph("graph.html")
                components.html(open("graph.html", "r", encoding="utf-8").read(), height=650)

            st.markdown("## 🕸️ 탐색된 그래프 시각화")
            nodes, edges = run_cypher_and_extract_elements(graphdb_driver, result_gs['t2c_for_recomm'])
            draw_graph_pyvis(nodes, edges)
