"""
Iteration Controller for Iterative Scoring and Feedback Loop
- Runs up to 3 iterations
- Stops early if convergence or high confidence is reached
- Applies feedback between iterations
"""
import copy
from scripts.intelligence.feedback_analyzer import FeedbackAnalyzer
from scripts.intelligence.learning_optimizer import LearningOptimizer

class IterationController:
    def __init__(self, scoring_func, pre_filter_func, trust_func, max_iterations=3, convergence_threshold=0.90):
        self.scoring_func = scoring_func
        self.pre_filter_func = pre_filter_func
        self.trust_func = trust_func
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.learning_optimizer = LearningOptimizer()
        self.feedback_analyzer = FeedbackAnalyzer()

    def run(self, raw_leads, query, intent_analysis):
        # Initial pre-filter and deduplication
        filtered_leads, _ = self.pre_filter_func(raw_leads)
        prev_scores = None
        all_outputs = []
        for iteration in range(1, self.max_iterations + 1):
            # Scoring
            scored = self.scoring_func(filtered_leads, query, intent_analysis)
            # Trust layer
            trusted = self.trust_func(scored, query)
            # Feedback analysis
            feedback = self.feedback_analyzer.analyze(trusted, trusted)
            confidences = [r.get('confidence', 0) for r in feedback['results']]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            # Attach confidence to each lead
            for i, lead in enumerate(trusted):
                lead['confidence'] = confidences[i] if i < len(confidences) else 0
            all_outputs = trusted
            # Early stopping: if all confidences > threshold, break
            if all(c >= self.convergence_threshold for c in confidences):
                break
            # Convergence: if scores have not changed significantly, break
            if prev_scores is not None:
                deltas = [abs(lead['score'] - prev) for lead, prev in zip(trusted, prev_scores)]
                if all(d < 0.01 for d in deltas):
                    break
            prev_scores = [lead['score'] for lead in trusted]
            # Feedback loop: update weights
            self.learning_optimizer.update(feedback)
        return all_outputs
