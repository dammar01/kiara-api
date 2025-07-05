from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from accelerate import Accelerator
import torch
import re


class ModelLoader:
    """
    A class used to load Kiara LLM model
    """

    def __init__(self, model_path: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True
        )
        self.accelerator = Accelerator()
        self.tokenizer.pad_token = self.tokenizer.eos_token
        # Simplified chat template with clear separators

        # Deepseek template
        self.tokenizer.chat_template = """
            {% if messages[0]['role'] == 'system' %}
            <|system|>
            {{ messages[0]['content'] }}
            {% endif %}
            {% for message in messages %}
            {% if message['role'] == 'user' %}
            <|user|>
            {{ message['content'] }}
            {% elif message['role'] == 'assistant' and message['content'] %}
            <|assistant|>
            {{ message['content'] }}
            {% endif %}
            {% endfor %}
            <|assistant|>
        """
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            llm_int8_enable_fp32_cpu_offload=True,
            bnb_4bit_quant_type="nf4",
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            # torch_dtype=torch.float16,
            quantization_config=quant_config,
            trust_remote_code=True,
            use_safetensors=True,
        )
        self.model = self.accelerator.prepare(model)
        self.system_prompt = """
        Kamu adalah asisten pribadi teknikal bernama Kiara. Tugasmu adalah membantu Dammar, seorang fullstack developer dan AI engineer.
        Kiara mampu:
        - Menjawab pertanyaan umum dan teknis secara singkat dan tepat.
        - Hanya memberikan informasi yang relevan, tidak mengulang atau mengelaborasi terlalu panjang.
        Gunakan Bahasa Indonesia, nada profesional, lembut, bersahabat dan padat. Jika ada informasi tidak diketahui, katakan "Saya belum mengetahui hal tersebut."
        """

    def _clean_response_gemma2(self, text: str) -> str:
        """
        Extract only the assistant's response from the generated text
        by removing the original prompt and matching the final assistant tag for gemma
        """
        match = re.search(
            r"<\|assistant\|>\s*(.*?)\s*(?:<end_of_turn>|<eos>|</s>|<\|)",
            text,
            re.DOTALL,
        )

        if match:
            cleaned = match.group(1).strip()
            cleaned = re.sub(r"\n{2,}", "\n", cleaned)
            return cleaned

        return text.strip()

    def predict(self, prompt: str) -> str:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Generate the formatted prompt using the chat template
        if hasattr(self.tokenizer, "apply_chat_template"):
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            formatted_prompt = prompt

        # Tokenize and prepare for model
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        # Generate response
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.3,
                top_p=0.7,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                repetition_penalty=1.2,
            )

        # Get the full generated text
        decoded = self.tokenizer.decode(output[0], skip_special_tokens=False)

        # Clean to extract only the assistant's response
        cleaned = self._clean_response_gemma2(decoded)
        return cleaned
