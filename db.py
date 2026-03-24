import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta
import hashlib

class MongoManager:
    def __init__(self):
        # Automatically pulls from secrets.toml (local) or Cloud Secrets
        uri = st.secrets["MONGO_URI"]
        self.client = MongoClient(uri)
        self.db = self.client["cricket_agent_prod"]
        self.history = self.db["chat_history"]
        self.cache = self.db["query_cache"]

    def get_session_history(self, session_id: str):
        doc = self.history.find_one({"session_id": session_id})
        return doc["messages"] if doc else []

    def save_session_history(self, session_id: str, messages: list):
        self.history.update_one(
            {"session_id": session_id},
            {"$set": {"messages": messages, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    def check_cache(self, query: str):
        q_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
        valid_window = datetime.utcnow() - timedelta(hours=24)
        return self.cache.find_one({"hash": q_hash, "timestamp": {"$gt": valid_window}})

    def set_cache(self, query: str, data: dict):
        q_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
        self.cache.update_one(
            {"hash": q_hash},
            {"$set": {"query": query, "data": data, "timestamp": datetime.utcnow()}},
            upsert=True
        )