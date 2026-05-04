import json
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(turns):
    return model.encode(turns)

def compute_signals(embeddings):
    drift = []
    jump = [0]

    for i in range(len(embeddings)):
        d0 = cosine_distances([embeddings[0]], [embeddings[i]])[0][0]
        drift.append(d0)

        if i > 0:
            d1 = cosine_distances([embeddings[i-1]], [embeddings[i]])[0][0]
            jump.append(d1)

    return drift, jump

def repetition_score(turns):
    scores = []
    seen = {}

    for t in turns:
        t_clean = t.strip().lower()
        seen[t_clean] = seen.get(t_clean, 0) + 1
        scores.append(seen[t_clean])

    return scores

def plot(turns, drift, jump, rep, title):
    x = list(range(len(turns)))

    plt.figure(figsize=(12,6))

    plt.plot(x, drift, label="Drift (global shift)")
    plt.plot(x, jump, label="Jump (local change)")
    plt.plot(x, rep, label="Repetition")

    # Mark known events
    plt.axvline(x=14, linestyle='--', label='Phase Shift (platform reveal)')
    plt.axvline(x=39, linestyle='--', label='Loop Start')

    plt.xlabel("Turn")
    plt.ylabel("Signal")
    plt.title(title)
    plt.legend()
    plt.grid()

    plt.savefig(f"analysis/{title}_final.png", dpi=300, bbox_inches='tight')
    plt.show()

def main():
    with open("analysis/data.json") as f:
        data = json.load(f)

    for convo in data:
        turns = convo["turns"]

        embeddings = get_embeddings(turns)
        drift, jump = compute_signals(embeddings)
        rep = repetition_score(turns)

        plot(turns, drift, jump, rep, convo["id"])

if __name__ == "__main__":
    main()