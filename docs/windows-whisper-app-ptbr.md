# Guia (Windows) — App local para transcrição com Whisper

Este guia explica como rodar um app simples com interface gráfica para transcrever áudios localmente.

## 1) Pré-requisitos

1. **Python 3.10+** instalado.
2. **FFmpeg** instalado e no `PATH`.
3. **Drivers NVIDIA atualizados** (para usar sua GPU RTX 5070 Ti).

## 2) Criar ambiente virtual

No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3) Instalar dependências

> Para GPU NVIDIA, instale PyTorch com CUDA conforme instruções oficiais do PyTorch.

Depois:

```powershell
pip install -U openai-whisper
```

Se necessário, instale também:

```powershell
pip install torch torchvision torchaudio
```

## 4) Rodar o app

```powershell
python apps/whisper_windows_app.py
```

## 5) Como usar

1. Clique em **Browse** e selecione o arquivo de áudio.
2. Escolha a pasta de saída.
3. Escolha o modelo (`turbo` é um bom padrão para começar).
4. Idioma:
   - `auto` para detectar automaticamente.
   - `pt` para português.
5. Task:
   - `transcribe` para transcrever.
   - `translate` para traduzir para inglês (não use `turbo` para isso).
6. Clique em **Start transcription**.

A transcrição será mostrada na tela e salva em um `.txt` na pasta escolhida.

## 6) Dicas de desempenho para sua RTX 5070 Ti

- Comece com **`turbo`** (rápido).
- Para máxima qualidade, teste `medium` ou `large`.
- Se der erro de memória GPU, use um modelo menor (`small` ou `base`).
