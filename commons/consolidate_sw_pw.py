import pandas as pd
import slugify
from sys import platform
#from lxml.doctestcompare import strip

def is_duplicates(item, list_):
    list_ = [slugify.slugify(i) for i in list_]
    indexes = [i for i in list_ if slugify.slugify(item) == i]
    return len(indexes) > 1

def file_mapping():
    path = input("Saisissez le chemin absolu de votre fichier:\t\n")
    if not path.lower().endswith(('.xls', '.xlsx')):
        print("Ce fichier n'est pas un fichier excel")
        return

    # pw_columns = ["Date heure1", "Véhicule", "Remorque", "Point Passage1 Designation", "Point Passage2 Designation",
    #                    "Produit designation", "Poids brut", "Poids tare", "Poids net", "Tiers / Acconier designation",
    #                    "Chargeur designation", "Transporteur designation", "Navire / Origine  designation",
    #                    "Destination designation", "Montant perçu  designation", "Container", "N° Plomb",
    #                    "Reste à rembourser  designation", "AutoEnlev / Embarq", "N° Colis", "Poids1", "Type",
    #                    "Activité", "Poids2", "Chauffeur", "Chantier", "N° CAP", "Numero", "Numero", "Point Passage1",
    #                    "Container  designation", "Destination", "Montant perçu", "Tiers / Acconier", "Navire / Origine",
    #                    "Chargeur", "Reste à rembourser", "Transporteur", "Type chargeur", "Chargeur  adresse1",
    #                    "Chargeur  adresse2", "Chargeur  adresse3", "Chargeur  code postal", "Chargeur  ville",
    #                    "Chargeur  pays", "Chargeur  pays", "Chargeur  siret", "Type destination",
    #                    "Type destination designation", "Destination adresse1", "Destination adresse2",
    #                    "Destination adresse3", "Destination code postal", "Destination ville", "Destination pays",
    #                    "Destination siret", "Remorque  designation", "N° Plomb  designation", "N° Colis  designation",
    #                    "Chauffeur  designation", "AutoEnlev / Embarq  designation", "Type véhicule  conteneur accepte",
    #                    "Annulé", "CAP designation", "N° FID", "Lecteur RFID1", "Lecteur RFID1 Designation",
    #                    "Lecture LAPI1", "Date heure2", "Utilisateur 1", "Utilisateur 2"]

    pw_columns = ["Date heure1", "Véhicule", "Remorque", "Point Passage1 Designation", "Point Passage2 Designation",
                  "Produit designation", "Poids brut", "Poids tare", "Poids net", "Tiers / Acconier designation",
                  "Chargeur designation", "Transporteur designation", "Navire / Origine designation",
                  "Destination designation", "Montant perçu designation", "Container", "N° Plomb",
                  "Reste à rembourser designation", "AutoEnlev / Embarq", "N° Colis", "Poids1", "Type",
                  "Activité", "Poids2", "Chauffeur", "Chantier", "N° CAP", "Numero", "Numero1", "Point Passage1",
                  "Destination", "Container designation", "Montant perçu", "Tiers / Acconier", "Navire / Origine",
                  "Chargeur", "Reste à rembourser", "Transporteur", "Type chargeur", "Chargeur  adresse1",
                  "Type véhicule  conteneur accepte", "Chargeur  adresse2", "Chargeur  adresse3",
                  "Chargeur  code postal", "Chargeur  ville",
                  "Chargeur  pays", "Chargeur  pays1", "Chargeur  siret", "Type destination",
                  "Type destination designation", "Destination adresse1", "Destination adresse2",
                  "Destination adresse3", "Destination code postal", "Destination ville", "Destination pays",
                  "Destination siret", "Remorque designation", "N° Plomb designation", "N° Colis designation",
                  "Chauffeur designation", "AutoEnlev / Embarq  designation", "Annulé", "CAP designation",
                  "N° FID", "Lecteur RFID1", "Lecteur RFID1 Designation",
                  "Lecture LAPI1", "Date heure2", "Utilisateur 1", "Utilisateur 2"]

    sw_columns_slug = ['date-pesee-1', 'heure-pesee-1', 'ndeg-immatriculation', 'remorque', 'pont-de-la-pesee-1',
                       'pont-de-la-pesee-2', 'produit', 'poids-2', 'poids-1', 'poids-net', 'tier', 'chargeur',
                       'transporteur', 'origine-navire', 'destination', 'paiement', 'conteneur', 'plomb',
                       'type-conteneur', 0, 0, 0, 0, 'activite', 0, 'chauffeur', 'ndeg-bon-de-livraison',
                       'ndeg-colis', 'code-de-pesee', 0, 'pont-de-la-pesee-1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'remorque', 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 'date-pesee-2', 'heure-pesee-2', 'operateur-1', 'operateur-2']

    sw_columns = ['Date-pesée 1', 'Heure-pesée 1', 'N° immatriculation', 'Remorque', 'Pont de la pesée 1',
                    'Pont de la pesée 2', 'Produit', 'Poids 2', 'Poids 1', 'Poids net', 'Tier', 'Chargeur',
                    'Transporteur', 'Origine/Navire', 'Destination', 'Paiement', 'Conteneur', 'Plomb', 'TYPE CONTENEUR',
                    0, 0, 0, 0, 'ACTIVITE', 0, 'Chauffeur', 'N° Bon de livraison', 'N° COLIS', 'Code de pesée', 0,
                    'Pont de la pesée 1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 'Remorque', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'Date-pesée 2', 'Heure-pesée 2', 'Opérateur 1',
                    'Opérateur 2']

    print("Chargement du fichier Excel...\n")

    try:
        df_sw = pd.read_excel(path)
    except Exception as e:
        print(e)
        print(f"\nLes libellés des colonnes attendues sont:\n {sw_columns}")
        return
    print("Chargement du fichier terminé avec succès...\n\n")
    column_dict = dict()
    missed_columns = []
    for column in [sw for sw in sw_columns_slug if sw]:
        if column not in [slugify.slugify(k) for k in df_sw.columns.tolist()]:
            missed_columns.append(sw_columns[sw_columns_slug.index(column)])
    for column in df_sw.columns:
        if slugify.slugify(column) in [k for k in sw_columns_slug if k]:
            column_dict[column] = slugify.slugify(column)
    data = dict()
    print("\n")
    df_sw = df_sw.rename(columns=column_dict)
    df_sw = df_sw.fillna('')
    print("\n")
    if missed_columns:
        print("Erreur!! Les libellés des colonnes possèdent des erreurs d'orthographe ou sont incomplètes\n"
              "Veuillez vérifier le fichier\n")
        print(f"Les libellés des colonnes manquantes sont: {missed_columns}\n")
        return
    sw_columns_slug = [s if s else " "  for s in sw_columns_slug ]
    for k,i in zip(pw_columns, range(pw_columns.__len__())):
    # Loop on headers of PowerWeight columns
        if sw_columns_slug[i].__contains__("date"):
            data[k] = pd.Series([f"{p} {m}" for p, m  in zip(df_sw[sw_columns_slug[i]], df_sw["heure-pesee-" + sw_columns_slug[i].split('-')[-1]])])
            sw_columns_slug.pop(sw_columns_slug.index("heure-pesee-" + sw_columns_slug[i].split('-')[-1]))
        else :
            if is_duplicates(k, pw_columns):
                # Special treatment for duplicated columns
                if i < pw_columns.__len__() - 1 and pw_columns[i] == pw_columns[i + 1]:
                    data[k + "2"] = " "
                    data[k] = " "
                else:
                    continue
            else:
                try:
                    data[k] = df_sw[sw_columns_slug[i]]
                except:
                    data[k] = " "
    dataframe = pd.DataFrame.from_dict(data)
    # print(dataframe.columns)
    # print("\n")
    # print(pw_columns)
    dataframe.columns = pw_columns
    print("\nGénération du fichier Excel consolidé...\n\n")
    document_name = path.split('/')[-1].split('.')[0]
    if platform.lower().__contains__("win"):
        document_name = path.split('\\')[-1].split('.')[0]
    dataframe.to_excel(f"CONSOLIDE_{document_name}.xlsx", index=False)
    print("Fin de tâche...\n\n")


if __name__ == '__main__':
    file_mapping()

