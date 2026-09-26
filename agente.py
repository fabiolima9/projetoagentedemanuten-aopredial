# agente.py - Módulo de Inteligência Artificial Generativa para Manutenção Predial

import os
from google import genai

def analisar_problema_manutencao(categoria, descricao, api_key=None):
    """
    Utiliza o modelo Gemini da Google para analisar a solicitação de manutenção
    em linguagem natural, mantendo separação rigorosa entre especialidades.
    """
    
    desc_lower = descricao.lower()
    
    if api_key and api_key.strip():
        try:
            client = genai.Client(api_key=api_key)
            
            prompt_sistema = f"""
            Você é um Engenheiro Sênior especialista em Manutenção Predial Hospitalar e Predial.
            Um profissional de manutenção registrou o seguinte problema:
            - Categoria rigorosa selecionada: {categoria}
            - Descrição detalhada do problema: "{descricao}"

            ATENÇÃO RESTRITA: Responda estritamente focado na categoria informada ({categoria}). 
            Por exemplo, se a categoria for Hidráulica, trate apenas de tubulações, vazamentos, registros, bombas, esgoto ou água, NUNCA misture com problemas elétricos, fiação ou disjuntores.

            Forneça um suporte técnico estruturado contendo exatamente os seguintes blocos:
            1. DIAGNOSTICO: Uma frase clara resumindo o problema provável na especialidade de {categoria}.
            2. CAUSAS: Uma lista com 3 possíveis causas técnicas específicas para {categoria}.
            3. VERIFICACOES: Uma lista com 3 verificações recomendadas no local.
            4. FERRAMENTAS: Uma lista com 3 ferramentas necessárias para esta especialidade.
            5. MATERIAIS: Uma lista com 2 ou 3 materiais ou EPIs necessários.
            6. SEGURANCA: Uma recomendação de segurança estrita aplicável.

            Retorne a resposta de forma limpa, utilizando marcadores claros para cada seção.
            """
            
            # Atualizado para o modelo atual suportado pela API
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_sistema
            )
            
            return {
                "origem": "IA Generativa (Gemini)",
                "diagnostico": response.text,
                "causas": [],
                "verificacoes": [],
                "ferramentas": [],
                "materiais": [],
                "seguranca": "Consulte sempre as NRs vigentes e utilize os EPIs obrigatórios."
            }
            
        except Exception as e:
            print(f"Erro ao conectar com a IA: {e}")
    
    # ==========================================
    # FALLBACK LOCAL (Regras Estáticas Separadas)
    # ==========================================
    resultado = {
        "origem": "Modo Local (Regras Estáticas)",
        "diagnostico": f"Análise preliminar padrão para ocorrência em {categoria}.",
        "causas": [
            "Desgaste natural de componentes pelo tempo de uso.",
            "Falta de inspeção preventiva recente no ativo.",
            "Sobrecarga operacional ou uso inadequado."
        ],
        "verificacoes": [
            "Realizar inspeção visual detalhada no local do chamado.",
            "Testar o funcionamento básico e isolar a área se necessário.",
            "Verificar histórico de intervenções anteriores."
        ],
        "ferramentas": [
            "Kit básico de ferramentas manuais",
            "Lanterna de inspeção"
        ],
        "materiais": [
            "EPIs básicos (Luvas, óculos de proteção, calçado de segurança)"
        ],
        "seguranca": "Sempre utilize os EPIs obrigatórios e siga rigorosamente as normas de segurança aplicáveis."
    }

    if categoria == "Elétrica" or ("tomada" in desc_lower or "energia" in desc_lower or "disjuntor" in desc_lower or "luz" in desc_lower):
        resultado["diagnostico"] = "Possível falha em circuito elétrico, disjuntor desarmado ou problema em ponto de tomada/interruptor."
        resultado["causas"] = [
            "Disjuntor seletivo ou geral desarmado por sobrecarga ou curto-circuito.",
            "Mau contato em bornes, conexões ou disjuntores do quadro elétrico.",
            "Fiação rompida ou danificada por aquecimento."
        ]
        resultado["verificacoes"] = [
            "Verificar o estado do disjuntor correspondente no Quadro de Distribuição (QDC).",
            "Medir a tensão no ponto utilizando multímetro digital.",
            "Inspecionar sinais de aquecimento ou cheiro de queimado nas proximidades."
        ]
        resultado["ferramentas"] = [
            "Multímetro digital com categoria de segurança adequada",
            "Chave teste / Detector de tensão sem contato",
            "Chaves isoladas"
        ]
        resultado["materiais"] = [
            "Terminais elétricos, fita isolante de boa qualidade",
            "Disjuntor ou tomada de substituição"
        ]
        resultado["seguranca"] = "ATENÇÃO: Risco de choque elétrico. Desligue o disjuntor correspondente antes de qualquer manuseio."

    elif categoria == "Hidráulica" or ("água" in desc_lower or "vazamento" in desc_lower or "infiltração" in desc_lower or "cano" in desc_lower or "registro" in desc_lower or "torneira" in desc_lower):
        resultado["diagnostico"] = "Ocorrência relacionada a vazamento, obstrução ou falta de alimentação na rede hidráulica."
        resultado["causas"] = [
            "Ruptura, rachadura ou descolamento em conexões de tubulações de PVC/cobre.",
            "Desgaste natural de vedantes, reparos de registros ou borrachas de vedação.",
            "Obstrução por detritos na rede de esgoto ou sifão."
        ]
        resultado["verificacoes"] = [
            "Verificar registros de fechamento do setor afetado para conter fluxo.",
            "Inspecionar conexões visíveis, sifões, caixas de inspeção e paredes com infiltração.",
            "Checar nível e funcionamento dos reservatórios ou barriletes."
        ]
        resultado["ferramentas"] = [
            "Chave grifo / Chave inglesa",
            "Trena e nível de bolha",
            "Lanterna de inspeção e balde coletor"
        ]
        resultado["materiais"] = [
            "Fita veda-rosca",
            "Cola para PVC, lixa para tubos e conexões de reparo rápido",
            "Estopa, panos de limpeza e sacos de vedação"
        ]
        resultado["seguranca"] = "Cuidado com pisos escorregadios devido a acúmulo de água. Feche o registro do setor antes de realizar cortes em tubulações."

    return resultado


def gerar_plano_preventiva_ia(equipamento_ou_setor, api_key=None):
    """
    Utiliza a IA Generativa para criar um plano de manutenção preventiva 
    personalizado para um determinado equipamento ou setor.
    """
    if api_key and api_key.strip():
        try:
            client = genai.Client(api_key=api_key)
            
            prompt = f"""
            Você é um Engenheiro Consultor Sênior em Manutenção Predial e Facilities.
            Gere um Plano de Manutenção Preventiva estruturado, profissional e normatizado para o seguinte ativo/setor:
            "{equipamento_ou_setor}"

            O plano deve conter obrigatoriamente:
            1. FREQUENCIA RECOMENDADA (Diária, Semanal, Mensal ou Anual)
            2. ROTINAS DE INSPECAO E TESTES (O que verificar)
            3. PROCEDIMENTOS DE LIMPEZA / LUBRIFICACAO
            4. NORMAS APLICAVEIS (Ex: NR-10, ABNT, etc.)
            
            Formate de maneira limpa com marcadores para facilitar a leitura do técnico.
            """
            
            # Atualizado para o modelo atual suportado pela API
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
            
        except Exception as e:
            return f"Erro ao gerar plano via IA: {e}"
            
    return "⚠️ Para gerar o plano automatizado de preventivas, insira sua chave de API do Google Gemini na barra lateral."