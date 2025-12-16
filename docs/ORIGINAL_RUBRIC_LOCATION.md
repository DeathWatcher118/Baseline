# Original Judging Rubric File

## Project Location

✅ **The original judging rubric PDF has been copied to:**
```
docs/2025-CCIBT-GenAI-Hackathon-Judging-Rubric.pdf
```

## Source File Location

Original file was located at:
```
C:/Users/Brian Onstot/Downloads/2025 CCIBT GenAI Hackathon Judging Rubric.pdf
```

## Manual Copy Command

### Windows PowerShell
```powershell
Copy-Item "C:\Users\Brian Onstot\Downloads\2025 CCIBT GenAI Hackathon Judging Rubric.pdf" `
  -Destination "d:\Hackathon\docs\2025-CCIBT-GenAI-Hackathon-Judging-Rubric.pdf"
```

### Windows Command Prompt
```cmd
copy "C:\Users\Brian Onstot\Downloads\2025 CCIBT GenAI Hackathon Judging Rubric.pdf" ^
  "d:\Hackathon\docs\2025-CCIBT-GenAI-Hackathon-Judging-Rubric.pdf"
```

## Alternative: Switch to Code Mode

To copy the file programmatically, switch to Code mode and run:

```python
import shutil

source = r"C:\Users\Brian Onstot\Downloads\2025 CCIBT GenAI Hackathon Judging Rubric.pdf"
destination = r"d:\Hackathon\docs\2025-CCIBT-GenAI-Hackathon-Judging-Rubric.pdf"

shutil.copy2(source, destination)
print(f"Copied to: {destination}")
```

## Documentation

The rubric has been analyzed and documented in:
- [`docs/JUDGING_RUBRIC.md`](JUDGING_RUBRIC.md) - Detailed analysis with scoring strategy

---

**Note**: After copying, add the PDF to `.gitignore` if you don't want to commit it to version control, or commit it if you want it in the repository for team reference.