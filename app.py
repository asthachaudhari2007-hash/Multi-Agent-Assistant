import os
import streamlit as st

from rag.pdf_loader import load_pdf
from rag.chunking import chunk_documents
from rag.vector_store import create_vectorstore, retrieve_docs

from agents.note_agent import generate_notes
from agents.quiz_agent import generate_quiz
from agents.revision_agent import create_plan

from llm import get_llm

from langchain_core.prompts import ChatPromptTemplate

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="Multi-Agent Academic Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Multi-Agent Academic Assistant")

st.write(
    "Upload your PDF and let AI generate Answers, Notes, Quiz and Revision Plan."
)

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

st.sidebar.title("📌 AI Features")

# ===============================
# NEW : Model Selection
# ===============================

selected_model = st.sidebar.selectbox(
    "🤖 Select AI Model",
    [
        "Gemini",
        "Ollama"
    ]
)

llm = get_llm(selected_model)

st.sidebar.success(f"Using: {selected_model}")

st.sidebar.divider()

# ===============================
# Existing Feature Selection
# ===============================

task = st.sidebar.radio(
    "Choose Task",
    [
        "Ask Question",
        "Notes",
        "Quiz",
        "Revision Plan"
    ]
)

# ---------------------------------------------------
# Upload Folder
# ---------------------------------------------------

os.makedirs("uploads", exist_ok=True)

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

# ---------------------------------------------------
# QA Prompt
# ---------------------------------------------------

qa_prompt = ChatPromptTemplate.from_template(
"""
You are an expert teacher.

Answer ONLY from the given context.

If the answer is unavailable, reply:

"I could not find the answer in the uploaded PDF."

Context:
{context}

Question:
{question}

Answer:
"""
)

qa_chain = qa_prompt | llm

# ---------------------------------------------------
# Session State
# ---------------------------------------------------

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "context" not in st.session_state:
    st.session_state.context = ""

if "query" not in st.session_state:
    st.session_state.query = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_query" not in st.session_state:
    st.session_state.quiz_query = ""

# NEW

if "selected_model" not in st.session_state:
    st.session_state.selected_model = selected_model

# Recreate QA chain whenever model changes

if st.session_state.selected_model != selected_model:

    st.session_state.selected_model = selected_model

    llm = get_llm(selected_model)

    qa_chain = qa_prompt | llm

    st.success(f"Switched to {selected_model}")
   # ---------------------------------------------------
# Upload PDF
# ---------------------------------------------------

