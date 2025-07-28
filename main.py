import os
import csv
from dotenv import load_dotenv
from typing import TypedDict

# LangGraph + LLM setup
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq

# Embedding + Vectorstore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# -------------------- ENV + LLM SETUP --------------------
load_dotenv()
llm = ChatGroq(model="llama3-8b-8192")

# -------------------- USER INPUT --------------------
def input_ticket():
    print("\n🎟️ Enter Support Ticket Details")
    subject = input("Subject: ")
    description = input("Description: ")
    return {"subject": subject, "description": description, "attempts": 0}

# -------------------- EMBEDDING + VECTOR STORE --------------------
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

category_docs = ["billing", "technical", "security", "general"]
all_texts = []
metadatas = []

for category in category_docs:
    path = f"data/{category}_docs.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            text = file.read().strip()
            if text:
                all_texts.append(text)
                metadatas.append({"category": category})

if not all_texts:
    raise ValueError("❌ No usable *_docs.txt files found in 'data/'.")

vectorstore = FAISS.from_texts(texts=all_texts, embedding=embedding, metadatas=metadatas)
retriever = vectorstore.as_retriever()

# -------------------- GRAPH NODES --------------------
def classify_node(state):
    subject = state["subject"]
    description = state["description"]
    prompt = f"""Classify this support issue into one category: Billing, Technical, Security, or General.

Subject: {subject}
Description: {description}"""
    category = llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
    print(f"[Classified as]: {category}")
    return {**state, "category": category}

def retrieve_node(state):
    query = f"{state['description']} {state['category']}"
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant documents found."
    return {**state, "context": context}

def draft_node(state):
    prompt = f"""Write a short and helpful customer support response (3–4 lines max) based on the following info:

Subject: {state['subject']}
Description: {state['description']}
Context:
{state['context']}

Be polite but avoid unnecessary details. Focus only on the solution."""
    draft = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    print(f"\n[Draft]:\n{draft}")
    return {**state, "draft": draft}

def review_node(state):
    prompt = f"""You are a support quality checker. Review this draft:

Draft:
{state['draft']}

If it's good, respond with 'Approved'. If not, respond with 'Rejected: <reason>'."""
    feedback = llm.invoke([HumanMessage(content=prompt)]).content
    attempts = state.get("attempts", 0)

    if "Approved" in feedback:
        print("[Review]: Approved ✅")
        return {**state, "review_feedback": feedback, "__condition__": "approved"}
    elif attempts >= 1:
        print("[Review]: Rejected Twice ❌")
        return {**state, "review_feedback": feedback, "attempts": attempts + 1, "__condition__": "failed"}
    else:
        print("[Review]: Rejected. Retrying 🔁")
        return {**state, "review_feedback": feedback, "attempts": attempts + 1, "__condition__": "retry"}

def escalate_node(state):
    with open("escalation_log.csv", "a", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            state["subject"],
            state["description"],
            state["draft"],
            state["review_feedback"]
        ])
    print("[Escalated] Ticket added to escalation_log.csv")
    return state

# -------------------- STATE TYPE --------------------
class TicketState(TypedDict, total=False):
    subject: str
    description: str
    attempts: int
    category: str
    context: str
    draft: str
    review_feedback: str

# -------------------- GRAPH BUILD --------------------
print("\n🚀 Running support ticket pipeline...")

builder = StateGraph(TicketState)
builder.add_node("classify", RunnableLambda(classify_node))
builder.add_node("retrieve", RunnableLambda(retrieve_node))
builder.add_node("draft", RunnableLambda(draft_node))
builder.add_node("review", RunnableLambda(review_node))
builder.add_node("escalate", RunnableLambda(escalate_node))

builder.set_entry_point("classify")
builder.add_edge("classify", "retrieve")
builder.add_edge("retrieve", "draft")
builder.add_edge("draft", "review")

builder.add_conditional_edges("review", {
    "approved": RunnableLambda(lambda x: END),
    "retry": RunnableLambda(retrieve_node),
    "failed": RunnableLambda(escalate_node)
})

# -------------------- RUN GRAPH --------------------
graph = builder.compile()
initial_state = input_ticket()
final_state = graph.invoke(initial_state)

print("\n✅ Ticket Summary")
print(f"🎯 Subject: {final_state.get('subject', 'N/A')}")
print(f"🧭 Category: {final_state.get('category', 'N/A')}")
print(f"\n💬 Support Reply:\n{final_state.get('draft', 'No reply generated.')}")
print(f"\n📝 Feedback: {final_state.get('review_feedback', 'No feedback.')}")
print(f"\n📊 Attempts: {final_state.get('attempts', 0)}")
print("\n🚀 Pipeline completed successfully!")