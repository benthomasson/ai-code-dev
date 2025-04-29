#!/usr/bin/env python3

"""
Answer questions about a code.
"""

import litellm
import click
from rich import print
from rich.prompt import Prompt


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
@click.option(
    "--num-ctx", default=8192, help="Size of the context"
)
@click.option("--temperature", default=0.7, help="Temperature to use for generation.")
def main(files, api_base, model, max_tokens, temperature, num_ctx):
    system_prompt = """You are a helpful code assistant.
    Given the following code answer questions about it"""

    code = []
    for file in files:
        with open(file) as f:
            code.append(f"{file}:\n{f.read()}")

    system_prompt += "\n\n".join(code)

    print(f"System prompt length {len(system_prompt)} approx tokens {len(system_prompt)//4}")

    # Iterate until all questions are answered
    done = False
    while not done:
        prompt = Prompt.ask(">")

        if prompt.strip() == "":
            continue

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
            num_ctx=num_ctx,
            api_base=api_base,
        )

        # Extract the content from the response messages.
        content = response["choices"][0]["message"]["content"]
        print(content)


if __name__ == "__main__":
    main()
