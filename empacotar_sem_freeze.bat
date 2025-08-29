@echo off
ECHO ==========================================================
ECHO      EMPACOTANDO O AI NAVIGATOR (SEM ATUALIZAR REQS)
ECHO ==========================================================
ECHO.
ECHO Usando o 'requirements.txt' existente que foi limpo manualmente.
ECHO.
ECHO Criando o arquivo de instalacao (AINavigator_Installer.zip)...
ECHO.

tar -a -cf AINavigator_Installer.zip --exclude="__pycache__" --exclude=".vscode" --exclude="*.pyc" .

ECHO.
ECHO ==========================================================
ECHO    ✅ SUCESSO! O pacote 'AINavigator_Installer.zip' foi criado.
ECHO ==========================================================
PAUSE