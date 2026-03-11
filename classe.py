import numpy as np
import time
import matplotlib.pyplot as plt

class Vecteur3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def add(self, other):
        return Vecteur3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def sub(self, other):
        return Vecteur3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def mul(self, scalar):
        return Vecteur3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def truediv(self, scalar):
        return Vecteur3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def __len__(self):
        return 3

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def norm(self):
        return np.sqrt(self.dot(self))

    def normalize(self):
        return self.truediv(self.norm())

class Couleur:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __len__(self):
        return 3
    
    def to_numpy(self):
        return np.array([self.r, self.g, self.b])
    
    def add(self, other):
        if isinstance(other, Couleur):
            return Couleur(self.r + other.r, self.g + other.g, self.b + other.b)
        elif isinstance(other, (int, float)):
            return Couleur(self.r + other, self.g + other, self.b + other)
    
    def mul(self, other):
        if isinstance(other, Couleur):
            return Couleur(self.r * other.r, self.g * other.g, self.b * other.b)
        elif isinstance(other, (int, float)):
            return Couleur(self.r * other, self.g * other, self.b * other)

class Objet3D:
    def __init__(self, couleur, reflection=0):
        self.couleur = couleur
        self.reflection = reflection

class Sphere(Objet3D):
    def __init__(self, position, rayon, couleur, reflection=0, diffuse_c=0, specular_c=0, specular_k=0):
        super().__init__(couleur, reflection)
        self.position = position
        self.rayon = rayon
        self.diffuse_c = diffuse_c
        self.specular_c = specular_c
        self.specular_k = specular_k

class Plan(Objet3D):
    def __init__(self, position, normal, couleur, reflection=0, diffuse_c=0, specular_c=0, specular_k=0):
        super().__init__(couleur, reflection)
        self.position = position
        self.normal = normal
        self.diffuse_c = diffuse_c
        self.specular_c = specular_c
        self.specular_k = specular_k

class Lumiere:
    def __init__(self, position, couleur):
        self.position = position
        self.couleur = couleur

class Camera:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction

class Scene:
    def __init__(self, objets, lumiere, camera, ambient=0.05, depth_max=5):
        self.objets = objets
        self.lumiere = lumiere
        self.camera = camera
        self.ambient = ambient
        self.depth_max = depth_max

    def ajouter_objet(self, objet):
        self.objets.append(objet)

    def ajouter_lumiere(self, lumiere):
        self.lumiere = lumiere

    def intersect_plane(self, rayO, rayD, position, normal):
        denom = rayD.dot(normal)
        if np.abs(denom) < 1e-6:
            return np.inf
        d = (position.sub(rayO).dot(normal)) / denom
        if d < 0:
            return np.inf
        return d

    def intersect_sphere(self, rayO, rayD, position, rayon):
        a = rayD.dot(rayD)
        OS = rayO.sub(position)
        b = 2 * rayD.dot(OS)
        c = OS.dot(OS) - rayon * rayon
        disc = b * b - 4 * a * c
        if disc > 0:
            distSqrt = np.sqrt(disc)
            q = (-b - distSqrt) / 2.0 if b < 0 else (-b + distSqrt) / 2.0
            t0 = q / a
            t1 = c / q
            t0, t1 = min(t0, t1), max(t0, t1)
            if t1 >= 0:
                return t1 if t0 < 0 else t0
        return np.inf

    def intersect(self, rayO, rayD, objet):
        if isinstance(objet, Plan):
            return self.intersect_plane(rayO, rayD, objet.position, objet.normal)
        elif isinstance(objet, Sphere):
            return self.intersect_sphere(rayO, rayD, objet.position, objet.rayon)

    def get_normal(self, objet, M):
        if isinstance(objet, Sphere):
            return (M.sub(objet.position)).normalize()
        elif isinstance(objet, Plan):
            return objet.normal

    def get_color(self, objet, M):
        couleur = objet.couleur
        if isinstance(couleur, Couleur):
            return couleur
        elif callable(couleur):
            return couleur(M)

    def trace_ray(self, rayO, rayD, depth=0):
        t = np.inf
        obj_idx = -1
        for i, objet in enumerate(self.objets):
            t_obj = self.intersect(rayO, rayD, objet)
            if t_obj < t:
                t, obj_idx = t_obj, i
        if t == np.inf:
            return None
        objet = self.objets[obj_idx]
        M = rayO.add(rayD.mul(t))
        N = self.get_normal(objet, M)
        couleur = self.get_color(objet, M)
        toL = (self.lumiere.position.sub(M)).normalize()
        toO = (self.camera.position.sub(M)).normalize()
        l = [self.intersect(M.add(N.mul(0.0001)), toL, obj) for k, obj in enumerate(self.objets) if k != obj_idx]
        if l and min(l) < np.inf:
            return None
        col_ray = Couleur(self.ambient, self.ambient, self.ambient)
        diffuse_light = max(N.dot(toL), 0)
        col_ray = col_ray.add(couleur.mul(diffuse_light * objet.diffuse_c))
        col_ray = col_ray.add(self.lumiere.couleur.mul(diffuse_light * objet.specular_c * max(N.dot((toL.add(toO)).normalize()), 0) ** objet.specular_k))
        return objet, M, N, col_ray

    def render(self, largeur, longueur, camera, screen_coords):
        img = np.zeros((longueur, largeur, 3))
        for i, x in enumerate(np.linspace(screen_coords[0], screen_coords[2], largeur)):
            for j, y in enumerate(np.linspace(screen_coords[1], screen_coords[3], longueur)):
                col = Couleur(0, 0, 0)
                Q = Vecteur3D(x, y, 0)
                D = (Q.sub(camera.position)).normalize()
                depth = 0
                rayO, rayD = camera.position, D
                reflection = 1.0
                while depth < self.depth_max:
                    traced = self.trace_ray(rayO, rayD, depth)
                    if not traced:
                        break
                    objet, M, N, col_ray = traced
                    rayO, rayD = M.add(N.mul(0.0001)), rayD.sub(N.mul(2 * N.dot(rayD)))
                    depth += 1
                    col = col.add(col_ray.mul(reflection))
                    reflection *= objet.reflection
                img[longueur - j - 1, i, :] = np.clip(col.to_numpy(), 0, 1)
        return img

