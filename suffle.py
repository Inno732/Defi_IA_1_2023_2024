from PIL import Image
import random
import os
from tqdm import tqdm

# Répertoire contenant les images à traiter
input_directory = "/Users/utilisateur/Desktop/VideoSplitterV2/PERSONNAL_DATABASE/no_fire_not_suffle"
output_directory = "/Users/utilisateur/Desktop/VideoSplitterV2/PERSONNAL_DATABASE/no_fire"

# Assurez-vous que le répertoire de sortie existe, sinon, créez-le
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Liste des fichiers image dans le répertoire d'entrée
image_files = [f for f in os.listdir(input_directory) if f.lower().endswith(('.png'))]
print("taille des images=",len(image_files))
for image_file in tqdm(range(len(image_files))):
    if image_file%2==0:
        # Ouvrir l'image
        image = Image.open(os.path.join(input_directory, image_files[image_file]))

        # Générez un angle de rotation aléatoire 
        angle = random.choice([-90,90,180,180])

         # Effectuez la rotation
        rotated_image = image.rotate(angle, expand=True)

        # Sauvegardez l'image dans le répertoire de sortie
        output_path = os.path.join(output_directory, f"rotated_{image_files[image_file]}")
        rotated_image.save(output_path)
    else:
        output_path = os.path.join(output_directory, image_files[image_file])
        image.save(output_path)
# Mélangez la liste d'images de sortie de manière aléatoire
random.shuffle(image_files)

print("Images rotatées et mélangées avec succès!")
