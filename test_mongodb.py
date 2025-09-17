import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URI
    uri = os.getenv("MONGODB_URI")
    print(f"Attempting to connect to MongoDB...")
    
    try:
        # Create client
        client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Test connection
        print("Pinging database...")
        await client.admin.command("ping")
        print("✅ Successfully connected to MongoDB!")
        
        # List databases
        print("\nListing databases:")
        async for db in client.list_databases():
            print(f"- {db['name']}")
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    asyncio.run(test_connection())
