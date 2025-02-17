import logging
import re

from langchain_core.language_models import BaseLLM
from langchain_core.prompts import ChatPromptTemplate

code_block_pattern = r"```(?:\w+\s+)?(.*?)```"
compiled_code_block_pattern = re.compile(code_block_pattern, re.DOTALL)

logger = logging.getLogger(__name__)


def prompt_code(llm: BaseLLM, prompt: ChatPromptTemplate, variables: dict = {}):
    """
    Prompt for code (automatically extracts code)

    :param prompt:
    :param llm:
    :param variables:
    :return:
    """

    chain = prompt | llm

    answer = ""
    answer = chain.invoke(variables)

    logger.debug(f"received answer\n{answer}")

    code_blocks = get_code_blocks(answer)

    #logger.debug(f"blocks \n{code_blocks}")

    return code_blocks


def prompt_code_units(llm: BaseLLM, prompt: ChatPromptTemplate, variables: dict = {}, samples: int = 1):
    """
    Prompt code solutions

    :param llm:
    :param prompt:
    :param variables:
    :param samples:
    :return:
    """

    code_solutions = []
    for sample in range(samples):
        code_blocks = prompt_code(llm, prompt, variables)
        # assume it's the first code block
        code_solution = code_blocks[0]
        code_solutions.append(code_solution)

    return code_solutions


def get_code_blocks(answer: str) -> list:
    """
    Extract all code blocks

    :param answer:
    :return:
    """

    blocks = compiled_code_block_pattern.findall(answer)
    return [block.strip() for block in blocks]