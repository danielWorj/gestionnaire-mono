"""
Clé publique ECDSA (courbe P-256 / SECP256R1) embarquée dans l'application.

C'est le SEUL secret présent côté école. Elle ne permet que de VÉRIFIER
qu'une licence a bien été signée par vous — elle ne permet en aucun cas
d'en fabriquer une nouvelle. La clé PRIVÉE correspondante ne doit jamais
apparaître dans ce dépôt ni sur les postes des écoles.

Cette clé est générée une seule fois via admin_tools/generate_keypair.py.
Le fichier ci-dessous contient une clé de DÉMONSTRATION générée pour les
besoins de ce dépôt : remplacez-la par votre propre clé publique avant
toute distribution réelle, et régénérez une licence pour chaque école
avec la nouvelle clé privée si vous la changez.
"""

PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEwcvGnPpj8YtPL9nY5ay0y8zBHb8J
wgmGKiS8RRF59iUeuLZLh7GdzAZlu5xS9iVs8//ilsVWjpROVUE5q9zCTw==
-----END PUBLIC KEY-----
"""