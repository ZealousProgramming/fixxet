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
]

@unique
class TaskType(Enum):
    TODO = 0
    FIXME = 1


class Task:
    def __init__(self, file_name:str, line_number: int, text: str, task_type: TaskType):
        self.file_name = file_name
        self.line_number = line_number
        self.text = text
        self.task_type = task_type


def print_directories(root_path, prefix: str = ''):
    prefix = prefix + '    '

    if root_path is not None:
        for pathx in root_path.iterdir():
            if pathx.is_dir():
                if pathx.name not in EXCLUDE_FOLDERS: 
                    # print(f'{prefix}{pathx}')
                    print_directories(pathx, prefix)
            else:
                if (pathx.suffix not in EXCLUDE_FILETYPES and
                    pathx.name not in EXCLUDE_FILETYPES):
                    print(f'{prefix}{pathx}')


def search(root_path: str, whitelist: list = None) -> list:
    tasks: list = []
    
    for pathx in root_path.iterdir():
        if pathx.is_dir():
            if pathx.name not in EXCLUDE_FOLDERS:
                tasks.extend(search(pathx, whitelist))
        else:
            if whitelist is None:
                if (pathx.suffix not in EXCLUDE_FILETYPES and
                    pathx.name not in EXCLUDE_FILETYPES):
                    tasks.append(pathx)
            else:
                if (pathx.suffix not in EXCLUDE_FILETYPES and
                    pathx.name not in EXCLUDE_FILETYPES and
                    pathx.suffix in whitelist):
                    # tasks.append(pathx)
                    tasks.extend(find_task(pathx))
    return tasks


def find_task(file_path: Path) -> list:
    tasks: list = []
    
    with file_path.open() as f:
        lines: list = f.read().splitlines()
        file_name: str = file_path.name

        for i, line in enumerate(lines):
            # print(line)
            if 'TODO' in line or 'FIXME' in line:
                task_type: TaskType = None

                if 'TODO' in line:
                    task_type = TaskType.TODO
                if 'FIXME' in line:
                    task_type = TaskType.FIXME

                edited_line: str = re.sub(r'[\n\t\s]*', '', line)
                tasks.append(Task(file_name, i, edited_line, task_type))

    return tasks


def print_help():
    print('Usage: fixxet [root_path] [file_type_whitelist..] [options]')
    print('Example: fixxet . -wl .py .json\n')
    print('Commands: ')
    print('-wl\tSet a whitelist filter')
    print('')
    print('General Options: ')
    print('-h, --help\tPrint usage information')


def main():
    # The root directory to recursively check
    root_path: Path = None

    # Extentsion
    ext: str = ''
    
    # Check to see if the user requested help
    if '-h' in argv or '--help' in argv:
        print_help()
        return

    arg_len: int = len(argv)
    whitelist: list = []

    append_wl: bool = False
    
    # If no root path was specified
    if arg_len == 1:
        root_path = Path('.')
    else:
        for i, arg in enumerate(argv):
            if i == 1:
                root_path = Path(arg)
            elif append_wl is True:
                if '-' in arg:
                    if arg.index('-') == 0:
                        append_wl = False
                        break
                elif '--' in arg:
                    if arg.index('--') == 0:
                        append_wl = False
                        break
                else:
                    whitelist.append(arg)
            elif '-wl' in arg:
                append_wl = True
    
    status_string: str = '[FIXXET] Searching in '
    for wl_entry in whitelist:
        status_string = status_string + f'{wl_entry} '

    status_string = status_string + f' files from root: {root_path.absolute()}'

    print(status_string)
    
    tasks: list = search(root_path, whitelist if len(whitelist) > 0 else None)
    
    todos_count: int = 0
    fixmes_count: int = 0

    print('Found:')
    for task in tasks:
        # print(f'\tLine {task.line_number}: {task.text}')
        if task.task_type == TaskType.TODO:
            todos_count += 1
        elif task.task_type == TaskType.FIXME:
            todos_count += 1

    print(f'{todos_count} TODOs, {fixmes_count} FIXMEs')


if __name__ == '__main__':
    main()
