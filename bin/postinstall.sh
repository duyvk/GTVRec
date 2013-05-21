python waitfordb.py
python ../manage.py syncdb --noinput
python mkadmin.py
mkdir -p ../media ../static
python ../manage.py collectstatic --noinput
