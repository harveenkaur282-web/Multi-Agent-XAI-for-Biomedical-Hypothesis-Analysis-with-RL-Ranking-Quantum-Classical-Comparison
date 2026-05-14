scipacy failed, in nlp_extractor spaCy model-en_core_web_sm is implemented and works perfectly and still extracts the necessary entities. 
the current knowlege graph made up of all the entities is saved in NetworkX node-link JSON format for now
When we r on deployment phase- then we ll make beautiful interactive web graph (using a library like pyvis or streamlit-agraph or vis.js)

update- this repository also needs acleanup as for ex knowlege graph folder is empty, so need to shift what was saved in the data folder- to knowlege graph instead, also some scripts dont seem to be working and have some errors that need to be fixed

### Identified Problems to Fix Now:
1. **Hardcoded Hypotheses**: The test block in `literature_agent.py` and `crew_manager.py` still use hardcoded strings instead of accepting dynamic user inputs.
2. **Directory Mess**: Graph output saves directly to `data/` instead of the correct `data/knowledge_graphs/` folder, leaving it empty.
3. **Generic Prompts**: CrewAI agent backstories and search queries lack domain focus and need tuning specifically for Women's Health / PCOS.
4. **Inefficient Fetching**: `biorxiv_fetcher.py` pulls all preprints from the last 60 days and filters locally, which is unoptimized and may hit rate limits.
5. **Secrets Management**: Some tools might fail in production if `.env` (API keys) isn't explicitly loaded across all agent files.