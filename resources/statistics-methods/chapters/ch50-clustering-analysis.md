# Ch50: 聚类分析与无监督学习 (Clustering Analysis)

> **适用场景**: 患者亚型发现、基因表达聚类、疾病分型、变量降维
> **核心方法**: K-means、层次聚类、DBSCAN、Gaussian Mixture
> **参考文献**: Hastie et al. (2009), Kaufman & Rousseeuw (1990)

---

## 1. 概述

聚类分析是无监督学习的核心方法，将观测分为若干组（簇），使组内相似度高、组间差异大。在医学研究中广泛用于：

- **患者亚型发现**: 疾病异质性分型（如糖尿病分型、抑郁症亚型）
- **基因表达聚类**: 样本聚类、基因共表达模块
- **影像聚类**: 病灶形态分类
- **风险分层**: 基于多维指标的患者风险分组

## 2. 主要方法

### 2.1 K-means 聚类

**原理**: 将 n 个观测分为 k 个簇，最小化簇内平方和 (WCSS)。

**优点**: 简单高效、可扩展
**缺点**: 需预设 k、对初始值敏感、假设球形簇

```r
# R: K-means
library(factoextra)
library(cluster)

# 标准化数据
df_scaled <- scale(df)

# Elbow method 选择 k
fviz_nbclust(df_scaled, kmeans, method = "wss") +
  geom_vline(xintercept = 3, linetype = 2)

# K-means 聚类
set.seed(42)
km_result <- kmeans(df_scaled, centers = 3, nstart = 25)

# 可视化
fviz_cluster(km_result, data = df_scaled, geom = "point",
             stand = FALSE, ellipse.type = "norm")

# 轮廓系数
sil <- silhouette(km_result$cluster, dist(df_scaled))
mean(sil[, 3])  # 平均轮廓宽度
```

```python
# Python: K-means
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# 标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Elbow method
inertias = []
K_range = range(2, 11)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=25)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

plt.plot(K_range, inertias, 'bo-')
plt.xlabel('k')
plt.ylabel('WCSS')
plt.title('Elbow Method')
plt.show()

# 最终聚类
km = KMeans(n_clusters=3, random_state=42, n_init=25)
labels = km.fit_predict(X_scaled)
silhouette_score(X_scaled, labels)
```

### 2.2 层次聚类

**原理**: 自底向上（凝聚）或自顶向下（分裂），生成树状图 (dendrogram)。

**优点**: 不需预设 k、树状图直观
**缺点**: 计算复杂度 O(n³)、不适合大规模数据

```r
# R: 层次聚类
hc <- hclust(dist(df_scaled), method = "ward.D2")

# 树状图
plot(hc, hang = -1, cex = 0.6)
rect.hclust(hc, k = 3, border = "red")

# 提取聚类标签
clusters <- cutree(hc, k = 3)
```

```python
# Python: 层次聚类
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

# Ward's method
Z = linkage(X_scaled, method='ward')

# 树状图
plt.figure(figsize=(10, 5))
dendrogram(Z, truncate_mode='lastp', p=30)
plt.show()

# 提取标签
labels = fcluster(Z, t=3, criterion='maxclust')
```

### 2.3 DBSCAN

**原理**: 基于密度的聚类，识别核心点、边界点和噪声点。

**优点**: 可发现任意形状簇、自动处理噪声
**缺点**: 对参数 (eps, min_samples) 敏感

```python
from sklearn.cluster import DBSCAN

db = DBSCAN(eps=0.5, min_samples=5)
labels = db.fit_predict(X_scaled)
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print(f"簇数: {n_clusters}, 噪声点: {sum(labels == -1)}")
```

## 3. 聚类评估指标

