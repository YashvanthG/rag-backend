conversation_store = {}

MAX_HISTORY = 7


def get_history(session_id: str):

    if session_id not in conversation_store:
        return []

    return conversation_store[session_id][-MAX_HISTORY:]


def save_history(session_id: str, question: str, answer: str):

    if session_id not in conversation_store:
        conversation_store[session_id] = []

    conversation_store[session_id].append(
        {"role": "user", "content": question}
    )

    conversation_store[session_id].append(
        {"role": "assistant", "content": answer}
    )

    conversation_store[session_id] = conversation_store[session_id][-MAX_HISTORY:]