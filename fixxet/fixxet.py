# Fixxit
from sys import argv
from pathlib import Path
from enum import Enum, unique
import re


EXCLUDE_FOLDERS: list = [
    '.git',
    'bin',
    'out',
    '.vscode',
    '__pycache__',
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


class Task:
    def __init__(self, file_name:str, line_number: int, text: str, task_type: TaskType):
        self.file_name = file_name
        self.line_number = line_number
        self.text = text
        self.task_type = task_type


def search_dir(root_path: str, 
           whitelist_ext: list = None,
           exclude_filenames: list = None,
          ) -> list:
    """ Recursively walks down directories from the root_path for TODOs and FIXMEs and         
        returns a list of Task objects containing metadata about the findings.

            Parameters:
                root_path (str): The root directory to search
                whitelist_ext (list): The list of extensions to whitelist
                exclude_filenames (list): The list of filenames to filter out

            Returns:
                tasks (list): List of Task Objects containing metadata
    """
    tasks: list = []
    wle: bool = True
    efn: bool = True

    if whitelist_ext is None:
        whitelist_ext = []
        wle = False

    if exclude_filenames is None:
        exclude_filenames = []
        efn = False
    
    for pathx in root_path.iterdir():
        if pathx.is_dir():
            if pathx.name not in EXCLUDE_FOLDERS:
                tasks.extend(search_dir(pathx, whitelist_ext, exclude_filenames))
        elif (pathx.suffix not in EXCLUDE_FILETYPES and
                pathx.name not in EXCLUDE_FILETYPES):
                
                if wle and pathx.suffix not in whitelist_ext:
                    continue
                if efn and pathx.name in exclude_filenames:
                    continue
                # tasks.append(pathx)
                tasks.extend(search_file(pathx))
    return tasks


def search_file(file_path: Path) -> list:
    """ Searches through the file, at the passed file_path, for TODOs and FIXMEs.
        Returns a list of Task objects containing metadata about the TODO.

            Parameters:
                file_path (Path): The path to the file

            Returns:
                tasks (list): A list of Task Objects containing metadata
    """

    tasks: list = []
    
    with file_path.open() as f:
        lines: list = f.read().splitlines()
        file_name: str = file_path.name

        for i, line in enumerate(lines):
            if 'TODO' in line or 'FIXME' in line:
                task_type: TaskType = None

                if 'TODO' in line:
                    task_type = TaskType.TODO
                if 'FIXME' in line:
                    task_type = TaskType.FIXME
                # FIXME(devon): Only remove the whitespaces that are in front
                edited_line: str = re.sub(r'[\n\t\s]*', '', line)
                tasks.append(Task(file_name, i, edited_line, task_type))

    return tasks


def print_help():
    """ Prints out the help menu to the console. """

    print('Usage: fixxet [root_path] ([file_extension_whitelist..] | [filename_excludes..]) [options]')
    print('Example: fixxet -wle .py .json')
    print('         fixxet ./src -wle .zig .json -ef cimport.zig\n')
    print('Options: ')
    print('-wle\tSet a extension whitelist filter')
    print('-ef\tAppend filename to the exclude filter')
    print('')
    print('General Options: ')
    print('-h, --help\tPrint usage information')


def main():
    # The root directory to recursively check
    root_path: Path = None
    
    # Check to see if the user requested help
    if '-h' in argv or '--help' in argv:
        print_help()
        return

    current_option: CurrentOption = CurrentOption.NONE
    whitelist_ext: list = []
    exclude_dirs: list = []
    exclude_filenames: list = []

    arg_len: int = len(argv)

    # If no root path was specified
    if arg_len == 1:
        root_path = Path('.')
    else:
        for i, arg in enumerate(argv):
            if i == 1:
                if '-' in arg or '--' in arg:
                    root_path = Path('.')
                else:
                    root_path = Path(arg)
                    continue
            if '-wle' in arg:
                current_option = CurrentOption.WL_EXT
            elif '-ef' in arg:
                current_option = CurrentOption.EX_FN
            else:
                if current_option == CurrentOption.WL_EXT:
                    whitelist_ext.append(arg)
                elif current_option == CurrentOption.EX_FN:
                    exclude_filenames.append(arg)
    
    status_string: str = '[FIXXET] Searching in '

    for wle_entry in whitelist_ext:
        status_string = status_string + f'{wle_entry} '
    status_string = status_string + f' files (excluding:'
    
    for ef_entry in exclude_filenames:
        status_string = status_string + f' {ef_entry}'

    status_string = status_string + f') from root: {root_path.absolute()}'

    print(status_string)
    
    tasks: list = search_dir(
        root_path, 
        whitelist_ext if len(whitelist_ext) > 0 else None,
        exclude_filenames if len(exclude_filenames) > 0 else None
    )
    
    todos_count: int = 0
    fixmes_count: int = 0

    print('Found:')
    for task in tasks:
        print(f'\t{task.file_name} on line {task.line_number}: {task.text}')
        if task.task_type == TaskType.TODO:
            todos_count += 1
        elif task.task_type == TaskType.FIXME:
            todos_count += 1
    

    print(f'{todos_count} TODOs, {fixmes_count} FIXMEs')


if __name__ == '__main__':
    main()
