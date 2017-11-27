# emotion

Command line
```
python main.py [video_name] —interval [time_interval(default: 1)]
```

ex)
```
python main.py bigbang.mkv —interval 3
```

If you already have a metadata file for the video, then
```
python main.py [video_file] --metadata [metadata_file_path]
```
this command will save your time :)


GUI
```
python manage.py runserver
```
if you haven't migrate DB, type
```
python manage.py migrate
```
before running server.


You can reach the web server via localhost:8000

If you want an application format, type
```
python view.py
```

Video files should be located in /emotion directory.

