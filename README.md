# Support Ticket Resolution Agent with Multi-Step Review Loop (LangGraph + RAG)

---

## 🧠 Project Summary

This is a support ticket resolution agent that:

* Takes **live user input** for support issues
* Uses **LangGraph** to define a multi-step process:

  * Classify the issue
  * Retrieve relevant documents
  * Draft a support reply
  * Auto-review the reply (loop if rejected)
  * Escalate if necessary
* Integrates **RAG (Retrieval-Augmented Generation)** to ground replies using support documents.

---

## ✅ Features Checklist

| Feature                              | Status |
| ------------------------------------ | ------ |
| Live user input                      | ✅      |
| LangGraph multi-step state machine   | ✅      |
| Issue classification (Billing, etc.) | ✅      |
| Retrieval-Augmented Generation (RAG) | ✅      |
| Short, helpful support reply         | ✅      |
| LLM-based review with retry loop     | ✅      |
| Escalation logged to CSV             | ✅      |
| Clean and readable final output      | ✅      |

---

## 🏗️ Project Structure

```
STRA/
├── main.py                  # Main pipeline
├── data/                    # Support policy documents
│   ├── billing_docs.txt
│   ├── technical_docs.txt
│   ├── general_docs.txt
│   └── security_docs.txt
├── escalation_log.csv      # Escalation record log (auto-created)
├── .env                    # Contains GROQ_API_KEY
└── README.md             
```

---

## ⚙️ Setup Instructions

### 1. Install dependencies:

```bash
pip install -r requirements.txt
```

Use this if you don’t have a `requirements.txt`:

```bash
pip install langgraph langchain langchain-community langchain-core langchain-huggingface langchain-groq faiss-cpu python-dotenv
```

### 2. Create `.env` file:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Add your support documents

Put text files inside the `/data` folder:

* `billing_docs.txt`
* `technical_docs.txt`
* `general_docs.txt`
* `security_docs.txt`

Each file should contain bullet points with issues, policies, keywords, and troubleshooting steps.

---

## 🚀 How to Run

```bash
python main.py
```

You will be prompted for:

```
Subject: Refund failed
Description: I cancelled my subscription but got charged again.
```

The system will:

1. Classify the issue
2. Retrieve relevant policies from your docs
3. Draft a short helpful reply
4. Review it
5. Retry/rewrite if rejected
6. Escalate if needed

---

## 🔁 Example Prompts (Test Cases)

### Test 1: Billing

```
Subject: Refund failed
Description: I cancelled my subscription but got charged again.
```

### Test 2: Technical

```
Subject: App crashes
Description: Every time I open the mobile app it crashes on the login screen.
```

### Test 3: Security

```
Subject: Someone accessed my account
Description: I received an alert that someone logged into my account from an unknown location.
```

### Test 4: General

```
Subject: How to change profile picture?
Description: I'm trying to update my display picture but can't find the option.
```

---



## 🔍 main.py — Line-by-Line Summary

| Line #  | Purpose                                                          |
| ------- | ---------------------------------------------------------------- |
| 1-7     | Import required libraries                                        |
| 10-12   | Load `.env` and initialize LLM                                   |
| 14-18   | Prompt user for live input                                       |
| 21-38   | Load support policy docs and embed them                          |
| 40-95   | Define graph nodes (classify, retrieve, draft, review, escalate) |
| 98-109  | Define TicketState type                                          |
| 111-122 | Build the LangGraph pipeline and conditional review logic        |
| 125-129 | Run the pipeline and show summary                                |

---

## 🧾 Credits

Built with:

* [LangGraph](https://github.com/langchain-ai/langgraph)
* [LangChain](https://www.langchain.com/)
* [Groq](https://groq.com/) for blazing-fast LLM API
* FAISS + HuggingFace for vector search


