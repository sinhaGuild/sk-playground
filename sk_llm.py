import semantic_kernel as sk
import streamlit as st
from dotenv import load_dotenv
from semantic_kernel.connectors.ai.open_ai import (
    AzureTextCompletion,
    OpenAIChatCompletion,
)

from utils import build_skill_matrix, format_output_as_markdown

SKILLS_PATH = "./skills"


def get_semantic_skill(text, skills):
    return skills[skills["function"] == text]["skill"].values[0]


class Semantic_LLM:
    def __init__(
        self, service_id, model_id="gpt-3.5-turbo-16k", use_Azure=False
    ) -> None:
        # Initialize the kernel
        self.kernel = sk.Kernel()
        self.SKILLS_MATRIX = build_skill_matrix(SKILLS_PATH)

        # Initialize llm on kernel
        if use_Azure:
            deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
            self.kernel.add_text_completion_service(
                "dv", AzureTextCompletion(deployment, endpoint, api_key)
            )
        else:
            if load_dotenv():
                api_key, org_id = sk.openai_settings_from_dot_env()
            # fix for streamlit cloud
            else:
                api_key = st.secrets["OPENAI_API_KEY"]
                org_id = st.secrets["OPENAI_ORG_ID"]
            self.kernel.add_chat_service(
                service_id, OpenAIChatCompletion(model_id, api_key, org_id)
            )

    def build_semantic_function(self, function_name):
        return self.kernel.import_semantic_skill_from_directory(
            SKILLS_PATH, get_semantic_skill(function_name, self.SKILLS_MATRIX)
        )[function_name]

    async def run_sequential_functions(self, seq, text):
        re = await self.kernel.run_async(*seq, input_str=text)
        return re

    def build_semantic_function_array(self, functions_list):
        re = []
        for func in functions_list:
            re.append(self.build_semantic_function(str(func)))
        re.append(format_output_as_markdown(self.kernel))
        return re
