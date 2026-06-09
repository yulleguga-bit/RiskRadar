import os
import time
import zipfile
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÕES ---
URL_PAGINA_DADOS_ABERTOS = "https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf"
PASTA_PROJETO = os.getcwd()
ARQUIVO_ZIP_LOCAL = os.path.join(PASTA_PROJETO, "download.zip")
BASE_HISTORICA = "base_completa_dashboard.csv"


def baixar_clicando_na_pagina():
    print("🌐 Abrindo o portal de Dados Abertos da PRF...")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")

    prefs = {
        "download.default_directory": PASTA_PROJETO,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico, options=chrome_options)

    try:
        driver.get(URL_PAGINA_DADOS_ABERTOS)
        wait = WebDriverWait(driver, 15)

        print("🧹 Aguardando a página carregar os pop-ups...")
        time.sleep(5)

        print("💥 Clicando no fundo da tela para fechar o pop-up 'Para começar'...")
        try:
            fundo_da_pagina = driver.find_element(By.TAG_NAME, "body")
            fundo_da_pagina.click()
            time.sleep(1)
        except Exception:
            pass

        print("🧹 Executando limpeza de cookies via código...")
        script_limpeza = """
        var cookiesMenu = document.querySelector('.lgpd-governo, .br-cookiebar, #lgpd-cookie-bar, .modal-backdrop');
        if(cookiesMenu) { cookiesMenu.remove(); }
        var backdrops = document.querySelectorAll('.modal-backdrop, .fade, .show');
        backdrops.forEach(function(el){ el.remove(); });
        """
        driver.execute_script(script_limpeza)
        time.sleep(1)

        print("🔍 Passo 1: Procurando o botão 'Baixar planilha'...")
        link_download = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'Baixar planilha')]"))
        )

        print("🖱️ Clicando para abrir a tela do Google Drive...")
        driver.execute_script("arguments[0].click();", link_download)

        # Como o link abre em uma nova aba do navegador, precisamos mandar o Selenium mudar o foco para ela
        print("🔄 Alternando para a aba do Google Drive...")
        time.sleep(5)  # Aguarda a aba abrir e estabilizar
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])

        print("🔍 Passo 2: Procurando o botão 'Baixar' do Google Drive (F12)...")
        # Localiza o botão usando o aria-label="Baixar" que você encontrou no F12
        botao_baixar_drive = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Baixar']"))
        )

        print("📥 Botão de Download encontrado! Disparando o download do ZIP...")
        driver.execute_script("arguments[0].click();", botao_baixar_drive)

        print("⏳ Aguardando a conclusão do download do arquivo ZIP...")
        timeout = 240  # 4 minutos (arquivos de acidentes costumam ser grandes)
        segundos = 0

        while segundos < timeout:
            time.sleep(4)
            segundos += 4

            arquivos = os.listdir(PASTA_PROJETO)
            # Filtra arquivos zip legítimos que não sejam o nosso alvo final ainda
            arquivos_zip = [f for f in arquivos if f.endswith(
                ".zip") and f != "download.zip"]
            cr_downloads = [f for f in arquivos if f.endswith(".crdownload")]

            # Se achou um arquivo zip pronto e o Chrome não está mais com o download temporário ativo
            if arquivos_zip and not cr_downloads:
                caminho_origem = os.path.join(PASTA_PROJETO, arquivos_zip[0])
                if os.path.exists(ARQUIVO_ZIP_LOCAL):
                    os.remove(ARQUIVO_ZIP_LOCAL)
                os.rename(caminho_origem, ARQUIVO_ZIP_LOCAL)
                print("✅ Download concluído de ponta a ponta!")
                return True

        print("❌ Tempo limite esgotado. O download demorou muito para concluir.")
        return False

    except Exception as e:
        print(f"❌ Falha durante a automação: {e}")
        return False
    finally:
        driver.quit()


def processar_dados():
    if not baixar_clicando_na_pagina():
        return

    print("📂 Abrindo o ZIP e tratando os dados com Pandas...")
    try:
        with zipfile.ZipFile(ARQUIVO_ZIP_LOCAL, "r") as z:
            arquivos_internos = z.namelist()
            csv_files = [f for f in arquivos_internos if f.endswith(".csv")]

            if not csv_files:
                print("❌ Nenhum arquivo .csv encontrado dentro do ZIP.")
                return

            nome_csv = csv_files[0]
            print(f"📄 Arquivo CSV encontrado interno: {nome_csv}")

            with z.open(nome_csv) as f_csv:
                df_novo = pd.read_csv(f_csv, sep=";", encoding="latin1")

    except Exception as e:
        print(f"❌ Falha ao ler o arquivo ZIP/CSV: {e}")
        return
    finally:
        if os.path.exists(ARQUIVO_ZIP_LOCAL):
            os.remove(ARQUIVO_ZIP_LOCAL)

    print("📊 Mesclando dados...")
    try:
        if os.path.exists(BASE_HISTORICA):
            print("🔄 Juntando com a sua base existente...")
            df_antigo = pd.read_csv(BASE_HISTORICA, sep=";", encoding="latin1")
            df_final = pd.concat([df_antigo, df_novo]
                                 ).drop_duplicates().reset_index(drop=True)
        else:
            print("📂 Criando novo arquivo de base histórica...")
            df_final = df_novo

        df_final.to_csv(BASE_HISTORICA, sep=";",
                        encoding="latin1", index=False)
        print(
            f"🚀 Sucesso absoluto! '{BASE_HISTORICA}' atualizado. Linhas totais: {len(df_final)}")

    except Exception as e:
        print(f"❌ Erro no processamento do Pandas: {e}")


if __name__ == "__main__":
    processar_dados()
