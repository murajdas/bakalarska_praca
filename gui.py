import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wordnet import NetworkAnalyzer

LANGUAGES = ['german', 'english', 'dutch', 'spanish', 'italian', 'portuguese']

class GraphManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.current_fig = None
        self.current_canvas = None

    def clear(self):
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()
        self.current_canvas = None
        self.current_fig = None

    def display(self, fig):
        self.clear()
        self.current_fig = fig
        self.current_canvas = FigureCanvasTkAgg(fig, master=self.parent_frame)
        self.current_canvas.draw()
        self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_current_plot(self, filename):
        if self.current_fig:
            self.current_fig.savefig(filename, dpi=300, bbox_inches='tight')


class WordNetworkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WordNetwork Analyzer of Kafka's Metamorphosis")
        self.root.geometry("1100x850")
        self.analyzer = NetworkAnalyzer()
        self.processor = None
        self.current_lang = tk.StringVar(value="german")
        self.with_punct = tk.BooleanVar(value=False)
        self.lemmatize = tk.BooleanVar(value=False)
        self.top_n = tk.IntVar(value=10)
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)

        self._build_controls(main_frame)
        self._build_right_panel(main_frame)
        self._show_welcome()

    def _build_controls(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        control_frame.columnconfigure(1, weight=1)

        ttk.Label(control_frame, text="Language:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(control_frame, textvariable=self.current_lang, values=LANGUAGES,
                     state='readonly', width=15).grid(row=0, column=1, pady=5, padx=5, sticky="w")

        ttk.Checkbutton(control_frame, text="Include punctuation", variable=self.with_punct).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(control_frame, text="Lemmatize", variable=self.lemmatize).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Button(control_frame, text="Load text", command=self.load_text).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Separator(control_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(control_frame, text="n:").grid(row=5, column=0, sticky="w", pady=5)
        ttk.Spinbox(control_frame, from_=1, to=100, textvariable=self.top_n, width=8).grid(row=5, column=1, sticky="w", pady=5, padx=5)

        buttons = [
            ("Top n-words by frequency", self.show_top_words),
            ("Top n-words by degree", self.show_top_degree),
            ("Network statistics", self.show_stats),
            ("Punctuation stats", self.show_punctuation),
            ("Zipf's law", self.show_zipf),
            ("Degree distribution", self.show_degree_dist),
            ("Heap's law", self.show_heaps),
            ("Export edges", self.export_edges),
            ("Save graph", self.save_current_plot),
        ]

        row = 6
        for text, cmd in buttons:
            ttk.Button(control_frame, text=text, command=cmd).grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
            row += 1

    def _build_right_panel(self, parent):
        right_panel = ttk.Frame(parent)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)

        output_frame = ttk.LabelFrame(right_panel, text="Output", padding="10")
        output_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        output_frame.columnconfigure(0, weight=1)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, width=60, height=12, font=('Courier', 10))
        self.output_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        graph_frame = ttk.LabelFrame(right_panel, text="Graph View", padding="10")
        graph_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)

        self.graph_canvas_frame = ttk.Frame(graph_frame)
        self.graph_canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.graph_manager = GraphManager(self.graph_canvas_frame)

    def set_output(self, text: str):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)

    def is_loaded(self):
        if self.processor is None:
            messagebox.showwarning("Warning", "Please load a text first!")
            return False
        return True

    def _show_welcome(self):
        self.set_output(
            "Welcome to WordNetwork Analyzer of Kafka's Metamorphosis!\n"
            + "=" * 50 + "\n"
            + "1. Select language\n2. Choose options\n3. Click 'Load text'\n4. Run analyses\n"
        )

    def load_text(self):
        try:
            self.set_output("Loading models and processing text...\n")
            self.root.update_idletasks()
            self.analyzer.load(lang=self.current_lang.get(), with_punctuation=self.with_punct.get(), lemmatize=self.lemmatize.get())
            self.processor = self.analyzer.processor
            graph = self.analyzer.graph
            self.set_output(
                f"Successfully loaded {self.current_lang.get().upper()} text!\n"
                + "=" * 50 + "\n"
                + f"Unique words: {graph.number_of_nodes()}\n"
                + f"Edges: {graph.number_of_edges()}\n"
            )
            self.graph_manager.clear()
        except Exception as e:
            self.set_output("")
            messagebox.showerror("Error", f"Failed to load text:\n{e}")

    def show_top_words(self):
        if not self.is_loaded():
            return
        words = self.analyzer.get_top_words(self.top_n.get())
        lines = [f"Top {self.top_n.get()} Most Frequent Words:", "=" * 50]
        for i, (w, c) in enumerate(words, 1):
            lines.append(f"{i:3d}. {w:15s} - {c:5d} occurrences")
        self.set_output("\n".join(lines))

    def show_top_degree(self):
        if not self.is_loaded():
            return
        words = self.analyzer.get_top_degree_words(self.top_n.get())
        lines = [f"Top {self.top_n.get()} Words by Degree:", "=" * 50]
        for i, (w, d) in enumerate(words, 1):
            lines.append(f"{i:3d}. {w:15s} - degree: {d:4d}")
        self.set_output("\n".join(lines))

    def show_stats(self):
        if not self.is_loaded():
            return
        self.set_output("Calculating network statistics, please wait...\n")
        self.root.update_idletasks()
        stats = self.analyzer.get_network_stats()
        lines = [
            "Network Statistics:", "=" * 50,
            f"Number of nodes: {stats['nodes']}",
            f"Number of edges: {stats['edges']}",
            f"Density: {stats['density']:.6f}",
            f"Average degree: {stats['avg_degree']:.4f}",
            f"Clustering coefficient: {stats['clustering']:.4f}",
            f"Average shortest path length: {stats['avg_path_length']:.4f}"
        ]
        self.set_output("\n".join(lines))

    def show_punctuation(self):
        if not self.is_loaded():
            return
        data = self.analyzer.get_punctuation_positions()
        lines = ["Punctuation Statistics:", "=" * 50]
        if not data:
            lines.append("No punctuation marks found.")
        else:
            for rank, token, cnt in data:
                lines.append(f"{rank:3d}. {token:10s} - {cnt:5d} occurrences")
        self.set_output("\n".join(lines))

    def show_zipf(self):
        if not self.is_loaded():
            return
        fig = self.analyzer.get_zipf_plot()
        self.graph_manager.display(fig)
        self.set_output("Zipf's Law Analysis Complete!\n" + "=" * 50 + "\n"
                        + "The graph shows the rank-frequency distribution.\n"
                        + "The red dashed line represents the power-law fit.\n")

    def show_degree_dist(self):
        if not self.is_loaded():
            return
        fig = self.analyzer.get_binned_degree_plot()
        self.graph_manager.display(fig)
        self.set_output("Degree Distribution Analysis Complete!\n" + "=" * 50 + "\n"
                        + "The graph shows the probability distribution of node degrees.\n"
                        + "The red dashed line represents the power-law fit.\n")

    def show_heaps(self):
        if not self.is_loaded():
            return
        fig = self.analyzer.get_heaps_plot()
        self.graph_manager.display(fig)
        self.set_output("Heap's Law Analysis Complete!\n" + "=" * 50 + "\n"
                        + "The graph shows vocabulary growth as a function of text length.\n"
                        + "The red dashed line represents the power-law fit.\n")

    def export_edges(self):
        if not self.is_loaded():
            return
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                initialfile=f"edges_{self.current_lang.get()}.csv")
        if not filename:
            return
        try:
            self.analyzer.network.export_edges_to_csv(filename)
            messagebox.showinfo("Success", f"Edges exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{e}")

    def save_current_plot(self):
        if not self.is_loaded():
            return
        if not self.graph_manager.current_fig:
            messagebox.showwarning("Warning", "No graph to save!")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                                initialfile=f"graph_{self.current_lang.get()}.png")
        if not filename:
            return
        try:
            self.graph_manager.save_current_plot(filename)
            messagebox.showinfo("Success", f"Graph saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save graph:\n{e}")


