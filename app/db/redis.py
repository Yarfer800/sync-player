from redis.asyncio import Redis, from_url
from app.core.config import Config

config = Config()

# Global redis client
redis_client: Redis = from_url(config.redis_url, decode_responses=True)
