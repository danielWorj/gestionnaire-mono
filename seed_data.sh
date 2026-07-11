#!/bin/bash
# ============================================================================
# Script de peuplement (seed) de la base de donnees via l'API REST
# Prerequis : jq installe (sudo apt install jq)
# Usage     : BASE_URL=http://localhost:5000/api ./seed_data.sh
# ============================================================================

BASE_URL="${BASE_URL:-http://localhost:5000/api}"

echo "=== Utilisation de BASE_URL = $BASE_URL ==="

# ============================================================================
# 1. ETABLISSEMENT (1 seule ligne)
# ============================================================================
echo ">> Creation de l'etablissement"
curl -s -X POST "$BASE_URL/structure/etablissement" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Complexe Scolaire Bilingue Les Cedres",
    "nom_bilingue": "Cedars Bilingual Comprehensive School",
    "adresse": "Rue de la Paix, Akwa",
    "bp": "BP 1234 Douala",
    "telephone": "699112233",
    "region": "Littoral",
    "logo_url": "storage/logo.png"
  }' | jq .

# ============================================================================
# 2. ANNEES SCOLAIRES (12)
# ============================================================================
echo ">> Creation des annees scolaires"
declare -a ANNEE

ANNEE[1]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2014-2015","active":false,"date_debut":"2014-09-01","date_fin":"2015-06-30"}' | jq -r '.data.id')
ANNEE[2]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2015-2016","active":false,"date_debut":"2015-09-01","date_fin":"2016-06-30"}' | jq -r '.data.id')
ANNEE[3]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2016-2017","active":false,"date_debut":"2016-09-01","date_fin":"2017-06-30"}' | jq -r '.data.id')
ANNEE[4]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2017-2018","active":false,"date_debut":"2017-09-01","date_fin":"2018-06-30"}' | jq -r '.data.id')
ANNEE[5]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2018-2019","active":false,"date_debut":"2018-09-01","date_fin":"2019-06-30"}' | jq -r '.data.id')
ANNEE[6]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2019-2020","active":false,"date_debut":"2019-09-01","date_fin":"2020-06-30"}' | jq -r '.data.id')
ANNEE[7]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2020-2021","active":false,"date_debut":"2020-09-01","date_fin":"2021-06-30"}' | jq -r '.data.id')
ANNEE[8]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2021-2022","active":false,"date_debut":"2021-09-01","date_fin":"2022-06-30"}' | jq -r '.data.id')
ANNEE[9]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2022-2023","active":false,"date_debut":"2022-09-01","date_fin":"2023-06-30"}' | jq -r '.data.id')
ANNEE[10]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2023-2024","active":false,"date_debut":"2023-09-01","date_fin":"2024-06-30"}' | jq -r '.data.id')
ANNEE[11]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2024-2025","active":false,"date_debut":"2024-09-01","date_fin":"2025-06-30"}' | jq -r '.data.id')
ANNEE[12]=$(curl -s -X POST "$BASE_URL/structure/annees-scolaires" -H "Content-Type: application/json" -d '{"libelle":"2025-2026","active":true,"date_debut":"2025-09-01","date_fin":"2026-06-30"}' | jq -r '.data.id')

echo "IDs annees scolaires: ${ANNEE[@]}"

# ============================================================================
# 3. CYCLES (10)
# ============================================================================
echo ">> Creation des cycles"
declare -a CYCLE

