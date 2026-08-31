import streamlit as st
import pandas as pd

from backend.router import route_question


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🤖",
    layout="wide"
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

    st.title("🤖 AI Business Assistant")

    st.caption(
        "Intelligent assistant for your ERP business data."
    )

    st.divider()

    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("What I can do")

    st.write(
        """
        **Business Data**

        • Sales analysis  
        • Product information  
        • Customer data  
        • Supplier information  
        • Inventory analysis  
        • Order information  

        **Database**

        • Table information  
        • Database structure  
        • SQL queries  
        • Database results  

        **Business Knowledge**

        • Company policies  
        • Business documents  
        • Internal information
        """
    )

    st.divider()

    st.caption(
        "AI Business Assistant • ERP Intelligence"
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🤖 AI Business Assistant")

st.caption(
    "Ask questions about your business data"
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if len(st.session_state.messages) == 0:

    st.write("")
    st.write("")
    st.write("")

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.markdown(
            "<div style='text-align:center;'>",
            unsafe_allow_html=True
        )

        st.markdown(
            "# 🤖"
        )

        st.markdown(
            "## How can I help you today?"
        )

        st.write(
            "Ask anything about your business data, "
            "database or business documents."
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    # ========================================================
    # USER MESSAGE
    # ========================================================

    if message["role"] == "user":

        with st.chat_message("user"):

            st.write(
                message["content"]
            )

    # ========================================================
    # ASSISTANT MESSAGE
    # ========================================================

    else:

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            # =================================================
            # ANSWER
            # =================================================

            st.markdown("### 💬 Answer")

            answer = message.get(
                "answer",
                "No answer available."
            )

            st.write(answer)


            # =================================================
            # SQL QUERY
            # =================================================

            sql = message.get("sql")

            if sql:

                st.markdown("### 🧠 SQL Query")

                st.code(
                    sql,
                    language="sql"
                )


            # =================================================
            # DATABASE RESULT
            # =================================================

            data = message.get("data")

            if data is not None:

                st.markdown("### 📊 Database Result")

                try:

                    # -----------------------------------------
                    # LIST
                    # -----------------------------------------

                    if isinstance(data, list):

                        if len(data) > 0:

                            df = pd.DataFrame(data)

                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True
                            )

                        else:

                            st.info(
                                "No matching records found."
                            )


                    # -----------------------------------------
                    # DICTIONARY
                    # -----------------------------------------

                    elif isinstance(data, dict):

                        df = pd.DataFrame([data])

                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )


                    # -----------------------------------------
                    # OTHER DATA
                    # -----------------------------------------

                    else:

                        st.write(data)

                except Exception as e:

                    print(
                        f"[DISPLAY ERROR] {e}"
                    )

                    st.write(data)


            # =================================================
            # QUERY DETAILS
            # =================================================

            result_type = message.get(
                "type"
            )

            intent = message.get(
                "intent"
            )

            if result_type or intent:

                with st.expander(
                    "🔎 Query Details"
                ):

                    if result_type:

                        st.write(
                            "**Type:**",
                            result_type
                        )

                    if intent:

                        st.write(
                            "**Intent:**",
                            intent
                        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Message AI Business Assistant..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    question = question.strip()

    if question:

        # ====================================================
        # SAVE USER MESSAGE
        # ====================================================

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # ====================================================
        # PROCESS QUESTION
        # ====================================================

        with st.spinner(
            "Analyzing your question..."
        ):

            try:

                result = route_question(
                    question
                )


                # =================================================
                # SAVE ASSISTANT RESULT
                # =================================================

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

                        "data": result.get(
                            "data"
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

                print(
                    f"[FRONTEND ERROR] {e}"
                )


                # =================================================
                # ERROR MESSAGE
                # =================================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "answer": (
                            "Sorry, I couldn't process "
                            "your question right now."
                        ),

                        "sql": None,

                        "data": None,

                        "type": "error",

                        "intent": str(e)
                    }
                )


        # ====================================================
        # REFRESH
        # ====================================================

        st.rerun()
