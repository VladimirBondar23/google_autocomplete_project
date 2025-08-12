from ai_model import AiModel
import asyncio

MOCK_USERNAME = "mock user"
EXIT_INPUT = "exit"


async def run(model):
    text_to_complete = input("Enter text to complete: ")
    while text_to_complete != EXIT_INPUT:
        completions = await model.get_best_completions(text_to_complete, MOCK_USERNAME)
        print(completions)
        text_to_complete = input("Enter text to complete: ")


async def main():
    model = AiModel()
    await model.add_user(MOCK_USERNAME)
    await run(model)


if __name__ == "__main__":
    asyncio.run(main())