CYCLE[1]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":1,"libelle":"Maternelle","cycle":"Petite, Moyenne et Grande section"}' | jq -r '.data.id')
CYCLE[2]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":2,"libelle":"Primaire","cycle":"SIL au CM2"}' | jq -r '.data.id')
CYCLE[3]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":3,"libelle":"College General","cycle":"6eme a la 3eme, filiere generale"}' | jq -r '.data.id')
CYCLE[4]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":4,"libelle":"College Technique","cycle":"6eme a la 3eme, filiere technique"}' | jq -r '.data.id')
CYCLE[5]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":5,"libelle":"Lycee Scientifique","cycle":"2nde a la Tle, serie C et D"}' | jq -r '.data.id')
CYCLE[6]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":6,"libelle":"Lycee Litteraire","cycle":"2nde a la Tle, serie A"}' | jq -r '.data.id')
CYCLE[7]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":7,"libelle":"Lycee Technique Industriel","cycle":"2nde a la Tle, filiere industrielle"}' | jq -r '.data.id')
CYCLE[8]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":8,"libelle":"Lycee Technique Commercial","cycle":"2nde a la Tle, filiere commerciale"}' | jq -r '.data.id')
CYCLE[9]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":9,"libelle":"Lycee Technique Agricole","cycle":"2nde a la Tle, filiere agricole"}' | jq -r '.data.id')
CYCLE[10]=$(curl -s -X POST "$BASE_URL/structure/cycles" -H "Content-Type: application/json" -d '{"ordre":10,"libelle":"Formation Professionnelle","cycle":"Filiere courte qualifiante"}' | jq -r '.data.id')

echo "IDs cycles: ${CYCLE[@]}"

# ============================================================================
# 4. CLASSES (12) - rattachees aux cycles
# ============================================================================
echo ">> Creation des classes"
declare -a CLASSE

CLASSE[1]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"6 eme A\",\"cycle_id\":${CYCLE[3]},\"effectif\":45,\"option\":\"Espagnol\",\"salle\":\"S01\"}" | jq -r '.data.id')
CLASSE[2]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"6 eme B\",\"cycle_id\":${CYCLE[3]},\"effectif\":48,\"option\":\"Allemand\",\"salle\":\"S02\"}" | jq -r '.data.id')
CLASSE[3]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"5 eme A\",\"cycle_id\":${CYCLE[3]},\"effectif\":42,\"option\":\"Espagnol\",\"salle\":\"S03\"}" | jq -r '.data.id')
CLASSE[4]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"4 eme A\",\"cycle_id\":${CYCLE[3]},\"effectif\":40,\"option\":\"Espagnol\",\"salle\":\"S04\"}" | jq -r '.data.id')
CLASSE[5]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"3 eme A\",\"cycle_id\":${CYCLE[3]},\"effectif\":38,\"option\":\"Espagnol\",\"salle\":\"S05\"}" | jq -r '.data.id')
CLASSE[6]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"3 eme B\",\"cycle_id\":${CYCLE[4]},\"effectif\":35,\"option\":\"Technique\",\"salle\":\"S06\"}" | jq -r '.data.id')
CLASSE[7]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"2 nde C\",\"cycle_id\":${CYCLE[5]},\"effectif\":36,\"option\":\"Sciences\",\"salle\":\"S07\"}" | jq -r '.data.id')
CLASSE[8]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"2 nde A\",\"cycle_id\":${CYCLE[6]},\"effectif\":39,\"option\":\"Litteraire\",\"salle\":\"S08\"}" | jq -r '.data.id')
CLASSE[9]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"1 ere D\",\"cycle_id\":${CYCLE[5]},\"effectif\":33,\"option\":\"Sciences\",\"salle\":\"S09\"}" | jq -r '.data.id')
CLASSE[10]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"1 ere A\",\"cycle_id\":${CYCLE[6]},\"effectif\":31,\"option\":\"Litteraire\",\"salle\":\"S10\"}" | jq -r '.data.id')
CLASSE[11]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"Tle D\",\"cycle_id\":${CYCLE[5]},\"effectif\":30,\"option\":\"Sciences\",\"salle\":\"S11\"}" | jq -r '.data.id')
CLASSE[12]=$(curl -s -X POST "$BASE_URL/structure/classes" -H "Content-Type: application/json" -d "{\"libelle\":\"Tle C\",\"cycle_id\":${CYCLE[5]},\"effectif\":28,\"option\":\"Sciences\",\"salle\":\"S12\"}" | jq -r '.data.id')

echo "IDs classes: ${CLASSE[@]}"

# ============================================================================
# 5. TRIMESTRES (12) - 3 trimestres pour 4 annees scolaires (annees 9 a 12)
# ============================================================================
echo ">> Creation des trimestres"
declare -a TRIMESTRE

