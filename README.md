# Gestion des décharges syndicales

[![pipeline status](https://gitlab.com/hashbangfr/sudeducation/badges/master/pipeline.svg)](https://gitlab.com/hashbangfr/sudeducation/-/commits/master)
[![coverage report](https://gitlab.com/hashbangfr/sudeducation/badges/master/coverage.svg)](https://gitlab.com/hashbangfr/sudeducation/-/commits/master)

Ce projet a pour objectif de gérer les décharges syndicales de SUD éducation (https://www.sudeducation.org/)

## Développement

### Gestion des dépendences

Les dépendances sont listées dans `setup.cfg`, sous la section `[options]`, soit dans `install_requires` (si c'est un requirement de production), ou dans `tests_require` (si c'est un requirement uniquement pour le dev ou les tests).

Ces 2 listes (`install_requires` et `tests_require`) sont utilisées pour générer 2 fichiers de requirements : celui utilisé en production (`requirements.txt`) et celui utilisé pour le développement et les tests (`requirements-tests.txt`)

Dans l'idéal vous ne devez jamais éditer les fichiers `requirements*.txt` mais éditer le fichier `setup.cfg` puis regénérer les requirements.

Pour générer ces 2 fichiers il vous faut lancer la commande suivante (pip-tools doit être installé dans votre virtualenv ou sur votre machine) :

```bash
./create_requirements.sh
```

Les fichiers de requirements contiennent toutes les dépendances (directes ou indirectes), avec leurs versions fixées.

### Installation des dépendances

Lancer ceci (après avoir créé un environement virtuel python et l'avoir activé) :

```bash
(venv-decharges) $ pip install -r requirements-tests.txt
```

### Préparer la BDD

Le projet utilise le SGBD MariaDB (ou MySQL). Vous devez donc installer MariaDB, lancer le service, puis créer un utilisateur et une base de données :

```bash
$ mysql -uroot -p
[...]
MariaDB [(none)]> CREATE DATABASE decharges CHARACTER SET UTF8;
MariaDB [(none)]> CREATE USER decharges@localhost IDENTIFIED BY 'decharges';
MariaDB [(none)]> GRANT ALL PRIVILEGES ON decharges.* TO decharges@localhost;
```

Ensuite, lancez les migrations django :

```bash
(venv-decharges) $ ./manage.py migrate
```

Vous pouvez également créer un superuser si vous le souhaitez : 

```bash
(venv-decharges) $ ./manage.py createsuperuser
```

### Lancer le serveur

```bash
(venv-decharges) $ ./manage.py runserver
# Site accessible sous http://localhost:8000
```

### Lancer les tests

```bash
(venv-decharges) $ pytest decharges/
```

### Linter le code

black, isort et flake8 sont utilisés pour linter le code de manière à avoir un code homogène. Pour cela lancez la commande suivante :

```bash
(venv-decharges) $ ./lintall.sh
```

Si la commande ne donne aucune erreur votre code est propre !

-----

## Variable d'environnement

Variables d'environnement nécessaires au projet en production

- **SECRET_KEY** : la clé secrète de Django, 64 caractères aléatoires est un bon choix
- **ALLOWED_HOSTS** : la liste des domaines autorisés à acceder à l'application, sous la forme : `example.com,www.example.com`
- **USE_HTTPS** : `True` si l'application est servie en HTTPs, `False` sinon. Le défaut est `True`
- **DB_NAME** : le nom de la base de données mariadb, si non spécifié `decharges` est utilisé
- **DB_USER** : le nom de l'utilisateur se connectant à la base de données mariadb, si non spécifié `decharges` est utilisé
- **DB_PASSWORD** : le mot de passe de l'utilisateur de la base de données mariadb, si non spécifié `decharges` est utilisé
- **DB_HOST** : le nom de domaine ou l'adresse IP de la base de données mariadb. Peut également être le chemin vers la socket mysql, voir : https://docs.djangoproject.com/en/3.2/ref/settings/#host
- **DB_PORT** : le port de la base de données mariadb, si non spécifié le port par défaut de mariadb est utilisé
- **STATIC_ROOT** : le chemin des fichiers statiques, si non spécifié `./static` est utilisé
- **MEDIA_ROOT** : le chemin des fichiers médias, si non spécifié `./media` est utilisé
- **EMAIL_BACKEND** : la méthode django pour envoyer des mails, par défaut `django.core.mail.backends.console.EmailBackend` est utilisé ce qui permet de voir les mails envoyés dans la console django. En production il fautdra sûrement utiliser `django.core.mail.backends.smtp.EmailBackend`
- **EMAIL_HOST** : le nom de domaine ou l'adresse IP du serveur mail SMTP
- **EMAIL_PORT** : le port du serveur mail SMTP, si non spécifié `587` est utilisé
- **EMAIL_HOST_USER** : l'utilisateur se connectant au serveur mail SMTP, si non spécifié `admin@sudeducation.hashbang.fr` est utilisé
- **EMAIL_HOST_PASSWORD** : le mot de passe utilisé pour se connecter au serveur mail SMTP
- **EMAIL_USE_TLS** : `True` si le serveur mail SMTP supporte le TLS, `False` sinon. Le défaut est `True`
- **DJANGO_DEFAULT_FROM_EMAIL** : l'adresse mail envoyant les emails de l'application, si non spécifié `admin@sudeducation.hashbang.fr` est utilisé
- **DJANGO_DEFAULT_FROM_EMAIL_NAME** : le nom de la personne envoyant les emails de l'application, si non spécifié `admin` est utilisé
- **DJANGO_SETTINGS_MODULE** : les settings à utiliser, `decharges.settings`

## Import des données

TODO

## Organisation du code

TODO
