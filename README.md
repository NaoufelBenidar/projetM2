# projetM2



Le script Python dans script/cleanning permet de nettoyer automatiquement un ou plusieurs datasets au format CSV ou Parquet. Il supprime les colonnes non définies dans le fichier `features.json`, traite les valeurs nulles, corrige certains types mixtes, harmonise les catégories textuelles et filtre les valeurs aberrantes selon des règles prédéfinies. 

`{ 
 	"nom_colonne_1":["stat"],
  	"nom_colonne_2":["binary"],
	"nom_colonne_3":["between",valeur_min,valeur_max],
  	"nom_colonne_4":["above",valeur_min],
	"nom_colonne_5":["under_equal",valeur_max] 
}`

Pour fonctionner correctement, le projet doit contenir un fichier `features.json` ainsi qu’un dossier `data/` regroupant les datasets à traiter. L'arborescence requise est la suivante :

├─ script.py
├─ project/
│   ├─ features.json
│   └─ data/
│       ├─ dataset1.csv
│       ├─ dataset2.csv
│       └─ ...

Le script modifie directement les fichiers présents dans ce dossier : il est donc indispensable de conserver une copie des données originales avant exécution.

---



Rapport

Lien Diapo :"https://www.canva.com/design/DAHCgwJftTg/46nRouDq1za9RCLHZh27DQ/edit?utm_content=DAHCgwJftTg&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton"
