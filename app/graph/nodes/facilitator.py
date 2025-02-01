from langchain_core.messages import SystemMessage
from graph.state import State
from pydantic import BaseModel, Field

from graph.llm import llm
from mbti.characteristics import MBTI_CHARACTERISTICS
mbti_description = ""
for mbti_type, description in MBTI_CHARACTERISTICS.items():
    mbti_description += f"#### {mbti_type} ####\n{description}\n\n"


class SelectMBTI(BaseModel):
    select_mbti: str = Field(description="MBTI特性（INTJ, INTP, ENTJ, ENTP, INFJ, INFP, ENFJ, ENFP, ISTJ, ISFJ, ESTJ, ESFJ, ISTP, ISFP, ESTP, ESFP）のいずれか", 
                             pattern=r"(INTJ|INTP|ENTJ|ENTP|INFJ|INFP|ENFJ|ENFP|ISTJ|ISFJ|ESTJ|ESFJ|ISTP|ISFP|ESTP|ESFP)")


SYSTEN_PROMPT = f"""\
あなたは会話を適切な人に誘導するファシリテーターです。
今までの会話履歴の中から次に発言させるのに一番適切なMBTI特性の人を「MBTI特性一覧」の中から選んでください。
MBTI特性のみ出力してください。
発言の冒頭は「発言者：」となっています。
同じ発言者が連続で発言しないようにしてください。


### MBTI特性一覧 ###
{mbti_description}


"Tips: Make sure to answer in the correct format."
"""


def facilitator(state: State):
    llm_structured = llm.with_structured_output(SelectMBTI)
    messages = state["messages"].copy()
    messages.insert(0, SystemMessage(content=SYSTEN_PROMPT))
    response = llm_structured.with_retry(stop_after_attempt=3).invoke(messages)
    return {"mbti_type": response.select_mbti}

