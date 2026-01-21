"""
Download required NLTK data
"""
import nltk

print("📥 Downloading NLTK data...")

try:
    nltk.download('punkt', quiet=True)
    print("✅ Downloaded punkt")
except Exception as e:
    print(f"❌ Error downloading punkt: {e}")

try:
    nltk.download('stopwords', quiet=True)
    print("✅ Downloaded stopwords")
except Exception as e:
    print(f"❌ Error downloading stopwords: {e}")

print("✅ NLTK data download complete!")