TRIMESTRE[1]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[9]},\"libelle\":\"Trimestre 1\",\"numero\":1,\"date_debut\":\"2022-09-01\",\"date_fin\":\"2022-12-15\"}" | jq -r '.data.id')
TRIMESTRE[2]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[9]},\"libelle\":\"Trimestre 2\",\"numero\":2,\"date_debut\":\"2023-01-05\",\"date_fin\":\"2023-03-20\"}" | jq -r '.data.id')
TRIMESTRE[3]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[9]},\"libelle\":\"Trimestre 3\",\"numero\":3,\"date_debut\":\"2023-04-01\",\"date_fin\":\"2023-06-20\"}" | jq -r '.data.id')

TRIMESTRE[4]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[10]},\"libelle\":\"Trimestre 1\",\"numero\":1,\"date_debut\":\"2023-09-01\",\"date_fin\":\"2023-12-15\"}" | jq -r '.data.id')
TRIMESTRE[5]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[10]},\"libelle\":\"Trimestre 2\",\"numero\":2,\"date_debut\":\"2024-01-05\",\"date_fin\":\"2024-03-20\"}" | jq -r '.data.id')
TRIMESTRE[6]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[10]},\"libelle\":\"Trimestre 3\",\"numero\":3,\"date_debut\":\"2024-04-01\",\"date_fin\":\"2024-06-20\"}" | jq -r '.data.id')

TRIMESTRE[7]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[11]},\"libelle\":\"Trimestre 1\",\"numero\":1,\"date_debut\":\"2024-09-01\",\"date_fin\":\"2024-12-15\"}" | jq -r '.data.id')
TRIMESTRE[8]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[11]},\"libelle\":\"Trimestre 2\",\"numero\":2,\"date_debut\":\"2025-01-05\",\"date_fin\":\"2025-03-20\"}" | jq -r '.data.id')
TRIMESTRE[9]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[11]},\"libelle\":\"Trimestre 3\",\"numero\":3,\"date_debut\":\"2025-04-01\",\"date_fin\":\"2025-06-20\"}" | jq -r '.data.id')

TRIMESTRE[10]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[12]},\"libelle\":\"Trimestre 1\",\"numero\":1,\"date_debut\":\"2025-09-01\",\"date_fin\":\"2025-12-15\"}" | jq -r '.data.id')
TRIMESTRE[11]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[12]},\"libelle\":\"Trimestre 2\",\"numero\":2,\"date_debut\":\"2026-01-05\",\"date_fin\":\"2026-03-20\"}" | jq -r '.data.id')
TRIMESTRE[12]=$(curl -s -X POST "$BASE_URL/structure/trimestres" -H "Content-Type: application/json" -d "{\"annee_scolaire_id\":${ANNEE[12]},\"libelle\":\"Trimestre 3\",\"numero\":3,\"date_debut\":\"2026-04-01\",\"date_fin\":\"2026-06-20\"}" | jq -r '.data.id')

echo "IDs trimestres: ${TRIMESTRE[@]}"

# ============================================================================
# 6. SEQUENCES (12) - 2 sequences pour les 6 trimestres des 2 dernieres annees
# ============================================================================
echo ">> Creation des sequences"
declare -a SEQUENCE

