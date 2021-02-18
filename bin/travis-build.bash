    #nex!/bin/bash
set -e

echo "This is travis-build.bash..."

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq

if python -c 'import sys;exit(sys.version_info < (3,))'
then
    PYTHONVERSION=3
else
    PYTHONVERSION=2
fi

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
if [ $CKANVERSION == 'master' ]
then
    echo "CKAN version: master"
else
    CKAN_TAG=$(git tag | grep ^ckan-$CKANVERSION | sort --version-sort | tail -n 1)
    git checkout $CKAN_TAG
    echo "CKAN version: ${CKAN_TAG#ckan-}"
fi

echo "Installing the recommended setuptools requirement"
if [ -f requirement-setuptools.txt ]
then
    pip install -r requirement-setuptools.txt
fi

python setup.py develop

if [ -f requirements-py2.txt ] && [ $PYTHONVERSION = 2 ]
then
    pip install -r requirements-py2.txt
else
    pip install -r requirements.txt
fi

pip install -r dev-requirements.txt

cd -

echo "Setting up Solr..."
docker run --name ckan-solr -p 8983:8983 -d openknowledge/ckan-solr-dev:$CKANVERSION

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "Initialising the database..."
cd ckan
if [ $CKANVERSION \< '2.9' ]
then
    paster db init -c test-core.ini
else
    ckan -c test-core.ini db init
fi
cd -

echo "Installing extension and its requirements..."
pip install -r requirements.txt
pip install -r dev-requirements.txt
python setup.py develop

echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

echo "travis-build.bash is done."
