# TashTech programming checks

Student-facing correctness checks for course exercises. Complete solutions are not included.

## Coffee machine

In CS50 IDE, save your program as `coffee_machine.c`. From the same folder, run:

```sh
check50 --local khajiev13/tashtech-checks/main/coffee
```

`--local` runs the checks inside your IDE. The command fetches the public checks from this repository.

- `:)` means a check passed.
- `:(` means a check failed; read its message, fix your code, save and run again.
- `:|` means a check could not run because an earlier check failed.

Use the supplied type and function names. Restore the initial stock to `{500, 200, 40, 3}` before checking. The required Espresso and Latte recipes must stay unchanged. Extra coffees and optional order summaries are allowed; optional extensions are not graded by this suite.

The tests check the three required functions and the repeated-order behaviour. Submit only your completed `coffee_machine.c` to LMS as instructed there; this command does not submit your homework. No manual test table or check50 report is required.

This is a TashTech course exercise using the open-source [check50](https://cs50.readthedocs.io/projects/check50/en/latest/) tool, not an official CS50 problem set.
