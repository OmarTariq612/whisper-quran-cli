# whisper-quran-cli

## Requirements:

```bash
sudo apt install ffmpeg -y
```
```bash
pip3 install click \
  mutagen \
  jiwer \
  evaluate \
  openai-whisper \
  pyarabic \
  audiomentations
```

```bash
python3 main.py --help
```

```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  generate  generate csv files containing WER for the given input and model
  merge     merge multiple csv files into one containing WER as a total
```

```bash
python3 main.py generate --help
```

```
Usage: main.py generate [OPTIONS] TEXT_CSV_PATH AUDIO_PATH

  generate csv files containing WER for the given input and model

Options:
  --model [tiny|base|small|medium|large]
                                  multilingual model used for transcribing
                                  (default: medium)
  --sorah-range FROM-TO INCLUSIVE (EX: 1:114)
  --out-prefix TEXT
  --log-level [normal|verbose]    determine the logging level (default:
                                  normal)
  -o DIRECTORY                    output directory
  -b, --bench                     export benchmark info to a file
  --help                          Show this message and exit.
```

```bash
python3 main.py merge --help
```

```
Usage: main.py merge [OPTIONS] SRC...

  merge multiple csv files into one containing WER as a total

Options:
  --out-prefix TEXT
  -o DIRECTORY
  --help             Show this message and exit.
```

## Examples

* Calculate WER and generate csv files + include benchmarking data for juz 28 (58:66)

```bash
python3 main.py generate \
  --sorah-range 58:66 \
  "/kaggle/input/last-three-juz-text/ayat_28-30.csv" \
  "/kaggle/working/Minshawy/audio/Minshawy_Murattal_128kbps" \
  --log-level verbose \
  --bench
```

* Merge multiple WER csv files into one.

```bash
python3 main.py merge \
  "output/husary_total.csv" \
  "output/hudhaify_total.csv" \
  "output/minshawy_total.csv"
```

* Use a checkpoint:

```bash
python3 main.py generate \
  --sorah-range 58:66 \
  "/kaggle/input/last-three-juz-text/ayat_28-30.csv" \
  "/kaggle/working/Minshawy/audio/Minshawy_Murattal_128kbps" \
  --model /kaggle/working/checkpoint-epoch=0007.ckpt \
  --log-level verbose \
  --bench
```

## Notes:

* `TEXT_CSV_PATH` must be a path for a file that contains literal columns `sorah`, `ayah` and `text`
* `AUDIO_PATH` is a directory that must contain sorahs in this format `sssaaa.mp3` where `s` refers to the sorah number and `a` refers to the ayah number. (ex: `001001.mp3`)
