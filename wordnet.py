import os
import string
from collections import Counter
from matplotlib.figure import Figure
import numpy as np
from scipy.stats import linregress
import powerlaw
import spacy
import networkx as nx

class TextProcessor:
    LANG_CONFIG = {
        'english':   {'model': 'en_core_web_trf', 'folder': 'EN', 'basename': 'Metamorphosis'},
        'italian':   {'model': 'it_core_news_lg', 'folder': 'IT', 'basename': 'La metamorfosi'},
        'portuguese':{'model': 'pt_core_news_lg', 'folder': 'PT', 'basename': 'A metamorfose'},
        'spanish':   {'model': 'es_dep_news_trf', 'folder': 'ES', 'basename': 'La metamorfosis'},
        'german':    {'model': 'de_dep_news_trf', 'folder': 'DE', 'basename': 'Die Verwandlung'},
        'dutch':     {'model': 'nl_core_news_lg', 'folder': 'NT', 'basename': 'De gedaanteverwisseling'},
    }

    def __init__(self, lang: str, lemmatize: bool = False, with_punctuation: bool = False, path: str = "."):
        if lang not in self.LANG_CONFIG:
            raise ValueError(f"Unsupported language: {lang}")
        
        self.lang = lang
        self.lemmatize = lemmatize
        self.with_punctuation = with_punctuation

        self.config = self.LANG_CONFIG[lang]
        self.punct = set(string.punctuation) | {'...'}

        self.source_path = os.path.join(path, self.config['folder'], self.config['basename'] + self._resolve_suffix())
        
        self.nlp = spacy.load(self.config['model'])
        self.text = self._load_text()
        self.doc = self.nlp(self.text, disable=['ner', 'parser'])
        self.tokens = self._tokenize()

    def _resolve_suffix(self) -> str:
        if self.lang in ['italian', 'portuguese'] and self.lemmatize:
            return ' - lemmatization.txt'
        return ' - modified.txt'
    
    def _load_text(self) -> str:
        with open(self.source_path, 'r', encoding='utf-8') as file:
            return file.read().lower()

    def _tokenize(self) -> list[str]:
        tokens = []

        for token in self.doc:
            if token.is_space:
                continue
            if not self.with_punctuation and token.is_punct:
                continue
            if not self.lemmatize:
                tokens.append(token.text)
                continue

            if token.is_punct or token.text in self.punct:
                tokens.append(token.text)
            else:
                tokens.extend(token.lemma_.split())

        return tokens
        
    def most_common_words(self, top_n: int = None) -> list[tuple[str, int]]:
        counter = Counter(self.tokens)
        if top_n is None:
            return counter.most_common()
        return counter.most_common(top_n)
    
    def get_punctuation_set(self) -> set[str]:
        return {token for token in self.tokens if token in self.punct}
    
    def punctuation_positions(self) -> list[tuple[int, str, int]]:
        positions = []
        for rank, (token, count) in enumerate(self.most_common_words(), start=1):
            if token in self.punct:
                positions.append((rank, token, count))
        return positions
    
