# Whisper Local (.exe) para Windows

Este mini-projeto cria um programa local (executável `.exe`) para transcrever áudio/vídeo com Whisper usando GPU NVIDIA.

## Pré-requisitos

1. **Windows 10/11**
2. **Python 3.11** instalado e no PATH
3. **FFmpeg** instalado (recomendado via `winget install Gyan.FFmpeg`)
4. Driver NVIDIA atualizado

## Gerar o `.exe`

Abra o PowerShell na pasta `windows_exe_app` e execute:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build_exe.ps1
```

No fim, o executável estará em:

```text
dist\WhisperLocal.exe
```

## Executar

Dê duplo clique em `WhisperLocal.exe`.

O app abrirá no navegador em `http://127.0.0.1:7860`.

## Dicas de uso para RTX 5070 Ti

- Comece com o modelo `turbo` (melhor velocidade geral)
- Se quiser aumentar qualidade em áudios difíceis, teste `medium` ou `large`
- Para traduzir para inglês, prefira `medium`/`large` com tarefa `translate`

## Saídas

Após transcrever, o app gera na pasta `outputs`:

- `arquivo.txt` (texto simples)
- `arquivo.srt` (legendas)
- `arquivo.vtt` (legendas web)

## Solução de problemas

- Se aparecer erro de FFmpeg, confirme no terminal:
  ```powershell
  ffmpeg -version
  ```
- Se o PyTorch não usar GPU:
  ```powershell
  python -c "import torch; print(torch.cuda.is_available())"
  ```
  Deve retornar `True`.
