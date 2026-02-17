CATEGORY_KEYWORDS = {
    "Food": ["food", "restaurant", "burger", "lunch", "dinner", "tea", "snacks"],
    "Travel": ["bus", "taxi", "uber", "fuel", "petrol", "flight"],
    "Shopping": ["mall", "shopping", "clothes", "shoes"],
    "Health": ["hospital", "medicine", "pharmacy"],
    "Bills": ["internet", "electricity", "water", "rent", "bill"],
}


def detect_categories(description):
    description = description.lower()
    matched = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for key in keywords:
            if key in description:
                matched.append(category)
                break

    if not matched:
        return ["Uncategorized"]

    return matched
