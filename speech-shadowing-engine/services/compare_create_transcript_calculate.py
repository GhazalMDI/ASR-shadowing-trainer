
import whisper
import tempfile
import subprocess
import os
import re
from difflib import SequenceMatcher


model = whisper.load_model("base")

def transcribe_audio(webm_bytes: bytes):
    wav_path = None
    webm_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
            f.write(webm_bytes)
            webm_path = f.name

        wav_path = webm_path.replace(".webm", ".wav")

        result = subprocess.run([
            "ffmpeg",
            "-y",
            "-i", webm_path,
            "-ar", "16000",
            "-ac", "1",
            wav_path
        ], capture_output=True, text=True)

        print("FFMPEG ERROR:", result.stderr)

        if not wav_path or not os.path.exists(wav_path):
            print("WAV NOT CREATED")
            return ""

        if os.path.getsize(wav_path) < 1000:
            print("WAV TOO SMALL")
            return ""

        result = model.transcribe(
            wav_path,
            language="en",
            fp16=False,
            no_speech_threshold=0.6,     
            logprob_threshold=-1.0,        
            condition_on_previous_text=False)
        if result.get("segments"):
            avg_logprob = result["segments"][0].get("avg_logprob", -1)
            if avg_logprob < -1.0:
                return ""

        text = result.get("text", "")
        print("TRANSCRIPT:", text)

        return text

    except Exception as e:
        print("TRANSCRIPTION FAILED:", str(e))
        return ""

    finally:
        try:
            if webm_path and os.path.exists(webm_path):
                os.remove(webm_path)
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except:
            pass

    
def parse_transcript(transcript_text):
    pattern = r'\[(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)\]\s+(.*?)(?=\[|$)'
    matches = re.findall(pattern,transcript_text,re.DOTALL)
    
    chunks = []
    for start_str,end_str,text in matches:
        chunks.append({
            "start":parse_time(start_str),
            "end":parse_time(end_str),
            "text":text.strip()
        })
    return chunks
    
def parse_time(t):
    h,m,s = t.split(":")
    return float(h) * 3600 + float(m) * 60 + float(s)
        
def get_expected_text(chunks,play_start,play_end):
    words = []
    for chunk in chunks:
        if chunk["start"] < play_end and chunk['end']>play_start:
            words.extend(chunk["text"].lower().split())
        elif chunk["start"] >= play_end:
            break
    return words
    
    
def compare(expected_words,user_text):
    if not user_text or not user_text.strip():
        return {
            "expected": expected_words,
            "got": [],
            "missed": len(expected_words),
            "score": 0.0
        }
    got = user_text.lower().split()
    
    matcher = SequenceMatcher(None,expected_words,got)
    matched = sum(b.size for b in matcher.get_matching_blocks())
    missed_count = max(0,len(expected_words) - matched)
    score = min(matched / len(expected_words), 1.0) if expected_words else 1.0
    
    return {
        "expected": expected_words,
        "got":got,
        "missed":missed_count,
        "score":round(score* 100,1)
    }