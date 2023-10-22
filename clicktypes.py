import click


class SorahRange(click.ParamType):
    name = "from-to inclusive (ex: 1:114)"

    def convert(self, value: str, param, ctx):
        if not ":" in value:
            self.fail(f"{value} is not a valid SorahRange")

        parts = value.split(":")
        if len(parts) != 2:
            self.fail(f"{value} is not a valid SorahRange")

        if not parts[0].isdecimal() or not parts[1].isdecimal():
            self.fail(
                f"invalid range: parts must be decimal between 1 and 114: {parts}"
            )

        minimum = int(parts[0], base=10)
        maximum = int(parts[1], base=10)

        if minimum < 1:
            self.fail(f"minimum({minimum}) must be > 0")
        if maximum > 114:
            self.fail(f"maximum({maximum}) must be <= 114")
        if minimum > maximum:
            self.fail(f"minimum({minimum}) must be <= maximum({maximum})")

        return (minimum, maximum)


SORAH_RANGE = SorahRange()
