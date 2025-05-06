# 📘 ExamTopics Question Viewer

A **Streamlit** web app that lets you view and export exam questions from [ExamTopics.com](https://www.examtopics.com) based on a specific exam code (e.g., `CAD`, `CSA`, `CIS-ITSM`). It scrapes discussion pages, shows most-voted answers, supports intuitive question navigation, and enables exporting the complete set to a PDF

## 🔧 Features

✅ Scrape questions and answers by exam code <br>
✅ View most-voted answers with optional highlighting <br>
✅ Read user discussion and selected answers <br>
✅ Navigate: next, previous, random, or search by number <br>
✅ Export questions and answers to a formatted PDF <br>
✅ Caching via local JSON to avoid re-scraping <br>
✅ Built-in error handling for rate limits and offline fallback

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/examtopics-viewer.git
cd examtopics-viewer
```

### 2. Create a Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

## 📤 Exporting to PDF
Once questions are loaded, click Export Questions to PDF. The PDF includes:

- Questions and all answers
- Information about most-voted answers
- Comments with selected answer labels
- Clean formatting for offline study

## 🛑 Rate Limiting Notice
Due to aggressive rate-limiting on ExamTopics, scraping questions is intentionally slow (5s between requests). If an error occurs, it's most likely due to your IP address being temporarily blocked or rate-limited. Once blocked, it may take hours or even days for your IP to be unblocked automatically. You will still have access to any previously scraped and saved questions. Additionally, you can sometimes continue to fetch more questions, but typically you'll be allowed to access only a few pages before hitting the limit again.

To bypass rate-limiting more quickly, you can try changing your IP address. Here are some easy ways:

🔌 Restart your router – Many ISPs assign a new IP on reconnect.

📱 Use your phone’s internet – Turn on mobile data sharing while scraping.

🔄 Switch networks – Try a different Wi-Fi or network (e.g., public hotspot).

🌐 Use a VPN – Switch to a different server/location.

## 📚 Pre-Scraped Exams
Some exams have already been scraped and saved locally in the data/ directory. These are the best way to use the app, since loading them avoids rate limits and delays entirely. Instead of waiting for slow scraping or risking being blocked, you can instantly load these pre-saved questions and explore them with full functionality.

To see the full list of available pre-scraped exams, check the data/ folder in the project directory — each exam has its own .json file named after its exam code (e.g., CAD.json)