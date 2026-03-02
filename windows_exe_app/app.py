import os
from pathlib import Path

import gradio as gr
import torch
import whisper
from whisper.utils import get_writer

MODELS = ["tiny", "base", "small", "medium", "large", "turbo"]
COMMON_LANGUAGES = [
    "Auto", "pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh", "ru"
]

_loaded_models = {}


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_model_cached(model_name: str):
    cache_key = f"{model_name}-{get_device()}"
    if cache_key not in _loaded_models:
        _loaded_models[cache_key] = whisper.load_model(model_name, device=get_device())
    return _loaded_models[cache_key]


def transcribe_file(audio_path, model_name, language, task, temperature):
    if not audio_path:
        raise gr.Error("Selecione um arquivo de áudio ou vídeo antes de transcrever.")

    language = None if language == "Auto" else language
    model = load_model_cached(model_name)

    result = model.transcribe(
        audio_path,
        language=language,
        task=task,
        temperature=float(temperature),
        fp16=torch.cuda.is_available(),
        verbose=False,
    )

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    basename = Path(audio_path).stem
    txt_path = output_dir / f"{basename}.txt"
    txt_path.write_text(result["text"].strip() + "\n", encoding="utf-8")

    writer_srt = get_writer("srt", str(output_dir))
    writer_vtt = get_writer("vtt", str(output_dir))
    writer_srt(result, basename)
    writer_vtt(result, basename)

    srt_path = output_dir / f"{basename}.srt"
    vtt_path = output_dir / f"{basename}.vtt"

    status = (
        "✅ Transcrição concluída\n"
        f"- Dispositivo: {get_device()}\n"
        f"- Modelo: {model_name}\n"
        f"- Idioma detectado: {result.get('language', 'n/d')}\n"
        f"- Segmentos: {len(result.get('segments', []))}"
    )

    return result["text"].strip(), str(txt_path), str(srt_path), str(vtt_path), status


def build_interface():
    with gr.Blocks(title="Whisper Local EXE") as demo:
        gr.Markdown("## 🎙️ Whisper Local - App executável no Windows")
        gr.Markdown(
            "Selecione um arquivo de áudio/vídeo, escolha o modelo e clique em **Transcrever**."
        )

        with gr.Row():
            audio_input = gr.File(label="Arquivo de áudio/vídeo", type="filepath")
            model_name = gr.Dropdown(MODELS, value="turbo", label="Modelo")

        with gr.Row():
            language = gr.Dropdown(COMMON_LANGUAGES, value="Auto", label="Idioma")
            task = gr.Dropdown(["transcribe", "translate"], value="transcribe", label="Tarefa")
            temperature = gr.Slider(0.0, 1.0, value=0.0, step=0.1, label="Temperatura")

        run_button = gr.Button("Transcrever", variant="primary")

        transcript = gr.Textbox(label="Texto transcrito", lines=12)
        txt_file = gr.File(label="Baixar TXT")
        srt_file = gr.File(label="Baixar SRT")
        vtt_file = gr.File(label="Baixar VTT")
        status = gr.Textbox(label="Status", lines=6)

        run_button.click(
            fn=transcribe_file,
            inputs=[audio_input, model_name, language, task, temperature],
            outputs=[transcript, txt_file, srt_file, vtt_file, status],
        )

    return demo


if __name__ == "__main__":
    server_port = int(os.environ.get("WHISPER_APP_PORT", "7860"))
    app = build_interface()
    app.launch(server_name="127.0.0.1", server_port=server_port, inbrowser=True)
