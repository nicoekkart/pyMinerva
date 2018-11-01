# pyMinerva

1. Install dependencies `pip install -r requirements.txt`
2. Create a secrets.py file in the minerva folder containing your minerva credentials:
```python
username = ""
password = ""
```
3. Adapt the file minerva/example_programs/synced_map.py to contain your courses. The key is a search string for the title of a course. The value is the folder where it should end up.
4. Run using `python -m example_programs.sync_files` in the minerva folder.