class NetworkBuilder:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        edges = zip(self.tokens[:-1], self.tokens[1:])
        self.graph.add_edges_from(edges)
        
    def network_stats(self) -> dict:
        n = self.graph.number_of_nodes()
        e = self.graph.number_of_edges()

        return {
            'nodes': n,
            'edges': e,
            'density': nx.density(self.graph),
            'avg_degree': 2 * e / n,
            'clustering': nx.average_clustering(self.graph),
            'avg_path_length': nx.average_shortest_path_length(self.graph)
        }
    
    def top_degree_words(self, top_n: int = 10) -> list[tuple[str, int]]:
        return sorted(self.graph.degree(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def export_edges_to_csv(self, output_path: str):
        punct = string.punctuation | {'...'}
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write("Source Target Type\n")

            for u, v in self.graph.edges():
                s = f"'{u}'" if u in punct else u
                t = f"'{v}'" if v in punct else v
                file.write(f"{s} {t} Undirected\n")

class AppliedStatistics:
    def __init__(self, processor: TextProcessor, network: NetworkBuilder):
        self.processor = processor
        self.network = network
    
    def zipf_law(self) -> Figure:
        min_rank = 10
        frequency = self.processor.most_common_words()
        ranks = np.arange(1, len(frequency) + 1)
        _, counts = zip(*frequency)
        probabilities = np.array(counts) / sum(counts)

        mask = ranks >= min_rank
        alpha, intercept, _, _, _ = linregress(np.log(ranks[mask]), np.log(probabilities[mask]))
        
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.scatter(ranks[mask], probabilities[mask], color='black', s=10, zorder=2)
        ax.scatter(ranks[~mask], probabilities[~mask], color='grey', s=10, zorder=2)
        ax.plot(ranks, np.exp(intercept) * ranks ** alpha, color='red', label=f'α={-alpha:.3f}', zorder=4, linewidth=1.5, linestyle='--')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('R')
        ax.set_ylabel('P(R)')
        ax.grid(True, which="major", ls="-", alpha=0.3)
        ax.set_title(F"Zipf's Law - {self.processor.lang.capitalize()}", fontsize=14)
        ax.legend(fontsize=12)        
        return fig
    
    def binned_degree_distribution(self) -> Figure:
        bins=20
        degrees = np.array([d for _, d in self.network.graph.degree()])
        fit = powerlaw.Fit(degrees, discrete=True, verbose=False)
        gamma = fit.alpha        
        xmin = fit.xmin
        
        bin_edges = np.logspace(np.log10(min(degrees)), np.log10(max(degrees)), num=bins + 1)
        counts, _ = np.histogram(degrees, bins=bin_edges)
        b_ks = np.sqrt(bin_edges[:-1] * bin_edges[1:])[counts > 0]
        b_probs = ((counts / len(degrees)) / np.diff(bin_edges))[counts > 0]
        
        mask = b_ks >= xmin
        log_k = np.log(b_ks[mask])
        log_p = np.log(b_probs[mask])
        intercept = np.mean(log_p + gamma * log_k)
        
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.scatter(b_ks, b_probs, color='black', s=20, zorder=2)
        ax.plot(b_ks, np.exp(intercept) * b_ks ** -gamma, color='red', label=f'γ = {gamma:.3f}\nx_min = {round(xmin)}', zorder=4, linewidth=1.5, linestyle='--')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('k')
        ax.set_ylabel('P(k)')
        ax.grid(True, which="major", ls="-", alpha=0.3)
        ax.set_title(f"Degree Distribution - {self.processor.lang.capitalize()}", fontsize=14)
        ax.legend(fontsize=12)
                
        return fig
    
    def heaps_law(self) -> Figure:
        total_tokens = []
        unique_tokens = []
        seen = set()
        
        for i, token in enumerate(self.processor.tokens):
            seen.add(token)
            total_tokens.append(i + 1)
            unique_tokens.append(len(seen))
        
        L = np.array(total_tokens)
        V = np.array(unique_tokens)
        
        beta, intercept, _, _, _ = linregress(np.log(L), np.log(V))
        
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(L, V, color='black', linewidth=1, zorder=2)
        ax.plot(L, np.exp(intercept) * L ** beta, color='red', 
                label=f'β = {beta:.3f}', linewidth=1.5, linestyle='--', zorder=3)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('L')
        ax.set_ylabel('V(L)')
        ax.grid(True, which="major", ls="-", alpha=0.3)
        ax.set_title(f"Heaps' Law - {self.processor.lang.capitalize()}", fontsize=14)
        ax.legend(fontsize=12)
        
        return fig
    
class NetworkAnalyzer:
    def __init__(self):
        self.processor = None
        self.network = None
        self.analyzer = None

    def load(self, lang: str, with_punctuation: bool, lemmatize: bool):
        self.processor = TextProcessor(lang=lang, with_punctuation=with_punctuation, lemmatize=lemmatize)
        self.network = NetworkBuilder(self.processor.tokens)
        self.analyzer = AppliedStatistics(self.processor, self.network)

    def get_top_words(self, n: int):
        return self.processor.most_common_words(n)

    def get_top_degree_words(self, n: int):
        return self.network.top_degree_words(n)

    def get_network_stats(self):
        return self.network.network_stats()

    def get_punctuation_positions(self):
        return self.processor.punctuation_positions()

    def get_zipf_plot(self):
        return self.analyzer.zipf_law()

    def get_binned_degree_plot(self):
        return self.analyzer.binned_degree_distribution()
    
    def get_heaps_plot(self):
        return self.analyzer.heaps_law()

    @property
    def graph(self):
        return self.network.graph
