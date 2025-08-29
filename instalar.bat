@echo off
CLS
ECHO ==========================================================
ECHO            BEM-VINDO AO INSTALADOR DO AI NAVIGATOR
ECHO ==========================================================
ECHO.
ECHO Este script ira descompactar e configurar o ambiente.
ECHO Certifique-se de que o Python 3.10+ ja esta instalado na maquina
ECHO e que a opcao "Add Python to PATH" foi marcada.
ECHO.
PAUSE

ECHO.
ECHO Descompactando os arquivos do projeto...
:: Descompacta o instalador na pasta atual
tar -xf AINavigator_Installer.zip
ECHO ✅ Arquivos descompactados.
ECHO.

ECHO Instalando as dependencias do Python...
:: Instala todas as bibliotecas da nossa lista
py -m pip install -r requirements.txt
ECHO ✅ Dependencias instaladas.
ECHO.

ECHO ==========================================================
ECHO    ✅ INSTALACAO CONCLUIDA COM SUCESSO!
ECHO.
ECHO    Para iniciar a aplicacao, de um duplo-clique no
ECHO    arquivo 'iniciar_app.bat'.
ECHO ==========================================================
PAUSE