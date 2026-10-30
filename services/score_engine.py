class ScoreEngine:

    def calculate(self, responses=None):

        visibility = 80
        citations = 75
        sentiment = 90
        ranking = 70

        if responses:
            has_google = any(
                isinstance(r, dict) and r.get("engine") == "Google Search"
                for r in responses
            )
            if has_google:
                visibility = 85

        score = (visibility * 0.4) + (citations * 0.3) + (sentiment * 0.2) + (ranking * 0.1)

        return round(score, 2)