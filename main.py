import streamlit as st
import pandas as pd
from agente import analisar_problema_manutencao, gerar_plano_preventiva_ia
from banco import (
    inicializar_banco, 
    salvar_ordem_servico, 
    buscar_todas_as_os, 
    obter_indicadores_gerais, 
    obter_os_por_coluna,
    fechar_ordem_servico
)

# Inicializa o banco de dados e a tabela ao iniciar a aplicação
inicializar_banco()

# Configuração básica da página do Streamlit
st.set_page_config(
    page_title="Agente de Manutenção Predial",
    page_icon="🔧",
    layout="wide"
)

# ==========================================
# BARRA LATERAL (CONFIGURAÇÕES E API KEY)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/maintenance.png", width=80)
    st.subheader("Configurações do Agente")
    st.write("Insira sua chave de API do Google Gemini para ativar a IA Generativa.")
    
    api_key_input = st.text_input("Google Gemini API Key", type="password", placeholder="Cole sua chave aqui...")
    
    if api_key_input:
        st.success("🤖 IA Generativa Conectada!")
    else:
        st.info("ℹ️ Sem chave informada. O sistema usará o modo de regras locais.")
    
    st.markdown("---")
    st.markdown("**Versão do Sistema:** 2.5 (Com Fechamento & Preventivas IA)")

# Título principal da aplicação
st.title("🔧 Agente de Inteligência Artificial para Manutenção Predial")
st.write("Sistema inteligente de apoio à gestão, diagnóstico e planejamento preventivo.")

# Criando abas para organizar a navegação
aba_nova, aba_consulta, aba_preventiva, aba_dashboard = st.tabs([
    "➕ Nova Solicitação", 
    "📋 Consultar & Fechar OS", 
    "🤖 Gerador de Preventivas (IA)",
    "📊 Dashboard de Indicadores"
])

