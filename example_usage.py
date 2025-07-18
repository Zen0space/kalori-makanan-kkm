#!/usr/bin/env python3
"""
Example usage of the Kalori Makanan API with API key authentication and rate limiting.

This script demonstrates:
1. Creating a test user and obtaining an API key
2. Making authenticated requests to various endpoints
3. Handling rate limit responses
4. Checking rate limit status
"""

import requests
import json
import time
from typing import Optional

# Base URL of the API (change this to your deployed URL)
BASE_URL = "http://localhost:8000"

class KaloriMakananAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = BASE_URL
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["X-API-Key"] = api_key

    def create_test_user(self):
        """Create a test user and get API key"""
        response = requests.post(f"{self.base_url}/api/create-test-user")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test user created successfully!")
            print(f"🔑 API Key: {data['api_key']}")
            print(f"⚠️  {data['message']}")
            return data['api_key']
        else:
            print(f"❌ Failed to create test user: {response.text}")
            return None

    def check_rate_limit_status(self):
        """Check current rate limit status"""
        response = requests.get(
            f"{self.base_url}/api/rate-limit-status",
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print("\n📊 Rate Limit Status:")
            print(f"User: {data['user']['email']} ({data['user']['name']})")

            for period, info in data['limits'].items():
                print(f"\n{period.replace('_', ' ').title()}:")
                print(f"  - Limit: {info['limit']}")
                print(f"  - Used: {info['used']}")
                print(f"  - Remaining: {info['remaining']}")

            # Also print headers
            self._print_rate_limit_headers(response)
        else:
            print(f"❌ Failed to check rate limit status: {response.text}")

    def search_foods(self, query: str):
        """Search for foods by name"""
        response = requests.get(
            f"{self.base_url}/foods/search",
            params={"name": query},
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 Search results for '{query}': {data['total']} found")

            for food in data['foods'][:5]:  # Show first 5 results
                print(f"\n  📋 {food['name']}")
                print(f"     Serving: {food.get('serving', 'N/A')}")
                print(f"     Calories: {food.get('calories_kcal', 'N/A')} kcal")
                print(f"     Category: {food.get('category', 'N/A')}")

            if data['total'] > 5:
                print(f"\n  ... and {data['total'] - 5} more results")

            self._print_rate_limit_headers(response)
            return data

        elif response.status_code == 429:
            print(f"⚠️  Rate limit exceeded!")
            self._handle_rate_limit_exceeded(response)
            return None

        elif response.status_code == 401:
            print(f"❌ Unauthorized: Invalid or missing API key")
            return None

        else:
            print(f"❌ Error searching foods: {response.text}")
            return None

    def get_food_detail(self, food_id: int):
        """Get detailed information about a specific food"""
        response = requests.get(
            f"{self.base_url}/foods/{food_id}",
            headers=self.headers
        )

        if response.status_code == 200:
            food = response.json()
            print(f"\n📋 Food Details:")
            print(f"  Name: {food['name']}")
            print(f"  Serving: {food.get('serving', 'N/A')}")
            print(f"  Weight: {food.get('weight_g', 'N/A')} g")
            print(f"  Calories: {food.get('calories_kcal', 'N/A')} kcal")
            print(f"  Category: {food.get('category', 'N/A')}")
            print(f"  Reference: {food.get('reference', 'N/A')}")

            self._print_rate_limit_headers(response)
            return food
        else:
            print(f"❌ Error getting food details: {response.text}")
            return None

    def list_categories(self):
        """Get list of all food categories"""
        response = requests.get(
            f"{self.base_url}/categories",
            headers=self.headers
        )

        if response.status_code == 200:
            categories = response.json()
            print(f"\n📂 Food Categories ({len(categories)} total):")
            for cat in categories[:10]:  # Show first 10
                print(f"  - {cat['name']}")

            if len(categories) > 10:
                print(f"  ... and {len(categories) - 10} more categories")

            self._print_rate_limit_headers(response)
            return categories
        else:
            print(f"❌ Error getting categories: {response.text}")
            return None

    def demonstrate_rate_limiting(self):
        """Demonstrate rate limiting by making multiple requests"""
        print("\n🔄 Demonstrating rate limiting...")
        print("Making multiple requests to trigger rate limit...")

        request_count = 0
        while request_count < 15:  # Try to exceed the per-minute limit
            response = requests.get(
                f"{self.base_url}/foods/search",
                params={"name": "test"},
                headers=self.headers
            )

            request_count += 1

            if response.status_code == 429:
                print(f"\n⚠️  Rate limit hit after {request_count} requests!")
                self._handle_rate_limit_exceeded(response)
                break
            elif response.status_code == 200:
                remaining = response.headers.get('X-RateLimit-Remaining-Minute', 'Unknown')
                print(f"  Request {request_count}: Success (Remaining this minute: {remaining})")
            else:
                print(f"  Request {request_count}: Error {response.status_code}")
                break

            # Small delay between requests
            time.sleep(0.1)

    def _print_rate_limit_headers(self, response):
        """Print rate limit headers from response"""
        print("\n📈 Rate Limit Info:")
        headers_to_check = [
            ('X-RateLimit-Limit-Minute', 'Limit per minute'),
            ('X-RateLimit-Remaining-Minute', 'Remaining this minute'),
            ('X-RateLimit-Limit-Hour', 'Limit per hour'),
            ('X-RateLimit-Remaining-Hour', 'Remaining this hour'),
            ('X-RateLimit-Limit-Day', 'Limit per day'),
            ('X-RateLimit-Remaining-Day', 'Remaining today')
        ]

        for header, label in headers_to_check:
            value = response.headers.get(header)
            if value:
                print(f"  {label}: {value}")

    def _handle_rate_limit_exceeded(self, response):
        """Handle rate limit exceeded response"""
        retry_after = response.headers.get('Retry-After', 'Unknown')
        print(f"  Retry after: {retry_after} seconds")

        # Print which limits were exceeded
        print("\n  Limits exceeded:")
        for period in ['minute', 'hour', 'day']:
            limit_header = f'X-RateLimit-Limit-{period.capitalize()}'
            used_header = f'X-RateLimit-Used-{period.capitalize()}'

            limit = response.headers.get(limit_header)
            used = response.headers.get(used_header)

            if limit and used and int(used) >= int(limit):
                print(f"    - {period}: {used}/{limit}")


def main():
    """Main demonstration function"""
    print("🍜 Kalori Makanan API Demo")
    print("=" * 50)

    # Step 1: Create test user and get API key
    print("\n1️⃣ Creating test user...")
    api = KaloriMakananAPI()
    api_key = api.create_test_user()

    if not api_key:
        print("Failed to create test user. Exiting.")
        return

    # Create authenticated client
    api = KaloriMakananAPI(api_key)

    # Step 2: Check initial rate limit status
    print("\n2️⃣ Checking initial rate limit status...")
    api.check_rate_limit_status()

    # Step 3: Search for foods
    print("\n3️⃣ Searching for foods...")
    api.search_foods("nasi goreng")

    # Step 4: Get food details
    print("\n4️⃣ Getting food details (ID: 1)...")
    api.get_food_detail(1)

    # Step 5: List categories
    print("\n5️⃣ Listing food categories...")
    api.list_categories()

    # Step 6: Check rate limit status again
    print("\n6️⃣ Checking rate limit status after requests...")
    api.check_rate_limit_status()

    # Step 7: Demonstrate rate limiting (optional)
    print("\n7️⃣ Would you like to demonstrate rate limiting? (y/n)")
    choice = input().lower()
    if choice == 'y':
        api.demonstrate_rate_limiting()

    print("\n✅ Demo completed!")
    print(f"\n💡 Your API key: {api_key}")
    print("Save this key to use in your applications!")


if __name__ == "__main__":
    main()
