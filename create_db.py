"""Create a pandas DataFrame from .docx files in the `conversations/` folder.

Produces columns: case_number, age, sex, persona, mbti, attachment_style, stress_response, conversation

Usage: run this script from the project root (it will look for `conversations/` next to this file)
"""
import os
import re
from pathlib import Path
import sys
import pandas as pd

try:
	import docx
except Exception:
	raise SystemExit(
		"Missing dependency 'python-docx'. Install with: pip install python-docx"
	)


def read_docx_text(path: Path) -> str:
	doc = docx.Document(str(path))
	paragraphs = [p.text for p in doc.paragraphs]
	# Join with newlines to preserve simple structure
	return "\n".join(paragraphs)


def parse_case_text(text: str) -> dict:
	# Normalize newlines and split into lines
	lines = [ln.strip() for ln in text.splitlines()]
	lines = [ln for ln in lines if ln != ""]

	out = {
		"case_number": None,
		"age": None,
		"sex": None,
		"persona": None,
		"mbti": None,
		"attachment_style": None,
		"stress_response": None,
		"conversation": None,
	}

	if not lines:
		return out

	# Case number (first line like 'CASE 1')
	first = lines[0]
	m = re.search(r"CASE\s*(\d+)", first, re.IGNORECASE)
	if m:
		out["case_number"] = int(m.group(1))

	# Second line usually contains age/sex/persona/mbti
	if len(lines) >= 2:
		second = lines[1]
		parts = [p.strip() for p in second.split("|")]
		# First part typically contains age and sex like '19-year-old woman'
		if parts:
			age_sex = parts[0]
			age_m = re.search(r"(\d{1,3})", age_sex)
			if age_m:
				out["age"] = int(age_m.group(1))
			sex_l = age_sex.lower()
			if "woman" in sex_l or "female" in sex_l:
				out["sex"] = "woman"
			elif "man" in sex_l or "male" in sex_l:
				out["sex"] = "man"
			else:
				# attempt to find gender words anywhere in the parts
				for p in parts:
					if "woman" in p.lower() or "female" in p.lower():
						out["sex"] = "woman"
						break
					if "man" in p.lower() or "male" in p.lower():
						out["sex"] = "man"
						break

		# MBTI often appears as a 4-letter code in one of the parts
		mbti = None
		for p in parts[::-1]:
			p_stripped = p.replace(" ", "")
			if re.fullmatch(r"[A-Z]{4}", p_stripped):
				mbti = p_stripped
				break
		out["mbti"] = mbti

		# Persona: join parts except the first (age/sex) and except MBTI
		persona_parts = []
		for p in parts[1:]:
			if p == mbti:
				continue
			persona_parts.append(p)
		out["persona"] = " | ".join(persona_parts) if persona_parts else None

	# Search for Attachment and Stress response lines anywhere
	for ln in lines:
		if ln.lower().startswith("attachment:"):
			out["attachment_style"] = ln.split(":", 1)[1].strip()
		if ln.lower().startswith("stress response:") or ln.lower().startswith("stress-response:"):
			out["stress_response"] = ln.split(":", 1)[1].strip()

	# Conversation: text after 'Chatbot:' if present, otherwise remaining lines after header block
	convo = None
	join_text = "\n".join(lines)
	# Try to find 'Chatbot:' marker (case-insensitive)
	m_chat = re.search(r"Chatbot:\s*(.*)", join_text, re.IGNORECASE | re.DOTALL)
	if m_chat:
		# conversation starts at the Chatbot: label position
		start = m_chat.start()
		convo = join_text[start:]
	else:
		# fallback: find the first blank line after the lines we've already parsed (we removed blanks)
		# So take everything after the stress/attachment lines if present
		# Heuristic: find index of line that starts with 'Chatbot' or first line that contains 'User:'
		idx = None
		for i, ln in enumerate(lines):
			if ln.lower().startswith("chatbot:") or ln.lower().startswith("user:"):
				idx = i
				break
		if idx is not None:
			convo = "\n".join(lines[idx:])
		else:
			# last resort: everything after line 1
			if len(lines) > 2:
				convo = "\n".join(lines[2:])

	out["conversation"] = convo

	return out


def build_dataframe(folder: Path) -> pd.DataFrame:
	rows = []
	for fp in sorted(folder.glob("*.docx")):
		try:
			text = read_docx_text(fp)
		except Exception as e:
			print(f"Warning: failed to read {fp}: {e}")
			continue
		parsed = parse_case_text(text)
		parsed["source_file"] = fp.name
		rows.append(parsed)

	df = pd.DataFrame(rows)
	# Reorder columns to match requested output
	cols = [
		"case_number",
		"age",
		"sex",
		"persona",
		"mbti",
		"attachment_style",
		"stress_response",
		"conversation",
		"source_file",
	]
	# Keep only existing cols
	cols = [c for c in cols if c in df.columns]
	return df[cols]


def main():
	base = Path(__file__).resolve().parent
	conv_folder = base / "conversations"
	if len(sys.argv) > 1:
		conv_folder = Path(sys.argv[1])

	if not conv_folder.exists():
		print(f"Conversations folder not found: {conv_folder}")
		raise SystemExit(1)

	df = build_dataframe(conv_folder)
	out_csv = base / "conversations_summary.csv"
	df.to_csv(out_csv, index=False)
	print(f"Wrote {out_csv} ({len(df)} rows)")
	print(df.head(10).to_string(index=False))


if __name__ == "__main__":
	main()

