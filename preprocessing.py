import re


def clean_text(text: str) -> str:
  """Normalizes user input text by converting to lowercase and removing extra punctuation."""
  if not text:
    return ""
  text = text.lower().strip()
  text = re.sub(r"[^\w\s]", "", text)
  text = re.sub(r"\s+", " ", text)
  return text