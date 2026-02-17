import re
from collections import defaultdict

CATEGORY_RULES = {
    "Food & Drinks": {
        "keywords": ["food", "snack", "drink", "meal", "restaurant", "cafe", "lunch", "dinner", "breakfast"],
        "merchants": ["kfc", "mcdonald", "pizza", "bakers"],
        "weight": 3
    },
    "Transport": {
        "keywords": ["bus", "taxi", "fuel", "petrol", "diesel", "uber", "pathao", "ride", "travel"],
        "merchants": ["nepaltaxi", "pathao"],
        "weight": 2
    },
    "Shopping": {
        "keywords": ["clothes", "shirt", "shoe", "watch", "fashion", "shopping", "mall"],
        "merchants": ["daraz", "amazon"],
        "weight": 3
    },
    "Bills & Utilities": {
        "keywords": ["electricity", "water", "internet", "wifi", "recharge", "billing", "topup"],
        "merchants": ["nea", "ntc", "ncell"],
        "weight": 3
    },
    "Health": {
        "keywords": ["hospital", "clinic", "pharmacy", "medicine", "health"],
        "merchants": ["bir hospital"],
        "weight": 2
    },
    "Entertainment": {
        "keywords": ["movie", "netflix", "spotify", "entertain", "game", "cinema"],
        "weight": 1
    },
    "Others": {
        "keywords": [],
        "weight": 0
    }
}

def categorize_expense(title: str, description: str = "", merchant: str = ""):
    text = f"{title} {description} {merchant}".lower()

    scores = defaultdict(int)

    for category, data in CATEGORY_RULES.items():
        # Match merchants
        for merchant_name in data.get("merchants", []):
            if merchant_name.lower() in text:
                scores[category] += data["weight"] * 2  # stronger weight for merchant

        # Match keywords
        for keyword in data.get("keywords", []):
            if re.search(rf"\b{keyword}\b", text):
                scores[category] += data["weight"]

    # Pick the category with the highest score
    if scores:
        best_category = max(scores, key=scores.get)
        if scores[best_category] > 0:
            return best_category

    # If nothing matches, assign to closest likely category
    fallback_keywords = {
        "Food & Drinks": ["eat", "drink", "meal", "snack", "coffee", "tea", "pizza", "burger"],
        "Entertainment": ["movie", "game", "cinema", "show", "netflix", "song"],
        "Transport": ["taxi", "bus", "ride", "fuel", "petrol", "trip"],
        "Shopping": ["buy", "purchase", "shop", "clothes", "mall"]
    }

    for category, keys in fallback_keywords.items():
        for key in keys:
            if key in text:
                return category

    # Default if completely unknown
    return "Others"
