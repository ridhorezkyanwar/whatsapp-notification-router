# Code package

The local review interface is `app.py`; the batch classifier is `main.py`.

From the repository root, install `code/requirements.txt`, set `GROQ_API_KEY`, then run:

```powershell
python -m streamlit run code/app.py
```

For batch mode, run `python code/main.py`. Full setup, output schema, and limitations are documented in the [repository README](../README.md).
