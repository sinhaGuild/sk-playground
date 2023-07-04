import datetime

import semantic_kernel as sk
import streamlit as st
from dotenv import load_dotenv
from semantic_kernel import ContextVariables
from semantic_kernel.connectors.ai.open_ai import (
    AzureTextCompletion,
    OpenAIChatCompletion,
    OpenAITextCompletion,
)

from utils import build_skill_matrix, format_output_as_markdown, get_semantic_skill

load_dotenv()


st.set_page_config(layout="wide")

SKILLS_PATH = "./skills"


@st.cache_resource
def build_skills_index():
    return build_skill_matrix(SKILLS_PATH)


SKILLS_MATRIX = build_skills_index()
kernel = sk.Kernel()

# context variables
# ctx = ContextVariables()
# ctx.set("style", "science-fiction")

# ctx = kernel.create_new_context()
# ctx["style"] = "horror"


def build_chat_service(service_id, model_id="gpt-3.5-turbo-16k", use_Azure=False):
    if use_Azure:
        deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
        kernel.add_text_completion_service(
            "dv", AzureTextCompletion(deployment, endpoint, api_key)
        )
    else:
        api_key, org_id = sk.openai_settings_from_dot_env()
        kernel.add_chat_service(
            service_id, OpenAIChatCompletion(model_id, api_key, org_id)
        )

    return kernel


kernel = build_chat_service("gpt")


async def run_sequential_functions(seq, text):
    # context = kernel.create_new_context()
    # for f in seq:
    #     await f(context=context)
    # ctx["input"] = text
    re = await kernel.run_async(*seq, input_str=text)
    return re


def build_semantic_function(function_name):
    return kernel.import_semantic_skill_from_directory(
        SKILLS_PATH, get_semantic_skill(function_name, SKILLS_MATRIX)
    )[function_name]


def build_semantic_function_array(functions_list):
    re = []
    for func in functions_list:
        re.append(build_semantic_function(str(func)))
    re.append(format_output_as_markdown(kernel))
    return re


if "history" not in st.session_state:
    st.session_state["history"] = []

st.markdown("## $\mathbb{S}$emantic $\mathbb{K}$ernel Playground")
st.sidebar.image("https://i.imgur.com/4D2ikLS.png", clamp=True, width=150)
st.sidebar.markdown("# $\mathbb{Parameters}$")
# -- Select Llama index or langchain
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
            submitted = st.form_submit_button("$\mathcal{Submit}$")

            if submitted:
                with st.container():
                    st.divider()
                    with st.spinner(f"Running Semantic functions as {radio}.."):
                        if radio == "Single":
                            func = build_semantic_function(sl_semanticFunction)
                            re = func(text)
                        else:
                            seq = build_semantic_function_array(
                                multisl_semanticFunction
                            )
                            re = await run_sequential_functions(seq, text)
                    st.markdown(re)
                    # st.markdown(re_seq)
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
