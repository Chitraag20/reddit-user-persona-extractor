import os
import praw
import openai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)
openai.api_key = OPENAI_API_KEY


def extract_username(input_str):
    if "reddit.com/user/" in input_str:
        return input_str.strip("/").split("/")[-1]
    elif input_str.startswith("u/"):
        return input_str[2:]
    else:
        return input_str.strip()


def fetch_user_data(username, limit=50):
    user = reddit.redditor(username)
    comments = []
    posts = []

    for comment in user.comments.new(limit=limit):
        comments.append({
            "body": comment.body,
            "subreddit": str(comment.subreddit),
            "permalink": f"https://www.reddit.com{comment.permalink}"
        })

    for post in user.submissions.new(limit=limit):
        posts.append({
            "title": post.title,
            "selftext": post.selftext,
            "subreddit": str(post.subreddit),
            "url": f"https://www.reddit.com{post.permalink}"
        })

    return comments, posts


def build_prompt(username, comments, posts):
    prompt = f"""
You are an intelligent assistant that creates detailed User Personas from Reddit data.

Below are Reddit posts and comments by u/{username}.
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

Write the persona in a structured, clear way like a UX persona.

POSTS:
"""

    for post in posts[:5]:
        prompt += f"\n[Post on r/{post['subreddit']}] {post['title']} - {post['selftext']} ({post['url']})"

    prompt += "\n\nCOMMENTS:\n"
    for comment in comments[:5]:
        prompt += f"\n[Comment on r/{comment['subreddit']}] {comment['body']} ({comment['permalink']})"

    prompt += "\n\nNow write the USER PERSONA:"
    return prompt

def generate_persona(prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in analyzing Reddit users."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


def save_output(username, content):
    out_dir = Path("persona_output")
    out_dir.mkdir(exist_ok=True)
    file_path = out_dir / f"persona_{username}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Persona saved at: {file_path}")


def main():
   import sys
   if len(sys.argv) > 1:
     input_str = sys.argv[1]
   else:
    print("Usage: python reddit_persona_builder.py <reddit_username_or_url>")
    sys.exit(1)
    username = extract_username(input_str)
    print(f"\n🔍 Extracting data for u/{username}...\n")
    comments, posts = fetch_user_data(username)
    prompt = build_prompt(username, comments, posts)
    persona = generate_persona(prompt)
    save_output(username, persona)


if __name__ == "__main__":
    main()
