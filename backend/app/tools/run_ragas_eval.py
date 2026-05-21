import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy

# --------------------------------------
# 1. LOAD YOUR GOOGLE SHEET (CSV EXPORT)
# --------------------------------------

# 👉 Replace this with your sheet CSV link
# Go to Sheet → File → Share → Publish → CSV

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCPW-sfck6LxipyTG6UcHiAcRDD_I2rgMrD6QrP-HItjEJaH-AHD6RisZXbKmpR3YKddUka21rrSmA/pub?output=csv"

df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

# --------------------------------------
# 2. CLEAN DATA
# --------------------------------------

# Convert contexts string → list
import json

def parse_context(x):
    try:
        return json.loads(x)
    except:
        return []

df["contexts"] = df["contexts"].apply(parse_context)

# --------------------------------------
# 3. CREATE DATASET
# --------------------------------------

dataset = Dataset.from_dict({
    "question": df["question"].tolist(),
    "answer": df["answer"].tolist(),
    "contexts": df["contexts"].tolist()
})

# --------------------------------------
# 4. RUN RAGAS
# --------------------------------------

result = evaluate(
    dataset,
    metrics=[
        Faithfulness(),
        AnswerRelevancy()
        
    ]
)

# --------------------------------------
# 5. PRINT RESULTS
# --------------------------------------

print("\n📊 RAGAS RESULTS:\n")

print("Faithfulness:", sum(result["faithfulness"]) / len(result["faithfulness"]))
print("Answer Relevancy:", sum(result["answer_relevancy"]) / len(result["answer_relevancy"]))

# Optional: row-wise output
df["faithfulness"] = result["faithfulness"]
df["answer_relevancy"] = result["answer_relevancy"]

print("\n📋 Detailed Row Scores:\n")
print(df[["question", "faithfulness", "answer_relevancy"]])