#!/usr/bin/env python3
"""
RedCodeJudge CLI
Official automated testing tool for the RedCodeNinja Team.
"""

import subprocess
import sys
import difflib
import time
import shutil
import argparse
import os
from pathlib import Path
from datetime import datetime

# ==============================================================================
#  CONFIGURATION
# ==============================================================================

PROJECT = "RedCodeJudge"
VERSION = "0.4.0"
AUTHOR  = "RedCodeNinja Team"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
#  UI 
# ==============================================================================

class Colors:
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    PURPLE  = '\033[95m'
    CYAN    = '\033[96m'
    GREY    = '\033[90m'
    ORANGE  = '\033[38;5;208m'
    
    BOLD    = '\033[1m'
    
    RESET   = '\033[0m'

class Icons:
    SUCCESS     = '🟢'
    FAIL        = '🔴'
    OUCH        = '🤡'

    AC          = '✅'
    WA          = '⛔'
    TLE         = '🐌'
    RTE         = '💣'
    UNK         = '👽'

    INPUT       = '📥'
    OUTPUT      = '🎯'
    RESULT      = '💬'

    BUILD       = '🔨'
    RUN         = '🚀'

    STEP        = '⚙️ '

    SCORE       = '🏆'
    ACCURACY    = '🎯'

    BALLON      = '🎈' 

class Status:
    AC = {
        'title': 'Accepted',
        'description': 'File match exactly',
        'acronym': 'AC',
        'icon': Icons.AC,
        'color': Colors.GREEN
    }

    WA = {
        'title': 'Wrong Answer',
        'description': 'File mismatch',
        'acronym': 'WA',
        'icon': Icons.WA,
        'color': Colors.RED
    }

    TLE = {
        'title': 'Time Limit Exceeded',
        'description': 'Execution timed out',
        'acronym': 'TLE',
        'icon': Icons.TLE,
        'color': Colors.YELLOW 
    }

    RTE = {
        'title': 'Runtime Error',
        'description': 'Process crashed (non-zero exit code)',
        'acronym': 'RTE',
        'icon': Icons.RTE,
        'color': Colors.PURPLE 
    }

    UNK = {
        'title': 'Unknown',
        'description': 'State not recognized',
        'acronym': 'UNK',
        'icon': Icons.UNK,
        'color': Colors.GREY
    }

