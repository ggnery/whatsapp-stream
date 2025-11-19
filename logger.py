import os
from datetime import datetime


def log_conversation(question: str, answer: str, error: bool = False):
    """
    Args:
        question: The user's question
        answer: The system's answer
        error: If True, marks the log entry as an error (default: False)
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Create log file path
    log_file = os.path.join(logs_dir, "conversation_log.txt")

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format log entry
    error_marker = "[ERRO] " if error else ""
    log_entry = f"[{timestamp}] {error_marker}PERGUNTA: {question} | RESPOSTA: {answer}\n"

    # Append to log file
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"✓ Conversa logada em: {log_file}")
    except Exception as e:
        print(f"✗ Erro ao logar conversa: {e}")


def get_log_file_path():
    """
    Returns:
        str: Full path to the log file
    """
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    return os.path.join(logs_dir, "conversation_log.txt")
