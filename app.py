import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile
import os

# Configuration de la page
st.set_page_config(page_title="KeaJJ - Logotisation", page_icon="🥋", layout="centered")

st.title("🥋 Ke'a Ju-Jitsu")
st.write("© Ke'a Ju-Jitsu photos")

# --- PARAMÈTRES (Sidebar) ---
st.sidebar.header("Paramètres de logotisation")
facteur_taille = st.sidebar.slider("Taille du logo (% de la largeur)", 5, 50, 15) / 100.0
opacite = st.sidebar.slider("Opacité du logo (%)", 10, 100, 50) / 100.0
marge = st.sidebar.slider("Marge (pixels)", 0, 100, 30)

# --- CHARGEMENT DU LOGO FIXE ---
# Assurez-vous que le nom du fichier correspond exactement au logo placé dans le même dossier
chemin_logo = "logo_blanc_fond_transparent.png"

try:
    logo_img = Image.open(chemin_logo).convert("RGBA")
    logo_charge = True
except FileNotFoundError:
    st.error(f"❌ Impossible de trouver le fichier '{chemin_logo}'. Veuillez le placer dans le même dossier que l'application.")
    logo_charge = False

# --- UPLOADS DES PHOTOS ---
if logo_charge:
    st.subheader("1. Ajouter les photos à traiter")
    image_files = st.file_uploader("Sélectionnez vos photos", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    # Fonction de traitement
    def process_image(img_upload, logo_upright, scale, opacity, margin):
        image_brute = Image.open(img_upload)
        image_orientee = ImageOps.exif_transpose(image_brute)
        image = image_orientee.convert("RGBA")
        
        exif = image_brute.getexif()
        if 274 in exif:
            exif[274] = 1 
            
        logo_largeur = int(image.width * scale)
        logo_hauteur = int((logo_largeur * logo_upright.height) / logo_upright.width)
        logo_redimensionne = logo_upright.resize((logo_largeur, logo_hauteur), Image.Resampling.LANCZOS)
        
        r, g, b, a = logo_redimensionne.split()
        a = a.point(lambda i: i * opacity)
        logo_redimensionne.putalpha(a)

        pos_x = image.width - logo_largeur - margin
        pos_y = image.height - logo_hauteur - margin
        
        image.paste(logo_redimensionne, (pos_x, pos_y), mask=logo_redimensionne)
        image_finale = image.convert("RGB")
        
        buf = io.BytesIO()
        if exif:
            image_finale.save(buf, format="JPEG", quality=95, exif=exif.tobytes())
        else:
            image_finale.save(buf, format="JPEG", quality=95)
            
        return buf.getvalue()

    # --- TRAITEMENT ---
    if image_files:
        st.subheader("2. Go Fight !")
        
        if st.button("GO ! 🥇Oss"):
            progress_text = "Opération en cours. Veuillez patienter..."
            my_bar = st.progress(0, text=progress_text)
            
            zip_buffer = io.BytesIO()
            images_traitees = 0
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for i, img_file in enumerate(image_files):
                    processed_bytes = process_image(img_file, logo_img, facteur_taille, opacite, marge)
                    nom_sortie = f"logotisee_{img_file.name}"
                    zip_file.writestr(nom_sortie, processed_bytes)
                    images_traitees += 1
                    
                    my_bar.progress((i + 1) / len(image_files), text=f"Traitement de {img_file.name}...")
            
            st.success(f"✌️ Traitement réussi ! {images_traitees} photo(s) siglée(s).")
            
            st.download_button(
                label="✅ Télécharger les photos (Fichier ZIP)",
                data=zip_buffer.getvalue(),
                file_name="KeaJJ_Photos_Logotisees.zip",
                mime="application/zip",
                use_container_width=True
            )

st.markdown("---")
st.markdown("""
### 🔒 Confidentialité des données
Le traitement est **100% temporaire** et toutes les images sont **immédiatement supprimées** de la mémoire une fois votre fichier ZIP téléchargé ou la page fermée.*
""")