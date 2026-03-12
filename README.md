# 🔦 RayTracing en Python

Un moteur de ray tracing implémenté from scratch en Python, avec rendu de sphères et de plans avec effets de lumière, d'ombres et de réflexions.

## 📸 Aperçu

Le programme génère une image de synthèse (`fig.png`) en résolution **1920×1080** représentant une scène 3D composée de sphères colorées et de plans, éclairée par une source lumineuse ponctuelle.

---

## 🗂️ Structure du code

Le projet repose sur une architecture orientée objet, organisée autour des classes suivantes :

### Mathématiques & couleurs
| Classe | Description |
|---|---|
| `Vecteur3D` | Vecteur 3D avec opérations : addition, soustraction, multiplication, division, produit scalaire, norme, normalisation |
| `Couleur` | Couleur RGB avec addition et multiplication (scalaire ou couleur × couleur) |

### Objets de la scène
| Classe | Description |
|---|---|
| `Objet3D` | Classe de base : couleur + coefficient de réflexion |
| `Sphere` | Sphère définie par position, rayon, couleur, réflexion, coefficients diffus/spéculaire |
| `Plan` | Plan infini défini par position, normale, couleur et propriétés d'éclairage |
| `Lumiere` | Source lumineuse ponctuelle (position + couleur) |
| `Camera` | Caméra définie par position et direction |

### Moteur de rendu
| Classe | Description |
|---|---|
| `Scene` | Contient tous les objets, la lumière et la caméra. Gère les intersections, le calcul de lumière et le rendu complet |

---

## ⚙️ Fonctionnement

### Algorithme de ray tracing

Pour chaque pixel de l'image, un rayon est lancé depuis la caméra. La scène est parcourue pour trouver l'objet le plus proche intersecté par ce rayon. Le moteur calcule ensuite :

1. **Les ombres** — en vérifiant si un objet bloque le chemin vers la lumière
2. **L'éclairage diffus** — basé sur l'angle entre la normale de surface et la lumière (modèle Lambertien)
3. **L'éclairage spéculaire** — reflets brillants selon le modèle de Blinn-Phong
4. **Les réflexions récursives** — jusqu'à `depth_max` rebonds

### Scène par défaut

La scène inclut :
- 🟡 Une grande sphère **jaune** (réflexion partielle) au centre
- ⚪ Deux grandes sphères **blanches** de part et d'autre (l'une totalement réfléchissante, l'autre mate)
- 🔴 Une petite sphère **rouge** (mate)
- 🟢 Une petite sphère **verte** (réflexion partielle)
- 🔵 Une petite sphère **bleue** (totalement réfléchissante)
- 🟦 Un **plan horizontal** blanc (sol) avec réflexion
- 🟦 Un **plan vertical** blanc (mur du fond)
- 💡 Une **lumière blanche** en position haute-gauche `(5, 5, -10)`

---

## 🚀 Installation & utilisation

### Prérequis

```bash
pip install numpy matplotlib
```

### Lancer le rendu

```bash
python classe.py
```

L'image résultante est sauvegardée sous le nom **`fig.png`** dans le répertoire courant.  
Le temps de rendu est affiché dans le terminal à la fin de l'exécution.

---

## 🔧 Paramètres configurables

Dans le fichier `classe.py`, vous pouvez modifier :

| Paramètre | Valeur par défaut | Description |
|---|---|---|
| `largeur` | `1920` | Largeur de l'image en pixels |
| `longueur` | `1080` | Hauteur de l'image en pixels |
| `depth_max` | `5` | Nombre maximum de rebonds de réflexion |
| `ambient` | `0.05` | Intensité de la lumière ambiante |

### Paramètres d'un objet (`Sphere` / `Plan`)

| Paramètre | Description |
|---|---|
| `couleur` | Couleur RGB (valeurs entre 0 et 1) |
| `reflection` | Coefficient de réflexion (0 = mat, 1 = miroir parfait) |
| `diffuse_c` | Intensité de l'éclairage diffus |
| `specular_c` | Intensité du reflet spéculaire |
| `specular_k` | Exposant de brillance (plus élevé = reflet plus petit et net) |

---

## ⚠️ Performance

Ce moteur est implémenté en **Python pur** (sans vectorisation avancée), ce qui le rend relativement lent pour de grandes résolutions. À titre indicatif, un rendu en 1920×1080 avec 5 niveaux de réflexion peut prendre **plusieurs minutes** selon votre machine.

Pour accélérer le rendu, vous pouvez :
- Réduire la résolution (`largeur`, `longueur`)
- Diminuer `depth_max`
- Envisager une vectorisation NumPy ou une parallélisation avec `multiprocessing`

---

## 📄 Licence

Ce projet est open source. Consultez le dépôt GitHub pour plus d'informations.
