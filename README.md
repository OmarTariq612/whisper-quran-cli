# whisper-quran-cli

## Requirements:

```bash
sudo apt install ffmpeg -y
```

```bash
pip3 install click \
  jiwer \
  openai-whisper \
  pydantic \
  mutagen \
  transformers \
  requests
```

```bash
python3 main.py --help
```

```
Usage: main.py [OPTIONS] {QuranComTranscriper|AyatTranscriper} METADATA_PATH
               AUDIO_PATH

  transcribe sorahs in the given range + the WER

Options:
  --model [name|checkpoint_path]  multilingual model used for transcribing
                                  (default: medium)
  --model-constructor [OpenAIWhisperModel|TransformersWhisperModel]
                                  model variant to use (openai-whisper or
                                  transformers)
  --normalize-text BOOLEAN        whether to normalize the output text of the
                                  model before calculating WER or not
  --sorah-range FROM-TO INCLUSIVE (EX: 1:114)
  -d, --device TEXT               device used to load the model
  -o DIRECTORY                    output directory
  --output-filename TEXT
  --help                          Show this message and exit.
```

## Examples

- Calculate WER + include benchmarking data for juz 28 (58:66) using `QuranComTranscriper` (model: default vanilla medium)

```bash
python3 main.py \
  --sorah-range 58:66 \
  "QuranComTranscriper" \
  "metadata.json" \
  "Minshawy_Murattal_128kbps"
```

- Calculate WER + include benchmarking data for juz 28 (58:66) using `AyatTranscriper` (model: default vanilla medium)

```bash
python3 main.py \
  --sorah-range 58:66 \
  "AyatTranscriper" \
  "ayat_28-30.csv" \
  "Minshawy_Murattal_128kbps"
```

- Use an opena-ai whisper checkpoint:

```bash
python3 main.py \
  --sorah-range 58:66 \
  --model "/kaggle/working/checkpoint-epoch=0007.ckpt" \
  --model-constructor "OpenAIWhisperModel" \
  "QuranComTranscriper" \
  "metadata.json" \
  "Minshawy_Murattal_128kbps"
```

- Use a whisepr transformers checkpoint:

```bash
python3 main.py \
  --sorah-range 58:66 \
  --model "/kaggle/working/checkpoint-epoch=0007.ckpt" \
  --model-constructor "TransformersWhisperModel" \
  "QuranComTranscriper" \
  "metadata.json" \
  "Minshawy_Murattal_128kbps"
```
