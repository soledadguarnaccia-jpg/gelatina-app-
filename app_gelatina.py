import streamlit as st
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Gelatina", layout="wide")

st.title("🎨 Generador de Piezas Gelatina")
st.write("Elegí un logo precargado o subí el tuyo")

# --- CONFIGURACIÓN DE CARPETAS ---
# Carpeta donde tenés los logos ahora
LOGOS_DIR = Path("activos/logotipos/activos/logotipos")

# --- CARGA DE LOGOS PRECARGADOS ---
logos_disponibles = {"Ninguno": None}

if LOGOS_DIR.exists():
    for archivo in LOGOS_DIR.glob("*.png"):
        if archivo.name == ".gitkeep":
            continue
        # Limpia el nombre: "GELATINA_LOGO AZUL.png" -> "Azul"
        nombre_mostrar = archivo.stem.replace("GELATINA_LOGO", "").strip()
        nombre_mostrar = nombre_mostrar.replace("copia", "").strip()
        if not nombre_mostrar:
            nombre_mostrar = archivo.stem
        logos_disponibles[nombre_mostrar.title()] = str(archivo)

# --- SIDEBAR: CONTROLES ---
with st.sidebar:
    st.header("1. Elegí el logo")
    
    opcion_logo = st.radio(
        "Fuente del logo:",
        ["Usar logo precargado", "Subir mi propio logo"],
        index=0
    )
    
    logo_final = None
    
    if opcion_logo == "Usar logo precargado":
        logo_elegido = st.selectbox(
            "Logos disponibles:",
            options=list(logos_disponibles.keys())
        )
        if logo_elegido!= "Ninguno":
            logo_final = logos_disponibles[logo_elegido]
            st.image(logo_final, caption=f"Preview: {logo_elegido}", width=200)
    else:
        archivo_subido = st.file_uploader("Subí un PNG", type=["png"])
        if archivo_subido:
            logo_final = archivo_subido
            st.image(logo_final, caption="Preview: Logo subido", width=200)
    
    st.divider()
    st.header("2. Texto y estilo")
    texto_principal = st.text_input("Texto principal", "Título Gelatina")
    # ARREGLADO: hex de 6 dígitos
    color_fondo = st.color_picker("Color de fondo", "#1E1E1E")
    color_texto = st.color_picker("Color de texto", "#FFFFFF")
    tamaño_fuente = st.slider("Tamaño de fuente", 20, 120, 60)

# --- ÁREA PRINCIPAL: PREVIEW ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Preview")
    
    # Crear imagen base 1080x1080
    ancho, alto = 1080, 1080
    img_preview = Image.new("RGB", (ancho, alto), color_fondo)
    draw = ImageDraw.Draw(img_preview)
    
    # Si hay logo, lo pegamos arriba centrado
    if logo_final:
        try:
            if isinstance(logo_final, str): # Es un path de logo precargado
                logo_img = Image.open(logo_final).convert("RGBA")
            else: # Es un archivo subido
                logo_img = Image.open(logo_final).convert("RGBA")
            
            # Redimensionar logo a 300px de ancho manteniendo proporción
            logo_img.thumbnail((300, 300))
            pos_x = (ancho - logo_img.width) // 2
            img_preview.paste(logo_img, (pos_x, 100), logo_img)
        except Exception as e:
            st.error(f"Error cargando logo: {e}")
    
    # Agregar texto centrado
    try:
        # Intenta usar una fuente default
        fuente = ImageFont.load_default()
        # Para calcular el tamaño del texto
        bbox = draw.textbbox((0, 0), texto_principal, font=fuente)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (ancho - text_w) // 2
        text_y = alto // 2
        draw.text((text_x, text_y), texto_principal, fill=color_texto, font=fuente)
    except:
        pass
    
    # Mostrar preview
    st.image(img_preview)
    
    # Botón de descarga
    buf = io.BytesIO()
    img_preview.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="⬇️ Descargar PNG",
        data=byte_im,
        file_name="gelatina_pieza.png",
        mime="image/png"
    )

with col2:
    st.subheader("Logos encontrados")
    if len(logos_disponibles) > 1:
        st.success(f"Encontré {len(logos_disponibles)-1} logos precargados")
        for nombre in list(logos_disponibles.keys())[1:]:
            st.write(f"✓ {nombre}")
    else:
        st.warning("No encontré logos en la carpeta")
        st.caption(f"Buscando en: {LOGOS_DIR}")

# --- FOOTER ---
st.divider()
st.caption("Hecho con Streamlit | Gelatina App v1.1")
