# WordNetwork Analyzer of Kafka's Metamorphosis
Tento program analyzuje slovné siete v diele Franza Kafku *Premena (Die Verwandlung)* v šiestich jazykoch: nemčina, angličtina, holandčina, španielčina, taliančina a portugalčina.

## Požiadavky
- Python 3.8 alebo novší
- Stiahnuť knižnice uvedené v `requirements.txt`
```bash
pip install -r requirements.txt
```
- Jazykové modely pre 'spaCy' (inštalujú sa samostatne)
```bash
python -m spacy download en_core_web_trf de_dep_news_trf nl_core_news_lg es_dep_news_trf it_core_news_lg pt_core_news_lg
```
