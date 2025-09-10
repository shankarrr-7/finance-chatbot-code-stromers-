# finance_chatbot.py
import pandas as pd
import os

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

# ---------- Main Program ----------
def main():
    print("💰 Personal Finance Chatbot (Python version)")
    income = float(input("Enter your monthly income: "))

    choice = input("Do you have a CSV file with transactions? (y/n): ").strip().lower()
    if choice == "y":
        path = input("Enter CSV file path (must have 'description,amount' columns): ").strip()
        df = pd.read_csv(path)
    else:
        print("Enter transactions (type 'done' to finish). Format: description,amount")
        rows = []
        while True:
            line = input("> ")
            if line.lower() == "done":
                break
            parts = line.split(",")
            if len(parts) == 2:
                rows.append({"description": parts[0], "amount": float(parts[1])})
        df = pd.DataFrame(rows)

    total_exp, by_cat, savings, rate = analyze(df, income)
    print(rule_based_summary(income, total_exp, savings, rate, by_cat.head(5)))

if __name__ == "__main__":
    main()