SEQUENCE[1]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[7]},\"libelle\":\"SEQ1\",\"numero\":1,\"date_debut\":\"2024-09-15\",\"date_fin\":\"2024-10-15\"}" | jq -r '.data.id')
SEQUENCE[2]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[7]},\"libelle\":\"SEQ2\",\"numero\":2,\"date_debut\":\"2024-11-15\",\"date_fin\":\"2024-12-10\"}" | jq -r '.data.id')
SEQUENCE[3]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[8]},\"libelle\":\"SEQ3\",\"numero\":1,\"date_debut\":\"2025-01-15\",\"date_fin\":\"2025-02-10\"}" | jq -r '.data.id')
SEQUENCE[4]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[8]},\"libelle\":\"SEQ4\",\"numero\":2,\"date_debut\":\"2025-02-20\",\"date_fin\":\"2025-03-10\"}" | jq -r '.data.id')
SEQUENCE[5]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[9]},\"libelle\":\"SEQ5\",\"numero\":1,\"date_debut\":\"2025-04-10\",\"date_fin\":\"2025-05-05\"}" | jq -r '.data.id')
SEQUENCE[6]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[9]},\"libelle\":\"SEQ6\",\"numero\":2,\"date_debut\":\"2025-05-15\",\"date_fin\":\"2025-06-10\"}" | jq -r '.data.id')
SEQUENCE[7]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[10]},\"libelle\":\"SEQ1\",\"numero\":1,\"date_debut\":\"2025-09-15\",\"date_fin\":\"2025-10-15\"}" | jq -r '.data.id')
SEQUENCE[8]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[10]},\"libelle\":\"SEQ2\",\"numero\":2,\"date_debut\":\"2025-11-15\",\"date_fin\":\"2025-12-10\"}" | jq -r '.data.id')
SEQUENCE[9]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[11]},\"libelle\":\"SEQ3\",\"numero\":1,\"date_debut\":\"2026-01-15\",\"date_fin\":\"2026-02-10\"}" | jq -r '.data.id')
SEQUENCE[10]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[11]},\"libelle\":\"SEQ4\",\"numero\":2,\"date_debut\":\"2026-02-20\",\"date_fin\":\"2026-03-10\"}" | jq -r '.data.id')
SEQUENCE[11]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[12]},\"libelle\":\"SEQ5\",\"numero\":1,\"date_debut\":\"2026-04-10\",\"date_fin\":\"2026-05-05\"}" | jq -r '.data.id')
SEQUENCE[12]=$(curl -s -X POST "$BASE_URL/structure/sequences" -H "Content-Type: application/json" -d "{\"trimestre_id\":${TRIMESTRE[12]},\"libelle\":\"SEQ6\",\"numero\":2,\"date_debut\":\"2026-05-15\",\"date_fin\":\"2026-06-10\"}" | jq -r '.data.id')

echo "IDs sequences: ${SEQUENCE[@]}"

# ============================================================================
# 7. PARENTS (12)
# ============================================================================
echo ">> Creation des parents"
declare -a PARENT

PARENT[1]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Mbarga","prenom":"Jean","telephone":"677001122","email":"jean.mbarga@gmail.com","adresse":"Bonapriso, Douala","profession":"Ingenieur"}' | jq -r '.data.id')
PARENT[2]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Etame","prenom":"Marie","telephone":"677002233","email":"marie.etame@gmail.com","adresse":"Bonanjo, Douala","profession":"Infirmiere"}' | jq -r '.data.id')
PARENT[3]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Fotso","prenom":"Paul","telephone":"677003344","email":"paul.fotso@gmail.com","adresse":"Bepanda, Douala","profession":"Commercant"}' | jq -r '.data.id')
PARENT[4]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Nguemo","prenom":"Alice","telephone":"677004455","email":"alice.nguemo@gmail.com","adresse":"Deido, Douala","profession":"Enseignante"}' | jq -r '.data.id')
PARENT[5]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Talla","prenom":"Robert","telephone":"677005566","email":"robert.talla@gmail.com","adresse":"Makepe, Douala","profession":"Comptable"}' | jq -r '.data.id')
PARENT[6]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Biya","prenom":"Sandrine","telephone":"677006677","email":"sandrine.biya@gmail.com","adresse":"Akwa, Douala","profession":"Avocate"}' | jq -r '.data.id')
PARENT[7]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Ondoa","prenom":"Emmanuel","telephone":"677007788","email":"emmanuel.ondoa@gmail.com","adresse":"New Bell, Douala","profession":"Chauffeur"}' | jq -r '.data.id')
PARENT[8]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Kamga","prenom":"Christelle","telephone":"677008899","email":"christelle.kamga@gmail.com","adresse":"Logbaba, Douala","profession":"Pharmacienne"}' | jq -r '.data.id')
PARENT[9]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Njoya","prenom":"David","telephone":"677009900","email":"david.njoya@gmail.com","adresse":"Bassa, Douala","profession":"Mecanicien"}' | jq -r '.data.id')
PARENT[10]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Essomba","prenom":"Rose","telephone":"677010011","email":"rose.essomba@gmail.com","adresse":"Ndokoti, Douala","profession":"Couturiere"}' | jq -r '.data.id')
PARENT[11]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Abena","prenom":"Francois","telephone":"677011122","email":"francois.abena@gmail.com","adresse":"Village, Douala","profession":"Agriculteur"}' | jq -r '.data.id')
PARENT[12]=$(curl -s -X POST "$BASE_URL/parents" -H "Content-Type: application/json" -d '{"nom":"Manga","prenom":"Beatrice","telephone":"677012233","email":"beatrice.manga@gmail.com","adresse":"PK14, Douala","profession":"Secretaire"}' | jq -r '.data.id')