class UI:
    @staticmethod
    def welcome():
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"{Colors.RED}")
        print(r"""
 ____           _  ____          _            _           _  
|  _ \ ___   __| |/ ___|___   __| | ___      | |_   _  __| | __ _  ___ 
| |_) / _ \ / _` | |   / _ \ / _` |/ _ \  _  | | | | |/ _` |/ _` |/ _ \
|  _ <  __/| (_| | |__| (_) | (_| |  __/ | |_| | |_| | (_| | (_| |  __/
|_| \_\___| \__,_|\____\___/ \__,_|\___|  \___/ \__,_|\__,_|\__, |\___|
                                                             |___/      CLI
        """)
        print(f"{Colors.RESET}{Colors.BOLD}{PROJECT} v{VERSION}{Colors.RESET} | {Colors.GREY}Powered by {AUTHOR} {Icons.BALLON}{Colors.RESET}")
        print(f"{Colors.GREY}System Time: {now}{Colors.RESET}")

    @staticmethod
    def section(title, icon=Icons.RUN):
        print(f"")
        print(f"{Colors.PURPLE}" + "="*65)
        print(f"{icon}  {Colors.BOLD}{title.upper()}{Colors.RESET}")
        print(f"{Colors.PURPLE}" + "="*65 + f"{Colors.RESET}")
        print(f"")

    @staticmethod
    def message(text, icon, color, comment="", err=None):
        print(f"   {icon} {color}{text:<25}{Colors.RESET} {comment}")

        if err:
            print(f"{Colors.GREY}{err.stderr.decode('utf-8', errors='replace')}{Colors.RESET}")

    @staticmethod
    def testcase(name, status=Status.UNK, input="", output="", result="", comment="", verbose=False, err=None):
        def diff(expected, current):
            content = list(difflib.unified_diff(expected, current, n=1, lineterm=''))
        
            if not content: 
                return
            
            print(f"      {Colors.GREY}┌─ Quick Diff ────────{Colors.RESET}")
            for line in content: 
                if line.startswith(('---', '+++', '@@')): 
                    continue
                
                color = Colors.GREEN if line.startswith('+') else (Colors.RED if line.startswith('-') else Colors.GREY)

                print(f"      {Colors.GREY}│{Colors.RESET} {color}{line}{Colors.RESET}")
            print(f"      {Colors.GREY}└─────────────────────{Colors.RESET}")
        
        def inline():
            UI.message(f"{name:<15} {status['acronym']}", status['icon'], status['color'], f"| {comment}", err)

            if status == Status.WA:
                expected = normalize(output)
                current = normalize(result)
                
                diff(expected, current)

        def block():
            def truncate(txt, lines=25):
                line = txt.strip().splitlines()

                if not line: 
                    return ["(empty)"]
                
                if len(line) > lines:
                    return line[:lines] + [f"{Colors.YELLOW}... ({len(line)-lines} hidden lines){Colors.RESET}"]
                
                return line

            print(f"")
            print(f"   {status['color']}┌── Case: {Colors.BOLD}{name} ─ {status['icon']} {status['title']} ({comment}){Colors.RESET}")
            
            print(f"   {status['color']}│{Colors.RESET}")
            print(f"   {status['color']}│{Colors.RESET} {Colors.GREY}Note: {status['description']}.{Colors.RESET}")
            print(f"   {status['color']}│{Colors.RESET}")

            print(f"   {status['color']}│{Colors.RESET} {Colors.BLUE}{Icons.INPUT} INPUT:{Colors.RESET}")
            for line in truncate(input): print(f"   {status['color']}│{Colors.RESET}    {line}")
            
            print(f"   {status['color']}│{Colors.RESET} {Colors.BLUE}{Icons.OUTPUT} OUTPUT:{Colors.RESET}")
            for line in truncate(output): print(f"   {status['color']}│{Colors.RESET}    {line}")

            print(f"   {status['color']}│{Colors.RESET} {status['color']}{Icons.RESULT} RESULT:                   (Test Result){Colors.RESET}")
            for line in truncate(result): print(f"   {status['color']}│{Colors.RESET}    {line}")

            print(f"   {status['color']}└────────────────────────────────────────────────────{Colors.RESET}")

            if err:
                print(f"{Colors.RESET}{Colors.GREY}{err.stderr.decode('utf-8', errors='replace')}{Colors.RESET}")

        block() if verbose else inline()

    @staticmethod
    def summary(n, stats):
        accuracy = (stats['AC']/n)*100 if n > 0 else 0
        
    
        note = f"(File match exactly! {Icons.BALLON})" if stats['AC'] == n and n > 0 else f""

        print(f"")
        print(f"="*65)
        print(f"")
        print(f"   {Icons.SCORE} {Colors.BOLD}FINAL SCORE:{Colors.RESET}")
        print(f"   AC: {Colors.GREEN}{stats['AC']}{Colors.RESET}  |  WA: {Colors.RED}{stats['WA']}{Colors.RESET}  |  TLE: {Colors.YELLOW}{stats['TLE']}{Colors.RESET}  |  RTE: {Colors.PURPLE}{stats['RTE']}{Colors.RESET}")
        print(f"")
        print(f"   {Icons.ACCURACY} Accuracy: {accuracy:.1f}% {note}{Colors.RESET}")
        print(f"")
        print(f"="*65)
        print(f"")

# ==============================================================================
#  CORE
# ==============================================================================

COMMANDS = {
    'python': {
        'compile': None, 
        'run': ['python3', '{src}']
        },
    
    'c': {
        'compile': ['gcc', '{src}', '-o', '{exe}', '-O2'], 
        'run': ['{exe}']
        },
    
    'cpp': {
        'compile': ['g++', '{src}', '-o', '{exe}', '-O2', '-std=c++17'], 
        'run': ['{exe}']
        },
    
    'java': {
        'compile': ['javac', '{src}', '-d', '{dir}'], 
        'run': ['java', '-cp', '{dir}', '{filename_no_ext}']}
}

TIMEOUT = 10.000

