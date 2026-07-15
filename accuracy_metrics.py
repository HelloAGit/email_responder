import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from accuracy_schemas import ResponseEvaluationReport

load_dotenv()

class EmailResponseJudge:
    def __init__(self):
        # We use a fast, cost-efficient model as our judge
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        self.structured_llm = self.llm.with_structured_output(ResponseEvaluationReport)

    def evaluate_response(self, request_id: str, incoming: str, reply: str, retrieved_examples: list) -> ResponseEvaluationReport:
        # Format the retrieved RAG contexts for the judge to inspect
        formatted_examples = ""
        for idx, item in enumerate(retrieved_examples):
            formatted_examples += f"Example {idx+1} (Incoming): {item.get('incoming', '')}\n"
            formatted_examples += f"Example {idx+1} (Past Reply): {item.get('reply', '')}\n\n"

        judge_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an impartial, highly critical Quality Assurance auditor for a customer service division.\n"
                "Your job is to run a deep evaluation of a generated draft reply against an incoming customer email "
                "and reference brand guidelines (demonstrated in the provided Past Examples).\n\n"
                "Review these strict grading rubrics:\n"
                "1. Semantic Coherence: Does it resolve the precise issue asked? Or is it generalized fluff?\n"
                "2. Tone Consistency: Does it sound like the examples? (e.g., professional, friendly, clear)?\n"
                "3. Factual Confidence: Check for hallucinations. Does it promise things not in the examples or state unverified facts?\n"
                "4. Response Quality: Is there a polite greeting, clear body paragraphs, and a closing?\n\n"
                "You must output a structured JSON response matching the required schema. Ensure the overall_accuracy "
                "score matches your weighted calculations exactly."
            )),
            ("user", (
                "--- PAST EXAMPLES (Reference Material) ---\n"
                "{examples}\n\n"
                "--- ACTUAL TRANSACTION ---\n"
                "Incoming Customer Email: {incoming}\n"
                "Generated Draft Reply: {reply}\n\n"
                "Evaluate the Generated Draft Reply."
            ))
        ])

        # Run evaluation chain
        eval_chain = judge_prompt | self.structured_llm
        report = eval_chain.invoke({
            "examples": formatted_examples,
            "incoming": incoming,
            "reply": reply
        })

        # Inject original contextual items back to the report object for storage
        report.request_id = request_id
        report.incoming_email = incoming
        report.generated_reply = reply
        return report
