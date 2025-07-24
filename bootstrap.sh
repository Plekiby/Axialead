#!/usr/bin/env bash
set -e

# 1. Création des dossiers principaux
mkdir -p services/{user-service,course-service,payment-service,subscription-service,stats-service,notification-service}
mkdir -p webapp/{templates,static,scripts}
mkdir -p infra/{k8s,ci}

# 2. README.md
cat > README.md <<EOM
# Axialead

Monorepo pour le site de formations.

- /services : microservices Python (Flask/FastAPI)
- /webapp   : application web Flask + Jinja2
- /infra    : manifests Kubernetes & CI
EOM

# 3. Squelettes pour chaque service
for svc in services/*; do
  (
    cd "$svc"
    python3 -m venv venv
    touch app.py requirements.txt
    echo "# $svc" > README.md
  )
done

# 4. Initialisation de /webapp
(
  cd webapp
  python3 -m venv venv
  source venv/bin/activate
  pip install flask jinja2
  deactivate

  touch app.py requirements.txt
)

echo "🗂️ Arborescence et squelettes créés avec succès !"
EOF