echo "IDs parents: ${PARENT[@]}"

# ============================================================================
# 8. ELEVES (12) - multipart/form-data, rattaches a un parent existant
# ============================================================================
echo ">> Creation des eleves"
declare -a ELEVE

ELEVE[1]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026001" -F "nom=Mbarga" -F "prenom=Junior" -F "date_naissance=2012-03-14" -F "lieu_naissance=Douala" -F "sexe=M" -F "adresse=Bonapriso, Douala" -F "parent_id=${PARENT[1]}" | jq -r '.data.id')
ELEVE[2]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026002" -F "nom=Etame" -F "prenom=Carine" -F "date_naissance=2011-07-22" -F "lieu_naissance=Yaounde" -F "sexe=F" -F "adresse=Bonanjo, Douala" -F "parent_id=${PARENT[2]}" | jq -r '.data.id')
ELEVE[3]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026003" -F "nom=Fotso" -F "prenom=Steve" -F "date_naissance=2010-01-05" -F "lieu_naissance=Bafoussam" -F "sexe=M" -F "adresse=Bepanda, Douala" -F "parent_id=${PARENT[3]}" | jq -r '.data.id')
ELEVE[4]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026004" -F "nom=Nguemo" -F "prenom=Divine" -F "date_naissance=2010-09-18" -F "lieu_naissance=Douala" -F "sexe=F" -F "adresse=Deido, Douala" -F "parent_id=${PARENT[4]}" | jq -r '.data.id')
ELEVE[5]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026005" -F "nom=Talla" -F "prenom=Kevin" -F "date_naissance=2009-11-30" -F "lieu_naissance=Douala" -F "sexe=M" -F "adresse=Makepe, Douala" -F "parent_id=${PARENT[5]}" | jq -r '.data.id')
ELEVE[6]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026006" -F "nom=Biya" -F "prenom=Grace" -F "date_naissance=2009-04-12" -F "lieu_naissance=Douala" -F "sexe=F" -F "adresse=Akwa, Douala" -F "parent_id=${PARENT[6]}" | jq -r '.data.id')
ELEVE[7]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026007" -F "nom=Ondoa" -F "prenom=Patrick" -F "date_naissance=2008-06-25" -F "lieu_naissance=Douala" -F "sexe=M" -F "adresse=New Bell, Douala" -F "parent_id=${PARENT[7]}" | jq -r '.data.id')
ELEVE[8]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026008" -F "nom=Kamga" -F "prenom=Melissa" -F "date_naissance=2008-02-08" -F "lieu_naissance=Douala" -F "sexe=F" -F "adresse=Logbaba, Douala" -F "parent_id=${PARENT[8]}" | jq -r '.data.id')
ELEVE[9]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026009" -F "nom=Njoya" -F "prenom=Aristide" -F "date_naissance=2007-10-03" -F "lieu_naissance=Douala" -F "sexe=M" -F "adresse=Bassa, Douala" -F "parent_id=${PARENT[9]}" | jq -r '.data.id')
ELEVE[10]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026010" -F "nom=Essomba" -F "prenom=Nadia" -F "date_naissance=2007-05-19" -F "lieu_naissance=Douala" -F "sexe=F" -F "adresse=Ndokoti, Douala" -F "parent_id=${PARENT[10]}" | jq -r '.data.id')
ELEVE[11]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026011" -F "nom=Abena" -F "prenom=Herve" -F "date_naissance=2006-12-27" -F "lieu_naissance=Douala" -F "sexe=M" -F "adresse=Village, Douala" -F "parent_id=${PARENT[11]}" | jq -r '.data.id')
ELEVE[12]=$(curl -s -X POST "$BASE_URL/inscription/eleves" -F "matricule=MAT2026012" -F "nom=Manga" -F "prenom=Larissa" -F "date_naissance=2006-08-15" -F "lieu_naissance=Douala" -F "sexe=F" -F "adresse=PK14, Douala" -F "parent_id=${PARENT[12]}" | jq -r '.data.id')

