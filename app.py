from flask import Flask, render_template

app = Flask(__name__)

# Pipeline stages (static for now, can be dynamic)
pipeline = [
    {
        "name": "GitHub Push",
        "desc": "Push Code",
        "status": "✔ Triggered",
        "color": "github",
    },
    {
        "name": "GitHub Actions",
        "desc": "Checkout & Build",
        "status": "✔ Success",
        "color": "ci",
    },
    {
        "name": "Docker",
        "desc": "Login & Push Image",
        "status": "✔ Completed",
        "color": "docker",
    },
    {
        "name": "yq",
        "desc": "Update Deployment YAML",
        "status": "✔ Updated",
        "color": "yq",
    },
    {
        "name": "GitHub Commit",
        "desc": "Push Deployment Changes",
        "status": "✔ Committed",
        "color": "github",
    },
    {
        "name": "Argo CD",
        "desc": "Sync Repo → Deploy",
        "status": "✔ Synced",
        "color": "argo",
    },
    {
        "name": "Kubernetes",
        "desc": "Application Running",
        "status": "✔ Live",
        "color": "k8s",
    },
]


@app.route("/")
def home():
    return render_template("index.html", pipeline=pipeline)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
