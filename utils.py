from llm_response.langgraph_graph_state import GraphState
from neo4j import GraphDatabase
import os
from config import CONFIG
import timeit
import streamlit as st



graphdb_driver = GraphDatabase.driver(uri=CONFIG.neo4j_url, 
                                      auth=(
                                          CONFIG.neo4j_user,
                                          CONFIG.neo4j_password
                                          )
                                        )


def get_ratings_str(d):
    ratings_lst = []
    for platform in ['naver', 'kakao', 'google']:
        if (platform in d.metadata['store_Rating']) and (d.metadata['store_Rating'][platform] is not None):
            pf_rating = d.metadata['store_Rating'][platform]
        else:
            continue
        if platform in d.metadata['reviewCount'] and (d.metadata['reviewCount'][platform] is not None):
            pf_rc = d.metadata['reviewCount'][platform]
        else:
            continue
        ratings_lst.append(f"{platform} {pf_rating}({pf_rc}명)")
    rating_str = ', '.join(ratings_lst)
    return rating_str


class DotDict(dict):
    """딕셔너리 키를 속성처럼 접근할 수 있도록 하는 클래스"""
    def __getattr__(self, key):
        return self.get(key)
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __delattr__(self, key):
        del self[key]



# Add example query buttons
def add_recomm_query(state:GraphState=None):
    def add_query(example_query):
        st.session_state.messages.append({"role": "user", "content": example_query})
    
    print("state : ", state)

    if state is None :
        query1, query2 = get_init_recomm_query()
        col1, col2 = st.columns(2)
        with col1:
            if st.button(query1):
                print(f"사전질문1 들어옴!!")
                print(f"messages add 전! : {st.session_state.messages}")
                add_query(query1)
                st.session_state.clicked_recomm_query = query1
                print(f"messages add 후! : {st.session_state.messages}")
                st.session_state.query = query1
        with col2:
            if st.button(query2):
                print(f"사전질문2 들어옴!!")
                print(f"messages add 전! : {st.session_state.messages}")
                add_query(query2)
                st.session_state.clicked_recomm_query = query2
                print(f"messages add 후! : {st.session_state.messages}")
                st.session_state.query = query2
    else : 
        col1, col2 = st.columns(2)
        with col1:
            query1 = state['similar_query'][0]
            if st.button(query1):
                print(f"생성된질문1 들어옴!!")
                print(f"messages add 전! : {st.session_state.messages}")
                add_query(query1)
                st.session_state.clicked_recomm_query = query1
                print(f"messages add 후! : {st.session_state.messages}")
                st.session_state.query = query1
        with col2:
            query2 = state['similar_query'][1]
            if st.button(query2):
                print(f"생성된질문2 들어옴!!")
                print(f"messages add 전! : {st.session_state.messages}")
                add_query(query2)
                st.session_state.clicked_recomm_query = query2
                print(f"messages add 후! : {st.session_state.messages}")
                st.session_state.query = query2
        
        


def get_init_recomm_query() :
    example_query1 = "60대 부모님과 가기 좋은 애월읍 흑돼지 맛집 추천해줘"
    # example_query2 = "5살 아이와 함께 3인 가족이 가기 좋은 제주 신화월드와 가까운 한식당 추천해줘"
    example_query2 = "애월읍에서 60대가 가장 많이 가는 카페는?"
    return example_query1, example_query2