echo "IDs eleves: ${ELEVE[@]}"

# ============================================================================
# 9. INSCRIPTIONS (12) - annee scolaire active
# ============================================================================
echo ">> Creation des inscriptions"

curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[1]},\"classe_id\":${CLASSE[1]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Inscrit\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[2]},\"classe_id\":${CLASSE[1]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Inscrit\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[3]},\"classe_id\":${CLASSE[2]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Redoublant\",\"redoublant\":true}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[4]},\"classe_id\":${CLASSE[3]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Inscrit\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[5]},\"classe_id\":${CLASSE[4]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Inscrit\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[6]},\"classe_id\":${CLASSE[5]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Inscrit\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[7]},\"classe_id\":${CLASSE[6]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Transfere\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[8]},\"classe_id\":${CLASSE[7]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Inscrit\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[9]},\"classe_id\":${CLASSE[8]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Inscrit\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[10]},\"classe_id\":${CLASSE[9]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Redoublant\",\"redoublant\":true}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[11]},\"classe_id\":${CLASSE[11]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Inscrit\",\"redoublant\":false}" | jq .
curl -s -X POST "$BASE_URL/inscription/inscriptions" -H "Content-Type: application/json" -d "{\"eleve_id\":${ELEVE[12]},\"classe_id\":${CLASSE[12]},\"annee_scolaire_id\":${ANNEE[12]},\"statut\":\"Abandon\",\"redoublant\":false}" | jq .

# ============================================================================
# 10. ENSEIGNANTS (12)
# ============================================================================
echo ">> Creation des enseignants"
declare -a ENSEIGNANT

ENSEIGNANT[1]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Mballa","prenom":"Georges","telephone":"690112233","email":"georges.mballa@ecole.cm","grade":"Professeur des lycees","est_titulaire":true}' | jq -r '.data.id')
ENSEIGNANT[2]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Nkoulou","prenom":"Sylvie","telephone":"690112244","email":"sylvie.nkoulou@ecole.cm","grade":"Professeur certifie","est_titulaire":true}' | jq -r '.data.id')
ENSEIGNANT[3]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Fongang","prenom":"Michel","telephone":"690112255","email":"michel.fongang@ecole.cm","grade":"Professeur des lycees","est_titulaire":false}' | jq -r '.data.id')
ENSEIGNANT[4]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Ateba","prenom":"Nadege","telephone":"690112266","email":"nadege.ateba@ecole.cm","grade":"Instituteur","est_titulaire":true}' | jq -r '.data.id')
ENSEIGNANT[5]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Simo","prenom":"Bertrand","telephone":"690112277","email":"bertrand.simo@ecole.cm","grade":"Professeur certifie","est_titulaire":false}' | jq -r '.data.id')
ENSEIGNANT[6]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Ekwalla","prenom":"Chantal","telephone":"690112288","email":"chantal.ekwalla@ecole.cm","grade":"Professeur des lycees","est_titulaire":true}' | jq -r '.data.id')
ENSEIGNANT[7]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Doumbe","prenom":"Serge","telephone":"690112299","email":"serge.doumbe@ecole.cm","grade":"Professeur certifie","est_titulaire":false}' | jq -r '.data.id')
ENSEIGNANT[8]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Kenmogne","prenom":"Aurelie","telephone":"690113300","email":"aurelie.kenmogne@ecole.cm","grade":"Instituteur","est_titulaire":true}' | jq -r '.data.id')
ENSEIGNANT[9]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Tchoua","prenom":"Franck","telephone":"690113311","email":"franck.tchoua@ecole.cm","grade":"Professeur des lycees","est_titulaire":true}' | jq -r '.data.id')
ENSEIGNANT[10]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Belinga","prenom":"Odette","telephone":"690113322","email":"odette.belinga@ecole.cm","grade":"Professeur certifie","est_titulaire":false}' | jq -r '.data.id')
ENSEIGNANT[11]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Zang","prenom":"Olivier","telephone":"690113333","email":"olivier.zang@ecole.cm","grade":"Professeur des lycees","est_titulaire":true}' | jq -r '.data.id')
ENSEIGNANT[12]=$(curl -s -X POST "$BASE_URL/pedagogie/enseignants" -H "Content-Type: application/json" -d '{"nom":"Moukouri","prenom":"Pauline","telephone":"690113344","email":"pauline.moukouri@ecole.cm","grade":"Instituteur","est_titulaire":false}' | jq -r '.data.id')

