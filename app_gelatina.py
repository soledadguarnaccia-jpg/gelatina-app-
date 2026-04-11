import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
from io import BytesIO

st.set_page_config(page_title="Gelatina Noticias", layout="centered")
st.title("Gelatina Noticias – Generador de Placas")

modo = st.radio("1. Elegí el modo", ["SERIO – Azul/Rojo", "SOLEMNE – Blanco y Negro"], horizontal=True)
uploaded_file = st.file_uploader("2. Subí la foto 4:5", type=["jpg","png","jpeg"])
logo_file = st.file_uploader("3. Subí logo SOLO si tu foto NO lo tiene", type=["png"])
tag = st.text_input("4. Tag / Categoría", "TECNOLOGIA").upper()
titulo = st.text_area("5. Titular", "Estudiantes de Universidad de La Rioja crean un robot humanoide")
bajada = st.text_input("6. Bajada – máx 2 líneas", "Creado por estudiantes riojanos")
fecha = st.text_input("7. Fecha SOLO si tu foto NO la tiene", "")

if st.button("Generar placa") and uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    W, H = 1080, 1350
    
    if "SOLEMNE" in modo: 
        img = ImageOps.grayscale(img).convert("RGB")
    
    img_ratio = img.width / img.height
    target_ratio = W / (H * 0.65)
    if img_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))
    img = img.resize((W, int(H * 0.65)))
    
    canvas = Image.new("RGB", (W, H), "#FFFFFF")
    canvas.paste(img, (0, 0))
    draw = ImageDraw.Draw(canvas)
    
    # FUENTES CON NEGRITA SIMULADA Y SOPORTE DE TILDES
    try:
        font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_bajada = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        # Fallback: usa default pero con stroke para simular negrita
        font_tag = ImageFont.load_default(size=36)
        font_titulo = ImageFont.load_default(size=72)
        font_bajada = ImageFont.load_default(size=42)
        font_fecha = ImageFont.load_default(size=32)
    
    zocalo_y = int(H * 0.65)
    draw.rectangle([(0, zocalo_y), (W, H)], fill="#F8F7F4")
    
    if "SOLEMNE" in modo:
        color_tag_fondo, color_tag_texto, color_titulo, color_bajada = "#000000", "#FFFFFF", "#000000", "#1E1E1E"
        draw.rectangle([(0, zocalo_y), (W, zocalo_y + 3)], fill="#000000")
    else:
        color_tag_fondo, color_tag_texto, color_titulo, color_bajada = "#1A237E", "#FFFFFF", "#1E1E1E", "#4A4A4A"
    
    # Tag - sacamos tildes para evitar el ⌧
    tag = tag.replace("Í","I").replace("Á","A").replace("É","E").replace("Ó","O").replace("Ú","U")
    tag_padding_x, tag_padding_y = 24, 12
    tag_bbox = draw.textbbox((0,0), tag, font=font_tag)
    tag_w = tag_bbox[2] - tag_bbox[0] + tag_padding_x*2
    tag_h = tag_bbox[3] - tag_bbox[1] + tag_padding_y*2
    draw.rectangle([(40, zocalo_y + 40), (40 + tag_w, zocalo_y + 40 + tag_h)], fill=color_tag_fondo)
    draw.text((40 + tag_padding_x, zocalo_y + 40 + tag_padding_y), tag, font=font_tag, fill=color_tag_texto)
    
    # Titular con negrita simulada usando stroke
    y_text = zocalo_y + 40 + tag_h + 40
    for line in textwrap.wrap(titulo, width=18):
        # stroke_width=1 simula negrita si la fuente no es bold
        draw.text((40, y_text), line, font=font_titulo, fill=color_titulo, stroke_width=1, stroke_fill=color_titulo)
        y_text += 82
    
    # Bajada
    y_text += 20
    for line in textwrap.wrap(bajada, width=28)[:2]:
        draw.text((40, y_text), line, font=font_bajada, fill=color_bajada)
        y_text += 52
    
    # Logo SOLO si lo subís
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        logo.thumbnail((140, 140))
        canvas.paste(logo, (40, 40), logo)
    
    # Fecha SOLO si la completás
    if fecha:
        fecha_w = draw.textbbox((0,0), fecha, font=font_fecha)[2]
        draw.text((W - fecha_w - 40, 40), fecha, font=font_fecha, fill="white", stroke_width=1, stroke_fill="black")
    
    st.image(canvas)
    buf = BytesIO()
    canvas.save(buf, format="PNG")
    nombre_archivo = f"gelatina_{modo.split()[0].lower()}_{tag.lower()}.png"
    st.download_button("Descargar PNG 1080x1350", buf.getvalue(), nombre_archivo, "image/png")
