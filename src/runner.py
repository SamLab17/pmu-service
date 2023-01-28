import re
import subprocess
from pathlib import Path
from time import sleep
import fileinput
from dataclasses import dataclass
from typing import Union

BASE_IMAGE = Path("images/debian.qcow2")
OUTPUT_FILE_DIR = Path("output_files")

@dataclass
class RunRequest():
    id: str
    file: Path

@dataclass 
class RunResult():
    error: bool
    err_msg: str
    output_file: Union[Path, None]

def strip_ansi(file: Path) -> str:
    """Strip ANSI color codes from output. From https://superuser.com/a/380778"""
    subprocess.check_call([
        "sed",
        "-i",
        r"s/\x1b\[[\?0-9;]*[mhl]//g",
        str(file.absolute())
    ])

def trim_boot(file: Path):
    """Trim boot info from beginning of file"""
    found_login = False
    keep_newline = False
    for line in fileinput.input(file, inplace=True):
        assert '\r' not in line
        if found_login:
            empty = (line == "\n")
            if empty:
                if keep_newline:
                    print(line, end='')
                else:
                    keep_newline = True
            else:
                print(line, end='')
                keep_newline = False
        else:
            found_login = "login" in line


def make_snapshot_disk(base_image: Path) -> Path:
    SNAPSHOT_IMAGE = "guest.qcow2"
    subprocess.check_call([
        "qemu-img",
        "create",
        "-f", "qcow2",
        "-b", f"{base_image.absolute()}",
        SNAPSHOT_IMAGE
    ])
    ret = Path(SNAPSHOT_IMAGE)
    assert(ret.exists())
    return ret


def copy_file_to_disk(disk: Path, file: Path, disk_path: str):
    try:
        subprocess.check_call([
                "scripts/copy_to_guest.sh",
                str(disk.absolute()),
                str(file.absolute()),
                disk_path
            ],
        )
    finally:
        subprocess.check_call([
            "scripts/unmount.sh"
        ])
        sleep(1)


def remove_file_from_disk(disk: Path, disk_path: str):
    try:
        subprocess.check_call([
                "scripts/remove_guest_file.sh",
                str(disk.absolute()),
                disk_path
            ],
        )
    finally:
        subprocess.check_call([
            "scripts/unmount.sh"
        ])
        sleep(1)



def run_program_on_guest(run_id: str, disk: Path, guest_path: str, timeout: int = 60) -> Path:
    outfile_path = OUTPUT_FILE_DIR / Path(f"output-{run_id}.txt")
    outfile = open(outfile_path, 'w')

    subprocess.run([
            "expect",
            "scripts/run_program.sh",
            str(disk.absolute()),
            guest_path,
            str(timeout)
        ],
        stdout=outfile,
        stderr=outfile,
        # Shouldn't take more than ~5 seconds to boot the VM
        timeout=timeout + 5
    )
    outfile.close()

    trim_boot(outfile_path)
    strip_ansi(outfile_path)
    return outfile_path

def run(req: RunRequest):
    print("run!")
    test_program = req.file
    guest_path = f"/root/{test_program.name}"
    try:
        copy_file_to_disk(BASE_IMAGE, test_program, guest_path)
        output = run_program_on_guest(req.id, BASE_IMAGE, guest_path)
        return RunResult(False, "", output)
        # Send output
    except Exception as e:
        # Send some kind of error message
        return RunResult(True, str(e), None)
    finally:
        remove_file_from_disk(BASE_IMAGE, guest_path)

def init():
    # Make output file directory
    subprocess.check_call(["mkdir", "-p", str(OUTPUT_FILE_DIR.absolute())])
    # Check for debian image?
    if not BASE_IMAGE.exists():
        print(f"Did not find {BASE_IMAGE.name} at {BASE_IMAGE}")
        print(f"Downloading an image...")
        DEBIAN_IMAGE_URL = "https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-generic-amd64.qcow2"
        subprocess.check_call([
            "wget",
            "-O",
            str(BASE_IMAGE.absolute()),
            DEBIAN_IMAGE_URL
        ])
        assert BASE_IMAGE.exists()

def main() -> int:

    test_program = Path("scripts/test_program")
    guest_path = "/root/test_program"

    copy_file_to_disk(BASE_IMAGE, test_program, guest_path)

    print(f"Running {test_program} in VM...")
    output = run_program_on_guest('main', BASE_IMAGE, guest_path)

    for line in open(output, 'r'):
        print(line, end='')

    raise(SystemExit(0))

if __name__ == '__main__':
    main()