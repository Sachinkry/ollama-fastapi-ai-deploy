# app/models/model_registry.py
from app.models.llm_model import LocalLLM
import threading

class ModelRegistry:
    def __init__(self):
        self.models = {}
        self.initialized = False
        print("🚀 ModelRegistry initialized but models not loaded yet.")

    def _load_models(self):
        print("🧠 Loading models in background thread...")
        try:
            self.models = {
                "distilgpt2": LocalLLM("distilgpt2"),
                "DialoGPT-small": LocalLLM("microsoft/DialoGPT-small"),
                # Comment out TinyLlama until stable (too big for M1)
                # "TinyLlama": LocalLLM("TinyLlama/TinyLlama-1.1B-Chat-v0.6"),
            }
            self.initialized = True
            print(f"✅ Models ready: {list(self.models.keys())}")
        except Exception as e:
            print(f"❌ Error loading models: {e}")

    def list_models(self):
        if not self.initialized:
            return []
        return list(self.models.keys())

    def get_model(self, name: str):
        if not self.initialized:
            raise RuntimeError("Models are still loading. Try again later.")
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found.")
        return self.models[name]

    def start_loading(self):
        threading.Thread(target=self._load_models, daemon=True).start()


# Singleton instance
model_registry = ModelRegistry()
