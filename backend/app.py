import streamlit as st
import pandas as pd

from backend.router import route_question


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ==============================
       MAIN BACKGROUND
    ============================== */

    .stApp {
        background-color: #0b0f14;
        color: #ffffff;
    }

    .main .block-container {
        max-width: 1150px;
        padding-top: 35px;
        padding-bottom: 120px;
    }


    /* ==============================
       SIDEBAR
    ============================== */

    section[data-testid="stSidebar"] {
        background-color: #10151c;
        border-right: 1px solid #252c36;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 30px 20px;
    }


    /* ==============================
       SIDEBAR TITLE
    ============================== */

    .sidebar-title {
        font-size: 22px;
        font-weight: 700;
        color: white;
        margin-bottom: 5px;
    }

    .sidebar-subtitle {
        font-size: 13px;
        color: #8f9aaa;
        margin-bottom: 25px;
    }


    /* ==============================
       HEADER
    ============================== */

    .header-box {
        background-color: #151a22;
        border: 1px solid #2a323d;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 25px;
    }

    .header-title {
        font-size: 30px;
        font-weight: 700;
        color: white;
        margin-bottom: 5px;
    }

    .header-subtitle {
        font-size: 14px;
        color: #8f9aaa;
    }


    /* ==============================
       WELCOME
    ============================== */

    .welcome-box {
        background-color: #151a22;
        border: 1px solid #2a323d;
        border-radius: 16px;
        padding: 55px 30px;
        text-align: center;
        margin-bottom: 30px;
    }

    .welcome-icon {
        font-size: 45px;
        margin-bottom: 15px;
    }

    .welcome-title {
        font-size: 27px;
        font-weight: 650;
        color: white;
        margin-bottom: 10px;
    }

    .welcome-text {
        font-size: 14px;
        color: #8f9aaa;
    }


    /* ==============================
       USER MESSAGE
    ============================== */

    .user-box {
        background-color: #1b212a;
        border: 1px solid #303946;
        border-radius: 14px;
        padding: 18px 22px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .user-label {
        font-size: 12px;
        font-weight: 600;
        color: #8f9aaa;
        margin-bottom: 7px;
        text-transform: uppercase;
    }

    .user-question {
        color: white;
        font-size: 15px;
    }


    /* ==============================
       ANSWER
    ============================== */

    .answer-heading {
        font-size: 23px;
        font-weight: 650;
        color: white;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .answer-box {
        background-color: #151a22;
        border: 1px solid #303946;
        border-radius: 14px;
        padding: 22px;
        color: #f5f7fa;
        font-size: 15px;
        line-height: 1.7;
        margin-bottom: 20px;
    }


    /* ==============================
       SQL
    ============================== */

    .section-heading {
        font-size: 21px;
        font-weight: 650;
        color: white;
        margin-top: 25px;
        margin-bottom: 10px;
    }


    /* ==============================
       DETAILS
    ============================== */

    .details-box {
        background-color: #12171e;
        border: 1px solid #2a323d;
        border-radius: 12px;
        padding: 18px 20px;
        margin-top: 15px;
    }

    .details-label {
        color: #8f9aaa;
        font-size: 12px;
        margin-bottom: 4px;
    }

    .details-value {
        color: white;
        font-size: 14px;
    }


    /* ==============================
       BUTTONS
    ============================== */

    .stButton > button {
        border-radius: 10px;
        background-color: #1b212a;
        border: 1px solid #353e4b;
        color: white;
    }

    .stButton > button:hover {
        background-color: #242b35;
        border-color: #667085;
        color: white;
    }


    /* ==============================
       CHAT INPUT
    ============================== */

    div[data-testid="stChatInput"] {
        background-color: #151a22;
    }

    div[data-testid="stChatInput"] textarea {
        background-color: #151a22 !important;
        color: white !important;
        border: 1px solid #343d49 !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #7f8997 !important;
    }


    /* ==============================
       HIDE STREAMLIT MENU / FOOTER
    ============================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            🤖 AI Business Assistant
        </div>

        <div class="sidebar-subtitle">
            Intelligent ERP business assistant
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown(
        """
        <div style="
            color:#8f9aaa;
            font-size:13px;
            line-height:1.7;
        ">
            Ask natural-language questions about your
            ERP database and business information.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="header-box">

        <div class="header-title">
            🤖 AI Business Assistant
        </div>

        <div class="header-subtitle">
            Ask questions about your business data
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-box">

            <div class="welcome-icon">
                🤖
            </div>

            <div class="welcome-title">
                How can I help you today?
            </div>

            <div class="welcome-text">
                Ask anything about your business data,
                database or business documents.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    if message["role"] == "user":

        question_text = str(
            message.get("content", "")
        )

        st.markdown(
            f"""
            <div class="user-box">

                <div class="user-label">
                    You
                </div>

                <div class="user-question">
                    {question_text}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # ASSISTANT MESSAGE
    # --------------------------------------------------------

    else:

        answer = message.get(
            "answer",
            "No answer available."
        )

        # Answer heading
        st.markdown(
            """
            <div class="answer-heading">
                💬 Answer
            </div>
            """,
            unsafe_allow_html=True
        )

        # IMPORTANT:
        # Use st.write instead of putting answer
        # inside HTML.
        st.markdown(
            f"""
            <div class="answer-box">
                {answer}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # SQL QUERY
        # ----------------------------------------------------

        sql = message.get("sql")

        if sql:

            st.markdown(
                """
                <div class="section-heading">
                    🧠 SQL Query
                </div>
                """,
                unsafe_allow_html=True
            )

            st.code(
                str(sql),
                language="sql"
            )


        # ----------------------------------------------------
        # DATABASE RESULT
        # ----------------------------------------------------

        database_result = message.get(
            "result"
        )

        if database_result is not None:

            st.markdown(
                """
                <div class="section-heading">
                    📊 Database Result
                </div>
                """,
                unsafe_allow_html=True
            )

            try:

                if isinstance(
                    database_result,
                    list
                ):

                    if len(database_result) > 0:

                        st.dataframe(
                            pd.DataFrame(
                                database_result
                            ),
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No records found."
                        )

                else:

                    st.write(
                        database_result
                    )

            except Exception:

                st.write(
                    database_result
                )


        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        result_type = message.get(
            "type"
        )

        intent = message.get(
            "intent"
        )

        if result_type or intent:

            with st.expander(
                "🔎 Details",
                expanded=False
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.caption("Type")

                    st.write(
                        result_type
                        or "unknown"
                    )

                with col2:

                    st.caption("Intent")

                    st.write(
                        intent
                        or "Not available"
                    )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Message AI Business Assistant..."
)


# ============================================================
# RECEIVE NEW QUESTION
# ============================================================

if question:

    question = question.strip()

    if question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        st.rerun()


# ============================================================
# PROCESS QUESTION
# ============================================================

if (
    st.session_state.messages
    and
    st.session_state.messages[-1]["role"] == "user"
    and
    (
        len(st.session_state.messages) == 1
        or
        st.session_state.messages[-2]["role"]
        != "assistant"
    )
):

    current_question = (
        st.session_state.messages[-1]["content"]
    )

    with st.spinner(
        "Analyzing your question..."
    ):

        try:

            result = route_question(
                current_question
            )

            # ----------------------------------------------
            # Store complete result
            # ----------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",

                    "answer": result.get(
                        "answer",
                        "No answer available."
                    ),

                    "sql": result.get(
                        "sql"
                    ),

                    "result": result.get(
                        "result"
                    ),

                    "type": result.get(
                        "type"
                    ),

                    "intent": result.get(
                        "intent",
                        ""
                    )
                }
            )

        except Exception as e:

            st.session_state.messages.append(
                {
                    "role": "assistant",

                    "answer": (
                        "Sorry, something went wrong "
                        "while processing your question."
                    ),

                    "sql": None,

                    "result": None,

                    "type": "error",

                    "intent": str(e)
                }
            )

    st.rerun()
