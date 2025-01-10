---
layout: page
title: Visualizing Information Retrieval - A TF-IDF Approach with TileBars
description: This article explores a TF-IDF-based visual query system using TileBars to retrieve and rank research documents efficiently. By leveraging metadata and the first three paragraphs of each document, it combines preprocessing, normalization, and intuitive visualizations to present relevant results. Future improvements, including lemmatization and sparse matrices, are also discussed.
img: https://images.unsplash.com/photo-1554906493-4812e307243d?q=80&w=1972&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D
importance: 2
category: work

---

**Information Retrieval and Visualization Using TF-IDF**

Efficient retrieval and ranking of research documents are critical in making vast repositories of information accessible and actionable. This article demonstrates a visual query system using TileBars to present results in a user-friendly and intuitive format. The system leverages the first three paragraphs of each research document to construct the dataset. Each row in the document store represents a single line of text derived from these paragraphs. Metadata, such as the document ID (docid), title, text, token count, category, and line ID (lineid), provides structured information for each line.

**Dataset Structure and Preprocessing**

The dataset comprises individual rows for each line of the document's initial section, allowing for fine-grained analysis. For example, the MATLAB article is divided into three lines, each corresponding to one paragraph. Metadata fields, such as tokencount, indicate the number of tokens in the line, and category identifies the broader topic. This preprocessing ensures that data is well-organized for querying and visualization.

**Implementation Details**

TF-IDF (Term Frequency-Inverse Document Frequency) is the backbone of this query system. The algorithm measures the relevance of terms to a document while mitigating the effects of commonly used words. It ensures that words frequent within a single document but rare across multiple documents receive high scores, reducing the influence of techniques like keyword stuffing often used in search engine optimization scams. For example, if a document artificially inflates keyword frequencies, TF-IDF penalizes this by accounting for term ubiquity across the corpus.

Inspired by Ted Mei's "Demystifying TF-IDF in Indexing and Ranking," I constructed a framework to compute TF-IDF scores and rank documents based on cosine similarity between the query and document vectors. This approach enhances the relevance and context of the results. To normalize the influence of document length, z-score normalization is applied, which adjusts term counts based on their mean and standard deviation within the corpus. This ensures that shorter documents are not unfairly penalized while maintaining the robustness of the ranking mechanism.

![tilebar_demo](https://github.com/godot107/godot107.github.io/blob/main/assets/img/tf_idf_gif.gif)


**Visualization**

The visualization uses TileBars, where each column represents a text paragraph, and rows represent the query terms. Tooltips provide details about term occurrences, counts, and line IDs, enhancing interactivity. This gradient-based visualization ensures that even documents with low term counts can be meaningfully represented. The tool allows users to gain insights at a glance while offering the granularity needed for deeper exploration.

![tilebar](https://github.com/godot107/godot107.github.io/blob/main/assets/img/tf_idf_demo_img.png)


**Notebook**
[View Interactive Colab Notebook](https://colab.research.google.com/drive/1ffjWWK-XXGChGaaE4gx71aSNWl8GuOs2#scrollTo=3P6JpjlIw_Tp)

<a href = "https://github.com/godot107/tf-idf-app">Source Code</a>

**Future Improvements**

While the current implementation is effective, there is potential for enhancement. Incorporating lemmatization could improve term matching by reducing inflected forms of words to their base forms. However, this would increase runtime. Switching to sparse matrices for representing TF-IDF scores would also improve memory efficiency, enabling the system to scale better for larger datasets.

Resources

<a href = "https://stackoverflow.com/questions/58988394/count-number-of-elements-in-string-in-pandas-cell">Count Number of Elements in String in Pandas Cell</a>

<a href = "https://stackoverflow.com/questions/39173992/drop-all-data-in-a-pandas-dataframe">Drop All Data in a Pandas DataFrame</a>

<a href = "https://www.geeksforgeeks.org/tf-idf-model-for-page-ranking/">TF-IDF Model for Page Ranking</a>

<a href = "https://ted-mei.medium.com/demystify-tf-idf-in-indexing-and-ranking-5c3ae88c3fa0">Demystify TF-IDF in Indexing and Ranking by Ted Mei</a>

<a href = "https://stackoverflow.com/questions/27298178/concatenate-strings-from-several-rows-using-pandas-groupby">Concatenate Strings from Several Rows Using Pandas GroupBy</a>

