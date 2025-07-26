import os
import re
import json
import subprocess

class DialogGenerator:
    def __init__(self, backend="groq", model_name="llama3-8b-8192", env_path=None, model_path=None, auto_model=False):
        self.backend = backend
        self.model_name = model_name

        if self.backend == "groq":
            from openai import OpenAI
            key = os.getenv("GROQ_API_KEY")
            if env_path:
                with open(env_path) as f:
                    for line in f:
                        if "GROQ_API_KEY" in line:
                            key = line.strip().split("=")[1]
                            break
            if not key:
                raise ValueError("GROQ_API_KEY not found. Provide via .env or env_path.")
            self.client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

        elif self.backend == "local":
            if auto_model:
                self.model_path = self._download_model_if_needed()
            else:
                if not model_path:
                    raise ValueError("No model_path provided and auto_model is False.")
                self.model_path = model_path
            self._install_llama_cpp()
            from llama_cpp import Llama
            self.pipeline = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=4,
                chat_format="llama-2",
                n_gpu_layers=20
            )

    def _install_llama_cpp(self):
        try:
            import llama_cpp
        except ImportError:
            print("🔧 Installing llama-cpp-python...")
            subprocess.run(["pip", "install", "llama-cpp-python"], check=True)

    def _download_model_if_needed(self):
        model_filename = "llama-2-7b-chat.Q4_K_M.gguf"
        model_path = f"/content/{model_filename}"
        if not os.path.exists(model_path):
            print("⬇️ Downloading LLaMA 2 7B Chat model...")
            subprocess.run([
                "wget", "-O", model_path,
                "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"
            ], check=True)
        else:
            print("✅ Model already exists.")
        return model_path

    def _load_prompt(self, path):
        with open(path, "r") as f:
            return f.read()

    def extract_json(self, text):
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON block found.")
    
        block = text[start:end+1]
    
        # Correcciones básicas
        block = block.replace("“", '"').replace("”", '"').replace("’", "'")
        block = block.replace('\\"', '"')
        block = re.sub(r'("P\\d)(:\s*\")', r'\1"\2', block)
    
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            print("❌ First JSON parse failed, trying repair...")
    
            repaired = self.try_repair(block)  # ← Usamos el método de abajo
            if repaired:
                return repaired
            print("❌ Final repair failed.\n", block)
            raise
    def try_repair(self, block):
        try:
            # Correcciones avanzadas
            block = re.sub(r',\s*}', '}', block)  # elimina comas antes de }
            block = re.sub(r',\s*]', ']', block)  # elimina comas antes de ]
            block = re.sub(r'(\w+):', r'"\1":', block)  # comillas en keys sin comillas
            block = re.sub(r'“|”', '"', block)
            block = re.sub(r'\["([^"]+)"\s+in\s+[^"\]]+\]', r'["\1"]', block)
            block = re.sub(r'(")(\s*])', r'\1,\2', block)
    
            # Reparación de listas de tonos, metas, etc.
            block = re.sub(r'\n+', ' ', block)
            block = re.sub(r'\s+', ' ', block)
    
            return json.loads(block)
        except Exception:
            return None


    def generate_specification(self, real_dialog, prompt_path="prompts/...", base_dir=None, dialog_id=None):
        prompt = self._load_prompt(prompt_path)
        prompt_filled = prompt.replace("{REAL_DIALOG_HERE}", real_dialog)

        if self.backend == "groq":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt_filled}],
                temperature=0.7
            )
            output = response.choices[0].message.content
        else:
            response = self.pipeline.create_chat_completion(
                messages=[{"role": "user", "content": prompt_filled}]
            )
            output = response["choices"][0]["message"]["content"]

        print("🟡 Model output for specification:\n", output)

        if base_dir and dialog_id:
            raw_path = os.path.join(base_dir, "specifications_failed", f"{dialog_id}_raw_output.txt")
            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(output)

        try:
            parsed = self.extract_json(output)
            return parsed, output
        except Exception as e:
            return None, output


    def generate_dialog(self, specification, prompt_path="prompts/prompt_generate_dialog.txt"):
        prompt = self._load_prompt(prompt_path)
        prompt_filled = prompt.replace("{SPECIFICATION_HERE}", str(specification))

        if self.backend == "groq":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt_filled}],
                temperature=0.8
            )
            return response.choices[0].message.content
        else:
            response = self.pipeline.create_chat_completion(
                messages=[{"role": "user", "content": prompt_filled}]
            )
            return response["choices"][0]["message"]["content"]
