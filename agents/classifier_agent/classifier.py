import json
import os
import dotenv

# LLM imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()

class ClassifierAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.intent_labels = ["RFQ", "Complaint", "Invoice", "Regulation", "Fraud Risk"]
        # For fallback rule-based detection
        self.intent_examples = {
            "RFQ": ["request for quote", "quotation", "quote needed", "rfq"],
            "Complaint": ["not satisfied", "complaint", "issue", "problem", "bad experience", "unsatisfied"],
            "Invoice": ["invoice", "bill", "amount due", "payment due", "billed"],
            "Regulation": ["regulation", "compliance", "policy", "gdpr", "fda"],
            "Fraud Risk": ["fraud", "suspicious", "unauthorized", "risk", "scam"]
        }

    def detect_format(self, file_path, content):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".json":
            return "JSON"
        elif ext in [".eml", ".msg", ".txt"]:
            return "Email"
        elif ext == ".pdf":
            return "PDF"
        try:
            json.loads(content)
            return "JSON"
        except Exception:
            pass
        if "From:" in content and "Subject:" in content:
            return "Email"
        return "Unknown"

    def detect_intent(self, content):
        # Use Gemini LLM for intent detection
        prompt = ChatPromptTemplate.from_template("""
You are a business document classifier. Classify this document into one of:
[RFQ, Complaint, Invoice, Regulation, Fraud Risk]

Respond with only the label.

Content:
{content}
""")
        chain = prompt | self.llm
        try:
            result = chain.invoke({"content": content}).content.strip()
            for label in self.intent_labels:
                if label.lower() in result.lower():
                    return label
        except Exception:
            pass
        # Fallback: rule-based intent detection
        content_lower = content.lower()
        for intent, keywords in self.intent_examples.items():
            for kw in keywords:
                if kw in content_lower:
                    return intent
        return "Unknown"

    def classify(self, file_path, content):
        fmt = self.detect_format(file_path, content)
        intent = self.detect_intent(content)
        return {"format": fmt, "intent": intent}
