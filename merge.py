import pathlib
from utils import path_join
from csv import DictReader


def merge(srcs: tuple[str, ...], out_prefix: str = "merged", output_dir: str = "."):
    output_dir_path = pathlib.Path(output_dir)
    opened_files = []

    for src in srcs:
        opened_files.append(open(src, "r"))

    with open(
        path_join(output_dir_path, f"{out_prefix}_total.csv"), "w"
    ) as output_file:
        fieldnames = DictReader(opened_files[0]).fieldnames
        output_file.write(f"{','.join(fieldnames)}\n")  # type: ignore
        opened_files[0].seek(0, 0)  # type: ignore

        readers: list[DictReader] = []
        for opened_file in opened_files:
            readers.append(DictReader(opened_file))

        for line in readers[0]:
            total_num = float(line["wer"]) * int(line["num_words_reference"])  # type: ignore
            total_denum = int(line["num_words_reference"])
            for i in range(1, len(readers)):
                line = next(readers[i])
                total_num += float(line["wer"]) * int(line["num_words_reference"])  # type: ignore
                total_denum += int(line["num_words_reference"])

            wer = total_num / total_denum
            num_words_reference = total_denum
            entry: list[str] = []
            for fieldname in fieldnames:  # type: ignore
                if fieldname == "wer":
                    entry.append(f"{wer:.4f}")
                elif fieldname == "num_words_reference":
                    entry.append(f"{num_words_reference}")
                else:
                    entry.append(line[fieldname])

            output_file.write(f"{','.join(entry)}\n")

    for opened_file in opened_files:
        opened_file.close()
