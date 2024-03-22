# whisper-quran-cli

## Requirements:

```bash
sudo apt install ffmpeg -y
```
```bash
pip3 install click \
  jiwer \
  openai-whisper \
  pydantic
```

```bash
python3 main.py --help
```

```
Usage: main.py [OPTIONS] METADATA_PATH AUDIO_PATH

  generate csv files containing WER for the given input and model

Options:
  --model [name|checkpoint_path]  multilingual model used for transcribing
                                  (default: medium)
  --sorah-range FROM-TO INCLUSIVE (EX: 1:114)
  --out-prefix TEXT
  -o DIRECTORY                    output directory
  -d, --device TEXT               device used to load the model
  --help                          Show this message and exit.
```

## Examples

* Calculate WER + include benchmarking data for juz 28 (58:66)

```bash
python3 main.py \
  --sorah-range 58:66 \
  "metadata.json" \
  "Minshawy_Murattal_128kbps"
```

* Use a checkpoint:

```bash
python3 main.py \
  --sorah-range 58:66 \
  "metadata.json" \
  "Minshawy_Murattal_128kbps" \
  --model /kaggle/working/checkpoint-epoch=0007.ckpt
```

## Notes:

* `METADATA_PATH` must be a path for a json file that contains follows the schema in `models.py`

* `AUDIO_PATH` is a directory that must contain sorahs in this format `sss-pppppp.mp3` where `s` refers to the sorah number and `p` refers to the part number. (ex: `001-000001.mp3`)
