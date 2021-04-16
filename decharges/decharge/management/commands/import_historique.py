import csv
from decimal import Decimal
from typing import List

from django.conf import settings
from django.core.management import BaseCommand

from decharges.decharge.models import Corps, UtilisationTempsDecharge
from decharges.user_manager.models import Syndicat


class Command(BaseCommand):
    help = "Importe l'historique des UtilisationTempsDecharge depuis un csv"
    federation = None

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--csv-file",
            action="store",
            dest="csv_file",
            help="CSV comportant l'historique des utilisation de décharges par les syndiqués",
        )

    def handle(self, *args, **options):
        # Vérifions que la fédération est présente en BDD
        self.federation = Syndicat.objects.filter(is_superuser=True).first()
        if not self.federation:
            print(
                "Les temps importés de l'historique seront rattachés à la fédération, "
                "il est donc nécessaire que la fédération "
                "(syndicat avec les droit django superuser) "
                "soit présente en base de données."
            )
            exit(1)

        with open(options["csv_file"]) as f:
            self.import_history(f)

    def import_history(self, csv_file):
        """
        Le header du CSV à importer ressemble à ceci :

        ['Civilité', 'Prénom', "Nom d'usage", 'Structure ou affectation', 'Corps',
         '2020-2021', '2019-2020', ...]

        :param csv_file: le path du fichier CSV à importer
        :return: None
        """
        reader = csv.reader(csv_file, delimiter=",")
        header = next(reader)
        annees = self._clean_years(header[5:])
        nb_updated = 0
        nb_created = 0
        for history_line in reader:
            civilite = history_line[0].strip()
            prenom = history_line[1].strip()
            nom = history_line[2].strip()
            rne = history_line[3].strip()
            code_corps = (
                history_line[4].strip().zfill(3)
            )  # zfill prepend zeros if needed
            corps, _ = Corps.objects.get_or_create(code_corps=code_corps)
            print(f"Création/mise à jour du temps syndical de {prenom} {nom}")
            for index_annee, annee in enumerate(annees):
                etp = history_line[5 + index_annee]
                if not etp:
                    continue

                # in case the csv was exported with a french locale
                etp = etp.replace(",", ".")
                etp = round(Decimal(etp), settings.PRECISION_ETP)
                if etp == Decimal(0):
                    continue

                already_existing = UtilisationTempsDecharge.objects.filter(
                    prenom=prenom,
                    nom=nom,
                    annee=annee,
                    code_etablissement_rne=rne,
                )
                if already_existing:
                    utilisation_tps_decharge = already_existing.first()
                    utilisation_tps_decharge.corps = corps
                    utilisation_tps_decharge.civilite = civilite
                    utilisation_tps_decharge.syndicat = self.federation
                    utilisation_tps_decharge.etp = etp
                    utilisation_tps_decharge.save()
                    nb_updated += 1
                else:
                    UtilisationTempsDecharge.objects.create(
                        prenom=prenom,
                        nom=nom,
                        code_etablissement_rne=rne,
                        annee=annee,
                        corps=corps,
                        civilite=civilite,
                        syndicat=self.federation,
                        etp=etp,
                        commentaire_de_mise_a_jour="Importé depuis le document historique",
                    )
                    nb_created += 1

        print("\nFin de l'import")
        print(f"{nb_updated} temps mis à jour")
        print(f"{nb_created} temps créés")

    @staticmethod
    def _clean_years(years: List[str]):
        return [int(year.split("-")[0]) for year in years]
