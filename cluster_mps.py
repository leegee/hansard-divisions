import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# Load saved DataFrame from Parquet file
df = pd.read_parquet("mp_vote_map.parquet")
print(f"Loaded DataFrame shape: {df.shape}")

# Optionally remove MPs with few votes (absolute sum of votes > 50)
df_filtered = df[df.abs().sum(axis=1) > 50]
print(f"Data shape after filtering MPs with >50 votes: {df_filtered.shape}")

if df_filtered.empty:
    raise ValueError("DataFrame is empty after filtering — no MPs with enough votes")

# Dimensionality reduction for visualization
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(df_filtered)

# Clustering
kmeans = KMeans(n_clusters=4, random_state=42)
labels = kmeans.fit_predict(X_reduced)

# Visualise
plt.figure(figsize=(10, 8))
sns.scatterplot(x=X_reduced[:, 0], y=X_reduced[:, 1], hue=labels, palette="tab10", legend="full")
plt.title("Clustering of MPs Based on Voting Records")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.legend(title="Cluster")
plt.grid(True)
plt.tight_layout()
plt.show()
