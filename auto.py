class AutomateDeterministe:
    def __init__(self, table_afn, etat_initial, etats_finaux):
        self.table_afn = table_afn
        self.etat_initial_afn = etat_initial
        self.etats_finaux_afn = set(etats_finaux)
        
        self.alphabet = sorted({
            symbole for transitions in self.table_afn.values()
            for symbole in transitions.keys() if symbole != '$'
        })
        
        self.table_afd = {}
        self.etats_finaux_afd = set()
        self.etat_initial_afd = ""
        
        self.construire_afd()

    def _fermeture_epsilon(self, etats):
        pile = list(etats)
        fermeture = set(etats)
        while pile:
            etat = pile.pop()
            if etat in self.table_afn and '$' in self.table_afn[etat]:
                for suivant in self.table_afn[etat]['$']:
                    if suivant not in fermeture:
                        fermeture.add(suivant)
                        pile.append(suivant)
        return frozenset(fermeture)

    def _deplacer(self, etats, symbole):
        atteints = set()
        for etat in etats:
            if etat in self.table_afn and symbole in self.table_afn[etat]:
                atteints.update(self.table_afn[etat][symbole])
        return frozenset(atteints)

    def _format_nom_etat(self, ensemble_etats):
        if not ensemble_etats:
            return "Ø"
        return "{" + ",".join(sorted(list(ensemble_etats))) + "}"

    def construire_afd(self):
        init_set = self._fermeture_epsilon({self.etat_initial_afn})
        self.etat_initial_afd = self._format_nom_etat(init_set)
        
        file_attente = [init_set]
        visites = {init_set}
        self.table_afd = {}

        while file_attente:
            courant = file_attente.pop(0)
            courant_nom = self._format_nom_etat(courant)
            self.table_afd[courant_nom] = {}

            if any(e in self.etats_finaux_afn for e in courant):
                self.etats_finaux_afd.add(courant_nom)

            for symbole in self.alphabet:
                proches = self._deplacer(courant, symbole)
                cible = self._fermeture_epsilon(proches)
                
                if not cible:
                    continue

                cible_nom = self._format_nom_etat(cible)
                self.table_afd[courant_nom][symbole] = cible_nom

                if cible not in visites:
                    visites.add(cible)
                    file_attente.append(cible)

    def afficher_table_afd(self):
        print("\n" + "="*60)
        print("                 TABLE DE TRANSITION DE L'AFD                 ")
        print("="*60)
        
        en_tete = f"{'État AFD':<20} | " + " | ".join([f"{s:^8}" for s in self.alphabet])
        print(en_tete)
        print("-" * len(en_tete))

        for etat, transitions in self.table_afd.items():
            prefixe = "->" if etat == self.etat_initial_afd else "  "
            suffixe = "*" if etat in self.etats_finaux_afd else " "
            label = f"{prefixe}{suffixe} {etat}"
            
            ligne = f"{label:<20} | "
            ligne += " | ".join([f"{transitions.get(s, '-'):^8}" for s in self.alphabet])
            print(ligne)
        print("-" * len(en_tete))
        print("Légende : -> = État Initial | * = État Final\n")

    def generer_code_mermaid(self):
        """Génère le code du graphe au format Mermaid (visualisable en schéma visuel)."""
        print("\n" + "="*60)
        print("         CODE DU SCHÉMA VISUEL (Format Mermaid)          ")
        print("="*60)
        print("Copiez ce code dans un éditeur compatible (comme Notion, GitHub, ou sur https://mermaid.live) :")
        print("-" * 60)
        print("stateDiagram-v2")
        print(f"    [*] --> {self.etat_initial_afd}")
        
        for etat in self.etats_finaux_afd:
            print(f"    {etat} : État Final")

        for src, trans in self.table_afd.items():
            for sym, dest in trans.items():
                print(f"    {src} --> {dest} : {sym}")
        print("="*60 + "\n")

    def executer_chaine(self, chaine):
        etat_courant = self.etat_initial_afd
        print(f"\n" + "—"*50)
        print(f" SIMULATION DU MOT : \"{chaine}\"")
        print("—"*50)
        
        for i, symbole in enumerate(chaine, 1):
            if symbole not in self.alphabet:
                print(f"❌ Erreur : Symbole '{symbole}' hors de l'alphabet.")
                return False

            if etat_courant in self.table_afd and symbole in self.table_afd[etat_courant]:
                prochain_etat = self.table_afd[etat_courant][symbole]
                print(f" 🟢 Étape {i} : '{symbol}' ==> {etat_courant} ➔ {prochain_etat}")
                etat_courant = prochain_etat
            else:
                print(f" 🔴 Étape {i} : '{symbole}' ==> Bloqué depuis {etat_courant}")
                etat_courant = None
                break

        est_accepte = etat_courant in self.etats_finaux_afd
        print("—"*50)
        print(f"📌 État final : {etat_courant if etat_courant else 'Bloqué'}")
        print(f"RÉSULTAT : {'RECONNU ✅' if est_accepte else 'REFUSÉ ❌'}")
        print("—"*50)
        return est_accepte


# ==========================================
# EXÉCUTION
# ==========================================
if __name__ == "__main__":
    afn_demo = {
        'q0': {'$': ['q1'], 'a': ['q0']},
        'q1': {'b': ['q2']},
        'q2': {'a': ['q2'], 'b': ['q2']}
    }
    
    afd = AutomateDeterministe(afn_demo, 'q0', ['q2'])
    afd.afficher_table_afd()
    
    # Génère le schéma visuel sous forme de code textuel intelligent
    afd.generer_code_mermaid()
    
    while True:
        mot = input("Entrez un mot à tester (ou 'q' pour quitter) : ").strip()
        if mot.lower() == 'q':
            break
        afd.executer_chaine(mot)
