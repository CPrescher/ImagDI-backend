set FLASK_APP=imagdi
set FLASK_ENV=development
cd %~dp0
conda activate .\envs && flask run --with-threads
