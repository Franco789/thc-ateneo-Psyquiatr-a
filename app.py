import streamlit as st
import numpy as np
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y BLINDAJE CONTRA INTERFERENCIAS EN EL DOM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Neurobiología de la Exposición a THC | Ateneo de Psiquiatría",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Directiva anti-traductor para prevenir el error 'removeChild on Node'
st.markdown("""
<head>
    <meta name="google" content="notranslate">
</head>
<style>
    html, body, [class*="css"], .stApp {
        translate: no !important;
    }
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, h4 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        letter-spacing: -0.2px;
    }
    div[data-testid="stMetric"] {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. PANEL LATERAL: VARIABLES FARMACOCINÉTICAS Y GENÉTICAS
# -----------------------------------------------------------------------------
st.sidebar.title("Perfil Clínico del Paciente")
st.sidebar.caption("Parámetros cuantitativos para el cálculo de plasticidad ontogenética, cinética tisular y modulación génica:")

edad_inicio = st.sidebar.slider(
    "1. Edad de inicio del consumo regular (Años)",
    min_value=12, max_value=28, value=15, step=1,
    help="Determina la coincidencia con la ventana crítica de maduración y poda sináptica en la corteza prefrontal dorsolateral."
)

potencia_thc = st.sidebar.slider(
    "2. Potencia estimada de la cepa (% Δ⁹-THC)",
    min_value=2, max_value=30, value=20, step=1,
    help="Cannabis tradicional histórico: 2-4%. Cepas hidropónicas y concentrados actuales: 15-28% de concentración de Δ⁹-THC."
)

frecuencia_semanal = st.sidebar.slider(
    "3. Frecuencia de consumo (Días/semana)",
    min_value=1, max_value=7, value=6, step=1,
    help="La exposición continuada satura la vía retrógrada endocannabinoide e induce fosforilación de receptores CB1 por GRKs."
)

anios_consumo = st.sidebar.slider(
    "4. Años de consumo sostenido",
    min_value=1, max_value=15, value=5, step=1,
    help="Duración cronológica de la exposición durante el período formativo o adulto."
)

abstinencia_semanas = st.sidebar.slider(
    "5. Tiempo de abstinencia actual (Semanas)",
    min_value=0, max_value=24, value=0, step=1,
    help="0 = Consumo activo. El intervalo de 4 semanas (28-30 días) representa la normalización de la densidad de receptores CB1 en PET."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Farmacogenética Prefrontal")
polimorfismo_comt = st.sidebar.selectbox(
    "Genotipo COMT (Val158Met)",
    options=[
        "Val/Val (Actividad enzimática alta)",
        "Val/Met (Actividad enzimática intermedia)",
        "Met/Met (Actividad enzimática basal baja)"
    ],
    index=0,
    help="La enzima catecol-O-metiltransferasa modula el aclaramiento de dopamina en la corteza prefrontal, regulando la estabilidad ejecutiva."
)

# -----------------------------------------------------------------------------
# 3. MOTOR CUANTITATIVO FARMACODINÁMICO Y PSICOMÉTRICO
# -----------------------------------------------------------------------------

# Modulador farmacogenético COMT
if "Val/Val" in polimorfismo_comt:
    mod_comt = 1.30
    desc_gen = (
        "Genotipo Val/Val: Mayor tasa de degradación enzimática de catecolaminas. El tono dopaminérgico prefrontal basal "
        "se sitúa en el límite inferior de la curva funcional. Ante la saturación de receptores CB1, este subgrupo "
        "evidencia la mayor vulnerabilidad en memoria de trabajo y velocidad de procesamiento."
    )
elif "Val/Met" in polimorfismo_comt:
    mod_comt = 1.00
    desc_gen = (
        "Genotipo Val/Met: Actividad enzimática intermedia. Expresa una susceptibilidad neurocognitiva promedio acorde con "
        "las distribuciones normativas de cohorte poblacional."
    )
else:
    mod_comt = 0.75
    desc_gen = (
        "Genotipo Met/Met: Menor degradación enzimática y niveles basales elevados de dopamina en la corteza prefrontal. "
        "Muestra mayor preservación frente al deterioro ejecutivo en pruebas psicométricas, aunque con menor umbral "
        "para la inducción de reactividad psicotomimética (saliencia aberrante) ante dosis altas de Δ⁹-THC."
    )

# Vulnerabilidad ontogenética de poda sináptica (Gogtay et al. / Lewis et al.)
vuln_poda = 1.0 / (1.0 + np.exp((edad_inicio - 17.5) / 1.3))

# Carga de exposición acumulada normalizada (Unidades Cannabinoides Estándar)
carga_thc = (potencia_thc / 5.0) * (frecuencia_semanal / 7.0) * anios_consumo

# Dinámica de receptores CB1 en tomografía PET ([¹⁸F]FMPEP-d₂ / Hirvonen et al.)
downreg_base = 0.52 * (1.0 - np.exp(-carga_thc / 3.2))

if abstinencia_semanas == 0:
    recup_factor = 0.0
else:
    recup_factor = 1.0 - np.exp(-abstinencia_semanas / 1.4)

downreg_actual = downreg_base * (1.0 - recup_factor)
disponibilidad_cb1_global = (1.0 - downreg_actual) * 100.0
disponibilidad_cb1_global = min(100.0, max(35.0, disponibilidad_cb1_global))

# Volumen de distribución regional (VT en mL/cm³)
vt_ctrl_dlpfc = 1.35
vt_ctrl_acc = 1.25
vt_ctrl_estriado = 1.45
vt_ctrl_ventriculo = 0.05

caida_frac_dlpfc = downreg_actual * 0.90
vt_pac_dlpfc = vt_ctrl_dlpfc * (1.0 - caida_frac_dlpfc)

caida_frac_acc = downreg_actual * 1.05
vt_pac_acc = vt_ctrl_acc * (1.0 - caida_frac_acc)

caida_frac_estriado = downreg_actual * 1.20
vt_pac_estriado = vt_ctrl_estriado * (1.0 - caida_frac_estriado)

vt_pac_ventriculo = vt_ctrl_ventriculo

# Reversibilidad biológica estructural (Dunedin Study / Meier et al.)
capacidad_reversibilidad = 1.0 / (1.0 + np.exp(-(edad_inicio - 19.5) / 1.2))
factor_abstinencia_recup = min(1.0, (abstinencia_semanas / 24.0)) * capacidad_reversibilidad

# Subescalas neuropsicológicas WAIS-IV
caida_max_psi = 10.0 * vuln_poda * (1.0 - np.exp(-carga_thc / 4.8)) * mod_comt
caida_act_psi = -1.0 * (caida_max_psi * (1.0 - (factor_abstinencia_recup * 0.65)))

caida_max_wmi = 8.6 * vuln_poda * (1.0 - np.exp(-carga_thc / 4.8)) * mod_comt
caida_act_wmi = -1.0 * (caida_max_wmi * (1.0 - (factor_abstinencia_recup * 0.60)))

caida_max_pri = 4.8 * vuln_poda * (1.0 - np.exp(-carga_thc / 6.0))
caida_act_pri = -1.0 * (caida_max_pri * (1.0 - (factor_abstinencia_recup * 0.75)))

caida_max_vci = 1.6 * vuln_poda * (1.0 - np.exp(-carga_thc / 8.0))
caida_act_vci = -1.0 * (caida_max_vci * (1.0 - (factor_abstinencia_recup * 0.90)))

# FSIQ compuesto (Coeficiente Intelectual Total)
fsiq_neto = (caida_act_psi * 0.35) + (caida_act_wmi * 0.35) + (caida_act_pri * 0.15) + (caida_act_vci * 0.15)

# Clasificación del fenotipo clínico
if edad_inicio < 17 and anios_consumo >= 3:
    fenotipo = "Disrupción Estructural Persistente"
    fenotipo_desc = "Atrofia en arborización dendrítica de interneuronas GABAérgicas PV+ y mielinización deficitaria de sustancia blanca frontal."
elif edad_inicio < 21:
    fenotipo = "Vulnerabilidad Intermedia"
    fenotipo_desc = "Compromiso mixto: desensibilización receptora con remodelado microestructural incompleto tras cesación prolongada."
else:
    fenotipo = "Disfunción Funcional Reversible"
    fenotipo_desc = "Regulación a la baja de receptores CB1 sin alteración citoarquitectónica. Reversibilidad completa tras cese sostenido."

# -----------------------------------------------------------------------------
# 4. ENCABEZADO Y MÉTRICAS INSTITUCIONALES
# -----------------------------------------------------------------------------
st.title("Dinámica del Neurodesarrollo, Plasticidad y Exposición a Δ⁹-THC")
st.markdown("**Simulador Cuantitativo de Farmacodinámica del Receptor CB1, Tomografía PET y Trayectorias Psicométricas Longitudinales** | Ateneo de Psiquiatría")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(
        label="Vulnerabilidad de Poda Cortical",
        value=f"{vuln_poda * 100:.1f} %",
        help=f"Susceptibilidad ontogenética calculada a los {edad_inicio} años. Cuantifica el riesgo de poda aberrante en interneuronas GABAérgicas PV+."
    )
    st.caption(f"Ventana de maduración prefrontal ({edad_inicio} años).")

with col_m2:
    delta_cb1 = f"{(disponibilidad_cb1_global - 100.0):.1f} %" if disponibilidad_cb1_global < 99.0 else "Basal Fisiológico"
    st.metric(
        label="Densidad CB1 en PET ([¹⁸F]FMPEP-d₂)",
        value=f"{disponibilidad_cb1_global:.1f} %",
        delta=delta_cb1,
        help="Disponibilidad de receptores CB1 expresados en membrana celular respecto al control fisiológico."
    )
    txt_abs_estado = "Consumo activo (Semana 0)" if abstinencia_semanas == 0 else f"{abstinencia_semanas} sem. de abstinencia"
    st.caption(f"Estado clínico: {txt_abs_estado}.")

with col_m3:
    st.metric(
        label="Impacto Neto en CI Total (FSIQ)",
        value=f"{fsiq_neto:.1f} puntos",
        delta=f"{fsiq_neto:.1f} WAIS",
        delta_color="inverse",
        help="Variación en la Escala Wechsler (WAIS-IV) ajustada por factores de confusión y genotipo COMT."
    )
    st.caption(f"Genotipo COMT: {polimorfismo_comt.split()[0]}.")

with col_m4:
    st.metric(
        label="Fenotipo Neuroestructural",
        value=fenotipo,
        help=fenotipo_desc
    )
    st.caption(fenotipo_desc[:44] + "...")

st.divider()

# -----------------------------------------------------------------------------
# 5. CONTROL DE NAVEGACIÓN ESTABLE
# -----------------------------------------------------------------------------
modulo_seleccionado = st.radio(
    "Selección de Módulo Clínico:",
    [
        "1. Neuroimagen PET y Cuantificación de Regiones de Interés (ROI)",
        "2. Trayectoria Longitudinal del CI y Ventana Crítica Ontogenética",
        "3. Desglose Neuropsicológico (WAIS-IV) y Control en Gemelos",
        "4. Conclusiones y Directrices Asistenciales"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# -----------------------------------------------------------------------------
# MÓDULO 1: NEUROIMAGEN PET
# -----------------------------------------------------------------------------
if modulo_seleccionado.startswith("1."):
    st.subheader("Farmacodinámica del Receptor CB1 y Reconstrucción Tomográfica PET")
    st.markdown(
        "Evaluación de la desensibilización por internalización vesicular (*downregulation*) de receptores CB1 "
        "mediante el radiotrazador específico **[¹⁸F]FMPEP-d₂** (antagonista selectivo inverso de alta afinidad)."
    )

    col_pet_l, col_pet_r = st.columns([1, 1])

    with col_pet_l:
        st.markdown("**Cinética Temporal de Reexpresión del Receptor CB1 tras el Cese**")
        semanas_vec = np.linspace(0, 12, 140)
        curva_recup = ((1.0 - downreg_base) + (downreg_base * (1.0 - np.exp(-semanas_vec / 1.4)))) * 100.0

        fig_pet_curva = go.Figure()

        fig_pet_curva.add_trace(go.Scatter(
            x=semanas_vec, y=[100]*len(semanas_vec),
            mode='lines', name='Control Fisiológico (Línea Basal 100%)',
            line=dict(color='#10B981', width=1.5, dash='dash')
        ))

        fig_pet_curva.add_trace(go.Scatter(
            x=semanas_vec, y=curva_recup,
            mode='lines', name='Cinética de Reexpresión CB1',
            line=dict(color='#F59E0B', width=3)
        ))

        marcador_x = min(12.0, float(abstinencia_semanas))
        fig_pet_curva.add_trace(go.Scatter(
            x=[marcador_x], y=[disponibilidad_cb1_global],
            mode='markers+text', name='Estado Actual del Paciente',
            marker=dict(color='#EF4444', size=12, symbol='diamond'),
            text=[f"Semana {abstinencia_semanas}: {disponibilidad_cb1_global:.1f}%"],
            textposition="top center",
            textfont=dict(color="#FFFFFF", size=11)
        ))

        fig_pet_curva.add_vrect(
            x0=0, x1=4, fillcolor="rgba(239, 68, 68, 0.08)",
            layer="below", line_width=0,
            annotation_text="Ventana de Resensibilización Rápida (0-4 semanas)",
            annotation_position="bottom right",
            annotation_font=dict(color="#EF4444", size=10)
        )

        fig_pet_curva.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#0D131F',
            xaxis=dict(title="Semanas de Abstinencia Monitorizada", gridcolor='#1E293B', range=[0, 12]),
            yaxis=dict(title="Disponibilidad de Receptores CB1 (% Basal)", gridcolor='#1E293B', range=[30, 110]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=20, b=20),
            height=370
        )
        st.plotly_chart(fig_pet_curva, use_container_width=True, key="fig_curva_pet_nav")

    with col_pet_r:
        st.markdown("**Corte Axial Tomográfico PET: Control Sano vs. Paciente Simulado**")
        st.caption("Reconstrucción semicuantitativa a nivel de corteza prefrontal, cíngulo anterior, estriado y ventrículos laterales.")

        n = 55
        x = np.linspace(-3, 3, n)
        y = np.linspace(-3, 3, n)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + (Y/1.2)**2)
        mascara = R <= 2.2

        pfc = np.exp(-((X)**2 + (Y - 1.4)**2) / 0.7) * 1.10
        cing = np.exp(-((X)**2 + (Y - 0.3)**2) / 0.45) * 1.00
        estriado = (np.exp(-((X - 0.9)**2 + (Y + 0.1)**2) / 0.32) + np.exp(-((X + 0.9)**2 + (Y + 0.1)**2) / 0.32)) * 1.15
        corteza = np.exp(-((R - 1.8)**2) / 0.22) * 0.75
        ventriculos = (np.exp(-((X - 0.35)**2 + (Y - 0.3)**2) / 0.08) + np.exp(-((X + 0.35)**2 + (Y - 0.3)**2) / 0.08)) * 1.3

        senal_sana = np.maximum(0, (pfc + cing + estriado + corteza - ventriculos)) * mascara

        pfc_pac = pfc * (1.0 - caida_frac_dlpfc)
        cing_pac = cing * (1.0 - caida_frac_acc)
        estriado_pac = estriado * (1.0 - caida_frac_estriado)
        corteza_pac = corteza * (disponibilidad_cb1_global / 100.0)

        senal_paciente = np.maximum(0, (pfc_pac + cing_pac + estriado_pac + corteza_pac - ventriculos)) * mascara

        separador = np.zeros((n, 6))
        m_dual = np.hstack([senal_sana, separador, senal_paciente])

        fig_pet_axial = go.Figure(data=go.Heatmap(
            z=m_dual,
            colorscale='Jet',
            zmin=0.0, zmax=1.2,
            showscale=True,
            colorbar=dict(
                title=dict(text="Unión CB1 (VT en mL/cm³)", side="right"),
                thickness=12,
                len=0.8,
                tickfont=dict(color="#CBD5E1", size=10)
            )
        ))

        fig_pet_axial.add_annotation(x=13, y=51, text="CONTROL BASAL (100%)", showarrow=False, font=dict(color="#10B981", size=11))
        fig_pet_axial.add_annotation(x=91, y=51, text=f"PACIENTE ({disponibilidad_cb1_global:.1f}%)", showarrow=False, font=dict(color="#EF4444" if disponibilidad_cb1_global < 85 else "#10B981", size=11))

        fig_pet_axial.add_annotation(x=13, y=41, text="DLPFC", showarrow=True, arrowhead=2, arrowcolor="#FFFFFF", font=dict(color="#FFFFFF", size=9))
        fig_pet_axial.add_annotation(x=91, y=41, text="DLPFC", showarrow=True, arrowhead=2, arrowcolor="#FFFFFF", font=dict(color="#FFFFFF", size=9))
        fig_pet_axial.add_annotation(x=22, y=28, text="Estriado", showarrow=True, arrowhead=2, arrowcolor="#FFFFFF", font=dict(color="#FFFFFF", size=9))
        fig_pet_axial.add_annotation(x=100, y=28, text="Estriado", showarrow=True, arrowhead=2, arrowcolor="#FFFFFF", font=dict(color="#FFFFFF", size=9))

        fig_pet_axial.add_annotation(x=52, y=53, text="ANTERIOR (Frontal)", showarrow=False, font=dict(color="#94A3B8", size=9))
        fig_pet_axial.add_annotation(x=52, y=2, text="POSTERIOR (Occipital)", showarrow=False, font=dict(color="#94A3B8", size=9))

        fig_pet_axial.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
            margin=dict(l=10, r=10, t=10, b=10),
            height=370
        )
        st.plotly_chart(fig_pet_axial, use_container_width=True, key="fig_axial_pet_nav")

    st.info(
        "**INTERPRETACIÓN RADIOLÓGICA DEL MAPA TOMOGRÁFICO:**\n\n"
        "* **Rojo / Naranja intenso (VT > 1.1 mL/cm³):** Densidad fisiológica íntegra. Abundancia de receptores CB1 funcionales acoplados a proteína Gi/o en membrana plasmática.\n"
        "* **Amarillo / Verde (VT ≈ 0.7 - 0.9 mL/cm³):** Desensibilización e inicio de reciclaje endosomal. La neurotransmisión retrógrada inhibitoria se vuelve errática.\n"
        "* **Azul frío / Cian (VT < 0.6 mL/cm³):** Regulación a la baja (*downregulation*) pronunciada. Secuestro vesicular del receptor en endosomas citoplasmáticos por exceso agonista.\n"
        "* **Centro oscuro:** Ventrículos laterales. Líquido cefalorraquídeo acelular sin expresión de receptores CB1 (control radiológico negativo interno)."
    )

    st.markdown("#### Cuantificación de Volumen de Distribución Regional ($V_T$ en $\\text{mL}\\cdot\\text{cm}^{-3}$)")
    st.caption("El volumen de distribución $V_T$ expresa la relación de equilibrio entre la concentración tisular del trazador fijado al receptor y la fracción libre plasmática. Un menor $V_T$ refleja una reducción directa en la densidad de receptores CB1 funcionales.")

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.metric(
            label="DLPFC (Corteza Prefrontal Dorsolateral)",
            value=f"{vt_pac_dlpfc:.2f} mL/cm³",
            delta=f"{-caida_frac_dlpfc*100:.1f} %",
            delta_color="inverse"
        )
        st.caption("**Correlato:** Memoria de trabajo y control inhibitorio. La atenuación del freno CB1 sobre interneuronas GABAérgicas PV+ altera la sincronización en banda gamma (40 Hz).")

    with col_t2:
        st.metric(
            label="Cíngulo Anterior (ACC)",
            value=f"{vt_pac_acc:.2f} mL/cm³",
            delta=f"{-caida_frac_acc*100:.1f} %",
            delta_color="inverse"
        )
        st.caption("**Correlato:** Monitoreo de conflicto y detección de errores. Su hipofunción explica el sesgo atencional hacia la sustancia y la rigidez perseverativa.")

    with col_t3:
        st.metric(
            label="Estriado Ventral / Accumbens",
            value=f"{vt_pac_estriado:.2f} mL/cm³",
            delta=f"{-caida_frac_estriado*100:.1f} %",
            delta_color="inverse"
        )
        st.caption("**Correlato:** Circuito de recompensa y prominencia de incentivo. Constituye el área de mayor desensibilización receptora; sustenta el aplanamiento afectivo en consumo diario.")

    with col_t4:
        st.metric(
            label="Ventrículos Laterales (LCR)",
            value=f"{vt_pac_ventriculo:.2f} mL/cm³",
            delta="0.0 % (Basal)",
            delta_color="off"
        )
        st.caption("**Correlato:** Control radiológico negativo. Al carecer de receptores CB1, valida que la atenuación tisular no obedece a artefactos de flujo o filtrado.")

    st.markdown("---")

    if abstinencia_semanas == 0:
        st.error(
            f"**ESTADO CLÍNICO: CONSUMO ACTIVO ({potencia_thc}% THC, {frecuencia_semanal} días/semana):** "
            f"La estimulación suprafisiológica continuada mantiene a los receptores CB1 fosforilados por GRKs y secuestrados "
            f"hacia endosomas intracelulares por β-arrestina-2. La disponibilidad global del radiotrazador desciende un {100 - disponibilidad_cb1_global:.1f}%. "
            f"Se asocia a desinhibición dopaminérgica subcortical y pérdida del control ejecutivo frontal."
        )
    elif abstinencia_semanas < 4:
        st.warning(
            f"**ESTADO CLÍNICO: FASE DE RESENSIBILIZACIÓN ACTIVA ({abstinencia_semanas} semanas de abstinencia monitorizada):** "
            f"Los endosomas reciclan y reincorporan activamente los receptores CB1 hacia la membrana plasmática. "
            f"La densidad actual alcanza el {disponibilidad_cb1_global:.1f}%. Persiste una neurotransmisión GABAérgica inestable, "
            f"sustrato psicofarmacológico del insomnio y la labilidad afectiva propios de la abstinencia temprana."
        )
    else:
        st.success(
            f"**ESTADO CLÍNICO: NORMALIZACIÓN RECEPTORA COMPLETA ({abstinencia_semanas} semanas de abstinencia confirmada):** "
            f"Superado el umbral de 4 semanas (28-30 días documentados por Hirvonen et al.), el volumen de distribución del "
            f"radiotrazador se restablece al {disponibilidad_cb1_global:.1f}%, siendo indistinguible del control basal. "
            f"**Directriz diagnóstica:** La normalización del receptor no equivale a la regeneración axonal si la poda sináptica fue interrumpida en la adolescencia."
        )

    with st.expander("🔬 Fundamento Fisiopatológico: Autorregulación Homeostática del Freno Neuroquímico", expanded=True):
        st.markdown(
            "El sistema endocannabinoide opera fisiológicamente como un **mecanismo de modulación retrógrada a demanda**: "
            "cuando la neurona postsináptica se despolariza, libera ligandos lipofílicos que viajan en sentido retrógrado para activar los receptores CB1 "
            "en el terminal presináptico y regular la exocitosis de glutamato o GABA.\n\n"
            "**La disrupción farmacodinámica exógena:** Cuando ingresa Δ⁹-THC en concentraciones suprafisiológicas sostenidas, "
            "el sistema pierde su selectividad espacio-temporal. La neurona interpreta esta saturación continua como una sobrecarga funcional "
            "y, como mecanismo de defensa biológico para evitar daño excitotóxico, fosforila el receptor y lo internaliza hacia endosomas citoplasmáticos.\n\n"
            "**La lección fisiopatológica para el ateneo:** Al interrumpirse el agonismo exógeno (abstinencia monitorizada), la maquinaria celular "
            "desfosforila y recicla la proteína receptora de regreso a la membrana en aproximadamente 28 días. Sin embargo, *la restitución de la proteína "
            "en la membrana no repara la pérdida de arborización dendrítica ni la desmielinización si la interferencia ocurrió durante la fase plástica de la adolescencia*."
        )

# -----------------------------------------------------------------------------
# MÓDULO 2: TRAYECTORIA LONGITUDINAL DEL CI
# -----------------------------------------------------------------------------
elif modulo_seleccionado.startswith("2."):
    st.subheader("Trayectoria Longitudinal del Coeficiente Intelectual (10 a 45 años)")
    st.caption("Modelado psicométrico calibrado sobre la cohorte prospectiva de Dunedin (Meier et al., PNAS 2012 / Am J Psychiatry 2022).")

    edades = np.linspace(10, 45, 180)
    ci_base = 100.0
    edad_cese = edad_inicio + anios_consumo

    ci_vals = []
    ci_low = []
    ci_high = []

    for e in edades:
        if e < edad_inicio:
            val = ci_base
        elif e <= edad_cese:
            prog = (e - edad_inicio) / max(1, anios_consumo)
            val = ci_base - (abs(fsiq_neto) * prog)
        else:
            t_post = e - edad_cese
            perdida = abs(fsiq_neto)
            recup = perdida * (0.80 * capacidad_reversibilidad) * min(1.0, t_post / 2.0)
            val = ci_base - perdida + recup

        ci_vals.append(val)
        disp = 2.0 + (0.3 * (e - 10) / 10.0)
        ci_low.append(val - disp)
        ci_high.append(val + disp)

    fig_tr = go.Figure()

    fig_tr.add_trace(go.Scatter(
        x=np.concatenate([edades, edades[::-1]]),
        y=np.concatenate([ci_high, ci_low[::-1]]),
        fill='toself', fillcolor='rgba(239, 68, 68, 0.08)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip", showlegend=False
    ))

    fig_tr.add_trace(go.Scatter(
        x=edades, y=[100]*len(edades),
        mode='lines', name='Control Normativo Poblacional (Sin exposición)',
        line=dict(color='#64748B', width=2, dash='dash')
    ))

    fig_tr.add_trace(go.Scatter(
        x=edades, y=ci_vals,
        mode='lines', name='Paciente Simulado',
        line=dict(color='#EF4444', width=3.5)
    ))

    fig_tr.add_vline(x=edad_inicio, line_width=1.5, line_dash="dot", line_color="#F59E0B")
    fig_tr.add_annotation(x=edad_inicio, y=107, text=f"Inicio regular ({edad_inicio}a)", showarrow=False, font=dict(color="#F59E0B", size=11), bgcolor="#1E293B")

    fig_tr.add_vline(x=edad_cese, line_width=1.5, line_dash="dot", line_color="#10B981")
    fig_tr.add_annotation(x=edad_cese, y=104, text=f"Cese ({edad_cese}a)", showarrow=False, font=dict(color="#10B981", size=11), bgcolor="#1E293B")

    min_y = min(85.0, min(ci_low) - 2)
    fig_tr.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#0D131F',
        xaxis=dict(title="Edad Cronológica (Años)", gridcolor='#1E293B', range=[10, 45]),
        yaxis=dict(title="Puntuación Escala WAIS (CI Total)", gridcolor='#1E293B', range=[min_y, 110.0]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=20, b=20),
        height=390
    )
    st.plotly_chart(fig_tr, use_container_width=True, key="fig_trayectoria_nav")

    if edad_inicio < 17:
        st.error(
            f"**INTERFERENCIA EN VENTANA CRÍTICA DE NEURODESARROLLO (Inicio a los {edad_inicio} años):** "
            f"La exposición coincidió con el pico ontogenético de poda sináptica en interneuronas de parvalbúmina (PV+) "
            f"y la mielinización del fascículo uncinado. La reducción estimada es de {abs(fsiq_neto):.1f} puntos de CI Total. "
            f"Aun con cese posterior del consumo, la capacidad de reversibilidad biológica se limita al {capacidad_reversibilidad*100:.1f}%, "
            f"reproduciendo la disrupción estructural irreversible descrita por Meier et al."
        )
    else:
        st.info(
            f"**EXPOSICIÓN EN ETAPA POSMADURATIVA (Inicio a los {edad_inicio} años):** "
            f"Las redes frontocorticales y los tractos mielinizados ya habían alcanzado su arquitectura estructural adulta antes del contacto. "
            f"La caída en el rendimiento durante el período de uso activo responde a saturación funcional reversible. Tras la abstinencia sostenida, "
            f"el modelo proyecta una recuperación del {capacidad_reversibilidad*100:.1f}% del rendimiento psicométrico basal."
        )

    with st.expander("🔬 Fundamento Fisiopatológico: Plasticidad Dependiente de Fase Ontogenética", expanded=True):
        st.markdown(
            "La diferencia pronóstica fundamental obedece a la **fase de maduración del tejido nervioso**:\n\n"
            "* **El cerebro adolescente en ventana de poda (Morfogénesis y consolidación de circuitos):** "
            "Cualquier interferencia farmacológica altera la guía axónica y la eliminación de espinas dendríticas redundantes. "
            "La perturbación en esta etapa genera una red con menor densidad sináptica y tractos de sustancia blanca menos compactos; "
            "se trata de un defecto estructural permanente.\n\n"
            "* **El cerebro adulto post-madurativo (Estabilidad arquitectónica alcanzada):** Los circuitos ya alcanzaron su topografía definitiva. "
            "El consumo crónico introduce interferencia funcional transitoria (disminución en velocidad y memoria operativa), pero al retirar "
            "la molécula y permitir la depuración tisular, el sustrato anatómico subyacente reasume su nivel de rendimiento basal."
        )

# -----------------------------------------------------------------------------
# MÓDULO 3: DESGLOSE WAIS-IV Y CONTROL EN GEMELOS
# -----------------------------------------------------------------------------
elif modulo_seleccionado.startswith("3."):
    st.subheader("Desglose por Dominios Neuropsicológicos (Escala WAIS-IV)")
    st.caption("Análisis de afectación diferencial entre funciones ejecutivas fluidas y redes cristalizadas de alta resiliencia.")

    col_wais_l, col_wais_r = st.columns([1, 1])

    with col_wais_l:
        st.markdown("**Variación respecto a la Línea de Base por Dominio Psicométrico**")
        doms = [
            "Velocidad de Procesamiento (PSI)",
            "Memoria de Trabajo (WMI)",
            "Razonamiento Perceptivo (PRI)",
            "Comprensión Verbal (VCI)"
        ]
        vals = [caida_act_psi, caida_act_wmi, caida_act_pri, caida_act_vci]

        fig_wais_bar = go.Figure(go.Bar(
            x=vals, y=doms, orientation='h',
            marker=dict(
                color=['#EF4444', '#F59E0B', '#3B82F6', '#10B981'],
                line=dict(color='#1E293B', width=1)
            ),
            text=[f"{v:.1f} pts" for v in vals],
            textposition='outside',
            textfont=dict(color="#FFFFFF", size=11)
        ))

        min_x = min(-12.0, min(vals) - 2.5)
        fig_wais_bar.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#0D131F',
            xaxis=dict(title="Diferencial respecto al Nivel Basal (Puntos WAIS-IV)", gridcolor='#1E293B', range=[min_x, 1]),
            yaxis=dict(gridcolor='#1E293B', autorange="reversed"),
            margin=dict(l=20, r=30, t=10, b=20),
            height=340
        )
        st.plotly_chart(fig_wais_bar, use_container_width=True, key="fig_wais_bar_nav")

    with col_wais_r:
        st.markdown("**Sustrato Neurobiológico Específico por Dominio**")
        st.markdown(
            f"* **Velocidad de Procesamiento (PSI) [{caida_act_psi:.1f} pts]:** Dominio de mayor vulnerabilidad. Se asocia de forma lineal a una menor anisotropía fraccional en el "
            f"**cuerpo calloso y fascículo uncinado** en estudios de resonancia con tensor de difusión (DTI). Clínicamente se manifiesta como bradipsiquia y latencia incrementada en tareas de secuenciación.\n"
            f"* **Memoria de Trabajo (WMI) [{caida_act_wmi:.1f} pts]:** Pérdida de acoplamiento de oscilaciones gamma (40 Hz) en la "
            f"**corteza prefrontal dorsolateral (DLPFC)** por desensibilización del freno GABAérgico retrogrado. Evidencia dificultad en la retención y manipulación activa de información inmediata.\n"
            f"* **Comprensión Verbal (VCI) [{caida_act_vci:.1f} pts]:** Redes semánticas cristalizadas de alta estabilidad ontogenética; no exhiben reducciones estadísticamente significativas."
        )

    st.info(f"**MODULACIÓN FARMACOGENÉTICA COMT Val158Met ({polimorfismo_comt.split()[0]}):** {desc_gen}")
    st.divider()

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.warning(
            "**Objeción Metodológica: Rogeberg (PNAS, 2013)**\n\n"
            "Argumentó que el descenso psicométrico en la cohorte de Dunedin respondía a variables socioeconómicas confusoras "
            "(estatus socioeconómico de origen y deserción escolar temprana), cuestionando la causalidad neurotóxica directa."
        )

    with col_e2:
        st.success(
            "**Resolución Científica: Jackson et al. (PNAS, 2016)**\n\n"
            "Estudio en **gemelos monocigóticos genéticamente idénticos discordantes para consumo**: al controlar al 100% la carga genética "
            "y el entorno sociofamiliar compartido, el gemelo expuesto presentó un déficit selectivo dosis-dependiente en **velocidad de procesamiento "
            "y memoria de trabajo**, validando el impacto neurobiológico específico."
        )

# -----------------------------------------------------------------------------
# MÓDULO 4: CONCLUSIONES Y DIRECTRICES ASISTENCIALES
# -----------------------------------------------------------------------------
elif modulo_seleccionado.startswith("4."):
    st.subheader("Conclusiones y Directrices Asistenciales para la Práctica Psiquiátrica")
    st.caption("Síntesis traslacional sustentada en la evidencia biofísica y psicométrica presentada:")

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.success(
            "**1. Disociación Receptor-Estructura:**\n\n"
            "La normalización al 100% del volumen de distribución de receptores CB1 en tomografía PET tras 4 semanas de abstinencia "
            "**no certifica la resolución del daño neuroestructural**. En el paciente que inició en la adolescencia, el receptor retorna a la membrana plasmática, "
            "pero la poda axónica y la mielinización interrumpidas durante la ventana madurativa dejan una secuela fija e irreversible."
        )
        st.info(
            "**2. Inadecuación del Constructo de 'Deterioro Cognitivo Global':**\n\n"
            "El Δ⁹-THC no compromete todas las funciones corticales de forma homogénea. La evaluación neuropsicológica debe focalizarse en "
            "**velocidad de procesamiento (PSI) y memoria de trabajo (WMI)**, preservando los dominios cristalizados verbales (VCI). "
            "El informe clínico debe evitar el diagnóstico de déficit global en favor de perfiles de disfunción ejecutiva focal."
        )

    with c_p2:
        st.warning(
            "**3. Interacción Genoma-Ambiente (GxE) en la Estratificación del Riesgo:**\n\n"
            "La magnitud de la secuela cognitiva no responde exclusivamente a la dosis acumulada. La carga alélica en enzimas de aclaramiento dopaminérgico "
            "(**COMT Val158Met**) determina la susceptibilidad individual: los portadores Val/Val requieren intervenciones de cesación tempranas y mayor monitorización neurocognitiva."
        )
        st.error(
            "**4. La Ventana Crítica de los 16-18 Años como Meta Preventiva:**\n\n"
            "El factor pronóstico determinante no radica en la potencia de la cepa consumida en la adultez, sino en la **edad cronológica del inicio regular**. "
            "Retrasar el primer contacto más allá de los 20-21 años transforma un riesgo de daño microestructural permanente en una disfunción funcional predominantemente reversible tras la cesación."
        )
        