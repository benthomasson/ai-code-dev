#!/usr/bin/env python3

"""
Answer questions about a code.
"""

import ast

import litellm
import click
from rich import print
from rich.prompt import Prompt

from gen_utils import parse_code_blobs


@click.command()
@click.argument("files", nargs=-1)
@click.option(
    "--api-base",
    default="http://localhost:11434",
    help="Base URL for the API.",
    envvar="API_BASE",
)
@click.option(
    "--model", default="ollama/qwen3:14b", help="Model to use for generation."
)
@click.option(
    "--max-tokens", default=3000, help="Maximum number of tokens to generate."
)
@click.option("--temperature", default=0.7, help="Temperature to use for generation.")
def main(files, api_base, model, max_tokens, temperature):

    system_prompt = """You are a helpful code assistant.
    Given the following code answer questions about it"""

    code = []
    for file in files:
        with open(file) as f:
            code.append(f"{file}:\n{f.read()}")

    system_prompt += "\n\n".join(code)

    # Iterate until all questions are answered
    done = False
    while not done:

        prompt = Prompt.ask(">")

        if prompt == "":
            break

        # Call the model with a system and user prompts.
        # Think if the system prompt as the function we are calling
        # and the prompt as the arguments to that functions.
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            num_ctx=8192,
            api_base=api_base,
        )

        # Extract the content from the response messages.
        content = response["choices"][0]["message"]["content"]
        print(content)


if __name__ == "__main__":
    main()
