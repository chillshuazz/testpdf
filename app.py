import streamlit as st
import io
import qrcode
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from datetime import datetime
from PIL import Image

def generate_qr_image(url):
    """Genera una imagen QR desde una URL y la guarda en un archivo temporal"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.convert("RGB")
    
    # Guardar en archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name)
    temp_file.close()
    return temp_file.name

def create_professional_pdf(datos):
    """Crea un PDF con diseño profesional similar al original"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesizes=letter)
    width, height = letter
    
    # === MÁRGENES Y CONFIGURACIÓN ===
    margin = 40
    content_width = width - 2*margin
    
    # === ENCABEZADO: EMPRESA (con línea separadora) ===
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, height - 35, "CHILENA DE REVISIONES TECNICAS SPA")
    c.setFont("Helvetica", 7)
    c.drawString(margin, height - 46, "LO BLANCO 1789 LA PINTANA")
    c.drawString(margin, height - 56, f"Planta: {datos['planta']}   Teléfono: {datos['telefono']}")
    
    # Línea horizontal debajo del encabezado
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(margin, height - 65, width - margin, height - 65)
    
    # === TÍTULO CENTRAL ===
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, height - 45, "CERTIFICADO DE INSPECCION VISUAL")
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, height - 60, f"Nº{datos['numero_certificado']}")
    
    # === QR CODE (esquina superior derecha) ===
    qr_temp_path = None
    try:
        if datos['qr_url']:
            qr_temp_path = generate_qr_image(datos['qr_url'])
            c.drawImage(qr_temp_path, width - margin - 60, height - 95, width=55, height=55)
            c.setFont("Helvetica", 5)
            c.drawCentredString(width - margin - 32, height - 102, "SCAN QR")
    except Exception as e:
        st.warning(f"No se pudo generar el QR: {e}")
    
    # Línea vertical separadora QR
    c.line(width - margin - 70, height - 35, width - margin - 70, height - 95)
    
    y_pos = height - 115
    
    # === TEXTO INTRODUCTORIO (con recuadro) ===
    c.setFont("Helvetica", 7)
    intro = "Certifico que el vehículo más abajo individualizado, ha sido inspeccionado visualmente de acuerdo al procedimiento establecido en el Manual de Procedimientos e Interpretación de Resultados, determinándose que el vehículo inspeccionado presenta las siguientes características y números identificatorios:"
    lines = simpleSplit(intro, "Helvetica", 7, content_width - 20)
    
    # Dibujar recuadro alrededor del texto introductorio
    text_height = len(lines) * 9 + 10
    c.rect(margin, y_pos - text_height, content_width, text_height + 5)
    
    for i, line_text in enumerate(lines):
        c.drawString(margin + 5, y_pos - i*9, line_text)
    
    y_pos -= text_height + 20
    
    # === SECCIÓN: IDENTIFICACIÓN DEL VEHÍCULO ===
    # Título de sección con fondo
    c.setFillColor(colors.lightgrey)
    c.rect(margin, y_pos - 15, content_width, 15, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin + 5, y_pos - 12, "IDENTIFICACION DEL VEHICULO")
    y_pos -= 30
    
    # === TABLA DE DATOS DEL VEHÍCULO (con líneas) ===
    c.setFont("Helvetica-Bold", 7)
    
    # Definir columnas: (label, value, x_label, x_value)
    campos = [
        ("Patente:", datos['patente'], "Tipo Vehículo:", datos['tipo_vehiculo']),
        ("Marca:", datos['marca'], "Modelo:", datos['modelo']),
        ("Año:", datos['año'], "N° VIN:", datos['vin']),
        ("N° Motor:", datos['numero_motor'], "N° Chasis:", datos['numero_chasis']),
        ("Color:", datos['color'], "Cilindrada:", datos['cilindrada']),
        ("N° Asientos:", datos['asientos'], "N° Puertas:", datos['puertas']),
        ("Combustible:", datos['tipo_combustible'], "Tracción:", datos['traccion']),
        ("Peso Bruto (Kg):", datos['peso_bruto'], "Corridas Asientos:", datos['corridas_asientos']),
        ("Disp. Ejes:", datos['disposicion_ejes'], "Carrocería:", datos['carroceria']),
        ("Juzgado:", datos['juzgado'], "Causa Rol:", datos['causa_rol']),
    ]
    
    # Dibujar tabla con líneas
    table_x = [margin, 150, 300, width - margin]
    
    for i, (lbl1, val1, lbl2, val2) in enumerate(campos):
        row_y_top = y_pos - i*14
        row_y_bottom = row_y_top - 14
        
        # Líneas horizontales
        c.line(margin, row_y_top, width - margin, row_y_top)
        
        # Columna 1: Label
        c.setFont("Helvetica-Bold", 7)
        c.drawString(margin + 3, row_y_top - 9, lbl1)
        c.setFont("Helvetica", 7)
        c.drawString(margin + 3, row_y_top - 9 + 10, str(val1)[:25])  # Truncar si es muy largo
        
        # Columna 2: Label
        c.setFont("Helvetica-Bold", 7)
        c.drawString(303, row_y_top - 9, lbl2)
        c.setFont("Helvetica", 7)
        c.drawString(303, row_y_top - 9 + 10, str(val2)[:35])
    
    # Línea final de la tabla
    final_row = y_pos - len(campos)*14
    c.line(margin, final_row, width - margin, final_row)
    y_pos = final_row - 25
    
    # === SECCIÓN: IDENTIFICACIÓN PETICIONARIO ===
    c.setFillColor(colors.lightgrey)
    c.rect(margin, y_pos - 15, content_width, 15, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin + 5, y_pos - 12, "IDENTIFICACION PETICIONARIO")
    y_pos -= 30
    
    c.setFont("Helvetica-Bold", 7)
    c.drawString(margin, y_pos, f"Nombre:")
    c.setFont("Helvetica", 7)
    c.drawString(margin + 40, y_pos, datos['propietario'][:60])
    y_pos -= 12
    
    c.setFont("Helvetica-Bold", 7)
    c.drawString(margin, y_pos, f"Domicilio:")
    c.setFont("Helvetica", 7)
    c.drawString(margin + 45, y_pos, datos['domicilio'][:55])
    
    c.setFont("Helvetica-Bold", 7)
    c.drawString(350, y_pos, f"Teléfono:")
    c.setFont("Helvetica", 7)
    c.drawString(400, y_pos, datos['telefono_propietario'])
    y_pos -= 25
    
    # === SECCIÓN: OBSERVACIONES (con recuadro) ===
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y_pos, "OBSERVACIONES:")
    y_pos -= 18
    
    # Recuadro para observaciones
    obs_height = 40
    c.rect(margin, y_pos - obs_height, content_width, obs_height)
    c.setFont("Helvetica", 7)
    obs_lines = simpleSplit(datos['observaciones'], "Helvetica", 7, content_width - 10)
    for i, obs_line in enumerate(obs_lines[:4]):  # Máximo 4 líneas
        c.drawString(margin + 5, y_pos - 8 - i*9, obs_line)
    
    y_pos -= obs_height + 25
    
    # === FECHA Y LUGAR ===
    c.setFont("Helvetica", 8)
    c.drawString(margin, y_pos, f"{datos['lugar']}, {datos['fecha']}")
    y_pos -= 30
    
    # === FIRMA ELECTRÓNICA AVANZADA ===
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin, y_pos, "FIRMA ELECTRÓNICA AVANZADA:")
    c.setFont("Helvetica", 8)
    c.drawString(margin, y_pos - 12, datos['firma'])
    c.drawString(margin, y_pos - 24, f"Válido hasta: {datos['validez_firma']}")
    
    # Línea para firma
    c.line(margin, y_pos - 35, margin + 200, y_pos - 35)
    
    # === PIE DE PÁGINA ===
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.grey)
    c.drawCentredString(width/2, 25, f"Revisión Técnica Vehicular - Planta {datos['lugar'].upper()}")
    c.drawCentredString(width/2, 15, f"Documento generado digitalmente - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    c.save()
    buffer.seek(0)
    
    # Limpiar archivo temporal del QR
    if qr_temp_path and os.path.exists(qr_temp_path):
        try:
            os.remove(qr_temp_path)
        except:
            pass
    
    return buffer


def main():
    st.set_page_config(page_title="✏️ Editor Certificados RTV Pro", layout="wide", page_icon="🚗")
    
    st.title("🚗 Editor Profesional de Certificados RTV")
    st.markdown("*Genera certificados con diseño original, líneas, tablas y QR personalizado*")
    st.markdown("---")
    
    with st.form("formulario_profesional"):
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.subheader("🔗 QR Personalizado")
            qr_url = st.text_input("URL para el QR", "https://ejemplo.cl/verificar/CIV030300192")
            st.caption("El QR se generará con esta URL")
            
            st.subheader("🏢 Empresa")
            planta = st.text_input("Planta", "B-1327")
            telefono = st.text_input("Teléfono", "223070813")
            numero_certificado = st.text_input("N° Certificado", "CIV030300192")
            
            st.subheader("🚙 Vehículo")
            patente = st.text_input("Patente", "KH-GJ51")
            marca = st.text_input("Marca", "MAXUS")
            modelo = st.text_input("Modelo", "V80")
            tipo_vehiculo = st.text_input("Tipo Vehículo", "FURGON (CARGA HASTA <= 1.750 KG)")
            año = st.text_input("Año", "2018")
            vin = st.text_input("N° VIN", "LSKG4GC19JA040079")
        
        with col2:
            st.subheader("🔧 Motor/Chasis")
            numero_motor = st.text_input("N° Motor", "19D4N1NYH316K025")
            numero_chasis = st.text_input("N° Chasis", "LSKG4GC19JA040079")
            color = st.text_input("Color", "BLANCO")
            
            st.subheader("⚙️ Especificaciones")
            cilindrada = st.text_input("Cilindrada (cc)", "")
            asientos = st.text_input("N° Asientos", "3")
            puertas = st.text_input("N° Puertas", "3")
            tipo_combustible = st.text_input("Combustible", "DIESEL")
            traccion = st.text_input("Tracción", "Delantera")
            peso_bruto = st.text_input("Peso Bruto (Kg)", "2699")
            corridas_asientos = st.text_input("Corridas Asientos", "1")
            disposicion_ejes = st.text_input("Disposición Ejes", "2 ejes")
            carroceria = st.text_input("Carrocería", "FURGON")
        
        with col3:
            st.subheader("📋 Datos Adicionales")
            juzgado = st.text_input("Juzgado", "")
            causa_rol = st.text_input("Causa Rol", "")
            
            st.subheader("👤 Propietario")
            propietario = st.text_area("Nombre", "INVERSIONES GALLARDO PIZARRO LIMITADA", height=70)
            domicilio = st.text_input("Domicilio", "")
            telefono_prop = st.text_input("Teléfono Propietario", "")
            
            st.subheader("📝 Otros")
            observaciones = st.text_area("Observaciones", "DEBE REINSCRIBIR NUMERO DE MOTOR", height=60)
            lugar = st.text_input("Lugar", "LA PINTANA")
            fecha = st.text_input("Fecha", datetime.now().strftime("%d de %B de %Y"))
            firma = st.text_input("Firma Electrónica", "CRISTIAN VICUÑA SAAVEDRA")
            validez = st.text_input("Válido Hasta", datetime.now().strftime("%d/%m/%Y"))
        
        st.markdown("---")
        generar = st.form_submit_button("🎨 GENERAR PDF PROFESIONAL", type="primary", use_container_width=True)
    
    if generar:
        datos = {
            'qr_url': qr_url,
            'planta': planta, 'telefono': telefono, 'numero_certificado': numero_certificado,
            'patente': patente, 'marca': marca, 'modelo': modelo, 'tipo_vehiculo': tipo_vehiculo,
            'año': año, 'vin': vin, 'numero_motor': numero_motor, 'numero_chasis': numero_chasis,
            'color': color, 'cilindrada': cilindrada, 'asientos': asientos, 'puertas': puertas,
            'tipo_combustible': tipo_combustible, 'traccion': traccion, 'peso_bruto': peso_bruto,
            'corridas_asientos': corridas_asientos, 'disposicion_ejes': disposicion_ejes,
            'carroceria': carroceria, 'juzgado': juzgado, 'causa_rol': causa_rol,
            'propietario': propietario, 'domicilio': domicilio, 'telefono_propietario': telefono_prop,
            'observaciones': observaciones, 'lugar': lugar, 'fecha': fecha,
            'firma': firma, 'validez_firma': validez,
        }
        
        with st.spinner("🎨 Diseñando PDF profesional..."):
            try:
                pdf_buffer = create_professional_pdf(datos)
                st.success("✅ PDF generado con diseño original")
                
                # Vista previa del QR
                if qr_url:
                    st.markdown(f"**🔍 QR generado para:** `{qr_url}`")
                
                st.download_button(
                    label="📥 Descargar PDF Profesional",
                    data=pdf_buffer,
                    file_name=f"Certificado_RT_{patente}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error al generar PDF: {str(e)}")
                st.exception(e)
    
    # Panel de ayuda
    with st.expander("📖 Guía de Uso Rápida"):
        st.markdown("""
        ### ✨ Características Profesionales:
        
        🔹 **Diseño fiel al original**: Líneas, tablas, recuadros y formato oficial
        🔹 **QR Personalizado**: Ingresa cualquier URL y se generará automáticamente
        🔹 **Campos pre-cargados**: Todos tus datos (MAXUS, KH-GJ51, LA PINTANA, etc.)
        🔹 **Fecha automática**: Se actualiza al día de generación
        🔹 **Pie de página profesional**: Incluye timestamp de generación
        
        ### 📋 Pasos:
        1. Modifica los campos que necesites
        2. Ingresa la URL para el QR (opcional)
        3. Haz clic en **GENERAR PDF PROFESIONAL**
        4. Descarga tu certificado listo para usar
        
        > 💡 *Tip: Deja la URL del QR en blanco si no necesitas código QR*
        """)

if __name__ == "__main__":
    main()