# Paramètres de la scène
largeur = 1920
longueur = 1080
depth_max = 5

start = time.time()

# Création de la lumière
lumiere = Lumiere(Vecteur3D(5.0, 5.0, -10.0), Couleur(1.0, 1.0, 1.0))

# Création de la caméra
camera = Camera(Vecteur3D(0, 0, -1), Vecteur3D(0, 0, 0))

# Création de la scène
scene = Scene([], lumiere, camera, 0.05, depth_max)

# Création des objets
sphere1 = Sphere(Vecteur3D(0.0, 0.1, 2), 0.6, Couleur(1, 1, 0), 0.5, 0.5, 0.5, 100)
# Deuxieme sphere blanche à droit de la première
sphere2 = Sphere(Vecteur3D(1.7, 0.1, 2), 0.6, Couleur(1, 1, 1), 1, 0.5, 0.5, 100)
# Troisième sphere blanche à gauche de la première
sphere3 = Sphere(Vecteur3D(-1.7, 0.1, 2), 0.6, Couleur(1, 1, 1), 0, 0.5, 0.5, 100)
# petite sphere rouge
sphere4 = Sphere(Vecteur3D(-1.3, -0.2, 1), 0.2, Couleur(1, 0, 0), 0, 0.5, 0.5, 100)
# petite sphere verte
sphere5 = Sphere(Vecteur3D(0.0, -0.2, 1), 0.2, Couleur(0, 1, 0), 0.5, 0.5, 0.5, 100)
# petite sphere bleue
sphere6 = Sphere(Vecteur3D(1.3, -0.2, 1), 0.2, Couleur(0, 0, 1), 1, 0.5, 0.5, 100)

plan1 = Plan(Vecteur3D(0.0, -0.5, 0.0), Vecteur3D(0.0, 1.0, 0.0), Couleur(1, 1, 1), 0.2, 0.5, 0.5, 100)

# mur blanc au fond de la scène jusqu'aux limites de l'écran
plan2 = Plan(Vecteur3D(0.0, 0.0, 3), Vecteur3D(0.0, 0.0, -1.0), Couleur(1, 1, 1), 0.2, 0.5, 0.5, 100)

scene.ajouter_objet(sphere1)
scene.ajouter_objet(sphere2)
scene.ajouter_objet(sphere3)
scene.ajouter_objet(sphere4)
scene.ajouter_objet(sphere5)
scene.ajouter_objet(sphere6)
scene.ajouter_objet(plan1)
scene.ajouter_objet(plan2)

# Coordonnées de l'écran
screen_coords = (-largeur / longueur, -1, largeur / longueur, 1)

# Rendu de l'image
img = scene.render(largeur, longueur, camera, screen_coords)

# Sauvegarde de l'image dans la racine
plt.imsave('fig.png', img)

print('Temps de rendu :', time.time() - start, 's')