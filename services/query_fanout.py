class QueryFanout:

    def generate(self, business, location):

        business = business.strip()
        location = location.strip()

        return [
            f"{business} {location}",
            f"{business} reviews {location}",
            f"{business} Google Business Profile {location}",
            f"{business} official website",
            f"{business} LinkedIn",
            f"{business} AI services {location}",
            f"{business} software development {location}",
            f"{business} customer reviews",
            f"{business} contact information",
            f"{business} reputation"
        ]