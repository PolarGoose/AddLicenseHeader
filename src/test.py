from os import remove
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase, main

from add_license_header import add_license_header_command_line


def create_temp_file_with_content(content):
    with NamedTemporaryFile(mode='w+t', delete=False) as file:
        file.write('\n'.join(content))
    return file.name


def execute(file_content, license_file_content, line_comment_symbol, license_header_unique_identifiers,
            cs_region_name, replace_existing_license_header):
    file = create_temp_file_with_content(file_content)
    license_file = create_temp_file_with_content(license_file_content)

    args = ['--file-name', file,
            '--license-file-name', license_file,
            '--line-comment-symbol', line_comment_symbol]
    if cs_region_name is not None:
        args += ['--cs-region-name', cs_region_name]
    if replace_existing_license_header:
        args.append('--replace-existing-license-header')
    args += ['--license-header-unique-identifiers'] + license_header_unique_identifiers

    try:
        add_license_header_command_line(args)
        return Path(file).read_text().splitlines()
    finally:
        remove(file)
        remove(license_file)


class Test(TestCase):
    def test_add_header_to_empty_file(self):
        output = execute(
            file_content=[],
            license_file_content=['1', '2'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C', '(c)'],
            cs_region_name=None,
            replace_existing_license_header=False)
        self.assertEqual(['// 1', '// 2'], output)

    def test_add_header_with_region_with_no_name_to_empty_file(self):
        output = execute(
            file_content=[],
            license_file_content=['1', '2'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name="header",
            replace_existing_license_header=False)
        self.assertEqual(['#region header', '// 1', '// 2', '#endregion header'], output)

    def test_add_header_with_region_to_empty_file(self):
        output = execute(
            file_content=[],
            license_file_content=['1', '2'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name="name",
            replace_existing_license_header=False)
        self.assertEqual(['#region name', '// 1', '// 2', '#endregion name'], output)

    def test_add_header(self):
        output = execute(
            file_content=['content'],
            license_file_content=['1', '2'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=False)
        self.assertEqual(['// 1', '// 2', '', 'content'], output)

    def test_update_header_in_file_consisting_only_of_license_header(self):
        output = execute(
            file_content=['// 1', '// C 2', '// 3'],
            license_file_content=['1', '2'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['// 1', '// 2'], output)

    def test_update_header_in_file(self):
        output = execute(
            file_content=['// 1', '// C 2', '// 3', '4'],
            license_file_content=['1', '2'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['// 1', '// 2', '', '4'], output)

    def test_update_header_in_file_with_new_line_separating_license_header_and_content(self):
        output = execute(
            file_content=['// 1', '// C 2', '// 3', '', '4'],
            license_file_content=['1', '2'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['// 1', '// 2', '', '4'], output)

    def test_add_header_in_file_which_starts_with_comment_block(self):
        output = execute(
            file_content=['// 3', '// 4', '5'],
            license_file_content=['1', '2'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['// 1', '// 2', '', '// 3', '// 4', '5'], output)

    def test_add_header_to_script_file(self):
        output = execute(
            file_content=['#!bb', '// 1', '2'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4', '', '// 1', '2'], output)

    def test_add_header_to_script_file_with_empty_line_after_the_first_line(self):
        output = execute(
            file_content=['#!bb', '', '// 1', '2'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4', '', '// 1', '2'], output)

    def test_add_header_to_script_file_with_only_one_line(self):
        output = execute(
            file_content=['#!bb'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4'], output)

    def test_add_header_to_script_file_with_only_two_lines(self):
        output = execute(
            file_content=['#!bb', '1'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4', '', '1'], output)

    def test_update_header_in_script_file(self):
        output = execute(
            file_content=['#!bb', '// C'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4'], output)

    def test_update_header_in_script_file_with_content(self):
        output = execute(
            file_content=['#!bb', '', '// C', '', '1', '2'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4', '', '1', '2'], output)

    def test_update_header_in_script_file_without_content(self):
        output = execute(
            file_content=['#!bb', '', '// C'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4'], output)

    def test_update_header_in_script_file_without_content_2(self):
        output = execute(
            file_content=['#!bb', '// C', '// 1'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4'], output)

    def test_update_header_in_script_file_without_content_3(self):
        output = execute(
            file_content=['#!bb', '// C'],
            license_file_content=['3', '4'],
            line_comment_symbol='//',
            license_header_unique_identifiers=['C'],
            cs_region_name=None,
            replace_existing_license_header=True)
        self.assertEqual(['#!bb', '', '// 3', '// 4'], output)


if __name__ == '__main__':
    main()
