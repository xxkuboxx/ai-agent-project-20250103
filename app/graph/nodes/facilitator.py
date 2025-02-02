from langchain_core.messages import SystemMessage
from graph.state import State
from pydantic import BaseModel, Field

from graph.llm import llm
from mbti.name import NAME_MBTI
from mbti.characteristics import MBTI_CHARACTERISTICS


class SelectMBTI(BaseModel):
    select_mbti: str = Field(description="INTJ, INTP, ENTJ, ENTP, INFJ, INFP, ENFJ, ENFP, ISTJ, ISFJ, ESTJ, ESFJ, ISTP, ISFP, ESTP, ESFPのいずれか", 
                             pattern=r"(INTJ|INTP|ENTJ|ENTP|INFJ|INFP|ENFJ|ENFP|ISTJ|ISFJ|ESTJ|ESFJ|ISTP|ISFP|ESTP|ESFP|建築家|論理学者|指揮官|討論者|提唱者|仲介者|主人公|運動家|管理者|擁護者|幹部|領事|巨匠|冒険家|起業家|エンターテイナー)")     

def generate_system_prompt(previous_mbti_type):
    """
    system_promptの作成
    """
    # mbtiの説明文章の作成
    mbti_description = ""
    for mbti_type, description in MBTI_CHARACTERISTICS.items():
        mbti_description += f"#### {mbti_type} ####\n{description}\n\n"
    # プロンプト作成
    system_prompt = f"""\
あなたは会話を適切な人にコメントを誘導するファシリテーターです。
今までの会話履歴の中から次にコメントさせるのに一番適切なMBTI特性の人を「MBTI特性一覧」の中から選んでください。
INTJ, INTP, ENTJ, ENTP, INFJ, INFP, ENFJ, ENFP, ISTJ, ISFJ, ESTJ, ESFJ, ISTP, ISFP, ESTP, ESFPのいずれかのみ出力し、それ以外の言葉は出力しないでください。
また、「{previous_mbti_type}」を出力すると同じ人が何度も発言することになるため、それが望ましい時以外は、なるべく出力しないでください。

### MBTI特性一覧 ###
{mbti_description}

"Tips: Make sure to answer in the correct format."
"""
    return system_prompt


def facilitator(state: State):
    llm_structured = llm.with_structured_output(SelectMBTI)
    chat_memory = state["chat_memory"]
    messages = state["messages"][-chat_memory:].copy()
    if "mbti_type" in state:
        previous_mbti_type = state["mbti_type"]
    else:
        previous_mbti_type = ""
    system_prompt = generate_system_prompt(previous_mbti_type)
    messages.insert(0, SystemMessage(content=system_prompt))
    response = llm_structured.with_retry(stop_after_attempt=5).invoke(messages)
    select_mbti = response.select_mbti
    # MBTI特性でなく名前が返されてきた場合はMBTI特性に修正する。
    if select_mbti in NAME_MBTI:
        select_mbti = NAME_MBTI[select_mbti]
    return {"mbti_type": select_mbti}
