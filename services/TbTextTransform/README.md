# TbTextTransform

Simple .NET console app proof-of-concept for integrating external executables into the orchestrator.

Usage:

- Transform a single text file to uppercase:
  dotnet run --project services/TbTextTransform -- input.txt output.txt

- Transform all `.txt` files in a directory to uppercase (writes to `out_upper` by default):
  dotnet run --project services/TbTextTransform -- input_folder

Outputs:
- Writes files and prints `WROTE:<path>` lines to stdout for each file written.
- Returns exit code `0` on success, `1` on error, `2` for usage errors.
