import json
import os
import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
from graphrag.retriever import get_neo4j_vector, retrieve_store_nodes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from llm_response.make_response import get_llm_response
from llm_response.langgraph_app import app, GraphState
from langchain_core.runnables import RunnableConfig
from utils import add_recomm_query, get_init_recomm_query
import streamlit.components.v1 as components

# 예시 노드/링크 데이터
graph_data = {
    "nodes": [
        {"id": "맛집A", "citationCount": 10},
        {"id": "맛집B", "citationCount": 5},
        {"id": "관광지", "citationCount": 8},
    ],
    "links": [
        {"source": "맛집A", "target": "관광지", "type": "NEAR"},
        {"source": "맛집B", "target": "관광지", "type": "NEAR"},
    ],
}

# 개선된 CSS 스타일
st.markdown(
    """
    <style>
    /* 전체 페이지 설정 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
        height: 100vh;
        overflow: hidden;
    }
    
    /* 컬럼 높이 설정 */
    .stColumn {
        height: calc(100vh - 100px);
        overflow: hidden;
    }
    
    /* 왼쪽 컬럼 (채팅) */
    .stColumn:first-child {
        display: flex;
        flex-direction: column;
        padding-right: 1rem;
    }
    
    /* 오른쪽 컬럼 (그래프) */
    .stColumn:last-child {
        display: flex;
        flex-direction: column;
        padding-left: 1rem;
        border-left: 1px solid #e0e0e0;
    }
    
    /* 헤더 영역 */
    .main-header {
        flex-shrink: 0;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* 채팅 영역 컨테이너 */
    .chat-container {
        flex-grow: 1;
        overflow-y: auto;
        padding: 1rem 0;
        margin-bottom: 1rem;
        max-height: calc(100vh - 300px);
    }
    
    /* 채팅 입력창 */
    .stChatInput {
        flex-shrink: 0;
        position: sticky;
        bottom: 0;
        background: white;
        padding: 1rem 0;
        border-top: 1px solid #e0e0e0;
        z-index: 100;
    }
    
    /* 채팅 메시지 */
    .stChatMessage {
        margin-bottom: 1rem;
    }
    
    /* 그래프 영역 */
    .graph-container {
        flex-grow: 1;
        height: 100%;
        overflow: hidden;
    }
    
    /* 스크롤바 커스텀 */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* 그래프 제목 */
    .graph-title {
        flex-shrink: 0;
        padding: 1rem 0;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}
    ]

print("APP START!")

# 컬럼 레이아웃
left_col, right_col = st.columns([3, 2])

with left_col:
    # 헤더 영역
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("Welcome to Jeju!👋")
    st.subheader("Jeju food so good, you'll say 'Wow, that's delicious!' 🍊")
    st.write("Get personalized restaurant recommendations in Jeju based on your travel crew and age group.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 세션 상태 초기화
    if "query" not in st.session_state:
        st.session_state.query = None

    if "similar_query" not in st.session_state:
        st.session_state.similar_query = get_init_recomm_query()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}
        ]

    # 채팅 영역 컨테이너
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # 채팅 기록 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 채팅 입력 (항상 하단에 고정)
    if query := st.chat_input("Say something"):
        st.session_state.query = query
        st.session_state.messages.append({"role": "user", "content": query})
        
        # 새 메시지 추가 후 자동 스크롤을 위해 rerun
        st.rerun()

    # LangGraph 실행 및 응답 처리
    config = RunnableConfig(recursion_limit=20, configurable={"thread_id": "movie"})
    if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
        with st.spinner("Thinking..."):
            gs = GraphState(
                query=st.session_state.query,
                messages=st.session_state.messages
            )
            result_gs = app.invoke(gs, config=config)

        if result_gs.get("final_answer"):
            st.session_state.messages.append(
                {"role": "assistant", "content": result_gs["final_answer"]}
            )
            st.rerun()

        # Cypher 쿼리 결과 처리
        if "t2c_for_recomm" in result_gs:
            st.markdown("## 🧠 생성된 Cypher 쿼리")
            st.code(result_gs["t2c_for_recomm"], language="cypher")

            from neo4j.graph import Node, Relationship
            from pyvis.network import Network
            from utils import graphdb_driver

            def run_cypher_and_extract_elements(driver, cypher):
                result = driver.execute_query(cypher)
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
                    net.add_node(
                        node.id,
                        label=node.get("MCT_NM") or node.get("name") or str(node.id),
                        title=str(dict(node)),
                    )
                for start, end, rel in edges:
                    net.add_edge(start, end, label=rel)
                net.save_graph("graph.html")
                components.html(open("graph.html", "r", encoding="utf-8").read(), height=650)

            nodes, edges = run_cypher_and_extract_elements(graphdb_driver, result_gs["t2c_for_recomm"])
            st.markdown("## 🕸️ 탐색된 그래프 시각화")
            draw_graph_pyvis(nodes, edges)

with right_col:
    # 그래프 제목
    st.markdown('<div class="graph-title">', unsafe_allow_html=True)
    st.markdown("### 🕸️ Knowledge Graph")
    st.markdown("Interactive visualization of restaurant relationships")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 그래프 영역
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    
    # 개선된 D3.js 그래프
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body, html {{
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
            }}
            svg {{
                width: 100%;
                height: 100%;
                display: block;
            }}
            .links line {{
                stroke: #999;
                stroke-opacity: 0.6;
                stroke-width: 2px;
            }}
            .nodes circle {{
                stroke: #fff;
                stroke-width: 1.5px;
                cursor: pointer;
            }}
            .nodes text {{
                font: 12px sans-serif;
                pointer-events: none;
                text-anchor: middle;
                dominant-baseline: middle;
            }}
            .tooltip {{
                position: absolute;
                padding: 10px;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                border-radius: 5px;
                pointer-events: none;
                font-size: 12px;
                z-index: 1000;
            }}
        </style>
    </head>
    <body>
        <svg id="graph"></svg>
        <div class="tooltip" style="opacity: 0;"></div>
        <script>
            const data = {json.dumps(graph_data)};
            
            // SVG 설정
            const svg = d3.select("#graph");
            const width = window.innerWidth * 0.4; // 우측 컬럼 너비에 맞춤
            const height = window.innerHeight * 0.8; // 높이 조정
            
            svg.attr("width", width).attr("height", height);
            
            // 색상 스케일
            const color = d3.scaleOrdinal(d3.schemeCategory10);
            
            // 반지름 스케일
            const radiusScale = d3.scaleSqrt()
                .domain([0, d3.max(data.nodes, d => d.citationCount)])
                .range([15, 50]);
            
            // 시뮬레이션 설정
            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-400))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(d => radiusScale(d.citationCount) + 5));
            
            // 툴팁
            const tooltip = d3.select(".tooltip");
            
            // 링크 그리기
            const link = svg.append("g")
                .attr("class", "links")
                .selectAll("line")
                .data(data.links)
                .enter().append("line")
                .attr("stroke-width", 2);
            
            // 노드 그룹 생성
            const node = svg.append("g")
                .attr("class", "nodes")
                .selectAll("g")
                .data(data.nodes)
                .enter().append("g")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            // 노드 원 그리기
            node.append("circle")
                .attr("r", d => radiusScale(d.citationCount))
                .attr("fill", d => color(d.id))
                .on("mouseover", function(event, d) {{
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooltip.html(`<strong>${{d.id}}</strong><br/>Citations: ${{d.citationCount}}`)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                }})
                .on("mouseout", function(d) {{
                    tooltip.transition()
                        .duration(500)
                        .style("opacity", 0);
                }});
            
            // 노드 텍스트 라벨
            node.append("text")
                .text(d => d.id)
                .attr("dy", 4)
                .style("font-size", "10px")
                .style("fill", "white")
                .style("font-weight", "bold");
            
            // 시뮬레이션 틱
            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node
                    .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            }});
            
            // 드래그 함수들
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
            
            // 윈도우 리사이즈 처리
            window.addEventListener('resize', function() {{
                const newWidth = window.innerWidth * 0.4;
                const newHeight = window.innerHeight * 0.8;
                svg.attr("width", newWidth).attr("height", newHeight);
                simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
                simulation.alpha(0.3).restart();
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(html_template, height=800, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)