import os

import pandas as pd


def build_skill_matrix(PATH, to_pandas=True):
    res = []
    for root, dirs, files in os.walk(PATH):
        if root == PATH:
            continue
        if len(root.split(os.path.sep)) > 3:
            continue
        for directory in dirs:
            # res.extend(dirs)
            res.append({"skill": root.split("/")[2], "function": directory})
    if to_pandas:
        return pd.DataFrame(res, columns=["skill", "function"])
    else:
        return res


def get_semantic_skill(text, skills):
    return skills[skills["function"] == text]["skill"].values[0]


prompt_template_sample = """
FORMAT THE PROVIDED INPUT BELOW TO MARKDOWN.
+++++

{{$input}}
+++++

"""


def format_output_as_markdown(kernel):
    return kernel.create_semantic_function(
        prompt_template_sample, max_tokens=1500, top_p=0.96, temperature=0.0
    )
