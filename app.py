import streamlit as st
import os
import json
import random
from streamlit_modal import Modal
import streamlit.components.v1 as components
from scraper import get_question_links, scrape_questions, load_json_from_github
from pdf import generate_pdf
from ui_utils import render_question_header, render_question_body, render_answers, render_discussion, render_highlight_toggle

if os.environ.get("HOSTNAME"):
    IS_DEPLOYED = os.environ["HOSTNAME"] == "streamlit"
else:
    IS_DEPLOYED = False

def get_exam_questions(exam_code, progress, rapid_scraping=False):
    if IS_DEPLOYED:
        questions, err = load_json_from_github(exam_code)
        if questions:
            progress.progress(100, text=f"Loaded from GitHub")
            return questions, ""
        else:
            return [], err
    else:
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
        questions_obj = scrape_questions(links, questions_path, progress, rapid_scraping)
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

st.session_state["rapid_scraping"] = st.session_state.get("rapid_scraping", False)
st.session_state["show_discussion"] = st.session_state.get("show_discussion", True)
st.session_state["default_highlight"] = st.session_state.get("default_highlight", False)

st.title("ExamTopics Question Viewer")

top_col1, top_options_btn_col, top_col2 = st.columns((15,1,4))
code_col, options_btn_col = st.columns((15, 1))

if "questions" not in st.session_state:
    with code_col:
        exam_code = st.text_input("Enter Exam Code (e.g., CAD):", placeholder="Enter Exam Code (e.g., CAD):", label_visibility="collapsed")
    with options_btn_col:
        open_modal = st.button("⚙️", key="gear_button", help="Open Settings")
else:
    with top_col1:
        exam_code = st.text_input("Enter Exam Code (e.g., CAD):", placeholder="Enter Exam Code (e.g., CAD):", label_visibility="collapsed")
    with top_options_btn_col:
        open_modal = st.button("⚙️", key="gear_button", help="Open Settings")

modal = Modal(
    title="Settings",
    key="demo-modal",
    padding=22,
    max_width=480
)
if open_modal:
    modal.open()

if modal.is_open():
    with modal.container():
        st.markdown("### 🔧 Scraper Settings")

        rapid_scraping = st.toggle(
            "Enable Rapid Scraping",
            help="Faster scraping, but may trigger rate-limiting from the website."
        )
        
        st.session_state["rapid_scraping"] = rapid_scraping

        st.markdown("""
        <hr style='margin-top:10px;margin-bottom:10px'/>
        """, unsafe_allow_html=True)

        st.markdown("### 🎨 Display Preferences")

        default_highlight = st.toggle("Highlight correct answers by default", value=st.session_state.get("default_highlight", False), help="Highlight correct answers by default")
        show_discussion = st.toggle("Show discussion", value=st.session_state.get("show_discussion", True), help="Show discussion by default")
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.session_state["show_discussion"] = show_discussion
        st.session_state["default_highlight"] = default_highlight
        if default_highlight:
            st.session_state["highlight"] = True

if exam_code:
    if "loaded_exam_code" not in st.session_state or st.session_state.loaded_exam_code != exam_code:
        with st.spinner("Fetching questions..."):
            progress = st.progress(0, text="Starting questions extraction...")
            questions, err = get_exam_questions(exam_code, progress, rapid_scraping=st.session_state["rapid_scraping"])
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
        else:
            question_number = int(selected_question["question_number"])
            while question_number <= max(int(q["question_number"]) for q in questions):
                print(question_number)
                question_number += 1
                matching_questions = [q for q in questions if q.get("question_number") == str(question_number)]
                if matching_questions:
                    selected_question = matching_questions[0]
                    break
            st.session_state.highlight = False
    elif previous_button:
        matching_questions = [q for q in questions if q.get("question_number") == str(int(selected_question["question_number"]) - 1)]
        if matching_questions:
            selected_question = matching_questions[0]
            st.session_state.highlight = False
        else:
            question_number = int(selected_question["question_number"])
            while question_number > 0 and question_number - 1 >= 0:
                question_number -= 1
                matching_questions = [q for q in questions if q.get("question_number") == str(question_number)]
                if matching_questions:
                    selected_question = matching_questions[0]
                    break
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
    
    if selected_question:
        st.session_state.question = selected_question
        render_question_header(selected_question)

        render_question_body(selected_question, "https://www.examtopics.com")

        higlight_flag = st.session_state.get("highlight", False) or st.session_state.get("default_highlight", False)
        render_answers(selected_question, higlight_flag)
        if not st.session_state.get("default_highlight"):
            render_highlight_toggle(selected_question)

        if st.session_state.get("show_discussion"):
            st.markdown("---")
            st.markdown("### Discussion:")
            render_discussion(selected_question.get("comments", []))

