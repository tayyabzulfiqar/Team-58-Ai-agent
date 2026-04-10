import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools.report_generator import report_generator

mock_data = {
    "scoring": {
        "top": {"title": "conversion optimization", "score": 7},
        "validated_opportunities": [{"title": "checkout friction"}, {"title": "weak offer clarity"}],
    },
    "decision": {"decision": "conversion optimization"},
    "execution": {
        "steps": ["Fix checkout flow", "Improve offer clarity"],
        "platforms": ["facebook", "instagram"],
    },
}

result = report_generator(mock_data)

print(json.dumps(result, indent=2))
