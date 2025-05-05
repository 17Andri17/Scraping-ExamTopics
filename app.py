import streamlit as st
import requests
import os
import json
import random
from bs4 import BeautifulSoup
from scraper import get_question_links, scrape_questions
from pdf import generate_pdf

def fix_image_paths(html_text, prefix):
    soup = BeautifulSoup(html_text, "html.parser")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src.startswith("http"):
            img["src"] = prefix + src
    return str(soup)

def get_exam_questions(exam_code, progress):
    questions_path = f"data/{exam_code}.json"
    links_path = f"data/{exam_code}_links.json"

    if os.path.exists(questions_path):
        with open(questions_path, "r", encoding="utf-8") as f:
            questions_JSON = json.load(f)
            if questions_JSON.get("status") == "complete":
                progress.progress(100, text=f"Extracted questions from file")
                return questions_JSON.get("questions", [])
            
    links = get_question_links(exam_code, progress, links_path)    
    questions_obj = scrape_questions(links, questions_path, progress)
    questions = questions_obj.get("questions", [])
    if questions_obj.get("error","") != "":
        st.error("Error occurred while scraping questions.")
        return (questions, True)
    return (questions, False)
    
def clear_text():
    st.session_state.input = st.session_state.question_number_input_text
    st.session_state.question_number_input_text = ""

st.set_page_config(page_title="ExamTopics Viewer", layout="wide")

css_style = """
            <style>
            .stMainBlockContainer{
                padding-top: 16px;
            }
            </style>
            <div id="top"></div>
        """
st.markdown(css_style, unsafe_allow_html=True)
st.title("ExamTopics Question Viewer")


top_col1, top_col2 = st.columns((4,1))

if "questions" not in st.session_state:
    exam_code = st.text_input("Enter Exam Code (e.g., CAD):", placeholder="Enter Exam Code (e.g., CAD):", label_visibility="collapsed")
else:
    with top_col1:
        exam_code = st.text_input("Enter Exam Code (e.g., CAD):", placeholder="Enter Exam Code (e.g., CAD):", label_visibility="collapsed")

