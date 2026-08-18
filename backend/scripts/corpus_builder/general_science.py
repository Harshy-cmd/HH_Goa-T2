"""General Science Domain Knowledge Generator.
Comprehensive educational coverage of Physics, Chemistry, Biology, Earth Science, and Astronomy.
"""
from __future__ import annotations

def get_general_science_documents() -> list[dict]:
    data = [
        # Physics
        ("sci-phys-newton-laws", "Newton's Laws of Motion", "physics",
         "Sir Isaac Newton formulated the three fundamental laws of classical mechanics: First Law (Law of Inertia) states an object remains at rest or in uniform motion unless acted upon by an external net force. Second Law (F = ma) states force equals the rate of change of momentum (mass times acceleration). Third Law states for every action, there is an equal and opposite reaction."),
        ("sci-phys-gravity", "Gravity and Universal Gravitation", "physics",
         "Gravity is a fundamental natural interaction by which all things with mass or energy are attracted toward one another. Newton's Law of Universal Gravitation states that the gravitational force between two masses is directly proportional to the product of their masses and inversely proportional to the square of the distance between them: F = G*(m1*m2)/r^2. Einstein's General Relativity describes gravity as spacetime curvature."),
        ("sci-phys-thermodynamics", "The Laws of Thermodynamics", "physics",
         "Thermodynamics governs heat, work, and energy conversion across physical systems. The Zeroth Law establishes thermal equilibrium and temperature. The First Law (Conservation of Energy) dictates energy cannot be created or destroyed, only transformed. The Second Law states the total entropy of an isolated system always increases over time. The Third Law states entropy approaches a constant minimum as temperature approaches absolute zero (0 Kelvin)."),
        ("sci-phys-electromagnetism", "Electromagnetism and Maxwell's Equations", "physics",
         "Electromagnetism is the physical force governing electric charges and magnetic fields. James Clerk Maxwell unified electricity, magnetism, and light into four governing equations: Gauss's Law for electricity, Gauss's Law for magnetism, Faraday's Law of Induction, and the Ampere-Maxwell Law, proving electromagnetic waves propagate at the speed of light."),
        ("sci-phys-optics-waves", "Wave Mechanics and Optics", "physics",
         "Waves are disturbances that transfer energy through matter or space without net transport of matter. Mechanical waves require a physical medium, while electromagnetic waves propagate through a vacuum. Light exhibits wave-particle duality, undergoing reflection, refraction (Snell's Law), diffraction, interference, and polarization."),

        # Chemistry
        ("sci-chem-atomic-structure", "Atomic Structure and Subatomic Particles", "chemistry",
         "Atoms are the basic building blocks of chemical matter, composed of three primary subatomic particles: protons (positively charged) and neutrons (neutral) bound together in the dense central nucleus, surrounded by electrons (negatively charged) occupying quantized energy orbitals according to quantum mechanical principles."),
        ("sci-chem-periodic-table", "The Periodic Table of Elements", "chemistry",
         "The Periodic Table arranges all 118 known chemical elements in order of increasing atomic number (number of protons). Columns represent 'groups' with similar valence electron configurations and chemical reactivities (e.g., Alkali Metals, Halogens, Noble Gases). Rows represent 'periods' corresponding to expanding electron shell energy levels."),
        ("sci-chem-bonding", "Chemical Bonding (Ionic, Covalent, Metallic)", "chemistry",
         "Chemical bonds form when atoms share or transfer valence electrons to achieve stable octet configurations. Covalent bonds involve the mutual sharing of electron pairs between nonmetals. Ionic bonds result from electrostatic attraction between oppositely charged ions formed by electron transfer between metals and nonmetals. Metallic bonds involve a delocalized 'sea' of valence electrons surrounding metal cations."),
        ("sci-chem-reactions-acids", "Chemical Reactions, Acids, and Bases", "chemistry",
         "Chemical reactions rearrange atoms to transform reactants into products while conserving mass. In aqueous chemistry, acids increase hydronium ion (H3O+) concentrations (pH < 7), while bases increase hydroxide ion (OH-) concentrations (pH > 7). Neutralization reactions between acids and bases produce water and a salt."),

        # Biology
        ("sci-bio-cell-structure", "Cell Structure and Organelles", "biology",
         "The cell is the basic structural, functional, and biological unit of all living organisms. Prokaryotic cells lack a membrane-bound nucleus, whereas eukaryotic cells contain specialized membrane-bound organelles including the nucleus (housing genomic DNA), mitochondria (cellular respiration and ATP generation), endoplasmic reticulum, and Golgi apparatus."),
        ("sci-bio-dna-genetics", "DNA, RNA, and Molecular Genetics", "biology",
         "Deoxyribonucleic Acid (DNA) is the double-helix molecule that carries hereditary genetic instructions in living organisms. Composed of nucleotide building blocks (Adenine, Thymine, Cytosine, Guanine), DNA replicates and transcribes genetic information into Messenger RNA (mRNA), which is translated by ribosomes into functional protein chains (the Central Dogma of Molecular Biology)."),
        ("science-photosynthesis-en", "Photosynthesis in Green Plants and Algae", "biology",
         "Photosynthesis is the biological process by which green plants, algae, and cyanobacteria convert light energy into chemical energy. Using sunlight, water (H2O), and carbon dioxide (CO2), chloroplasts containing chlorophyll produce glucose (C6H12O6) and release oxygen gas (O2) into the atmosphere as a vital by-product: 6CO2 + 6H2O + Light -> C6H12O6 + 6O2."),
        ("sci-bio-cellular-respiration", "Cellular Respiration and ATP Generation", "biology",
         "Cellular respiration is the biochemical pathway by which eukaryotic cells break down glucose molecules in the presence of oxygen to produce adenosine triphosphate (ATP), the primary energy currency of the cell. The process proceeds through three stages: Glycolysis in the cytoplasm, the Krebs Cycle in the mitochondrial matrix, and the Electron Transport Chain across the inner mitochondrial membrane."),
        ("sci-bio-evolution", "Biological Evolution and Natural Selection", "biology",
         "Biological evolution is the change in the heritable traits of biological populations over successive generations. Charles Darwin articulated natural selection as the primary evolutionary mechanism, wherein individuals with advantageous phenotypic traits best suited to their environment enjoy higher reproductive success and pass those traits to offspring."),

        # Earth Science
        ("sci-earth-atmosphere", "Earth's Atmosphere and Weather Systems", "earth_science",
         "Earth's atmosphere is a layer of gases composed primarily of nitrogen (78%), oxygen (21%), argon (0.93%), and trace greenhouse gases (carbon dioxide, water vapor, methane). The atmosphere consists of five distinct thermal layers: Troposphere (where weather occurs), Stratosphere (containing the protective ozone layer), Mesosphere, Thermosphere, and Exosphere."),
        ("sci-earth-water-cycle", "The Hydrologic (Water) Cycle", "earth_science",
         "The water cycle describes the continuous movement of water on, above, and below the surface of the Earth. Driven by solar radiation, water evaporates from oceans and surface bodies, transpires from plants, condenses into clouds in the atmosphere, falls back as precipitation (rain or snow), and returns via surface runoff and groundwater infiltration."),
        ("sci-earth-plate-tectonics", "Plate Tectonics and Geology", "earth_science",
         "Plate tectonics is the scientific theory explaining the large-scale motion of seven major and numerous minor lithospheric plates over Earth's ductile asthenosphere. Plate boundary interactions drive geological phenomena including earthquakes, volcanic activity, mountain building (orogeny), and oceanic trench formation across convergent, divergent, and transform boundaries."),

        # Astronomy
        ("sci-astro-solar-system", "The Solar System and Planetary Bodies", "astronomy",
         "The Solar System comprises the Sun and all gravitationally bound astronomical bodies orbiting it. The eight recognized planets in order of distance from the Sun are Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Inner terrestrial planets feature rocky surfaces, while outer planets are divided into gas giants (Jupiter, Saturn) and ice giants (Uranus, Neptune)."),
        ("sci-astro-stellar-evolution", "Stellar Evolution and Black Holes", "astronomy",
         "Stars are luminous spheres of plasma held together by their own gravity and powered by nuclear fusion in their cores. When high-mass stars exhaust their nuclear fuel, they undergo gravitational core collapse resulting in a supernova explosion, leaving behind extremely dense remnants such as neutron stars or stellar-mass black holes whose gravitational escape velocity exceeds the speed of light.")
    ]
    docs = []
    for doc_id, title, topic, text in data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "general_science",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })
    return docs