echo "IDs enseignants: ${ENSEIGNANT[@]}"

# ============================================================================
# 11. GROUPES DE MATIERE (10)
# ============================================================================
echo ">> Creation des groupes de matiere"
declare -a GROUPE

GROUPE[1]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Sciences"}' | jq -r '.data.id')
GROUPE[2]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Lettres"}' | jq -r '.data.id')
GROUPE[3]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Langues"}' | jq -r '.data.id')
GROUPE[4]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Arts"}' | jq -r '.data.id')
GROUPE[5]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Sport"}' | jq -r '.data.id')
GROUPE[6]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Technique"}' | jq -r '.data.id')
GROUPE[7]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Economie"}' | jq -r '.data.id')
GROUPE[8]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Informatique"}' | jq -r '.data.id')
GROUPE[9]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Religion"}' | jq -r '.data.id')
GROUPE[10]=$(curl -s -X POST "$BASE_URL/pedagogie/groupes-matiere" -H "Content-Type: application/json" -d '{"libelle":"Civisme"}' | jq -r '.data.id')

echo "IDs groupes: ${GROUPE[@]}"

# ============================================================================
# 12. MATIERES (15) - rattachees aux groupes
# ============================================================================
echo ">> Creation des matieres"
declare -a MATIERE

MATIERE[1]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Mathematiques\",\"groupe_id\":${GROUPE[1]}}" | jq -r '.data.id')
MATIERE[2]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Physique\",\"groupe_id\":${GROUPE[1]}}" | jq -r '.data.id')
MATIERE[3]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Chimie\",\"groupe_id\":${GROUPE[1]}}" | jq -r '.data.id')
MATIERE[4]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Sciences de la Vie et de la Terre\",\"groupe_id\":${GROUPE[1]}}" | jq -r '.data.id')
MATIERE[5]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Francais\",\"groupe_id\":${GROUPE[2]}}" | jq -r '.data.id')
MATIERE[6]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Histoire\",\"groupe_id\":${GROUPE[2]}}" | jq -r '.data.id')
MATIERE[7]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Geographie\",\"groupe_id\":${GROUPE[2]}}" | jq -r '.data.id')
MATIERE[8]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Anglais\",\"groupe_id\":${GROUPE[3]}}" | jq -r '.data.id')
MATIERE[9]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Espagnol\",\"groupe_id\":${GROUPE[3]}}" | jq -r '.data.id')
MATIERE[10]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Allemand\",\"groupe_id\":${GROUPE[3]}}" | jq -r '.data.id')
MATIERE[11]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Arts Plastiques\",\"groupe_id\":${GROUPE[4]}}" | jq -r '.data.id')
MATIERE[12]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Musique\",\"groupe_id\":${GROUPE[4]}}" | jq -r '.data.id')
MATIERE[13]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Education Physique et Sportive\",\"groupe_id\":${GROUPE[5]}}" | jq -r '.data.id')
MATIERE[14]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Informatique\",\"groupe_id\":${GROUPE[8]}}" | jq -r '.data.id')
MATIERE[15]=$(curl -s -X POST "$BASE_URL/pedagogie/matieres" -H "Content-Type: application/json" -d "{\"libelle\":\"Education a la Citoyennete\",\"groupe_id\":${GROUPE[10]}}" | jq -r '.data.id')

