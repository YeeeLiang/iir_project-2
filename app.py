from flask import Flask, request, render_template, redirect
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import os
import matplotlib.pyplot as plt
import numpy as np
import random
import nltk

nltk.download('punkt')  # 下載 tokenizer 資源
nltk.download('wordnet')  # 下載 WordNet

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

lemmatizer = WordNetLemmatizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('files')
    file_results = []

    for file in files:
        if file.filename == '':
            continue  # 忽略空文件
        content = file.read().decode('utf-8')
        tokens = word_tokenize(content)
        tokens = [token for token in tokens if token.isalpha()]  # 只保留字母

        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
        line_color = f'#{random.randint(0, 0xFFFFFF):06x}'

        porter_plot_path = plot_distribution(lemmatized_tokens, 'porter', file.filename, line_color)
        lancaster_plot_path = plot_distribution(lemmatized_tokens, 'lancaster', file.filename, line_color)

        freq_dist = {}
        for word in lemmatized_tokens:
            freq_dist[word] = freq_dist.get(word, 0) + 1

        sorted_freq_dist = dict(sorted(freq_dist.items(), key=lambda item: item[1], reverse=True))
        top_words = list(sorted_freq_dist.keys())[:10]

        file_results.append({
            'filename': file.filename,
            'porter_plot': porter_plot_path,
            'lancaster_plot': lancaster_plot_path,
            'words': ', '.join(lemmatized_tokens),
            'top_words': top_words
        })

    return render_template('results.html', file_results=file_results)

def plot_distribution(words, algorithm, filename, line_color):
    freq_dist = {}
    for word in words:
        freq_dist[word] = freq_dist.get(word, 0) + 1

    sorted_freq_dist = dict(sorted(freq_dist.items(), key=lambda item: item[1], reverse=True))

    plt.figure(figsize=(10, 6))
    x_values = np.arange(len(sorted_freq_dist))
    plt.plot(x_values, sorted_freq_dist.values(), marker='o', color=line_color)

    plt.title(f'{algorithm.capitalize()} Frequency Distribution Chart - {filename}')
    plt.xlabel('Words by rank order')
    plt.ylabel('Frequency of Words')
    plt.xticks([])

    plot_filename = f'{algorithm}_{filename}.png'
    plt.tight_layout()
    plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], plot_filename))
    plt.close()

    return plot_filename

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)
