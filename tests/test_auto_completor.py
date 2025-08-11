import pytest
import auto_completor
import time

ARCHIVE_DIRECTORY = "../Archive"


@pytest.fixture
def completor():
    completor = auto_completor.AutoCompletor(ARCHIVE_DIRECTORY)
    return completor


def test_simple_input(completor):
    input_text = "my name is"
    completions = completor.get_best_k_completions(input_text)
    assert len(completions) == 5
    print("\ncompletions for input: ", input_text)
    for completion in completions:
        print(completion)


def test_input_with_whitespace(completor):
    input_text_with_whitespace = "this           is   "
    input_text_without_whitespace = "this is"
    completions_with_whitespace = completor.get_best_k_completions(input_text_with_whitespace)
    completions_without_whitespace = completor.get_best_k_completions(input_text_without_whitespace)
    reprs_with_whitespace = [repr(c) for c in completions_with_whitespace]
    reprs_without_whitespace = [repr(c) for c in completions_without_whitespace]

    assert reprs_with_whitespace == reprs_without_whitespace


def test_input_with_symbols(completor):
    input_text_with_symbols = "my, name, is"
    input_text_without_symbols = "my name is"
    completions_with_symbols = completor.get_best_k_completions(input_text_with_symbols)
    completions_without_symbols = completor.get_best_k_completions(input_text_without_symbols)
    reprs_with_symbols = [repr(c) for c in completions_with_symbols]
    reprs_without_symbols = [repr(c) for c in completions_without_symbols]

    assert reprs_with_symbols == reprs_without_symbols


def test_input_with_typo(completor):
    input_text_without_typo = "shell scripting"

    # missing character typo
    input_text_with_typo = "shell scriting"
    completions_with_typo = completor.get_best_k_completions(input_text_with_typo)
    reprs_with_typo = [repr(c) for c in completions_with_typo]
    assert any(input_text_without_typo in s.lower() for s in reprs_with_typo)

    # extra character typo
    input_text_with_typo = "shell scripxting"
    completions_with_typo = completor.get_best_k_completions(input_text_with_typo)
    reprs_with_typo = [repr(c) for c in completions_with_typo]
    assert any(input_text_without_typo in s.lower() for s in reprs_with_typo)

    # wrong character typo
    input_text_with_typo = "shell screpting"
    completions_with_typo = completor.get_best_k_completions(input_text_with_typo)
    reprs_with_typo = [repr(c) for c in completions_with_typo]
    assert any(input_text_without_typo in s.lower() for s in reprs_with_typo)


def test_completion_search_performance(completor):
    test_inputs = [
        "my name is",
        "The Concepts section helps you learn about the parts of the Kubernetes",
        "shell scripting",
        "python programming language",
        "introduction to machine learning"
    ]

    durations = []

    for text in test_inputs:
        start = time.perf_counter()
        completor.get_best_k_completions(text)
        durations.append(time.perf_counter() - start)

    avg_duration = sum(durations) / len(durations)

    print(f"\nAverage autocomplete time over {len(test_inputs)} inputs: {avg_duration:.3f} seconds")
    assert avg_duration < 5.5
