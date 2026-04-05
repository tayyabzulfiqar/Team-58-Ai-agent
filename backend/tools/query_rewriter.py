from backend.services.qwen_service import qwen_generate


def rewrite_query(query):
    prompt = f"""
Convert this topic into 3 human-style questions people ask online.

Topic: {query}

Output:

- question 1

- question 2

- question 3
    """

    response = qwen_generate(prompt)

    return response
