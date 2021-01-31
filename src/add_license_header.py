#!/usr/bin/env python3

from argparse import ArgumentParser, RawTextHelpFormatter
from os.path import isfile
from pathlib import Path
from sys import argv


def add_cs_region(content, region_name):
    content.insert(0, f"#region {region_name}")
    content.append(f"#endregion {region_name}")


def prepare_license_header(content_of_copyright_header_file, line_comment_symbol, cs_region_name=None):
    header = [line_comment_symbol + ' ' + line for line in content_of_copyright_header_file]

    if cs_region_name is not None:
        add_cs_region(header, cs_region_name)

    return header


def is_copyright_header(commented_block, license_header_unique_identifiers):
    for identifier in license_header_unique_identifiers:
        if identifier not in str(commented_block):
            return False
    return True


def find_first(content, predicate):
    return next((index for index, x in enumerate(content) if predicate(x)), None)


def find_where_first_comment_block_starts(file_content, line_comment_symbols):
    return find_first(file_content,
                      lambda line: line.startswith(tuple(line_comment_symbols)) and not line.startswith('#!'))


def find_where_comment_block_ends(file_content, comment_start_index, line_comment_symbols):
    end_index = find_first(file_content[comment_start_index:],
                           lambda line: not line.startswith(tuple(line_comment_symbols)))
    return end_index + comment_start_index if end_index is not None else None


def find_where_first_comment_block_starts_and_ends(file_content, line_comment_symbol):
    comment_symbols = [line_comment_symbol, '#region ', '#endregion']

    start_index = find_where_first_comment_block_starts(file_content, comment_symbols)

    if start_index is None:
        # the file doesn't contain any comment block
        return None, None

    end_index = find_where_comment_block_ends(file_content, start_index, comment_symbols)

    if end_index is None:
        # the comment block goes to the end of the file
        return start_index, len(file_content)

    # the comment block is in the beginning or middle of the file
    return start_index, end_index


def find_license_header(file_content, line_comment_symbol, license_header_unique_identifiers):
    start_index, end_index = find_where_first_comment_block_starts_and_ends(file_content,
                                                                            line_comment_symbol)
    if start_index is None:
        # file doesn't contain any copyright header
        return None, None

    if is_copyright_header(file_content[start_index:end_index], license_header_unique_identifiers):
        return start_index, end_index

    # file contains the first comment block, but this block is not a copyright header
    return None, None


def add_header(header, content):
    # if the content is a script file we insert the header after the first line
    if content and content[0].startswith('#!'):
        header[0] = '\n' + header[0]
        if len(content) > 1 and content[1] != '':
            header[-1] += '\n'
        return content[0:1] + header + content[1:]

    if content and content[0] != '':
        header[-1] += '\n'
    return header + content


def replace_header(new_header, content, current_header_start_index, current_header_end_index):
    if current_header_start_index != 0 and content[current_header_start_index - 1] != '':
        new_header[0] = '\n' + new_header[0]
    if current_header_end_index != len(content) and content[current_header_end_index] != '':
        new_header[-1] += '\n'
    return content[0:current_header_start_index] + new_header + content[current_header_end_index:]


def write_to_file_if_content_is_different(file_full_name, file_content, new_content):
    if file_content != new_content:
        Path(file_full_name).write_text('\n'.join(new_content) + '\n')


def add_license_header(file_full_name,
                       license_file_full_name,
                       line_comment_symbol,
                       license_header_unique_identifiers,
                       cs_region_name,
                       replace_existing_license_header):
    file_content = Path(file_full_name).read_text().splitlines()
    license_file_content = Path(license_file_full_name).read_text().splitlines()

    header_start_index, header_end_index = find_license_header(file_content, line_comment_symbol,
                                                               license_header_unique_identifiers)
    new_license_header = prepare_license_header(license_file_content, line_comment_symbol, cs_region_name)

    if header_start_index is None:
        new_content = add_header(new_license_header, file_content)
        write_to_file_if_content_is_different(file_full_name, file_content, new_content)

    if header_start_index is not None and replace_existing_license_header:
        new_content = replace_header(new_license_header, file_content, header_start_index, header_end_index)
        write_to_file_if_content_is_different(file_full_name, file_content, new_content)


def is_valid_file(parser, arg):
    if not isfile(arg):
        parser.error(f"The file '{arg}' doesn't exist")
    return arg


def parse_command_line_arguments(command_line_args):
    parser = ArgumentParser(description='A script to add a license header to a source file.\n'
                                        'Version = 0.0-dev~commithash',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('--file-name',
                        help='full name of a source file',
                        required=True,
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--license-file-name',
                        help='full name of a file which contains a content of a license header',
                        required=True,
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--line-comment-symbol',
                        help='what line comment symbol is used for a license header',
                        required=True)
    parser.add_argument('--license-header-unique-identifiers',
                        help='the substrigs which are used to distinguish a regular comment block from a license '
                             'header. For a comment block to be considered a license header, all these substrings '
                             'must be present. Regular expressions or wildcards are not supported',
                        nargs='+',
                        required=True)
    parser.add_argument('--cs-region-name',
                        help='wrap a license header inside a C# region with the specified name',
                        required=False)
    parser.add_argument('--replace-existing-license-header',
                        help='if a file already contains a license header, replace it with a new one. '
                             'In case a file already contains a proper license header, it will not be touched.',
                        required=False, action='store_true')
    return parser.parse_args(command_line_args)


def add_license_header_command_line(command_line_args):
    args = parse_command_line_arguments(command_line_args)

    add_license_header(
        file_full_name=args.file_name,
        license_file_full_name=args.license_file_name,
        line_comment_symbol=args.line_comment_symbol,
        license_header_unique_identifiers=args.license_header_unique_identifiers,
        cs_region_name=args.cs_region_name,
        replace_existing_license_header=args.replace_existing_license_header)


if __name__ == "__main__":
    add_license_header_command_line(argv[1:])
