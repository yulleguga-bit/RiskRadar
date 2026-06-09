import os

readme_content = """# 🛰️ RiskRadar - Automação de Atualização de Dados (PRF)

Este módulo faz parte do ecossistema **RiskRadar** e é responsável por automatizar a extração, tratamento e consolidação dos dados abertos de acidentes rodoviários disponibilizados pela Polícia Rodoviária Federal (PRF).

---

## 📖 Visão Geral do Desafio e Solução

A extração automatizada desses dados apresentou múltiplos desafios de infraestrutura e segurança por parte do portal do governo, exigindo uma evolução técnica em camadas para alcançar a estabilidade:

1. **Tentativa Inicial (Requests / HTTP Nativo):** Bloqueada imediatamente pelo servidor Nextcloud da PRF, que rejeitava requisições automatizadas padrão sem cabeçalhos de navegadores reais.
2. **Segunda Tentativa (cURL do Windows):** Barrada por falha no aperto de mão criptográfico (`SSL/TLS handshake failed / ERR_CONNECTION_CLOSED`), decorrente de incompatibilidades de certificados e travas estritas do servidor de arquivos.
3. **Solução Definitiva (Selenium WebDriver):** Implementação de uma automação que simula o comportamento humano completo. O robô abre um navegador real em segundo plano, contorna pop-ups de interface, navega até o ecossistema do Google Drive (onde a planilha de 2026 está hospedada) e dispara o gatilho de download nativo.

---

## 🛠️ Tecnologias Utilizadas

* **[Python 3.14+](https://www.python.org/):** Linguagem base para o desenvolvimento do script de automação e pipeline de dados.
* **[Selenium WebDriver (v4.44+)](https://www.selenium.dev/):** Ferramenta de automação web utilizada para emular interações humanas (cliques, navegação entre abas, injeção de JavaScript).
* **[WebDriver Manager](https://pypi.org/project/webdriver-manager/):** Gerenciador automatizado para baixar e sincronizar o binário do `chromedriver` de acordo com a versão exata do Google Chrome instalada na máquina de execução.
* **[Pandas](https://pandas.pydata.org/):** Biblioteca de alta performance para manipulação e análise de dados, utilizada na leitura, filtragem e mesclagem de arquivos de grande porte.
* **[Zipfile & OS (Nativos)](https://docs.python.org/3/library/index.html):** Módulos do Python para manipulação do sistema de arquivos local, extração dinâmica do ZIP baixado e remoção de resíduos temporários.

---

## 🛠️ Tecnologias Utilizadas

* **[Python 3.14+](https://www.python.org/):** Linguagem base para o desenvolvimento do script de automação e pipeline de dados.
* **[Selenium WebDriver (v4.44+)](https://www.selenium.dev/):** Ferramenta de automação web utilizada para emular interações humanas (cliques, navegação entre abas, injeção de JavaScript).
* **[WebDriver Manager](https://pypi.org/project/webdriver-manager/):** Gerenciador automatizado para baixar e sincronizar o binário do `chromedriver` de acordo com a versão exata do Google Chrome instalada na máquina de execução.
* **[Pandas](https://pandas.pydata.org/):** Biblioteca de alta performance para manipulação e análise de dados, utilizada na leitura, filtragem e mesclagem de arquivos de grande porte.
* **[Zipfile & OS (Nativos)](https://docs.python.org/3/library/index.html):** Módulos do Python para manipulação do sistema de arquivos local, extração dinâmica do ZIP baixado e remoção de resíduos temporários.

---

## ⚙️ Métodos e Estratégias Implementadas

Para consolidar a automação com sucesso, foram aplicadas as seguintes técnicas avançadas de Web Scraping:

### 1. Desativação de Restrições de Segurança (Flags do Chrome)
Configuração de argumentos estritos no Chrome Options para forçar a comunicação com o servidor, ignorando os erros gerados pelo handshake TLS corrompido do portal de arquivos:
```python
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")

_________________________________________________________________

2. Injeção de JavaScript para Limpeza de Interface (DOM Manipulation)
O portal gov.br exibe pop-ups flutuantes obrigatórios (Banners de cookies/LGPD e o assistente guiado "Para começar"). Esses elementos cobrem a tela e geravam erros de clique bloqueado. A solução foi injetar um script JS que deleta cirurgicamente os nós desses elementos direto na árvore do HTML:

var tourPopups = document.querySelectorAll('.br-tooltip, .govbr-help-popup');
tourPopups.forEach(function(el){ el.remove(); });


3. Simulação de Clique Físico em Ponto Cego
Como o assistente virtual do governo impede interações até ser fechado, programamos um clique inicial no elemento <body> da página. Isso emula o clique do usuário em "qualquer lugar da tela", fazendo com que as sobreposições voltem ao estado oculto.

4. Alternância Dinâmica de Janelas (Window Handles)
A PRF hospeda o arquivo de 2026 (datatran2026.csv) dentro de um diretório do Google Drive. Ao clicar no link da PRF, o navegador abre uma segunda aba. O script captura esse evento e muda o foco do robô para a aba correta:

driver.switch_to.window(driver.window_handles[-1])

5. Mapeamento via Elementos Semânticos (F12 Inspection)
Através da inspeção do código-fonte (F12), identificamos que o botão do Google Drive possui a propriedade acessível aria-label="Baixar". O Selenium utiliza essa propriedade com queries XPath para garantir precisão absoluta no clique do download:

Comando:
By.XPATH, "//button[@aria-label='Baixar']"

6. Pipeline Dedobrado com Pandas (ETL Incremental)
Após o término do download do arquivo .zip, o script:

Localiza e descompacta o arquivo interno de forma temporária.

Carrega o CSV novo utilizando a codificação correta (latin1) e separador ;.

Verifica se já existe uma base histórica (base_completa_dashboard.csv).

Executa um pd.concat() unindo a base antiga aos novos registros.

Executa um .drop_duplicates() para garantir que dados sobrepostos de requisições anteriores não gerem duplicidade de linhas no seu Dashboard.

Sobrescreve a base final otimizada e limpa o arquivo ZIP residual da máquina.

🚀 Como Executar
Certifique-se de ter o Google Chrome instalado na máquina.

Instale as dependências necessárias listadas no projeto:

pip install selenium webdriver-manager pandas

Execute o script de atualização no diretório raiz do repositório:

Bash
python atualizar_prf.py

Documentação desenvolvida para o repositório RiskRadar em Junho de 2026.
