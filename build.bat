pyinstaller -F armcom2.py
copy /y .\campaigns\*.json .\dist\campaigns
copy /y .\data\*.json .\dist\data
copy /y .\data\*.xp .\dist\data
copy /y .\data\*.png .\dist\data
copy /y .\sounds\*.ogg .\dist\sounds
del .\dist\data\armcom2.cfg