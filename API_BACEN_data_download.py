import time
import pandas as pd
import requests
from datetime import datetime

agora = datetime.now()
ano_atual = agora.year
mes_atual = agora.month
mes_limite = mes_atual - 1 if mes_atual > 1 else 1

def baixar_dados_bacen():
    '''
    Funcao responsavel por acionamento fora do arquivo
    '''    
    # Validação do Ano Inicial
    while True:
        ano = input('Qual será ano de ponto de partida para solicitar extrato? (YYYY): ').strip()
        if ano.isdigit() and len(ano) == 4:
            ano = int(ano)
            if ano <= ano_atual:
                break
        print(f"Ano inválido! Digite um ano válido de 4 dígitos até {ano_atual}.\n")

    print(f"Ano selecionado: {ano}")

    # ano atual
    if ano == ano_atual:
        # Trata caso esteja rodando em Janeiro ou Fevereiro do Ano Vigente
        if mes_atual == 1 or mes_atual == 2:
            print('Mes Janeiro e Fevereiro do ano vigente tem como referencia o mes de Janeiro para inicio de extratificacao...')
            mes_ini = 1
        else:      
            while True:
                try:
                    mes = int(input(f'Digite o número do mês de início do extrato (1 a {mes_limite}): '))
                    if 1 <= mes <= mes_limite:                   
                        mes_ini = mes                
                        break
                    print(f'Mês inválido! Digite um número entre 1 e {mes_limite}.')
                except ValueError:
                    print('Entrada inválida! Digite apenas números.')
    else:
        while True:
            try:
                mes = int(input('Digite o número do mês de início do extrato (1 a 12): '))
                if 1 <= mes <= 12:                    
                    mes_ini = mes                
                    break
                print('Mês inválido! Digite um número entre 1 e 12.')
            except ValueError:
                print('Entrada inválida! Digite apenas números.')

    

    print('DADOS GRAVADOS COM SUCESSO...\n')

    # Processamento dos Dados
   
    mes_envio = f"{int(ano)}{int(mes):02d}"
    
    while True:
        try:
            total = int(input('Quantas linhas para baixar por arquivo? (MIN 100, MAX 10000): '))
            # Validação para garantir que o número de linhas seja no mínimo 100
            if total >= 100 and total <=10000:
                break
            print('O valor deve ser de no minimo 100 linhas e no maximo 10000 linhas!')
        except ValueError:
            print('Valor deve ser inteiro!')


    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
    }

    print("Iniciando a extração com requests + pandas...")

    

    
    print(f"Baixando dados da solicitacao desde o mes solicitado: {mes_envio}...")

    url = (
        f"https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/"
        f"CnaePorteRecebedor(Database=@Database)?@Database='{mes_envio}'&$top={total}&$format=json"        
    )

    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200: # quando a resposta estiver pronta: 200
            data = response.json()

            # Extrai a lista de registros dentro da chave 'value' do OData
            registros = data.get("value", [])

            if registros:
                df_mes = pd.DataFrame(registros)                    
                print(f"-> Sucesso! {len(df_mes)} linhas importadas.")
            else:
                print(f"-> Nenhum dado retornado para o mês {mes_envio}.")
        else:
            print(
                f"Erro ao acessar o mês {mes_envio}: Status Code {response.status_code}"
            )

    except Exception as e:
        print(f"Erro ao processar o mês {mes_envio}: {e}")

    time.sleep(1)

# CONSOLIDANDO INFORMACAO
    if df_mes is not None:            
        df_mes.to_csv("dados_pix_selecionado.csv", index=False) 
        print(f"\n[FINALIZADO] Total de linhas: {len(df_mes)}")
        return df_mes    
    else:
        print("\nNenhum dado foi extraído.")

if __name__ == "__main__": #RODANDO  O SCRIPT DIRETO DESSE ARQUIVO
    print("--- TESTANDO EXTRAÇÃO ISOLADA ---")
    df_teste = baixar_dados_bacen()
    if not df_teste.empty:
        print(df_teste.head())