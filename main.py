import auto_completor


def main():
    directory = 'Archive'
    completor = auto_completor.AutoCompletor(directory)
    text = input("Enter text: ")
    results = completor.search(text)
    print(f'found {len(results)} results')
    for result in results[:10]:
        print(result)


if __name__ == '__main__':
    main()

