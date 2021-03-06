"""
    Parses all files in discord_commands extracting the command and the
    object name for the command, then writes it to
    discord_commands/all_commands.py
"""

import os
import re

cmd_file_pattern = re.compile(r'\w*_command\.py')


def get_all_command_files():
    """
        Gets all files matching the cmd_file_pattern

        :return: list
    """
    result = []
    for root, _, files in os.walk("discord_commands/"):
        # Skip __pycache__ folders
        if root.endswith('__pycache__'):
            continue

        for f in files:
            if cmd_file_pattern.match(f):
                result.append(root + "/" + f)

    return result


def build_all_commands(files):
    """
    Builds a dictionary of all of the commands, removes unncessary files from files parameter
    and returns updated files list

        :param files: list

    :return: list of files that have commands in them
    """

    cmd_pattern = re.compile(r'self\._command = \"(![a-zA-Z0-9]*)\"')
    class_pattern = re.compile(r'class ([a-zA-Z0-9]*)\(')
    cmds = {}
    files_to_remove = []

    for f in files:
        command = class_name = ""
        for _, line in enumerate(open(f)):
            cmd_match = cmd_pattern.search(line)
            class_match = class_pattern.search(line)
            if cmd_match:
                command = cmd_match.group(1)

            if class_match:
                class_name = class_match.group(1)

        if class_name and command:
            cmds[command] = {'class': class_name, 'file': f}
        else:
            files_to_remove.append(f)

    # Remove files that had no command
    for f in files_to_remove:
        files.remove(f)

    return cmds, files


def write_new_all_commands(cmd_dict, files):
    """
        Writes a new all_commands.py using the commands given in cmd_dict

        :param cmd_dict: dict
        :param files: list
    """
    fo = open('discord_commands/all_commands.py', 'w')
    fo.write('"""\n\tHouses a dictionary holding references to every command' +
             'available\n\tThis file is generated by scripts/' + 'update_all_commands.py\n"""\n')

    # Generate import lines
    for f in files:
        import_string = " import "
        from_string = __generate_from_string(f)

        for value in cmd_dict.values():
            if value['file'] == f:
                import_string += value['class']
        fo.write(from_string + import_string + "\n")

    # Write out command dict
    fo.write("\n\nCOMMANDS = {\n")
    for command, value in cmd_dict.items():
        print("Inserting entry for {}".format(command))
        fo.write("    '{0}': {1},\n".format(command, value['class']))
    fo.write("    'aliases': {\'servers\': {}, \'users\': {}}\n")
    fo.write("}\n")
    fo.close()

def __generate_from_string(module_file):
    """
        Generates the "from <module_name>" part of the import

        :param module_file: str
    """
    module = module_file.replace('discord_commands/', '')
    module = module.replace('.py', '')
    module = module.split('/')[0]

    return "from ." + module


if __name__ == "__main__":
    cmd_files = get_all_command_files()
    commands, cmd_files = build_all_commands(cmd_files)
    write_new_all_commands(commands, cmd_files)
