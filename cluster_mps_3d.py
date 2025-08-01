import pandas as pd
import json
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import plotly.express as px

# Load vote matrix
df = pd.read_parquet("mp_vote_map.parquet")
print(f"Loaded DataFrame shape: {df.shape}")

# Filter MPs with low participation
df_filtered = df[df.abs().sum(axis=1) > 50]
print(f"Data shape after filtering MPs with >50 votes: {df_filtered.shape}")

if df_filtered.empty:
    raise ValueError("DataFrame is empty after filtering")

# Load party and colour info
with open("mp_party.json", "r", encoding="utf-8") as f:
    party_map = json.load(f)

party_lookup = {int(k): v.get("Party", "Unknown") for k, v in party_map.items()}
colour_lookup = {int(k): "#" + v.get("PartyColour", "999999") for k, v in party_map.items()}
name_lookup = {int(k): v.get("Name", f"MP {k}") for k, v in party_map.items()}

# Dimensionality reduction with 3 components for 3D plot
pca = PCA(n_components=3)
X_reduced = pca.fit_transform(df_filtered)

# Clustering
kmeans = KMeans(n_clusters=4, random_state=42)
labels = kmeans.fit_predict(X_reduced)

# Prepare DataFrame for Plotly
plot_df = pd.DataFrame({
    "PCA1": X_reduced[:, 0],
    "PCA2": X_reduced[:, 1],
    "PCA3": X_reduced[:, 2],
    "MemberId": df_filtered.index,
    "Cluster": labels,
})
plot_df["Party"] = plot_df["MemberId"].map(party_lookup)
plot_df["Colour"] = plot_df["MemberId"].map(colour_lookup)
plot_df["Name"] = plot_df["MemberId"].map(name_lookup)

# Create 3D scatter plot with Plotly
fig = px.scatter_3d(
    plot_df,
    x="PCA1",
    y="PCA2",
    z="PCA3",
    color="Party",
    hover_name="Name",
    hover_data={"MemberId": True, "Cluster": True},
    color_discrete_map={party: plot_df[plot_df["Party"] == party]["Colour"].iloc[0] for party in plot_df["Party"].unique()},
    title="Past decade of MPs with > 50 votes clustered by voting record (3D PCA)",
    width=900,
    height=700,
)

fig.update_traces(marker=dict(size=6, line=dict(width=0.5, color='DarkSlateGrey')))

fig.show()

fig.write_html("./visualisations/mp_votes_3d_cluster.html")