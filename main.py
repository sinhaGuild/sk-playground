import datetime
import streamlit as st
from dotenv import load_dotenv
from utils import build_skill_matrix
from sk_llm import Semantic_LLM

load_dotenv()
st.set_page_config(layout="wide")


@st.cache_resource
def build_skills_index():
    return build_skill_matrix("./skills")


SKILLS_MATRIX = build_skills_index()


sem_kernel = Semantic_LLM(service_id="gpt")


if "history" not in st.session_state:
    st.session_state["history"] = []

st.markdown("## $\mathbb{S}$emantic $\mathbb{K}$ernel Playground")
st.sidebar.image("https://i.imgur.com/4D2ikLS.png", clamp=True, width=150)
st.sidebar.markdown("# $\mathbb{Parameters}$")
radio = st.sidebar.radio("Select Orchestration Method", ("Single", "Chain"))

if radio == "Single":
    st.sidebar.markdown("### $\mathbf{Skills\ and\ Semantic\ Functions}$")
    sl_semanticFunction = st.sidebar.selectbox(
        "Select a __function__ to run against your prompt",
        SKILLS_MATRIX["function"].values.tolist(),
    )
else:
    st.sidebar.markdown("### $\mathbf{Orchestrating\ Functions}$")
    multisl_semanticFunction = st.sidebar.multiselect(
        "Select specific __skills__ you'd like the $\mathcal{LLM}$ to use and run in sequence such as $Joke\ -\ BookIdeas\ -\ Markdown$",
        SKILLS_MATRIX["function"].values.tolist(),
    )


async def main():
    with st.container():
        with st.form("query_form"):
            st.markdown("### $\mathbb{PROMPT}$")
            text = st.text_area(
                "Enter any subject or topic.",
                "A Beaver and an eagle.",
            )
            submitted = st.form_submit_button(
                "$\mathcal{Submit}$", use_container_width=True
            )

            if submitted:
                with st.container():
                    st.divider()
                    with st.spinner(f"Running Semantic functions as {radio}.."):
                        if radio == "Single":
                            func = sem_kernel.build_semantic_function(
                                sl_semanticFunction
                            )
                            re = func(text)
                        else:
                            seq = sem_kernel.build_semantic_function_array(
                                multisl_semanticFunction
                            )
                            re = await sem_kernel.run_sequential_functions(seq, text)
                    st.markdown(re)
                    st.session_state["history"].append(re)
    st.divider()
    with st.container():
        st.markdown("### $\mathbb{HISTORY}$")
        st.divider()
        for i in reversed(st.session_state.history):
            with st.container():
                st.markdown(f"- Inference @ `{datetime.datetime.now()}`")
                st.info(i)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
