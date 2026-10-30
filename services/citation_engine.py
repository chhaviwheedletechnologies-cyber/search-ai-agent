class CitationEngine:

    def extract(self, responses, business_name=""):
        items = responses.get("responses", []) if isinstance(responses, dict) else responses
        citations = []
        seen = set()

        business = (business_name or "").lower().strip()

        for item in items:

            if not isinstance(item, dict):
                continue

            if item.get("engine") != "Google Search":
                continue

            competitors = item.get("competitors") or []
            for result in competitors:
                if not isinstance(result, dict):
                    continue

                title = result.get("title", "")
                source = result.get("source", "")
                url = result.get("link", "")

                text = f"{title} {source}".lower()

                # Sirf business-related results rakho
                if business and business not in text:
                    continue

                if url in seen:
                    continue

                seen.add(url)

                citations.append({
                    "title": title,
                    "position": result.get("position"),
                    "source": source,
                    "url": url
                })

        return citations