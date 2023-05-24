import openai
import time

def get_answer_from_model(user_prompt: str, model: str, 
        messages: list[dict[str, str]]) -> str:
    messages.append({"role": "user", "content": user_prompt})

    # TODO: Pass number of attempts as parameters
    # TODO: Pass retry time as parameter
    max_attempts = 5
    for i in range(1, max_attempts+1):
        try:
            print("Getting answer from model...")
            response = openai.ChatCompletion.create(
                model=model, messages=messages,
            )

        except openai.error.RateLimitError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 5
            print(f"Rate limit exceeded. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)

        except openai.error.APIError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 5
            print(f"API error occurred. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)

        except OSError as e:
            retry_time = 5
            print(f"Connection error occurred: {e}. Retrying in {retry_time} seconds...")      
            time.sleep(retry_time)
        
        else:
            break

    answer = response["choices"][0]["message"]["content"]
    return answer
