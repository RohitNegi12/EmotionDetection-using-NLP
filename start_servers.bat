cd "Emotion Detection 2"
\venv\Scripts\activate.bat
start "Back-end Server" flask --app analysis.py run --debug
deactivate
cd ../
cd "Emotion Detection GUI/"
\venv\Scripts\activate.bat
start "GUI Server" streamlit run main.py