from ai_model import AiModel

MOCK_USERNAME = "mock user"
EXIT_INPUT = "exit"


def run(model):
    text_to_complete = input("Enter text to complete: ")
    while text_to_complete != EXIT_INPUT:
        completions = model.get_best_completions(text_to_complete, MOCK_USERNAME)
        print(completions)
        text_to_complete = input("Enter text to complete: ")


def main():
    model = AiModel()
    model.add_user(MOCK_USERNAME)
    run(model)


if __name__ == "__main__":
    main()
