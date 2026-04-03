from agents.scoring_utils import extract_company_name, extract_domain


def enforce_diversity(results: list, limit: int = 5) -> list:
    selected = []
    domain_counts = {}
    seen_companies = set()
    content_type_counts = {}

    for item in results:
        domain = extract_domain(item.get("url", ""))
        content_type = item.get("content_type", "resource")
        company_name = (item.get("entity", {}) or {}).get("company_name") or extract_company_name(
            item.get("url", ""), item.get("_content", "")
        )

        if not domain:
            continue
        if company_name and company_name.lower() in seen_companies:
            continue
        if domain_counts.get(domain, 0) >= 1:
            continue
        if content_type_counts.get(content_type, 0) >= 2:
            continue

        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if company_name:
            seen_companies.add(company_name.lower())
        content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        selected.append(item)

        if len(selected) == limit:
            return selected

    for item in results:
        domain = extract_domain(item.get("url", ""))
        content_type = item.get("content_type", "resource")
        company_name = (item.get("entity", {}) or {}).get("company_name") or extract_company_name(
            item.get("url", ""), item.get("_content", "")
        )
        if not domain:
            continue
        if company_name and company_name.lower() in seen_companies:
            continue
        if domain_counts.get(domain, 0) >= 1:
            continue
        if content_type_counts.get(content_type, 0) >= 2:
            continue

        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if company_name:
            seen_companies.add(company_name.lower())
        content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        selected.append(item)
        if len(selected) == limit:
            break

    return selected
