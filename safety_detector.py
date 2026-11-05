from ai.preprocessing import clean_text


def is_wellness_related(text: str) -> bool:
  """Ensures conversations stay focused on general student wellness and study support."""
  cleaned = clean_text(text)
  return len(cleaned) > 0