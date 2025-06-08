import asyncio
import httpx

API_URL = "http://localhost:8000"
USERS = [
    {"username": "test-user-xkawofngyh131", "email": "testuser.xkawo@example.com", "password": "ktirhd24ivo22awn32#"},
    {"username": "test-user-jjkoelfmah125", "email": "testuser.jjkoe@example.com", "password": "ktirhd24ivo22awn32#"},
    {"username": "test-user-kdrihnekog232", "email": "testuser.kdrih@example.com", "password": "ktirhd24ivo22awn32#"},
]


async def register_or_login(client: httpx.AsyncClient, user):
    try:
        r = await client.post(f"{API_URL}/register", json=user)
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            print(f"[!] {user['username']} already exists, trying to login...")
        else:
            raise

    r = await client.post(
        f"{API_URL}/login",
        data={
            "username": user["email"],
            "password": user["password"]
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )


    r.raise_for_status()
    token = r.json()["access_token"]
    return token



async def create_auction(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Race Condition Test Auction",
        "description": "Let's test race conditions.",
        "starting_price": 100.0,
        "duration_minutes": 10
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_URL}/auctions", json=data, headers=headers)
        r.raise_for_status()
        return r.json()["id"]


async def place_bid(token, auction_id, amount):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"amount": amount}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_URL}/auctions/{auction_id}/bid", json=data, headers=headers)
        print(f"[BID] Status: {r.status_code}, Amount: {amount}, Response: {r.text}")


async def close_auction(token, auction_id):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_URL}/auctions/{auction_id}/close", headers=headers)
        if r.status_code == 200:
            print(f"✅ Auction {auction_id} closed.")
        else:
            print(f"⚠️ Failed to close auction {auction_id}: {r.status_code} - {r.text}")

async def main():
    async with httpx.AsyncClient() as client:
        tokens = []
        for user in USERS:
            try:
                token = await register_or_login(client, user)
                tokens.append(token)
            except Exception as e:
                print(f"❌ Failed for {user['username']}: {e}")
                return

    creator_token = tokens[0]
    bidder1_token = tokens[1]
    bidder2_token = tokens[2]

    auction_id = await create_auction(creator_token)
    print(f"✅ Auction created: {auction_id}")

    bid_amounts = [150, 200, 250]

    for amount in bid_amounts:
        await asyncio.gather(
            place_bid(bidder1_token, auction_id, amount),
            place_bid(bidder2_token, auction_id, amount)
        )
        await asyncio.sleep(1)

    await close_auction(creator_token, auction_id)


if __name__ == "__main__":
    asyncio.run(main())
