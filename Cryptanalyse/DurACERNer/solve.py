import os
import hashlib


if __name__ == "__main__":
    particule_a = "01 "
    particule_b = "01"

    print(particule_a)
    print(particule_b)

    try:
        if particule_a == particule_b:
            print("Une seule particule ne peut pas produire de collisions !")
            exit(1)
        
        sha256 = hashlib.sha256()
        sha256.update(bytes.fromhex(particule_a))
        position_particule_a = sha256.digest()
        print(position_particule_a.hex())

        sha256 = hashlib.sha256()
        sha256.update(bytes.fromhex(particule_b))
        position_particule_b = sha256.digest()
        print(position_particule_b.hex())

        if position_particule_a == position_particule_b:
            print("Bien joué ! Voici le résultat de l'analyse des données :")
            print(os.getenv("FLAG", "404CTF{Fake_Flag}"))
        else:
            print("Malhereusement vos particules ont échoué à se rencontrer...")
    except ValueError:
        print("Il semblerait qu'il y ait eu une erreur dans vos données...")
        exit(1)

