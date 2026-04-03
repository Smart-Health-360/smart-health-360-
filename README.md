# 🏥 SMART HEALTH 360°
### Sistema Inteligente de Conversão de Pacientes

O **Smart Health 360°** é uma solução baseada em **Inteligência Artificial e Análise Preditiva** desenvolvida para reduzir taxas de *no-show* e aumentar a conversão de pacientes na rede hospitalar.

O projeto foi desenhado como proposta estratégica para a **Rede Mater Dei**, integrando Machine Learning, automação de comunicação e dashboards gerenciais em nuvem.

---

## 👥 Desenvolvedores  
**Turma 2TSC0 — FIAP**

- **[Caio Guimarães Souza Gonçalves](https://github.com/caioguimaraes18)**
- **[Eric Yuiti Ito Nissi](https://github.com/YuitiNissi)**
- **[João Paulo Ferreira](https://github.com/joao-paulo-alt)**
- **Natália Guimarães Barbosa dos Santos**

---

## 🎯 O Problema

O setor de saúde privada enfrenta desafios críticos que impactam diretamente a sustentabilidade financeira e operacional:

- **No-show Crônico:** 1 em cada 5 pacientes não comparece às consultas (média de 20,1%).
- **Baixa Conversão:** Mais de 60% dos interessados não se tornam pacientes ativos.
- **Comunicação Ineficaz:** Lembretes genéricos que não consideram perfil comportamental.
- **Impacto Financeiro:** Perda de receita estimada em milhões devido a agendas ociosas.

---

## 💡 A Solução

A plataforma atua em toda a jornada do paciente através de:

1. **Análise Preditiva**  
   Cálculo de **Score de Risco (0–100)** para identificar pacientes propensos a faltar.

2. **IA Generativa**  
   Criação de mensagens personalizadas (*Nudges Digitais*) via OpenAI API.

3. **Automação via WhatsApp**  
   Comunicação direta para confirmação e reagendamento.

4. **Dashboards Gerenciais**  
   Monitoramento de KPIs em tempo real para tomada de decisão.

---

## 🏗️ Arquitetura e Fluxo Técnico

Infraestrutura baseada em **Microsoft Azure**:

- **Data Lake:** Azure Blob Storage  
- **Banco de Dados:** Azure SQL Database  
- **Processamento:** Python Backend  
- **Modelos de ML:** Random Forest + Gradient Boosting  
- **Acurácia média:** **87%**  
- **IA Generativa:** Personalização de mensagens  
- **Visualização:** Power BI e Streamlit  

---

## 📂 Estrutura do Repositório

```text
smart-health-360/
├── dados/           # Bases tratadas e de modelagem (CSV)
├── notebooks/       # Preparação, EDA, Modelagem e Dashboards (.ipynb)
├── app/             # Aplicação interativa (Streamlit)
├── modelos/         # Arquivos dos modelos treinados (.pkl)
└── README.md        # Documentação do projeto
```
---

<div align="center">

### 📄 Licença

Este projeto está distribuído sob a **MIT License**.  
Para mais informações, consulte o arquivo [`LICENSE`](LICENSE).

<br>

<sub>
Projeto acadêmico desenvolvido na FIAP (2026) como aplicação prática de Ciência de Dados,  
Machine Learning e Arquitetura em Nuvem voltados à gestão hospitalar e transformação digital na saúde privada brasileira.
</sub>

<br>

<sub>
Smart Health 360° • Todos os direitos reservados aos autores
</sub>

</div>