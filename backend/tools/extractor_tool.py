def extractor_tool(raw_text):
    if not raw_text:
        return ""

    lines = raw_text.split("\n")

    important = []

    for line in lines:
        line = line.strip()

        if len(line) > 40:
            important.append(line)

    return " ".join(important[:10])
