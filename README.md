# Gestion des décharges syndicales

Ce projet a pour objectif de gérer les décharges syndicales de SUD éducation (https://www.sudeducation.org/)

## Développement

### Gestion des dépendences

Les dépendances sont listées dans `setup.cfg`, sous la section `[options]`, soit dans `install_requires` (si c'est un requirement de production), ou dans `tests_require` (si c'est un requirement uniquement pour le developpement ou les tests).

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
(venv-decharges) $ pip install -Ur requirements-tests.txt
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

Notez que la base de données doit bien être en UTF-8, cf la documentation de django : https://docs.djangoproject.com/en/dev/ref/databases/#encoding

Ensuite, lancez les migrations django :

```bash
(venv-decharges) $ ./manage.py migrate
```

Vous pouvez également créer un superuser si vous le souhaitez : 

```bash
(venv-decharges) $ ./manage.py createsuperuser
```

### Rassembler les statiques

Cette commande permet de rassembler tous les fichiers statiques dans un même dossier, de manière à le servir efficacement avec nginx ou apache

```bash
(venv-decharges) $ ./manage.py collectstatic
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
- **MEDIA_ROOT** : le chemin des fichiers médias (fichiers uploadés par exemple), si non spécifié `./media` est utilisé
- **EMAIL_BACKEND** : la méthode django pour envoyer des mails, par défaut `django.core.mail.backends.console.EmailBackend` est utilisé ce qui permet de voir les mails envoyés dans la console django. En production il fautdra sûrement utiliser `django.core.mail.backends.smtp.EmailBackend`
- **EMAIL_HOST** : le nom de domaine ou l'adresse IP du serveur mail SMTP
- **EMAIL_PORT** : le port du serveur mail SMTP, si non spécifié `587` est utilisé
- **EMAIL_HOST_USER** : l'utilisateur se connectant au serveur mail SMTP, si non spécifié `admin@sudeducation.hashbang.fr` est utilisé
- **EMAIL_HOST_PASSWORD** : le mot de passe utilisé pour se connecter au serveur mail SMTP
- **EMAIL_USE_TLS** : `True` si le serveur mail SMTP supporte le TLS, `False` sinon. Le défaut est `True`
- **DJANGO_DEFAULT_FROM_EMAIL** : l'adresse mail envoyant les emails de l'application, si non spécifié `admin@sudeducation.hashbang.fr` est utilisé
- **DJANGO_DEFAULT_FROM_EMAIL_NAME** : le nom de la personne envoyant les emails de l'application, si non spécifié `admin` est utilisé
- **DJANGO_SETTINGS_MODULE** : les settings à utiliser, mettre `decharges.settings` en production

## Import des données

**Importer les Académies / Syndicats :**

Attention, avant de lancer cette commande, vous pouvez modifier les emails des syndicats contenus dans le JSON,
afin d'avoir directement des données correctes en base de données. Cependant vous pourrez faire la modification a posteriori si vous
préférez.

```bash
$ ./manage.py loaddata decharges/user_manager/fixtures/academies_syndicats.json
```

Note : Le script d'import utilisé pour générer cette fixture se trouve dans `imports/academies`

**Créer un parametre d'application**

Cette commande n'aura pas d'effet si une instance existe déjà, ce qui est l'effet escompté.

```bash
$ ./manage.py shell <<< "from decharges.parametre.models import *; ParametresDApplication.objects.get_or_create()"
```

**Importer l'historique**

Avant tout, générer un fichier historique en CSV et stockez-le dans `imports/historique/historique.csv`
(un exemple d'un tel fichier est présent dans le dossier)

**/!\\ /!\\ Attention :** le formattage du fichier CSV est important :

- la virgule doit être utilisée comme séparateur
- le guillement double `"` est utilisé pour délimiter les champs contenant des caractères spéciaux ('delimiter' ou 'quotechar')
- la première ligne doit contenir les headers du CSV, à savoir : Civilité, Prénom, Nom d'usage, Structure ou affectation, Corps, [les années]

Pour être sûr que le CSV est dans le bon format, un exemple est présent dans **imports/historique/historique.csv**

Assurez-vous également que la fédération a bien un compte sur le site avant de passer à la suite.

Lancez cette commande :

```bash
$ ./manage.py import_historique --csv-file=imports/historique/historique.csv
```

### Import des Corps

Une fois que l'application est lancée en production vous pouvez vous dirigez ici : https://example.com/admin/parametre/parametresdapplication/ et éditer l'objet existant.

On vous proposera alors d'ajouter un fichier "Corps annexe". Cela va avoir 3 effets :

1. Les utilisatrices et utilisateurs auront accès à ce fichier dans le formulaire d'ajout d'un·e bénéficiaire
2. La première colonne de ce fichier est utilisée pour importer les Corps dans l'application
3. Les Corps non-utilisés (avant l'import) présents en BDD seront supprimés

Un exemple d'un fichier à importer est présent ici : `decharges/decharge/tests/assets/corps_example.ods`

## Organisation du code

### `decharges/settings/base.py` :

Contient toutes les variables de l'application Django.

- `NB_HOURS_IN_A_YEAR` : à changer si le nombre d'heure d'un temps plein en une année n'est plus 1607
- `CHOIX_ORS` : les heures d'obligation de service possibles dans le formulaire
- `MAX_ETP_CONSECUTIFS` : le nombre maximum d'ETP consécutifs dans les statuts (3 ETP au moment d'écriture de cette doc)
- `ALERT_ETP_CONSECUTIFS` : le nombre d'ETP consécutif à partir duquel on alerte que cette personne approche les limites
- `MAX_ANNEES_CONSECUTIVES` : le nombre maximum d'années de délégation consécutives dans les statuts (8 ans au moment d'écriture de cette doc)
- `ALERT_ANNEES_CONSECUTIVES` : le nombre d'années de délégation consécutives à partir duquel on alerte que cette personne approche les limites
- `NB_ANNEES_POUR_REINITIALISER_LES_COMPTEURS` : le nombre d'années nécessaires pour réinitialiser les compteurs ci-dessus (ETPs cumulés et années de décharge consécutives)
- `MAX_ETP_EN_UNE_ANNEE` : le nombre d'ETP maximum pour un·e bénéficiaire en une année (0.5 à l'heure d'ecriture de la documentation)

