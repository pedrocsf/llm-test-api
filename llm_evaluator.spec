from PyInstaller.utils.hooks import collect_data_files, collect_submodules

APP_NAME = "LlmEvaluator"

analysis = Analysis(
    ["main.py"],
    pathex=["."],
    datas=[("models", "models")] + collect_data_files("fastembed"),
    hiddenimports=collect_submodules("sacrebleu"),
    excludes=["tkinter", "pytest"],
)
archive = PYZ(analysis.pure)
executable = EXE(
    archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    console=False,
)
collection = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    name=APP_NAME,
)
