# Fixxit
from sys import argv
from pathlib import Path
from enum import Enum, unique
from time import perf_counter
import re


EXCLUDE_FOLDERS: list = [
    '.git',
    'bin',
    'out',
    '.vscode',
    '__pycache__',
    'zig-out',
    'zig-cache',
]

EXCLUDE_FILETYPES: list = [
    '.md',
    '.txt',
    '.sh',
    '.bat',
    '.obj',
    '.dll',
    '.lib',
    '.exe',
    '.pdb',
    '.id',
    '.ini',
    '.git',
    '.gitignore',
    '.gitattributes',
    '.gitmodules',
    '.toml',
    '.yaml',
    '.wav',
    '.mp3',
    '.ogg',
    '.png',
    '.jpeg',
    '.bmp',
    '.ps',
    '.lnk',
    '.leo',
]

COMMANDS: list = [
    'run',
    'filter',
]


@unique
class TaskType(Enum):
    TODO = 0
    FIXME = 1


@unique
class CurrentOption(Enum):
    NONE = 0
    WL_EXT = 1
    WL_DIR = 2
    EX_FN = 3
    EX_DIR = 4


class SearchOptions():
    """
    A class to represent options that will alter the behavior of the search.

    Attributes
    ----------
    print_filenames: str
        Option to print the file names of the files searched through
    whitelist_ext: list
        List of file extensions to whitelist
    exclude_dirs: list
        List of directories to blacklist 
    exclude_filenames: list
        List of filenames to blacklist
    """
    def __init__(self, print_filenames):
        self.print_filenames = print_filenames
        self.whitelist_ext = []
        self.exclude_dirs = []
        self.exclude_filenames = []


class Task:
    """ 
    A class to represent the metadata of the TODO/FIXME.

    Attributes
    ----------
    filename: str
        The name of the file that contains the TODO/FIXME
    line_number: int
        The number of the line where the TODO/FIXME was found
    text: str
        The TODO/FIXME comment
    task_type: TaskType
        The type of the task either TaskType.TODO or TaskType.FIXME
    """
    def __init__(self, filename: str, line_number: int, text: str, task_type: TaskType):
        self.filename = filename
        self.line_number = line_number
        self.text = text
        self.task_type = task_type


def search_dir(root_path: str, options: SearchOptions) -> list:
    """ Recursively walks down directories from the root_path for TODOs and FIXMEs and         
        returns a list of Task objects containing metadata about the findings.

            Parameters:
                root_path (str): The root directory to search
                options (SearchOptions): Options that can alter the behavior of the search

            Returns:
                tasks (list): List of Task Objects containing metadata
    """
    tasks: list = []
    wle: bool = True
    ed: bool = True
    efn: bool = True

    if len(options.whitelist_ext) == 0:
        wle = False

    if len(options.exclude_dirs) == 0:
        ed = False

    if len(options.exclude_filenames) == 0:
        efn = False
    
    for pathx in root_path.iterdir():
        if pathx.is_dir():
            if pathx.name not in EXCLUDE_FOLDERS:
                if ed and pathx.name in options.exclude_dirs:
                    continue

                tasks.extend(search_dir(pathx, options))
        elif (pathx.suffix not in EXCLUDE_FILETYPES and
                pathx.name not in EXCLUDE_FILETYPES):
                
                if wle and pathx.suffix not in options.whitelist_ext:
                    continue
                if efn and pathx.name in options.exclude_filenames:
                    continue

                tasks.extend(search_file(pathx, options))

    return tasks


def search_file(file_path: Path, options: SearchOptions) -> list:
    """ Searches through the file, at the passed file_path, for TODOs and FIXMEs.
        Returns a list of Task objects containing metadata about the TODO.

            Parameters:
                file_path (Path): The path to the file
                options (SearchOptions): Options that can alter the behavior of the search

            Returns:
                tasks (list): A list of Task Objects containing metadata
    """

    tasks: list = []
    
    with file_path.open() as f:
        filename: str = file_path.name
        lines: list = f.read().splitlines()
        
        if options.print_filenames is True:
            print(filename)

        for i, line in enumerate(lines):
            if 'TODO' in line or 'FIXME' in line:
                task_type: TaskType = None

                if 'TODO' in line:
                    task_type = TaskType.TODO
                if 'FIXME' in line:
                    task_type = TaskType.FIXME

                edited_line: str = ""  #re.sub(r'[\n\t\s]*', '', line)
                
                for j, char in enumerate(line):
                    if char == '\s' or char == ' ':
                        continue
                    else:
                        edited_line = line[j:]
                        break

                tasks.append(
                    Task(filename, i, edited_line, task_type)
                )

    return tasks


