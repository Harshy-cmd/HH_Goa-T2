"""General Knowledge Domain Knowledge Generator.
Comprehensive educational coverage of World Geography, Economics, Major History, and Science Methodology.
"""
from __future__ import annotations

def get_general_knowledge_documents() -> list[dict]:
    data = [
        # --- 1. GEOGRAPHY ---
        ("gk-geo-continents-oceans", "Continents and Oceans of the Earth", "geography",
         "Earth's landmass is divided into seven recognized continents: Asia (the largest by land area and population), Africa (second largest, home to the Sahara Desert), North America, South America, Antarctica (the coldest, highest, driest, and windiest continent), Europe, and Australia/Oceania (the smallest continent). Earth's global ocean is divided into five oceanic basins: the Pacific Ocean (the largest and deepest, containing the Mariana Trench), Atlantic Ocean, Indian Ocean, Southern (Antarctic) Ocean, and Arctic Ocean."),
        ("gk-geo-mountains-rivers", "Major Mountain Ranges and Global River Systems", "geography",
         "The Himalayas in Asia constitute Earth's highest mountain range, containing Mount Everest (8,848.86 m) and K2, formed by the convergent collision of the Indian and Eurasian tectonic plates. The Andes in South America form the world's longest continental mountain range. Major global river systems include the Nile River in northeastern Africa (often cited as the longest at 6,650 km), the Amazon River in South America (the largest by water discharge and drainage basin), the Yangtze River in China, and the Mississippi-Missouri in North America."),
        ("gk-geo-coordinates-climate-zones", "Latitude, Longitude, Time Zones, and Climate Zones", "geography",
         "The geographic coordinate system uses Latitude (angles north or south of the Equator at 0 degrees, ranging to 90 degrees at the poles) and Longitude (angles east or west of the Prime Meridian at Greenwich, London at 0 degrees, ranging to 180 degrees at the International Date Line). Earth is partitioned into 24 standard time zones based on 15-degree longitudinal increments. Major solar climate zones include the Tropics (between Tropic of Cancer 23.5 N and Tropic of Capricorn 23.5 S), Temperate Zones, and Polar Frigid Zones."),

        # --- 2. ECONOMICS ---
        ("gk-econ-supply-demand", "Economics Fundamentals: Supply, Demand, and Market Equilibrium", "economics",
         "Economics is the social science studying the allocation of scarce resources among competing uses. The Law of Demand dictates that, ceteris paribus (all else equal), as the price of a good increases, consumer quantity demanded decreases. The Law of Supply states that as price increases, producer quantity supplied increases. The intersection of supply and demand curves establishes the Market Clearing Equilibrium Price where quantity demanded equals quantity supplied."),
        ("gk-econ-macro-gdp-inflation", "Macroeconomics: Gross Domestic Product (GDP), Inflation, and Policy", "economics",
         "Macroeconomics analyzes national and global economic performance. Gross Domestic Product (GDP = C + I + G + (X - M)) measures the total market value of all final goods and services produced within a country over a specific time period. Inflation is the sustained general increase in price levels and decrease in purchasing power of money, tracked via the Consumer Price Index (CPI). Central banks enact Monetary Policy (adjusting interest rates, reserve requirements, and money supply), while governments implement Fiscal Policy (taxation and government spending) to stabilize economic cycles."),
        ("gk-econ-market-structures", "Market Structures: Perfect Competition, Monopoly, and Oligopoly", "economics",
         "Market structures characterize competitive dynamics in an industry. Perfect Competition features many buyers and sellers, homogeneous products, perfect information, and zero barriers to entry (firms are price takers). Monopoly features a single seller with high barriers to entry and price-setting power. Oligopoly features a few dominant firms exhibiting strategic interdependence (e.g., Cournot/Bertrand competition, game-theoretic Nash equilibrium). Monopolistic Competition features many firms selling differentiated products."),

        # --- 3. MAJOR HISTORY & CIVILIZATIONS ---
        ("gk-hist-ancient-civilizations", "Ancient Civilizations: Mesopotamia, Egypt, Indus Valley, and China", "history",
         "Human urban civilization emerged in fertile river valleys: Mesopotamia (Sumerians, Babylonians between Tigris and Euphrates, inventing cuneiform script and the wheel), Ancient Egypt along the Nile (hieroglyphics, monumental pyramids, centralized pharaonic governance), the Indus Valley Civilization along the Indus and Ghaggar-Hakra (advanced urban planning, standardized brick weights, drainage networks at Mohenjo-Daro and Harappa), and Ancient China along the Yellow River (Shang and Zhou dynasties, bronze metallurgy, ancestor worship)."),
        ("gk-hist-classical-antiquity", "Classical Antiquity: Ancient Greece and the Roman Empire", "history",
         "Classical Antiquity shaped Western philosophical, legal, and political foundations. Ancient Greece introduced direct democracy in Athens, drama, and philosophy through Socrates, Plato, and Aristotle. The Roman Republic and subsequent Roman Empire established codified legal jurisprudence (Roman law), civil engineering (aqueducts, roads, arches, concrete), and military organization, governing the Mediterranean basin for centuries before the fall of Western Rome in 476 CE."),
        ("gk-hist-scientific-revolution", "The Scientific Revolution and the Enlightenment", "history",
         "The Scientific Revolution (16th to 18th centuries) replaced Aristotelian scholastic dogma with empirical observation, experimentation, and mathematical modeling. Nicolaus Copernicus proposed the heliocentric model, Galileo Galilei used the telescope to discover Jupiter's moons, Johannes Kepler formulated laws of planetary motion, and Sir Isaac Newton formulated universal gravitation and calculus. The subsequent Age of Enlightenment championed reason, individual human rights (John Locke, Voltaire), and secular governance."),
        ("gk-hist-industrial-revolution", "The Industrial Revolution and Technological Transformation", "history",
         "The Industrial Revolution, beginning in Britain during the mid-18th century, marked the transition from manual agrarian economies to mechanized industrial manufacturing. Powered by the commercial steam engine (James Watt), mechanized textile looms, iron metallurgy advancements, and railways, it dramatically accelerated global urbanization, transformed labor capital relations, and established modern industrial technological society."),

        # --- 4. SCIENCE METHODOLOGY & SOCIETY ---
        ("gk-sci-scientific-method", "The Scientific Method and Empirical Inquiry", "science_method",
         "The scientific method is a rigorous, iterative epistemology for acquiring empirical knowledge of the natural universe. It comprises systematic steps: making systematic observations, asking causal questions, formulating testable and falsifiable hypotheses (Karl Popper's falsificationism), conducting controlled experiments with independent and dependent variables, gathering quantitative data, analyzing results statistically, and subjecting findings to peer review in scientific journals."),
        ("gk-sci-sustainability-energy", "Renewable Energy and Environmental Sustainability", "science_method",
         "Environmental sustainability seeks to meet human needs without compromising the ecological equilibrium of future generations. Anthropogenic climate change is driven by greenhouse gas emissions (carbon dioxide, methane) from fossil fuel combustion. Renewable energy sources include Solar Photovoltaics (converting sunlight directly into electricity via the photoelectric effect), Wind Turbines (kinetic to electrical conversion), Hydroelectric Power, and Geothermal Energy, reducing carbon footprints to achieve global net-zero goals.")
    ]
    docs = []
    for doc_id, title, topic, text in data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "general_knowledge",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })
    return docs
