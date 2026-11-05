import pandas as pd
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / "data" / "MindMate_Database.xlsx"


# ============================================================
# LOAD TRAINING DATA
# ============================================================

def load_training_data():

    data = pd.read_excel(
        DATABASE,
        sheet_name="04_Training_Data"
    )

    data = data.dropna(
        subset=["Intent_ID", "Example_Text"]
    )

    data["Intent_ID"] = data["Intent_ID"].astype(str)
    data["Example_Text"] = data["Example_Text"].astype(str)

    return data


# ============================================================
# EXTRA TRAINING EXAMPLES
# ============================================================

EXTRA_EXAMPLES = {

    "INT001": [
        "I have an exam tomorrow and I'm really worried",
        "I am worried about my exam",
        "I am nervous about my upcoming exam",
        "My exam is making me really worried",
        "I am anxious about my test tomorrow",
        "I keep worrying about my exam"
    ],

    "INT006": [
        "I am having a stressful day",
        "Today is stressful",
        "I feel stressed today",
        "Everything is stressing me out",
        "I am feeling tense today",
        "I have a lot on my mind",
        "I need help with my stress"
    ],

    "INT007": [
        "I don't know how to handle everything",
        "I don't know what to do about everything",
        "Everything is too much",
        "I can't deal with everything",
        "There is too much happening",
        "I feel like everything is getting out of control",
        "I don't know where to begin",
        "I have too much going on"
    ],

    "INT008": [
        "I feel sad",
        "I am feeling sad",
        "I am having a bad day",
        "I don't feel good today",
        "I feel low",
        "Today has been difficult",
        "I am feeling down today",
        "I am not feeling okay today"
    ],

    "INT011": [
        "What should I do",
        "What can I do right now",
        "I need some advice",
        "Can you help me figure this out",
        "What should I do now",
        "Can you tell me what to do",
        "What can I do to feel better"
    ],

    "INT016": [
        "I need someone to talk to",
        "Can someone listen to me",
        "I just want to talk",
        "I need somebody to talk to",
        "Can I talk to you",
        "I want to talk about something",
        "I just need to talk",
        "I want someone to listen"
    ],

    "INT018": [
        "I just want to relax",
        "I need to calm down",
        "I want to unwind",
        "I need some peace",
        "I want to take a break",
        "I need some quiet time",
        "I want to feel calmer"
    ],

    "INT009": [
        "I am happy today",
        "I feel really happy",
        "Today is a good day",
        "I am feeling great",
        "I feel good today",
        "I am in a great mood"
    ],

    "INT020": [
        "I have to leave",
        "I need to go",
        "I will talk later",
        "I am leaving now",
        "Talk later",
        "I am done talking for now"
    ]
}


def add_extra_examples(data):

    extra_rows = []

    for intent_id, examples in EXTRA_EXAMPLES.items():

        for example in examples:

            extra_rows.append({
                "Intent_ID": intent_id,
                "Example_Text": example
            })

    extra_data = pd.DataFrame(extra_rows)

    return pd.concat(
        [data, extra_data],
        ignore_index=True
    )


# ============================================================
# TRAIN CLASSIFIER
# ============================================================

def train_classifier():

    data = load_training_data()

    data = add_extra_examples(data)

    X = data["Example_Text"]
    y = data["Intent_ID"]

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1
            )
        ),

        (
            "classifier",
            MultinomialNB(
                alpha=0.3
            )
        )
    ])

    model.fit(X, y)

    return model


model = train_classifier()


# ============================================================
# EXAM DETECTION
# ============================================================

def contains_exam_words(message):

    text = message.lower()

    exam_words = [
        "exam",
        "exams",
        "test",
        "tests",
        "paper",
        "papers",
        "results",
        "marks",
        "grade",
        "grades"
    ]

    return any(
        word in text
        for word in exam_words
    )


def is_exam_negation(message):

    text = message.lower().strip()

    negation_phrases = [
        "not about exam",
        "not about exams",
        "isn't about exam",
        "isn't about exams",
        "is not about exam",
        "is not about exams",
        "nothing to do with exam",
        "nothing to do with exams",
        "not related to exam",
        "not related to exams"
    ]

    return any(
        phrase in text
        for phrase in negation_phrases
    )


# ============================================================
# PREDICT INTENT
# ============================================================

def predict_intent(message):

    if not message:
        return "INT016"

    message = str(message).strip()

    if not message:
        return "INT016"

    cleaned = message.lower().strip()


    # ========================================================
    # VERY SHORT / VAGUE SUPPORT REQUESTS
    # ========================================================

    vague_messages = {
        "what should i do",
        "what do i do",
        "what can i do",
        "what now",
        "help me",
        "please help",
        "i need help",
        "i need advice",
        "can you help me",
        "can you help",
        "what should i do?",
        "what can i do?",
        "i don't know what to do",
        "i dont know what to do"
    }

    if cleaned in vague_messages:
        return "INT011"


    # ========================================================
    # EXPLICIT EXAM NEGATION
    # ========================================================
    # Example:
    # "It's not about exams"
    #
    # We don't want this to become INT001 simply because
    # the word "exams" appears.

    if is_exam_negation(message):

        return "INT006"


    # ========================================================
    # STRONG EXAM STRESS DETECTION
    # ========================================================
    # If the student clearly mentions an exam AND expresses
    # worry/stress/nervousness, classify as exam stress.

    if contains_exam_words(message):

        stress_words = [
            "stress",
            "stressed",
            "worried",
            "worry",
            "nervous",
            "anxious",
            "anxiety",
            "scared",
            "panic",
            "panicking",
            "pressure",
            "afraid",
            "fear"
        ]

        has_stress = any(
            word in cleaned
            for word in stress_words
        )

        if has_stress:
            return "INT001"


    # ========================================================
    # MODEL PREDICTION
    # ========================================================

    probabilities = model.predict_proba([message])[0]
    classes = model.classes_

    best_index = probabilities.argmax()

    best_intent = classes[best_index]
    best_probability = probabilities[best_index]


    # ========================================================
    # FALLBACK
    # ========================================================

    MIN_PROBABILITY = 0.10

    if best_probability < MIN_PROBABILITY:
        return "__fallback__"


    return best_intent