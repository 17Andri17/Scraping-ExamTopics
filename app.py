import streamlit as st
import requests
import os
import json
import random
from bs4 import BeautifulSoup
from scraper import get_question_links, scrape_questions
from pdf import generate_pdf
from ui_utils import render_question_header, render_question_body, render_answers, render_discussion, render_highlight_toggle


def get_exam_questions(exam_code, progress):
    questions_path = f"data/{exam_code}.json"
    links_path = f"data/{exam_code}_links.json"

    if os.path.exists(questions_path):
        with open(questions_path, "r", encoding="utf-8") as f:
            questions_JSON = json.load(f)
            if questions_JSON.get("status") == "complete":
                progress.progress(100, text=f"Extracted questions from file")
                return (questions_JSON.get("questions", []), "")
    try:        
        links = get_question_links(exam_code, progress, links_path)
    except Exception as e:
        return [], e
    
    if len(links) == 0:
        return [], "No questions found. Please check the exam code and try again."
    
    questions_obj = scrape_questions(links, questions_path, progress)
    questions = questions_obj.get("questions", [])
    if questions_obj.get("error","") != "":
        return (questions, f"Error occurred while scraping questions. Your connection may be slow or the website may have limited your rate. You can still see {len(questions)} questions. Try again later by refreshing the page.")
    return (questions, "")
    
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
        if st.session_state.get("error", "") != "":
            st.error(st.session_state.get("error", ""))
        else:
            st.success(f"Loaded {len(st.session_state.questions)} questions.")
        st.session_state.just_loaded = False

    if st.session_state.get("question"):
        selected_question = st.session_state.get("question")
    else:
        selected_question = None

    col1, col2, col3, col4 = st.columns((4,1,1,1))
    with col1:
        question_number_input = st.text_input("Search question", key="question_number_input_text", on_change=clear_text, placeholder="Search question number", label_visibility="collapsed")
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
        elif int(selected_question["question_number"]) < len(questions):
            selected_question = questions[int(selected_question["question_number"])]
            st.session_state.highlight = False
    elif previous_button:
        matching_questions = [q for q in questions if q.get("question_number") == str(int(selected_question["question_number"]) - 1)]
        if matching_questions:
            selected_question = matching_questions[0]
            st.session_state.highlight = False
        elif int(selected_question["question_number"] - 2) > 0:
            selected_question = questions[int(selected_question["question_number"])]
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
        render_question_header(selected_question)

        render_question_body(selected_question, "https://www.examtopics.com")

        render_answers(selected_question, st.session_state.highlight)

        render_highlight_toggle(selected_question)

        st.markdown("---")
        st.markdown("💬 **Discussion:**")
        render_discussion(selected_question.get("comments", []))


