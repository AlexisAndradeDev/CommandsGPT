import openai

def get_answer_from_model(user_prompt: str, model: str, 
        messages: list[dict[str, str]]) -> str:
    messages.append({"role": "user", "content": user_prompt})

    print("Getting answer from model...")
    response = openai.ChatCompletion.create(
        model=model, messages=messages,
    )

    answer = response["choices"][0]["message"]["content"]
    return answer
