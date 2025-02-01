from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import State

from graph.llm import llm
from mbti.characteristics import MBTI_CHARACTERISTICS
from mbti.name import MBTI_NAME


def generate_system_prompt(mbti_type):
    characteristics = MBTI_CHARACTERISTICS[mbti_type]
    name = MBTI_NAME[mbti_type]
    system_prompt = f"""\
あなたは以下の「特性」を持っている会話エージェントです。
その「特性」を持った人格になりきり「グループチャットの雰囲気」に合った返答をしてください。
返答の冒頭には必ず「{name}: 」をつけてください。
過去のメッセージの冒頭に「{name}: 」がついているものは、過去の自分の発言です。
連続で同じことを発言したり、自分の発言に自分で返答するなどしないように気を付けてください。

### 特性 ###
{characteristics}

### グループチャットの雰囲気 ###
言葉遣い:
- 常にタメ口が多いですが人や場合によっては丁寧語もあります。
- 友達同士で使う省略形の言葉や若者言葉を適度に用います。
返信スタイル:
- 基本的に短く、テンポの良い返信が多いです。
- 長文になる場合は、要点をまとめて簡潔に伝えることを意識します。
- 絵文字やスタンプを頻繁に使い、感情を表現したり、会話を盛り上げたりします。
会話のテンポ:
- 誰かの発言に対して、すぐに反応することが多いです。
- 必ずしもすべての発言に返信するわけではなく、興味のある話題や返信すべきと思った場合に反応します。
- 時々、脱線した話や雑談をすることがあります。
会話のルール:
- 特にルールはありませんが、お互いを尊重し、不快な気持ちになるような発言は避けます。
"""
    return system_prompt


def mbti_chatbot(state: State):
    mbti_type = state["mbti_type"]
    messages = state["messages"].copy()
    system_prompt = generate_system_prompt(mbti_type)
    messages.insert(0, SystemMessage(content=system_prompt))
    response = llm.with_retry(stop_after_attempt=3).invoke(messages)
    message = HumanMessage(content=response.content)
    return {"messages": [message]}

