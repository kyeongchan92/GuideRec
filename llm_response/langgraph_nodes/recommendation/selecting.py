import json
import re
from llm_response.langgraph_graph_state import GraphState
from prompt.final_selecting_for_recomm import FINAL_SELECTING_FOR_RECOMM_v2
from pprint import pprint


def final_selecting_for_recomm(llm, state: GraphState):
    print("Selecting for recomm".ljust(100, '='))

    prompt = FINAL_SELECTING_FOR_RECOMM_v2.format(
        query=state['query'],
        intent=state['rewritten_query'],
        candidates=state['candidate_str']
    )

    response = llm.invoke(prompt)

    raw = response.content.strip()

    # 코드 블록/주석 제거
    cleaned = (
        raw.replace("```", "")
            .replace("json", "")
            .strip()
    )

    # 작은따옴표 → 큰따옴표로 변환 (JSON 요구사항)
    cleaned_json_like = re.sub(r"'", '"', cleaned)

    try:
        state["selected_recommendations"] = eval(cleaned_json_like)
        pprint(f"Selected:\n{state['selected_recommendations']}")
    except Exception as e:
        print("⚠️ LLM 응답 eval 실패!")
        print("🔹 원본 응답:\n", raw)
        raise ValueError(f"LLM 응답 eval 실패했음: {e}")

    return state
