# TRIES determines the amount of tries for access to IMDB
TRIES=3

if [ $# -gt 0 ]; then
TRIES=$1
fi

python -m src.update_imdb $TRIES