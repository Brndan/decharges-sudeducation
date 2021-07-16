import datetime

from decharges.decharge.models import CIVILITE_AFFICHEE, UtilisationTempsDecharge


def aggregation_par_beneficiaire(utilisation_temps_decharges):
    """
    Aggrège les bénéficiares par prenom/nom/RNE. Cela permet par exemple de rassembler
    les bénéficiaires de temps de décharge de plusieurs syndicats

    :param utilisation_temps_decharges: les bénéficiaires à aggréger
    :return: Un dictionnaire représentant un tableau avec les noms des colonnes
    """
    beneficiaires = {}
    annees = set()

    for utilisation_temps_decharge in utilisation_temps_decharges:
        key = (
            f"{utilisation_temps_decharge.prenom}%"
            f"{utilisation_temps_decharge.nom}%"
            f"{utilisation_temps_decharge.code_etablissement_rne}"
        )
        beneficiaires[key] = beneficiaires.get(key, []) + [utilisation_temps_decharge]
        annees.add(utilisation_temps_decharge.annee)

    annees = sorted(annees, reverse=True)

    code_organisations = []
    m_mmes = []
    prenoms = []
    noms = []
    heures_decharges = []
    minutes_decharges = []
    etps_par_annee = []
    heures_ors = []
    minutes_ors = []
    aires = []
    corps = []
    rnes = []
    dates_debut = []
    dates_fin = []
    for temps_de_decharges_par_beneficiaire in beneficiaires.values():
        etp_par_annee = {annee: 0 for annee in annees}
        total_heures_decharges = 0
        for (
            temps_de_decharge
        ) in temps_de_decharges_par_beneficiaire:  # type: UtilisationTempsDecharge
            total_heures_decharges += temps_de_decharge.heures_de_decharges
            etp_par_annee[temps_de_decharge.annee] += temps_de_decharge.etp_utilises
        code_organisations.append("S01")  # le `Code organisation` est fixe
        temps_de_decharge = temps_de_decharges_par_beneficiaire[0]
        civilite = temps_de_decharge.civilite
        m_mmes.append(CIVILITE_AFFICHEE.get(civilite, civilite))
        prenoms.append(temps_de_decharge.prenom)
        noms.append(temps_de_decharge.nom)
        etps_par_annee.append(etp_par_annee)
        heures_decharges.append(int(total_heures_decharges))
        minutes_decharges.append(
            round((total_heures_decharges - int(total_heures_decharges)) * 60)
        )
        heures_ors.append(temps_de_decharge.heures_d_obligation_de_service)
        minutes_ors.append(0)  # aujourd'hui les `Heures ORS` sont entiers
        aires.append(2)  # le `AIRE` est fixe
        corps.append(
            temps_de_decharge.corps.code_corps if temps_de_decharge.corps else ""
        )
        rnes.append(temps_de_decharge.code_etablissement_rne)
        annee_courante = temps_de_decharge.annee
        date_debut_decharge = temps_de_decharge.date_debut_decharge or datetime.date(
            year=annee_courante, month=9, day=1
        )
        date_fin_decharge = temps_de_decharge.date_fin_decharge or datetime.date(
            year=annee_courante + 1, month=8, day=31
        )
        dates_debut.append(date_debut_decharge.strftime("%d/%m/%Y"))
        dates_fin.append(date_fin_decharge.strftime("%d/%m/%Y"))

    return {
        "code_organisations": code_organisations,
        "m_mmes": m_mmes,
        "prenoms": prenoms,
        "noms": noms,
        "heures_decharges": heures_decharges,
        "minutes_decharges": minutes_decharges,
        "etps_par_annee": etps_par_annee,
        "heures_ors": heures_ors,
        "minutes_ors": minutes_ors,
        "aires": aires,
        "corps": corps,
        "rnes": rnes,
        "dates_debut": dates_debut,
        "dates_fin": dates_fin,
    }


def calcul_repartition_temps(
    annee_en_cours,
    federation,
    syndicat,
    excluded_utilisation_temps_de_decharge_pk=None,
    excluded_temps_de_decharge_donne_pk=None,
    excluded_utilisation_cts_ponctuel_pk=None,
):
    temps_utilises = syndicat.utilisation_temps_de_decharges_par_annee.filter(
        annee=annee_en_cours,
        supprime_a__isnull=True,
    ).exclude(pk=excluded_utilisation_temps_de_decharge_pk)
    temps_utilises_total = sum(
        temps_consomme.etp_utilises
        for temps_consomme in temps_utilises
        if not temps_consomme.est_une_decharge_solidaires
    )
    temps_donnes = syndicat.temps_de_decharges_donnes.filter(
        annee=annee_en_cours,
    ).exclude(pk=excluded_temps_de_decharge_donne_pk)
    temps_donnes_total = sum(
        temps_donne.temps_de_decharge_etp for temps_donne in temps_donnes
    )
    temps_decharge_federation = None
    temps_recus_par_la_federation = 0
    temps_recus_par_des_syndicats = 0
    for temps_recu in syndicat.temps_de_decharges_par_annee.filter(
        annee=annee_en_cours,
    ):
        if (
            temps_recu.syndicat_donateur is not None
            and temps_recu.syndicat_donateur != federation
        ):
            temps_recus_par_des_syndicats += temps_recu.temps_de_decharge_etp
        else:
            temps_recus_par_la_federation += temps_recu.temps_de_decharge_etp
            temps_decharge_federation = temps_recu
    temps_restant = (
        temps_recus_par_la_federation
        + temps_recus_par_des_syndicats
        - temps_utilises_total
        - temps_donnes_total
    )
    cts_consommes = (
        syndicat.utilisation_cts_ponctuels_par_annee.filter(annee=annee_en_cours)
        .exclude(pk=excluded_utilisation_cts_ponctuel_pk)
        .first()
    )
    if cts_consommes:
        temps_restant -= cts_consommes.etp_utilises

    return (
        cts_consommes,
        temps_decharge_federation,
        temps_donnes,
        temps_donnes_total,
        temps_recus_par_des_syndicats,
        temps_recus_par_la_federation,
        temps_restant,
        temps_utilises,
        temps_utilises_total,
    )
