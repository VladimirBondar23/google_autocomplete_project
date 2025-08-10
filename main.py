from archive_reader import start_reading
import auto_completor


def main():
    directory = 'mockArchive'
    data_structure = start_reading(directory)
    auto_completor.init(data_structure)


if __name__ == '__main__':
    main()

