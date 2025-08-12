import asyncio
from helpers import parse_csv
from street import reverse_geocode

async def main():
    
    test_data = parse_csv("../tests/test_data.csv")
    
    results = await reverse_geocode(test_data)
    for r in results:
        print(r)

asyncio.run(main())