| 指标 | 类型 | 说明 | 范围 |
|------|------|------|------|
| 轮廓系数 (Silhouette) | 内部 | 簇内紧密度 vs 簇间分离度 | [-1, 1]，越大越好 |
| Gap Statistic | 内部 | 与均匀分布参考比较 | 越大越好 |
| Calinski-Harabasz | 内部 | 簇间方差/簇内方差 | 越大越好 |
| Davies-Bouldin | 内部 | 簇内距离/簇间距离 | 越小越好 |
| Adjusted Rand Index | 外部 | 与真实标签的一致性 | [-1, 1] |
| Purity | 外部 | 每个簇中主要类别的比例 | [0, 1] |

## 4. 降维可视化

```r
# R: PCA + t-SNE
library(Rtsne)
library(umap)

# PCA
pca_result <- prcomp(df_scaled)
fviz_pca_ind(pca_result, col.ind = as.factor(clusters), palette = "jco")

# t-SNE
tsne_result <- Rtsne(df_scaled, dims = 2, perplexity = 30)
plot(tsne_result$Y, col = clusters, pch = 16, main = "t-SNE")
```

```python
# Python: PCA + UMAP
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap

# PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# t-SNE
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
X_tsne = tsne.fit_transform(X_scaled)

# UMAP
reducer = umap.UMAP(random_state=42)
X_umap = reducer.fit_transform(X_scaled)
```

## 5. 医学应用示例

### 5.1 患者亚型发现

```python
# 基于多维临床指标的患者聚类
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 假设有年龄、BMI、血压、血糖、血脂等指标
clinical_vars = ['age', 'bmi', 'systolic_bp', 'fasting_glucose', 'triglycerides']
X = df[clinical_vars].dropna()
X_scaled = StandardScaler().fit_transform(X)

# 聚类
km = KMeans(n_clusters=4, random_state=42)
df['subtype'] = km.fit_predict(X_scaled)

# 亚型特征描述
df.groupby('subtype')[clinical_vars].agg(['mean', 'std'])
```

### 5.2 基因表达聚类

```r
# 使用 heatmap 可视化基因表达聚类
library(pheatmap)

# 选择差异表达基因
de_genes <- c("GENE1", "GENE2", "GENE3")  # 实际使用 DE 分析结果
expr_matrix <- as.matrix(expr_df[de_genes, ])

# 热图 + 聚类
pheatmap(expr_matrix, scale = "row",
         clustering_distance_rows = "euclidean",
         clustering_method = "ward.D2",
         show_rownames = TRUE)
```

## 6. 结果解释注意事项

- **聚类标签无内在含义**: 标签 1/2/3 仅为区分，需通过特征描述赋予临床意义
- **结果不唯一**: 不同方法、不同参数可能产生不同聚类
- **需领域知识验证**: 聚类结果必须与临床/生物学知识一致
- **样本量要求**: 每个簇应有足够样本（建议 ≥ 20）用于后续分析
- **聚类 vs 分类**: 聚类是无监督的，不能用分类指标（如准确率）评估

## 7. 常见陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| 不标准化变量 | 量纲不同导致聚类偏向高方差变量 | 先标准化 |
| 预设 k 不合理 | 选择错误的簇数 | 多种方法交叉验证 |
| 忽略缺失值 | 聚类算法不能处理缺失 | 插补或排除 |
| 过度解读 | 聚类不等于因果关系 | 仅描述性使用 |
| 样本量不足 | n < 5k 时 K-means 不稳定 | 增加 nstart 或换方法 |

## 8. 参考文献

1. Hastie T, Tibshirani R, Friedman J. The Elements of Statistical Learning. 2nd ed. Springer; 2009.
2. Kaufman L, Rousseeuw PJ. Finding Groups in Data. Wiley; 1990.
3. Tibshirani R, Walther G, Hastie T. Estimating the number of clusters in a data set via the gap statistic. J R Stat Soc B. 2001;63(2):411-423.
4. Rousseeuw PJ. Silhouettes: a graphical aid to the interpretation and validation of cluster analysis. J Comput Appl Math. 1987;20:53-65.
5. McInnes L, Healy J, Melville J. UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. arXiv:1802.03426. 2018.
