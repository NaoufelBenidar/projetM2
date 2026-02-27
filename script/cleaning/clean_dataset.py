import json
import pandas as pd
import os
import numpy as np


def main() :

    repository = './2_dirt_UNSW_NB15/' #Entrez le chemin vers le dossier contenant un ou plusieurs dataset
    repository_data = repository + 'data/'
    repository_features = repository + 'features.json'

    with open(repository_features, 'r', encoding='utf-8') as fichier:
        data_json = json.load(fichier)         

    # Vérification du types des fichiers
    files_list = os.listdir(repository_data)
    extensions = []

    for file in files_list :
        ext = os.path.splitext(file)
        extensions.append(ext)
    
    #  Ouverture et traîtement des fichiers selon leur type
    if '.parquet' in extensions : 
        for data,path,file in read_parquet_file(repository_data):

            data = delete_columns(data, data_json)            

            data = mixed_type_columns(data, path)

            is_null = is_values_null(data, file, path)
            
            if is_null :
                data = clean_db_null(data, file, path)

            data = clean_db_outlier(data, data_json, file)
            data = clean_wrong_words(data)

            data.to_csv(path, index = False)

    else : 
        for data,path,file in read_csv_file(repository_data):

            data = delete_columns(data, data_json)

            # Lignes utilisées pour le premier tri (les colonnes sont trop vides) (UNSW_NB15)
            # data = data.drop(columns = "ct_flw_http")
            # data = data.drop(columns = "is_ftp_login")
            # data = data.drop(columns = 'ct_ftp_cmd')
            
            data = mixed_type_columns(data)

            is_null = is_values_null(data, file)
            
            if is_null :
                data = clean_db_null(data, file)

            data = clean_db_outlier(data, data_json, file)
            data = clean_wrong_words(data)

            data.to_csv(path, index = False)
        
        combine_data(repository_data) # à enlever si pas de concaténation voulue
    
    
def combine_data(repository_data):
    """ Assemble tous les fichiers nettoyés en un seul

        Args : 
            repository_data (str): Repertoire contenant tous les fichiers nettoyés
    
    """

    all_data = pd.DataFrame() 
    for filename in os.listdir(repository_data):
        if filename.endswith(".csv"):
            file_path = os.path.join(repository_data, filename)
            data = pd.read_csv(file_path)  # Read each CSV file into a DataFrame
            all_data = pd.concat([all_data, data], ignore_index=True)  # Concatenate the data
    path = repository_data + 'combine.csv'
    all_data.to_csv(path, index = False)


def read_parquet_file(repository_data):
    """ Ouvre les fichiers parquet des datasets et crée un dataset pandas pour chacun, 
        il affiche le nombre de lignes

        Args : 
            repository_data (str): Chemin vers le répertoir contenant les datasets
        
        Returns : 
            data (DataFrame) : le dataset modifié
            path (str) : le chemin complet du fichier
            file (str) : le nom du fichier
    """

    file_list = os.listdir(repository_data)

    for file in file_list :
        print(file)
        path = repository_data + file
        data = pd.read_parquet(path)
        print("lignes total dans", file," :", len(data))
        yield data, path, file


def read_csv_file(repository_data):
    """ Ouvre les fichiers csv des datasets et crée un dataset pandas pour chacun, 
        il affiche le nombre de lignes

        Args : 
            repository_data (str): Chemin vers le répertoir contenant les datasets
        
        Returns : 
            data (DataFrame) : le dataset modifié
            path (str) : le chemin complet du fichier
            file (str) : le nom du fichier
    """

    files_list = os.listdir(repository_data)

    for file in files_list :
        print(file)
        path = repository_data + file
        data = pd.read_csv(path)
        print("lignes total dans", file," :", len(data))
        yield data, path, file


def delete_columns(data, data_json):
    """ Supprime les colonnes non présentes dans le fichier features.json

        Args : 
            data (DataFrame): DataSet Pandas traîté actuellement
            data_json (Dictionnaire) : données du fichier features.json
        
        Returns : 
            data (DataFrame) : le dataset modifié
    """

    columns_deleted = []
    columns_names = data_json.keys()    

    data.columns = data.columns.str.strip()

    for column in data.columns:
        if column not in columns_names : 
            data = data.drop(columns = column)
            columns_deleted.append(column)
    print("colonnes supprimées : ", len(columns_deleted), columns_deleted)

    return data


