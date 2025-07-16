import os
import sys
from dotenv import load_dotenv
from github import Github
import praw

# Load environment variables from .env file
load_dotenv()

# Set up Reddit API client
def get_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
        github_token = os.getenv("TOKEN")
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
        prompt += f"\n[Post on r/{post['subreddit']}] {post['title']} - {post['selftext']} ({post['url']})"

    prompt += "\n\nCOMMENTS:\n"
    for comment in comments:
        prompt += f"\n[Comment on r/{comment['subreddit']}] {comment['body']} ({comment['permalink']})"

    prompt += "\n\nNow write the USER PERSONA:"
    return prompt

# Create GitHub issue
def create_github_issue(username, persona):
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO")
    if not github_token or not github_repo:
        print("GitHub token or repo not set in environment variables.")
        return
    g = Github(github_token)
    repo = g.get_repo(github_repo)
    title = f"Persona for Reddit user u/{username}"
    body = persona
    issue = repo.create_issue(title=title, body=body)
    print(f"✅ GitHub issue created: {issue.html_url}")

# Ensure persona_output directory exists
def ensure_output_dir():
    os.makedirs("persona_output", exist_ok=True)

# Save persona to file
def save_output(username, persona):
    ensure_output_dir()
    filename = f"persona_output/persona_{username}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(persona)
    print(f"Persona saved to {filename}")

# Extract username from input
def extract_username(input_str):
    input_str = input_str.strip()
    if input_str.startswith("u/"):
        return input_str[2:]
    elif "reddit.com/user/" in input_str:
        return input_str.split("reddit.com/user/")[1].split('/')[0]
    else:
        return input_str

def main():
    if len(sys.argv) > 1:
        input_str = sys.argv[1]
    else:
        print("Usage: python reddit_persona_builder.py <reddit_username_or_url>")
        sys.exit(1)
    username = extract_username(input_str)
    print(f"\n🔍 Extracting data for u/{username}...\n")
    posts, comments = fetch_user_data(username)
    persona_prompt = build_persona_prompt(username, posts, comments)
    save_output(username, persona_prompt)
    create_github_issue(username, persona_prompt)

if __name__ == "__main__":
    main()
