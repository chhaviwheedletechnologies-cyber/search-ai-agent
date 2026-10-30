import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
# remove this import

load_dotenv()


class ScanEngine:

    def __init__(self):

        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")

    # ==========================================================
    # MAIN SCAN
    # ==========================================================

    def scan(self, prompts, location=None):
        responses = []
        failed_engines = []

        for prompt in prompts:
            engines = [
                self.scan_google(prompt, location),
                self.scan_chatgpt(prompt),
                self.scan_gemini(prompt),
                self.scan_perplexity(prompt)
            ]

            for result in engines:
                if result.get("status") == "success":
                    responses.append(result)
                else:
                    failed_engines.append({
                        "engine": result.get("engine"),
                        "prompt": prompt
                    })
  
        results = responses + [
            {
                "engine": f["engine"],
                "prompt": f["prompt"],
                "status": "failed"
            }
            for f in failed_engines
        ]

        return results

    # ==========================================================
    # CHATGPT
    # ==========================================================

    def scan_chatgpt(self, prompt):

        try:

            response = self.openai_client.chat.completions.create(

                model="gpt-4o-mini",

                messages=[

                    {
                        "role": "system",
                        "content": """
You are Birdeye-style AI Search Visibility Analyzer.

Rules:
- Analyze ONLY the business mentioned in the prompt.
- Use the business name exactly as provided.
- If the business appears in search results, state that clearly.
- Mention only business-specific visibility signals.
- Do NOT invent services.
- Do NOT recommend unrelated companies.
- Keep the response concise with:
  1. Mention Found/Not Found
  2. Visibility Signals
  3. Local Presence
  4. Improvement Opportunities
"""
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ]

            )

            return {
                "engine": "ChatGPT",
                "prompt": prompt,
                "response": response.choices[0].message.content,
                "status": "success"
            }

        except Exception as e:

            return {
                "engine": "ChatGPT",
                "prompt": prompt,
                "response": str(e),
                "status": "failed"
            }

    # ==========================================================
    # GEMINI
    # ==========================================================

    def scan_gemini(self, prompt):

        try:

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"

            payload = {

                "contents": [

                    {
                        "parts": [
                            {
                                "text": f"""
You are an AI Search Visibility Analyzer.

Analyze:
{prompt}

Return:
- Brand found
- Summary
- Key findings
- Suggestions
"""
                            }
                        ]
                    }

                ]

            }

            r = requests.post(url, json=payload, timeout=30)

            data = r.json()

            if "candidates" not in data:

                return {
                    "engine": "Gemini",
                    "prompt": prompt,
                    "response": data,
                    "status": "failed"
                }

            return {
                "engine": "Gemini",
                "prompt": prompt,
                "response": data["candidates"][0]["content"]["parts"][0]["text"],
                "status": "success"
            }

        except Exception as e:

            return {
                "engine": "Gemini",
                "prompt": prompt,
                "response": str(e),
                "status": "failed"
            }

    # ==========================================================
    # PERPLEXITY
    # ==========================================================

    def scan_perplexity(self, prompt):

        try:

            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            r = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            data = r.json()

            output = ""

            if "choices" in data:
                output = data["choices"][0]["message"]["content"]

            if not output:

                return {
                    "engine": "Perplexity",
                    "prompt": prompt,
                    "response": data,
                    "status": "failed"
                }

            return {
                "engine": "Perplexity",
                "prompt": prompt,
                "response": output,
                "status": "success"
            }

        except Exception as e:

            return {
                "engine": "Perplexity",
                "prompt": prompt,
                "response": str(e),
                "status": "failed"
            }

    # ==========================================================
    # SERPAPI
    # ==========================================================
    
    def scan_google(self, prompt, location=None): 
        try:
            url = "https://serpapi.com/search.json"

            params = {
                "engine": "google",
                "q": prompt,
                "hl": "en",
                "gl": "in",
                "api_key": self.serpapi_key
            }

            # User ne location di hai to hi bhejo
            if location:
                params["location"] = location

            data = requests.get(url, params=params, timeout=30).json()

            organic = data.get("organic_results", [])
            kg = data.get("knowledge_graph", {})

            competitors = []

            blocked_keywords = {
                "Cambridge",
                "rtings",
                "moody",
                "iec",
                "gst"
            }

            for item in organic:
                source = item.get("source", "")
                title = item.get("title", "")

                source_lower = source.lower()
                
                if any(k in source_lower for k in blocked_keywords):
                    continue

                competitors.append({
                    "position": item.get("position"),
                    "title": title,
                    "source": source,
                    "link": item.get("link")
                })

                if len(competitors) == 5:
                    break

            return {
                "engine": "Google Search",
                "prompt": prompt,
                "brand_found": bool(kg.get("title")),
                "knowledge_graph": {
                    "title": kg.get("title"),
                    "rating": kg.get("rating"),
                    "reviews": kg.get("review_count"),
                    "address": kg.get("address"),
                    "type": kg.get("type")
                },
                "competitors": competitors,
                "status": "success"
            }

        except Exception as e:
            return {
                "engine": "Google Search",
                "prompt": prompt,
                "response": str(e),
                "status": "failed"
            }

    # ==========================================================
    # AGGREGATION
    # ==========================================================

    def aggregate_results(self, prompts, results):

        success = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "failed"]

        citations = []
        seen = set()
        google_hits = 0
        review_count = 0

        strengths = []
        gaps = []

        # ---------------- Collect Google data ----------------

        for r in success:

            if r["engine"] != "Google Search":
                continue

            if r.get("brand_found"):
                google_hits += 1

            reviews = (r.get("knowledge_graph") or {}).get("reviews") or 0
            review_count = max(review_count, reviews)

            for item in r.get("competitors", []):

                link = item.get("link")

                if link and link not in seen:
                    seen.add(link)

                    citations.append({
                        "title": item.get("title"),
                        "source": item.get("source"),
                        "url": link
                    })

        # ---------------- Dynamic Summary ----------------

        if google_hits:
            strengths.append("Google Search visibility detected.")

        if any("linkedin.com" in c["url"].lower() for c in citations):
            strengths.append("LinkedIn presence detected.")

        if any(
            c["source"].lower() == "wheedle technologies"
            or ".ai" in c["url"].lower()
            for c in citations
        ):
            strengths.append("Official website detected.")

        if review_count < 5:
            gaps.append("More public reviews recommended.")

        gaps.append("FAQ schema recommended.")
        gaps.append("Local SEO can be strengthened.")

       # ---------------- Sentiment ----------------

        sentiment = "Positive" if google_hits else "Neutral"

       # ---------------- Dynamic Visibility Score ----------------

        visibility = 0

        if google_hits:
           visibility += 35

        visibility += min(25, len(citations) * 3)

        if review_count >= 50:
           visibility += 20
        elif review_count >= 10:
           visibility += 12
        elif review_count >= 1:
           visibility += 6

        visibility = min(100, visibility)

        return {
           "fanout": prompts,
           "responses": success,
           "failed_engines": [
               {
                   "engine": f["engine"],
                   "prompt": f["prompt"]
                }
                for f in failed
            ],
            "brand_found": google_hits > 0,
            "overall_sentiment": sentiment,
            "visibility_score": visibility,
            "summary": {
                "strengths": strengths,
                "gaps": gaps
            },
            "recommendations": [
                {
                    "title": "Add FAQ Schema",
                    "priority": "High"
                },
                {
                    "title": "Increase Google Reviews",
                    "priority": "High"
                },
                {
                    "title": "Strengthen Local Listings",
                    "priority": "Medium"
                }
            ],
            "citations": citations
        }