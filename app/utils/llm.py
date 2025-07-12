from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from accelerate import Accelerator
from peft import PeftModel
import torch
import re


class ModelLoader:
    """
    A class used to load Kiara LLM model
    """

    def __init__(self, model_path: str, tokenizer_path: str, adapter_path: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path, trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        special_tokens = {
            "additional_special_tokens": ["<|context|>", "<|endofanswer|>"]
        }

        self.tokenizer.add_special_tokens(special_tokens)
        self.accelerator = Accelerator()

        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=False,
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
        model.resize_token_embeddings(len(self.tokenizer), mean_resizing=False)
        self.model = PeftModel.from_pretrained(
            model,
            adapter_path,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        self.model = model.to("cuda")

    def add_system_prompt(self, system_prompt: str):
        self.system_prompt = system_prompt
        return self

    def _clean_response(self, text: str) -> str:
        """
        Extract only the assistant's response from the generated text
        by removing the original prompt and truncating at <|endofanswer|>
        """

        # Ambil isi antara <|assistant|> dan <|endofanswer|> atau sebelum role lain
        match = re.search(
            r"<\|assistant\|>\s*(.*?)(?=<\|endofanswer\|>|<\|user\||<\|system\||<\|assistant\||$)",
            text,
            re.DOTALL,
        )

        if match:
            cleaned = match.group(1).strip()
        else:
            # Fallback jika pattern tidak ketemu
            cleaned = text.strip()

        # Bersihkan semua special token sisa
        cleaned = re.sub(r"<\|[^|]*\|>", "", cleaned)
        cleaned = re.sub(r"</?s>", "", cleaned)  # </s> dan <s>
        cleaned = cleaned.replace("<eos>", "")

        # Token end lain yang tidak dipakai
        end_tokens = [
            "<end_of_turn>",
            "<|end|>",
            "<|endoftext|>",
            "<|im_end|>",
        ]
        for token in end_tokens:
            cleaned = cleaned.replace(token, "")

        # Normalisasi whitespace
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)  # max 2 newline
        cleaned = re.sub(r"[ \t]+", " ", cleaned)  # multiple space jadi satu
        cleaned = cleaned.strip()

        return cleaned

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
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                repetition_penalty=1.2,
                temperature=0.3,
                top_p=0.7,
            )

        # Get the full generated text
        decoded = self.tokenizer.decode(output[0], skip_special_tokens=False)

        # Clean to extract only the assistant's response
        cleaned = self._clean_response(decoded)
        return cleaned
