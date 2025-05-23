#!/usr/bin/env python3

"""
Answer questions about code.
"""

import time

import click
import litellm
from rich.console import Console
from rich.prompt import Prompt

from gen_utils import parse_code_blobs, rule

console = Console()


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
@click.option("--num-ctx", default=8192, help="Size of the context")
@click.option("--temperature", default=0.7, help="Temperature to use for generation.")
@click.option("--output", default="output.txt", help="Log of the LLM output responses.")
@click.option(
    "--output_code", default="output.py", help="Log of the code in LLM responses."
)
def main(files, api_base, model, max_tokens, temperature, num_ctx, output, output_code):

    system_prompt = """You are a helpful code assistant.
    Given the following code answer questions about it.
    """

    code = []
    for file in files:
        with open(file) as f:
            code.append(f"{file}:\n{f.read()}")

    system_prompt += "\n\n".join(code)

    console.print(
        f"System prompt length {len(system_prompt)} approx tokens {len(system_prompt)//4}"
    )

    # Iterate until all questions are answered
    done = False
    while not done:
        prompt = Prompt.ask("Ask code")

        if prompt.strip() == "":
            continue

        # Call the model with a system and user prompts.
        # Think of the system prompt as the function we are calling
        # and the prompt as the arguments to that functions.
        start = time.time()
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

        end = time.time()

        # Extract the content from the response messages.
        content = response["choices"][0]["message"]["content"]
        console.print(content)
        console.print(f"Took {end-start} seconds")

        with open(output, "a") as f:
            rule(f)
            f.write(content)
            rule(f)

        code = parse_code_blobs(content)
        if code:
            with open(output_code, "a") as f:
                rule(f)
                f.write(code)
                rule(f)


if __name__ == "__main__":
    main()
