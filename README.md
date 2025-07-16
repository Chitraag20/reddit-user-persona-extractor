# 🧠 Reddit User Persona Extractor

This Python tool extracts Reddit user activity (posts and comments), analyzes the content, and generates a personality-based **user persona** using the **Groq API (LLaMA3-70B)**.

---

## 📌 Features

- 🔍 Fetches latest posts and comments from a given Reddit user
- 🧱 Builds a custom prompt for persona generation
- 🤖 Uses **Groq LLaMA3-70B** for fast, smart persona summaries
- 💾 Saves results in a clean text file under `persona_output/`

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/reddit-user-persona-extractor.git
cd reddit-user-persona-extractor
```

### 2. Create a Virtual Environment (recommended)

```bash
python -m venv venv
```

Activate it:

- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- On **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Add Your API Keys

Create a `.env` file in the root directory with the following content:

```ini
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name
GROQ_API_KEY=your_groq_api_key
```

Get credentials from:
- [Reddit API](https://www.reddit.com/prefs/apps)
- [Groq API Key](https://console.groq.com/keys)

---

## 🛠️ How to Use

Run the script with a Reddit username or profile URL:

```bash
python reddit_persona_builder.py kojied
```

Or use a URL:

```bash
python reddit_persona_builder.py https://www.reddit.com/user/spez
```

---

## 📁 Output

Output is saved to the `persona_output/` folder:

```
persona_output/persona_<username>.txt
```

---

## 📦 Project Structure

```
reddit-user-persona-extractor/
│
├── reddit_persona_builder.py     # Main script
├── .env                          # API keys (you create this)
├── requirements.txt              # Required Python packages
├── persona_output/               # Output folder for saved results
└── README.md                     # This file
```

---


## 💡 Example

Here’s an example command:

```bash
python reddit_persona_builder.py u/spez
```

Creates: `persona_output/persona_spez.txt`

---
