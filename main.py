"""
Auto-completor main module.
This module is responsible for interaction with the user via CLI.

@Author: Gal Helner
"""
import auto_completor

# constants
ARCHIVE_DIRECTORY = "Archive"
LOADING_MSG = "Loading the files and preparing the system"
READY_MSG = "The system is ready."
PROMPT_MSG = "Enter your text: "
EXIT_INPUT = 'exit'
INPUT_SEPARATOR_SYMBOL = '#'
COMPLETIONS_LABEL = "Here are 5 suggestions:"
NO_SUGGESTIONS_LABEL = "No suggestions were found!"


def load_archive() -> auto_completor.AutoCompletor:
    """
    Loads the system data from the archive
    :return: AutoCompletor instance
    """
    print(LOADING_MSG)
    completor = auto_completor.AutoCompletor(ARCHIVE_DIRECTORY)
    print(READY_MSG, end=' ')
    return completor


def start_user_interaction(completor: auto_completor.AutoCompletor):
    """
    Starts the interaction with the user via CLI.
    :param completor: AutoCompletor instance
    """
    text = input(PROMPT_MSG)
    while text != EXIT_INPUT:
        text_for_search = text
        last_char_index = len(text) - 1
        if text[last_char_index] == INPUT_SEPARATOR_SYMBOL:
            # get rid of the seperator symbol before searching
            text_for_search = text[:-1]

        # get the best completion and print them
        completions = completor.get_best_k_completions(text_for_search)
        if len(completions) == 0:
            print(NO_SUGGESTIONS_LABEL)
        else:
            print(COMPLETIONS_LABEL)
            for index, completion in enumerate(completions):
                print(f'{index + 1}. {completion}')

        # preparing next search input text
        if text[last_char_index] == INPUT_SEPARATOR_SYMBOL:
            text_for_search = ''
            text = ''
        text += input(PROMPT_MSG + text_for_search)


def main():
    """
    Main function.
    """
    completor = load_archive()
    start_user_interaction(completor)


if __name__ == '__main__':
    main()
