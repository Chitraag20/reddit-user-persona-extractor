import os
import sys
from dotenv import load_dotenv
import praw
import openai
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Set up Reddit API client
def get_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )

# Fetch posts and comments for a given Reddit user
def fetch_user_data(username, post_limit=20, comment_limit=20):
    reddit = get_reddit_client()
    user = reddit.redditor(username)

    posts = []
    for submission in user.submissions.new(limit=post_limit):
        posts.append({
            'title': submission.title,
            'selftext': submission.selftext,
            'subreddit': str(submission.subreddit),
            'url': f"https://reddit.com{submission.permalink}"
        })

    comments = []
    for comment in user.comments.new(limit=comment_limit):
        comments.append({
            'body': comment.body,
            'subreddit': str(comment.subreddit),
            'permalink': f"https://reddit.com{comment.permalink}"
        })

    return posts, comments

# Build persona prompt
def build_persona_prompt(username, posts, comments):
    prompt = f"""Below are Reddit posts and comments by u/{username}.
Analyze their content and write a detailed User Persona including:

- Age (guess if not stated)
- Occupation (guess based on content)
- Location (if available or inferable)
- Personality (introvert/extrovert, traits)
- Behavior & Habits (posting frequency, topics)
- Frustrations (recurring complaints)
- Motivations
- Goals & Needs
- Top subreddits
- Citations for each trait (link to post or comment)

POSTS:
"""
    for post in posts:
        text = f"{post['title']} - {post['selftext']}".strip()
        prompt += f"- ({post['subreddit']}): {text}\n"

    prompt += "\nCOMMENTS:\n"
    for comment in comments:
        prompt += f"- ({comment['subreddit']}): {comment['body']}\n"

    prompt += "\n\nBased on the above, write a short personality profile."
    return prompt

# Save persona to file
def save_output(username, persona):
    os.makedirs("persona_output", exist_ok=True)
    filename = f"persona_output/persona_{username}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(persona)
    print(f"✅ Persona saved to {filename}")

# Extract username from input
def extract_username(input_str):
    input_str = input_str.strip()
    if input_str.startswith("u/"):
        return input_str[2:]
    elif "reddit.com/user/" in input_str:
        return input_str.split("reddit.com/user/")[1].split('/')[0]
    else:
        return input_str

# Generate persona using Groq API

def generate_persona_groq(prompt):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("❌ GROQ_API_KEY not found in environment variables!")

    client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are an expert personality analyst. Generate a detailed Reddit user persona."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2048,
    )

    return response.choices[0].message.content

# Main execution
def main():
    if len(sys.argv) > 1:
        input_str = sys.argv[1]
    else:
        print("Usage: python reddit_persona_builder.py <reddit_username_or_url>")
        sys.exit(1)

    username = extract_username(input_str)
    print(f"\n🔍 Fetching data for u/{username}...\n")
    posts, comments = fetch_user_data(username)
    persona_prompt = build_persona_prompt(username, posts, comments)

    print("\n🤖 Generating user persona...\n")
    persona_text = generate_persona_groq(persona_prompt)

    save_output(username, persona_text)

if __name__ == "__main__":
    main()
