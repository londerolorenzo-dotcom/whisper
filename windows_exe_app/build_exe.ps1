param(
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/5] Criando ambiente virtual (.venv)..."
& $PythonExe -m venv .venv

Write-Host "[2/5] Ativando ambiente virtual..."
.\.venv\Scripts\Activate.ps1

Write-Host "[3/5] Atualizando pip..."
python -m pip install --upgrade pip

Write-Host "[4/5] Instalando PyTorch CUDA e dependências do app..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install -r .\requirements-windows-exe.txt

Write-Host "[5/5] Gerando EXE com PyInstaller..."
pyinstaller --noconfirm --clean --onefile --name WhisperLocal .\app.py

Write-Host "Concluído! EXE em: .\dist\WhisperLocal.exe"
