import random
import re
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from graph.state import State

from graph.llm import llm
from mbti.characteristics import MBTI_CHARACTERISTICS
from mbti.name import MBTI_NAME


def remove_name_except_first(match):
    """
    コールバック関数: 最初のラベル以外は空文字列に置換える
    """
    global label_count
    label_count += 1
    if label_count == 1: # 最初のラベルは残す
        return match.group(0)
    else: # 2回目以降のラベルは削除
        return ''

def remove_duplicate_names_except_first(text, name):
    """
    最初のラベル以外を削除する関数
    """
    global label_count # グローバル変数を参照
    label_count = 0 # グローバル変数の初期化 (関数呼び出しごとにリセット)
    regex = rf'{name}: ' # 変数labelを使った正規表現
    result_str = re.sub(regex, remove_name_except_first, text)
    return result_str

def generate_system_prompt(mbti_type, name):
    characteristics = MBTI_CHARACTERISTICS[mbti_type]
    system_prompt = f"""\
あなたは以下の「特性」を持っている会話エージェントです。
その「特性」を持った人格になりきり「グループチャットの雰囲気」に合ったコメントをしてください。
コメントの際は必ず「コメントテンプレート」に従ってください。
自分の特性に合わせて、他の人に疑問を投げかけたり、質問に対して答えたり、持論を述べたりしてください。


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
会話の目的:
- 何かしらの問題解決を目的に、多様な意見を言い合い議論していく場です。

### コメントテンプレート ###
コメントの冒頭には必ず「{name}: 」をつけてください。
冒頭以外には「{name}: 」はつけないでください。
#### NG例 ####
{name}: うむ、ラーメンは確かに美味い。😋 {name}: 他の美味いものか、それは興味深い問いだな🤔
#### OK例 ####
{name}: うむ、ラーメンは確かに美味い。😋 他の美味いものか、それは興味深い問いだな🤔
"""
    return system_prompt

def regulate_messages(messages:list[BaseMessage], mbti_type:str) -> list[BaseMessage]:
    """
    過去の自分の発言を全てAIMessage型にし、連続で発言する場合はつかプロンプトをつける。
    """
    # 過去の自分の発言を全てAIMessage型にする。
    name = MBTI_NAME[mbti_type]
    new_messages = []
    for message in messages:
        if message.content.startswith(name):
            new_message = AIMessage(content=message.content)
            new_messages.append(new_message)
        else:
            new_messages.append(message)
    # 直前が自分の発言の場合は発言を促すように追加のプロンプトを挿入。
    if new_messages[-1].content.startswith(name):
        new_messages.append(HumanMessage(content=f"続けてコメントしてください。コメントの冒頭には必ず「{name}: 」をつけてください。"))
    return new_messages

def mbti_chatbot(state: State):
    chat_memory = state["chat_memory"]
    messages = state["messages"][-chat_memory:].copy()
    mbti_type = state["mbti_type"]
    name = MBTI_NAME[mbti_type]

    # messagesを選ばれたmbtiタイプのものに調整する。
    regulated_messages = regulate_messages(messages, mbti_type)

    # 選ばれたmbtiタイプの専用のシステムプロンプトを作成し、messagesの先頭に挿入
    system_prompt = generate_system_prompt(mbti_type, name)
    regulated_messages.insert(0, SystemMessage(content=system_prompt))

    # 返答結果を受け取る。
    response = llm.with_retry(stop_after_attempt=3).invoke(regulated_messages)
    content = response.content
    
    # 何も発言しなかった場合は絵文字を送付
    if not content:
        emoji_list = ["😀", "😃", "😄", "😆", "🙂", "🙃", "😇"]
        emoji = random.choice(emoji_list)
        content = f"{name}: {emoji}\n"
    
    # 名前を複数回入れてしまっている場合は除去する。
    content = remove_duplicate_names_except_first(content, name)

    # HumanMessage型にする。
    message = HumanMessage(content=content)

    return {"messages": [message]}