if exam_code:
    if "loaded_exam_code" not in st.session_state or st.session_state.loaded_exam_code != exam_code:
        with st.spinner("Fetching questions..."):
            progress = st.progress(0, text="Starting questions extraction...")
            questions, err = get_exam_questions(exam_code, progress)
            st.session_state.error = err
            st.session_state.questions = questions
            st.session_state.loaded_exam_code = exam_code
            st.session_state.just_loaded = True
            if len(questions) > 0:
                selected_question = questions[0]
                st.session_state.question = selected_question
            if len(questions) == 0:
                st.warning("No questions found.")
            st.rerun()
    else:
        questions = st.session_state.questions
    with top_col2:
        export_button = st.button("Export Questions to PDF", use_container_width=True)
    if export_button:
        progress_pdf = st.progress(0, text="Starting PDF generation...")
        questions = st.session_state["questions"]
        try:
            pdf_data = generate_pdf(questions, progress_pdf)
            st.success("PDF generation complete.")
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name=f"{exam_code}_questions.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"❌ Failed to generate PDF. Reason: {str(e)}. It may be due to a connection issue. Please try again.")

    if st.session_state.get("just_loaded"):
        if st.session_state.get("error"):
            st.error(f"Error occurred while scraping questions. Your connection may be slow or the website may have limited your rate. You can still see {len(st.session_state.questions)} questions. Try again later by refreshing the page.")
        else:
            st.success(f"Loaded {len(st.session_state.questions)} questions.")
        st.session_state.just_loaded = False

    if st.session_state.get("question"):
        selected_question = st.session_state.get("question")
    else:
        selected_question = None

    col1, col2, col3, col4 = st.columns((4,1,1,1))
    with col1:
        question_number_input = st.text_input("Search question", key="question_number_input_text", on_change=clear_text, placeholder="Search by number or text", label_visibility="collapsed")
    with col2:
        previous_button = st.button("Previous Question", use_container_width=True)
    with col3:
            random_button = st.button("Random Question", use_container_width=True)
    with col4:
        next_button = st.button("Next Question", use_container_width=True)
        

    if random_button and questions:
        selected_question = random.choice(questions)
        st.session_state.highlight = False
    elif next_button:
        matching_questions = [q for q in questions if q.get("question_number") == str(int(selected_question["question_number"]) + 1)]
        if matching_questions:
            selected_question = matching_questions[0]
            st.session_state.highlight = False
    elif previous_button:
        matching_questions = [q for q in questions if q.get("question_number") == str(int(selected_question["question_number"]) - 1)]
        if matching_questions:
            selected_question = matching_questions[0]
            st.session_state.highlight = False
    elif st.session_state.get("input", "") != "":
        matching_questions = [q for q in questions if q.get("question_number") == st.session_state.get("input")]
        if matching_questions:
            selected_question = matching_questions[0]
            question_number_input = "test"
            st.session_state.highlight = False
            st.session_state.input = ""
        else:
            st.warning("No question found with that number.")

    if not st.session_state.get("highlight"):
        st.session_state.highlight = False
    
    toggle_label = "Hide Most Voted Answers" if st.session_state.highlight else "Highlight Most Voted Answers"

    if selected_question:
        st.session_state.question = selected_question
        st.markdown(
                    f"""
                    <h3 style="display: flex; align-items: center; gap: 20px;">
                        Question {selected_question['question_number']}
                        <a href="{selected_question['link']}" target="_blank" style="
                            color: #1f77b4;
                            text-decoration: none;
                            font-size: 16px;
                        ">🔗 View on ExamTopics</a>
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(f"**{fix_image_paths(selected_question["question"], "https://www.examtopics.com")}**", unsafe_allow_html=True)

        for a in selected_question.get("answers", []):
            if st.session_state.highlight and a[0] in selected_question.get("most_voted", []):
                background_color = "lightgreen"
            else:
                background_color = "transparent"
            st.markdown(f'<div style="background-color:{background_color}; padding:10px; margin:2px; border-radius:5px;">{a}</div>', unsafe_allow_html=True)

        st.markdown("") 
        if len(selected_question.get("answers", [])) >= 2:
            if st.button(toggle_label):
                if selected_question.get("most_voted"):
                    st.session_state.highlight = not st.session_state.highlight
                    st.rerun()
                else:
                    st.warning("No most voted answer info available.")
            

        st.markdown("---")
        st.markdown("💬 **Discussion:**")

        comments = selected_question.get("comments", [])

        def render_discussion(comments):
            if not comments:
                st.info("No discussion available.")
                return

            st.markdown("""
            <style>
                .comment-box {
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 10px 15px;
                    margin-bottom: 16px;
                    background-color: #fdfdfd;
                }
                .comment-header {
                    font-weight: bold;
                    margin-bottom: 6px;
                    font-size: 1.05em;
                }
                .selected-label {
                    color: #2e7d32;
                    font-weight: bold;
                    margin-left: 10px;
                    font-size: 0.9em;
                }
                .reply {
                    margin-left: 12px;
                    margin-top: 6px;
                    padding: 6px 10px;
                    background-color: #f5f5f5;
                    border-left: 3px solid #ccc;
                    border-radius: 4px;
                    font-size: 0.9em;
                }
            </style>
            """, unsafe_allow_html=True)

            for idx, comment in enumerate(comments, 1):
                header = f"💬 Comment {idx}"
                if comment.get("selected_answer"):
                    header += f'<span class="selected-label">🟩 Selected Answer: {comment["selected_answer"]}</span>'

                replies_html = ""
                for reply in comment.get("replies", []):
                    replies_html += f'<div class="reply">{reply}</div>'

                comment_html = f"""
                <div class="comment-box">
                    <div class="comment-header">{header}</div>
                    <div>{comment['content']}</div>
                    {replies_html}</div>
                """
                st.markdown(comment_html, unsafe_allow_html=True)

        render_discussion(comments)