def extract(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except: 
        return ""

def normalize(text):
    return [line.rstrip() for line in text.strip().splitlines()]

def compile(lang, source, work_dir):
    UI.section("Step #1: Building", Icons.BUILD)
    
    config = COMMANDS.get(lang)
    
    if not config: 
        sys.exit(f"{Colors.RED}Language '{lang}' not supported.{Colors.RESET}")
    
    exe = work_dir / (source.stem + (".exe" if sys.platform=="win32" and lang in ['c','cpp'] else ""))

    if config['compile']:
        start = time.time()
        cmd = [arg.format(src=str(source), exe=str(exe), dir=str(work_dir)) for arg in config['compile']]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            UI.message(f"Build Success ({time.time() - start:.2f}s)", Icons.SUCCESS, Colors.GREEN)
        except subprocess.CalledProcessError as err:
            UI.message(f"Build Failed", Icons.FAIL, Colors.RED, f"(Exit {err.returncode})", err)
            return None
    else:
        UI.message(f"Skiping build step...", Icons.STEP, Colors.GREY)

    return [arg.format(src=str(source), exe=str(exe), dir=str(work_dir), filename_no_ext=source.stem) for arg in config['run']]

def run(command, input_dir, output_dir, work_dir, verbose=False):
    UI.section(f"Step #2: Running", Icons.RUN)

    input_files = sorted([f for f in (input_dir).glob('*') if f.is_file()])

    if not input_files:
        sys.exit(f"{Colors.RED}No input files found in directory '{input_dir}'.{Colors.RESET}")

    result_dir = work_dir / "output"
    result_dir.mkdir(parents=True, exist_ok=True)

    stats = {'AC': 0, 'WA': 0, 'TLE': 0, 'RTE': 0}

    for input_file in input_files:
        case = input_file.stem
        
        output_file = next(output_dir.glob(f"{case}.*"), output_dir / f"{case}.out")
        
        if not output_file.exists():
            UI.testcase(input_file.name, Status.UNK, extract(input_file), "", "", f"Missing expected output file (Skipping)", verbose, None)
            continue

        input_content = extract(input_file)
        output_content = extract(output_file)
        result_content = ""
        
        status = Status.UNK

        duration = 0.0
        err = None

        try:
            start = time.time()
            with open(input_file, 'r') as fi:
                proc = subprocess.run(command, stdin=fi, capture_output=True, timeout=TIMEOUT, check=True)
            duration = time.time() - start
            
            result_content = proc.stdout.decode('utf-8', errors='replace') 

            # Salva o que foi gerado pelo código
            with open(result_dir / f"{case}.out", 'w', encoding='utf-8') as fo:
                fo.write(result_content)

            output_normalized = normalize(output_content)
            result_normalized = normalize(result_content)

            if result_normalized == output_normalized:
                status = Status.AC
                stats['AC'] += 1
            else:
                status = Status.WA
                stats['WA'] += 1

        except subprocess.TimeoutExpired:
            status = Status.TLE
            stats['TLE'] += 1
            duration = TIMEOUT
            
        except subprocess.CalledProcessError as e:
            status = Status.RTE
            stats['RTE'] += 1
            err = e

        UI.testcase(input_file.name, status, input_content, output_content, result_content, f"{duration:.3f}s", verbose, err)
  
    UI.summary(len(input_files), stats)

# ==============================================================================
#  MAIN
# ==============================================================================

def main():
    desc = f"""
{PROJECT} v{VERSION}
------------------------------------------------------------
Official Local Judge for Competitive Programming.
Executes code against input files and compares with solutions.
    
Usage:
  python redcode_judge.py B.cpp --lang cpp --input ./contest/B/in --output ./contest/B/out
  python redcode_judge.py A.py  --lang python --input ./in --output ./out --work_dir ./my_results
    """
    
    parser = argparse.ArgumentParser(
        prog="RedCodeJudge",
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('file', help='Source code file path')
    parser.add_argument('--lang', choices=['c', 'cpp', 'java', 'python'], required=True, help='Programming language')
    
    parser.add_argument('-i','--input-dir', required=True, help='Directory containing input files (.in)')
    parser.add_argument('-o','--output-dir', required=True, help='Directory containing expected output files (.sol, .out)')
    parser.add_argument('-w','--work-dir', required=False, help='Directory for build artifacts and test results (Optional)')
    
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed I/O for debugging')
    
    UI.welcome()
    
    args = parser.parse_args()
    
    source = Path(args.file).resolve()
    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    
    if not source.exists(): 
        sys.exit(f"{Colors.RED}Source file '{source}' not found.{Colors.RESET}")

    if not input_dir.exists(): 
        sys.exit(f"{Colors.RED}Input directory '{input_dir}' not found.{Colors.RESET}")

    if not output_dir.exists(): 
        sys.exit(f"{Colors.RED}Output (Solution) directory '{output_dir}' not found.{Colors.RESET}")

    if args.work_dir:
        work_dir = Path(args.work_dir).resolve()
    else:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        work_dir = Path(f".redcodejudge-{timestamp}-{source.stem}").resolve()
    
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        command = compile(args.lang, source, work_dir)

        if command:
            run(command, input_dir, output_dir, work_dir, args.verbose)
    finally:
        pass

if __name__ == "__main__":
    main()