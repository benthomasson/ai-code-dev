#!/usr/bin/env python3

"""
Generate code from a given prompt.
"""

import ast

import litellm
import click
from rich import print

from gen_utils import parse_code_blobs


@click.command()
@click.option(
    "--system-prompt", default=None, help="System prompt to use.", prompt=True
)
@click.option(
    "--prompt", default=None, help="Prompt to use for generation.", prompt=True
)
@click.option(
    "--output", default=None, help="Output file to write the generated code to."
)
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
def main(system_prompt, prompt, output, api_base, model, max_tokens, temperature):

    # Iterate until we get valid code.
    done = False
    while not done:

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

        # Extract the generated code from the content
        # code blobs should look like:
        # ```python
        #    ...
        # ```
        code = parse_code_blobs(content)
        print("=" * 80)
        print(f"{code=}")
        print("=" * 80)

        # If we cannot find code try again.
        if not code:
            continue

        # If we cannot parse the code try again.
        try:
            ast.parse(code)
        except SyntaxError as e:
            print("Failed with syntax error", e)
            continue

        # Save the code to the output file if given.
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"✅ Code saved to {output}")
            done = True
        # else print the code
        else:
            print("Generated Code:\n")
            print(code)
            done = True


if __name__ == "__main__":
    main()
