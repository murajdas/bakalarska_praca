# WordNetwork Analyzer of Kafka's Metamorphosis
Tento program analyzuje slovné siete v diele Franza Kafku *Premena (Die Verwandlung)* v šiestich jazykoch: nemčina, angličtina, holandčina, španielčina, taliančina a portugalčina.

## Požiadavky
- Python 3.8 alebo novší
- Stiahnuť knižnice uvedené v `requirements.txt`
```bash
pip install -r requirements.txt
```
- inštalovať jazykové modely pre 'spaCy' (osobitne)
```bash
python -m spacy download en_core_web_trf 
```
```bash
python -m spacy download de_dep_news_trf 
```
```bash
python -m spacy download nl_core_news_lg 
```
```bash
python -m spacy download es_dep_news_trf 
```
```bash
python -m spacy download it_core_news_lg 
```
```bash
python -m spacy download pt_core_news_lg 
```
    
