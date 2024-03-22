import requests
from configg import LOCAL_SERVER_URL, max_tokens_in_answer

PROMPT_PARTS = {
                        "математика": "Ты учитель по математике. ",
                        "физика": "Ты учитель по физике. ",
                        "начинающий": "Отвечай просто и доступно, НЕ используй сложных терминов",
                        "продвинутый": "Отвечай развернуто и сложно, используя сложные термины",
                     }


def gpt_generate(user_content, answer, subject, level):
    subject_for_user = subject
    level_for_user = level
    system_content = PROMPT_PARTS.get(subject_for_user) + PROMPT_PARTS.get(level_for_user)
    assistant_content = "Решим задачу по шагам: "
    resp = requests.post(
        LOCAL_SERVER_URL,
        headers={"Content-Type": "application/json"},

        json={
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content + answer},
            ],
            "temperature": 1,
            "max_tokens": max_tokens_in_answer
        }
    )
    return resp
