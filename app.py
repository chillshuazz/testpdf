import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from datetime import datetime

def create_editable_pdf(datos):
    """Crea un PDF con los datos modificados"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesizes=letter)
    width, height = letter
    
    # Configurar fuente
    c.setFont("Helvetica", 8)
    
    # === ENCABEZADO - EMPRESA ===
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 40, "CHILENA DE REVISIONES TECNICAS SPA")
    c.setFont("Helvetica", 8)
    c.drawString(50, height - 52, "LO BLANCO 1789 LA PINTANA")
    c.drawString(50, height - 64, f"Planta: {datos['planta']}   Telefono: {datos['telefono']}")
    
    # === TÍTULO DEL CERTIFICADO ===
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, height - 45, "CERTIFICADO DE INSPECCION VISUAL")
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, height - 60, f"Nº{datos['numero_certificado']}")
    
    # QR placeholder
    c.rect(width - 75, height - 85, 55, 55)
    c.setFont("Helvetica", 6)
    c.drawCentredString(width - 47, height - 58, "QR")
    
    y_pos = height - 105
    
    # === TEXTO INTRODUCTORIO ===
    c.setFont("Helvetica", 7)
    intro = "Certifico que el vehículo más abajo individualizado, ha sido inspeccionado visualmente de acuerdo al procedimiento establecido en el Manual de Procedimientos e Interpretación de Resultados, determinándose que el vehículo inspeccionado presenta las siguientes características y números identificatorios:"
    lines = simpleSplit(intro, "Helvetica", 7, width - 100)
    for line in lines:
        c.drawString(50, y_pos, line)
        y_pos -= 10
    
    y_pos -= 15
    
    # === IDENTIFICACIÓN DEL VEHÍCULO ===
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y_pos, "IDENTIFICACION DEL VEHICULO")
    y_pos -= 20
    
    c.setFont("Helvetica-Bold", 7)
    campos = [
        ("Patente:", datos['patente'], "Tipo Vehiculo:", datos['tipo_vehiculo']),
        ("Marca:", datos['marca'], "Modelo:", datos['modelo']),
        ("Año:", datos['año'], "N° VIN:", datos['vin']),
        ("N° Motor:", datos['numero_motor'], "N° Chasis:", datos['numero_chasis']),
        ("Color:", datos['color'], "Cilindrada:", datos['cilindrada']),
        ("N° Asientos:", datos['asientos'], "N° Puertas:", datos['puertas']),
        ("Tipo Combustible:", datos['tipo_combustible'], "Tipo Tracción:", datos['traccion']),
        ("Peso Bruto (Kg):", datos['peso_bruto'], "N° Corridas Asientos:", datos['corridas_asientos']),
        ("N° Disposición Ejes:", datos['disposicion_ejes'], "Tipo Carroceria:", datos['carroceria']),
        ("Juzgado:", datos['juzgado'], "Causa Rol:", datos['causa_rol']),
    ]
    
    for campo1, val1, campo2, val2 in campos:
        if y_pos < 80:
            c.showPage()
            c.setFont("Helvetica-Bold", 7)
            y_pos = height - 50
        
        c.drawString(50, y_pos, campo1)
        c.setFont("Helvetica", 7)
        c.drawString(115, y_pos, str(val1))
        
        c.setFont("Helvetica-Bold", 7)
        c.drawString(280, y_pos, campo2)
        c.setFont("Helvetica", 7)
        c.drawString(360, y_pos, str(val2))
        
        y_pos -= 12
        c.setFont("Helvetica-Bold", 7)
    
    y_pos -= 25
    
    # === IDENTIFICACIÓN PETICIONARIO ===
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y_pos, "IDENTIFICACION PETICIONARIO")
    y_pos -= 18
    
    c.setFont("Helvetica-Bold", 7)
    c.drawString(50, y_pos, f"Nombre: {datos['propietario']}")
    y_pos -= 12
    c.drawString(50, y_pos, f"Domicilio: {datos['domicilio']}")
    c.drawString(350, y_pos, f"Teléfono: {datos['telefono_propietario']}")
    
    y_pos -= 25
    
    # === OBSERVACIONES ===
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y_pos, "OBSERVACIONES:")
    y_pos -= 12
    c.setFont("Helvetica", 7)
    obs_lines = simpleSplit(datos['observaciones'], "Helvetica", 7, width - 100)
    for line in obs_lines:
        c.drawString(50, y_pos, line)
        y_pos -= 10
    
    y_pos -= 30
    
    # === FECHA Y LUGAR ===
    c.setFont("Helvetica", 8)
    c.drawString(50, y_pos, f"{datos['lugar']}, {datos['fecha']}")
    
    # === FIRMA ELECTRÓNICA ===
    y_pos -= 35
    c.setFont("Helvetica-Bold", 8)
    c.drawString(50, y_pos, "FIRMA ELECTRÓNICA AVANZADA:")
    c.setFont("Helvetica", 8)
    c.drawString(50, y_pos - 12, datos['firma'])
    c.drawString(50, y_pos - 24, f"Válido hasta: {datos['validez_firma']}")
    
    # === PIE DE PÁGINA ===
    c.setFont("Helvetica", 6)
    c.drawCentredString(width/2, 30, f"COPIAPO -> {datos['lugar'].upper()}")
    
    c.save()
    buffer.seek(0)
    return buffer


def main():
    st.set_page_config(page_title="✏️ Editor Certificados RTV", layout="wide")
    
    st.title("🚗 Editor de Certificados de Inspección Visual")
    st.markdown("*Modifica fácilmente los datos de tus certificados*")
    st.markdown("---")
    
    with st.form("formulario_edicion"):
        col1, col2 = st.columns(2)
        
        with col1:
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
            vin = st.text_input("N° VIN", "")
            numero_motor = st.text_input("N° Motor", "19D4N1NYH316K025")
            numero_chasis = st.text_input("N° Chasis", "LSKG4GC19JA040079")
            color = st.text_input("Color", "BLANCO")
        
        with col2:
            st.subheader("⚙️ Especificaciones")
            cilindrada = st.text_input("Cilindrada", "")
            asientos = st.text_input("N° Asientos", "")
            puertas = st.text_input("N° Puertas", "")
            tipo_combustible = st.text_input("Combustible", "DIESEL")
            traccion = st.text_input("Tracción", "")
            peso_bruto = st.text_input("Peso Bruto (Kg)", "2699")
            corridas_asientos = st.text_input("Corridas Asientos", "")
            disposicion_ejes = st.text_input("Disposición Ejes", "2 ejes")
            carroceria = st.text_input("Carrocería", "FURGON")
            juzgado = st.text_input("Juzgado", "")
            causa_rol = st.text_input("Causa Rol", "")
            
            st.subheader("👤 Propietario")
            propietario = st.text_area("Nombre", "INVERSIONES GALLARDO PIZARRO LIMITADA")
            domicilio = st.text_input("Domicilio", "")
            telefono_prop = st.text_input("Teléfono", "")
            
            st.subheader("📝 Otros")
            observaciones = st.text_area("Observaciones", "DEBE REINSCRIBIR NUMERO DE MOTOR")
            lugar = st.text_input("Lugar", "LA PINTANA")
            fecha = st.text_input("Fecha", datetime.now().strftime("%d de %B de %Y"))
            firma = st.text_input("Firma", "CRISTIAN VICUÑA SAAVEDRA")
            validez = st.text_input("Válido Hasta", datetime.now().strftime("%d/%m/%Y"))
        
        st.markdown("---")
        generar = st.form_submit_button("📥 GENERAR PDF EDITADO", type="primary")
    
    if generar:
        datos = {
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
        
        with st.spinner("Generando PDF..."):
            try:
                pdf = create_editable_pdf(datos)
                st.success("✅ PDF generado")
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf,
                    file_name=f"Certificado_{patente}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error: {e}")
    
    with st.expander("📖 Instrucciones"):
        st.markdown("""
        1. Completa los campos con los datos que necesitas
        2. Haz clic en **GENERAR PDF EDITADO**
        3. Descarga el archivo resultante
        
        *Todos los campos están pre-configurados con tus datos*
        """)

if __name__ == "__main__":
    main()
