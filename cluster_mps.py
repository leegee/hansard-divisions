import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

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

# Reduce dimensions
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(df_filtered)

# Create DataFrame for plotting
plot_df = pd.DataFrame({
    "x": X_reduced[:, 0],
    "y": X_reduced[:, 1],
    "MemberId": df_filtered.index,
})
plot_df["Party"] = plot_df["MemberId"].map(party_lookup)
plot_df["Colour"] = plot_df["MemberId"].map(colour_lookup)

# Plot
plt.figure(figsize=(12, 9))
sns.scatterplot(
    data=plot_df,
    x="x", y="y",
    hue="Party",
    palette={party: plot_df[plot_df["Party"] == party]["Colour"].iloc[0] for party in plot_df["Party"].unique()},
    legend="full",
    s=70,
    edgecolor="black"
)

plt.title("MPs Clustered by Voting Record (Coloured by Party)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.grid(True)
plt.legend(title="Party", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()
