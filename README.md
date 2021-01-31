# AddLicenseHeader
A simple python script to add/update a license header in a source file.
The script can be used from command line or as a module for a Python script.<br>
Note: the script supports only single line comment symbols like `//`, `#`, e.t.c.

# System requirements
Python 3

# How to use
Download the latest [release](https://github.com/PolarGoose/AddLicenseHeader/releases/latest) and unpack it.
Look at the sections bellow to see how to use the script.

# Usage information
```
> python add_license_header.py --help
usage: add_license_header.py [-h] --file-name FILE_NAME --license-file-name LICENSE_FILE_NAME --line-comment-symbol LINE_COMMENT_SYMBOL --license-header-unique-identifiers LICENSE_HEADER_UNIQUE_IDENTIFIERS [LICENSE_HEADER_UNIQUE_IDENTIFIERS ...]
                             [--cs-region-name CS_REGION_NAME] [--replace-existing-license-header]

A script to add a license header to a source file.
Version = 0.0-dev~commithash

optional arguments:
  -h, --help            show this help message and exit
  --file-name FILE_NAME
                        full name of a source file
  --license-file-name LICENSE_FILE_NAME
                        full name of a file which contains a content of a license header
  --line-comment-symbol LINE_COMMENT_SYMBOL
                        what line comment symbol is used for a license header
  --license-header-unique-identifiers LICENSE_HEADER_UNIQUE_IDENTIFIERS [LICENSE_HEADER_UNIQUE_IDENTIFIERS ...]
                        the substrigs which are used to distinguish a regular comment block from a license header. For a comment block to be considered a license header, all these substrings must be present. Regular expressions or wildcards are not supported
  --cs-region-name CS_REGION_NAME
                        wrap a license header inside a C# region with the specified name
  --replace-existing-license-header
                        if a file already contains a license header, replace it with a new one. In case a file already contains a proper license header, it will not be touched.
```

# Example
Suppose we have source files `python_script.py` and `Programm.cs`:
```
#!/usr/bin/env python3

if __name__ == "__main__":
    print('Hello')
```
```
using System;

public class Program
{
	public static void Main()
	{
		Console.WriteLine("Hello World");
	}
}
```
We want to add the following license header `license.txt` inside them:
```
Copyright (c) 2021 PolarGoose
Permission is hereby granted, free of charge, to any person obtaining a copy
```
In order to do that, we need to run the following commands:
```
> python add_license_header.py ^
    --file-name "C:\MyRepo\Programm.cs" ^
    --license-file-name "C:\MyRepo\license.txt" ^
    --line-comment-symbol "//" ^
    --license-header-unique-identifiers "(c)" "Copyright" ^
    --cs-region-name "fileHeader"
```
```
> python add_license_header.py ^
    --file-name "C:\MyRepo\python_script.py" ^
    --license-file-name "C:\MyRepo\license.txt" ^
    --line-comment-symbol "#" ^
    --license-header-unique-identifiers "(c)" "Copyright"
```
After applying the commands the files will look like this:
```
#!/usr/bin/env python3

# Copyright (c) 2021 PolarGoose
# Permission is hereby granted, free of charge, to any person obtaining a copy

if __name__ == "__main__":
    print('Hello')
```
```
#region fileHeader
// Copyright (c) 2021 PolarGoose
// Permission is hereby granted, free of charge, to any person obtaining a copy
#endregion fileHeader

using System;

public class Program
{
	public static void Main()
	{
		Console.WriteLine("Hello World");
	}
}
```

# Example of using the script as a Python module
```
import os
import traceback
from glob import glob
from pathlib import Path

from add_license_header import add_license_header

root = os.path.dirname(os.path.realpath(__file__))
repo_dir = Path(os.path.join(root, '../MyRepo')).resolve()

cs_source_files = glob(f'{repo_dir}/**/*.cs', recursive=True)
license_file = os.path.join(root, 'License.txt')
for src_file in cs_source_files:
    try:
        add_license_header(
            file_full_name=src_file,
            license_file_full_name=license_file,
            line_comment_symbol="//",
            license_header_unique_identifiers=['(c)', 'Copyright'],
            cs_region_name="header",
            replace_existing_license_header=False)
    except Exception as ex:
        print(f"Failed to process a file: \n {src_file}")
        traceback.print_exc()
        print()
```
