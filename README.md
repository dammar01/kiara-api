# 🧠 Kiara API 🚀

**Kiara** is a personal AI assistant that runs on FastAPI and uses the local **Gemma** model as its base pretrained model. This project is for personal use only and serves as an API template for creating LLM model endpoints for **Gemma**.

## ⚙️ Key Features

- Local AI model integration using **Gemma** or Fine-tuning
- Supports Internal Key Access
- Supports **Function Calling** (Work in progress)
- Supports **CUDA 12.8**

## 🗂️ Directory Structure

```
kiara-api/
├── app/
│   ├── api/
│   │    ├── endpoint/
│   │    │   └── chat.py
│   │    └── router.py
│   ├── core/
│   │    ├── database.py
│   │    ├── middleware.py
│   │    └── settings.py
│   ├── models/
│   │    ├── chat.py
│   │    └── function_calling.py
│   ├── schemas/
│   │    └── chat_shemas.py
│   ├── utils/
│   │    └── llm.py
│   └── main.py
├── requirements.txt
├── public/
│   └── model/
├── venv/
...
```

## 🚀 Setup & Installation

1. **Clone repository**

   ```bash
    git clone https://github.com/dammar01/kiara-api.git
    cd kiara-api
   ```

2. **Create virtual environment**
   ```bash
    python -m venv venv
    venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Place your Gemma Model**
   - Download your desired Gemma model from [Hugging Face](https://huggingface.co/google)
   - Save the Gemma model in the path kiara-api/public/model
5. **Run FastAPI server**
   ```bash
   python run.py
   ```

## ⚡ API Endpoints

**POST http://127.0.0.1:5123/api/v1/chat/ask**

#### Request

```json
{
  "message": "Apa yang anda ketahui tentang saya?"
}
```

#### Response

````json
{
  "code": 200,
  "message": "Saya telah mempelajari banyak sekali tentang Anda. Kamu adalah seorang Fullstack Developer dan AI Engineer.  Aku akan membantumu dengan berbagai tugas, termasuk menjawab pertanyaan umum, memberikan informasi relevan dan memproses data.  Jika kamu membutuhkan bantuan, jangan ragu untuk bertanya!\n```\n**Penjelasan:**\n* **`",
  "data": [],
  "error": false
}
````

## 🔒 License

This project is licensed for personal use only.

It integrates and depends on third-party components:

- **Gemma** by Google DeepMind (via Hugging Face): https://huggingface.co/google/gemma
- **Hugging Face Transformers**: https://huggingface.co/transformers/

All rights belong to their respective authors.

If you wish to use or distribute this project, please contact the author.
