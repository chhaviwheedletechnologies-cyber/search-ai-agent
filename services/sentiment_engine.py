class SentimentEngine:

    def analyze(self, responses):
        # Handle both list and dict responses
        if isinstance(responses, dict):
            items = responses.get("responses", [])
        else:
            items = responses

        sentiments = []

        for item in items:
            if not isinstance(item, dict):
                continue

            text = str(item.get("response", "")).lower()

            if any(word in text for word in ["excellent", "great", "positive", "good", "5 star", "recommended"]):
                sentiment = "Positive"
            elif any(word in text for word in ["bad", "poor", "negative", "complaint", "issue"]):
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            sentiments.append({
                "engine": item.get("engine"),
                "prompt": item.get("prompt"),
                "sentiment": sentiment
            })

        return sentiments