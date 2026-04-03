import os
import sys
import time
import json

def validate_output(path):
	if not os.path.exists(path):
		print(f"❌ Output file missing: {path}")
		return False, 0
	try:
		with open(path, 'r', encoding='utf-8') as f:
			data = json.load(f)
		if not data:
			print(f"❌ Output file empty: {path}")
			return False, 0
	except Exception as e:
		print(f"❌ Output file invalid JSON: {path} ({e})")
		return False, 0
	return True, len(data) if isinstance(data, list) else 1

PIPELINE_STEPS = [
	{"name": "Collect Data", "script": "collect_data.py", "output": "../data/raw/raw_data.json"},
	{"name": "Process Data", "script": "process_data.py", "output": "../data/processed/processed_data.json"},
	{"name": "Analyze Data", "script": "analyze_data.py", "output": "../data/processed/analysis_output.json"},
	{"name": "AI Enrichment", "script": "ai_enrichment.py", "output": "../data/processed/ai_enriched.json"},
	{"name": "Decision Engine", "script": "decision_engine.py", "output": "../data/processed/decisions.json"},
	{"name": "Execution Engine", "script": "execution_engine.py", "output": "../data/processed/execution.json"},
	{"name": "Trust Scoring", "script": "trust_scoring.py", "output": "../data/processed/trusted_data.json"},
	{"name": "Memory Engine", "script": "memory_engine.py", "output": "../data/memory/memory.json"},
	{"name": "Pattern Detection", "script": "pattern_engine.py", "output": "../data/processed/patterns.json"},
	{"name": "Strategy Engine", "script": "strategy_engine.py", "output": "../data/processed/strategy.json"},
]

print("Running Full AI Pipeline...\n")
step_times = []
for step in PIPELINE_STEPS:
	print(f"\n➡️  {step['name']}...")
	script_path = os.path.join(os.path.dirname(__file__), step['script'])
	output_path = os.path.join(os.path.dirname(__file__), step['output'])
	abs_output_path = os.path.abspath(output_path)
	print(f"[PIPELINE] CWD: {os.getcwd()}")
	print(f"[PIPELINE] Output path: {output_path}")
	print(f"[PIPELINE] Absolute output path: {abs_output_path}")
	success = False
	data_count = 0
	for attempt in range(2):
		t0 = time.time()
		exit_code = os.system(f"{sys.executable} {script_path}")
		t1 = time.time()
		step_time = t1 - t0
		if os.path.exists(abs_output_path):
			size = os.path.getsize(abs_output_path)
			with open(abs_output_path, "rb") as f:
				file_bytes = f.read()
			import hashlib
			sha = hashlib.sha256(file_bytes).hexdigest()
			print(f"[PIPELINE] Output file exists after step. Size: {size} bytes | SHA256: {sha}")
			try:
				with open(abs_output_path, "r", encoding="utf-8") as f:
					preview = f.read(200)
				print(f"[PIPELINE] Output file preview: {preview}")
			except Exception as e:
				print(f"[PIPELINE] Error reading output file for preview: {e}")
		else:
			print(f"[PIPELINE] Output file does not exist after step.")
		# File integrity check after each step
		if step['name'] != 'Collect Data' and os.path.exists(abs_output_path):
			# Check if raw_data.json changed unexpectedly
			raw_path = os.path.abspath("backend/data/raw/raw_data.json")
			if os.path.abspath(abs_output_path) == raw_path:
				print("[GUARD] UNAUTHORIZED MODIFICATION - STOPPING PIPELINE")
				exit(1)
		valid, count = validate_output(output_path)
		data_count = count
		if exit_code == 0 and valid:
			print(f"✅ {step['name']} complete in {step_time:.2f}s | Data count: {data_count}")
			step_times.append((step['name'], step_time, True, data_count))
			success = True
			break
		else:
			print(f"❌ {step['name']} failed (attempt {attempt+1}) | Data count: {data_count}")
			time.sleep(2)
	if not success:
		print(f"❌ {step['name']} failed twice. Stopping pipeline.")
		step_times.append((step['name'], step_time, False, data_count))
		break
	time.sleep(2)

print("\nFULL PIPELINE COMPLETE\n")
print("Step Results:")
for name, t, ok, count in step_times:
	print(f" - {name}: {'✅' if ok else '❌'} ({t:.2f}s) | Data count: {count}")