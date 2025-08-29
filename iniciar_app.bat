@echo off
CLS
TITLE AI Navigator - Painel de Controle

ECHO ==========================================================
ECHO            INICIANDO O AI NAVIGATOR
ECHO ==========================================================
ECHO.
ECHO Este script ira iniciar os dois servidores necessarios.
ECHO Duas novas janelas de terminal serao abertas.
ECHO.
ECHO Mantenha as duas janelas abertas para que a aplicacao funcione.
ECHO Para desligar, basta fechar as duas janelas.
ECHO.
ECHO ==========================================================
ECHO.
PAUSE

ECHO Iniciando Servidor de Back-End (API)...
START "AI NAVIGATOR - BACKEND (Python Flask)" cmd /k "py app.py"

ECHO Iniciando Servidor de Front-End (Arquivos)...
START "AI NAVIGATOR - FRONTEND (HTTP Server)" cmd /k "py -m http.server -b 127.0.0.1"

ECHO.
ECHO Aguardando 5 segundos para os servidores estabilizarem...
timeout /t 5 /nobreak > NUL

ECHO Abrindo a aplicacao no seu navegador...
start http://127.0.0.1:8000/

ECHO.
ECHO Servidores iniciados. Esta janela de controle pode ser fechada.
ECHO.
PAUSE
EXIT