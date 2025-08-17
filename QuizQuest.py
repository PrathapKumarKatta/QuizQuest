import requests
import html
import random
import time

BASE_URL = "https://opentdb.com/api.php"
TOKEN_URL = "https://opentdb.com/api_token.php"

def get_token():
    try:
        r = requests.get(f"{TOKEN_URL}?command=request")
        r.raise_for_status()
        data = r.json()
        return data.get("token")
    except Exception as e:
        print(f"⚠️ Could not get session token: {e}")
        return None

def fetch_questions(amount, category, difficulty, token):
    params = {
        "amount": amount,
        "type": "multiple",
    }
    if category != "any":
        params["category"] = category
    if difficulty != "any":
        params["difficulty"] = difficulty
    if token:
        params["token"] = token

    try:
        r = requests.get(BASE_URL, params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"⚠️ Network error: {e}")
        return None

def pick_category():
    categories = [
        ("any", "Any"),
        ("9", "General Knowledge"),
        ("10", "Entertainment: Books"),
        ("11", "Entertainment: Film"),
        ("12", "Entertainment: Music"),
        ("13", "Entertainment: Musicals & Theatres"),
        ("14", "Entertainment: Television"),
        ("15", "Entertainment: Video Games"),
        ("16", "Entertainment: Board Games"),
        ("17", "Science & Nature"),
        ("18", "Science: Computers"),
        ("19", "Science: Mathematics"),
        ("20", "Mythology"),
        ("21", "Sports"),
        ("22", "Geography"),
        ("23", "History"),
        ("24", "Politics"),
        ("25", "Art"),
        ("26", "Celebrities"),
        ("27", "Animals"),
        ("28", "Vehicles"),
        ("29", "Entertainment: Comics"),
        ("30", "Science: Gadgets"),
        ("31", "Entertainment: Japanese Anime & Manga"),
        ("32", "Entertainment: Cartoon & Animations")
    ]
    
    print("\nChoose a category:")
    for i, (_, name) in enumerate(categories, start=1):
        print(f"{i}. {name}")
    
    choice = input("Category number: ").strip()
    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(categories):
            return categories[num - 1][0]
    print("⚠️ Invalid choice, using Any category.")
    return "any"

def pick_difficulty():
    difficulties = ["any", "easy", "medium", "hard"]
    print("\nChoose difficulty:")
    for i, diff in enumerate(difficulties, start=1):
        print(f"{i}. {diff.capitalize()}")
    
    choice = input("Difficulty number: ").strip()
    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(difficulties):
            return difficulties[num - 1]
    print("⚠️ Invalid choice, using Any difficulty.")
    return "any"

def main():
    print("🎯 Welcome to the API-Powered Quiz!")
    print("Type 'quit' to exit anytime.\n")

    token = get_token()
    category = pick_category()
    difficulty = pick_difficulty()

    score = 0
    total = 0
    category_scores = {}  # Track per-category results
    question_buffer = []

    while True:
        if not question_buffer:
            data = fetch_questions(5, category, difficulty, token)
            if not data or not data.get('results'):
                if data and data.get('response_code') == 4:
                    print("\n⚠️ Question pool exhausted for these settings.")
                    print("💡 Try changing category/difficulty next time.\n")
                    break
                print("⚠️ No questions received. Retrying in 3 seconds...\n")
                time.sleep(3)
                continue
            question_buffer = data['results']

        qdata = question_buffer.pop(0)
        question = html.unescape(qdata['question'])
        correct = html.unescape(qdata['correct_answer'])
        cat_name = html.unescape(qdata['category'])  # Category from API
        options = [html.unescape(a) for a in qdata['incorrect_answers']] + [correct]
        random.shuffle(options)

        print(f"\n📚 Category: {cat_name}")
        print(f"Q: {question}")
        for i, opt in enumerate(options, start=1):
            print(f"  {i}. {opt}")

        ans = input("Your answer (number or 'quit'): ").strip().lower()
        if ans == "quit":
            print(f"\n🏁 Final Score: {score}/{total}")
            break
        if ans.isdigit():
            choice = int(ans)
            if 1 <= choice <= len(options):
                total += 1
                # Ensure category exists in score tracking
                if cat_name not in category_scores:
                    category_scores[cat_name] = {"score": 0, "total": 0}
                category_scores[cat_name]["total"] += 1

                if options[choice - 1] == correct:
                    print("✅ Correct!\n")
                    score += 1
                    category_scores[cat_name]["score"] += 1
                else:
                    print(f"❌ Wrong! Correct answer: {correct}\n")
                print(f"📊 Current Score: {score}/{total}")
            else:
                print("⚠️ Invalid option.")
        else:
            print("⚠️ Invalid input.")


    print("\n📌 Category-wise Score Breakdown:")
    for cat, sdata in category_scores.items():
        print(f"  {cat}: {sdata['score']}/{sdata['total']}")

if __name__ == "__main__":
    main()

