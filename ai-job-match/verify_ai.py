"""Optional integration check. Downloads the pretrained model on first use."""
from pathlib import Path
from analyzer.core import analyze

if __name__ == "__main__":
    root = Path(__file__).parent
    result = analyze((root / "samples/resume.txt").read_text(),
                     (root / "samples/job_description.txt").read_text(), mode="semantic")
    assert 0 <= result["text_similarity"] <= 100
    assert result["skill_coverage"] == 44.4
    print("AI integration check passed")
    for key in ["model", "text_similarity", "skill_coverage"]:
        print(f"{key}: {result[key]}")