if uploaded_file:

    file_path = os.path.join(
        "uploads",
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("✅ PDF Uploaded Successfully")

    st.info(f"🤖 Current AI Model: {selected_model}")

    # ---------------------------------------
    # Build Vector Database
    # ---------------------------------------

    if st.session_state.vectorstore is None:

        with st.spinner("📄 Loading PDF..."):
            documents = load_pdf(file_path)

        st.success(f"Loaded {len(documents)} pages")

        with st.spinner("✂ Splitting into Chunks..."):
            chunks = chunk_documents(documents)

        st.success(f"{len(chunks)} Chunks Created")

        with st.spinner("🧠 Creating Vector Database..."):
            vectorstore = create_vectorstore(chunks)

        st.session_state.vectorstore = vectorstore

    vectorstore = st.session_state.vectorstore

    # ---------------------------------------
    # User Query
    # ---------------------------------------

    query = st.text_input(
        "Enter Topic / Question",
        value=st.session_state.query,
        placeholder="Example: Explain Communication Process"
    )

    col1, col2 = st.columns([3,1])

    with col1:

        generate = st.button(
            "🚀 Generate",
            use_container_width=True
        )

    with col2:

        clear = st.button(
            "🗑 Clear",
            use_container_width=True
        )

    # ---------------------------------------
    # Clear Context
    # ---------------------------------------

    if clear:

        st.session_state.context = ""
        st.session_state.query = ""
        st.session_state.quiz = None
        st.session_state.quiz_query = ""

        st.rerun()

    # ---------------------------------------
    # Generate Context
    # ---------------------------------------

    if generate:

        if query.strip() == "":

            st.warning("⚠ Please enter a topic or question.")

        else:

            with st.spinner("🔍 Retrieving relevant content..."):

                docs = retrieve_docs(
                    vectorstore,
                    query
                )

            context = "\n\n".join(
                [
                    doc.page_content
                    for doc in docs
                ]
            )

            st.session_state.context = context
            st.session_state.query = query

            # Reset quiz when topic changes

            st.session_state.quiz = None
            st.session_state.quiz_query = ""

            st.success("✅ Context Retrieved Successfully")

# ---------------------------------------------------
# Stop Until Context Exists
# ---------------------------------------------------

if st.session_state.context == "":

    st.info("📄 Upload a PDF and click Generate to continue.")

    st.stop()

context = st.session_state.context
query = st.session_state.query
# ===================================================
# ASK QUESTION
# ===================================================

if task == "Ask Question":

    with st.spinner(f"🤖 Generating Answer using {selected_model}..."):

        response = qa_chain.invoke(
            {
                "context": context,
                "question": query
            }
        )

    st.divider()

    st.subheader("🤖 AI Answer")

    st.write(response.content)

# ===================================================
# NOTES
# ===================================================

elif task == "Notes":

    with st.spinner(f"📝 Generating Notes using {selected_model}..."):

        notes = generate_notes(
            context,
            selected_model
        )

    st.divider()

    st.subheader("📘 AI Study Notes")

    st.markdown(notes)

# ===================================================
# QUIZ
# ===================================================

elif task == "Quiz":

    current_topic = uploaded_file.name + "_" + query + "_" + selected_model

    if (
        st.session_state.quiz is None
        or st.session_state.quiz_query != current_topic
    ):

        with st.spinner(f"🧠 Generating Quiz using {selected_model}..."):

            quiz = generate_quiz(
                context,
                selected_model
            )

        if len(quiz) == 0:

            st.error("Quiz generation failed.")
            st.stop()

        st.session_state.quiz = quiz
        st.session_state.quiz_query = current_topic

    quiz = st.session_state.quiz

    st.divider()

    st.subheader("📝 AI Generated Quiz")

    for i, q in enumerate(quiz):

        st.write(f"### Q{i+1}. {q['question']}")

        st.radio(
            "Choose one:",
            q["options"],
            key=f"answer_{i}"
        )

    st.divider()

    if st.button("✅ Submit Quiz"):

        score = 0

        for i, q in enumerate(quiz):

            user_answer = st.session_state.get(
                f"answer_{i}",
                ""
            )

            if user_answer == q["correct_answer"]:
                score += 1

        percentage = (score / len(quiz)) * 100

        if percentage >= 90:
            grade = "A+"
            remark = "🌟 Outstanding!"
            st.balloons()

        elif percentage >= 80:
            grade = "A"
            remark = "🎉 Excellent!"

        elif percentage >= 70:
            grade = "B"
            remark = "👏 Very Good!"

        elif percentage >= 60:
            grade = "C"
            remark = "🙂 Good Job!"

        else:
            grade = "D"
            remark = "📚 Keep Practicing!"

        st.success(remark)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Score",
                f"{score}/{len(quiz)}"
            )

        with col2:
            st.metric(
                "Percentage",
                f"{percentage:.1f}%"
            )

        with col3:
            st.metric(
                "Grade",
                grade
            )

        st.divider()

        st.subheader("📖 Quiz Review")

        for i, q in enumerate(quiz):

            user_answer = st.session_state.get(
                f"answer_{i}",
                ""
            )

            st.write(f"### Q{i+1}. {q['question']}")

            st.write(
                f"**Your Answer:** {user_answer}"
            )

            if user_answer == q["correct_answer"]:

                st.success(
                    f"✅ Correct Answer: {q['correct_answer']}"
                )

            else:

                st.error(
                    f"❌ Correct Answer: {q['correct_answer']}"
                )

            st.info(
                f"💡 Explanation: {q['explanation']}"
            )

            st.divider()

    if st.button("🔄 Generate New Quiz"):

        st.session_state.quiz = None
        st.session_state.quiz_query = ""

        for i in range(len(quiz)):

            key = f"answer_{i}"

            if key in st.session_state:
                del st.session_state[key]

        st.rerun()

# ===================================================
# REVISION PLAN
# ===================================================

elif task == "Revision Plan":

    with st.spinner(f"📅 Creating Revision Plan using {selected_model}..."):

        plan = create_plan(
            context,
            selected_model
        )

    st.divider()

    st.subheader("📅 7-Day AI Revision Plan")

    st.markdown(plan)

# ===================================================
# Footer
# ===================================================

st.divider()

st.markdown(
    f"""
---
### 📚 Multi-Agent Academic Assistant

**Current Model:** `{selected_model}`

Built using:

- 🤖 Google Gemini 2.5 Flash
- 🦙 Ollama Llama 3.2
- 🦜 LangChain
- 📄 Retrieval-Augmented Generation (RAG)
- 🔎 FAISS Vector Database
- 🤗 HuggingFace Embeddings
- 🎈 Streamlit

### Features

- ✅ Ask Questions from PDF
- ✅ AI Generated Notes
- ✅ AI Quiz Generator
- ✅ AI Revision Planner
- ✅ Model Switching (Gemini / Ollama)
"""
) 