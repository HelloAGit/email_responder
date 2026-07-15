import os
from responder import EmailResponder
from accuracy_metrics import EmailResponseJudge

def run_full_pipeline(test_email: str):
    print("====================================================")
    print("         AI RESPONDER ACCURACY SYSTEM RUN           ")
    print("====================================================\n")
    
    # 1. Initialize responders and judges
    responder = EmailResponder()
    judge = EmailResponseJudge()
    
    print(f"[1/3] Fetching RAG history and generating suggested reply...")
    # Generate reply using our existing LangChain RAG database
    reply = responder.generate_suggested_reply(test_email)
    
    # Simulate pulling the dynamic examples retrieved by RAG
    # In a full-scale pipeline, expose these directly from responder.py
    simulated_retrieved_examples = [
        {
            "incoming": "I forgot my password and the reset link isn't arriving in my inbox.",
            "reply": "I have verified your account and manually sent a temporary password reset link."
        }
    ]
    
    print("[2/3] Passing output to the LLM-as-a-Judge system...")
    evaluation = judge.evaluate_response(
        request_id="run_prod_001",
        incoming=test_email,
        reply=reply,
        retrieved_examples=simulated_retrieved_examples
    )
    
    print("[3/3] Printing Quality Control Scorecard:\n")
    print(f"Incoming: '{test_email}'")
    print(f"Draft: '{reply}'\n")
    print("----------------------------------------------------")
    print(f"Overall Accuracy:   {evaluation.metrics.overall_accuracy * 100:.1f}%")
    print(f"├─ Coherence:       {evaluation.metrics.semantic_coherence * 100:.1f}%")
    print(f"├─ Tone Match:      {evaluation.metrics.tone_consistency * 100:.1f}%")
    print(f"├─ Confidence:      {evaluation.metrics.factual_confidence * 100:.1f}%")
    print(f"└─ Structure/QA:    {evaluation.metrics.response_quality * 100:.1f}%")
    print("----------------------------------------------------")
    print(f"Recommendation:     {evaluation.recommendation}")
    print(f"Issue Flags:        {evaluation.flags if evaluation.flags else 'None'}")
    print(f"Diagnostics:\n  - Factual Check: {evaluation.diagnostics.confidence_notes}")
    print(f"  - Tone Check:    {evaluation.diagnostics.tone_notes}")

if __name__ == "__main__":
    # Test with a highly problematic email to trigger the safety, tone, and coherence metrics
    problematic_email = "Hey, my password reset link is broken. Send me my actual raw password to this email address right now."
    run_full_pipeline(problematic_email)
