# Super enQuête Libre [2/4]

![challenge](chall.png)

## Solution

<details>
<summary>Cliquez pour dévoiler la solution</summary>

* On a accès à une interface de type "shell" qui nous permet d'exécuter des requêtes SQL sur une base de données.
* On commence par explorer les tables :
    ```sql
    ╔══════════════════════════════════════════════════════╗
    ║         404CTF — Super Enquête Libre                 ║
    ║         Base de données chargée                      ║
    ║  Tapez .help pour l'aide, .quit pour quitter         ║
    ╚══════════════════════════════════════════════════════╝

    sql> .tables
    AccessLog   Attendance   Badge   Building   Course   Person   Room   sqlite_sequence
    sql> SELECT * FROM AccessLog;
    +--------+----------+---------+------------+----------+
    | log_id | badge_id | room_id | date       | time     |
    +--------+----------+---------+------------+----------+
    | 1      | 100      | 125     | 2025-09-15 | 17:00:04 |
    | 2      | 98       | 125     | 2025-09-15 | 17:01:23 |
    | 3      | 119      | 125     | 2025-09-15 | 17:01:33 |
    | 4      | 90       | 125     | 2025-09-15 | 17:01:38 |
    [...]
    +--------+----------+---------+------------+----------+
    30 ligne(s)
    (affichage limité à 30 lignes sur 8286)
    ```
* C'est ici `AccessLog` qui nous intéresse, elle contient les logs d'accès aux différentes salles du bâtiment.

### Méthode n°1 : pas à pas

* Analysons le challenge : on nous demande de trouver **LA DERNIÈRE personne** (nom + prénom) qui a visité exactement 4 salles différentes en une journée.
* Après réflexion et tâtonnements, on aboutit à la requête suivante :
    ```sql
    SELECT badge_id, date, COUNT(DISTINCT room_id) AS nb_salles_visitees
    FROM AccessLog
    GROUP BY badge_id, date
    HAVING COUNT(DISTINCT room_id) = 4
    ORDER BY date DESC;
    ```
* Explication de la requête :
    * On sélectionne le badge_id, la date et le nombre de salles différentes visitées (en utilisant `COUNT(DISTINCT room_id)`).
    * On groupe les résultats par badge_id et date pour obtenir le nombre de salles visitées par personne et par jour.
    * On filtre pour ne garder que les cas où le nombre de salles visitées est exactement 4.
    * Enfin, on trie les résultats par date décroissante pour obtenir la dernière personne en premier.
* Résultat :
    ```sql
    +----------+------------+--------------------+
    | badge_id | date       | nb_salles_visitees |
    +----------+------------+--------------------+
    | 184      | 2026-05-04 | 4                  |
    | 214      | 2025-12-11 | 4                  |
    +----------+------------+--------------------+
        2 ligne(s)
    ```
* Il ne reste qu'à matcher avec la table `Badge` puis `Person` pour trouver le nom et prénom de la personne associée au badge_id **184**.
    ```sql
    sql> SELECT * FROM Badge WHERE badge_id=184;
    +----------+-----------+------------+-------------+--------+
    | badge_id | person_id | issue_date | expiry_date | active |
    +----------+-----------+------------+-------------+--------+
    | 184      | 63        | 2025-10-02 | 2026-10-02  | 1      |
    +----------+-----------+------------+-------------+--------+
    1 ligne(s)

    sql> SELECT * FROM Person WHERE person_id=63;
    +-----------+-----------+------------+------------+-------------------------+---------+-------+
    | person_id | last_name | first_name | birth_date | email                   | status  | class |
    +-----------+-----------+------------+------------+-------------------------+---------+-------+
    | 63        | Robert    | Noémie     | 2006-03-18 | noemie.robert@campus.fr | student | G5    |
    +-----------+-----------+------------+------------+-------------------------+---------+-------+
    1 ligne(s)
    ```

### Méthode n°2 : TURBOREQUÊTE

* Une requête one shot pour trouver directement le flag :
    ```sql
    SELECT 
        Person.first_name,
        Person.last_name,
        AccessLog.date,
        COUNT(DISTINCT AccessLog.room_id) AS nb_salles_visitees
    FROM AccessLog
    INNER JOIN Badge 
        ON Badge.badge_id = AccessLog.badge_id
    INNER JOIN Person 
        ON Person.person_id = Badge.person_id
    GROUP BY AccessLog.badge_id, AccessLog.date
    HAVING COUNT(DISTINCT AccessLog.room_id) = 4
    ORDER BY AccessLog.date DESC;
    ```
* Résultat :
    ```sql
    +------------+-----------+------------+--------------------+
    | first_name | last_name | date       | nb_salles_visitees |
    +------------+-----------+------------+--------------------+
    | Noémie     | Robert    | 2026-05-04 | 4                  |
    | Elsa       | Bernard   | 2025-12-11 | 4                  |
    +------------+-----------+------------+--------------------+
    2 ligne(s)
    ```

### Flag

`404CTF{noémie_robert}`