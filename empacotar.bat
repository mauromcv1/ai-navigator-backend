@echo off
ECHO ==========================================================
ECHO            EMPACOTANDO O AI NAVIGATOR
ECHO ==========================================================
ECHO.
ECHO Criando a lista de ferramentas (requirements.txt)...
py -m pip freeze > requirements.txt

ECHO.
ECHO Criando o arquivo de instalacao (AINavigator_Installer.zip)...
ECHO (Isso pode levar um momento)
ECHO.

:: Usa o comando 'tar' (presente no Windows 10/11) para criar um zip
:: Ignorando pastas de cache e arquivos desnecessários
tar -a -cf AINavigator_Installer.zip --exclude="__pycache__" --exclude=".vscode" --exclude="*.pyc" .

ECHO.
ECHO ==========================================================
ECHO    ✅ SUCESSO! O pacote 'AINavigator_Installer.zip' foi criado.
ECHO    Copie este arquivo e o 'instalar.bat' para a nova maquina.
ECHO ==========================================================
PAUSE