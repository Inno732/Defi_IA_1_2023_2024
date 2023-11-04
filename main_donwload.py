import os
from pytube import YouTube
from tqdm import tqdm

# Entrez l'URL de la vidéo YouTube que vous souhaitez télécharger
video_url = "https://www.youtube.com/watch?v=3sQO_KdouJ4"

# Créez un objet YouTube
yt = YouTube(video_url)

# Sélectionnez la meilleure qualité vidéo disponible
video_stream = yt.streams.get_highest_resolution()

# Choisissez un emplacement pour enregistrer la vidéo
download_path = "/Users/utilisateur/Desktop/VideoSplitterV2"

# Assurez-vous que le dossier de destination existe, sinon, créez-le
if not os.path.exists(download_path):
    os.makedirs(download_path)

# Téléchargez la vidéo
tqdm(video_stream.download(output_path=download_path))

print("Téléchargement terminé !")
