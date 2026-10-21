"""Public feedback for the three required Coffee Machine functions."""

import re
import resource
import signal
import subprocess
import tempfile

import check50


INVALID = "Invalid choice. Choose a listed coffee ID or 0."
OUTPUT_LIMIT = 262144


def compile_source(source, executable):
    # A healthy compiler can take several seconds when a Codespace starts.
    process = check50.run(f"clang {source} -o {executable} -std=c11 -ggdb -lm -lcs50")
    try:
        output = process.stdout(timeout=30)
    finally:
        process.kill()
    if process.exitcode != 0:
        lines = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", output).splitlines()
        if len(lines) > 50:
            lines = lines[:25] + lines[-25:]
        for line in lines:
            check50.log(line)
        raise check50.Failure(f"{source} failed to compile",
                              help="Read the compiler messages above; keep the supplied function names and parameters.")


def limit_output():
    # Set only in the child program; an accidental printing loop stays bounded.
    resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_LIMIT, OUTPUT_LIMIT))


def run_program(arguments, input_text="", hint="Check the loop and its exit condition."):
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            result = subprocess.run(arguments, input=input_text, text=True, stdout=stdout, stderr=stderr,
                                    timeout=3, preexec_fn=limit_output)
        except subprocess.TimeoutExpired:
            raise check50.Failure("program did not finish within 3 seconds", help=hint)
        stdout.seek(0)
        stderr.seek(0)
        output = stdout.read(OUTPUT_LIMIT).decode("utf-8", errors="replace")
        errors = stderr.read(OUTPUT_LIMIT).decode("utf-8", errors="replace")
    if result.returncode == -signal.SIGXFSZ or len(output) >= OUTPUT_LIMIT or len(errors) >= OUTPUT_LIMIT:
        raise check50.Failure("program produced too much output; check for an endless loop", help=hint)
    if result.returncode != 0:
        raise check50.Failure(errors.strip()[:2000] or f"program exited with {result.returncode}", help=hint)
    return output


def fixture(name, hint):
    run_program(["./coffee_checks", name], hint=hint)


def reader(input_text, expected):
    output = run_program(["./coffee_checks", "read"], input_text,
                         "In read_coffee_choice, keep asking until 0 or a listed ID; keep the EOF check.")
    match = re.search(r"CHECK50_RETURN=(-?\d+)", output)
    actual = int(match.group(1)) if match else "no returned choice"
    if actual != expected:
        raise check50.Mismatch(str(expected), str(actual),
                               help="Validate inside read_coffee_choice, before returning the choice.")
    return output


def menu_ids():
    output = run_program(["./coffee_checks", "ids"])
    return [int(value) for value in re.findall(r"CHECK50_ID=(\d+)", output)]


@check50.check()
def exists():
    """coffee_machine.c exists"""
    check50.exists("coffee_machine.c")


@check50.check(exists, timeout=90)
def compiles():
    """coffee_machine.c and its three required functions compile"""
    compile_source("coffee_machine.c", "coffee_machine")
    check50.include("harness.c")
    compile_source("harness.c", "coffee_checks")


@check50.check(compiles)
def reader_valid():
    """read_coffee_choice accepts Exit and each listed coffee ID"""
    for choice in [0, *menu_ids()]:
        reader(f"{choice}\n", choice)
    reader("hello\n1\n", 1)


@check50.check(compiles)
def reader_invalid():
    """read_coffee_choice retries unlisted numbers with the required message"""
    ids = menu_ids()
    missing = next(value for value in range(1, len(ids) + 2) if value not in ids)
    output = reader(f"-1\n{missing}\n2\n", 2)
    if output.count(INVALID) != 2:
        raise check50.Failure("expected the invalid-choice message once for each unlisted number",
                              help=f'Print "{INVALID}" inside the validation loop.')


@check50.check(compiles)
def reader_eof():
    """read_coffee_choice returns Exit at end of input"""
    reader("", 0)


@check50.check(compiles)
def exact_stock():
    """exactly enough of all four supplies is allowed"""
    fixture("exact", "Use >= for every required amount; exactly enough is valid.")


@check50.check(compiles)
def espresso_without_milk():
    """Espresso can be made with zero milk"""
    fixture("no_milk", "Compare stock to this coffee's recipe; Espresso needs no milk.")


@check50.check(compiles)
def short_water():
    """orders are refused when only water is insufficient"""
    fixture("water", "All four comparisons must be true; check water with &&.")


@check50.check(compiles)
def short_milk():
    """orders are refused when only milk is insufficient"""
    fixture("milk", "All four comparisons must be true; check milk with &&.")


@check50.check(compiles)
def short_beans():
    """orders are refused when only beans are insufficient"""
    fixture("beans", "All four comparisons must be true; check beans with &&.")


@check50.check(compiles)
def short_cups():
    """orders are refused when only cups are insufficient"""
    fixture("cups", "All four comparisons must be true; check paper cups with &&.")


@check50.check(compiles)
def deducts_recipe():
    """stock_after_coffee subtracts all four recipe amounts"""
    fixture("deduct", "Subtract each needed amount from the matching stock field and return stock.")


@check50.check(compiles)
def refusal_unchanged():
    """a refused order returns all four stock amounts unchanged"""
    fixture("refusal", "Keep all four subtractions inside the can_make_coffee check.")


@check50.check(compiles)
def returned_copy():
    """the returned stock changes while the original copy stays unchanged"""
    fixture("copy", "Return the updated Stock copy. The caller must save the returned value.")


@check50.check(compiles)
def repeated_orders():
    """main saves stock across Espresso, Latte, Latte, then refusal"""
    output = run_program(["./coffee_machine"], "1\n2\n2\n1\n0\n",
                         "Save the returned stock in main and stop when the choice is 0.")
    pattern = (r"Stock\s*:\s*water\s*=\s*(-?\d+)\s*ml\s*,\s*"
               r"milk\s*=\s*(-?\d+)\s*ml\s*,\s*beans\s*=\s*(-?\d+)\s*g\s*,\s*"
               r"cups\s*=\s*(-?\d+)")
    actual = [tuple(map(int, values)) for values in re.findall(pattern, output)]
    expected = [(500, 200, 40, 3), (400, 200, 30, 2), (300, 150, 20, 1),
                (200, 100, 10, 0), (200, 100, 10, 0)]
    labels = ["Starting stock", "After Espresso", "After first Latte", "After second Latte", "After refusal"]
    hint = "Restore starting stock to {500, 200, 40, 3}; main must save stock_after_coffee's return."
    for label, want, got in zip(labels, expected, actual):
        if got != want:
            expected_text = "/".join(map(str, want))
            actual_text = "/".join(map(str, got))
            raise check50.Failure(f"{label}: expected {expected_text}; got {actual_text} (water/milk/beans/cups)", help=hint)
    if len(actual) != len(expected):
        raise check50.Failure(f"expected stock for 5 steps; found {len(actual)}", help=hint)
    made = re.findall(r"(Espresso|Latte)\s+ready\.", output)
    if made != ["Espresso", "Latte", "Latte"] or not re.search(r"Not\s+enough\s+supplies\.", output):
        raise check50.Failure("expected three successful drinks, then refusal because no cups remain",
                              help="Refused orders must not make a drink or deduct stock.")
