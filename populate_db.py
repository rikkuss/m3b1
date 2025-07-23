import pandas as pd
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from database import SessionLocal, engine
from models import Client, Base, ClientMeta, ClientSituation, Contrat

# Chemin vers votre fichier CSV
CSV_FILE_PATH = "donnees_nettoyees.csv"

def populate_database():
    """
    Lit les données d'un fichier CSV, les transforme et les insère dans la base de données SQLite.
    """
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        logger.info(f"Lecture du fichier CSV : {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH)
        df = df.where(pd.notna(df), None)

        clients_to_add = []
        logger.info(f"{len(df)} lignes trouvées. Début de la transformation et de l'insertion...")

        for _, row in df.iterrows():
            client = Client(
                client_meta = ClientMeta(
                    age=row['age'],
                    poids=row['poids'],
                    niveau_etude=row['niveau_etude'],
                    smoker=(row['smoker'] == 'oui'),
                    situation_familiale=row['situation_familiale'],
                ),
                client_situation = ClientSituation(
                    revenu_estime_mois=row['revenu_estime_mois'],
                    risque_personnel=row['risque_personnel'],
                    loyer_mensuel=row['loyer_mensuel'],
                ),
                contrats = [Contrat(
                    montant_pret=row['montant_pret'],
                )]
            )
            clients_to_add.append(client)

        db.add_all(clients_to_add)

        db.commit()

        logger.success(f"{len(clients_to_add)} clients ont été ajoutés avec succès à la base de données !")

    except FileNotFoundError:
        logger.error(f"Le fichier {CSV_FILE_PATH} n'a pas été trouvé. Vérifiez le chemin d'accès.")
    except Exception as e:
        logger.error(f"Une erreur est survenue : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()