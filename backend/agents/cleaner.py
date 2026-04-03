def clean_data(raw_data):
    cleaned = []

    print(f"🧪 BEFORE CLEAN: {len(raw_data)}")

    for item in raw_data:
        if not isinstance(item, dict):
            continue

        text = item.get("content", "").strip()

        if len(text) > 100:
            cleaned.append({
                "url": item.get("url", ""),
                "content": text,
            })

    cleaned = cleaned[:5]

    print(f"🧹 AFTER CLEAN: {len(cleaned)}")
    return cleaned