def print_help():
    """ Prints out the help menu to the console. """

    print('Usage: fixxet command [root_path] ([file_extension_whitelist..] | [filename_excludes..] | [directory_excludes..]) [options]')
    print('Example: fixxet run -wle .py .json')
    print('         fixxet run ./src -wle .zig .json -ef cimport.zig\n')

    print('Commands: ')
    print('run\tRuns fixxet')
    print('filter\tPrints the list of standard folders and file extensions to blacklist')
    print('')
    print('Options: ')
    print('-wle\tSet a extension whitelist filter')
    print('-ef\tAppend filename to the exclude filter')
    print('-ed\tAppend directory to the exclude filter')
    print('-p\tPrint out the filenames while searching')
    print('')
    print('General Options: ')
    print('-h, --help\tPrint usage information')


def print_filter():
    """ Prints out the builtin blacklist filters to the console. """

    print('Filters:')
    print('----------')
    print('Directories:')
    for d in EXCLUDE_FOLDERS:
        print(f'\t{d}')
    print('Extensions:')
    for e in EXCLUDE_FILETYPES:
        print(f'\t{e}')


def parse_command(arg: str) -> bool:
    """ Parses the argument and returns if the execution chain should continue.
            
            Parameters:
                arg (str): The argument from argv to parse

            Returns:
                result (bool): Whether or not the execution chain should continue.
    """

    if arg not in COMMANDS:
        print(f"[FIXXET] '{arg}' is not a valid command, please revise and try again. For the list of valid commands, run 'fixxet -help'.")
        return False
    elif arg == 'run':
        return True
    elif arg == 'filter':
        print_filter()
        return False

def main():
    # The root directory to recursively check
    root_path: Path = None
    
    if '--h' in argv or '-help' in argv:
        print(f'[FIXXET] {argv} is not a valid command. \nTry fixxet -h or fixxet --help')
        return
    # Check to see if the user requested help
    if '-h' in argv or '--help' in argv:
        print_help()
        return

    current_option: CurrentOption = CurrentOption.NONE
    options: SearchOptions = SearchOptions(False)

    arg_len: int = len(argv)

    # If no root path was specified
    if arg_len == 2:
        root_path = Path('.')
        if parse_command(argv[1]) is False:
            return
        
    else:
        for i, arg in enumerate(argv):
            if i == 1:
                if parse_command(arg) is False:
                    return
            elif i == 2:
                if '-' in arg or '--' in arg:
                    root_path = Path('.')
                else:
                    root_path = Path(arg)
                    continue
            if '-wle' == arg:
                current_option = CurrentOption.WL_EXT
            elif '-ed' == arg:
                current_option = CurrentOption.EX_DIR
            elif '-ef' == arg:
                current_option = CurrentOption.EX_FN
            elif '-p' == arg:
                options.print_filenames = True
            else:
                if current_option == CurrentOption.WL_EXT:
                    options.whitelist_ext.append(arg)
                elif current_option == CurrentOption.EX_DIR:
                    options.exclude_dirs.append(arg)
                elif current_option == CurrentOption.EX_FN:
                    options.exclude_filenames.append(arg)
    
    status_string: str = '[FIXXET] Searching in '

    for wle_entry in options.whitelist_ext:
        status_string = status_string + f'{wle_entry} '

    status_string = status_string + f' files (excluding files:'
    for ef_entry in options.exclude_filenames:
        status_string = status_string + f' {ef_entry}'

    status_string = status_string + f') not in folders ('
    for ed_entry in options.exclude_dirs:
        status_string = status_string + f' {ed_entry}'

    status_string = status_string + f') starting from root: {root_path.absolute()}'

    print(status_string)

    start_time: float = perf_counter()
    
    tasks: list = search_dir(root_path, options)
    
    end_time: float = perf_counter() - start_time
    todos_count: int = 0
    fixmes_count: int = 0

    print('Found:')
    for task in tasks:
        print(f'\t{task.filename} on line {task.line_number}: {task.text}')
        if task.task_type == TaskType.TODO:
            todos_count += 1
        elif task.task_type == TaskType.FIXME:
            todos_count += 1
    

    print(f'{todos_count} TODOs, {fixmes_count} FIXMEs in {"{:0.4f}".format(end_time)}s')


if __name__ == '__main__':
    main()