# ==========================================
# ABA 1: NOVA SOLICITAÇÃO E ANÁLISE DO AGENTE
# ==========================================
with aba_nova:
    st.subheader("📝 Registrar Nova Solicitação de Manutenção")

    with st.form("form_manutencao"):
        descricao = st.text_area(
            "Descrição do Problema",
            placeholder="Ex: Vazamento de água no sifão da pia / Tomada da sala 302 sem energia..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            local = st.text_input("Local / Ala / Andar", placeholder="Ex: Segundo Andar, Ala Sul")
            setor = st.selectbox(
                "Setor",
                ["UTI", "Pronto Socorrro", "Enfermaria", "Centro Cirúrgico", "Recepção", "Administrativo", "Áreas Comuns", "Outros"]
            )
            equipamento = st.text_input("Equipamento / Ativo", placeholder="Ex: Registro geral, Bomba d'água 02")

        with col2:
            tipo_manutencao = st.selectbox(
                "Tipo de Manutenção",
                ["Corretiva", "Preventiva"]
            )
            
            categoria = st.selectbox(
                "Categoria do Problema",
                [
                    "Elétrica",
                    "Hidráulica",
                    "Civil",
                    "Pintura",
                    "Refrigeração / Climatização",
                    "Bombas",
                    "Portas e Fechaduras",
                    "Iluminação",
                    "Equipamentos Gerais"
                ]
            )
            
            prioridade = st.selectbox(
                "Prioridade Sugerida",
                ["Baixa", "Média", "Alta", "Crítica"]
            )

        submit_button = st.form_submit_button(label="🔍 Analisar Problema com IA e Gerar OS")

    if submit_button:
        if not descricao.strip():
            st.warning("⚠️ Por favor, preencha a descrição do problema antes de enviar.")
        else:
            diagnostico_ia = analisar_problema_manutencao(categoria, descricao, api_key=api_key_input)
            
            os_id = salvar_ordem_servico(
                descricao=descricao,
                local=local,
                setor=setor,
                equipamento=equipamento,
                categoria=categoria,
                tipo=tipo_manutencao,
                prioridade=prioridade,
                diagnostico=str(diagnostico_ia['diagnostico'])
            )
            
            st.success(f"Ordem de Serviço **OS #{os_id}** gerada e salva com sucesso no banco de dados!")
            
            st.markdown("---")
            
            # Bloco Visual para Impressão da OS
            st.markdown(f"""
            <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: #333;">
                <h2 style="text-align: center; color: #2E7D32;">ORDEM DE SERVIÇO - OS #{os_id}</h2>
                <hr>
                <p><b>Tipo:</b> {tipo_manutencao} | <b>Prioridade:</b> {prioridade} | <b>Status:</b> Aberta</p>
                <p><b>Local:</b> {local} | <b>Setor:</b> {setor} | <b>Equipamento:</b> {equipamento}</p>
                <p><b>Categoria:</b> {categoria}</p>
                <p><b>Descrição:</b> {descricao}</p>
                <hr>
                <h3>🤖 Diagnóstico Preliminar ({diagnostico_ia['origem']}):</h3>
                <div>{diagnostico_ia['diagnostico']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button("🖨️ Imprimir / Salvar PDF desta Ordem de Serviço"):
                st.components.v1.html("<script>window.print();</script>", height=0)
            
            st.info(
                "💡 **Aviso Legal / Operacional:** Este diagnóstico preliminar é uma sugestão de apoio "
                "ao profissional e não substitui a inspeção técnica presencial ou as Normas Regulamentadoras."
            )

# ==========================================
# ABA 2: CONSULTAR & FECHAR ORDENS DE SERVIÇO
# ==========================================
with aba_consulta:
    st.subheader("📋 Histórico e Fechamento de Ordens de Serviço")
    st.write("Consulte os chamados anteriores e realize o encerramento informando a solução aplicada.")
    
    dados_os = buscar_todas_as_os()
    
    if not dados_os:
        st.info("📭 Nenhuma Ordem de Serviço cadastrada no momento.")
    else:
        df_os = pd.DataFrame(dados_os, columns=[
            "ID", "Data/Hora", "Descrição", "Local", "Setor", 
            "Equipamento", "Categoria", "Tipo", "Prioridade", "Status", "Diagnóstico"
        ])
        st.dataframe(df_os, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔒 Encerrar / Fechar Ordem de Serviço")
        
        with st.form("form_fechar_os"):
            os_para_fechar = st.number_input("Digite o ID da OS que deseja fechar", min_value=1, step=1)
            solucao_aplicada = st.text_area("Descrição da Solução Aplicada", placeholder="Ex: Substituição do sifão danificado e teste de vazamento realizado com sucesso.")
            botao_fechar = st.form_submit_button("✅ Concluir e Fechar OS")
            
        if botao_fechar:
            if not solucao_aplicada.strip():
                st.warning("⚠️ Por favor, descreva a solução aplicada para encerrar a OS.")
            else:
                fechar_ordem_servico(os_para_fechar, solucao_aplicada)
                st.success(f"🎉 Ordem de Serviço **OS #{os_para_fechar}** foi fechada com sucesso! Atualize a página para ver o novo status.")

# ==========================================
# ABA 3: GERADOR DE PREVENTIVAS POR IA
# ==========================================
with aba_preventiva:
    st.subheader("🤖 Gerador Inteligente de Planos de Manutenção Preventiva")
    st.write("Utilize a Inteligência Artificial para estruturar rotinas preventivas completas para qualquer ativo da instituição.")
    
    with st.form("form_preventiva"):
        ativo_input = st.text_input(
            "Equipamento ou Sistema para Preventiva",
            placeholder="Ex: Sistema de Ar-Condicionado Central / Bombas de Incêndio / Gerador de Emergência"
        )
        botao_gerar_preventiva = st.form_submit_button("🚀 Gerar Plano Preventivo com IA")
        
    if botao_gerar_preventiva:
        if not ativo_input.strip():
            st.warning("⚠️ Informe o nome do equipamento ou sistema.")
        else:
            with st.spinner("Gerando plano de manutenção preventiva personalizado..."):
                plano_gerado = gerar_plano_preventiva_ia(ativo_input, api_key=api_key_input)
                
            st.success("Plano preventivo gerado com sucesso!")
            st.markdown("---")
            st.markdown(f"### 📋 Plano de Preventiva: {ativo_input}")
            st.markdown(plano_gerado)
            
            if st.button("🖨️ Imprimir Plano Preventivo"):
                st.components.v1.html("<script>window.print();</script>", height=0)

# ==========================================
# ABA 4: DASHBOARD DE INDICADORES
# ==========================================
with aba_dashboard:
    st.subheader("📊 Painel de Indicadores de Manutenção")
    total_os, os_abertas, os_criticas = obter_indicadores_gerais()
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Total de Ordens de Serviço", value=total_os)
    with m2:
        st.metric(label="Ordens Abertas", value=os_abertas)
    with m3:
        st.metric(label="Ordens Críticas", value=os_criticas)
        
    st.markdown("---")
    col_dash1, col_dash2 = st.columns(2)
    with col_dash1:
        st.markdown("#### 🏢 OS por Setor")
        dados_setor = obter_os_por_coluna("setor")
        if dados_setor:
            df_setor = pd.DataFrame(dados_setor, columns=["Setor", "Quantidade"])
            st.dataframe(df_setor, use_container_width=True, hide_index=True)
        else:
            st.info("Sem dados suficientes.")
    with col_dash2:
        st.markdown("#### 🏷️ OS por Categoria")
        dados_categoria = obter_os_por_coluna("categoria")
        if dados_categoria:
            df_cat = pd.DataFrame(dados_categoria, columns=["Categoria", "Quantidade"])
            st.dataframe(df_cat, use_container_width=True, hide_index=True)
        else:
            st.info("Sem dados suficientes.")