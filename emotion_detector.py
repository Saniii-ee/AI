from ai.preprocessing import clean_text


def detect_emotion(text: str) -> str:
  """Detects basic emotional states from student messages to personalize responses."""
  cleaned = clean_text(text)

  stressed_keywords = ["stress", "anxious", "overwhelmed", "pressure", "worried"]
  tired_keywords = ["tired", "exhausted", "sleepy", "drained", "burnout"]
  calm_keywords = ["calm", "good", "relaxed", "happy", "okay"]

  if any(word in cleaned for word in stressed_keywords):
    return "stressed"
  elif any(word in cleaned for word in tired_keywords):
    return "tired"
  elif any(word in cleaned for word in calm_keywords):
    return "calm"

  return "neutral"