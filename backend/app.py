import streamlit as st

from backend.router import route_question


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🤖 AI Business Assistant")

st.write(
    "Ask any business-related question and get an answer "
    "from your business data."
)


# =========================================================
# QUESTION INPUT
# =========================================================

question = st.text_input(
    "Ask a business question:",
    placeholder="Example: Which products have low stock?"
)


# =========================================================
# ASK BUTTON
# =========================================================

if st.button("Ask", type="primary"):

    if not question.strip():

        st.warning(
            "Please enter a business question."
        )

    else:

        with st.spinner("Thinking..."):

            try:

                result = route_question(
                    question.strip()
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

                st.stop()


        # =================================================
        # SQL RESULT
        # =================================================

        if result.get("type") == "sql":

            st.subheader("Answer")

            answer = result.get(
                "answer",
                "I couldn't generate an answer."
            )

            st.markdown(answer)

            # ---------------------------------------------
            # VIEW SQL
            # ---------------------------------------------

            sql = result.get(
                "sql",
                ""
            )

            if sql:

                with st.expander("View SQL"):

                    st.code(
                        sql,
                        language="sql"
                    )

            # ---------------------------------------------
            # VIEW RAW DATA
            # ---------------------------------------------

            with st.expander("View Raw Data"):

                data = result.get(
                    "data",
                    []
                )

                if data:

                    st.dataframe(
                        data,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No matching records found."
                    )


        # =================================================
        # DATABASE OVERVIEW RESULT
        # =================================================

        elif result.get("type") == "database_overview":

            st.subheader(
                "🗄️ Database Overview"
            )

            answer = result.get(
                "answer",
                ""
            )

            if answer:

                st.markdown(answer)

            else:

                st.info(
                    "No database information available."
                )


        # =================================================
        # RAG RESULT
        # =================================================

        elif result.get("type") == "rag":

            st.subheader("Answer")

            answer = result.get(
                "answer",
                ""
            )

            if answer:

                st.markdown(answer)

            else:

                rag_data = result.get(
                    "data",
                    {}
                )

                context = rag_data.get(
                    "context",
                    ""
                )

                if context:

                    st.write(context)

                else:

                    st.info(
                        "No relevant business information found."
                    )


        # =================================================
        # ERROR RESULT
        # =================================================

        elif result.get("type") == "error":

            st.error(
                result.get(
                    "message",
                    "Something went wrong."
                )
            )

            # ---------------------------------------------
            # SHOW SQL IF AVAILABLE
            # ---------------------------------------------

            failed_sql = result.get(
                "sql",
                ""
            )

            if failed_sql:

                with st.expander(
                    "View Failed SQL"
                ):

                    st.code(
                        failed_sql,
                        language="sql"
                    )


        # =================================================
        # UNKNOWN RESULT
        # =================================================

        else:

            st.warning(
                "I couldn't understand the question."
            )

            # ---------------------------------------------
            # DEBUG INFORMATION
            # ---------------------------------------------

            with st.expander(
                "View Router Response"
            ):

                st.write(result)