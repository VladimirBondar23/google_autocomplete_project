import auto_completor

ARCHIVE_DIRECTORY = "Archive"
LOADING_MSG = "Loading the files and preparing the system"
READY_MSG = "The system is ready."
PROMPT_MSG = "Enter your text: "
EXIT_SYMBOL = '#'
COMPLETIONS_LABEL = "Here are 5 suggestions:"
NO_SUGGESTIONS_LABEL = "No suggestions were found!"


def load_archive() -> auto_completor.AutoCompletor:
    print(LOADING_MSG)
    completor = auto_completor.AutoCompletor(ARCHIVE_DIRECTORY)
    print(READY_MSG, end=' ')
    return completor


def start_user_interaction(completor: auto_completor.AutoCompletor):
    text = input(PROMPT_MSG)
    while text != EXIT_SYMBOL:
        completions = completor.get_best_k_completions(text)
        if len(completions) == 0:
            print(NO_SUGGESTIONS_LABEL)
        else:
            print(COMPLETIONS_LABEL)
            for index, completion in enumerate(completions):
                print(f'{index + 1}. {completion}')
        text = input(PROMPT_MSG)


def main():
    completor = load_archive()
    start_user_interaction(completor)


if __name__ == '__main__':
    main()
