import pandas as pd 
import os

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

def main() :
    repo = './bdd_2/Processed_IoT_dataset/' #Entrez le chemin vers le dossier contenant un ou plusieurs dataset
    read_csv_file(repo) #Choissiez la bonne fonction selon si ce sont des fichiers csv ou parquets
    # read_parquet_file(repo)
    

def read_parquet_file(repo):
    """ Lis et appele des fonction pour traiter un répertoire contenant des fichier parquet de dataset

    Args : 
        repo (str): Chemin vers le répertoir  
    
    """

    file_list = os.listdir(repo)

    for file in file_list :
        path = repo + file
        data = pd.read_parquet(path)
        is_null = is_values_null(data, file, path)
        mixed_type_columns(data, path)

        if is_null :
            clean_db(data, path)


def read_csv_file(repo):
    """ Lis et appele des fonction pour traiter un répertoire contenant des fichier csv de dataset

    Args : 
        repo (str): Chemin vers le répertoir  
    
    """

    file_list = os.listdir(repo)

    for file in file_list :
        print(file)
        path = repo + file
        data = pd.read_csv(path)
        is_null = is_values_null(data, file, path)
        mixed_type_columns(data, path)

        if is_null :
            clean_db(data, path)


def is_values_null(data, file, path) :
    """ Vérifie si il existe des valeurs nulles dans le dataset en traitement

    Args : 
        data (pd.DataFrame): le dataset
        file (str): nom du fichier contenant le dataset
        path (str): chemin du fichier contenant le dataset
    
    Returns : 
        (bool) : True si il y a des des valeurs nulles et False sinon
    """

    missing_values = data.isnull()

    col_null = []
    data = data.replace({"Null": pd.NA, "na": pd.NA, "": pd.NA, " ": pd.NA})
    data.to_csv(path, index = False)


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


def mixed_type_columns(data, file):
    """ Vérifie si il y a des colones contenant plusieurs types différents, si c'est le cas,
    un seul type est conservé et les valeurs sont transformé ou supprimée puis le fichier est enregistré
    (ici seul le mélange booléen et int/float a été traîté)

    Args : 
        data (pd.DataFrame): le dataset
        file (str): nom du fichier contenant le dataset
    
    """

    mixed_cols = []
    for col in data.columns:
        types_in_col = set(type(v) for v in data[col].dropna())
        if len(types_in_col) > 1:
            mixed_cols.append((col, types_in_col))
    
    for col, types_in_col in mixed_cols :
       if str in types_in_col and (int in types_in_col or float in types_in_col):
        print("there are mixed types")
        data[col] = (
            data[col].astype(str).str.strip().str.lower().replace({
                "1" : "true",
                "0" : "false",
                "0.0" : "false",
                "1.0" : "true"
            })
        ) 
        data.to_csv(file, index = False)


def clean_db(data, path):
    """ Nettoyage des données

    Args : 
        data (pd.DataFrame): le dataset
        path (str): chemin du fichier contenant le dataset
    
    """

    data_cleaned = data.dropna()

    n_removed = len(data) - len(data_cleaned)
    print(f"Lignes supprimées : {n_removed}")

    data_cleaned.to_csv(path, index = False)



main()
