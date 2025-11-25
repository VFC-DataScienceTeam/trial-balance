import json
from pathlib import Path
from executor_dispatcher import ExecutorDispatcher

ROOT = Path(__file__).resolve().parents[2]
REG_PATH = ROOT / 'config' / 'report_registry.json'


def main():
    with open(REG_PATH, 'r', encoding='utf-8') as f:
        reg = json.load(f)

    reports = reg.get('reports', [])
    report = next((r for r in reports if r.get('id') == 'tb_text_upper'), None)
    if report is None:
        print('tb_text_upper not found in registry')
        return 2

    project_rel = report.get('path')
    params = report.get('parameters', {})
    input_path = params.get('input_path')
    output_path = params.get('output_path')

    ed = ExecutorDispatcher(ROOT)
    proj_path = ROOT / project_rel
    args = [str(input_path), str(output_path)] if output_path else [str(input_path)]

    print(f"Running dotnet project: {proj_path} with args: {args}")
    res = ed.run_dotnet_project(proj_path, args)
    print('returncode:', res.get('returncode'))
    print('ok:', res.get('ok'))
    print('stdout:\n', res.get('stdout'))
    print('stderr:\n', res.get('stderr'))

    # list outputs if created
    outdir = ROOT / (output_path or (Path(input_path) / 'out_upper'))
    print('expected outdir:', outdir)
    if outdir.exists():
        files = list(outdir.glob('**/*'))
        print('output files:')
        for f in files:
            print('-', f)
    else:
        print('No output directory created yet.')


if __name__ == '__main__':
    raise SystemExit(main())
