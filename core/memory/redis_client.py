import redis
import json
from datetime import datetime
from typing import Dict, Any, Optional

class MemoryStore:
    def __init__(self, host="redis", port=6379, db=0):
        # Key changes: removed decode_responses=True
        self.conn = redis.Redis(
            host=host,
            port=port,
            db=db,
            socket_connect_timeout=3,
            socket_keepalive=True
        )

    def _make_key(self, source_id: str) -> str:
        return f"trace:{source_id}"
    
    def get_full_trace(self, source_id: str) -> Optional[Dict[str, Any]]:
        key = self._make_key(source_id)
        data = self.conn.hgetall(key)
        if not data:
            return None
            
        parsed_data = {}
        for k, v in data.items():
            try:
                # Decode bytes to string first
                key_str = k.decode("utf-8") if isinstance(k, bytes) else k
                val_str = v.decode("utf-8") if isinstance(v, bytes) else v
                parsed_data[key_str] = json.loads(val_str)
            except json.JSONDecodeError:
                parsed_data[key_str] = val_str
            except Exception as e:
                print(f"Error parsing trace data: {str(e)}")
                parsed_data[key_str] = val_str
        return parsed_data

    def store_trace(self, source_id: str, data: dict):
        self.conn.hset(f"trace:{source_id}", mapping={
            k: json.dumps(v) if not isinstance(v, (bytes, str)) else v 
            for k, v in data.items()
        })

    def log_metadata(self, source_id: str, metadata: Dict[str, Any]):
        key = self._make_key(source_id)
        metadata["timestamp"] = metadata.get("timestamp") or datetime.utcnow().isoformat()
        self.conn.hset(key, "metadata", json.dumps(metadata))

    def log_agent_fields(self, source_id: str, agent_name: str, fields: Dict[str, Any]):
        key = self._make_key(source_id)
        self.conn.hset(key, f"{agent_name}_fields", json.dumps(fields))

    def log_action(self, source_id: str, action: str):
        key = self._make_key(source_id)
        self.conn.hset(key, "action", action)

    def log_decision_trace(self, source_id: str, trace: Any):
        key = self._make_key(source_id)
        self.conn.hset(key, "decision_trace", json.dumps(trace))
