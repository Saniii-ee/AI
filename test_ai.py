from ai.intent_classifier import predict_intent


test_messages = [

    "I'm stressed about my maths exam",

    "I have an exam tomorrow and I'm really worried",

    "I'm feeling sad",

    "I feel lonely",

    "I can't sleep properly",

    "I can't motivate myself to study",

    "I feel overwhelmed",

    "what should I do",

    "help me",

    "it's not about exams",

    "I'm just having a bad day",

    "I don't know what's wrong",

    "I'm happy today"

]


print("\nMindMate AI Test")
print("=" * 60)


for message in test_messages:

    intent = predict_intent(
        message
    )

    print(
        f"\nMessage : {message}"
    )

    print(
        f"Intent  : {intent}"
    )


print("\n")