def is_values_null(data, file) :
    """ Vérifie si il existe des valeurs nulles dans le dataset en traitement

        Args : 
            data (pd.DataFrame): le dataset
            file (str): nom du fichier contenant le dataset
        
        Returns : 
            (bool) : True si il y a des des valeurs nulles et False sinon
    """

    col_null = []
    data = data.replace({"Null": pd.NA, "na": pd.NA, "": pd.NA, " ": pd.NA, None: pd.NA, "None": pd.NA})
    missing_values = data.isnull()


    for col, nb_missing in missing_values.items():
        is_null_values = ((nb_missing == 0).all())  # Vérifie si il y a des valeurs nulles dans chaque catégorie (colonne)
        if (is_null_values == False):               # Si il y a des valeurs nulles
            print(data[data[col].isnull()])         # On affiches les colonnes les contenants
            col_null.append(col)

    if len(col_null) > 0 :
        print(col_null)
        return True
    else :
        print("pas de valeurs null dans le fichier : ", file)
        return False


def mixed_type_columns(data):
    """ Vérifie si il y a des colones contenant plusieurs types différents, si c'est le cas,
    un seul type est conservé et les valeurs sont transformé ou supprimée puis le fichier est enregistré
    (ici seul le mélange booléen et int/float a été traîté)

    Args : 
        data (pd.DataFrame): le dataset
    
    """

    for col in data.columns:

        if pd.api.types.is_numeric_dtype(data[col]):
            continue

        converted = pd.to_numeric(data[col], errors="coerce")

        if converted.notna().sum() == data[col].notna().sum():

            if (converted % 1 == 0).all():
                data[col] = converted.astype("Int64")
            else:
                data[col] = converted.astype(float)

            continue 
        else : 
            values = data[col].astype(str).str.strip().str.lower()
            unique_vals = set(values.dropna().unique())

            if unique_vals.issubset({"true", "false"}):
                data[col] = values.map({"true": True, "false": False})
                continue
        
    return data


def clean_db_null(data, file):
    """ Supprime les données nulles

    Args : 
        data (pd.DataFrame): le dataset
        file (str): nom du dataset
    
    """

    data = data.dropna()

    print("lignes aprés nettoyage valeurs nulles dans : ", file, " : ", len(data))
    return data


def clean_db_outlier(data, data_json, file) :
    """ Supprime les données abérantes en se basant sur le fichier features.json

    Args : 
        data (pd.DataFrame): le dataset
        data_json (Dictionnaire): contient les informations sur le dataset pour le néttoyer
        file (str): nom du dataset
    
    """

    columns_names = data_json.keys()

    for column in columns_names : 
        type = data_json[column]
        treatment = type[0]
        match treatment : 
            case "stat" :
                print("traitemant statistique : ", column)
                q1 = np.percentile(data[column], 25)
                q3 = np.percentile(data[column], 75)
                iqr = q3 - q1
                lower_bound = q1 - 3 * iqr
                upper_bound = q3 + 3 * iqr
                print("lower_bound : ", lower_bound)
                print("upper_bound :", upper_bound)
                data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

            case "binary" :
                print("binaire : ", column)
                data = data[data[column].between(0, 1)]
            case "between" :
                print("entre : ", column)
                vmin = type[1]
                vmax = type[2]
                data = data[data[column].between(vmin, vmax)]
            case "under" :
                print("under : ", column)
                vmax = type[1]
                data = data[data[column] < vmax]
            case "above" :
                print("above : ", column)
                vmin = type[1]
                data = data[data[column] > vmin]
            case "under_equal" :
                print("under equal : ", column)
                vmax = type[1]
                data = data[data[column] <= vmax]
            case "above_equal" :
                print("above equal : ", column)
                vmin = type[1]
                data = data[data[column] >= vmin]    

    print("lignes après suppression des valeurs abérantes dans ", file, " : ", len(data))

    return data


def clean_wrong_words(data) :
    """ Modifie les mots qui ont une écriture proche (ajout manuel)

        Args : 
            data (pd.DataFrame): le dataset
    
    """
    # Cas particulier, à enlever ou rajouter si besoin 

    # Pour UNSW_NB15 : 

    data['attack_cat'] = data['attack_cat'].str.strip()
    data['attack_cat'] = data['attack_cat'].replace({
        'Backdoors': 'Backdoor',
        'Fuzzers ': 'Fuzzers',
        ' Reconnaissance ': 'Reconnaissance',
        ' Shellcode ': 'Shellcode'
    })

    data['service'] = data['service'].str.strip()
    data['service'] = data['service'].replace({
        '-' : 'NoServices'
    })

    return data

main()