echo "IDs matieres: ${MATIERE[@]}"

# ============================================================================
# 13. TITULAIRES DE CLASSE (12) - annee scolaire active
# ============================================================================
echo ">> Affectation des titulaires de classe"

curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[1]},\"enseignant_id\":${ENSEIGNANT[1]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[2]},\"enseignant_id\":${ENSEIGNANT[2]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[3]},\"enseignant_id\":${ENSEIGNANT[3]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[4]},\"enseignant_id\":${ENSEIGNANT[4]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[5]},\"enseignant_id\":${ENSEIGNANT[5]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[6]},\"enseignant_id\":${ENSEIGNANT[6]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[7]},\"enseignant_id\":${ENSEIGNANT[7]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[8]},\"enseignant_id\":${ENSEIGNANT[8]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[9]},\"enseignant_id\":${ENSEIGNANT[9]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[10]},\"enseignant_id\":${ENSEIGNANT[10]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[11]},\"enseignant_id\":${ENSEIGNANT[11]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/titulaires-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[12]},\"enseignant_id\":${ENSEIGNANT[12]},\"annee_scolaire_id\":${ANNEE[12]}}" | jq .

# ============================================================================
# 14. MATIERES-CLASSE (15) - affectation matiere + enseignant a une classe
# ============================================================================
echo ">> Affectation des matieres aux classes"

curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[1]},\"matiere_id\":${MATIERE[1]},\"enseignant_id\":${ENSEIGNANT[1]},\"coefficient\":4}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[1]},\"matiere_id\":${MATIERE[5]},\"enseignant_id\":${ENSEIGNANT[2]},\"coefficient\":4}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[2]},\"matiere_id\":${MATIERE[8]},\"enseignant_id\":${ENSEIGNANT[3]},\"coefficient\":3}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[3]},\"matiere_id\":${MATIERE[2]},\"enseignant_id\":${ENSEIGNANT[4]},\"coefficient\":3}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[4]},\"matiere_id\":${MATIERE[3]},\"enseignant_id\":${ENSEIGNANT[5]},\"coefficient\":3}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[5]},\"matiere_id\":${MATIERE[4]},\"enseignant_id\":${ENSEIGNANT[6]},\"coefficient\":2}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[6]},\"matiere_id\":${MATIERE[14]},\"enseignant_id\":${ENSEIGNANT[7]},\"coefficient\":2}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[7]},\"matiere_id\":${MATIERE[1]},\"enseignant_id\":${ENSEIGNANT[1]},\"coefficient\":6}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[8]},\"matiere_id\":${MATIERE[5]},\"enseignant_id\":${ENSEIGNANT[2]},\"coefficient\":6}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[9]},\"matiere_id\":${MATIERE[2]},\"enseignant_id\":${ENSEIGNANT[4]},\"coefficient\":6}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[10]},\"matiere_id\":${MATIERE[6]},\"enseignant_id\":${ENSEIGNANT[8]},\"coefficient\":4}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[11]},\"matiere_id\":${MATIERE[3]},\"enseignant_id\":${ENSEIGNANT[5]},\"coefficient\":6}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[12]},\"matiere_id\":${MATIERE[1]},\"enseignant_id\":${ENSEIGNANT[1]},\"coefficient\":7}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[1]},\"matiere_id\":${MATIERE[8]},\"enseignant_id\":${ENSEIGNANT[3]},\"coefficient\":2}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[2]},\"matiere_id\":${MATIERE[13]},\"enseignant_id\":${ENSEIGNANT[9]},\"coefficient\":1}" | jq .
curl -s -X POST "$BASE_URL/pedagogie/matieres-classe" -H "Content-Type: application/json" -d "{\"classe_id\":${CLASSE[3]},\"matiere_id\":${MATIERE[9]},\"enseignant_id\":${ENSEIGNANT[10]},\"coefficient\":2}" | jq .

echo "=== Peuplement termine ==="
