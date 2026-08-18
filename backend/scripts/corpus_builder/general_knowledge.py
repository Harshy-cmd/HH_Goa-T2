"""General Knowledge Domain Knowledge Generator.
Comprehensive educational coverage of Geography, Economics, Major History, and Science Methodology.
"""
from __future__ import annotations

def get_general_knowledge_documents() -> list[dict]:
    data = [
        ("gk-geo-continents-oceans", "Continents and Oceans of the Earth", "geography",
         "The Earth's landmass is divided into seven continents: Asia (the largest and most populous), Africa, North America, South America, Antarctica (the coldest and driest), Europe, and Australia/Oceania. The Earth's continuous global body of salt water is divided into five recognized oceans: Pacific Ocean (the largest and deepest), Atlantic Ocean, Indian Ocean, Southern Ocean, and Arctic Ocean."),
        ("gk-geo-mountains-rivers", "Major Mountain Ranges and World Rivers", "geography",
         "The Himalayas in Asia contain the world's highest peaks, including Mount Everest at 8,848 meters above sea level. The Andes in South America form the longest continental mountain range on Earth. Major river systems include the Nile River in northeastern Africa (often cited as the longest) and the Amazon River in South America (the largest by water discharge volume)."),
        ("gk-econ-fundamentals", "Economics Fundamentals: Supply, Demand, and Market Equilibrium", "economics",
         "Economics is the social science studying the production, distribution, and consumption of goods and services. The Law of Demand states that, ceteris paribus, as the price of a good increases, quantity demanded decreases. The Law of Supply states that as price increases, quantity supplied increases. The intersection of supply and demand curves establishes the market equilibrium price."),
        ("gk-econ-macroeconomics", "Macroeconomics, GDP, and Inflation", "economics",
         "Macroeconomics examines economy-wide phenomena such as total output, economic growth, and price stability. Gross Domestic Product (GDP) measures the total monetary value of all finished goods and services produced within a nation over a specific time period. Inflation is the general progressive increase in prices and fall in the purchasing power of money, monitored using the Consumer Price Index (CPI)."),
        ("gk-hist-ancient-civilizations", "Ancient Civilizations and the Cradle of Humanity", "history",
         "Early human civilization arose along fertile river valleys: the Mesopotamian Sumerians between the Tigris and Euphrates (inventors of cuneiform writing), Ancient Egypt along the Nile (known for hieroglyphs and monumental architecture), the Indus Valley Civilization along the Indus and Saraswati rivers (celebrated for urban planning and metallurgy), and Ancient China along the Yellow River."),
        ("gk-hist-scientific-revolution", "The Scientific Revolution and the Enlightenment", "history",
         "The Scientific Revolution (16th to 18th centuries) transformed European views of nature, transitioning from scholasticism to empirical observation and mathematical analysis, pioneered by Nicolaus Copernicus, Galileo Galilei, Johannes Kepler, and Sir Isaac Newton. This laid the foundation for the Age of Enlightenment, emphasizing reason, individual liberty, and empirical inquiry."),
        ("gk-hist-industrial-revolution", "The Industrial Revolution", "history",
         "The Industrial Revolution, beginning in Britain in the late 18th century, marked the transition from handcraft agrarian economies to machine-driven industrial manufacturing. Powered by the steam engine, mechanization of textiles, metallurgy advancements, and railways, it dramatically reshaped global urbanization, labor structures, and modern technological society."),
        ("gk-sci-scientific-method", "The Scientific Method and Empirical Inquiry", "science_method",
         "The scientific method is an iterative, rigorous framework for acquiring empirical knowledge about the natural universe. It comprises six core steps: making observations, formulating questions, constructing testable hypotheses, designing controlled experiments, gathering and analyzing quantitative data, and drawing peer-reviewed conclusions.")
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
