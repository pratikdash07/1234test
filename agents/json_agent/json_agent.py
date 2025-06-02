import json
import os
from core.memory.redis_client import MemoryStore

class JSONAgent:
    def __init__(self):
        self.required_fields = {
            "order_id": int,
            "customer": str,
            "amount": float,
            "items": list
        }
        self.memory_store = MemoryStore()

    def parse(self, content):
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return {"valid": False, "error": "Invalid JSON format", "anomalies": ["Invalid JSON"]}

        anomalies = []
        for field, field_type in self.required_fields.items():
            if field not in data:
                anomalies.append(f"Missing field: {field}")
            elif not isinstance(data[field], field_type):
                anomalies.append(f"Type error: {field} should be {field_type.__name__}")

        result = {
            "valid": len(anomalies) == 0,
            "data": data if len(anomalies) == 0 else None,
            "anomalies": anomalies
        }
        return result

    def process(self, file_path, content, classification):
        source_id = os.path.splitext(os.path.basename(file_path))[0]

        # Log metadata
        self.memory_store.log_metadata(
            source_id,
            {
                "source": "json",
                "filename": file_path,
                "classification": classification
            }
        )

        result = self.parse(content)
        self.memory_store.log_agent_fields(source_id, "json_agent", result)

        if not result["valid"]:
            self.memory_store.log_action(source_id, "alert")
        else:
            self.memory_store.log_action(source_id, "accept")

        trace = {
            "step": "json_processed",
            "result": result,
            "action": "alert" if not result["valid"] else "accept"
        }
        self.memory_store.log_decision_trace(source_id, trace)

        return result