### `decharges/decharge`

L'application django principale, où se trouvent les données d'attribution et d'utilisation des temps de décharges.

Notamment :

- validators.py : contient les validateurs des données côté backend
- models.py : contient les modèles de données
- forms/ : contients les formulaires django, permettant de transformer les données utlisateur en objets python et de valider plus finement les données utilisateur
- tests/ : les tests de l'application
- templates/ : les fichiers HTML de l'application, écrits en django-template
- views/ : les fonctions qui répondent aux appels HTTP du client. Pour organiser au maximum le code, il y a un fichier par page (ex: `accueil.py`) ou par modèle de données (ex: `temps_de_decharge.py`)
- urls.py : permet de faire la liaison entre les URLs de l'application et les views (ci-dessus) appelées

### `decharges/parametres`

Une petite application permettant de gérer les paramètres du site via l'interface admin de django. Par exemple :

- l'année en cours, pour savoir quelles données afficher
- si oui ou non les syndicats peuvent accéder à l'édition des décharges
- téléverser le fichier annexe des Corps

### `decharges/user_manager`

L'application permettant de gérer les utilisateurs. Vous y trouverez notamment :

- le modèle de `Syndicat` (qui hérite du modèle User de django)
- le modèle `Academie` qui regroupe les syndicats
- les templates (decharges/user_manager/templates/registration) qui surchargent les templates de base de la gestion d'utilisateurs de django

## Logiques spécifiques

### Nom/Prénom/RNE

Dans l'application un·e bénéficiaire est identifié·e de manière via trois données : son nom, son prénom et son RNE (identifiant d'établissement).

Ce qui signifie que si deux syndicats souhaitent donner du temps de décharge à une même personne, les syndicats doivent faire
attention à bien renseigner le nom/prénom/RNE de la personne sans faute de frappe.

### Attribution de temps et partage académique

Dans decharges/decharge/models.py quatre modèles sont présents (au moment de l'ecriture de la documentation):

- Corps
- UtilisationTempsDecharge
- UtilisationCreditDeTempsSyndicalPonctuel
- TempsDeDecharge

Le `Corps` représente le Corps d'enseignement est est juste constitué d'un code.

Une instance de `UtilisationTempsDecharge` décrit le temps de décharge utilisé par un·e bénéficiaire (nom/prénom/RNE) pour une année donnée (ex: 2020-2021) dans un syndicat donné.

Une instance de `UtilisationCreditDeTempsSyndicalPonctuel` décrit le temps de décharge en CTS utilisé par un syndicat pour une année donnée (ex: 2020-2021)

Une instance de `TempsDeDecharge` représente un "échange" de temps de décharge pour une année donnée. Une instance de `TempsDeDecharge` peut donc représenter plusieurs choses différentes :

- si le `syndicat_donateur` n'est pas spécifié (ou est le syndicat de la Fédération), cette instance représente le quota d'ETP attribué par la fédération au `syndicat_beneficiaire` pour une année donnée
- si le `syndicat_donateur` est spécifié (et différent de la fédération), alors l'instance représente une mutualisation académique : le `syndicat_donateur` donne `temps_de_decharge_etp` au `syndicat_beneficiaire` à une année donnée
- enfin si le `syndicat_beneficiaire` est la Fédération, l'instance représente le quota en ETP donné à SUD par le ministère pour une année donnée
