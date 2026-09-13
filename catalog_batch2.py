"""
Batch 2: expands the PawsAndScrubs catalog with more breeds, cat variants,
and nursing specialties. Each entry: (breed_line, role_line, tone, animal, pronoun, slug)
"""

COMBOS = [
    ("Dachshund Mom", "Nurse Life", "black_shirt", "dog", "her", "dachshund_mom_nurse"),
    ("Husky Mom", "ER Nurse", "white_shirt", "dog", "her", "husky_mom_er_nurse"),
    ("Poodle Mom", "Nurse Life", "white_shirt", "dog", "her", "poodle_mom_nurse"),
    ("Pitbull Mom", "ICU Nurse", "black_shirt", "dog", "her", "pitbull_mom_icu_nurse"),
    ("Chihuahua Mom", "Nurse Life", "white_shirt", "dog", "her", "chihuahua_mom_nurse"),
    ("Great Dane Dad", "ER Nurse", "black_shirt", "dog", "his", "great_dane_dad_er_nurse"),
    ("Border Collie Mom", "School Nurse", "white_shirt", "dog", "her", "border_collie_mom_school_nurse"),
    ("Boxer Dad", "ICU Nurse", "black_shirt", "dog", "his", "boxer_dad_icu_nurse"),
    ("Beagle Mom", "Nurse Life", "white_shirt", "dog", "her", "beagle_mom_nurse"),
    ("Australian Shepherd Mom", "Pediatric Nurse", "black_shirt", "dog", "her", "aussie_mom_peds_nurse"),
    ("Rottweiler Dad", "ER Nurse", "black_shirt", "dog", "his", "rottweiler_dad_er_nurse"),
    ("Cat Mom", "Nurse Life", "white_shirt", "cat", "her", "cat_mom_nurse"),
    ("Tabby Cat Mom", "Nurse Life", "black_shirt", "cat", "her", "tabby_cat_mom_nurse"),
    ("Black Cat Mom", "ICU Nurse", "white_shirt", "cat", "her", "black_cat_mom_icu_nurse"),
    ("Orange Cat Mom", "Nurse Life", "black_shirt", "cat", "her", "orange_cat_mom_nurse"),
    ("Siamese Cat Mom", "School Nurse", "white_shirt", "cat", "her", "siamese_cat_mom_school_nurse"),
    ("Maine Coon Cat Mom", "NICU Nurse", "black_shirt", "cat", "her", "mainecoon_cat_mom_nicu_nurse"),
    ("Golden Retriever Dad", "OR Nurse", "white_shirt", "dog", "his", "golden_retriever_dad_or_nurse"),
    ("German Shepherd Mom", "Travel Nurse", "black_shirt", "dog", "her", "gsd_mom_travel_nurse"),
    ("French Bulldog Dad", "Hospice Nurse", "white_shirt", "dog", "his", "frenchie_dad_hospice_nurse"),
    ("Labrador Dad", "L&D Nurse", "black_shirt", "dog", "his", "labrador_dad_ld_nurse"),
    ("Corgi Dad", "Psych Nurse", "white_shirt", "dog", "his", "corgi_dad_psych_nurse"),
    ("Dachshund Dad", "Home Health Nurse", "black_shirt", "dog", "his", "dachshund_dad_homehealth_nurse"),
    ("Husky Dad", "NICU Nurse", "white_shirt", "dog", "his", "husky_dad_nicu_nurse"),
    ("Pitbull Mom", "Travel Nurse", "black_shirt", "dog", "her", "pitbull_mom_travel_nurse"),
]
