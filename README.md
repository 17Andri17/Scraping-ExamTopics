# 📘 ExamTopics Question Viewer

🔗 Online App: https://examtopics-question-viewer.streamlit.app/
> **Note:** The **online version** of this app only supports viewing exams that were scraped earlier.  
> Due to limited free hosting storage, **live scraping is not available online**.  
> For full functionality, including scraping new exams and offline access, please **clone and run the app locally**.

## 💡 What is This?
A **Streamlit** web app that lets you view and export exam questions from [ExamTopics.com](https://www.examtopics.com) based on a specific exam code (e.g., `CAD`, `CSA`, `CIS-ITSM`). It scrapes discussion pages, shows most-voted answers, supports intuitive question navigation, and enables exporting everything to a well-formatted PDF for offline review.

## 🔧 Features

✅ Scrape questions and answers by exam code <br>
✅ View most-voted answers with optional highlighting <br>
✅ Read user discussion and selected answers <br>
✅ Navigate: next, previous, random, or search by number <br>
✅ Export questions and answers to a formatted PDF <br>
✅ Caching via local JSON to avoid re-scraping <br>
✅ Built-in error handling for rate limits and offline fallback

---

## 🚀 Getting Started (Offline / Full Version)

### 1. Clone the Repository

```bash
git clone https://github.com/{your-username}/ExamTopics-Question-Viewer.git
cd ExamTopics-Question-Viewer
```

### 2. Create a Virtual Environment & Install Dependencies

```bash
python -m venv {venv-name}
source {venv-name}/bin/activate  # On Windows: {venv-name}\Scripts\activate
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

ExamTopics enforces **aggressive rate-limiting**, so by default, the app waits **5 seconds between requests** to reduce the risk of being blocked.

If an error occurs while scraping, it’s likely because your IP address has been temporarily **rate-limited or blocked**. This block can last **several hours to days**, depending on usage.  
However, you’ll still be able to view any questions you’ve previously scraped and saved locally. Additionally, you can sometimes continue to fetch more questions, but typically you'll be allowed to access only a few pages before hitting the limit again.

### ⚡ Rapid Scraper Option (Use with Caution)

In the app’s **settings**, you can enable a **“Rapid Scraper”** mode that disables the 5-second delay.  
This allows for much faster scraping, but it **greatly increases the chance of hitting rate limits or getting blocked**.


To bypass rate-limiting more quickly, you can try changing your IP address. Here are some easy ways:

- 🔌 **Restart your router** – may assign a new IP
- 📱 **Use mobile data** or tethering
- 🔄 **Switch networks** (e.g., to a public Wi-Fi)
- 🌐 **Try a VPN** with different server locations

## 📚 Pre-Scraped Exams
Some exams have already been scraped and saved locally in the data/ directory. These are the best way to use the app, since loading them avoids rate limits and delays entirely. Instead of waiting for slow scraping or risking being blocked, you can instantly load these pre-saved questions and explore them with full functionality.

To see the full list of available pre-scraped exams, check the data/ folder in the project directory — each exam has its own .json file named after its exam code (e.g., CAD.json)
