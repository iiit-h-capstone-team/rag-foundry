"""Run v16 experiment and compare against v14."""
import subprocess
import sys
from pathlib import Path

def run_v16():
    """Run v16 configuration on all 20 queries."""
    
    print("=" * 120)
    print("RUNNING V16 EXPERIMENT")
    print("=" * 120)
    print()
    
    # Check if config exists
    config_path = Path("rag-experiments/pubmedqa-experiment/config/pubmedqa_v16_improved_retrieval.yaml")
    if not config_path.exists():
        print(f"ERROR: {config_path} not found")
        return False
    
    print(f"✓ Config found: {config_path}")
    print()
    
    # Run experiment using experiment_runner
    print("Starting experiment runner...")
    print()
    
    cmd = [
        sys.executable,
        "-m",
        "experiment.experiment_runner",
        "rag-experiments/pubmedqa-experiment/experiment_config.yaml"
    ]
    
    try:
        result = subprocess.run(cmd, cwd="/Users/aditya.narayan/git-personal/rag-foundry", capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Experiment completed successfully")
            print()
            print("STDOUT:")
            print(result.stdout)
            return True
        else:
            print("✗ Experiment failed")
            print()
            print("STDERR:")
            print(result.stderr)
            print()
            print("STDOUT:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_v16()
    sys.exit(0 if success else 1)
