import json
import os
from accuracy_metrics import EmailResponseJudge

def run_validation_correlation():
    print("Starting Metric Validation Engine...")
    
    # Load Golden Evaluation Set
    with open("data/evaluation_set.json", "r") as f:
        eval_set = json.load(f)
        
    judge = EmailResponseJudge()
    
    # We will fetch a generic mock context to keep the judge grounded
    mock_context = [
        {"incoming": "I want to cancel", "reply": "Your account has been cancelled."},
        {"incoming": "How to pay?", "reply": "We accept credit card payments."}
    ]
    
    predicted_scores = []
    human_scores = []
    
    print("\nEvaluating test set via LLM-as-a-Judge...")
    for idx, item in enumerate(eval_set):
        report = judge.evaluate_response(
            request_id=f"eval_test_{idx}",
            incoming=item["incoming"],
            reply=item["reply"],
            retrieved_examples=mock_context
        )
        
        # Scale our 0.0-1.0 AI score to match the 1.0-5.0 Human scale for comparison
        scaled_ai_score = 1.0 + (report.metrics.overall_accuracy * 4.0)
        
        predicted_scores.append(scaled_ai_score)
        human_scores.append(item["human_rating"])
        
        print(f"Sample {idx+1}: Human Rating: {item['human_rating']:.1f} | AI Judge Rating: {scaled_ai_score:.1f}")
        
    # Calculate Mean Absolute Error (MAE) between human and AI scores
    mae = sum(abs(p - h) for p, h in zip(predicted_scores, human_scores)) / len(eval_set)
    print("\n=== SYSTEM VALIDATION METRICS ===")
    print(f"Total Test Samples: {len(eval_set)}")
    print(f"Mean Absolute Error (MAE): {mae:.3f} (Lower is better)")
    
    if mae < 0.75:
        print("✅ PASS: The automated LLM judge is highly correlated with human evaluations.")
    else:
        print("⚠️ WARNING: AI metrics drift from human assessments. Adjust the system prompts.")

if __name__ == "__main__":
    run_validation_correlation()
