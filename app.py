import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Helpers ----------
CATEGORY_KEYWORDS = {
    "Rent": ["rent", "apartment", "lease"],
    "Groceries": ["grocery", "supermarket", "store"],
    "Transport": ["uber", "ola", "taxi", "bus", "train", "fuel"],
    "Dining": ["restaurant", "cafe", "pizza", "burger"],
    "Entertainment": ["netflix", "spotify", "movie"],
    "Utilities": ["electricity", "water", "internet", "phone"],
    "Shopping": ["amazon", "mall", "shop"],
    "Health": ["pharmacy", "hospital", "doctor"],
}

def categorize(desc):
    desc = desc.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in desc for k in kws):
            return cat
    return "Other"

def analyze(df, income=None):
    df["category"] = df["description"].apply(categorize)
    total_exp = df["amount"].sum()
    by_cat = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    savings = None
    rate = None
    if income:
        savings = income - total_exp
        rate = savings / income if income > 0 else 0
    return total_exp, by_cat, savings, rate

def rule_based_summary(income, expenses, savings, rate, top_categories):
    text = f"""
--- Budget Summary ---
Income: {income}
Total Expenses: {expenses}
Savings: {savings if savings is not None else 'N/A'}
Savings Rate: {rate:.2%} if rate else 'N/A'

Top Categories:
{top_categories}

Tip: {"Try to save at least 20% of your income." if rate and rate<0.2 else "Good job! You're saving well."}
"""
    return text

def ai_summary(user_question):
    """Get AI-generated financial advice from OpenAI"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",   # use gpt-4 if available
        messages=[
            {"role": "system", "content": "You are a helpful financial advisor. Keep answers simple and clear."},
            {"role": "user", "content": user_question},
        ],
    )
    return response.choices[0].message.content

# ---------- Streamlit App ----------
st.title("💰 Personal Finance Chatbot")

income = st.number_input("Enter your monthly income:", min_value=0.0, step=100.0)

# Choice between CSV upload and manual entry
option = st.radio("How do you want to enter your expenses?", ("Upload CSV", "Enter manually"))

df = None
if option == "Upload CSV":
    uploaded_file = st.file_uploader("Upload a CSV with transactions (columns: description,amount)", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

elif option == "Enter manually":
    st.write("Enter your transactions below (format: description,amount). Type 'done' when finished.")
    manual_data = st.text_area("Enter transactions, one per line:")
    if manual_data.strip():
        rows = []
        for line in manual_data.split("\n"):
            line = line.strip()
            if line.lower() == "done" or line == "":
                continue
            parts = line.split(",")
            if len(parts) == 2:
                try:
                    rows.append({"description": parts[0], "amount": float(parts[1])})
                except ValueError:
                    pass
        if rows:
            df = pd.DataFrame(rows)

# Show budget summary if data available
if df is not None and not df.empty:
    total_exp, by_cat, savings, rate = analyze(df, income)
    st.subheader("📊 Budget Summary")
    st.text(rule_based_summary(income, total_exp, savings, rate, by_cat.head(5)))

# AI Chatbot section
st.subheader("🤖 Ask the Finance Chatbot")
user_question = st.text_input("Type your question about your finances:")
if st.button("Ask"):
    if user_question.strip() != "":
        with st.spinner("Thinking..."):
            try:
                answer = ai_summary(user_question)
                st.success(answer)
            except Exception as e:
                st.error(f"OpenAI error: {e}")

