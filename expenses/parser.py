from .categorizer import categorize_expense
import re
def parse_and_categorize(description):
    items = []
    for part in description.split(','):
        part = part.strip()
        if not part:
            continue
        match = re.search(r'(\d+\.?\d*)', part)
        if match:
            amount = float(match.group(1))
            title = part.replace(match.group(1), '').strip()
            category_name = categorize_expense(title)
            items.append({
                'title': title,
                'amount': amount,
                'description': title,  # optional: can be improved
                'categories': [category_name]
            })
    return items
