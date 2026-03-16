import streamlit as st
import pandas as pd
from utils import (
    evaluate_prompt_quality,
    evaluate_llm_responses,
    init_history_state,
    add_history_row,
    reset_history,
)

st.set_page_config(
    page_title="Prompt Evaluation & LLM Comparison Tool",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Prompt Evaluation & LLM Comparison Tool")
st.caption("A portfolio project for AI Trainer, LLM Evaluation, and Prompt Review roles.")

menu = st.sidebar.radio(
    "Choose Module",
    [
        "Home",
        "Prompt Quality Evaluation",
        "LLM Response Comparison",
        "Evaluation History",
        "Batch Prompt Review",
    ],
)

if menu == "Home":
    st.subheader("Project Overview")
    st.write(
        """
This application simulates real-world AI Trainer and LLM evaluation workflows.

### Core Capabilities
- Evaluate prompt quality using structured criteria
- Compare two LLM responses side-by-side
- Score outputs on relevance, clarity, safety, and factuality
- Maintain evaluation history
- Batch review prompts from CSV files

### Skills Demonstrated
- Prompt analysis
- LLM response ranking
- Human feedback simulation
- AI quality review
- Streamlit app development
- Structured evaluation workflow design
        """
    )

elif menu == "Prompt Quality Evaluation":
    st.subheader("✍️ Prompt Quality Evaluation")

    prompt_text = st.text_area(
        "Enter a prompt to evaluate",
        height=180,
        placeholder="Example: Explain machine learning in simple terms for a beginner.",
    )

    if st.button("Evaluate Prompt"):
        if prompt_text.strip():
            result = evaluate_prompt_quality(prompt_text)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Scores")
                st.write(f"**Clarity:** {result['clarity']}/5")
                st.write(f"**Specificity:** {result['specificity']}/5")
                st.write(f"**Completeness:** {result['completeness']}/5")
                st.write(f"**Ambiguity Control:** {result['ambiguity_control']}/5")
                st.write(f"**Total Score:** {result['total']}/20")

            with col2:
                st.markdown("### Prompt Review")
                st.write(f"**Level:** {result['level']}")
                st.write(f"**Summary:** {result['summary']}")

            st.markdown("### Improvement Suggestions")
            for suggestion in result["suggestions"]:
                st.write(f"- {suggestion}")

        else:
            st.warning("Please enter a prompt first.")

elif menu == "LLM Response Comparison":
    st.subheader("⚖️ LLM Response Comparison")

    prompt = st.text_area(
        "Prompt",
        height=100,
        placeholder="Enter the original prompt here...",
    )
    response_a = st.text_area(
        "Response A",
        height=180,
        placeholder="Paste the first LLM response here...",
    )
    response_b = st.text_area(
        "Response B",
        height=180,
        placeholder="Paste the second LLM response here...",
    )

    reviewer = st.text_input("Reviewer Name", value="Ishwari")

    if st.button("Compare Responses"):
        if prompt.strip() and response_a.strip() and response_b.strip():
            result = evaluate_llm_responses(prompt, response_a, response_b)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Response A")
                st.write(f"**Relevance:** {result['A']['relevance']}/5")
                st.write(f"**Clarity:** {result['A']['clarity']}/5")
                st.write(f"**Safety:** {result['A']['safety']}/5")
                st.write(f"**Factuality:** {result['A']['factuality']}/5")
                st.write(f"**Instruction Following:** {result['A']['instruction_following']}/5")
                st.write(f"**Total Score:** {result['A']['total']}/25")

            with col2:
                st.markdown("### Response B")
                st.write(f"**Relevance:** {result['B']['relevance']}/5")
                st.write(f"**Clarity:** {result['B']['clarity']}/5")
                st.write(f"**Safety:** {result['B']['safety']}/5")
                st.write(f"**Factuality:** {result['B']['factuality']}/5")
                st.write(f"**Instruction Following:** {result['B']['instruction_following']}/5")
                st.write(f"**Total Score:** {result['B']['total']}/25")

            st.success(f"Winner: {result['winner']}")
            st.info(result["summary"])

            init_history_state()
            add_history_row(
                prompt=prompt,
                reviewer=reviewer,
                winner=result["winner"],
                score_a=result["A"]["total"],
                score_b=result["B"]["total"],
                summary=result["summary"],
            )

        else:
            st.warning("Please fill in the prompt, Response A, and Response B.")

elif menu == "Evaluation History":
    st.subheader("🗂️ Evaluation History")

    init_history_state()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Refresh History"):
            st.rerun()

    with col2:
        if st.button("Clear History"):
            reset_history()
            st.success("Evaluation history cleared.")
            st.rerun()

    if len(st.session_state.evaluation_history) > 0:
        history_df = pd.DataFrame(st.session_state.evaluation_history)
        st.dataframe(history_df, use_container_width=True)

        csv = history_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Evaluation History CSV",
            data=csv,
            file_name="evaluation_history.csv",
            mime="text/csv",
        )
    else:
        st.info("No evaluations recorded yet.")

elif menu == "Batch Prompt Review":
    st.subheader("📂 Batch Prompt Review")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("### Uploaded Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        prompt_col = st.selectbox("Select prompt column", df.columns)

        if st.button("Run Batch Prompt Evaluation"):
            output_rows = []

            for prompt_text in df[prompt_col].astype(str):
                result = evaluate_prompt_quality(prompt_text)
                output_rows.append({
                    "prompt": prompt_text,
                    "clarity": result["clarity"],
                    "specificity": result["specificity"],
                    "completeness": result["completeness"],
                    "ambiguity_control": result["ambiguity_control"],
                    "total_score": result["total"],
                    "level": result["level"],
                    "summary": result["summary"],
                    "top_suggestion": result["suggestions"][0] if result["suggestions"] else "",
                })

            output_df = pd.DataFrame(output_rows)
            st.write("### Batch Evaluation Results")
            st.dataframe(output_df, use_container_width=True)

            csv = output_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Batch Results CSV",
                data=csv,
                file_name="batch_prompt_review.csv",
                mime="text/csv",
            )